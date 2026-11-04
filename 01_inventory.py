"""
STEP 1 -- Find out what is actually on the SSD.

You cannot write code against data you have not looked at. This script walks
the cuttings folder, counts everything, samples a few images, and writes an
inventory table. Run it first, read the output carefully, then come back and
fill in the well name mapping in config.py if needed.

Run:  python 01_inventory.py
"""

from pathlib import Path
from collections import Counter

import pandas as pd
from PIL import Image

import config as C


def scan(root: Path) -> pd.DataFrame:
    exclude = getattr(C, "SCAN_EXCLUDE_DIRS", set())
    rows = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.name.startswith("."):          # skip .DS_Store and friends
            continue
        rel = p.relative_to(root)
        parts = rel.parts
        if any(part in exclude for part in parts[:-1]):   # skip junk folders
            continue
        rows.append(
            {
                "path": str(p),
                "filename": p.name,
                "stem": p.stem,
                "ext": p.suffix.lower(),
                "size_mb": round(p.stat().st_size / 1e6, 3),
                "n_levels": len(parts),
                "folder_1": parts[0] if len(parts) > 1 else "",
                "folder_2": parts[1] if len(parts) > 2 else "",
                "folder_3": parts[2] if len(parts) > 3 else "",
            }
        )
    return pd.DataFrame(rows)


def main():
    root = C.CUTTINGS_DIR
    if not root.exists():
        raise SystemExit(
            f"\nCannot find:\n  {root}\n\n"
            "Fix SSD_ROOT / CUTTINGS_DIR in config.py.\n"
            "To see mounted drives, run in Terminal:  ls /Volumes\n"
        )

    print(f"Scanning {root} ...")
    df = scan(root)

    if df.empty:
        raise SystemExit("Found no files. Check the path points at the right folder.")

    print("\n" + "=" * 70)
    print(f"TOTAL FILES        : {len(df):,}")
    print(f"TOTAL SIZE         : {df.size_mb.sum()/1000:.1f} GB")
    print("=" * 70)

    print("\nFILE TYPES")
    print(df.ext.value_counts().to_string())

    print("\nFOLDER DEPTH (how many levels below the root)")
    print(df.n_levels.value_counts().sort_index().to_string())

    print("\nTOP-LEVEL FOLDERS  <-- these are probably your wells")
    print(df.folder_1.value_counts().head(30).to_string())

    print("\nSECOND-LEVEL FOLDERS")
    print(df.folder_2.value_counts().head(30).to_string())

    imgs = df[df.ext.isin(C.IMAGE_EXTS)]
    print(f"\nIMAGE FILES: {len(imgs):,}")

    if len(imgs):
        print("\nSAMPLE FILENAMES  <-- look for the depth in here")
        for name in imgs.stem.sample(min(25, len(imgs)), random_state=0):
            print("   ", name)

        print("\nIMAGE PROPERTIES (first 8 openable images)")
        shown = 0
        for p in imgs.path:
            try:
                with Image.open(p) as im:
                    print(f"    {Path(p).name:<45} {im.size[0]}x{im.size[1]}  {im.mode}")
                shown += 1
            except Exception as e:
                print(f"    {Path(p).name:<45} FAILED TO OPEN: {e}")
            if shown >= 8:
                break

    non_img = df[~df.ext.isin(C.IMAGE_EXTS)]
    if len(non_img):
        print(f"\nNON-IMAGE FILES: {len(non_img):,}  <-- check for metadata/CSV/depth tables")
        print(non_img.ext.value_counts().head(10).to_string())
        print("\n  sample names:")
        for name in non_img.filename.sample(min(15, len(non_img)), random_state=0):
            print("   ", name)

    df.to_csv(C.INVENTORY_CSV, index=False)
    print(f"\nWritten: {C.INVENTORY_CSV}")

    print("""
-----------------------------------------------------------------------
WHAT TO DO NOW
1. Look at the sample filenames above. Where is the depth encoded?
   Is it in the filename, a folder name, or a separate metadata file?
2. Look at the top-level folder names. Do they match your well names?
   If not, fill in WELL_NAME_MAP in config.py.
3. Note the image dimensions. If they are huge (say 4000x3000), tiling
   into patches will work well. If they are small, reduce PATCH_GRID.
4. If there are CSV or TXT files, open one. It may already contain the
   depth index, which saves you parsing filenames.
Then run 02_build_index.py
-----------------------------------------------------------------------
""")


if __name__ == "__main__":
    main()
