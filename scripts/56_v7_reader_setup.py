"""
v7 step 3 (V7_PLAN.md C2.2, C3): work folders for the two tile readers.

Reader A reads every tile; reader B reads a seeded random 30 % of each well's
tiles plus the symbol-audit tiles (chosen from the column images by pattern
alone, see AUDIT). Each folder holds only what a reader may open: its tiles,
the sheet's legend, the rules and a list giving the (seeded random) order.

Also writes calib/G1_labels.csv: the printed 100 m labels checked by eye.

Run:  python 56_v7_reader_setup.py
"""
import shutil
from importlib import import_module

import numpy as np
import pandas as pd

import config as C

XS = import_module("35_v3_xrf_shallow")
OUT = C.WORK_DIR / "v7" / "step3"
RULES = C.REPO_DIR / "results" / "v7" / "step3" / "reader_rules.md" if hasattr(C, "REPO_DIR") else None
SEED_A, SEED_B, FRAC_B, CHUNK = 5601, 5602, 0.30, 36
# tiles (top depth) holding the non-clay patterns named in check_step3_protocol.md
AUDIT = {"34_4-6": [1200, 1240, 1640, 1800], "34_4-7": [1160, 1720], "34_7-4": [1160, 1680],
         "34_8-3_A": [1080, 1200], "34_7-9": [1600, 1640], "34_7-10": [1080], "24_9-3": [520, 1080, 1760, 1880],
         "34_8-3": []}
# printed 100 m labels seen centred on their calibrated line (contact sheets, 2026-11-10)
G1 = {"34_4-6": (400, 1900), "34_4-7": (500, 1900), "34_7-4": (500, 1900), "34_8-3": (1300, 2100),
      "34_8-3_A": (1000, 2200), "34_7-10": (500, 1900), "34_7-9": (500, 1900), "24_9-3": (300, 2900)}
G1_NOT_SEEN = {"34_4-7": [700, 1400], "34_7-9": [700, 800]}  # label faded or out of frame; line still on the grid


def folder(reader, name, well, tiles, order_rng):
    d = OUT / "readers" / reader / name
    if d.exists():
        shutil.rmtree(d)
    (d / "tiles").mkdir(parents=True)
    tiles = list(tiles)
    order_rng.shuffle(tiles)
    for t in tiles:
        shutil.copy(OUT / "tiles" / well / t, d / "tiles" / t)
    shutil.copy(OUT / "legends" / f"{well}_legend.png", d / "legend.png")
    shutil.copy("results/v7/step3/reader_rules.md", d / "reader_rules.md")
    (d / "list.txt").write_text("\n".join(tiles) + "\n")
    return {"reader": reader, "folder": name, "well": well, "n": len(tiles)}


def fix_2493():
    """The one pre-declared fix after G2 (V7_PLAN.md C3): reader C re-reads all
    of 24/9-3 with rules version 3; reader D reads a fresh 30 % (tiles reader B
    did not read)."""
    idx = pd.read_csv(OUT / "tiles" / "index.csv")
    tiles = idx[idx.well == "24_9-3"].tile.tolist()
    rc, rd = np.random.default_rng(5603), np.random.default_rng(5604)
    rows = []
    for i, part in enumerate(np.array_split(list(rc.permutation(tiles)), 2)):
        rows.append(folder("C", f"24_9-3_{i + 1}", "24_9-3", part, rc))
    bsel = pd.read_csv(OUT / "readers" / "B_selection.csv")
    rest = sorted(set(tiles) - set(bsel[bsel.well == "24_9-3"].tile))
    pick = sorted(rd.choice(rest, int(np.ceil(FRAC_B * len(tiles))), replace=False))
    rows.append(folder("D", "24_9-3_1", "24_9-3", pick, rd))
    pd.DataFrame(rows).to_csv(OUT / "readers" / "folders_fix_24_9-3.csv", index=False)
    print(pd.DataFrame(rows).to_string(index=False))


def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "fix_24_9-3":
        fix_2493()
        return
    idx = pd.read_csv(OUT / "tiles" / "index.csv")
    ra, rb = np.random.default_rng(SEED_A), np.random.default_rng(SEED_B)
    rows, bsel = [], []
    for well, g in idx.groupby("well", sort=True):
        tiles = g.tile.tolist()
        perm = list(ra.permutation(tiles))
        k = int(np.ceil(len(perm) / CHUNK))
        for i, part in enumerate(np.array_split(perm, k)):
            rows.append(folder("A", f"{well}_{i + 1}", well, part, ra))
        nb = int(np.ceil(FRAC_B * len(tiles)))
        pick = set(rb.choice(tiles, nb, replace=False))
        audit = {f"{well}_{d:04d}.png" for d in AUDIT[well]}
        assert audit <= set(tiles), (well, audit - set(tiles))
        for t in sorted(pick | audit):
            bsel.append({"well": well, "tile": t, "random": t in pick, "audit": t in audit})
        allb = sorted(pick | audit)
        kb = int(np.ceil(len(allb) / CHUNK))
        for i, part in enumerate(np.array_split(allb, kb)):
            rows.append(folder("B", f"{well}_{i + 1}", well, part, rb))
    pd.DataFrame(rows).to_csv(OUT / "readers" / "folders.csv", index=False)
    pd.DataFrame(bsel).to_csv(OUT / "readers" / "B_selection.csv", index=False)
    g1 = []
    for well, (a, b) in G1.items():
        for d in range(a, b + 1, 100):
            g1.append({"well": well, "label_m": d, "seen_centred_within_1m": d not in G1_NOT_SEEN.get(well, []),
                       "top_shetland_m": XS.TOP_SHETLAND[well]})
    pd.DataFrame(g1).to_csv(OUT / "calib" / "G1_labels.csv", index=False)
    t = pd.DataFrame(rows)
    print(t.groupby("reader").agg(folders=("folder", "size"), tiles=("n", "sum")).to_string())
    print(t.to_string(index=False))


if __name__ == "__main__":
    main()
