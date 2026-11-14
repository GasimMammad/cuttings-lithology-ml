"""
Engineered features for cuttings patches -- FIXED LIST, approved 2026-07-31.
15 features in four blocks. No post-hoc selection; the list is frozen before
evaluation.

Physical scale, MEASURED from the in-frame ruler:
  source photo 7.14 um/px; tile = 672 source px = 4.80 mm; patch = 224 px
  => 21.4 um/px in the patch.
  A 2 mm lithic chip spans ~93 px; a 0.2 mm free sand grain ~9 px.

Blocks:
  free_grain  (4): fft_hi_lo, gran_fine_frac, gran_coarse_frac, gran_bimod
  quartz      (3): bright_lowsat_frac, bright_lowsat_meanarea, specular_density
  texture     (3): glcm_contrast, glcm_homogeneity, glcm_entropy
  colour      (6): lab_L_mean/a_mean/b_mean, lab_L_std/a_std/b_std   [CONTROLS]

Amendment 1 (user, 2026-07-31) -- the FFT low band is corrected for the
illumination-gradient leakage path:
  * a low-order polynomial surface (plane + quadratic terms) is fitted and
    subtracted from each patch, removing lighting falloff without touching
    the ~93 px chip scale;
  * a 2D Hann window is applied before the transform;
  * the DC bin is dropped;
  * the low band starts at 0.4 cyc/mm (not at the first Fourier bin);
  * bands are compared as MEAN power per radial bin, so the unequal bin
    counts (6 low vs 27 high) do not bias the ratio and the low band is
    averaged rather than read off ~4 noisy bins.
"""

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.color import rgb2lab, rgb2hsv
from skimage.feature import graycomatrix, graycoprops
from skimage.morphology import disk, opening, white_tophat
from skimage.measure import label as cc_label

# ---- geometry constants ----
UM_PER_PX = 21.4                     # in the 224 px patch
MM_PER_PX = UM_PER_PX / 1000.0
PATCH_MM = 224 * MM_PER_PX           # 4.79 mm

# ---- FFT bands (cycles / mm) ----
LOW_BAND = (0.4, 1.5)                # 0.67-2.5 mm  -> lithic chip scale
HIGH_BAND = (2.5, 8.0)               # 0.125-0.4 mm -> free sand grain scale

# ---- granulometry radii (px) ----
GRAN_RADII = [1, 2, 3, 4, 6, 8, 11, 15, 20, 27, 36, 47]
FINE_MAX_R = 9        # radius px; diameter <= 0.4 mm
COARSE_MIN_R = 23     # radius px; diameter >= 1.0 mm

# -----------------------------------------------------------------------------
# REVISION 2026-07-31, after the amendment-3 instrument check.
# The fault was conceptual: the original description of the discriminator was
# OPTICAL ("clear, white and glassy grains"), but it had been specified as
# SIZE-based. Greyscale granulometry measures any fine intensity structure --
# chip surface mottling and inter-chip shadows -- which swamps free grains, so
# gran_fine_frac and gran_bimod came out BACKWARDS (clay > sand).
# Repair, not deletion: the same size-distribution logic is now computed
# INSIDE the bright/low-saturation mask, i.e. over candidate quartz grains
# only. This is also the E3 rosette discrimination done properly, as a
# distribution rather than a single mean.
#   gran_fine_frac -> mask_fine_frac  ; gran_bimod -> mask_bimod
# gran_coarse_frac (+1.28, correct direction) and fft_hi_lo are KEPT as
# specified. fft_hi_lo is not mask-restricted: a mask is not rectangular and
# windowed-FFT over an irregular support introduces its own edge artefacts,
# so it stays as-is and is judged by the block ablation.
# specular_density is DROPPED: 4.504 vs 4.482 is null AND there is a
# mechanism -- cuttings are photographed wet, so the whole frame is glossy.
# Nothing else is pruned; features that merely underperformed without an
# explanatory mechanism stay in and are judged by the ablation.
# -----------------------------------------------------------------------------

