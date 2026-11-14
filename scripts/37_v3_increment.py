"""
v3 EXPLORATORY -- do photographs add anything beyond the bag's dry weight?

For each held-out eligible well: AUC of signed dry weight alone vs AUC of the
mean of within-well ranks of (signed dry weight, photo signal). Signs were
learned on training wells in 34_v3_baselines.py. No fitting here.
Also reported: whole-well and local (pairs < 50 m) AUC; paired Wilcoxon.

Run:  python 37_v3_increment.py      (after 34_v3_baselines.py)
"""
from importlib import import_module

import numpy as np
import pandas as pd
from scipy.stats import rankdata, wilcoxon

import config as C

EV = import_module("29_v2_evaluate")
BL = import_module("34_v3_baselines")
R = C.WORK_DIR / "v3_results"


def wrank(v):
    out = np.full(len(v), np.nan)
    ok = np.isfinite(v)
    out[ok] = rankdata(v[ok]) / ok.sum()
    return out


def main():
    s = pd.read_csv(R / "signals_per_depth.csv")
    rows = []
    for w, g in s.groupby("well"):
        g = g[g.label.isin(["sand", "clay"]) & g.DRY_WEIGHT.notna()]
        y = (g.label == "sand").values
        if y.sum() < 3 or (~y).sum() < 3:
            continue
        wt = wrank(g.DRY_WEIGHT.values)
        row = {"well": w, "weight": EV.auc(y, wt),
               "weight_local50": BL.local_auc(g.depth_m.values, wt, y, 50)[0]}
        for k in ("D1", "ONE_FEATURE", "E2", "XRF_SIAL"):
            comb = np.nanmean([wt, wrank(g[k].values)], axis=0)
            row[f"{k}"] = EV.auc(y, wrank(g[k].values))
            row[f"weight+{k}"] = EV.auc(y, comb)
            row[f"weight+{k}_local50"] = BL.local_auc(g.depth_m.values, comb, y, 50)[0]
        rows.append(row)
    t = pd.DataFrame(rows).set_index("well")
    t.to_csv(R / "increment_over_weight.csv")
    print(t.round(2).T.to_string())
    for k in ("D1", "ONE_FEATURE", "E2", "XRF_SIAL"):
        d = (t[f"weight+{k}"] - t.weight).values
        dl = (t[f"weight+{k}_local50"] - t.weight_local50).dropna().values
        print(f"weight+{k:12} vs weight: whole-well median diff {np.median(d):+.3f} ({(d > 0).sum()}/{len(d)} up, "
              f"p {wilcoxon(d, alternative='greater').pvalue:.3f}) | local50 median diff {np.median(dl):+.3f} "
              f"({(dl > 0).sum()}/{len(dl)} up, p {wilcoxon(dl, alternative='greater').pvalue:.3f})")


if __name__ == "__main__":
    main()
