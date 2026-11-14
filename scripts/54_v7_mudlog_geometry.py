"""
v7 step 3 (V7_PLAN.md step 3, C2.1): geometry of the mud-log sheets.

For each sheet: find the heavy horizontal grid lines (one every 10 m), chain
them into a pixel -> depth table from one anchor read by eye from a printed
depth label, and write a contact sheet of the depth track at every 100 m so
the calibration can be checked against the printed labels (gate G1).

Reads only the mud-log images. No XRF, no photographs, no labels.

Run:  python 54_v7_mudlog_geometry.py [well ...]
"""
import sys

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
from scipy.ndimage import uniform_filter1d
from scipy.signal import find_peaks

import config as C

Image.MAX_IMAGE_PIXELS = None
OUT = C.WORK_DIR / "v7" / "step3"
SRC = OUT / "mudlogs"

# file; px per m (nominal); x-range of a gridded track used to find the 10 m
# lines; x-range of the depth track (labels); approximate x-range of the
# cuttings column; anchor (y pixel of a labelled line, its depth in m).
SHEETS = {
    "34_4-6": dict(f="34_4-6_MUD_LOG_MD_PLOT_1.TIF", pxm=23.8, grid=(2150, 3300), dtrack=(1880, 2110),
                   col=(3308, 3609), anchor=(22190, 1050.0), family="anadrill"),
    "34_4-7": dict(f="34_4-7_MUD_LOG_MD_PLOT_1.TIF", pxm=23.4, grid=(1450, 2900), dtrack=(930, 1040),
                   col=(1040, 1345), anchor=(25246, 1200.0), family="exlog"),
    "34_7-4": dict(f="34_7-4_MUD_LOG_MD_PLOT_1.TIF", pxm=23.6, grid=(1400, 2840), dtrack=(850, 990),
                   col=(990, 1300), anchor=(27358, 1400.0), family="exlog"),
    "34_8-3": dict(f="34_8-3_MUD_LOG_MD_PLOT_1.TIF", pxm=23.4, grid=(2500, 3900), dtrack=(2010, 2130),
                   col=(2130, 2440), anchor=(20264, 2000.0), family="exlog"),
    "34_8-3_A": dict(f="34_8-3_A_MUD_LOG_MD_PLOT_1.TIF", pxm=23.6, grid=(1190, 2670), dtrack=(700, 800),
                     col=(800, 1110), anchor=(22427, 1700.0), family="exlog"),
    "34_7-10": dict(f="34_7-10_MUD_LOG_REPORT_1_ENCL_1.TIF", pxm=15.75, grid=(812, 1787), dtrack=(470, 550),
                    col=(550, 760), anchor=(16606, 1200.0), family="exlog"),
    "34_7-9": dict(f="34_7-9_MUD_LOG_REPORT_1_ENCL_1.TIF", pxm=15.75, grid=(780, 1750), dtrack=(440, 515),
                   col=(515, 720), anchor=(18109, 1300.0), family="exlog"),
    "34_7-1": dict(f="34_7-1_MUD_LOG_MD_PLOT_1.TIF", pxm=24.2, grid=(560, 1180), dtrack=(1360, 1472),
                   col=(1472, 1775), anchor=(13289, 820.0), family="gearhart1984"),  # X3 (text route)
    "34_7-9_saga": dict(f="34_7-9_SAGA_LITH.TIF", pxm=24.2, grid=(200, 1000), dtrack=(1091, 1234),
                        col=(1234, 1527), anchor=(21868, 1220.0), family="saga"),  # X2: rendered from the PDF at scale 5
    "24_9-3": dict(f="24_9-3_MUD_LOG_MD_PLOT_1.TIF", pxm=15.7, grid=(1440, 2200), dtrack=(1050, 1150),
                   col=(1163, 1364), anchor=(17300, 1080.0), family="gearhart"),
}


def load(well):
    im = Image.open(SRC / SHEETS[well]["f"])
    return im


def row_profile(im, x0, x1, thr=110):
    """Dark fraction of each pixel row over [x0, x1), read in bands."""
    W, H = im.size
    out = np.empty(H, np.float32)
    for y in range(0, H, 4000):
        a = np.asarray(im.crop((x0, y, x1, min(H, y + 4000))).convert("L"))
        out[y:y + a.shape[0]] = (a < thr).mean(1)
    return out


def heavy_lines(prof, s10):
    """Candidate 10 m lines: the strongest row in each ~10 m neighbourhood."""
    p = uniform_filter1d(prof, 5)
    pk, pr = find_peaks(p, distance=int(0.55 * s10), height=0.35)
    return pk, pr["peak_heights"]


