"""
v10 part S (V10_PLAN.md with the review amendments): photo stratigraphy.
Major tops in a held-out location from bag photographs, against Sodir group tops. Run once.

  python 70_v10_strat.py          writes ~/sinkite_ml_work_v2/v10/S_results.json and S_tops.csv
"""
import json
from importlib import import_module

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import config as C

M = import_module("52_v7_photo_to_xrf")
E = import_module("63_v8_elements_when")
OUT = C.WORK_DIR / "v10"
UNITS = ["Nordland", "Hordaland", "Rogaland", "Cretaceous", "below base Cretaceous"]
BOUND = ["top Hordaland", "top Rogaland", "top Cretaceous", "base Cretaceous"]
MEGA = {"NORDLAND GP": 0, "HORDALAND GP": 1, "ROGALAND GP": 2, "SHETLAND GP": 3, "CROMER KNOLL GP": 3}
TWINS = ["34_8-3", "34_8-3_A"]
LOC = lambda w: "34_8-3" if w in TWINS else w
MIN_SIDE, NEAR_M = 10, 70.0
# mud-system changes printed in the mud-log headers (results/v9/k3_sheet_check.md); other wells: shoes only
MUD_CHANGE = {"34_4-7": [470, 915, 2423], "34_7-10": [428, 918, 2413], "34_7-4": [972, 1930, 2756],
              "34_7-9": [471, 915, 2250], "34_8-3": [1317], "34_8-3_A": []}
XRF_EL = ["SI", "K", "FE", "CA", "TI", "ZR", "SR"]


def reference(wells_u):
    s = pd.read_csv("results/v10/sodir_litho_11wells.csv")
    s["wlbName"], s["lsuName"] = s.wlbName.str.strip(), s.lsuName.str.strip()
    g = s[s.lsuLevel.str.strip() == "GROUP"]
    wb = pd.read_csv("results/v10/sodir_wellbores_11wells.csv")
    wb["n"] = wb.wlbWellboreName.str.strip()
    cas = pd.read_csv("results/v3/sodir_casing_table.csv", encoding="utf-8-sig")
    cas["wlbName"] = cas.wlbName.str.strip()
    ref = {}
    for w in wells_u:
        x = g[g.wlbName == E.sodir(w)].sort_values("lsuTopDepth")
        assert len(x), w
        r = wb[wb.n == E.sodir(w)].iloc[0]
        tops = {}
        for k in range(4):
            below = x[[MEGA.get(n, 4) > k for n in x.lsuName]]
            if len(below):
                tops[k] = float(below.lsuTopDepth.min())
        ev = sorted(set(float(v) for v in cas[cas.wlbName == E.sodir(w)].wlbCasingDepth.values) | set(map(float, MUD_CHANGE.get(w, []))))
        ref[w] = {"groups": x, "tops": tops, "kb": float(r.wlbKellyBushElevation), "wd": float(r.wlbWaterDepth),
                  "xy": (float(r.wlbEwUtm), float(r.wlbNsUtm)), "events": ev}
    return ref


def unit_of(d, groups):
    m = np.full(len(d), 4)
    for r in groups.itertuples():
        m[(d > r.lsuTopDepth) & (d <= r.lsuBottomDepth)] = MEGA.get(r.lsuName, 4)
    m[d <= groups.lsuTopDepth.min()] = 0
    last = groups.sort_values("lsuBottomDepth").iloc[-1]  # a bag just below the last listed base keeps that unit
    m[d > last.lsuBottomDepth] = MEGA.get(last.lsuName, 4)
    return m


def segment(logp):
    """Unit sequence maximising the summed log probability; going down, the unit stays or moves to the next."""
    n, k = logp.shape
    dp, bk = np.full((n, k), -np.inf), np.zeros((n, k), int)
    dp[0] = logp[0]
    for i in range(1, n):
        for c in range(k):
            a, b = dp[i - 1, c], (dp[i - 1, c - 1] if c > 0 else -np.inf)
            bk[i, c] = c if a >= b else c - 1
            dp[i, c] = logp[i, c] + max(a, b)
    c = int(np.argmax(dp[-1]))
    seq = np.zeros(n, int)
    for i in range(n - 1, -1, -1):
        seq[i] = c
        c = bk[i, c]
    return seq


def picks(d, seq):
    """Predicted depth of each boundary; flag when no bag is assigned to a deeper unit."""
    out = {}
    for k in range(4):
        ix = np.flatnonzero(seq > k)
        if len(ix) == 0:
            out[k] = (float(d[-1]), "none deeper")
        elif ix[0] == 0:
            out[k] = (float(d[0]), "all deeper")
        else:
            out[k] = (float((d[ix[0] - 1] + d[ix[0]]) / 2), "")
    return out


def fit_clf(X, y):
    p = make_pipeline(StandardScaler(), PCA(n_components=min(32, X.shape[1]), random_state=0),
                      LogisticRegression(C=1.0, class_weight="balanced", max_iter=5000))
    return p.fit(X, y)


