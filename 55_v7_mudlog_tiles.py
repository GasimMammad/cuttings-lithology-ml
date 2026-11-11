"""
v7 step 3 (V7_PLAN.md step 3, C2): tiles of the mud-log cuttings column for
the readers.

For each well the cuttings % column is followed down the sheet (the scans
drift sideways), cut into tiles of TILE_M metres and enlarged. The script
adds only two aids, both outside the column: a depth ruler from the
calibration of 54_v7_mudlog_geometry.py (left margin) and a 0-100 % ruler
(top and bottom margins), with faint guide lines every 10 % and every 5 m.

Reads only the mud-log images and the calibration tables. No XRF, no
photographs, no labels. The depth range per well is fixed here from the
logged interval and top Shetland; bag depths are not read.

Run:  python 55_v7_mudlog_tiles.py [well ...]
"""
import sys
from importlib import import_module

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import uniform_filter1d

import config as C

G = import_module("54_v7_mudlog_geometry")
XS = import_module("35_v3_xrf_shallow")
OUT = C.WORK_DIR / "v7" / "step3"
TILE_M = 40.0
PAD_M = 2.0
# first logged depth of the cuttings column on each sheet (from the header)
LOG_TOP = {"34_4-6": 400, "34_4-7": 470, "34_7-4": 480, "34_8-3": 1318, "34_8-3_A": 996,
           "34_7-10": 440, "34_7-9": 471, "24_9-3": 145}
BELOW_M = 40.0  # digitise this far below top Shetland


def font(size):
    for f in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def col_profile(im, y0, y1, x0, x1):
    a = np.asarray(im.crop((x0, y0, x1, y1)).convert("L"))
    return uniform_filter1d((a < 110).mean(0).astype(np.float64), 5)


def find_column(im, y0, y1, xl, xr, search=45):
    """Left and right border of the column near (xl, xr): the pair of heavy
    vertical lines, a fixed width apart (+/-3 %), with the greatest strength."""
    w = xr - xl
    x0 = max(0, xl - search - 10)
    p = col_profile(im, y0, y1, x0, xr + search + 10)
    best, arg = -1.0, (xl, xr)
    for dl in range(-search, search + 1):
        a = xl + dl
        for ww in range(int(0.97 * w), int(1.03 * w) + 1):
            b = a + ww
            if a - x0 < 0 or b - x0 >= len(p):
                continue
            v = p[a - x0] + p[b - x0] - 0.002 * abs(dl)
            if v > best:
                best, arg = v, (a, b)
    return arg, best


def track_column(well, im, t, tops):
    """Column borders for every tile, walking away from the configured one."""
    cfg = G.SHEETS[well]
    y_ref = 0.33 * im.size[1]
    ys = [np.interp([d, d + TILE_M], t.depth_m, t.y) for d in tops]
    order = np.argsort([abs(y[0] - y_ref) for y in ys])
    k0 = int(order[0])
    out = {}
    cur = cfg["col"]
    for k in list(range(k0, len(tops))):
        (a, b), v = find_column(im, int(ys[k][0]), int(ys[k][1]), *cur)
        out[k] = (a, b, v)
        cur = (a, b)
    cur = out[k0][:2]
    for k in range(k0 - 1, -1, -1):
        (a, b), v = find_column(im, int(ys[k][0]), int(ys[k][1]), *cur)
        out[k] = (a, b, v)
        cur = (a, b)
    return out


