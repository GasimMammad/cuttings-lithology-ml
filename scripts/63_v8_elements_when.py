"""
v8 parts A and B (V8_PLAN.md with the reviewer amendments), and the frozen
photograph predictions for part D.

  A  more elements from the same photographs (K, Fe, Ca, Ti, Zr over Al)
  B  when does the step-1 model work (spread of the chemistry)
  preT  pre-Tertiary R-D predictions for part D, saved before any tile is read

Run:  python 63_v8_elements_when.py A | B | preT
"""
import itertools
import json
import sys
from importlib import import_module

import lasio
import numpy as np
import pandas as pd
from scipy.stats import rankdata, wilcoxon

import config as C
from features import FEATURE_NAMES

M = import_module("52_v7_photo_to_xrf")
XS, CM, EV = M.XS, M.CM, M.EV
OUT = C.WORK_DIR / "v8"
EL = ["SI", "AL", "K", "FE", "CA", "TI", "ZR", "SR", "BA", "CL", "S"]
TARGETS = ["K", "FE", "CA", "TI", "ZR"]
EXTRA_CTRL = {"CA": ["S"], "ZR": ["SR"]}
WIN_M, WIN_MIN, MIN_WIN = 150.0, 15, 5
BCU = {"34_4-6": 2577, "34_4-7": 2502, "34_7-10": 2400, "34_7-4": 2517, "34_7-9": 2443, "34_8-3": 2827,
       "34_8-3_A": 3003}  # base Cretaceous, Sodir lithostratigraphy (results/v8/sodir_litho_tops.csv)
lowo = lambda w: w


def sodir(w):
    return w.replace("_", "/").replace("/A", " A")


def xrf(base):
    out = pd.DataFrame(np.nan, index=base.index, columns=EL)
    for w in base.well.unique():
        f = C.SSD_ROOT / "Wells" / w / "DRILLING" / f"{w}_CUTTINGS_XRF_1.LAS"
        if not f.exists():
            continue
        t = lasio.read(str(f), engine="normal").df()[EL]
        t.index = np.round(t.index.values.astype(float), 2)
        t = t[~t.index.duplicated()]
        m = (base.well == w).values
        out.loc[m, EL] = t.reindex(np.round(base.depth_m.values[m], 2)).values
    return out


def logs(x):
    """log10 of each element; non-detects (<= 0) are missing. Cl and S as controls keep step 1's log10(v + 1)."""
    L = {}
    for e in EL:
        v = x[e].values.astype(float)
        L[e] = np.log10(v + 1.0) if e in ("CL", "S") else np.where(v > 0, np.log10(np.where(v > 0, v, 1.0)), np.nan)
    return L


def load():
    base, emb = EV.load_tables()
    wells, d = base.well.values, base.depth_m.values.astype(float)
    s1 = pd.read_csv(C.WORK_DIR / "v7" / "step1_predictions.csv")
    assert (s1.well.values == wells).all() and np.allclose(s1.depth_m.values, d)
    S = s1.in_S.values.astype(bool) & np.isfinite(s1.T1.values)
    return base, emb, wells, d, s1, S, logs(xrf(base))


def hpw(v, d, m):
    out = np.full(len(v), np.nan)
    out[m] = M.highpass(d[m], v[m])
    return out


def holm(p):
    p = pd.Series(p)
    o = p.sort_values()
    adj = np.maximum.accumulate([(len(o) - i) * v for i, v in enumerate(o.values)])
    return pd.Series(np.minimum(adj, 1.0), index=o.index).reindex(p.index)


def wil(s, alt="greater"):
    s = pd.Series(s).dropna()
    return float(wilcoxon(s.values, alternative=alt).pvalue) if len(s) >= 5 and (s != 0).any() else np.nan


def exact_perm_p(a, b):
    """Exact one-sided permutation p of the Spearman correlation (all n! pairings)."""
    ra, rb = rankdata(a), rankdata(b)
    obs = float((ra * rb).sum())
    it = itertools.permutations(range(len(a)))
    hit = tot = 0
    while True:
        ch = np.fromiter(itertools.chain.from_iterable(itertools.islice(it, 500000)), dtype=np.int8)
        if ch.size == 0:
            break
        P = ch.reshape(-1, len(a))
        hit += int(((rb[P] * ra).sum(1) >= obs - 1e-9).sum())
        tot += len(P)
    return hit / tot


