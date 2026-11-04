"""
Extract the FROZEN 15-feature set for every patch.
Sharded: run as `python 07_extract_features.py <shard> <nshards>` to process a
slice, or with no arguments to combine the shard outputs into 07_features.csv.
(Sharding avoids ProcessPoolExecutor, which deadlocks on macOS/spawn when the
parent's stdio is redirected.)

The feature list is fixed in features.py and must not change after evaluation
begins.
"""
import sys
from pathlib import Path

import pandas as pd

import config as C
from features import features_for_patch, FEATURE_NAMES

SHARD_DIR = C.WORK_DIR / "feature_shards"


def run_shard(shard, nshards):
    SHARD_DIR.mkdir(parents=True, exist_ok=True)
    p = pd.read_csv(C.PATCHES_CSV)
    sub = p.iloc[shard::nshards].copy()
    rows = []
    for n, (_, r) in enumerate(sub.iterrows(), 1):
        try:
            rows.append(features_for_patch(r.patch_path))
        except Exception:
            rows.append({k: float("nan") for k in FEATURE_NAMES})
        if n % 50 == 0:
            print(f"shard {shard}: {n}/{len(sub)}", flush=True)
    out = pd.concat([sub.reset_index(drop=True),
                     pd.DataFrame(rows)], axis=1)
    out.to_csv(SHARD_DIR / f"shard_{shard:02d}.csv", index=False)
    print(f"shard {shard}: DONE {len(out)} rows", flush=True)


def combine():
    files = sorted(SHARD_DIR.glob("shard_*.csv"))
    if not files:
        raise SystemExit("no shards found")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df = df.sort_values(["well", "depth_m", "tile"]).reset_index(drop=True)
    dest = C.WORK_DIR / "07_features.csv"
    df.to_csv(dest, index=False)
    print(f"combined {len(files)} shards -> {dest}  ({len(df):,} rows)")
    print(f"NaN rows: {int(df[FEATURE_NAMES].isna().any(axis=1).sum())}")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        run_shard(int(sys.argv[1]), int(sys.argv[2]))
    else:
        combine()
