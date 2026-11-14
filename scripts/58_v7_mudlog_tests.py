"""
v7 step 3 (V7_PLAN.md C3-C5, C8): the mud-log sand fraction against chemistry
and photographs. Stages are run in this order, each committed before the next:

  python 58_v7_mudlog_tests.py elig     C4: eligibility and the set of record (labels only)
  python 58_v7_mudlog_tests.py g3       G3: label against XRF Si/Al (no photographs)
  python 58_v7_mudlog_tests.py photo    C5: P2 (primary), P1, baselines, sensitivities (run once)
  python 58_v7_mudlog_tests.py c8       C8: mud-log glauconite against XRF G and the step-2 score (exploratory)

Labels: bag_labels_A.csv from `57_v7_mudlog_labels.py labels fix` (reader A,
with reader C for 24/9-3).
"""
import json
import sys
from importlib import import_module

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import config as C
from features import FEATURE_NAMES

EV = import_module("29_v2_evaluate")
BL = import_module("34_v3_baselines")
M = import_module("52_v7_photo_to_xrf")
OUT = C.WORK_DIR / "v7" / "step3"
CORES = {"24_9-3": [(1777.0, 1798.0)]}  # cored intervals inside the Tertiary (protocol check)
INF_THR, MIN_INF, MIN_CLUST, CLUST_GAP, MIN_BAGS, MIN_WELLS = 0.05, 15, 3, 30.0, 30, 6
PAIR_M, PAIR_DY, MIN_PAIRS = 50.0, 0.2, 20


def load():
    base, emb = EV.load_tables()
    wells, d = base.well.values, base.depth_m.values.astype(float)
    s1 = pd.read_csv(C.WORK_DIR / "v7" / "step1_predictions.csv")
    assert (s1.well.values == wells).all() and np.allclose(s1.depth_m.values, d)
    lab = pd.read_csv(OUT / "bag_labels_A.csv")
    lab["depth_m"] = lab.depth_m.round(2)
    t = base[["well", "depth_m"]].assign(depth_m=base.depth_m.round(2)).merge(
        lab[["well", "depth_m", "Y", "sand", "silt", "glauc", "carb", "clay", "sand_with_faded", "cover"]],
        on=["well", "depth_m"], how="left")
    assert len(t) == len(base)
    core = np.zeros(len(base), bool)
    for w, iv in CORES.items():
        for a, b in iv:
            core |= (wells == w) & (d >= a) & (d <= b)
    S = s1.in_S.values.astype(bool) & np.isfinite(t.Y.values) & ~core
    return base, emb, wells, d, s1, t, S


def clusters(depths, gap=CLUST_GAP):
    if len(depths) == 0:
        return 0
    return 1 + int((np.diff(np.sort(depths)) > gap).sum())


def eligibility(wells, d, Y, S):
    rows = []
    for w in np.unique(wells[np.isfinite(Y)]):
        m = S & (wells == w)
        r = {"well": w, "n_bags": int(m.sum())}
        if m.sum() >= 3:
            hp = M.highpass(d[m], Y[m])
            inf = np.abs(hp) >= INF_THR
            r.update(n_informative=int(inf.sum()), n_clusters=clusters(d[m][inf]), mean_sand=float(Y[m].mean()),
                     share_nonzero=float((Y[m] > 0).mean()))
        else:
            r.update(n_informative=0, n_clusters=0, mean_sand=np.nan, share_nonzero=np.nan)
        r["eligible"] = bool(r["n_bags"] >= MIN_BAGS and r["n_informative"] >= MIN_INF and r["n_clusters"] >= MIN_CLUST)
        rows.append(r)
    return pd.DataFrame(rows)


def per_well(pred, y, wells, d, S, elig):
    out = {}
    for w in elig:
        m = S & (wells == w) & np.isfinite(pred) & np.isfinite(y)
        if m.sum() >= MIN_BAGS:
            out[w] = M.rho(M.highpass(d[m], pred[m]), M.highpass(d[m], y[m]))
    return pd.Series(out, dtype=float)


