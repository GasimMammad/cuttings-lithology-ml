"""
STAGE 2 step 2 — CONTROLS ONLY for 34/7-6.

Computes the green index for the control windows ONLY. The target windows
(1218 to 1310 m) are deliberately EXCLUDED so that no target number exists
until the controls have been reported and reviewed.

Thresholds FROZEN, identical to the ten-well run: a* < -5.0, C* >= 12.0,
15 < L* < 80, same crop, same JPEG draft decode.

Usage: python 20_controls_34_7_6.py <shard> <nshards>   then with no args to combine.
"""
import re
import sys

import numpy as np
import pandas as pd
from PIL import Image
from skimage.color import rgb2lab

import config as C

Image.MAX_IMAGE_PIXELS = None

A_MAX, C_MIN = -5.0, 12.0          # FROZEN
L_MIN, L_MAX = 15.0, 80.0
CROP_FRAC = (260 / 6000, 260 / 4000, 5980 / 6000, 3560 / 4000)
RX = re.compile(r"_CUTTINGS_PHOTO_M_(\d+)_W_1\.JPG$")
WELL_DIR = C.SSD_ROOT / "Wells" / "34_7-6" / "DRILLING"
SHARD_DIR = C.WORK_DIR / "s2_control_shards"

TARGET_LO, TARGET_HI = 1218.0, 1310.0      # EXCLUDED HERE


def control_photos():
    from pathlib import Path
    out = []
    for p in sorted(Path(WELL_DIR).iterdir()):
        m = RX.search(p.name)
        if not m:
            continue
        z = float(m.group(1)) / 100.0
        if TARGET_LO <= z <= TARGET_HI:
            continue                        # target withheld
        if (1036.5 <= z <= 1095.0) or z > 1450.0:
            out.append((z, str(p)))
    return sorted(out)


def green_index(path):
    with Image.open(path) as im:
        im.draft("RGB", (im.size[0] // 8, im.size[1] // 8))
        im = im.convert("RGB")
        w, h = im.size
        x0, y0, x1, y1 = CROP_FRAC
        im = im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))
        arr = np.asarray(im, dtype=np.float64) / 255.0
    lab = rgb2lab(arr)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    chroma = np.sqrt(a * a + b * b)
    mask = (a < A_MAX) & (chroma >= C_MIN) & (L > L_MIN) & (L < L_MAX)
    return float(mask.mean())


def run_shard(shard, nshards):
    SHARD_DIR.mkdir(parents=True, exist_ok=True)
    items = control_photos()[shard::nshards]
    rows = []
    for n, (z, p) in enumerate(items, 1):
        try:
            gi = green_index(p)
        except Exception:
            gi = float("nan")
        rows.append({"well": "34_7-6", "depth_m": z, "green_index": gi, "path": p})
        if n % 20 == 0:
            print(f"shard {shard}: {n}/{len(items)}", flush=True)
    pd.DataFrame(rows).to_csv(SHARD_DIR / f"c_{shard:02d}.csv", index=False)
    print(f"shard {shard}: DONE {len(rows)}", flush=True)


def combine():
    files = sorted(SHARD_DIR.glob("c_*.csv"))
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df = df.sort_values("depth_m").reset_index(drop=True)
    out = C.WORK_DIR / "20_controls_34_7_6.csv"
    df.to_csv(out, index=False)
    assert not ((df.depth_m >= TARGET_LO) & (df.depth_m <= TARGET_HI)).any(), \
        "target photographs leaked into the control set"
    print(f"combined -> {out}   n={len(df)}   "
          f"(target 1218-1310 m verified absent)")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        run_shard(int(sys.argv[1]), int(sys.argv[2]))
    else:
        combine()
