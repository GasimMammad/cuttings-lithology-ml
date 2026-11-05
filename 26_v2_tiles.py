"""
v2 STEP 4 -- cut EVERY W_1 photograph into the approved 16 tiles (sharded).

Same geometry as 04_prepare_patches.py (crop 260..5980 x 260..3560, 4x4
square 672 px tiles resized to 224 px), but for all photos, labelled or not:
unlabelled photos are needed for label-free per-well normalisation and for
blind sand-fraction logs.

Run:  python 26_v2_tiles.py <shard> <nshards>     (one process per shard)
      python 26_v2_tiles.py                       (combine shards -> PATCHES_CSV)
"""
import sys
from importlib import import_module
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

import config as C

Image.MAX_IMAGE_PIXELS = None
P4 = import_module("04_prepare_patches")
SHARD_DIR = C.WORK_DIR / "tile_shards"


def run_shard(shard, nshards):
    SHARD_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(C.LABELS_CSV)
    df = df[df.processing == "standard"].sort_values(["well", "depth_m"])
    df = df.iloc[shard::nshards]
    xs, ys = P4.tile_origins()
    ba = {w: P4.load_ba(w) for w in df.well.unique()}
    tops = {w: P4.load_tops(w) for w in df.well.unique()}
    rows, bad = [], 0
    for k, r in enumerate(df.itertuples()):
        src = Path(r.path)
        try:
            with Image.open(src) as im:
                sx, sy = im.size[0] / 6000.0, im.size[1] / 4000.0
                wd = C.PATCH_DIR / r.well
                wd.mkdir(parents=True, exist_ok=True)
                fm = P4.formation_of(tops[r.well], float(r.depth_m))
                b = ba[r.well].get(round(float(r.depth_m), 2), np.nan)
                loaded = False
                for j, y in enumerate(ys):
                    for i, x in enumerate(xs):
                        out = wd / f"{src.stem}__r{j}c{i}.jpg"
                        if not out.exists():
                            if not loaded:
                                im.load(); loaded = True
                            box = (round(x * sx), round(y * sy),
                                   round((x + P4.TILE) * sx), round((y + P4.TILE) * sy))
                            im.crop(box).resize((C.PATCH_SIZE, C.PATCH_SIZE),
                                                Image.LANCZOS).save(out, quality=92)
                        rows.append({"patch_path": str(out), "source_stem": src.stem,
                                     "tile": f"r{j}c{i}", "well": r.well,
                                     "depth_m": r.depth_m, "gr": r.gr, "vsh": r.vsh,
                                     "label": r.label,
                                     "zone_name": r.zone_name if isinstance(r.zone_name, str) else "",
                                     "formation": fm, "ba_ppm": b, "probe_only": False})
        except Exception as e:
            bad += 1
            print(f"  unreadable {src.name}: {e}", flush=True)
        if k % 50 == 0:
            print(f"shard {shard}: {k}/{len(df)}", flush=True)
    pd.DataFrame(rows).to_csv(SHARD_DIR / f"tiles_{shard}.csv", index=False)
    print(f"shard {shard}: DONE {len(rows)} patches, {bad} unreadable", flush=True)


def combine():
    parts = sorted(SHARD_DIR.glob("tiles_*.csv"))
    out = pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
    out.to_csv(C.PATCHES_CSV, index=False)
    print(f"{len(parts)} shards -> {len(out):,} patches -> {C.PATCHES_CSV}")
    print(pd.crosstab(out.well, out.label).to_string())


if __name__ == "__main__":
    if len(sys.argv) == 3:
        run_shard(int(sys.argv[1]), int(sys.argv[2]))
    else:
        combine()
