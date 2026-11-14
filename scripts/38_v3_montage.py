"""
v3 EXPLORATORY -- what does the ResNet-50 (D1) signal see in the shallow
section above the 20" shoe? For each 34/x well: the 5 photos D1 scores most
sand-like and the 5 least, two tiles each (r1c1, r2c2), annotated with depth,
XRF Si/Al and K/Al and bag dry weight. D1 scores are leave-one-well-out
(34/7-1: trained on all 10 labelled wells).

Run:  python 38_v3_montage.py
"""
from importlib import import_module

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

import config as C

BL = import_module("34_v3_baselines")
EV = import_module("29_v2_evaluate")
SHOE20 = {"34_7-9": 899, "34_7-10": 901, "34_4-7": 902, "34_7-4": 953, "34_7-1": 1070}
N, T = 5, 224


def main():
    s = pd.read_csv(C.WORK_DIR / "v3_results" / "signals_per_depth.csv")
    base, emb = EV.load_tables()
    # D1 for 34/7-1 (not in the LOWO set): fit on all labelled wells
    X, use_pca = EV.build_inputs(base, emb)["D1"]
    lab = base.label.values
    tr = np.isin(lab, ["sand", "clay"])
    clf = EV.make_clf(use_pca).fit(X[tr], lab[tr] == "sand")
    m71 = (base.well == "34_7-1").values
    s.loc[m71, "D1"] = clf.predict_proba(X[m71])[:, 1]
    lab_csv = pd.read_csv(C.LABELS_CSV)
    stem = lab_csv[lab_csv.processing == "standard"].set_index(["well", "depth_m"]).stem
    W = 2 * T * 2 + 40
    rows = []
    for w, shoe in SHOE20.items():
        g = s[(s.well == w) & (s.depth_m < shoe) & s.D1.notna()].sort_values("D1")
        rows.append((w, g.tail(N).iloc[::-1], g.head(N)))
    canvas = Image.new("RGB", (N * (2 * T + 12) + 140, len(rows) * (2 * T + 70) + 30), "white")
    dr = ImageDraw.Draw(canvas)
    y0 = 10
    for w, hi, lo in rows:
        dr.text((10, y0 + T // 2), w.replace("_", "/"), fill="black")
        for r_i, (grp, tag) in enumerate(((hi, "most sand-like"), (lo, "least sand-like"))):
            yy = y0 + r_i * (T + 35)
            dr.text((10, yy + T // 2 + 14), tag, fill="black")
            for k, (_, r) in enumerate(grp.iterrows()):
                xx = 140 + k * (2 * T + 12)
                st = stem[(w, r.depth_m)]
                for j, t in enumerate(("r1c1", "r2c2")):
                    canvas.paste(Image.open(C.PATCH_DIR / w / f"{st}__{t}.jpg"), (xx + j * T, yy))
                dr.text((xx, yy + T + 2), f"{r.depth_m:.0f} m  D1 {r.D1:.2f}  Si/Al {r.XRF_SIAL:.2f}  "
                                          f"wt {abs(r.DRY_WEIGHT) if np.isfinite(r.DRY_WEIGHT) else float('nan'):.0f} g",
                        fill="black")
        y0 += 2 * T + 70
    out = C.WORK_DIR / "v3_results" / "figures" / "v3_montage_D1_above_20in_shoe.png"
    canvas.save(out)
    print("written", out)


if __name__ == "__main__":
    main()