def run_model(Z, ok, wells, d, unit, ref):
    """Leave one location out; returns per-well unit sequence and picked tops."""
    res, bag = {}, []
    for loc in sorted(set(LOC(w) for w in np.unique(wells))):
        held = [w for w in np.unique(wells) if LOC(w) == loc]
        tr = ok & ~np.isin(wells, held)
        clf = fit_clf(Z[tr], unit[tr])
        assert list(clf.classes_) == [0, 1, 2, 3, 4]
        for w in held:
            ix = np.flatnonzero(ok & (wells == w))
            ix = ix[np.argsort(d[ix], kind="stable")]
            lp = clf.predict_log_proba(Z[ix])
            seq = segment(lp)
            res[w] = picks(d[ix], seq)
            bag.append(pd.DataFrame({"well": w, "depth_m": d[ix], "unit": unit[ix], "pred_unit": seq, "argmax_unit": lp.argmax(1)}))
    return res, pd.concat(bag)


def summarise(t, col, base_col=None, loc_wells=None):
    """Per-location median error; paired one-sided Wilcoxon against a baseline column."""
    x = t if loc_wells is None else t[t.well.isin(loc_wells)]
    g = x.groupby("well")
    r = {"n_tops": int(len(x)), "n_locations": int(g.ngroups), "median_error_m": float(x[col].median()),
         "median_of_location_medians_m": float(g[col].median().median()), "share_within_30m": float((x[col] <= 30).mean()),
         "per_location_median_m": g[col].median().round(1).to_dict()}
    if base_col is not None and g.ngroups >= 5:
        a, b = g[col].median(), g[base_col].median()
        r["wins (location median smaller)"] = int((a < b).sum())
        r["p_better"] = float(wilcoxon(a - b, alternative="less").pvalue)
        r["p_worse"] = float(wilcoxon(a - b, alternative="greater").pvalue)
        r["median_paired_difference_m"] = float((a - b).median())
    return r


