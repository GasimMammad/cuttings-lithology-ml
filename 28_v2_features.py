"""
v2 -- the FROZEN 15 engineered features (features.py, unchanged) for the
eleven-well set. Sharded, and tolerant of tiles that are still being written.

Which tiles: all 16 tiles of every W_1 photo, in priority order
  0. sand / clay depths (the classifier's inputs)
  1. tile r1c1 of every other photo
  2. remaining tiles of mixed / unstable depths
  3. remaining tiles of all other photos
(features.py now uses an exact fast disk opening, ~0.1 s per tile.)

Run:  python 28_v2_features.py <shard> <nshards>
      python 28_v2_features.py            (combine -> WORK_DIR/28_features.csv)
"""
import os
import sys
import time
from pathlib import Path

import pandas as pd

import config as C
from features import FEATURE_NAMES, features_for_patch

SHARD_DIR = C.WORK_DIR / "feature_shards"
IN_ZONE = {"sand", "clay", "mixed", "unstable"}


def patch_list():
    df = pd.read_csv(C.LABELS_CSV)
    df = df[df.processing == "standard"].sort_values(["well", "depth_m"])
    rows = []
    for r in df.itertuples():
        tiles = [f"r{j}c{i}" for j in range(4) for i in range(4)]
        if r.label in ("sand", "clay"):
            prio = {t: 0 for t in tiles}
        elif r.label in IN_ZONE:
            prio = {t: (1 if t == "r1c1" else 2) for t in tiles}
        else:
            prio = {t: (1 if t == "r1c1" else 3) for t in tiles}
        for t, pr in prio.items():
            rows.append({"prio": pr,"patch_path": str(C.PATCH_DIR / r.well / f"{r.stem}__{t}.jpg"),
                         "well": r.well, "depth_m": r.depth_m, "tile": t,
                         "label": r.label, "vsh": r.vsh, "gr": r.gr,
                         "zone_name": r.zone_name if isinstance(r.zone_name, str) else ""})
    return pd.DataFrame(rows)


def done_paths():
    """Patch paths already written by any earlier or concurrent shard."""
    done = set()
    for f in SHARD_DIR.glob("part_*.csv"):
        try:
            done |= set(pd.read_csv(f, usecols=["patch_path"]).patch_path)
        except Exception:
            pass
    return done


def run_shard(shard, nshards):
    """Incremental: appends one row per patch to part_<shard>_<n>.csv, skips
    patches already done (so the job can be restarted with a new shard
    count), and does in-zone tiles before the normalisation-only tiles."""
    SHARD_DIR.mkdir(parents=True, exist_ok=True)
    allp = patch_list()
    allp = allp[allp.prio <= int(os.environ.get("MAXPRIO", "3"))]   # optional cap
    allp = allp.sort_values(["prio", "well", "depth_m", "tile"], kind="stable")
    todo = allp[~allp.patch_path.isin(done_paths())]
    sub = todo.iloc[shard::nshards].drop(columns="prio").reset_index(drop=True)
    out = SHARD_DIR / f"part_{shard}_{nshards}.csv"
    cols = list(sub.columns) + FEATURE_NAMES
    if not out.exists():
        out.write_text(",".join(cols) + "\n")
    t0, n = time.time(), 0
    pending = list(range(len(sub)))
    with open(out, "a") as fh:
        while pending:
            left = []
            for k in pending:
                p = Path(sub.patch_path[k])
                if not p.exists():
                    left.append(k)
                    continue
                try:
                    f = features_for_patch(p)
                except Exception:
                    time.sleep(0.5)
                    try:
                        f = features_for_patch(p)
                    except Exception:
                        f = {c: float("nan") for c in FEATURE_NAMES}
                row = sub.iloc[k].tolist() + [f[c] for c in FEATURE_NAMES]
                pd.DataFrame([row], columns=cols).to_csv(fh, header=False, index=False)
                fh.flush()
                n += 1
                if n % 200 == 0:
                    print(f"shard {shard}: {n}/{len(sub)}  {time.time()-t0:.0f}s", flush=True)
            if left and len(left) == len(pending):
                if time.time() - t0 > 4 * 3600:
                    print(f"shard {shard}: giving up on {len(left)} missing tiles", flush=True)
                    break
                time.sleep(30)
            pending = left
    print(f"shard {shard}: DONE {n} patches in {time.time()-t0:.0f}s", flush=True)


def combine():
    files = sorted(SHARD_DIR.glob("part_*.csv"))
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df = df.drop_duplicates("patch_path")
    df = df.sort_values(["well", "depth_m", "tile"]).reset_index(drop=True)
    dest = C.WORK_DIR / "28_features.csv"
    df.to_csv(dest, index=False)
    print(f"{len(files)} shards -> {dest} ({len(df):,} rows, "
          f"{int(df[FEATURE_NAMES].isna().any(axis=1).sum())} NaN rows)")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        run_shard(int(sys.argv[1]), int(sys.argv[2]))
    else:
        combine()
