"""
v7 step 2 (V7_PLAN.md, step 2, sections A1-A7): glauconite-pellet blob
detector at native resolution (7.14 um/px), plus the old green index (GI)
computed with the unchanged v1 function, for one set of W_1 photographs.

Sets (never joined to G here):
  lunde   all W_1 photos in the Lunde Fm (glauconite impossible): calibration
  g       all W_1 photos of bags with a defined XRF G (v6 table), Lista included

Parameters are FROZEN (spec A3-A5). Sensitivity gates (A6: pixel L* upper 45
and 55; hole filling off; per-well a*, b* median shift) are computed in the same pass, so the
drive is read once.

Run:  python 53_v7_pellet_blobs.py <set> <shard> <nshards>     one shard
      python 53_v7_pellet_blobs.py <set>                       combine shards
"""
import hashlib
import sys
import time

import numpy as np
import pandas as pd
from PIL import Image
from scipy import ndimage as ndi
from skimage.color import rgb2lab
from skimage.feature import peak_local_max
from skimage.measure import regionprops_table
from skimage.morphology import remove_small_holes
from skimage.segmentation import watershed

import config as C

Image.MAX_IMAGE_PIXELS = None
OUT = C.WORK_DIR / "v7" / "step2"

# ---- FROZEN parameters (V7_PLAN.md step 2, A1-A5) ---------------------------
CROP = (260, 260, 5980, 3560)
L_SHADOW = 12.0
H_LO, H_HI = 95.0, 200.0
C_LO, C_HI = 4.0, 30.0
L_LO, L_HI = 15.0, 50.0
A_MAX = -1.5
D_LO, D_HI = 14.0, 72.0
SOL, CIRC, AXR = 0.80, 0.50, 0.40
BL_MAX, BC_MIN = 45.0, 5.0
HOLE_PX = 30
# ---- old green index, FROZEN (16_green_index_all.py) ------------------------
GI_A_MAX, GI_C_MIN, GI_L_MIN, GI_L_MAX = -5.0, 12.0, 15.0, 80.0
GI_CROP_FRAC = (260 / 6000, 260 / 4000, 5980 / 6000, 3560 / 4000)

_DISK2 = np.array([[0, 0, 1, 0, 0], [0, 1, 1, 1, 0], [1, 1, 1, 1, 1],
                   [0, 1, 1, 1, 0], [0, 0, 1, 0, 0]], bool)  # skimage disk(2)


def green_index(path):
    """Unchanged from 16_green_index_all.py (1/8 draft decode)."""
    with Image.open(path) as im:
        im.draft("RGB", (im.size[0] // 8, im.size[1] // 8))
        im = im.convert("RGB")
        w, h = im.size
        x0, y0, x1, y1 = GI_CROP_FRAC
        im = im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))
        arr = np.asarray(im, dtype=np.float64) / 255.0
    lab = rgb2lab(arr)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    chroma = np.sqrt(a * a + b * b)
    return float(((a < GI_A_MAX) & (chroma >= GI_C_MIN) & (L > GI_L_MIN) & (L < GI_L_MAX)).mean())


def load_lab(path):
    with Image.open(path) as im:
        rgb = np.asarray(im.convert("RGB").crop(CROP), dtype=np.float32) / 255.0
    lab = np.empty(rgb.shape, np.float32)
    for y in range(0, rgb.shape[0], 550):
        lab[y:y + 550] = rgb2lab(rgb[y:y + 550])
    del rgb
    for k in range(3):
        lab[..., k] = ndi.gaussian_filter(lab[..., k], 1.0)
    return lab[..., 0], lab[..., 1], lab[..., 2]


