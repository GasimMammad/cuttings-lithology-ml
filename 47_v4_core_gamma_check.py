"""
v4 -- objective check of the core-photo raters with CORE GAMMA (review round 7).
Core gamma (34/8-3, 34/8-3 A; NORCORE files parsed by 44_v4_plug_data.py) is
measured on the core in core depth, so no core-to-log shift is needed.
Per rater and well: AUC of SAND vs MUD bins using total core gamma (low =
sand), and Spearman of per-metre sand fraction vs mean core gamma. Plugs
(34/8-3, 24/9-3): fraction of plugs with horizontal permeability > 1 mD that
fall in SAND bins (precision check, plugs are biased toward sand).

Run:  python 47_v4_core_gamma_check.py [--v2]
"""
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import config as C

EV = __import__("importlib").import_module("29_v2_evaluate")
D = C.WORK_DIR / ("core_digitised_v2" if "--v2" in sys.argv else "core_digitised")
GAMMA = {"Counts", "TOTAL GAMMA COUNTS/MIN"}
PERM = {"ka HOR", "KLINK. CORR. GAS PERM. HOR"}


def main():
    pdata = pd.read_csv(C.WORK_DIR / "v4_results" / "plug_data.csv")
    for rater_dir in sorted(D.glob("*")):
        for f in sorted(rater_dir.glob("*.csv")):
            w = f.stem
            r = pd.read_csv(f)
            g = pdata[(pdata.well == w) & pdata.curve.isin(GAMMA)]
            k = pdata[(pdata.well == w) & pdata.curve.isin(PERM)]
            out = [f"{rater_dir.name} {w}:"]
            if len(g):
                gm = []
                for b in r.itertuples():
                    v = g[(g.depth_m >= b.bin_top_m) & (g.depth_m < b.bin_bottom_m)].value
                    gm.append(v.mean() if len(v) else np.nan)
                r["gamma"] = gm
                sm = r[r["class"].isin(["SAND", "MUD"]) & r.gamma.notna()]
                a = EV.auc(sm["class"].values == "SAND", -sm.gamma.values)
                r["m"] = np.floor(r.bin_top_m)
                cored = r[r["class"].isin(["SAND", "HET", "MUD", "OTHER"])].copy()
                cored["v"] = cored["class"].map({"SAND": 1, "HET": 0.5, "MUD": 0, "OTHER": 0})
                pm = cored.groupby("m").agg(f=("v", "mean"), g=("gamma", "mean")).dropna()
                rho = spearmanr(pm.f, -pm.g)[0] if len(pm) > 5 else np.nan
                out.append(f"core-gamma AUC SAND vs MUD bins {a:.2f} (n {len(sm)}); per-metre rho(sand frac, -gamma) {rho:.2f} (n {len(pm)})")
            if len(k):
                hi = k[k.value > 1].depth_m.values
                cls = [r[(r.bin_top_m <= z) & (z < r.bin_bottom_m)]["class"].tolist()[:1] for z in hi]
                cls = [c[0] for c in cls if c]
                if cls:
                    out.append(f"plugs >1 mD in SAND bins {np.mean([c == 'SAND' for c in cls]):.0%} "
                               f"(HET {np.mean([c == 'HET' for c in cls]):.0%}, n {len(cls)})")
            if len(out) > 1:
                print(" ".join(out))


if __name__ == "__main__":
    main()
