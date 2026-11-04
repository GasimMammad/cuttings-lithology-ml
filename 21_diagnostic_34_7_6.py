"""
STEP 2b diagnostic for 34/7-6.

Establishes whether the shallow section is MEASURABLE with the frozen index,
by separating three candidate causes of the control failure:
  (1) dilution artefact  - sparse trays, index normalised by whole crop
  (2) chroma block       - shallow cannot reach C* >= 12.0
  (3) genuine absence    - hue gate itself empty shallow

Thresholds are NOT re-tuned. The frozen gates are reported as-is; the extra
numbers are diagnostics about them, not replacements for them.

Items 1-4 by GROUP (pooled) so no per-window target index is produced.
Item 5 is colour statistics per window, which does not compute the index.
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
A_MAX, C_MIN = -5.0, 12.0            # FROZEN
L_MIN, L_MAX = 15.0, 80.0
CROP_FRAC = (260 / 6000, 260 / 4000, 5980 / 6000, 3560 / 4000)
RX = re.compile(r"_CUTTINGS_PHOTO_M_(\d+)_W_1\.JPG$")
WELL_DIR = C.SSD_ROOT / "Wells" / "34_7-6" / "DRILLING"
SHARD = C.WORK_DIR / "s2b_shards"

# cuttings mask: exclude the dark anodised tray. Reported at three cut-offs so
# the conclusion cannot hinge on one arbitrary choice.
TRAY_CUTS = (15.0, 20.0, 25.0)


def photos():
    out = []
    for p in sorted(Path(WELL_DIR).iterdir()):
        m = RX.search(p.name)
        if not m:
            continue
        z = float(m.group(1)) / 100.0
        if 1000.0 <= z <= 1895.0:
            out.append((z, str(p)))
    return sorted(out)


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
    r = {}
    for cut in TRAY_CUTS:
        r[f"maskfrac_L{int(cut)}"] = float((L > cut).mean())
    mask = L > TRAY_CUTS[0]
    n = max(int(mask.sum()), 1)
    r["hue_gate"] = float(((a < A_MAX) & mask).sum() / n)
    r["chroma_gate"] = float(((ch >= C_MIN) & mask).sum() / n)
    r["both_masknorm"] = float(((a < A_MAX) & (ch >= C_MIN) &
                                (L > L_MIN) & (L < L_MAX)).sum() / n)
    r["index_cropnorm"] = float(((a < A_MAX) & (ch >= C_MIN) &
                                 (L > L_MIN) & (L < L_MAX)).mean())
    r["L_med"] = float(np.median(L[mask]))
    r["a_med"] = float(np.median(a[mask]))
    r["b_med"] = float(np.median(b[mask]))
    r["C_med"] = float(np.median(ch[mask]))
    r["a_p01"] = float(np.percentile(a[mask], 1))
    r["C_p99"] = float(np.percentile(ch[mask], 99))
    return r


def run_shard(shard, nshards):
    SHARD.mkdir(parents=True, exist_ok=True)
    items = photos()[shard::nshards]
    rows = []
    for n, (z, p) in enumerate(items, 1):
        try:
            r = measure(p)
        except Exception:
            r = {}
        r.update({"depth_m": z, "path": p})
        rows.append(r)
        if n % 10 == 0:
            print(f"shard {shard}: {n}/{len(items)}", flush=True)
    pd.DataFrame(rows).to_csv(SHARD / f"d_{shard:02d}.csv", index=False)
    print(f"shard {shard}: DONE {len(rows)}", flush=True)


def combine():
    df = pd.concat([pd.read_csv(f) for f in sorted(SHARD.glob("d_*.csv"))],
                   ignore_index=True).sort_values("depth_m")
    df.to_csv(C.WORK_DIR / "21_diagnostic_34_7_6.csv", index=False)
    print(f"combined n={len(df)} -> 21_diagnostic_34_7_6.csv")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        run_shard(int(sys.argv[1]), int(sys.argv[2]))
    else:
        combine()
