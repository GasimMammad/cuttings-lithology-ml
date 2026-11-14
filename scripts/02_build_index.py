"""
STEP 2 -- Build the master index: one row per photograph, with well and depth.

This table is the backbone of the whole project. Everything downstream joins
onto it. Getting the depth right matters more than anything else you will do
in the ML part, so this script runs in DRY RUN mode first and shows you what
it extracted, before you commit.

Run:  python 02_build_index.py            (dry run, shows what it would do)
      python 02_build_index.py --commit   (writes the index)
"""

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import config as C


# =============================================================================
# DEPTH PARSING -- adapted 2026-07-31 to the NOROG Digital Cuttings Project
# naming convention found on this SSD:
#   <well>_CUTTINGS_PHOTO_M_<depth-in-CENTIMETRES>_<W|U>_<exposure>.JPG
#   e.g. 34_4-6_CUTTINGS_PHOTO_M_100000_W_1.JPG  ->  1000.00 m, white light
# Confirmed against the depth label printed inside the photographs.
#
# We accept ONLY white-light (_W_) cuttings photos. This single rule also
# excludes UV frames (_U_), camera-raw duplicates (CUTTINGS_PHOTO_RAW_M),
# core photos (CORE_PHOTO) and scanned report pages, none of which match.
# =============================================================================

RE_NOROG_W = re.compile(r"_CUTTINGS_PHOTO_M_(\d+)_W_\d+$")
RE_NOROG_UV = re.compile(r"_CUTTINGS_PHOTO_M_(\d+)_U_\d+$")


def parse_depth(stem: str):
    """Return (depth_m, method) or (None, reason)."""
    m = RE_NOROG_W.search(stem)
    if m:
        d = float(m.group(1)) / 100.0        # centimetres -> metres
        if 0 < d < 6000:
            return d, "norog_cm"
        return None, "depth_out_of_range"

    if RE_NOROG_UV.search(stem):
        return None, "uv_excluded"           # ultraviolet frame, by decision

    if "CUTTINGS_PHOTO" in stem:
        return None, "cuttings_but_unparsed"  # should not happen; investigate

    return None, "not_a_cuttings_photo"      # core photos, report scans, etc.


# =============================================================================
# WELL PARSING
# =============================================================================

def parse_well(row) -> str:
    """
    Work out which well a file belongs to. Tries, in order:
      1. the explicit WELL_NAME_MAP in config
      2. an EXACT match between the top-level folder and a known well name
         (on this SSD the folder Wells/<well>/ is exactly the well name)
      3. a word-boundary-safe search in the path/filename. Plain substring
         matching is NOT safe: "34_7-1" is a substring of "34_7-10", which
         would silently mis-assign files once more wells are added.
    """
    candidates = [str(row.folder_1), str(row.folder_2), str(row.folder_3), str(row.stem)]

    for cand in candidates:
        if cand in C.WELL_NAME_MAP:
            return C.WELL_NAME_MAP[cand]

    for cand in candidates[:3]:                      # exact folder match
        if cand in C.WELLS:
            return cand

    haystack = " ".join(candidates).lower()
    for w in C.WELLS:
        # match 34_4-6, 34/4-6, 34-4-6 styles, but never inside a longer name
        variants = {w.lower(), w.replace("_", "/").lower(), w.replace("_", "-").lower()}
        for v in variants:
            if re.search(re.escape(v) + r"(?![0-9a-z])", haystack):
                return w

    return "UNKNOWN"


