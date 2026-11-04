"""
PART D1 — green index for EVERY W_1 photograph in all ten wells.

THRESHOLDS ARE FROZEN: a* < -5.0 and C* >= 12.0, with 15 < L* < 80.
Calibrated once on 34/4-6's Utsira against its Upper Pliocene background
(2026-08-01) and NOT recalibrated here. Same crop and JPEG-draft decode as
12_glauconite_test.py so values are directly comparable to the earlier run.

Sharded: `python 16_green_index_all.py <shard> <nshards>` processes a slice;
with no arguments it combines the shards. (Sharding avoids the macOS/spawn
ProcessPoolExecutor deadlock hit earlier.)
Both data roots are READ-ONLY.
"""
import re
import sys

import numpy as np
import pandas as pd
from PIL import Image
from skimage.color import rgb2lab

import config as C

Image.MAX_IMAGE_PIXELS = None

A_MAX = -5.0          # FROZEN
C_MIN = 12.0          # FROZEN
L_MIN, L_MAX = 15.0, 80.0
CROP_FRAC = (260 / 6000, 260 / 4000, 5980 / 6000, 3560 / 4000)
RX = re.compile(r"_CUTTINGS_PHOTO_M_(\d+)_W_1$")
SHARD_DIR = C.WORK_DIR / "green_shards"


def photo_list():
    rows = []
    for w in C.ALL_WELLS:
        for p in sorted(C.drilling_dir(w).iterdir()):
            m = RX.search(p.stem)
            if m:
                rows.append((w, float(m.group(1)) / 100.0, str(p)))
    return sorted(rows)


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
    return (float(mask.mean()), float(a.mean()), float(np.percentile(a, 1)),
            float(L.mean()), float(b.mean()))


def run_shard(shard, nshards):
    SHARD_DIR.mkdir(parents=True, exist_ok=True)
    items = photo_list()[shard::nshards]
    rows = []
    for n, (w, z, p) in enumerate(items, 1):
        try:
            gi, am, a1, Lm, bm = green_index(p)
        except Exception:
            gi = am = a1 = Lm = bm = float("nan")
        rows.append({"well": w, "depth_m": z, "green_index": gi,
                     "a_mean": am, "a_p01": a1, "L_mean": Lm, "b_mean": bm,
                     "path": p})
        if n % 50 == 0:
            print(f"shard {shard}: {n}/{len(items)}", flush=True)
    pd.DataFrame(rows).to_csv(SHARD_DIR / f"g_{shard:02d}.csv", index=False)
    print(f"shard {shard}: DONE {len(rows)}", flush=True)


def combine():
    files = sorted(SHARD_DIR.glob("g_*.csv"))
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df = df.sort_values(["well", "depth_m"]).reset_index(drop=True)
    out = C.WORK_DIR / "16_green_index_all.csv"
    df.to_csv(out, index=False)
    print(f"combined {len(files)} shards -> {out}  ({len(df):,} photographs)")
    print(df.groupby("well").green_index.agg(["size", "median", "max"]).to_string())


if __name__ == "__main__":
    if len(sys.argv) == 3:
        run_shard(int(sys.argv[1]), int(sys.argv[2]))
    else:
        combine()
