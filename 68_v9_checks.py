"""
v9 checks (V9_PLAN.md with the reviewer's amendments). All EXPLORATORY; each stage is run once.

  python 68_v9_checks.py k2b    deep mud-log test (v8 D) with the twin held out together, and drop-one-other reference
  python 68_v9_checks.py k2c    fine-tuned network at 34/8-3 without the sidetrack in training (after `59 trainx`)
  python 68_v9_checks.py k3     gamma-ray key for the digitised sand fraction (v8 D set and v7 step-3 set)

Nothing here changes a v7 or v8 file. Outputs: ~/sinkite_ml_work_v2/v9/.
"""
import json
import sys
from importlib import import_module

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

import config as C

M = import_module("52_v7_photo_to_xrf")
T = import_module("58_v7_mudlog_tests")
E = import_module("63_v8_elements_when")
JT = import_module("67_v8_jt_score")
EV = import_module("29_v2_evaluate")
OUT = C.WORK_DIR / "v9"
TWINS = ["34_8-3", "34_8-3_A"]


def dump(name, res):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / name, "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


def fit_predict_rd(X, y, ok, wells, held, drop=()):
    """R-D fitted on rows `ok` outside `held` and `drop`; prediction for `held`."""
    tr = ok & ~np.isin(wells, [held, *drop])
    te = ok & (wells == held)
    out = np.full(len(y), np.nan)
    out[te] = M.fit_rd(X[tr], y[tr]).predict(X[te])
    return out


# ----------------------------------------------------------------------------
# K2b
# ----------------------------------------------------------------------------
def k2b():
    wells, d, q, t, J, Lg = JT.load()
    base, emb, _, _, s1, S, L = E.load()
    grp = q.n_shoes_above.values
    el = pd.read_csv(JT.OUT / "jt_eligibility.csv")
    el = el[el.eligible].well.tolist()
    Y = t.Y.values
    # the pre-Tertiary model of v8 D, rebuilt exactly as 63.pre_tertiary
    rgb = emb["rgb"].astype(float)
    lsial = L["SI"] - L["AL"]
    has = np.isfinite(lsial)
    tert = d < np.array([E.XS.TOP_SHETLAND[w] for w in wells])
    P = ~tert & ~np.asarray(E.CM.shoe_mask(base)) & has
    okw = [w for w in np.unique(wells[P]) if (P & (wells == w)).sum() >= M.MIN_STRETCH]
    Pk = P & np.isin(wells, okw)
    TP = M.zwell(lsial, wells, P)
    X = M.zwell_mat(rgb, wells, P)
    ok = Pk & np.isfinite(TP) & np.isfinite(X).all(1)
    one = lambda pred, w: float(JT.per_well(pred, Y, wells, d, J, grp, [w]).get(w, np.nan))

    # reproduction of the predictions used in D (leave-one-well-out)
    base_rho, pred_lowo = {}, np.full(len(d), np.nan)
    for w in okw:
        p = fit_predict_rd(X, TP, ok, wells, w)
        pred_lowo[wells == w] = p[wells == w]
    m = np.isfinite(q.pred_P.values) & np.isfinite(pred_lowo)
    assert np.allclose(pred_lowo[m], q.pred_P.values[m], atol=1e-6), "v8 D predictions not reproduced"
    for w in el:
        base_rho[w] = one(pred_lowo, w)

    res = {"training wells of the pre-Tertiary model": okw, "eligible wells (amended test of v8 D)": el,
           "leave-one-well-out (as v8 D)": T.summ(pd.Series(base_rho))}
    # location-out: both twins held out together
    pred_loc = pred_lowo.copy()
    for w, other in (TWINS, TWINS[::-1]):
        p = fit_predict_rd(X, TP, ok, wells, w, drop=[other])
        pred_loc[wells == w] = p[wells == w]
    loc = JT.per_well(pred_loc, Y, wells, d, J, grp, el)
    r6 = T.summ(loc)
    tw = loc.copy()
    tw["34_8-3 pair"] = tw[TWINS].mean()
    r5 = T.summ(tw.drop(TWINS))
    res["location-out (34/8-3 and 34/8-3 A held out together), six wells"] = r6
    res["location-out, twins merged as one unit"] = r5

    # reference: each twin with one OTHER training well dropped, in turn
    ref, verdict = {}, {}
    for w, other in (TWINS, TWINS[::-1]):
        rows = {}
        for o in [x for x in okw if x not in TWINS]:
            rows[o] = one(fit_predict_rd(X, TP, ok, wells, w, drop=[o]), w)
        falls = {o: base_rho[w] - v for o, v in rows.items()}
        ref[w] = {"lowo": base_rho[w], "twin dropped": float(loc[w]), "fall when the twin is dropped": base_rho[w] - float(loc[w]),
                  "rho with one other well dropped": {o: round(v, 4) for o, v in rows.items()},
                  "largest fall from dropping one other well": float(max(falls.values())),
                  "which": max(falls, key=falls.get)}
        verdict[w] = bool(loc[w] >= 0.30 and ref[w]["fall when the twin is dropped"] <= ref[w]["largest fall from dropping one other well"])
    res["per twin"] = ref
    res["rule: both twins >= +0.30 and fall no larger than the largest drop-one-other fall"] = verdict
    res["wording"] = ("does not depend on the twin" if all(verdict.values())
                      else "depends in part on the twin being in training")
    dump("k2b_results.json", res)


