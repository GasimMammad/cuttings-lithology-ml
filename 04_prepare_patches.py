"""
STEP 4 -- Cut each photograph into patches and cache them at 224 px.
Reworked 2026-07-31:

- W_1 ("standard" processing) photos only.
- Crop x[260,5980] x y[260,3560]: removes the printed rulers and the label
  box, keeps only cuttings (measured at full resolution, all wells).
- 4x4 grid of 16 evenly spaced SQUARE 672 px tiles, resized to 224 px --
  a 3x downsample with no aspect distortion, so fine-sand grain texture
  (18-35 px raw) survives. Replaces the spec's 3x3 non-square scheme.
- Each patch row carries: label, Vsh, zone_name, formation, ba_ppm (barite
  from the per-sample cuttings XRF -- the mud-contamination covariate used
  for leakage testing), and probe_only (mud-log probe set: NEVER train).

Default run caches labelled depths + the mud-log probe depths.
--all additionally caches every W_1 photo (prediction targets).

Run:  python 04_prepare_patches.py
      python 04_prepare_patches.py --all
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm

import config as C

Image.MAX_IMAGE_PIXELS = None       # allow large scans

try:
    import lasio
except ImportError:
    raise SystemExit("Missing lasio. Run:  pip install lasio")

# ---- approved geometry (2026-07-31) ----
CROP = (260, 260, 5980, 3560)
TILE = 672
GRID = 4


def tile_origins():
    x0, y0, x1, y1 = CROP
    xs = [round(x0 + i * (x1 - x0 - TILE) / (GRID - 1)) for i in range(GRID)]
    ys = [round(y0 + j * (y1 - y0 - TILE) / (GRID - 1)) for j in range(GRID)]
    return xs, ys


def load_ba(well: str) -> pd.Series:
    """Per-sample barite (ppm) from the cuttings XRF, indexed by depth."""
    p = C.SSD_ROOT / "Wells" / well / "DRILLING" / f"{well}_CUTTINGS_XRF_1.LAS"
    if not p.exists():
        return pd.Series(dtype=float)
    df = lasio.read(str(p), engine="normal").df()
    if "BA" not in df.columns:
        return pd.Series(dtype=float)
    s = df["BA"].copy()
    s.index = np.round(s.index.values.astype(float), 2)
    return s


def load_tops(well: str) -> pd.DataFrame:
    f = (C.SSD_ROOT / "Wells" / "files" /
         f"Well_{well.replace('_', '-', 1)}_FormationTops.txt")
    if not f.exists():
        # v2: some wells keep tops in their own folder (34_7-6)
        alt = C.SSD_ROOT / "Wells" / well / "Formation_tops.txt"
        if alt.exists():
            t = pd.read_csv(alt, sep="\t")
            return pd.DataFrame({"MD_TOP_mMD_RKB": t.iloc[:, 0],
                                 "SURFACE_NAME": t.iloc[:, 1].str.strip()})
        return pd.DataFrame(columns=["SURFACE_NAME", "MD_TOP_mMD_RKB"])
    return pd.read_csv(f, sep="\t")


def formation_of(tops: pd.DataFrame, z: float) -> str:
    below = tops[tops.MD_TOP_mMD_RKB <= z]
    return below.iloc[-1].SURFACE_NAME if len(below) else "above tops"


def main(do_all: bool):
    if not C.LABELS_CSV.exists():
        raise SystemExit("Run 03_make_labels.py --commit first.")

    df = pd.read_csv(C.LABELS_CSV)
    df = df[df.processing == "standard"].copy()      # W_1 only, by decision

    probe = pd.DataFrame(columns=["well", "depth_m", "mudlog_label"])
    probe_path = C.WORK_DIR / "03_mudlog_probe.csv"
    if probe_path.exists():
        probe = pd.read_csv(probe_path)
    probe_key = set(zip(probe.well, np.round(probe.depth_m, 2)))

    is_probe = [ (w, round(z, 2)) in probe_key
                 for w, z in zip(df.well, df.depth_m) ]
    df["probe_only"] = is_probe

    if do_all:
        work = df
        print(f"Caching ALL {len(work):,} W_1 photographs (incl. prediction targets).")
    else:
        keep = df.label.isin(C.CLASSES) | df.probe_only
        work = df[keep]
        print(f"Caching {len(work):,} photographs "
              f"({int(df.label.isin(C.CLASSES).sum()):,} labelled + "
              f"{int(df.probe_only.sum())} mud-log probe).")

    C.PATCH_DIR.mkdir(parents=True, exist_ok=True)
    xs, ys = tile_origins()

    ba_by_well = {w: load_ba(w) for w in work.well.unique()}
    tops_by_well = {w: load_tops(w) for w in work.well.unique()}

    rows = []
    skipped = {"too_small": 0, "unreadable": 0}

    for _, r in tqdm(work.iterrows(), total=len(work), desc="tiling"):
        src = Path(r.path)
        try:
            with Image.open(src) as im:
                if im.size[0] * im.size[1] < C.MIN_IMAGE_PIXELS:
                    skipped["too_small"] += 1
                    continue
                if im.size != (6000, 4000):
                    # geometry was measured on 6000x4000 frames; scale crop
                    sx, sy = im.size[0] / 6000.0, im.size[1] / 4000.0
                else:
                    sx = sy = 1.0

                well_dir = C.PATCH_DIR / str(r.well)
                well_dir.mkdir(exist_ok=True)

                zkey = round(float(r.depth_m), 2)
                ba = ba_by_well[r.well].get(zkey, np.nan)
                fm = formation_of(tops_by_well[r.well], float(r.depth_m))

                for j, y in enumerate(ys):
                    for i, x in enumerate(xs):
                        box = (round(x * sx), round(y * sy),
                               round((x + TILE) * sx), round((y + TILE) * sy))
                        out_name = f"{src.stem}__r{j}c{i}.jpg"
                        out_path = well_dir / out_name
                        if not out_path.exists():
                            patch = im.crop(box).resize(
                                (C.PATCH_SIZE, C.PATCH_SIZE), Image.LANCZOS)
                            patch.save(out_path, quality=92)
                        rows.append({
                            "patch_path": str(out_path),
                            "source_stem": src.stem,
                            "tile": f"r{j}c{i}",
                            "well": r.well,
                            "depth_m": r.depth_m,
                            "gr": r.gr,
                            "vsh": r.vsh,
                            "label": r.label,
                            "zone_name": r.zone_name if isinstance(r.zone_name, str) else "",
                            "formation": fm,
                            "ba_ppm": ba,
                            "probe_only": bool(r.probe_only),
                        })
        except Exception:
            skipped["unreadable"] += 1
            continue

    out = pd.DataFrame(rows)
    out.to_csv(C.PATCHES_CSV, index=False)

    print("\n" + "=" * 70)
    print(f"PATCHES CACHED: {len(out):,}")
    print("=" * 70)
    print(f"skipped, too small : {skipped['too_small']}")
    print(f"skipped, unreadable: {skipped['unreadable']}")
    if len(out):
        tr = out[~out.probe_only]
        print("\nTrainable patches by well and label:")
        print(pd.crosstab(tr.well, tr.label).to_string())
        print(f"\nProbe-only patches (never trained on): {int(out.probe_only.sum()):,}")
        n_ba = int(np.isfinite(out.ba_ppm).sum())
        print(f"Patches with Ba covariate: {n_ba:,} of {len(out):,}")
        sample = out.patch_path.head(200)
        size_gb = (sum(Path(p).stat().st_size for p in sample) / len(sample)
                   * len(out) / 1e9)
        print(f"Approx. cache size: {size_gb:.2f} GB at {C.PATCH_DIR}")
    print(f"\nWritten: {C.PATCHES_CSV}")
    print("Next: 05_train.py")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true",
                    help="also cache unlabelled photos (prediction targets)")
    main(ap.parse_args().all)
