"""
Central configuration. EDIT THE PATHS AT THE TOP, then leave the rest alone
until a script tells you to come back and tune something.

Every other script imports from here, so paths live in exactly one place.
"""

from pathlib import Path

# =============================================================================
# 1. PATHS -- YOU MUST EDIT THESE
# =============================================================================

# Your external SSD. Find the exact name by running in Terminal:  ls /Volumes
# If the name has spaces it is still fine here, Python handles it.
SSD_ROOT = Path("/Volumes/PortableSSD")

# Folder on the SSD that contains the cuttings photographs.
# NPD/Diskos layout: photos live in Wells/<well>/DRILLING/, so we point at
# the whole Wells tree and let the scripts filter.
CUTTINGS_DIR = SSD_ROOT / "Wells"

# -----------------------------------------------------------------------------
# 2026-08-02: the cuttings data now lives in TWO places. The five original
# wells were MOVED off the SSD to free space and sit at the home-directory
# root; the five new wells are on the SSD. Both locations are READ-ONLY.
# Scripts must resolve a well through well_dir() rather than assuming one root.
# -----------------------------------------------------------------------------
WELL_ROOTS = [
    Path.home(),                 # relocated originals: ~/<well>/DRILLING/
    SSD_ROOT / "Wells",          # new wells: /Volumes/PortableSSD/Wells/<well>/
]

ALL_WELLS = ["24_9-3", "24_9-4", "34_4-6", "34_4-7", "34_7-1",
             "34_7-4", "34_7-9", "34_7-10", "34_8-3", "34_8-3_A"]


def well_dir(well: str) -> Path:
    """Return the directory of `well`, searching WELL_ROOTS in order."""
    for root in WELL_ROOTS:
        p = root / well
        if (p / "DRILLING").is_dir():
            return p
    raise FileNotFoundError(
        f"well {well!r} not found under any of: "
        + ", ".join(str(r) for r in WELL_ROOTS))


def drilling_dir(well: str) -> Path:
    return well_dir(well) / "DRILLING"

# Folder containing your LAS well log files (Wells/<well>/LOGS/*.LAS).
LAS_DIR = SSD_ROOT / "Wells"

# Folder names to skip entirely when scanning the SSD (old experiments,
# recycle bin, etc.). Matched against any folder name in the path.
SCAN_EXCLUDE_DIRS = {"cuttings-ml", ".venv", "$RECYCLE.BIN",
                     "System Volume Information", ".Spotlight-V100", ".Trashes"}

# Where all outputs go. This lives on the Mac, NOT the SSD, so that results
# survive unplugging the drive. It is small (tables, models, figures).
WORK_DIR = Path.home() / "sinkite_ml_work"

# Where the cropped image patches get written. On the INTERNAL drive: it is
# faster than the external SSD, and the SSD is treated as read-only.
PATCH_DIR = Path.home() / "sinkite_ml_data" / "patches"


# =============================================================================
# 2. WELLS
# =============================================================================

# The wells you currently have cuttings for. Use whatever naming appears in
# your folder structure; script 01 will tell you what that is.
WELLS = ["24_9-3", "24_9-4", "34_4-6", "34_4-7", "34_7-1"]

# Map from however the well appears in the cuttings folder tree to a clean
# name. Fill this in after running script 01. Left empty means "use as is".
WELL_NAME_MAP = {
    # "NO_24_9-3_cuttings": "24_9-3",
}


# =============================================================================
# 3. IMAGE HANDLING
# =============================================================================

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}

# Each source photograph is cut into a GRID x GRID array of patches.
# 3 means 9 patches per photo. This multiplies your training data and makes
# each sample a close-up of the grains rather than a whole tray.
PATCH_GRID = 3

# Final size fed to the network. 224 is what ImageNet models expect.
PATCH_SIZE = 224

# Skip source images smaller than this (thumbnails, icons, corrupt files).
MIN_IMAGE_PIXELS = 400 * 400


# =============================================================================
# 4. LABEL GENERATION FROM GAMMA RAY  (reworked 2026-07-31)
# =============================================================================
# Absolute GR (API) is not comparable between these wells (different tool
# vintages/contractors), so labels use shale volume instead:
#     Vsh = (GR - GR_clean) / (GR_shale - GR_clean), clipped to [0, 1]
# GR_clean / GR_shale are the median GR of NAMED known-lithology intervals
# per well (anchored endmembers, chosen geologically -- NOT blind
# percentiles). A single Vsh threshold then applies across all wells.

VSH_SAND_MAX = 0.30   # Vsh below this  -> "sand"
VSH_CLAY_MIN = 0.60   # Vsh above this  -> "clay"
                      # in between      -> "mixed" (excluded from training)

# The GR source per well, selected 2026-07-31 by maximum coverage of
# cuttings depths. Path is relative to SSD_ROOT/Wells.
# Optional (min_m, max_m) restricts the usable depth range: 24_9-4 is
# wireline-only by decision -- its MWD section stays unlabelled.
GR_SOURCES = {
    "24_9-3": ("24_9-3/LOGS/24_9-3_ISF_LSS_GR__COMPOSITED.LAS", None),
    "24_9-4": ("24_9-4/LOGS/24_9-4_LDT_CNT_SGT_AMS__COMPOSIT.LAS", None),
    "34_4-6": ("34_4-6/LOGS/34_4-6_ISF_LSS_GR__COMPOSITED.LAS", None),
    "34_4-7": ("34_4-7/LOGS/34_4-7_MWD_RES_GR__COMPOSITED.LAS", None),
    "34_7-1": ("34_7-1/LOGS/34_7-1_ISF_BHC_MSFL_GR__COMPOSIT.LAS", None),
}