def concordance(pred, y, wells, d, S, elig):
    """Local pair concordance: pairs < 50 m apart whose Y differs by >= 0.2."""
    out, npairs = {}, {}
    for w in elig:
        m = np.flatnonzero(S & (wells == w) & np.isfinite(pred) & np.isfinite(y))
        dd, yy, pp = d[m], y[m], pred[m]
        i, j = np.triu_indices(len(m), 1)
        k = (np.abs(dd[i] - dd[j]) < PAIR_M) & (np.abs(yy[i] - yy[j]) >= PAIR_DY)
        npairs[w] = int(k.sum())
        if k.sum() >= MIN_PAIRS:
            s = np.sign(yy[i][k] - yy[j][k]) * np.sign(pp[i][k] - pp[j][k])
            out[w] = float(((s > 0) + 0.5 * (s == 0)).mean())
    return pd.Series(out, dtype=float), npairs


def summ(s, null=0.0):
    s = s.dropna()
    r = {"n_wells": int(len(s)), "per_well": s.round(4).to_dict()}
    if len(s) >= 3:
        bs = np.median(M.RNG.choice(s.values, (10000, len(s))), axis=1)
        r.update(median=float(s.median()), n_above=int((s > null).sum()),
                 wilcoxon_p=float(wilcoxon(s.values - null, alternative="greater").pvalue),
                 boot95_median=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))])
    return r


def lowo(X, y, wells, d, S, kind, fold=lambda w: w, weights=False):
    pred = np.full(len(y), np.nan)
    ok = S & np.isfinite(y) & np.isfinite(X).all(1)
    folds = np.array([fold(w) for w in wells])
    for f in np.unique(folds[ok]):
        tr, te = ok & (folds != f), ok & (folds == f)
        if weights:  # equal weight per training well (step 1's fit_rd ignores weights, so fit here)
            p = make_pipeline(StandardScaler(), PCA(n_components=32, random_state=0), Ridge(alpha=1.0))
            p.fit(X[tr], y[tr], ridge__sample_weight=M.well_weights(wells[tr]))
            pred[te] = p.predict(X[te])
        else:
            pred[te] = (M.fit_rd if kind == "RD" else M.fit_re)(X[tr], y[tr]).predict(X[te])
    return pred


def stage_elig():
    base, emb, wells, d, s1, t, S = load()
    e = eligibility(wells, d, t.Y.values, S)
    n = int(e.eligible.sum())
    rec = "S (Tertiary)" if n >= MIN_WELLS else "W (whole well): the pre-Tertiary must be digitised first"
    e.to_csv(OUT / "C4_eligibility.csv", index=False)
    with open(OUT / "C4_set_of_record.json", "w") as f:
        json.dump({"n_eligible_in_S": n, "min_wells": MIN_WELLS, "set_of_record": rec,
                   "eligible_wells": e[e.eligible].well.tolist(), "n_bags_S": int(S.sum())}, f, indent=1)
    print(e.round(3).to_string(index=False))
    print(f"eligible wells in S: {n} -> set of record: {rec}")


def stage_g3():
    base, emb, wells, d, s1, t, S = load()
    e = pd.read_csv(OUT / "C4_eligibility.csv")
    elig = e[e.eligible].well.tolist()
    s = per_well(s1.T1.values, t.Y.values, wells, d, S, elig)
    r = summ(s)
    r["all_wells_with_30_bags"] = per_well(s1.T1.values, t.Y.values, wells, d, S, e[e.n_bags >= MIN_BAGS].well.tolist()).round(4).to_dict()
    r["stop"] = bool(r.get("median", 0) <= 0)
    r["tier"] = "usable" if r.get("median", 0) >= 0.15 else "noisy (a failed photo test is uninformative)"
    with open(OUT / "G3_results.json", "w") as f:
        json.dump(r, f, indent=1)
    print(json.dumps(r, indent=1))