# ----------------------------------------------------------------------------
# K2c
# ----------------------------------------------------------------------------
def k2c():
    X1 = C.WORK_DIR / "v7" / "x1"
    base, emb = EV.load_tables()
    s1 = pd.read_csv(C.WORK_DIR / "v7" / "step1_predictions.csv")
    wells, d = base.well.values, base.depth_m.values.astype(float)
    S = s1.in_S.values.astype(bool) & np.isfinite(s1.T1.values)
    T1 = s1.T1.values
    key = base[["well", "depth_m"]]
    rho_w = lambda pred, w: float(M.per_well_hp(pred, T1, wells, d, S & (wells == w)).get(w, np.nan))
    files = {0: "cnn_sial_predictions.csv", 1000: "cnn_sial_predictions_seed1000.csv", 2000: "cnn_sial_predictions_seed2000.csv"}
    nt = pd.read_csv(X1 / "cnn_sial_predictions_notwin.csv")
    res = {}
    for w in TWINS:
        rows = {}
        for sd, f in files.items():
            a = key.merge(pd.read_csv(X1 / f), on=["well", "depth_m"], how="left").p.values
            b = key.merge(nt[nt.seed == sd].drop(columns="seed"), on=["well", "depth_m"], how="left").p.values
            assert np.isfinite(b[S & (wells == w)]).all(), (w, sd)
            rows[sd] = {"with twin": rho_w(a, w), "without twin": rho_w(b, w)}
            rows[sd]["difference (with minus without)"] = rows[sd]["with twin"] - rows[sd]["without twin"]
        wt = [rows[s]["with twin"] for s in files]
        wo = [rows[s]["without twin"] for s in files]
        res[w] = {"by seed": rows, "mean with twin": float(np.mean(wt)), "mean without twin": float(np.mean(wo)),
                  "seed SD without twin": float(np.std(wo, ddof=1)), "all three seeds above zero without twin": bool(min(wo) > 0)}
    # frozen models with the same well removed
    other = dict([TWINS, TWINS[::-1]])
    fz = pd.read_pickle(X1 / "frozen_r18_bag_features.pkl")
    X18 = key.merge(fz, on=["well", "depth_m"], how="left").drop(columns=["well", "depth_m"]).values.astype(float)
    S18 = S & np.isfinite(X18).all(1)
    Z18 = M.zwell_mat(X18, wells, S18)
    Z50 = M.zwell_mat(emb["rgb"].astype(float), wells, S)
    ok50 = S & np.isfinite(Z50).all(1)
    for w in TWINS:
        chk = fit_predict_rd(Z50, T1, ok50, wells, w)
        mm = S & (wells == w)
        assert np.allclose(chk[mm], s1.pred_RD.values[mm], atol=1e-6), "step-1 R-D predictions not reproduced"
        res[w]["R-D (frozen ResNet-50)"] = {"with twin": rho_w(chk, w),
                                            "without twin": rho_w(fit_predict_rd(Z50, T1, ok50, wells, w, drop=[other[w]]), w)}
        res[w]["frozen ResNet-18 control"] = {"with twin": rho_w(fit_predict_rd(Z18, T1, S18, wells, w), w),
                                              "without twin": rho_w(fit_predict_rd(Z18, T1, S18, wells, w, drop=[other[w]]), w)}
    m, pos = res["34_8-3"]["mean without twin"], res["34_8-3"]["all three seeds above zero without twin"]
    res["wording for 34/8-3 (rule fixed in V9_PLAN)"] = (
        "does not depend on the sidetrack being in training" if (m >= 0.15 and pos)
        else "depends on the sidetrack being in training" if m <= 0.10 else "unclear")
    res["notes"] = ["seed SD at 34/8-3 with the twin was 0.10: a change below about 0.2 is within seed noise",
                    "removing a well also makes the training set one well smaller; not controlled",
                    "34/8-3 A fold: descriptive, no rule", "one well, singled out after X1; no p value"]
    dump("k2c_results.json", res)


