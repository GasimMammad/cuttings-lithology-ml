"""
METHODS VERIFICATION: is the chroma gate C* >= 12.0 inert across all eleven wells?

The operative question is not "what fraction of pixels clear C*", it is
"of the pixels that already pass the hue gate a* < -5.0, what fraction ALSO
pass chroma". If that is ~100 percent, the chroma gate removes nothing from the
index and the index is in substance a single hue threshold.

Sampled photographs per well, spread over depth. Read-only.
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from skimage.color import rgb2lab

import config as C

Image.MAX_IMAGE_PIXELS = None
A_MAX, C_MIN = -5.0, 12.0
L_MIN, L_MAX = 15.0, 80.0
CROP_FRAC = (260 / 6000, 260 / 4000, 5980 / 6000, 3560 / 4000)
RX = re.compile(r"_CUTTINGS_PHOTO_M_(\d+)_W_1\.JPG$")
N_PER_WELL = 10
SHARD = C.WORK_DIR / "chroma_shards"

WELLS = C.ALL_WELLS + ["34_7-6"]


def well_dir(w):
    if w == "34_7-6":
        return C.SSD_ROOT / "Wells" / "34_7-6" / "DRILLING"
    return C.drilling_dir(w)


def sample(w):
    ph = []
    for p in sorted(well_dir(w).iterdir()):
        m = RX.search(p.name)
        if m:
            ph.append((float(m.group(1)) / 100.0, str(p)))
    ph.sort()
    if len(ph) <= N_PER_WELL:
        return ph
    idx = np.linspace(0, len(ph) - 1, N_PER_WELL).round().astype(int)
    return [ph[i] for i in idx]


def measure(path):
    with Image.open(path) as im:
        im.draft("RGB", (im.size[0] // 8, im.size[1] // 8))
        im = im.convert("RGB")
        w, h = im.size
        x0, y0, x1, y1 = CROP_FRAC
        im = im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))
        arr = np.asarray(im, dtype=np.float64) / 255.0
    lab = rgb2lab(arr)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    ch = np.sqrt(a * a + b * b)
    mask = (L > L_MIN) & (L < L_MAX)
    hue = (a < A_MAX) & mask
    n_hue = int(hue.sum())
    return {
        "frac_chroma_pass": float((ch[mask] >= C_MIN).mean()),
        "n_hue_pass": n_hue,
        # THE OPERATIVE NUMBER: of hue-passing pixels, how many survive chroma
        "hue_and_chroma_over_hue": float(((hue & (ch >= C_MIN)).sum() / n_hue)
                                         if n_hue else np.nan),
        "b_med": float(np.median(b[mask])),
    }


def run_shard(shard, nshards):
    SHARD.mkdir(parents=True, exist_ok=True)
    jobs = [(w, z, p) for w in WELLS for z, p in sample(w)][shard::nshards]
    rows = []
    for n, (w, z, p) in enumerate(jobs, 1):
        try:
            r = measure(p)
        except Exception:
            r = {}
        r.update({"well": w, "depth_m": z})
        rows.append(r)
        if n % 10 == 0:
            print(f"shard {shard}: {n}/{len(jobs)}", flush=True)
    pd.DataFrame(rows).to_csv(SHARD / f"x_{shard:02d}.csv", index=False)
    print(f"shard {shard}: DONE {len(rows)}", flush=True)


def combine():
    df = pd.concat([pd.read_csv(f) for f in sorted(SHARD.glob("x_*.csv"))],
                   ignore_index=True)
    df.to_csv(C.WORK_DIR / "22_chroma_gate_check.csv", index=False)
    print("=" * 92)
    print("CHROMA GATE VERIFICATION, ELEVEN WELLS")
    print("  operative column: of pixels passing a* < -5.0, the fraction that")
    print("  ALSO pass C* >= 12.0. If ~1.000 the chroma gate removes nothing.")
    print("=" * 92)
    print(f"{'well':10} {'n photos':>9} {'b* med':>8} {'frac pixels C*>=12':>20} "
          f"{'HUE-PASS surviving chroma':>27}")
    for w in WELLS:
        s = df[df.well == w]
        if not len(s):
            continue
        print(f"{w:10} {len(s):>9} {s.b_med.median():8.2f} "
              f"{s.frac_chroma_pass.median():20.4f} "
              f"{s.hue_and_chroma_over_hue.median():27.4f}")
    print(f"\n  ALL WELLS: median fraction of hue-passing pixels surviving the "
          f"chroma gate = {df.hue_and_chroma_over_hue.median():.4f}")
    print(f"  minimum across all {len(df)} photographs = "
          f"{df.hue_and_chroma_over_hue.min():.4f}")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        run_shard(int(sys.argv[1]), int(sys.argv[2]))
    else:
        combine()
