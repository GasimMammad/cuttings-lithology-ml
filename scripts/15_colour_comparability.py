"""
PART A3 — CIELAB colour comparability across all ten wells over 1000-1450 m.
Same crop and draft-decode as the glauconite index (12_glauconite_test.py), so
the statistics describe exactly the pixels the index sees.
Read-only on both data roots. Writes a CSV + prints the table.
"""
import re

import numpy as np
import pandas as pd
from PIL import Image
from skimage.color import rgb2lab

import config as C

Image.MAX_IMAGE_PIXELS = None
CROP_FRAC = (260 / 6000, 260 / 4000, 5980 / 6000, 3560 / 4000)
RX = re.compile(r"_CUTTINGS_PHOTO_M_(\d+)_W_1$")
WINDOW = (1000.0, 1450.0)


def photos(well):
    out = []
    for p in sorted(C.drilling_dir(well).iterdir()):
        m = RX.search(p.stem)
        if m:
            out.append((float(m.group(1)) / 100.0, p))
    return sorted(out)


def lab_stats(path):
    with Image.open(path) as im:
        im.draft("RGB", (im.size[0] // 8, im.size[1] // 8))
        im = im.convert("RGB")
        w, h = im.size
        x0, y0, x1, y1 = CROP_FRAC
        im = im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))
        arr = np.asarray(im, dtype=np.float64) / 255.0
    lab = rgb2lab(arr)
    return [lab[..., i].mean() for i in range(3)] + [lab[..., i].std() for i in range(3)]


def main():
    rows = []
    for w in C.ALL_WELLS:
        sel = [(z, p) for z, p in photos(w) if WINDOW[0] <= z <= WINDOW[1]]
        print(f"{w}: {len(sel)} photos in {WINDOW[0]:.0f}-{WINDOW[1]:.0f} m", flush=True)
        for z, p in sel:
            try:
                L, a, b, Ls, as_, bs = lab_stats(p)
            except Exception:
                continue
            rows.append({"well": w, "depth_m": z, "L": L, "a": a, "b": b,
                         "L_sd": Ls, "a_sd": as_, "b_sd": bs})
    df = pd.DataFrame(rows)
    df.to_csv(C.WORK_DIR / "15_colour_comparability.csv", index=False)
    g = df.groupby("well").agg(n=("L", "size"), L=("L", "mean"), a=("a", "mean"),
                               b=("b", "mean"), L_sd=("L", "std"),
                               a_sd=("a", "std"), b_sd=("b", "std"))
    g = g.reindex([w for w in C.ALL_WELLS if w in g.index])
    print("\n" + "=" * 92)
    print(f"PART A3 -- CIELAB over {WINDOW[0]:.0f}-{WINDOW[1]:.0f} m "
          "(per-photo means, then averaged per well)")
    print("=" * 92)
    print(f"{'well':10} {'n':>4} {'L*':>8} {'a*':>8} {'b*':>8} | "
          f"{'sd L*':>7} {'sd a*':>7} {'sd b*':>7}")
    for w, r in g.iterrows():
        print(f"{w:10} {int(r.n):>4} {r.L:8.2f} {r.a:8.2f} {r.b:8.2f} | "
              f"{r.L_sd:7.2f} {r.a_sd:7.2f} {r.b_sd:7.2f}")
    ref = g.loc[["34_4-6", "34_4-7", "34_7-1"]]
    print(f"\n  reference (the three already-validated wells): "
          f"L* {ref.L.min():.1f}-{ref.L.max():.1f}, "
          f"a* {ref.a.min():.2f}-{ref.a.max():.2f}, "
          f"b* {ref.b.min():.1f}-{ref.b.max():.1f}")
    print("\n  deviation of each well from the reference RANGE "
          "(0 = inside the validated range):")
    for w, r in g.iterrows():
        dL = max(0, ref.L.min() - r.L, r.L - ref.L.max())
        da = max(0, ref.a.min() - r.a, r.a - ref.a.max())
        db = max(0, ref.b.min() - r.b, r.b - ref.b.max())
        flag = "  <-- OUTSIDE" if (dL > 5 or da > 1.5 or db > 4) else ""
        print(f"    {w:10} dL* {dL:5.2f}   da* {da:5.2f}   db* {db:5.2f}{flag}")


if __name__ == "__main__":
    main()
