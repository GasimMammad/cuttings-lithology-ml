"""
v7 extra X3 (V7_PLAN.md "Extras"): reader tiles for 34/7-1 (text route) and
24/9-4 (hand-drawn wellsite geologist log). Reads only the mud-log images.

  34/7-1  80 m tiles: calibrated depth ruler + the cuttings column + the
          description column (the column holds only single-row minor symbols,
          so the description text is read; route B of agent5_inventory.md).
  24/9-4  main-bore sheets down to 1753 m (sidetrack below): each sheet body in
          three overlapping pieces showing the sheet's own handwritten depth
          labels, the cuttings column and a 0-100 % ruler. No script depth.

Run:  python 61_v7_x3_tiles.py
"""
from importlib import import_module

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

import config as C

G = import_module("54_v7_mudlog_geometry")
T = import_module("55_v7_mudlog_tiles")
OUT = C.WORK_DIR / "v7" / "step3"
# 24/9-4 main bore: frame index -> printed depth interval (from the sheet headers)
F94 = {8: (130, 272), 9: (270, 412), 22: (410, 542), 21: (560, 682), 20: (690, 832), 19: (832, 972),
       18: (970, 1112), 17: (1110, 1250), 16: (1250, 1390), 15: (1390, 1530), 14: (1530, 1670), 13: (1670, 1812)}
COL94, DEP94, BODY94 = (550, 746), (70, 170), (880, 3120)


def tiles_3471():
    w, cfg = "34_7-1", G.SHEETS["34_7-1"]
    im = G.load(w)
    t = pd.read_csv(OUT / "calib" / f"{w}_depth_table.csv")
    (OUT / "tiles" / "34_7-1_text").mkdir(parents=True, exist_ok=True)
    rows = []
    for d0 in np.arange(440, 1860, 80.0):
        ya, yb = np.interp([d0 - 2, d0 + 82], t.depth_m, t.y).astype(int)
        left = im.crop((cfg["dtrack"][0], ya, cfg["col"][1] + 130, yb)).convert("RGB")
        desc = im.crop((3020, ya, 3800, yb)).convert("RGB")
        z = 1400.0 / (yb - ya)
        left = left.resize((int(left.size[0] * z), 1400)); desc = desc.resize((int(desc.size[0] * z), 1400))
        out = Image.new("RGB", (90 + left.size[0] + 10 + desc.size[0], 1400), (255, 255, 255))
        out.paste(left, (90, 0)); out.paste(desc, (90 + left.size[0] + 10, 0))
        dr = ImageDraw.Draw(out)
        for dep in np.arange(np.ceil((d0 - 2) / 10) * 10, d0 + 82.01, 10):
            y = (np.interp(dep, t.depth_m, t.y) - ya) * z
            inside = d0 <= dep <= d0 + 80
            dr.line([(70, y), (90, y)], fill=(220, 0, 0), width=2)
            dr.text((4, y - 6), f"{dep:.0f} m", fill=(200, 0, 0) if inside else (150, 150, 150))
        for dep in (d0, d0 + 80):
            y = (np.interp(dep, t.depth_m, t.y) - ya) * z
            dr.line([(70, y), (out.size[0], y)], fill=(0, 150, 0), width=2)
        name = f"34_7-1_{int(d0):04d}.png"
        out.save(OUT / "tiles" / "34_7-1_text" / name)
        rows.append({"well": "34_7-1", "top_m": d0, "bottom_m": d0 + 80, "tile": name})
    return rows


def tiles_2494():
    im = Image.open(OUT / "mudlogs" / "24_9-4_MUD_LOG_MD_PLOT_4.TIF")
    (OUT / "tiles" / "24_9-4").mkdir(parents=True, exist_ok=True)
    rows = []
    for k, (a, b) in sorted(F94.items(), key=lambda x: x[1]):
        im.seek(k)
        f = im.convert("L")
        y0, y1 = BODY94
        edges = np.linspace(y0, y1, 4).astype(int)
        for i in range(3):
            ya, yb = max(y0, edges[i] - 60), min(y1, edges[i + 1] + 60)
            dep = f.crop((DEP94[0], ya, DEP94[1], yb)); col = f.crop((COL94[0] - 20, ya, COL94[1] + 20, yb))
            z = 2.0
            dep = dep.resize((int(dep.size[0] * z), int(dep.size[1] * z))); col = col.resize((int(col.size[0] * z), int(col.size[1] * z)))
            H = col.size[1] + 80
            out = Image.new("RGB", (dep.size[0] + 20 + col.size[0], H), (255, 255, 255))
            out.paste(dep.convert("RGB"), (0, 40)); xc = dep.size[0] + 20; out.paste(col.convert("RGB"), (xc, 40))
            dr = ImageDraw.Draw(out)
            for pct in range(0, 101, 10):
                x = xc + (20 + (COL94[1] - COL94[0]) * pct / 100) * z
                for yy in (2, H - 34):
                    dr.text((x - 8, yy + 6), str(pct), fill=(0, 60, 220))
                dr.line([(x, 40), (x, H - 40)], fill=(150, 180, 255), width=1)
            name = f"24_9-4_f{k:02d}_{i + 1}.png"
            out.save(OUT / "tiles" / "24_9-4" / name)
            rows.append({"well": "24_9-4", "frame": k, "piece": i + 1, "sheet_interval": f"{a}-{b}", "tile": name})
    return rows


def main():
    r = tiles_3471() + tiles_2494()
    pd.DataFrame(r).to_csv(OUT / "tiles" / "index_x3.csv", index=False)
    print(pd.DataFrame(r).groupby("well").size().to_string())


if __name__ == "__main__":
    main()
