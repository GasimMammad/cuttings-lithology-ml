"""
v3b -- bag-interval GR targets for every W_1 photograph (V3_PLAN.md section 4).

The bag sequence comes from the NOROG cuttings-analysis CSV of each well
(one row per archived bag), merged with the photo depths. For a photo at D
with previous bag depth D_prev and next bag depth D_next:
  bottom  interval (D_prev, D]          primary (sample depth = bottom)
  centre  interval (D - s/2, D + s/2], s = D - D_prev
  below   interval (D, D_next]
Per interval: Vsh mean and NSF = fraction of GR samples with Vsh < 0.30.
Vsh uses the v2 zone and anchors exactly; an interval that leaves its zone
is missing. No predictions are read here.

Output: WORK_DIR/v3_results/interval_targets.csv

Run:  python 39_v3b_interval_targets.py
"""
from importlib import import_module

import numpy as np
import pandas as pd

import config as C

L3 = import_module("03_make_labels")
BL = import_module("34_v3_baselines")


def bag_depths(well, photo_depths):
    fs = sorted((C.SSD_ROOT / "Wells" / well / "DRILLING").glob(f"{well}_CUTTINGS_ANALYSIS_*_ENCL_1.CSV"))
    d = set(np.round(photo_depths, 2))
    if fs:
        t = pd.read_csv(fs[0], skiprows=1)
        d |= set(np.round(pd.to_numeric(t["MD (m)"], errors="coerce").dropna().values, 2))
    return np.array(sorted(d))


def stats(dz, vz, a, b):
    m = (dz > a) & (dz <= b)
    if m.sum() < 3:
        return np.nan, np.nan
    v = vz[m]
    return float(v.mean()), float((v < C.VSH_SAND_MAX).mean())


def main():
    lab = pd.read_csv(C.LABELS_CSV)
    lab = lab[lab.processing == "standard"]
    rows = []
    for well, zones in C.LABEL_ZONES.items():
        rel, _ = C.GR_SOURCES[well]
        gr = L3.load_gr(C.SSD_ROOT / "Wells" / rel)
        d_all, g_all = gr.index.values.astype(float), gr.values.astype(float)
        ph = lab[lab.well == well].sort_values("depth_m")
        bags = bag_depths(well, ph.depth_m.values)
        for zi, z in enumerate(zones):
            clean, shale, _ = L3.anchored_endmembers(gr, z)
            lo, hi = z["range"]
            m = (d_all >= lo) & (d_all <= hi)
            dz, vz = d_all[m], np.clip((g_all[m] - clean) / (shale - clean), 0, 1)
            for r in ph[(ph.depth_m >= lo) & (ph.depth_m <= hi)].itertuples():
                D = round(float(r.depth_m), 2)
                k = np.searchsorted(bags, D)
                prev = bags[k - 1] if k > 0 else np.nan
                nxt = bags[k + 1] if k + 1 < len(bags) else np.nan
                s = D - prev if np.isfinite(prev) else np.nan
                out = {"well": well, "depth_m": r.depth_m, "zone": z["name"], "s": s}
                for tag, (a, b) in {"bottom": (prev, D),
                                    "centre": (D - s / 2, D + s / 2) if np.isfinite(s) else (np.nan, np.nan),
                                    "below": (D, nxt)}.items():
                    ok = np.isfinite(a) and np.isfinite(b) and a >= lo and b <= hi
                    v, f = stats(dz, vz, a, b) if ok else (np.nan, np.nan)
                    out[f"vsh_{tag}"], out[f"nsf_{tag}"] = v, f
                rows.append(out)
    t = pd.DataFrame(rows)
    (C.WORK_DIR / "v3_results").mkdir(parents=True, exist_ok=True)
    t.to_csv(C.WORK_DIR / "v3_results" / "interval_targets.csv", index=False)
    print(t.groupby("well").agg(n=("depth_m", "size"), s_median=("s", "median"),
                                ok_bottom=("vsh_bottom", lambda x: int(x.notna().sum()))).to_string())


if __name__ == "__main__":
    main()