# ----------------------------------------------------------------------------
# K3
# ----------------------------------------------------------------------------
def gr_interval_mean(wells, a, b):
    """Mean of the wireline gamma-ray curve over (a, b] for every bag; NaN without a curve or with < 3 samples."""
    L3 = import_module("03_make_labels")
    out, n = np.full(len(b), np.nan), np.zeros(len(b), int)
    for w in np.unique(wells):
        if w not in C.GR_SOURCES:
            continue
        rel, rng = C.GR_SOURCES[w]
        gr = L3.load_gr(C.SSD_ROOT / "Wells" / rel, rng)
        z, v = gr.index.values.astype(float), gr.values.astype(float)
        cs = np.concatenate([[0.0], np.cumsum(v)])
        for i in np.flatnonzero((wells == w) & np.isfinite(a) & np.isfinite(b)):
            lo, hi = np.searchsorted(z, a[i], side="right"), np.searchsorted(z, b[i], side="right")
            n[i] = hi - lo
            if hi - lo >= 3:
                out[i] = (cs[hi] - cs[lo]) / (hi - lo)
    return out, n


def neg_summ(s):
    """Per-well rho expected NEGATIVE: one-sided Wilcoxon (less), bootstrap CI of the median."""
    s = s.dropna()
    r = T.summ(-s)
    out = {"n_wells": r["n_wells"], "per_well": s.round(4).to_dict()}
    if "median" in r:
        out.update(median=-r["median"], n_below_zero=r["n_above"], wilcoxon_p_less=r["wilcoxon_p"],
                   boot95_median=[-r["boot95_median"][1], -r["boot95_median"][0]])
    return out