def mad(v):
    v = v[np.isfinite(v)]
    return float(np.median(np.abs(v - np.median(v)))) if len(v) else np.nan


# ------------------------------------------------------------------ part A
def part_a():
    base, emb, wells, d, s1, S, L = load()
    W = np.unique(wells[S])
    X_RD = M.zwell_mat(emb["rgb"].astype(float), wells, S)
    X_RE = M.zwell_mat(base[FEATURE_NAMES].values.astype(float), wells, S,
                       base[["ref_" + c for c in FEATURE_NAMES]].values.astype(float))
    pT1 = s1.pred_RD.values
    res, per, preds = {}, {}, {"well": wells, "depth_m": d, "in_S": S}
    for e in TARGETS:
        T = M.zwell(L[e] - L["AL"], wells, S & np.isfinite(L[e]))
        ok = S & np.isfinite(T)
        p, _ = M.cv_predict(X_RD, T, wells, d, ok, "RD", lowo)
        pe, _ = M.cv_predict(X_RE, T, wells, d, ok, "RE", lowo)
        preds[f"T_{e}"], preds[f"pred_{e}"] = T, p
        r = {}
        rows = {k: {} for k in ("rho", "mud", "beyond", "given_T1", "t1model_raw", "RE")}
        for w in W:
            m = ok & (wells == w) & np.isfinite(p)
            if m.sum() < M.MIN_STRETCH:
                continue
            hp = lambda v: M.highpass(d[m], v[m])
            hp_p, hp_t = hp(p), hp(T)
            rows["rho"][w] = M.rho(hp_p, hp_t)
            mud = [hp(L["BA"]), hp(L["CL"])] + [hp(L[c]) for c in EXTRA_CTRL.get(e, [])]
            rows["mud"][w] = M.partial_rho(hp_p, hp_t, np.column_stack(mud))
            rows["beyond"][w] = M.partial_rho(hp_p, hp_t, np.column_stack([hp(L["SI"]), hp(L["AL"])]))
            rows["given_T1"][w] = M.partial_rho(hp_p, hp_t, np.column_stack([hp(s1.T1.values)]))
            rows["t1model_raw"][w] = M.rho(hp(pT1), hp_t)
            rows["RE"][w] = M.rho(hp(pe), hp_t)
        t = pd.DataFrame(rows)
        # Si/Al model reused, sign fixed from the other wells
        t["t1model"] = [np.sign(t.t1model_raw.drop(w).mean()) * t.t1model_raw[w] for w in t.index]
        per[e] = t
        r["n_wells"] = int(len(t))
        r["rho"] = M.summarise(t.rho)
        for k in ("mud", "beyond", "given_T1"):
            r[k] = {"median": float(t[k].median()), "n_pos": int((t[k] > 0).sum()), "wilcoxon_p": wil(t[k])}
        r["specificity: own model minus Si/Al model (sign from other wells)"] = {
            "median_own": float(t.rho.median()), "median_t1model": float(t.t1model.median()),
            "paired_p": wil(t.rho - t.t1model)}
        r["colour baseline R-E"] = {"median": float(t.RE.median()), "paired_RD_gt_RE_p": wil(t.rho - t.RE)}
        res[e + "/Al"] = r
    hp_pass = holm({e: res[e + "/Al"]["rho"]["wilcoxon_p"] for e in TARGETS})
    hb = holm({e: res[e + "/Al"]["beyond"]["wilcoxon_p"] for e in TARGETS})
    counting = []
    for e in TARGETS:
        r = res[e + "/Al"]
        r["holm_p"] = float(hp_pass[e])
        r["passes"] = bool(r["holm_p"] < 0.05 and r["rho"]["median_rho"] >= 0.10)
        r["beyond"]["holm_p"] = float(hb[e])
        b_ok = bool(r["beyond"]["median"] >= 0.05 and r["beyond"]["holm_p"] < 0.05)
        m_ok = bool(r["mud"]["median"] >= 0.05 and np.sign(r["mud"]["median"]) == np.sign(r["rho"]["median_rho"]))
        r["counts"] = bool(r["passes"] and b_ok and m_ok)
        r["criteria"] = {"a_passes": r["passes"], "b_beyond_Si_and_Al": b_ok, "c_mud_partial": m_ok}
        if r["counts"]:
            counting.append(e)
    n_pass = sum(res[e + "/Al"]["passes"] for e in TARGETS)
    res["summary"] = {"n_pass": int(n_pass), "counting_targets": counting,
                      "wording": ("a rough chemical log" if len(counting) >= 2 else
                                  "the photographs see one chemical axis; the other elements follow it" if n_pass else
                                  "no evidence beyond Si/Al")}
    flags = {}
    for w in W:
        m = S & (wells == w)
        hp = lambda v: M.highpass(d[m], v[m])
        flags[w] = {"rho_K_Cl": M.rho(hp(L["K"]), hp(L["CL"])), "rho_Fe_Ti": M.rho(hp(L["FE"]), hp(L["TI"]))}
    res["flags (high-passed, per well)"] = flags
    OUT.mkdir(parents=True, exist_ok=True)
    pd.concat(per, axis=1).round(4).to_csv(OUT / "A_per_well.csv")
    pd.DataFrame(preds).to_csv(OUT / "A_predictions.csv", index=False)
    with open(OUT / "A_results.json", "w") as f:
        json.dump(res, f, indent=1, default=float)
    for e in TARGETS:
        r = res[e + "/Al"]
        print(f"{e}/Al: median rho {r['rho']['median_rho']:+.3f} ({r['rho']['n_pos']}/{r['n_wells']}), Holm p {r['holm_p']:.4f}, "
              f"mud {r['mud']['median']:+.3f}, beyond Si&Al {r['beyond']['median']:+.3f} (Holm p {r['beyond']['holm_p']:.4f}), "
              f"given T1 {r['given_T1']['median']:+.3f}, Si/Al model {r['specificity: own model minus Si/Al model (sign from other wells)']['median_t1model']:+.3f} "
              f"(paired p {r['specificity: own model minus Si/Al model (sign from other wells)']['paired_p']:.3f}), "
              f"R-E {r['colour baseline R-E']['median']:+.3f} (paired p {r['colour baseline R-E']['paired_RD_gt_RE_p']:.3f}), counts {r['counts']}")
    print(json.dumps(res["summary"], indent=1))
    print(pd.DataFrame(flags).T.round(2).to_string())


