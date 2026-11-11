"""
v8 part D (V8_PLAN.md): tiles of the mud-log cuttings column below base
Cretaceous (Jurassic-Triassic) for the seven wells, and contact sheets of
the printed depth labels in that range (gate G1).

Geometry only: mud-log images, the calibration tables of script 54 and the
column tracker of script 55. No XRF, no photographs, no labels. The depth
range is base Cretaceous (Sodir) to the deepest photographed bag.

Run:  python 64_v8_jt_tiles.py
"""
from importlib import import_module

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

import config as C

G = import_module("54_v7_mudlog_geometry")
T = import_module("55_v7_mudlog_tiles")
E = import_module("63_v8_elements_when")
OUT = C.WORK_DIR / "v7" / "step3"
DST = OUT / "tiles_jt"


def labels_sheet(well, t, im, lo, hi, idx):
    """Depth-track crops at native resolution, centred on every 100 m line in [lo, hi].
    The crop follows the sideways drift of the sheet (taken from the tracked column)."""
    cfg = G.SHEETS[well]
    hp = int(6.0 * cfg["pxm"])
    crops = []
    for r in t[np.isclose(t.depth_m % 100, 0) & (t.depth_m >= lo) & (t.depth_m <= hi)].itertuples():
        k = idx.iloc[(idx.top_m - r.depth_m).abs().values.argmin()]
        sh = int(k.xl) - cfg["col"][0]
        x0, x1 = cfg["dtrack"][0] + sh - 50, cfg["dtrack"][1] + sh + 50
        y = int(round(r.y))
        c = im.crop((x0, y - hp, x1, y + hp)).convert("RGB")
        dr = ImageDraw.Draw(c)
        dr.line([(0, hp), (22, hp)], fill=(255, 0, 0), width=2)
        dr.line([(c.size[0] - 22, hp), (c.size[0], hp)], fill=(255, 0, 0), width=2)
        dr.rectangle([0, 0, 64, 20], fill=(255, 255, 255))
        dr.text((3, 2), f"{r.depth_m:.0f}{'' if r.detected else ' ?'}", fill=(255, 0, 0), font=T.font(16))
        crops.append(c)
    w, h = crops[0].size
    sheet = Image.new("RGB", (len(crops) * (w + 8), h), (255, 255, 255))
    for i, c in enumerate(crops):
        sheet.paste(c, (i * (w + 8), 0))
    sheet.save(OUT / "calib" / f"jt_{well}_labels.png")
    return len(crops)


def main():
    base, _ = E.EV.load_tables()
    idx3 = pd.read_csv(OUT / "tiles" / "index.csv")
    rows = []
    for well, bcu in E.BCU.items():
        cfg = G.SHEETS[well]
        im = G.load(well)
        t = pd.read_csv(OUT / "calib" / f"{well}_depth_table.csv")
        deepest = float(base.depth_m[base.well == well].max())
        top = np.floor(bcu / T.TILE_M) * T.TILE_M
        bot = min(np.ceil(deepest / T.TILE_M) * T.TILE_M, np.floor((t.depth_m.max() - T.PAD_M) / T.TILE_M) * T.TILE_M)
        # follow the column down from the deepest step-3 tile (the sheets drift sideways)
        last = idx3[idx3.well == well].sort_values("top_m").iloc[-1]
        cur, walk = (int(last.xl), int(last.xr)), {}
        for d0 in np.arange(last.bottom_m, bot, T.TILE_M):
            ya, yb = np.interp([d0, d0 + T.TILE_M], t.depth_m, t.y)
            (a, b), v = T.find_column(im, int(ya), int(yb), *cur)
            cur = (a, b)
            walk[d0] = (a, b, v)
        zoom = min(450.0 / (cfg["col"][1] - cfg["col"][0]), 1480.0 / ((T.TILE_M + 2 * T.PAD_M) * cfg["pxm"]))
        (DST / well).mkdir(parents=True, exist_ok=True)
        for d0 in np.arange(top, bot, T.TILE_M):
            xl, xr, v = walk[d0]
            img = T.render(well, im, t, d0, xl, xr, zoom)
            name = f"{well}_{int(d0):04d}.png"
            img.save(DST / well / name)
            rows.append({"well": well, "top_m": d0, "bottom_m": d0 + T.TILE_M, "tile": name, "xl": xl, "xr": xr,
                         "border_strength": round(v, 3), "w": img.size[0], "h": img.size[1]})
        x = pd.DataFrame([r for r in rows if r["well"] == well])
        r = t[(t.depth_m >= top) & (t.depth_m <= bot)]
        sp = np.diff(r.y.values)
        n = labels_sheet(well, t, im, top, bot, x)
        allw = [v[2] for v in walk.values()]
        print(f"{well}: {len(x)} tiles {top:.0f}-{bot:.0f} m (deepest bag {deepest:.0f}), column x {x.xl.min()}-{x.xl.max()}, "
              f"weakest border {x.border_strength.min():.2f} (on the way down {min(allw):.2f}); 10 m spacing px median {np.median(sp):.1f} "
              f"(min {sp.min():.1f}, max {sp.max():.1f}; nominal {10 * cfg['pxm']:.1f}), lines detected {r.detected.mean():.2f}, {n} labels on the contact sheet")
    pd.DataFrame(rows).to_csv(DST / "index.csv", index=False)
    print("tiles:", len(rows))


if __name__ == "__main__":
    main()