def k3():
    res = {"gamma ray": "mean of the composite wireline curve over the label's own interval (D_prev, D] (primary); "
                        "point value at D (descriptive)",
           "sheet check": "results/v9/k3_sheet_check.md: none of the eight sheets prints a gamma-ray track"}
    word = lambda r: ("the digitised sand fraction follows gamma ray"
                      if (r.get("median", 0) <= -0.20 and r.get("wilcoxon_p_less", 1) < 0.05)
                      else "no detectable agreement with gamma ray")

    # ---- set (i): v8 D, amended test (six wells)
    wells, d, q, t, J, Lg = JT.load()
    base, _ = EV.load_tables()
    grp = q.n_shoes_above.values
    el = pd.read_csv(JT.OUT / "jt_eligibility.csv")
    el = el[el.eligible].well.tolist()
    Y = t.Y.values
    lab = pd.read_csv(JT.OUT / "jt_bag_labels_A.csv")
    lab["depth_m"] = lab.depth_m.round(2)
    a = pd.DataFrame({"well": wells, "depth_m": np.round(d, 2)}).merge(lab[["well", "depth_m", "a"]], on=["well", "depth_m"], how="left").a.values
    grm, ns = gr_interval_mean(wells, a.astype(float), d)
    pw = lambda x, y, sel: JT.per_well(x, y, wells, d, sel, grp, el)
    n_no = {w: int((J & (wells == w) & ~np.isfinite(grm)).sum()) for w in el}
    r = neg_summ(pw(grm, Y, J))
    clean = J & ~((t.carb.values + t.marl.values >= 30) | (t.coal.values > 0))
    res["D set (below base Cretaceous, six wells)"] = {
        "bags per well": {w: int((J & (wells == w) & np.isfinite(grm)).sum()) for w in el},
        "bags without gamma ray": n_no, "median samples per interval": float(np.median(ns[J & np.isfinite(grm)])),
        "KEY: sand fraction vs interval-mean gamma ray": r, "wording": word(r),
        "descriptive: sand fraction vs point gamma ray at D": neg_summ(pw(base.gr.values.astype(float), Y, J)),
        "descriptive: without bags with carbonate+marl >= 30 % or any coal": neg_summ(pw(grm, Y, clean)),
        "reference: measured Si/Al vs interval-mean gamma ray": neg_summ(pw(grm, q.T1_J.values, J)),
        "reference (not independent of gamma ray): photo prediction vs interval-mean gamma ray": neg_summ(pw(grm, q.pred_P.values, J))}

    # ---- set (ii): v7 step 3, Tertiary test of record (six wells)
    base, emb, wells, d, s1, t, S = T.load()
    lab = pd.read_csv(T.OUT / "bag_labels_A.csv")
    lab["depth_m"] = lab.depth_m.round(2)
    a = pd.DataFrame({"well": wells, "depth_m": np.round(d, 2)}).merge(lab[["well", "depth_m", "a"]], on=["well", "depth_m"], how="left").a.values
    e = pd.read_csv(T.OUT / "C4_eligibility.csv")
    el = e[e.eligible].well.tolist()
    Y = t.Y.values
    _, _, nshoe = E.masks(base, wells, d)
    grm, ns = gr_interval_mean(wells, a.astype(float), d)

    def pw3(x, y, split=True):
        out = {}
        for w in el:
            m = S & (wells == w) & np.isfinite(x) & np.isfinite(y)
            if m.sum() >= T.MIN_BAGS:
                g = nshoe[m] if split else None
                out[w] = M.rho(M.highpass(d[m], x[m], groups=g), M.highpass(d[m], y[m], groups=g))
        return pd.Series(out, dtype=float)

    r = neg_summ(pw3(grm, Y))
    res["Tertiary set (v7 step 3, six wells)"] = {
        "bags per well": {w: int((S & (wells == w) & np.isfinite(grm) & np.isfinite(Y)).sum()) for w in el},
        "bags without gamma ray": {w: int((S & (wells == w) & np.isfinite(Y) & ~np.isfinite(grm)).sum()) for w in el},
        "KEY: sand fraction vs interval-mean gamma ray (stretches split at casing shoes)": r, "wording": word(r),
        "descriptive: step 3's own high-pass (no split at shoes)": neg_summ(pw3(grm, Y, split=False)),
        "descriptive: sand fraction vs point gamma ray at D": neg_summ(pw3(base.gr.values.astype(float), Y)),
        "reference: measured Si/Al vs interval-mean gamma ray": neg_summ(pw3(grm, s1.T1.values)),
        "reference (not independent of gamma ray): photo prediction vs interval-mean gamma ray": neg_summ(pw3(grm, s1.pred_RD.values))}
    res["limits"] = ["gamma ray is not sand: mica, potassium feldspar and heavy minerals raise it in sandstone; coal and limestone lower it",
                     "Tertiary: glauconitic sands and tuffs raise gamma ray, so a weak negative is expected",
                     "the composite curve does not name its runs: open-hole and through-casing gamma ray cannot be told apart from the file",
                     "agreement supports the whole chain (wellsite geologist, sheet, reader, bag join), not the reader alone",
                     "this is an instrument key, not a human key"]
    dump("k3_results.json", res)


if __name__ == "__main__":
    {"k2b": k2b, "k2c": k2c, "k3": k3}[sys.argv[1]]()
