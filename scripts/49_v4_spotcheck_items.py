"""
v4 -- human spot-check set (review round 8): 40 bins of 34/7-10, blind to
both raters. 25 random from the 51 disputed bins (A SAND, B HET/MUD) and 15
random from bins where both raters gave the same core class (SAND/MUD/HET).
Shuffled. Writes the answer key to results/v4/spotcheck_key.csv (NOT shown to
the labeller) and the page items + images to the scratch folder.

Run:  python 49_v4_spotcheck_items.py <out_dir>
"""
import base64
import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

import config as C

W = "34_7-10"


def main(out):
    out = Path(out)
    a = pd.read_csv(C.WORK_DIR / "core_digitised_v2/A" / f"{W}.csv")
    b = pd.read_csv(C.WORK_DIR / "core_digitised_v2/B" / f"{W}.csv")
    for t in (a, b):
        t["key"] = (t.bin_top_m * 100).round().astype(int)
    m = a.merge(b[["key", "class"]], on="key", suffixes=("_a", "_b"))
    disputed = m[(m.class_a == "SAND") & m.class_b.isin(["HET", "MUD"])]
    agreed = m[(m.class_a == m.class_b) & m.class_a.isin(["SAND", "MUD", "HET"])]
    rng = np.random.default_rng(42)
    d = disputed.iloc[rng.choice(len(disputed), 25, replace=False)].assign(stratum="disputed")
    g = agreed.iloc[rng.choice(len(agreed), 15, replace=False)].assign(stratum="agreed")
    items = pd.concat([d, g]).sample(frac=1, random_state=7).reset_index(drop=True)
    items["item"] = [f"i{k + 1:02d}" for k in range(len(items))]
    items["quarter"] = ((items.bin_top_m - items.tray_top_m) / (items.tray_bottom_m - items.tray_top_m) * 4).round().astype(int)
    key = items[["item", "photo", "tray_index", "tray_top_m", "tray_bottom_m", "bin_top_m", "bin_bottom_m",
                 "quarter", "class_a", "class_b", "stratum"]]
    key.to_csv("results/v4/spotcheck_key.csv", index=False)
    imgs = {}
    for ph in sorted(items.photo.unique()):
        im = Image.open(C.WORK_DIR / "core_thumbs" / W / ph).convert("RGB")
        im = im.resize((round(im.width * 1400 / im.height), 1400), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=80)
        imgs[ph] = base64.b64encode(buf.getvalue()).decode()
    page_items = [{"item": r.item, "photo": r.photo, "tray": int(r.tray_index),
                   "trayTop": float(r.tray_top_m), "trayBottom": float(r.tray_bottom_m),
                   "binTop": round(float(r.bin_top_m), 3), "binBottom": round(float(r.bin_bottom_m), 3),
                   "quarter": int(r.quarter)} for r in items.itertuples()]
    (out / "items.json").write_text(json.dumps(page_items))
    (out / "images.json").write_text(json.dumps(imgs))
    print(len(page_items), "items,", len(imgs), "photos,",
          f"{sum(len(v) for v in imgs.values()) / 1e6:.1f} MB base64; strata", items.stratum.value_counts().to_dict())


if __name__ == "__main__":
    main(sys.argv[1])