def chain(prof, y0, s10, H, n=5):
    """Comb tracker. From the anchor line, step one 10 m line at a time. At
    each step the next line position and the local spacing are chosen to
    maximise the summed line strength of the next `n` comb teeth, so a single
    stray line (a curve, a lithology symbol, a seam) cannot pull the chain.
    Returns y per 10 m index, a hit flag (line strength at the tooth), k0."""
    p = uniform_filter1d(prof.astype(np.float64), 5)
    p = p - uniform_filter1d(p, int(s10))  # remove the local background
    offs = np.arange(-int(0.12 * s10), int(0.12 * s10) + 1)
    scal = np.linspace(0.97, 1.03, 13)

    def walk(sign):
        ys, s, y = [], float(s10), float(y0)
        while True:
            best, arg = -1e9, (0, s)
            for sc in scal:
                ss = s * sc
                teeth = y + sign * ss * np.arange(1, n + 1)
                for o in offs:
                    t = np.round(teeth + o).astype(int)
                    t = t[(t >= 0) & (t < H)]
                    if len(t) == 0:
                        continue
                    v = p[t].sum() - 0.002 * abs(o) - 0.5 * abs(sc - 1)
                    if v > best:
                        best, arg = v, (o, ss)
            o, ss = arg
            yn = y + sign * ss + o
            if not (0 <= yn < H):
                break
            s = 0.7 * s + 0.3 * abs(yn - y) if abs(abs(yn - y) - s) < 0.08 * s else s
            y = yn
            ys.append((y, p[int(round(y))] > 0.15))
        return ys
    up, dn = walk(-1), walk(+1)
    ys = up[::-1] + [(float(y0), True)] + dn
    return np.array([y for y, _ in ys]), np.array([h for _, h in ys]), len(up)


def calibrate(well, im=None, verbose=True):
    cfg = SHEETS[well]
    im = im or load(well)
    W, H = im.size
    s10 = cfg["pxm"] * 10
    prof = row_profile(im, *cfg["grid"])
    pk, ph = heavy_lines(prof, s10)
    if cfg["anchor"] is None:
        return dict(peaks=pk, prof=prof)
    ya, da = cfg["anchor"]
    j = np.argmin(np.abs(pk - ya))
    assert abs(pk[j] - ya) < 0.2 * s10, (well, "anchor is not on a detected line", pk[j], ya)
    ys, hit, k0 = chain(prof, pk[j], s10, H)
    d = da + 10.0 * (np.arange(len(ys)) - k0)
    t = pd.DataFrame({"y": ys, "depth_m": d, "detected": hit})
    if verbose:
        sp = np.diff(ys)
        print(f"{well}: {len(t)} lines, detected {hit.mean():.2f}, depth {d.min():.0f}-{d.max():.0f} m, "
              f"spacing px/10 m median {np.median(sp):.1f} (p1 {np.percentile(sp, 1):.1f}, p99 {np.percentile(sp, 99):.1f})")
    return dict(table=t, peaks=pk, prof=prof)


def contact_sheet(well, t, im, step=100.0, half_m=8.0):
    """Depth-track crops centred on every `step` m line, predicted y in red."""
    cfg = SHEETS[well]
    x0, x1 = cfg["dtrack"][0] - 40, cfg["col"][1] + 40
    hp = int(half_m * cfg["pxm"])
    rows = t[np.isclose(t.depth_m % step, 0)]
    tiles = []
    for r in rows.itertuples():
        y = int(round(r.y))
        if y - hp < 0 or y + hp > im.size[1]:
            continue
        c = im.crop((x0, y - hp, x1, y + hp)).convert("RGB")
        s = 150 / c.size[1]
        c = c.resize((int(c.size[0] * s), 150))
        dr = ImageDraw.Draw(c)
        dr.line([(0, 75), (c.size[0], 75)], fill=(255, 0, 0), width=1)
        dr.rectangle([0, 0, 62, 13], fill=(255, 255, 255))
        dr.text((2, 1), f"{r.depth_m:.0f} {'' if r.detected else '?'}", fill=(255, 0, 0))
        tiles.append(c)
    if not tiles:
        return
    w = tiles[0].size[0]
    ncol = max(1, 1500 // (w + 4))
    nrow = int(np.ceil(len(tiles) / ncol))
    sheet = Image.new("RGB", (ncol * (w + 4), nrow * 154), (255, 255, 255))
    for i, c in enumerate(tiles):
        sheet.paste(c, ((i % ncol) * (w + 4), (i // ncol) * 154))
    sheet.save(OUT / "calib" / f"{well}_labels.png")


def main():
    (OUT / "calib").mkdir(parents=True, exist_ok=True)
    for well in (sys.argv[1:] or SHEETS):
        im = load(well)
        r = calibrate(well, im)
        if "table" not in r:
            print(well, "no anchor yet;", len(r["peaks"]), "candidate lines; first", r["peaks"][:8])
            continue
        r["table"].to_csv(OUT / "calib" / f"{well}_depth_table.csv", index=False)
        contact_sheet(well, r["table"], im)


if __name__ == "__main__":
    main()