def render(well, im, t, d0, xl, xr, zoom):
    pxm = G.SHEETS[well]["pxm"]
    w = xr - xl
    mx = int(0.12 * w)  # a little context either side of the column
    ya, yb = np.interp([d0 - PAD_M, d0 + TILE_M + PAD_M], t.depth_m, t.y)
    ya, yb = int(round(ya)), int(round(yb))
    c = im.crop((xl - mx, ya, xr + mx, yb)).convert("RGB")
    c = c.resize((int(c.size[0] * zoom), int(c.size[1] * zoom)), Image.LANCZOS)
    L, T = 92, 40
    out = Image.new("RGB", (c.size[0] + L + 10, c.size[1] + 2 * T), (255, 255, 255))
    out.paste(c, (L, T))
    ov = Image.new("RGBA", out.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    f, fs = font(17), font(13)
    X = lambda pct: L + (mx + w * pct / 100.0) * zoom
    Y = lambda dep: T + (np.interp(dep, t.depth_m, t.y) - ya) * zoom
    for pct in range(0, 101, 10):
        x = X(pct)
        d.line([(x, T), (x, T + c.size[1])], fill=(0, 90, 255, 70 if pct % 50 else 130), width=1)
        for yy in (4, T + c.size[1] + 4):
            d.text((x - 9, yy + 8), str(pct), fill=(0, 60, 220, 255), font=fs)
            d.line([(x, yy + (30 if yy > T else 26)), (x, yy + (36 if yy > T else 34))], fill=(0, 60, 220, 255), width=2)
    dd = np.arange(np.ceil((d0 - PAD_M) / 5) * 5, d0 + TILE_M + PAD_M + 0.01, 5.0)
    for dep in dd:
        y = Y(dep)
        inside = d0 - 1e-6 <= dep <= d0 + TILE_M + 1e-6
        d.line([(L - 12, y), (L + c.size[0], y)], fill=(230, 0, 0, 80 if inside else 40), width=1)
        d.line([(L - 12, y), (L, y)], fill=(230, 0, 0, 255), width=2)
        d.text((4, y - 10), f"{dep:.0f} m", fill=(200, 0, 0, 255) if inside else (150, 150, 150, 255), font=f)
    for dep in (d0, d0 + TILE_M):  # limits of the interval to be read
        y = Y(dep)
        d.line([(L - 12, y), (L + c.size[0], y)], fill=(0, 150, 0, 200), width=2)
    out = Image.alpha_composite(out.convert("RGBA"), ov).convert("RGB")
    return out


def main():
    rows = []
    for well in (sys.argv[1:] or G.SHEETS):
        cfg = G.SHEETS[well]
        im = G.load(well)
        t = pd.read_csv(OUT / "calib" / f"{well}_depth_table.csv")
        top = np.floor(LOG_TOP[well] / TILE_M) * TILE_M
        bot = min(XS.TOP_SHETLAND[well] + BELOW_M, t.depth_m.max() - TILE_M)
        tops = np.arange(top, bot, TILE_M)
        cols = track_column(well, im, t, tops)
        # column about 450 px wide, tile no taller than 1480 px (so the reader's image is not downscaled)
        zoom = min(450.0 / (cfg["col"][1] - cfg["col"][0]), 1480.0 / ((TILE_M + 2 * PAD_M) * cfg["pxm"]))
        (OUT / "tiles" / well).mkdir(parents=True, exist_ok=True)
        for k, d0 in enumerate(tops):
            xl, xr, v = cols[k]
            img = render(well, im, t, d0, xl, xr, zoom)
            name = f"{well}_{int(d0):04d}.png"
            img.save(OUT / "tiles" / well / name)
            rows.append({"well": well, "top_m": d0, "bottom_m": d0 + TILE_M, "tile": name, "xl": xl, "xr": xr,
                         "border_strength": round(v, 3), "w": img.size[0], "h": img.size[1]})
        x = pd.DataFrame([r for r in rows if r["well"] == well])
        print(f"{well}: {len(x)} tiles {tops[0]:.0f}-{tops[-1] + TILE_M:.0f} m, column x {x.xl.min()}-{x.xl.max()}, "
              f"width {int((x.xr - x.xl).min())}-{int((x.xr - x.xl).max())}, weakest border {x.border_strength.min():.2f}")
    idx = OUT / "tiles" / "index.csv"
    new = pd.DataFrame(rows)
    if idx.exists():
        old = pd.read_csv(idx)
        new = pd.concat([old[~old.well.isin(new.well.unique())], new])
    new.sort_values(["well", "top_m"]).to_csv(idx, index=False)


if __name__ == "__main__":
    main()
