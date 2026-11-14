"""
v7 step 1, checks required by review round 16 (run after the primary):
  1. Colour-only baselines: lab_L_mean alone, and mean L*a*b* (3 features),
     through the same LOWO / high-pass / Wilcoxon as the primary.
  2. Per-well rho of the primary above and below 950 m.
  3. The primary on S minus the v3 shallow-test bags (labels excluded_zone or
     no_log, above top Shetland), so v7 evidence does not recycle v3's.
  4. (Added, not required) R-D prediction partial on the high-passed
     mean L*a*b*: does the embedding carry information beyond mean colour?

Run:  python 52b_v7_extra_checks.py
"""
import json
from importlib import import_module

import numpy as np
import pandas as pd

import config as C
from features import FEATURE_NAMES

EV = import_module("29_v2_evaluate")
XS = import_module("35_v3_xrf_shallow")
CM = import_module("42_v4_cement_mask")
M = import_module("52_v7_photo_to_xrf")
OUT = C.WORK_DIR / "v7"
SPLIT_M = 950.0


def main():
    base, emb = EV.load_tables()
    wells = base.well.values
    d = base.depth_m.values.astype(float)
    x = M.xrf_table(base)
    tert = d < np.array([XS.TOP_SHETLAND[w] for w in wells])
    S = tert & ~CM.shoe_mask(base) & (x.SI.values > 0) & (x.AL.values > 0)
    T1 = M.zwell(np.log10(x.SI.values / x.AL.values), wells, S)
    E15 = base[FEATURE_NAMES].values.astype(float)
    R15 = base[["ref_" + c for c in FEATURE_NAMES]].values.astype(float)
    Z = M.zwell_mat(E15, wells, S, R15)
    lab_cols = [FEATURE_NAMES.index(c) for c in ("lab_L_mean", "lab_a_mean", "lab_b_mean")]
    pr = pd.read_csv(OUT / "step1_predictions.csv")
    assert (pr.depth_m.values == d).all() and (pr.well.values == wells).all()
    pRD = pr.pred_RD.values
    res, pw = {}, {}

    # 1. colour-only baselines
    for tag, cols in (("colour L* only", lab_cols[:1]), ("colour mean L*a*b*", lab_cols)):
        p, _ = M.cv_predict(Z[:, cols], T1, wells, d, S, "RE", lambda w: w)
        r, s = M.block(p, T1, wells, d, S, tag)
        both = pd.concat([pd.Series(pw.get("primary", None)) if False else s], axis=1)
        res[tag], pw[tag] = r, s
    prim = M.per_well_hp(pRD, T1, wells, d, S)
    pw["primary"] = prim
    from scipy.stats import wilcoxon
    for tag in ("colour L* only", "colour mean L*a*b*"):
        dd = (prim - pw[tag]).dropna()
        res[tag]["paired_RD_gt_colour_p"] = float(wilcoxon(dd, alternative="greater").pvalue)

    # 4. R-D partial on hp mean colour
    part = {}
    for w in np.unique(wells[S]):
        m = S & (wells == w) & np.isfinite(pRD) & np.isfinite(Z[:, lab_cols]).all(1)
        ctrl = np.column_stack([M.highpass(d[m], Z[m, c]) for c in lab_cols])
        part[w] = M.partial_rho(M.highpass(d[m], pRD[m]), M.highpass(d[m], T1[m]), ctrl)
    part = pd.Series(part)
    res["R-D partial on hp mean L*a*b* (added)"] = {**M.summarise(part), "per_well": part.round(4).to_dict()}
    pw["R-D partial colour"] = part

    # 2. above / below 950 m (high-pass over the full series, rho computed on each part)
    for tag, sub in (("above 950 m", d < SPLIT_M), ("below 950 m", d >= SPLIT_M)):
        s = {}
        for w in np.unique(wells[S]):
            m = S & (wells == w)
            hp_p, hp_y = M.highpass(d[m], pRD[m]), M.highpass(d[m], T1[m])
            k = sub[m]
            s[w] = M.rho(hp_p[k], hp_y[k]) if k.sum() >= M.MIN_STRETCH else np.nan
        s = pd.Series(s)
        res[f"primary {tag}"] = {**M.summarise(s), "per_well": s.round(4).to_dict(),
                                 "n_bags": int((S & sub).sum())}
        pw[f"primary {tag}"] = s

    # 3. S minus the v3 shallow-test bags (high-pass on the remaining bags only)
    v3 = np.isin(base.label.values, ["excluded_zone", "no_log"]) & tert
    S3 = S & ~v3
    s = M.per_well_hp(pRD, T1, wells, d, S3)
    res["primary on S minus v3 shallow set"] = {**M.summarise(s), "per_well": s.round(4).to_dict(),
                                                "n_bags": int(S3.sum()), "n_removed": int((S & v3).sum())}
    pw["S minus v3"] = s

    pd.DataFrame(pw).round(4).to_csv(OUT / "step1_extra_checks_per_well.csv")
    with open(OUT / "step1_extra_checks.json", "w") as f:
        json.dump(res, f, indent=1, default=float)
    for k, v in res.items():
        print(f"{k:42s} med {v.get('median_rho', np.nan):+.3f}  pos {v.get('n_pos')}/{v.get('n_wells')}  "
              f"p {v.get('wilcoxon_p', np.nan):.4f}  {('paired RD>col p %.4f' % v['paired_RD_gt_colour_p']) if 'paired_RD_gt_colour_p' in v else ''}"
              f"{('  n_bags %d' % v['n_bags']) if 'n_bags' in v else ''}")
    print(pd.DataFrame(pw).round(2).to_string())


if __name__ == "__main__":
    main()
