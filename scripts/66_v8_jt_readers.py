"""
v8 part D: reader folders for the Jurassic-Triassic tiles (script 64).
Reader JA reads every tile of a well; reader JB a seeded 20 % (at least 2).
Each folder holds the tiles in a seeded random order, the well's legend and
the rules (rules v3 unchanged + the addendum). Nothing else.

Run:  python 66_v8_jt_readers.py
"""
import shutil

import numpy as np
import pandas as pd

import config as C

OUT = C.WORK_DIR / "v7" / "step3"
SEED_A, SEED_B, FRAC_B = 5611, 5612, 0.20
ORDER = ["34_4-6", "34_7-4", "34_7-9", "34_7-10", "34_8-3", "34_4-7", "34_8-3_A"]  # by usable bags (V8_PLAN.md)
RULES = "results/v7/step3/reader_rules.md"
ADD = "results/v7/step3/reader_rules_jt_addendum.md"


def folder(reader, well, tiles, rng):
    d = OUT / "readers" / reader / well
    if d.exists():
        shutil.rmtree(d)
    (d / "tiles").mkdir(parents=True)
    tiles = list(tiles)
    rng.shuffle(tiles)
    for t in tiles:
        shutil.copy(OUT / "tiles_jt" / well / t, d / "tiles" / t)
    shutil.copy(f"results/v7/step3/{well}_legend.png", d / "legend.png")
    (d / "reader_rules.md").write_text(open(RULES).read() + open(ADD).read())
    (d / "list.txt").write_text("\n".join(tiles) + "\n")
    return {"reader": reader, "well": well, "n": len(tiles)}


def main():
    idx = pd.read_csv(OUT / "tiles_jt" / "index.csv")
    ra, rb = np.random.default_rng(SEED_A), np.random.default_rng(SEED_B)
    rows, bsel = [], []
    for well in ORDER:
        tiles = idx[idx.well == well].tile.tolist()
        rows.append(folder("JA", well, tiles, ra))
        nb = max(2, int(np.ceil(FRAC_B * len(tiles))))
        pick = sorted(rb.choice(tiles, nb, replace=False))
        bsel += [{"well": well, "tile": t} for t in pick]
        rows.append(folder("JB", well, pick, rb))
    pd.DataFrame(rows).to_csv(OUT / "readers" / "folders_jt.csv", index=False)
    pd.DataFrame(bsel).to_csv(OUT / "readers" / "JB_selection.csv", index=False)
    t = pd.DataFrame(rows)
    print(t.pivot(index="well", columns="reader", values="n").reindex(ORDER).to_string())
    print(t.groupby("reader").n.sum().to_dict())


if __name__ == "__main__":
    main()
