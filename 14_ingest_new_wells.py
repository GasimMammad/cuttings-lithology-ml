"""
PART A1 — inventory + depth parsing for all ten wells across TWO roots.
W_1 photographs only. DRY RUN: prints parsed examples and per-well statistics,
writes nothing until --commit.

Both data roots are read-only; this only lists and parses filenames.
"""
import argparse
import re
import sys

import numpy as np
import pandas as pd

import config as C

RX_W1 = re.compile(r"_CUTTINGS_PHOTO_M_(\d+)_W_1$")
RX_ANY = re.compile(r"_CUTTINGS_PHOTO_M_(\d+)_([WU])_(\d+)$")


def parse_depth(stem: str):
    """NOROG DCP convention: depth in CENTIMETRES, W_1 = standard processing."""
    m = RX_W1.search(stem)
    if m:
        d = float(m.group(1)) / 100.0
        return (d, "norog_cm") if 0 < d < 6000 else (None, "depth_out_of_range")
    m = RX_ANY.search(stem)
    if m:
        return None, f"excluded_{m.group(2)}_{m.group(3)}"
    if "CUTTINGS_PHOTO" in stem:
        return None, "cuttings_but_unparsed"
    return None, "not_a_cuttings_photo"


def scan_well(well):
    d = C.drilling_dir(well)
    rows = []
    for p in sorted(d.iterdir()):
        if p.name.startswith("."):
            continue
        if p.suffix.lower() not in C.IMAGE_EXTS:
            continue
        depth, how = parse_depth(p.stem)
        rows.append({"well": well, "path": str(p), "stem": p.stem,
                     "depth_m": depth, "how": how,
                     "size_mb": round(p.stat().st_size / 1e6, 2)})
    return pd.DataFrame(rows)


def main(commit, wells):
    frames = []
    for w in wells:
        try:
            root = C.well_dir(w)
        except FileNotFoundError as e:
            print(f"[{w}] {e}")
            continue
        df = scan_well(w)
        frames.append(df)
        ok = df[df.depth_m.notna()]
        print("=" * 96)
        print(f"{w}   root: {root}")
        print("=" * 96)
        print(f"  image files scanned : {len(df):,}")
        print(f"  parsed as W_1       : {len(ok):,}")
        print("  parse outcomes      : "
              + ", ".join(f"{k}={v}" for k, v in df.how.value_counts().items()))
        if ok.empty:
            print("  !! NO W_1 PHOTOS PARSED"); continue
        dep = np.sort(ok.depth_m.unique())
        print(f"  depth range         : {dep.min():.1f} - {dep.max():.1f} m")
        print(f"  unique depths       : {len(dep)}")
        diffs = np.round(np.diff(dep), 2)
        if len(diffs):
            vals, cnts = np.unique(diffs, return_counts=True)
            print(f"  modal spacing       : {vals[np.argmax(cnts)]:g} m "
                  f"({cnts.max()} of {len(diffs)} intervals)")
        print(f"  mean file size      : {ok.size_mb.mean():.1f} MB")
        print("\n  25 PARSED EXAMPLES (verify by eye):")
        for _, r in ok.sample(min(25, len(ok)), random_state=0).sort_values("depth_m").iterrows():
            print(f"    {r.stem:<48} -> {r.depth_m:8.1f} m")
        print()
    allw = pd.concat(frames, ignore_index=True)
    ok = allw[allw.depth_m.notna()]
    print("=" * 96)
    print(f"TOTAL W_1 PHOTOGRAPHS ACROSS {ok.well.nunique()} WELLS: {len(ok):,}")
    print("=" * 96)
    print(ok.groupby("well").agg(n=("depth_m", "size"),
                                 uniq=("depth_m", "nunique"),
                                 top=("depth_m", "min"),
                                 base=("depth_m", "max")).to_string())
    if not commit:
        print("\n>>> DRY RUN. Nothing written. Rerun with --commit after approval.")
        return
    out = C.WORK_DIR / "14_index_all_wells.csv"
    ok.to_csv(out, index=False)
    print(f"\nWritten: {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--wells", nargs="*", default=None)
    a = ap.parse_args()
    main(a.commit, a.wells or C.ALL_WELLS)