def blobs(L, a, b, chip_n, l_hi=L_HI, a_shift=0.0, b_shift=0.0, fill=True, brown=False, detail=False):
    """Accepted-blob count and area for one gate setting."""
    a = a - a_shift
    b = b - b_shift
    Cc = np.hypot(a, b)
    h = np.degrees(np.arctan2(b, a)) % 360
    if brown:  # diagnostic only (geochemistry check): oxidised pellets, hue 40-95 deg, a* > 0
        g = (h >= 40.0) & (h < H_LO) & (Cc >= C_LO) & (Cc <= C_HI) & (L >= L_LO) & (L <= l_hi) & (a > 0)
    else:
        g = (h >= H_LO) & (h <= H_HI) & (Cc >= C_LO) & (Cc <= C_HI) & (L >= L_LO) & (L <= l_hi) & (a <= A_MAX)
    g = ndi.binary_opening(g, structure=_DISK2)
    if fill:
        g = remove_small_holes(g, HOLE_PX)
    gate_frac = g.sum() / chip_n
    lbl0, n0 = ndi.label(g)
    if n0 == 0:
        return dict(S=0.0, S_area=0.0, n_ok=0, n_cand=0, gate_frac=float(gate_frac), large_green_frac=0.0)
    dist = ndi.distance_transform_edt(g)
    pk = peak_local_max(dist, min_distance=7, threshold_abs=5, labels=lbl0, exclude_border=False)
    mk = np.zeros(g.shape, np.int32)
    mk[tuple(pk.T)] = np.arange(1, len(pk) + 1)
    lbl = watershed(-dist, mk, mask=g)
    pr = regionprops_table(lbl, intensity_image=np.dstack([L, Cc, a, b]),
                           properties=("area", "perimeter", "solidity", "major_axis_length",
                                       "minor_axis_length", "intensity_mean"))
    A = pr["area"]
    deq = np.sqrt(4 * A / np.pi)
    circ = 4 * np.pi * A / np.maximum(pr["perimeter"], 1) ** 2
    axr = pr["minor_axis_length"] / np.maximum(pr["major_axis_length"], 1e-6)
    ok = ((deq >= D_LO) & (deq <= D_HI) & (pr["solidity"] >= SOL) & (circ >= CIRC) & (axr >= AXR)
          & (pr["intensity_mean-0"] <= BL_MAX) & (pr["intensity_mean-1"] >= BC_MIN))
    # components larger than the size gate, measured before the watershed split
    big = ndi.sum(g, lbl0, np.arange(1, n0 + 1))
    big = big[np.sqrt(4 * big / np.pi) > D_HI].sum()
    out = dict(S=float(ok.sum() / chip_n * 1e6), S_area=float(A[ok].sum() / chip_n), n_ok=int(ok.sum()),
               n_cand=int(len(A)), gate_frac=float(gate_frac), large_green_frac=float(big / chip_n))
    if detail:  # descriptive histograms of the accepted blobs (size in px, hue in deg)
        hb = np.degrees(np.arctan2(pr["intensity_mean-3"][ok], pr["intensity_mean-2"][ok])) % 360
        for lo, hi in ((14, 24), (24, 36), (36, 50), (50, 72)):
            out[f"n_d{lo}_{hi}"] = int(((deq[ok] >= lo) & (deq[ok] < hi + (hi == 72))).sum())
        for lo, hi in ((95, 120), (120, 150), (150, 200)):
            out[f"n_h{lo}_{hi}"] = int(((hb >= lo) & (hb < hi + (hi == 200))).sum())
    return out


def score(path, ab_shift=None):
    t0 = time.time()
    L, a, b = load_lab(path)
    chip = L >= L_SHADOW
    n = int(chip.sum())
    r = blobs(L, a, b, n, detail=True)
    out = {**r, "chip_frac": float(chip.mean()), "L_mean": float(L[chip].mean()),
           "a_mean": float(a[chip].mean()), "b_mean": float(b[chip].mean()),
           "a_med": float(np.median(a[::8, ::8][chip[::8, ::8]])),
           "b_med": float(np.median(b[::8, ::8][chip[::8, ::8]]))}
    for tag, lh in (("L45", 45.0), ("L55", 55.0)):
        s = blobs(L, a, b, n, l_hi=lh)
        out[f"S_{tag}"], out[f"S_area_{tag}"] = s["S"], s["S_area"]
    s = blobs(L, a, b, n, fill=False)  # review round 17: hole filling off
    out["S_nofill"], out["S_area_nofill"] = s["S"], s["S_area"]
    s = blobs(L, a, b, n, brown=True)  # geochemistry check: brown rounded blobs (descriptive)
    out["S_brown"] = s["S"]
    if ab_shift is not None:  # A6 per-well normalisation (second pass only)
        s = blobs(L, a, b, n, a_shift=ab_shift[0], b_shift=ab_shift[1])
        out["S_wellnorm"], out["S_area_wellnorm"] = s["S"], s["S_area"]
    out["GI"] = green_index(path)
    out["t_s"] = time.time() - t0
    return out


