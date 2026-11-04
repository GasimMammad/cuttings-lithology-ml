"""
PART D4(ii) — full-resolution montage of the highest green-index photographs
inside each well's OLIGOCENE target interval, so the green material can be
confirmed by eye as glauconite pellets rather than a stain, another green
mineral, or a lighting artefact.

Native-resolution centre crops (no downsampling of the grains themselves).
Only wells whose Oligocene interval actually fires above background are
included; the script reports which wells qualified.
"""
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

import config as C

Image.MAX_IMAGE_PIXELS = None
G = pd.read_csv(C.WORK_DIR / "16_green_index_all.csv")
OLIG = {"34_7-4": (1187, 1340), "34_7-9": (1172, 1340), "34_7-10": (1093, 1350),
        "34_8-3": (1320, 1500), "34_8-3_A": (1240, 1300), "34_4-6": (1250, 1390),
        "34_4-7": (1200, 1220), "34_7-1": (1170, 1200)}
CW, CH, SC = 1100, 760, 0.62
TOPN = 4


def bg(w):
    s = G[(G.well == w) & (G.depth_m > 1450)].green_index
    return float(s.median()) if len(s) else np.nan


def main():
    cells, notes = [], []
    for w, (a, b) in OLIG.items():
        sub = G[(G.well == w) & (G.depth_m >= a) & (G.depth_m <= b)]
        if sub.empty:
            continue
        base = bg(w)
        fire = sub[sub.green_index > base].sort_values("green_index", ascending=False)
        if fire.empty:
            notes.append(f"{w}: no photograph above background — nothing to show")
            continue
        notes.append(f"{w}: {len(fire)}/{len(sub)} above background, "
                     f"showing top {min(TOPN, len(fire))}")
        for _, r in fire.head(TOPN).iterrows():
            cells.append((w, r.depth_m, r.green_index, r.path))
    for n in notes:
        print("  " + n)
    if not cells:
        print("\nNO Oligocene photograph in ANY well exceeds its own background.")
        print("No montage produced — there is nothing to confirm by eye.")
        return
    ncol = 4
    nrow = int(np.ceil(len(cells) / ncol))
    cw, ch = int(CW * SC), int(CH * SC)
    pad, lab = 10, 26
    M = Image.new("RGB", (ncol * (cw + pad) + pad,
                          nrow * (ch + pad + lab) + pad), (25, 25, 25))
    dr = ImageDraw.Draw(M)
    for i, (w, z, gi, p) in enumerate(cells):
        with Image.open(p) as im:
            W, H = im.size
            crop = im.crop((W // 2 - CW // 2, H // 2 - CH // 2,
                            W // 2 + CW // 2, H // 2 + CH // 2))
            crop = crop.convert("RGB").resize((cw, ch), Image.LANCZOS)
        x = pad + (i % ncol) * (cw + pad)
        y = pad + (i // ncol) * (ch + pad + lab)
        M.paste(crop, (x, y))
        dr.text((x + 4, y + ch + 5),
                f"{w.replace('_','/')}  {z:.0f} m   green={gi:.4f}",
                fill=(110, 235, 140))
    out = C.FIG_DIR / "19_oligocene_montage.jpg"
    M.save(out, quality=93)
    print(f"\nmontage: {out}  ({M.size[0]}x{M.size[1]}, native-resolution crops)")


if __name__ == "__main__":
    main()