# ------------------------------------------------------------------ part B
def windows(d, hp_p, hp_y, hp_raw):
    """Consecutive WIN_M windows from the top of each continuous stretch."""
    sid = M.stretch_ids(d)
    out = []
    for s in np.unique(sid):
        ix = np.flatnonzero(sid == s)
        k = np.floor((d[ix] - d[ix].min()) / WIN_M).astype(int)
        for j in np.unique(k):
            i = ix[k == j]
            ok = np.isfinite(hp_p[i]) & np.isfinite(hp_y[i])
            if ok.sum() >= WIN_MIN:
                out.append({"top": float(d[i].min()), "n": int(ok.sum()), "rho": M.rho(hp_p[i], hp_y[i]),
                            "mad_meas": mad(hp_raw[i]), "mad_pred": mad(hp_p[i])})
    return pd.DataFrame(out)


def part_b():
    base, emb, wells, d, s1, S, L = load()
    raw = L["SI"] - L["AL"]
    p, T1 = s1.pred_RD.values, s1.T1.values
    rows, win, b2, b3 = {}, [], {}, {}
    for w in np.unique(wells[S]):
        m = S & (wells == w) & np.isfinite(p)
        dd = d[m]
        hp_p, hp_y, hp_raw = M.highpass(dd, p[m]), M.highpass(dd, T1[m]), M.highpass(dd, raw[m])
        rows[w] = {"rho": M.rho(hp_p, hp_y), "mad_meas": mad(hp_raw), "mad_pred": mad(hp_p), "n_bags": int(m.sum()),
                   "median_spacing_m": float(np.median(np.diff(np.sort(dd)))), "mean_logBa": float(np.nanmean(L["BA"][m]))}
        t = windows(dd, hp_p, hp_y, hp_raw).assign(well=w)
        win.append(t)
        if len(t) >= MIN_WIN:
            b2[w] = M.rho(t.rho.values, t.mad_meas.values) if len(t) >= 10 else float(pd.Series(t.rho).corr(t.mad_meas, method="spearman"))
            b3[w] = M.rho(t.rho.values, t.mad_pred.values) if len(t) >= 10 else float(pd.Series(t.rho).corr(t.mad_pred, method="spearman"))
    t = pd.DataFrame(rows).T
    win = pd.concat(win)
    sp = lambda a, b: float(pd.Series(a).corr(pd.Series(b), method="spearman"))
    res = {"B1 between wells: rho vs MAD of measured hp log10(Si/Al)":
               {"spearman": sp(t.rho.values, t.mad_meas.values), "exact_perm_p_one_sided": exact_perm_p(t.rho.values, t.mad_meas.values), "n": int(len(t))},
           "B1 descriptive: rho vs n_bags / spacing / mean log Ba":
               {k: sp(t.rho.values, t[k].values) for k in ("n_bags", "median_spacing_m", "mean_logBa")},
           "B2 within wells: window rho vs window MAD (measured)":
               {"per_well": {k: round(v, 4) for k, v in b2.items()}, "median": float(np.nanmedian(list(b2.values()))),
                "n_pos": int(sum(v > 0 for v in b2.values())), "n_wells": len(b2), "wilcoxon_p": wil(pd.Series(b2)),
                "windows_per_well": win.groupby("well").size().to_dict()},
           "B3 label-free, between wells: rho vs MAD of hp prediction":
               {"spearman": sp(t.rho.values, t.mad_pred.values), "exact_perm_p_one_sided": exact_perm_p(t.rho.values, t.mad_pred.values)},
           "B3 label-free, within wells: window rho vs window MAD (prediction)":
               {"per_well": {k: round(v, 4) for k, v in b3.items()}, "median": float(np.nanmedian(list(b3.values()))),
                "n_pos": int(sum(v > 0 for v in b3.values())), "wilcoxon_p": wil(pd.Series(b3))}}
    # B4: Tertiary against pre-Tertiary (step-1 sets; separately trained models)
    f = OUT / "preT_predictions.csv"
    if f.exists():
        q = pd.read_csv(f)
        b4 = {}
        for w in np.unique(wells[q.in_P.values]):
            m = q.in_P.values & (wells == w) & np.isfinite(q.pred_P.values)
            if m.sum() < M.MIN_STRETCH or w not in t.index:
                continue
            dd = d[m]
            b4[w] = {"rho_T": float(t.rho[w]), "rho_preT": M.rho(M.highpass(dd, q.pred_P.values[m]), M.highpass(dd, q.T1_P.values[m])),
                     "mad_T": float(t.mad_meas[w]), "mad_preT": mad(M.highpass(dd, raw[m]))}
        b = pd.DataFrame(b4).T
        same = np.sign(b.rho_preT - b.rho_T) == np.sign(b.mad_preT - b.mad_T)
        res["B4 Tertiary vs pre-Tertiary (descriptive)"] = {"per_well": b.round(4).to_dict(orient="index"),
                                                            "n_same_sign": int(same.sum()), "n_wells": int(len(b))}
    b1s, b2r = res["B1 between wells: rho vs MAD of measured hp log10(Si/Al)"], res["B2 within wells: window rho vs window MAD (measured)"]
    follows = bool(b2r["wilcoxon_p"] < 0.05 and b1s["spearman"] > 0 and b2r["median"] > 0)
    rule = bool(follows and res["B3 label-free, within wells: window rho vs window MAD (prediction)"]["wilcoxon_p"] < 0.05)
    res["wording"] = ("skill follows the spread of the chemistry" + ("; a label-free rule of thumb is supported" if rule else
                      "; no label-free rule of thumb")) if follows else "no usable predictor of where it works was found (11 wells)"
    OUT.mkdir(parents=True, exist_ok=True)
    t.round(4).to_csv(OUT / "B_per_well.csv")
    win.round(4).to_csv(OUT / "B_windows.csv", index=False)
    with open(OUT / "B_results.json", "w") as f2:
        json.dump(res, f2, indent=1, default=float)
    print(t.round(3).to_string())
    print(json.dumps(res, indent=1, default=float))