def photo_set(name):
    idx = pd.read_csv(C.WORK_DIR / "02_index.csv")
    idx = idx[idx.stem.str.endswith("_W_1")][["well", "depth_m", "stem", "path"]]
    idx["depth_m"] = idx.depth_m.round(2)
    if name == "lunde":
        p = pd.read_csv(C.PATCHES_CSV, usecols=["well", "depth_m", "formation"]).drop_duplicates(["well", "depth_m"])
        key = p[p.formation.astype(str).str.upper().eq("LUNDE FM")][["well", "depth_m"]]
    elif name == "g":
        g = pd.read_csv(C.REPO_DIR / "results" / "v6" / "D_xrf_glauconite_bags.csv") if hasattr(C, "REPO_DIR") \
            else pd.read_csv("results/v6/D_xrf_glauconite_bags.csv")
        key = g[np.isfinite(g.G)][["well", "depth_m"]]  # G itself is NOT carried along
    else:
        raise SystemExit("set must be lunde or g")
    key = key.assign(depth_m=key.depth_m.round(2)).drop_duplicates()
    return idx.merge(key, on=["well", "depth_m"]).sort_values(["well", "depth_m"]).reset_index(drop=True)


def main():
    name = sys.argv[1]
    OUT.mkdir(parents=True, exist_ok=True)
    ps = photo_set(name)
    if len(sys.argv) == 2:  # combine
        parts = [pd.read_csv(f) for f in sorted(OUT.glob(f"{name}_shard_*.csv"))]
        t = pd.concat(parts).drop_duplicates("stem").sort_values(["well", "depth_m"])
        missing = set(ps.stem) - set(t.stem)
        t.to_csv(OUT / f"{name}_scores.csv", index=False)
        h = hashlib.sha256((OUT / f"{name}_scores.csv").read_bytes()).hexdigest()
        print(f"{name}: {len(t)} photos, missing {len(missing)}, sha256 {h}")
        print(t.groupby("well").S.describe().round(2).to_string())
        return
    shard, nsh = int(sys.argv[2]), int(sys.argv[3])
    f = OUT / f"{name}_shard_{shard}of{nsh}.csv"
    done = set(pd.read_csv(f).stem) if f.exists() else set()
    rows = pd.read_csv(f).to_dict("records") if f.exists() else []
    shift = None
    sf = OUT / f"{name}_well_ab_median.csv"  # written by the wellnorm step, if run
    if sf.exists():
        shift = pd.read_csv(sf, index_col=0)
    for i, r in enumerate(ps.iloc[shard::nsh].itertuples()):
        if r.stem in done:
            continue
        try:
            ab = (shift.loc[r.well, "a"], shift.loc[r.well, "b"]) if shift is not None else None
            rows.append({"well": r.well, "depth_m": r.depth_m, "stem": r.stem, **score(r.path, ab)})
        except Exception as e:
            print("ERR", r.stem, e, flush=True)
            continue
        if i % 10 == 0:
            pd.DataFrame(rows).to_csv(f, index=False)
            print(shard, i, r.well, r.depth_m, round(rows[-1]["S"], 2), round(rows[-1]["t_s"], 1), flush=True)
    pd.DataFrame(rows).to_csv(f, index=False)
    print("shard done", shard, len(rows), flush=True)


if __name__ == "__main__":
    main()