def main(commit: bool):
    if not C.INVENTORY_CSV.exists():
        raise SystemExit("Run 01_inventory.py first.")

    inv = pd.read_csv(C.INVENTORY_CSV)
    imgs = inv[inv.ext.isin(C.IMAGE_EXTS)].copy()
    if imgs.empty:
        raise SystemExit("No image files in the inventory. Check IMAGE_EXTS in config.py.")

    for col in ("folder_1", "folder_2", "folder_3", "stem"):
        imgs[col] = imgs[col].fillna("")

    parsed = imgs.stem.apply(lambda s: pd.Series(parse_depth(str(s)), index=["depth_m", "how"]))
    imgs = pd.concat([imgs, parsed], axis=1)
    imgs["well"] = imgs.apply(parse_well, axis=1)

    # W_1 = "standard" processing (colour-calibrated, consistent across the
    # project) -> used for training. W_2 = "dynamic" (per-image Adobe Auto)
    # -> kept in the index but EXCLUDED from training; reserved as a
    # colour-robustness test set (predict W_2 of held-out wells only).
    imgs["processing"] = np.where(
        imgs.stem.str.contains(r"_W_1$"), "standard",
        np.where(imgs.stem.str.contains(r"_W_2$"), "dynamic", ""))

    print("=" * 70)
    print("DEPTH PARSING RESULT")
    print("=" * 70)
    print(imgs.how.value_counts().to_string())

    ok = imgs[imgs.depth_m.notna()]
    bad = imgs[imgs.depth_m.isna()]
    print(f"\nParsed depth for {len(ok):,} of {len(imgs):,} images "
          f"({100*len(ok)/len(imgs):.1f}%)")

    print("\nSPOT CHECK -- verify these by eye before committing")
    for _, r in imgs.sample(min(25, len(imgs)), random_state=1).iterrows():
        d = f"{r.depth_m:8.1f}" if pd.notna(r.depth_m) else "    None"
        print(f"  {str(r.stem)[:50]:<52} -> well={r.well:<10} depth={d}  ({r.how})")

    if len(bad):
        print(f"\nFAILED TO PARSE ({len(bad)} files), examples:")
        for name in bad.stem.head(10):
            print("   ", name)

    print("\n" + "=" * 70)
    print("WELL ASSIGNMENT")
    print("=" * 70)
    print(imgs.well.value_counts().to_string())

    if (imgs.well == "UNKNOWN").any():
        print("\nSome files could not be assigned to a well. Fill in WELL_NAME_MAP")
        print("in config.py using the folder names printed by script 01.")

    print("\n" + "=" * 70)
    print("DEPTH RANGE PER WELL")
    print("=" * 70)
    if len(ok):
        summary = (ok.groupby("well").depth_m
                   .agg(n="count", min_m="min", max_m="max", median_m="median")
                   .round(1))
        print(summary.to_string())
        print("\nSanity check: do these depth ranges look like real well depths?")
        print("If a well shows a range like 1 to 300 you have parsed a sample")
        print("number, not a depth. Fix parse_depth() and rerun.")

        # ---- sampling statistics per well (unique depths, spacing, gaps) ----
        # A "unique depth" is one physical cuttings sample; several photos can
        # share it. The modal (most common) spacing tells us the sampling
        # interval, and gaps > 3x modal flag missing sample runs.
        print("\n" + "=" * 70)
        print("SAMPLING STATISTICS PER WELL (unique depths, not photo counts)")
        print("=" * 70)
        for well, grp in ok[ok.well != "UNKNOWN"].groupby("well"):
            depths = np.sort(grp.depth_m.unique())
            n_uniq = len(depths)
            line = f"{well}: {n_uniq} unique depths"
            if n_uniq >= 2:
                diffs = np.round(np.diff(depths), 2)
                vals, counts = np.unique(diffs, return_counts=True)
                modal = vals[np.argmax(counts)]
                line += (f", modal spacing {modal:g} m "
                         f"({counts.max()} of {len(diffs)} intervals)")
                print(line)
                gaps = [(depths[i], depths[i + 1], diffs[i])
                        for i in range(len(diffs)) if diffs[i] > 3 * modal]
                if gaps:
                    print(f"    gaps > 3x modal spacing: {len(gaps)}")
                    for top, base, g in sorted(gaps, key=lambda t: -t[2])[:5]:
                        print(f"      {top:8.1f} -> {base:8.1f} m  (gap {g:g} m)")
                    if len(gaps) > 5:
                        print(f"      ... and {len(gaps) - 5} smaller ones")
                else:
                    print("    no gaps > 3x modal spacing")
            else:
                print(line)

    if not commit:
        print("\n>>> DRY RUN. Nothing written.")
        print(">>> If the spot check above looks correct, rerun with:  --commit")
        return

    out = ok[ok.well != "UNKNOWN"].copy()
    out = out[["path", "filename", "stem", "well", "depth_m", "how",
               "processing", "size_mb"]]
    out = out.sort_values(["well", "depth_m", "processing"]).reset_index(drop=True)
    out.to_csv(C.INDEX_CSV, index=False)
    print(f"\nWritten {len(out):,} rows to {C.INDEX_CSV}")
    print(out.processing.value_counts().to_string())
    print("Next: 03_make_labels.py")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true", help="write the index file")
    main(ap.parse_args().commit)