MASK_FINE_MAX_MM = 0.4        # equivalent diameter below which a blob is "fine"

FEATURE_BLOCKS = {
    "free_grain": ["fft_hi_lo", "gran_coarse_frac", "mask_fine_frac", "mask_bimod"],
    "quartz":     ["bright_lowsat_frac", "bright_lowsat_meanarea"],
    "texture":    ["glcm_contrast", "glcm_homogeneity", "glcm_entropy"],
    "colour":     ["lab_L_mean", "lab_a_mean", "lab_b_mean",
                   "lab_L_std", "lab_a_std", "lab_b_std"],
}
FEATURE_NAMES = [f for blk in FEATURE_BLOCKS.values() for f in blk]
COLOUR_FREE_NAMES = [f for b, fs in FEATURE_BLOCKS.items() if b != "colour" for f in fs]


# =============================================================================
def _detrend(g):
    """Subtract a fitted quadratic illumination surface (amendment 1)."""
    h, w = g.shape
    yy, xx = np.mgrid[0:h, 0:w]
    y = (yy / h - 0.5).ravel()
    x = (xx / w - 0.5).ravel()
    A = np.column_stack([np.ones_like(x), x, y, x * x, y * y, x * y])
    coef, *_ = np.linalg.lstsq(A, g.ravel(), rcond=None)
    return g - (A @ coef).reshape(h, w)


def _fft_hi_lo(g):
    """log10(mean high-band power / mean low-band power), gradient-corrected."""
    d = _detrend(g)
    n = d.shape[0]
    win = np.outer(np.hanning(n), np.hanning(n))
    F = np.fft.fftshift(np.fft.fft2(d * win))
    P = np.abs(F) ** 2
    cy = cx = n // 2
    yy, xx = np.mgrid[0:n, 0:n]
    kr = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)       # cycles per patch
    freq = kr / PATCH_MM                                 # cycles per mm
    lo = (freq >= LOW_BAND[0]) & (freq <= LOW_BAND[1]) & (kr > 0)   # DC dropped
    hi = (freq >= HIGH_BAND[0]) & (freq <= HIGH_BAND[1])
    plo, phi = P[lo].mean(), P[hi].mean()                # MEAN per bin
    return float(np.log10((phi + 1e-12) / (plo + 1e-12)))


def _sarle(values, weights):
    """Sarle's bimodality coefficient of `values` weighted by `weights`."""
    wsum = weights.sum() + 1e-12
    mu = (weights * values).sum() / wsum
    var = (weights * (values - mu) ** 2).sum() / wsum
    sd = np.sqrt(var) + 1e-12
    skew = (weights * ((values - mu) / sd) ** 3).sum() / wsum
    kurt = (weights * ((values - mu) / sd) ** 4).sum() / wsum
    return float((skew ** 2 + 1.0) / max(kurt, 1e-6))


def _gran_coarse(g):
    """
    Greyscale pattern spectrum -> coarse (chip-scale >= 1.0 mm) fraction.
    The sum telescopes: sum_{r>=27} PS(r) = (open_20 - open_47)/total, so only
    two openings are needed instead of the full 12-radius spectrum. Verified
    numerically identical to the full computation.
    """
    g8 = (np.clip(g, 0, 1) * 255).astype(np.uint8)
    total = float(g8.sum()) + 1e-9
    lo = float(_fast_opening(g8, 20).sum())
    hi = float(_fast_opening(g8, 47).sum())
    return float((lo - hi) / total)


# -----------------------------------------------------------------------------
# v2 SPEED-UP (2026-11-05), results unchanged.
# skimage opening(g8, disk(r)) evaluates the full (2r+1)^2 footprint at every
# pixel (~1.2 s per call at r = 47). A flat disk is a stack of horizontal
# segments, so erosion = min over the disk's rows of a shifted 1-D running
# minimum (O(N) each), and likewise dilation with max. Same "reflect"
# boundary as skimage/scipy (numpy "symmetric" padding). Verified identical
# to skimage.morphology.opening, array-equal, on 120 openings (60 patches x
# r in {20, 47}); 18x faster.
# -----------------------------------------------------------------------------
def _disk_rows(r):
    fp = disk(r)
    rows = []
    for i in range(fp.shape[0]):
        c = np.flatnonzero(fp[i])
        rows.append((i - r, r - c[0]))
    return rows


