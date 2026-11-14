"""
v4 B2 (V4_PLAN.md section E) -- DESCRIPTIVE plug-referenced bed-scale check,
34/8-3, 2839-2897 m (Ness + Etive; Rannoch excluded). No p-value is claimed.

Per cuttings bag (photo depth D, support (D - s, D], s = spacing to previous
bag): median plug helium porosity, median log10 horizontal permeability, plug
count per metre. Gate: Spearman(XRF Si/Al, median log-perm) > 0.
Signals never trained on 34/8-3: ONE_FEATURE, D1, E2; baselines: colour
(-lab_a_mean), bag dry weight (training-learned sign), core gamma (-counts).

Run:  python 48_v4_plug_check.py
"""
from importlib import import_module

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import config as C

EV = import_module("29_v2_evaluate")
IT = import_module("39_v3b_interval_targets")
WELL, TOP, BASE = "34_8-3", 2839.0, 2897.0


def main():
    base, _ = EV.load_tables()
    sig = pd.read_csv(C.WORK_DIR / "v3_results" / "signals_per_depth.csv")
    sig = sig.merge(base[["well", "depth_m", "lab_a_mean"]], on=["well", "depth_m"], how="left")
    plugs = pd.read_csv(C.WORK_DIR / "v4_results" / "plug_data.csv")
    plugs = plugs[plugs.well == WELL]
    por = plugs[plugs.curve == "He Por %"]
    perm = plugs[plugs.curve == "ka HOR"]
    gam = plugs[plugs.curve == "Counts"]

    s = sig[(sig.well == WELL) & sig.depth_m.between(TOP, BASE)].sort_values("depth_m").copy()
    bags = IT.bag_depths(WELL, sig[sig.well == WELL].depth_m.values)
    rows = []
    for r in s.itertuples():
        k = np.searchsorted(bags, round(r.depth_m, 2))
        prev = bags[k - 1] if k > 0 else np.nan
        a, b = prev, r.depth_m
        pp = por[(por.depth_m > a) & (por.depth_m <= b)].value
        kk = perm[(perm.depth_m > a) & (perm.depth_m <= b)].value
        gg = gam[(gam.depth_m > a) & (gam.depth_m <= b)].value
        rows.append({"depth_m": r.depth_m, "s": b - a, "n_plugs": len(pp),
                     "plug_density": len(pp) / (b - a) if b > a else np.nan,
                     "med_por": pp.median() if len(pp) else np.nan,
                     "med_logk": np.log10(kk.clip(lower=0.01)).median() if len(kk) else np.nan,
                     "core_gamma": gg.mean() if len(gg) else np.nan,
                     "ONE_FEATURE": r.ONE_FEATURE, "D1": r.D1, "E2": r.E2,
                     "XRF_SIAL": r.XRF_SIAL, "DRY_WEIGHT": r.DRY_WEIGHT,
                     "COLOUR": -r.lab_a_mean})
    t = pd.DataFrame(rows)
    t["CORE_GAMMA"] = -t.core_gamma
    out = C.WORK_DIR / "v4_results"
    t.to_csv(out / "plug_check_34_8-3.csv", index=False)
    print(f"bags in {TOP:.0f}-{BASE:.0f} m: {len(t)}; with >= 1 plug: {int((t.n_plugs > 0).sum())}; "
          f"median bag spacing {t.s.median():.1f} m")
    g = t.dropna(subset=["med_logk"])
    gate = spearmanr(g.XRF_SIAL, g.med_logk)[0]
    print(f"GATE rho(XRF Si/Al, median log-perm) = {gate:+.2f} (n {len(g)}) -> "
          f"{'PASS (informative)' if gate > 0 else 'FAIL (uninformative)'}")
    res = []
    for sname in ["ONE_FEATURE", "D1", "E2", "COLOUR", "DRY_WEIGHT", "CORE_GAMMA", "XRF_SIAL"]:
        row = {"signal": sname}
        for ref in ("med_logk", "med_por", "plug_density"):
            gg = t.dropna(subset=[ref, sname])
            row[f"rho_{ref}"] = spearmanr(gg[sname], gg[ref])[0] if len(gg) > 5 else np.nan
            row[f"n_{ref}"] = len(gg)
        res.append(row)
    res = pd.DataFrame(res)
    res.to_csv(out / "plug_check_34_8-3_summary.csv", index=False)
    print(res.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