def stage_photo():
    base, emb, wells, d, s1, t, S = load()
    e = pd.read_csv(OUT / "C4_eligibility.csv")
    elig = e[e.eligible].well.tolist()
    Y = t.Y.values
    res = {"n_bags_S": int(S.sum()), "eligible": elig}

    def both(pred, tag, y=Y, sel=S):
        s = per_well(pred, y, wells, d, sel, elig)
        r = summ(s)
        c, npairs = concordance(pred, y, wells, d, sel, elig)
        r["concordance"] = {**summ(c, null=0.5), "n_pairs": npairs}
        res[tag] = r
        return s

    # ---- P2 (primary): step-1 held-out Si/Al predictions, no retraining
    p2 = s1.pred_RD.values
    sP2 = both(p2, "P2 PRIMARY step-1 R-D Si/Al prediction vs Y")
    r = res["P2 PRIMARY step-1 R-D Si/Al prediction vs Y"]
    r["claim_pass"] = bool(r.get("wilcoxon_p", 1) < 0.05 and r.get("median", 0) >= 0.10)
    circ, lagp, lagacf = {}, {}, {}
    for w in elig:
        m = S & (wells == w) & np.isfinite(p2)
        hp_p, hp_y = M.highpass(d[m], p2[m]), M.highpass(d[m], Y[m])
        circ[w] = M.circ_null(hp_p, hp_y, d[m])
        lagp[w], lagacf[w] = M.lag_profile(hp_p, hp_y, d[m], lags=range(-3, 4))
    r["circular_null"] = {w: {"rho_kept": round(o, 4), "p": round(p, 4)} for w, (o, p) in circ.items()}
    r["lag_profile_median"] = {int(k): float(np.nanmedian([lagp[w][k] for w in elig])) for k in range(-3, 4)}
    r["lag_noskill_median"] = {int(k): float(np.nanmedian([lagp[w][0] * lagacf[w][k] for w in elig])) for k in range(-3, 4)}
    both(s1.pred_RE.values, "P2b step-1 R-E Si/Al prediction vs Y")
    both(s1.pred_LOAO.values, "P2c step-1 R-D leave-one-area-out Si/Al prediction vs Y")

    # ---- reference: measured Si/Al
    sREF = both(s1.T1.values, "REFERENCE measured Si/Al vs Y (G3)")
    res["P2 share of reference (median of per-well rho ratio)"] = float(np.nanmedian((sP2 / sREF.reindex(sP2.index)).values))

    # ---- P1 (secondary): retrain on Y
    rgb = emb["rgb"].astype(float)
    E15 = base[FEATURE_NAMES].values.astype(float)
    R15 = base[["ref_" + c for c in FEATURE_NAMES]].values.astype(float)
    XRD, XRE = M.zwell_mat(rgb, wells, S), M.zwell_mat(E15, wells, S, R15)
    lab = [FEATURE_NAMES.index(c) for c in ("lab_L_mean", "lab_a_mean", "lab_b_mean")]
    p1 = lowo(XRD, Y, wells, d, S, "RD")
    sP1 = both(p1, "P1 R-D retrained on Y, LOWO")
    both(lowo(XRD, Y, wells, d, S, "RD", weights=True), "P1 equal well weights")
    both(lowo(XRD, Y, wells, d, S, "RD", fold=M.AREA), "P1 leave-one-area-out")
    both(lowo(XRE, Y, wells, d, S, "RE"), "R-E (15 features) retrained on Y")
    pc = lowo(XRE[:, lab], Y, wells, d, S, "RE")
    sC = both(pc, "colour only (mean L*a*b*) retrained on Y")
    for tag, s in (("P1", sP1), ("P2", sP2)):
        dd = (s - sC.reindex(s.index)).dropna()
        res[f"paired {tag} > colour-only p"] = float(wilcoxon(dd, alternative="greater").pvalue) if len(dd) >= 3 else None

    # ---- baselines (direct, as in step 1)
    dw = BL.dry_weight(base)
    for name, sig in (("relative depth", d.copy()), ("bag dry weight", np.log10(dw))):
        raw = per_well(sig, Y, wells, d, S, elig)
        signed = {}
        for w in raw.index:  # sign taken from the other wells, as in step 1
            oth = raw.drop(w).dropna()
            signed[w] = (np.sign(oth.mean()) if len(oth) else 1.0) * raw[w]
        res[f"baseline {name} (sign from the other wells)"] = {**summ(pd.Series(signed)), "concordance": {}}

    # ---- sensitivities of the primary to the label
    tt = t.copy()
    sens = {"Y + glauconite": (tt.sand + tt.glauc) / 100.0, "Y_coarse (sand + silt)": (tt.sand + tt.silt) / 100.0,
            "faded blocks included": tt.sand_with_faded / 100.0}
    for k in (-1, 1):  # one sample up or down: the label of the neighbouring bag in the well
        sh = np.full(len(Y), np.nan)
        for w in np.unique(wells):
            ix = np.flatnonzero(wells == w)
            ix = ix[np.argsort(d[ix])]
            sh[ix] = pd.Series(Y[ix]).shift(k).values
        sens[f"Y shifted {k:+d} bag"] = pd.Series(sh)
    for k, y in sens.items():
        y = np.asarray(y, float)
        sel = t_sel = (s1.in_S.values.astype(bool) & np.isfinite(y)) if k == "faded blocks included" else (S & np.isfinite(y))
        both(p2, f"P2 sensitivity: {k}", y=y, sel=sel)

    with open(OUT / "step3_results.json", "w") as f:
        json.dump(res, f, indent=1, default=float)
    pd.DataFrame({"well": wells, "depth_m": d, "in_S3": S, "Y": Y, "T1": s1.T1.values, "pred_P2": p2, "pred_P1": p1,
                  "pred_colour": pc}).to_csv(OUT / "step3_predictions.csv", index=False)
    for k, v in res.items():
        if isinstance(v, dict) and "median" in v:
            c = v["concordance"]
            print(f"{k:58s} med {v['median']:+.3f} pos {v['n_above']}/{v['n_wells']} p {v['wilcoxon_p']:.4f} "
                  f"CI [{v['boot95_median'][0]:+.2f},{v['boot95_median'][1]:+.2f}] | concord {c.get('median', np.nan):.3f} "
                  f"({c.get('n_above', 0)}/{c.get('n_wells', 0)}) p {c.get('wilcoxon_p', np.nan):.4f}")
        elif not isinstance(v, (dict, list)):
            print(k, v)
    print("P2 per well:", res["P2 PRIMARY step-1 R-D Si/Al prediction vs Y"]["per_well"])
    print("reference per well:", res["REFERENCE measured Si/Al vs Y (G3)"]["per_well"])
    print("claim_pass:", res["P2 PRIMARY step-1 R-D Si/Al prediction vs Y"]["claim_pass"])