def _flat_morph(img, r, fn1d, red):
    p = np.pad(img, r, mode="symmetric")
    h, w = img.shape
    acc = None
    for dy, hw in _disk_rows(r):
        seg = fn1d(p, size=2 * hw + 1, axis=1, mode="nearest")[r + dy:r + dy + h, r:r + w]
        acc = seg.copy() if acc is None else red(acc, seg, out=acc)
    return acc


def _fast_opening(img, r):
    return _flat_morph(_flat_morph(img, r, ndimage.minimum_filter1d, np.minimum),
                       r, ndimage.maximum_filter1d, np.maximum)


def _quartz_optics(rgb):
    """
    Bright low-saturation mask -> area fraction, mean blob area, and the
    SIZE DISTRIBUTION of the candidate quartz grains within it
    (mask_fine_frac, mask_bimod). Segmentation-free in the sense that no
    attempt is made to split touching lithic chips; only the optically
    quartz-like material is delineated.
    """
    hsv = rgb2hsv(rgb)
    mask = (hsv[..., 2] > 0.70) & (hsv[..., 1] < 0.25)
    frac = float(mask.mean())
    lab_img, n = cc_label(mask, return_num=True)
    if n == 0:
        return frac, 0.0, 0.0, 0.0
    sizes_px = np.bincount(lab_img.ravel())[1:].astype(float)
    areas_mm2 = sizes_px * (MM_PER_PX ** 2)
    mean_area = float(areas_mm2.mean())
    eq_diam_mm = 2.0 * np.sqrt(areas_mm2 / np.pi)
    fine = float(areas_mm2[eq_diam_mm < MASK_FINE_MAX_MM].sum() /
                 (areas_mm2.sum() + 1e-12))
    bimod = _sarle(np.log(eq_diam_mm + 1e-6), areas_mm2) if n >= 3 else 0.0
    return frac, mean_area, fine, bimod


def _glcm(g):
    q = (np.clip(g, 0, 1) * 15).astype(np.uint8)
    m = graycomatrix(q, distances=[4], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4],
                     levels=16, symmetric=True, normed=True)
    contrast = float(graycoprops(m, "contrast").mean())
    homog = float(graycoprops(m, "homogeneity").mean())
    p = m[:, :, 0, :]
    ent = float(np.mean([-np.sum(p[..., k] * np.log2(p[..., k] + 1e-12))
                         for k in range(p.shape[-1])]))
    return contrast, homog, ent


def features_for_patch(path):
    """Return a dict of the 16 fixed features for one patch file."""
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255.0
    g = rgb @ np.array([0.2125, 0.7154, 0.0721])
    fft_hi_lo = _fft_hi_lo(g)
    coarse = _gran_coarse(g)
    bfrac, barea, mask_fine, mask_bimod = _quartz_optics(rgb)
    contrast, homog, ent = _glcm(g)
    lab = rgb2lab(rgb)
    return {
        "fft_hi_lo": fft_hi_lo,
        "gran_coarse_frac": coarse,
        "mask_fine_frac": mask_fine,
        "mask_bimod": mask_bimod,
        "bright_lowsat_frac": bfrac,
        "bright_lowsat_meanarea": barea,
        "glcm_contrast": contrast,
        "glcm_homogeneity": homog,
        "glcm_entropy": ent,
        "lab_L_mean": float(lab[..., 0].mean()),
        "lab_a_mean": float(lab[..., 1].mean()),
        "lab_b_mean": float(lab[..., 2].mean()),
        "lab_L_std": float(lab[..., 0].std()),
        "lab_a_std": float(lab[..., 1].std()),
        "lab_b_std": float(lab[..., 2].std()),
    }