def main():
    base, emb, wells, d, s1, S, L = E.load()
    wells_u = sorted(np.unique(wells))
    ref = reference(wells_u)
    unit = np.zeros(len(d), int)
    for w in wells_u:
        unit[wells == w] = unit_of(d[wells == w], ref[w]["groups"])
    allrows = np.ones(len(d), bool)

    # evaluated tops (labels only)
    tops = []
    for w in wells_u:
        dw, uw = d[wells == w], unit[wells == w]
        for k, t in ref[w]["tops"].items():
            if dw.min() < t < dw.max() and (uw == k).sum() >= MIN_SIDE and (uw == k + 1).sum() >= MIN_SIDE:
                near_d = np.sort(dw)[np.abs(np.sort(dw) - t) <= 100]
                sp = float(np.median(np.diff(near_d))) if len(near_d) > 2 else np.nan
                ev = ref[w]["events"]
                e = min(ev, key=lambda v: abs(v - t)) if ev else np.nan
                tops.append({"well": w, "k": k, "boundary": BOUND[k], "true_m": t, "bag_spacing_m": sp, "event_m": e,
                             "event_dist_m": abs(e - t) if ev else np.nan})
    T = pd.DataFrame(tops)

    # baselines (no photographs)
    prim = [w for w in wells_u if w != "34_8-3_A"]
    for i, r in T.iterrows():
        w, k = r.well, r.k
        others = [o for o in prim if LOC(o) != LOC(w) and k in ref[o]["tops"]]
        bsf = np.median([ref[o]["tops"][k] - ref[o]["kb"] - ref[o]["wd"] for o in others])
        T.loc[i, "regional_m"] = bsf + ref[w]["kb"] + ref[w]["wd"]
        o = min(others, key=lambda o: np.hypot(ref[o]["xy"][0] - ref[w]["xy"][0], ref[o]["xy"][1] - ref[w]["xy"][1]))
        T.loc[i, "offset_well"] = o
        T.loc[i, "offset_km"] = np.hypot(ref[o]["xy"][0] - ref[w]["xy"][0], ref[o]["xy"][1] - ref[w]["xy"][1]) / 1000
        T.loc[i, "offset_m"] = ref[o]["tops"][k] - ref[o]["kb"] + ref[w]["kb"]

    # photo model
    Zp = M.zwell_mat(emb["rgb"].astype(float), wells, allrows)
    okp = np.isfinite(Zp).all(1)
    pk, bags = run_model(Zp, okp, wells, d, unit, ref)
    # measured chemistry (reference row)
    Xc = np.column_stack([L[e] - L["AL"] for e in XRF_EL])
    okc = np.isfinite(Xc).all(1)
    Zc = M.zwell_mat(Xc, wells, okc)
    pc, _ = run_model(Zc, okc, wells, d, unit, ref)
    for i, r in T.iterrows():
        T.loc[i, "photo_m"], T.loc[i, "photo_flag"] = pk[r.well][r.k]
        T.loc[i, "xrf_m"] = pc[r.well][r.k][0]
    for c in ("photo", "regional", "offset", "xrf"):
        T[f"err_{c}"] = (T[f"{c}_m"] - T.true_m).abs()
    T["signed_photo"] = T.photo_m - T.true_m
    T["err_photo_bags"] = T.err_photo / T.bag_spacing_m
    T["near"] = T.event_dist_m <= NEAR_M
    T["err_event"] = T.event_dist_m
    T["pick_closer_to_event"] = (T.photo_m - T.event_m).abs() < T.err_photo
    T["no_closer_than_event_baseline"] = T.err_photo >= T.err_event
    OUT.mkdir(parents=True, exist_ok=True)
    T.round(2).to_csv(OUT / "S_tops.csv", index=False)
    bags.to_csv(OUT / "S_bag_units.csv", index=False)

    P = T[T.well.isin(prim)]
    res = {"n_evaluated_tops": {"10 primary wells": int(len(P)), "34_8-3_A (descriptive)": int((T.well == "34_8-3_A").sum())},
           "photo": summarise(P, "err_photo"),
           "S2 PRIMARY photo vs offset well": summarise(P, "err_photo", "err_offset"),
           "S1 secondary photo vs regional prognosis": summarise(P, "err_photo", "err_regional"),
           "baseline offset well": summarise(P, "err_offset"), "baseline regional": summarise(P, "err_regional"),
           "reference: measured XRF chemistry, same method": summarise(P, "err_xrf"),
           "photo error in bags (median)": float(P.err_photo_bags.median()),
           "tops with no bag assigned to the deeper unit": int((P.photo_flag == "none deeper").sum()),
           "tops with all bags assigned deeper": int((P.photo_flag == "all deeper").sum()),
           "per boundary": {b: {"n": int(len(x)), "median_error_m": float(x.err_photo.median()), "signed_median_m": float(x.signed_photo.median()),
                                "offset_median_m": float(x.err_offset.median()), "regional_median_m": float(x.err_regional.median()),
                                "xrf_median_m": float(x.err_xrf.median()), "within_30m": int((x.err_photo <= 30).sum())}
                            for b, x in P.groupby("boundary", sort=False)}}
    near, far = P[P.near], P[~P.near]
    amb = near.pick_closer_to_event | near.no_closer_than_event_baseline
    res["casing and mud diagnostic"] = {
        "near tops (shoe or mud change within 70 m)": int(len(near)), "far tops": int(len(far)),
        "near by boundary": near.boundary.value_counts().to_dict(),
        "near: median photo error m": float(near.err_photo.median()) if len(near) else None,
        "near: median error of the shoe baseline m": float(near.err_event.median()) if len(near) else None,
        "far: median photo error m": float(far.err_photo.median()) if len(far) else None,
        "near: pick closer to the shoe or change than to the true top": int(near.pick_closer_to_event.sum()),
        "near: pick no closer to the true top than the shoe baseline": int(near.no_closer_than_event_baseline.sum()),
        "near: either": int(amb.sum()),
        "wording": ("at these tops the picks cannot be separated from casing or mud changes" if len(near) and amb.sum() > len(near) / 2
                    else "the picks at near tops are closer to the true top than to the shoe or mud change in most cases"),
        "FAR tops only: S2 photo vs offset": summarise(far, "err_photo", "err_offset"),
        "FAR tops only: S1 photo vs regional": summarise(far, "err_photo", "err_regional")}
    bp = bags[bags.well.isin(prim)]
    res["bag level (primary wells)"] = {"balanced accuracy, segmented": float(balanced_accuracy_score(bp.unit, bp.pred_unit)),
                                        "balanced accuracy, per-bag argmax (no order constraint)": float(balanced_accuracy_score(bp.unit, bp.argmax_unit)),
                                        "confusion (rows true, columns segmented)": confusion_matrix(bp.unit, bp.pred_unit, labels=range(5)).tolist()}
    A = T[T.well == "34_8-3_A"]
    res["34_8-3_A (descriptive, depths in MD)"] = A[["boundary", "true_m", "photo_m", "err_photo", "xrf_m"]].round(1).to_dict(orient="records")
    s2, s1r = res["S2 PRIMARY photo vs offset well"], res["S1 secondary photo vs regional prognosis"]
    res["wording S2"] = ("better than an offset well" if s2["p_better"] < 0.05 else "worse than an offset well" if s2["p_worse"] < 0.05
                         else "not distinguishable from an offset well (n = 10)")
    res["wording S1"] = ("better than a regional depth prognosis" if s1r["p_better"] < 0.05
                         else "not shown to be better than a regional depth prognosis (n = 10 locations, two areas, all used before)")
    with open(OUT / "S_results.json", "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))
    print(T[["well", "boundary", "true_m", "photo_m", "err_photo", "err_offset", "err_regional", "err_xrf", "near", "event_dist_m", "photo_flag"]].round(0).to_string(index=False))


if __name__ == "__main__":
    main()