def stage_c8():
    base, emb, wells, d, s1, t, S = load()
    g = pd.read_csv("results/v6/D_xrf_glauconite_bags.csv")[["well", "depth_m", "G"]]
    sc = pd.read_csv("results/v7/step2_g_scores.csv")[["well", "depth_m", "S", "GI"]]
    x = t.assign(depth_m=t.depth_m.round(2)).merge(g.assign(depth_m=g.depth_m.round(2)), on=["well", "depth_m"], how="left") \
         .merge(sc.assign(depth_m=sc.depth_m.round(2)), on=["well", "depth_m"], how="left")
    rows = []
    for w, q in x[np.isfinite(x.glauc)].groupby("well"):
        nz = int((q.glauc > 0).sum())
        r = {"well": w, "n_bags": len(q), "n_glauc_bags": nz}
        qg = q[np.isfinite(q.G)]
        if nz >= 10 and len(qg) >= 10:
            r["rho_glauc_G"] = spearmanr(qg.glauc, qg.G)[0]
            r["G_median_where_glauc"] = qg.G[qg.glauc > 0].median()
            r["G_median_elsewhere"] = qg.G[qg.glauc == 0].median()
            r["share_Ggt02_with_glauc"] = float((qg.glauc[qg.G > 0.2] > 0).mean()) if (qg.G > 0.2).any() else np.nan
            qs = qg[np.isfinite(qg.S)]
            r["rho_glauc_photoS"] = spearmanr(qs.glauc, qs.S)[0] if len(qs) >= 10 else np.nan
        rows.append(r)
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "C8_glauconite.csv", index=False)
    print(out.round(3).to_string(index=False))


if __name__ == "__main__":
    {"elig": stage_elig, "g3": stage_g3, "photo": stage_photo, "c8": stage_c8}[sys.argv[1]]()
