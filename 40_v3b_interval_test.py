"""
v3b TEST (V3_PLAN.md sections 4 and 4b): do photographs track the bag's
drilled interval better than the point GR label?

Step 1 (no images): scan offset o and width w of the bag support against
cuttings XRF Si/Al; pick (o, w) by the pre-registered rule; XRF positive
control against point Vsh.
Step 2 (images): per well, delta = rho(hp signal, -hp target) - rho(hp signal,
-hp Vsh_point) over in-zone photos; one-sided Wilcoxon over the six 10 m wells.

Run:  python 40_v3b_interval_test.py
"""
from importlib import import_module

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon

import config as C

L3 = import_module("03_make_labels")
XS = import_module("35_v3_xrf_shallow")
BL = import_module("34_v3_baselines")
EV = import_module("29_v2_evaluate")
OUT = C.WORK_DIR / "v3_results"
WELLS = ["34_4-6", "34_4-7", "34_7-4", "34_7-6", "34_7-9", "34_7-10"]
OFFSETS = list(range(-15, 16))
WIDTHS = [3, 5, 10, 15]
IN_ZONE = ["sand", "clay", "mixed", "unstable"]


def zone_curves(well):
    rel, _ = C.GR_SOURCES[well]
    gr = L3.load_gr(C.SSD_ROOT / "Wells" / rel)
    d, g = gr.index.values.astype(float), gr.values.astype(float)
    out = []
    for z in C.LABEL_ZONES[well]:
        clean, shale, _ = L3.anchored_endmembers(gr, z)
        lo, hi = z["range"]
        m = (d >= lo) & (d <= hi)
        out.append((z["name"], lo, hi, d[m], np.clip((g[m] - clean) / (shale - clean), 0, 1)))
    return out


def window_mean(curves, zone, D, o, w):
    for name, lo, hi, dz, vz in curves:
        if name != zone:
            continue
        a, b = D + o - w, D + o
        if a < lo or b > hi:
            return np.nan
        m = (dz > a) & (dz <= b)
        return float(vz[m].mean()) if m.sum() >= 3 else np.nan
    return np.nan


def hp_by_zone(df, col):
    out = np.full(len(df), np.nan)
    for z, g in df.groupby("zone_name"):
        idx = g.index.values
        out[df.index.get_indexer(idx)] = XS.highpass(g.depth_m.values, g[col].values.astype(float))
    return out


def rho(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    return spearmanr(a[ok], b[ok])[0] if ok.sum() >= 15 else np.nan


def main():
    s = pd.read_csv(OUT / "signals_per_depth.csv")
    base, _ = EV.load_tables()
    s["sial"] = BL.xrf_sial(base)
    s = s[s.well.isin(WELLS) & s.label.isin(IN_ZONE)].reset_index(drop=True)
    curves = {w: zone_curves(w) for w in WELLS}

    # ---------- step 1: XRF-only support scan ----------
    s["hp_sial"] = np.nan
    s["hp_vpt"] = np.nan
    for w in WELLS:
        m = (s.well == w).values
        sub = s[m]
        s.loc[m, "hp_sial"] = hp_by_zone(sub, "sial")
        s.loc[m, "hp_vpt"] = hp_by_zone(sub, "vsh")
    point = np.nanmean([rho(s.hp_sial[s.well == w].values, -s.hp_vpt[s.well == w].values) for w in WELLS])
    scan = []
    targets = {}
    for o in OFFSETS:
        for wd in WIDTHS:
            t = np.array([window_mean(curves[r.well], r.zone_name, r.depth_m, o, wd) for r in s.itertuples()])
            col = f"t_{o}_{wd}"
            s[col] = t
            hp = np.full(len(s), np.nan)
            for w in WELLS:
                m = (s.well == w).values
                hp[m] = hp_by_zone(s[m], col)
            targets[(o, wd)] = hp
            r = [rho(s.hp_sial[s.well == w].values, -hp[(s.well == w).values]) for w in WELLS]
            scan.append({"offset": o, "width": wd, "mean_rho": float(np.nanmean(r)),
                         **{f"rho_{w}": x for w, x in zip(WELLS, r)}})
    scan = pd.DataFrame(scan)
    scan["dist"] = (scan.offset ** 2 + ((scan.width - 10) / 1.0) ** 2) ** 0.5
    best = scan.sort_values(["mean_rho", "dist"], ascending=[False, True]).iloc[0]
    o_b, w_b = int(best.offset), int(best.width)
    scan.to_csv(OUT / "v3b_support_scan.csv", index=False)
    print(f"XRF vs point Vsh: mean rho {point:+.3f}")
    print(f"XRF best support: offset {o_b:+d} m, width {w_b} m, mean rho {best.mean_rho:+.3f}  "
          f"(bottom convention o=0,w=10: {scan[(scan.offset == 0) & (scan.width == 10)].mean_rho.iloc[0]:+.3f})")
    print(scan.pivot_table(index="offset", columns="width", values="mean_rho").round(3).to_string())
    control_ok = best.mean_rho > point
    print(f"positive control (interval beats point for XRF): {control_ok}")

    # ---------- step 2: image test ----------
    tb = targets[(o_b, w_b)]
    rows = []
    for sig in ("ONE_FEATURE", "D1", "E2", "DRY_WEIGHT"):
        hps = np.full(len(s), np.nan)
        for w in WELLS:
            m = (s.well == w).values
            hps[m] = hp_by_zone(s[m], sig)
        for w in WELLS:
            m = (s.well == w).values
            r_int, r_pt = rho(hps[m], -tb[m]), rho(hps[m], -s.hp_vpt.values[m])
            rows.append({"signal": sig, "well": w, "rho_interval": r_int, "rho_point": r_pt,
                         "delta": r_int - r_pt})
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "v3b_interval_test.csv", index=False)
    print(t.pivot_table(index="well", columns="signal", values="delta").round(3).to_string())
    for sig, g in t.groupby("signal", sort=False):
        d = g.delta.dropna().values
        p = wilcoxon(d, alternative="greater").pvalue
        print(f"{sig:12} median rho point {g.rho_point.median():+.3f} -> interval {g.rho_interval.median():+.3f} | "
              f"delta median {np.median(d):+.3f}, {(d > 0).sum()}/{len(d)} > 0, Wilcoxon p {p:.4f}")


if __name__ == "__main__":
    main()