# Label zones (2026-07-31, pending review).
# One GR calibration does NOT hold along a whole well here: composited logs
# splice runs with different calibrations, Triassic Lunde red beds are a
# different GR regime from the Tertiary, and the Cretaceous Shetland Gp is
# carbonate-prone (low GR = marl/limestone, NOT sand). So labels are only
# generated inside explicit zones, each with its own anchored endmembers:
#   {"range": (min_m, max_m), "sand": (top, base, name), "shale": (...)}.
# Photos inside the logged interval but outside every zone -> "excluded_zone".
# 34_4-7 has NO zones: both its GR sources (MWD and DIFL wireline) are
# internally inconsistent (run-splice calibration jumps); excluded until its QC figure
# is reviewed.
LABEL_ZONES = {
    # 24_9-3: zone ends at top Jorsalfare (Shetland Gp, carbonate-prone).
    # Split at 2016-2036 m: the composite used THROUGH-CASING GR there
    # (24_9-3_2633.REP), attenuated -> no labels from that stretch.
    "24_9-3": [
        {"range": (0, 2016), "name": "paleogene_a",
         "sand": (1210, 1255, "Grid Fm sand interior"),
         "shale": (2065, 2210, "Sele Fm claystone")},
        {"range": (2036, 2836), "name": "paleogene_b",
         "sand": (1210, 1255, "Grid Fm sand interior"),
         "shale": (2065, 2210, "Sele Fm claystone")},
    ],
    "24_9-4": [
        {"range": (0, 1858), "name": "paleogene",  # wireline segment only
         "sand": (1216, 1240, "Grid Fm sand interior"),
         "shale": (1660, 1850, "Hordaland claystone")},
    ],
    "34_4-6": [
        {"range": (0, 1775), "name": "tertiary",   # down to top Jorsalfare
         "sand": (1361, 1375, "Hordaland sand body"),
         "shale": (1695, 1765, "Lista Fm claystone")},
        # Lunde zone split at 2755-2761 m: through-casing GR near the
        # 9 5/8" shoe (34_4-6_7560.REP) -> no labels from that stretch.
        {"range": (2577, 2755), "name": "lunde_a", # Triassic Lunde Fm
         "sand": (2679, 2693, "Lunde sand body A"),
         "shale": (2900, 3100, "Lunde lower mudstone")},
        {"range": (2761, 3153), "name": "lunde_b", # Lunde continued (to top Lomvi)
         "sand": (2679, 2693, "Lunde sand body A"),
         "shale": (2900, 3100, "Lunde lower mudstone")},
    ],
    "34_7-1": [
        {"range": (0, 1823), "name": "tertiary",   # down to top Jorsalfare
         "sand": (360, 460, "Nordland sand interior"),
         "shale": (1200, 1600, "Hordaland claystone")},
    ],
    # "34_4-7": no zones -- excluded pending review of the QC figure
}

# Cuttings depth is a lag-corrected estimate, not a measurement. A label is
# kept only if EVERY Vsh sample within this window falls in the same class
# as the centre value (all sand or all clay), so metres of depth error
# cannot flip the label. (Class-consistency filter; replaces the old
# GR-spread tolerance.)
GR_STABILITY_WINDOW_M = 3.0   # look this far above and below.
                              # = the operator's 3 m sampling interval; the
                              # tightest window that still uses >1 log sample.
                              # Chosen 2026-07-31 from the 2x2 window/threshold
                              # table: best cross-well sand concentration
                              # (76% in 24_9-3 vs 86% at +/-5 m) at no cost in
                              # label purity.

# Common curve names for gamma ray in Norwegian LAS files, tried in order.
GR_ALIASES = ["GR", "GRC", "GR_1", "SGR", "CGR", "GRD", "GAMMA"]


# =============================================================================
# 5. TRAINING
# =============================================================================

CLASSES = ["sand", "clay"]      # binary to start. Add "mixed" later if useful.

BATCH_SIZE = 32
NUM_WORKERS = 4                 # set to 0 if you get crashes on macOS
EPOCHS_HEAD = 4                 # stage 1: train only the new final layer
EPOCHS_FINETUNE = 6             # stage 2: also unfreeze the last conv block
LR_HEAD = 1e-3
LR_FINETUNE = 1e-4
SEED = 42

# Depth bin size (metres) for the final sand-fraction curve.
OUTPUT_BIN_M = 5.0


# =============================================================================
# 6. DERIVED PATHS -- do not edit
# =============================================================================

INVENTORY_CSV = WORK_DIR / "01_inventory.csv"
INDEX_CSV = WORK_DIR / "02_index.csv"
LABELS_CSV = WORK_DIR / "03_labelled.csv"
PATCHES_CSV = WORK_DIR / "04_patches.csv"
MODEL_DIR = WORK_DIR / "models"
FIG_DIR = WORK_DIR / "figures"
PRED_DIR = WORK_DIR / "predictions"

for _d in (WORK_DIR, MODEL_DIR, FIG_DIR, PRED_DIR):
    _d.mkdir(parents=True, exist_ok=True)