# ------------------------------------------------------------------ part D predictions
def masks(base, wells, d):
    cas = pd.read_csv("results/v3/sodir_casing_table.csv")
    cas["wlbName"] = cas.wlbName.str.strip()
    cas = cas[cas.wlbCasingType.str.strip().isin(["CONDUCTOR", "SURF.COND.", "INTERM.", "LINER"])]
    core = pd.read_csv("results/v4/sodir_core_table.csv")
    core["wlbName"] = core.wlbName.str.strip()
    shoe, cored, nshoe = np.zeros(len(d), bool), np.zeros(len(d), bool), np.zeros(len(d), int)
    for w in np.unique(wells):
        sel = wells == w
        for s in np.unique(cas[cas.wlbName == sodir(w)].wlbCasingDepth.values):
            shoe |= sel & (d >= s) & (d <= s + CM.MASK_M)
            nshoe[sel & (d >= s)] += 1
        for a, b in core[core.wlbName == sodir(w)][["wlbCoreIntervalTop", "wlbCoreIntervalBottom"]].values:
            cored |= sel & (d >= a) & (d <= b)
    return shoe, cored, nshoe


def pre_tertiary():
    """Photograph predictions for part D. Uses photographs and XRF only; no mud-log label exists yet."""
    base, emb, wells, d, s1, S, L = load()
    rgb = emb["rgb"].astype(float)
    E15 = base[FEATURE_NAMES].values.astype(float)
    R15 = base[["ref_" + c for c in FEATURE_NAMES]].values.astype(float)
    lsial = L["SI"] - L["AL"]
    has = np.isfinite(lsial)
    tert = d < np.array([XS.TOP_SHETLAND[w] for w in wells])
    # set P exactly as step 1's "pre-Tertiary, descriptive" block
    P = ~tert & ~np.asarray(CM.shoe_mask(base)) & has
    okw = [w for w in np.unique(wells[P]) if (P & (wells == w)).sum() >= M.MIN_STRETCH]
    Pk = P & np.isin(wells, okw)
    TP = M.zwell(lsial, wells, P)
    pP, _ = M.cv_predict(M.zwell_mat(rgb, wells, P), TP, wells, d, Pk, "RD", lowo)
    pPre, _ = M.cv_predict(M.zwell_mat(E15, wells, P, R15), TP, wells, d, Pk, "RE", lowo)
    TCa = M.zwell(L["CA"] - L["AL"], wells, P & np.isfinite(L["CA"]))
    pCa, _ = M.cv_predict(M.zwell_mat(rgb, wells, P), TCa, wells, d, Pk & np.isfinite(TCa), "RD", lowo)
    chk = M.per_well_hp(pP, TP, wells, d, Pk)
    ref = json.load(open("results/v7/step1_results.json"))["pre-Tertiary (descriptive)"]["per_well"]
    assert all(abs(chk[w] - v) < 1e-3 for w, v in ref.items()), (chk.round(4).to_dict(), ref)
    # range of part D: below base Cretaceous, shoe mask with liners, Sodir cores out
    shoe, cored, nshoe = masks(base, wells, d)
    J = np.array([w in BCU and dd >= BCU[w] for w, dd in zip(wells, d)]) & has & ~shoe & ~cored
    TJ = M.zwell(lsial, wells, J)
    pJ, _ = M.cv_predict(M.zwell_mat(rgb, wells, J), TJ, wells, d, J, "RD", lowo)
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"well": wells, "depth_m": d, "in_P": Pk, "T1_P": TP, "pred_P": pP, "pred_P_RE": pPre,
                  "T_CaAl_P": TCa, "pred_P_CaAl": pCa, "in_J": J, "T1_J": TJ, "pred_J": pJ,
                  "n_shoes_above": nshoe, "cored": cored}).to_csv(OUT / "preT_predictions.csv", index=False)
    print("step-1 pre-Tertiary per-well rho reproduced:", chk.round(4).to_dict())
    print("bags in range J per well:", pd.Series(wells[J]).value_counts().sort_index().to_dict())


if __name__ == "__main__":
    {"A": part_a, "B": part_b, "preT": pre_tertiary}[sys.argv[1]]()
