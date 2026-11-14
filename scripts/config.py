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
SSD_ROOT = Path("/Volumes/T9/GasimMammadov_MasterProject2026")

# Folder on the SSD that contains the cuttings photographs.
# NPD/Diskos layout: photos live in Wells/<well>/DRILLING/, so we point at
# the whole Wells tree and let the scripts filter.
CUTTINGS_DIR = SSD_ROOT / "Wells"

# -----------------------------------------------------------------------------
# 2026-11-05: all wells are back in one place, the T9 drive
# (SSD_ROOT/Wells/<well>/). READ-ONLY. Scripts still resolve a well through
# well_dir(), so a second root can be added here if data moves again.
# -----------------------------------------------------------------------------
WELL_ROOTS = [
    SSD_ROOT / "Wells",
]

ALL_WELLS = ["24_9-3", "24_9-4", "34_4-6", "34_4-7", "34_7-1", "34_7-6",
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
WORK_DIR = Path.home() / "sinkite_ml_work_v2"

# Where the cropped image patches get written. On the INTERNAL drive: it is
# faster than the external SSD, and the SSD is treated as read-only.
PATCH_DIR = Path.home() / "sinkite_ml_data_v2" / "patches"


# =============================================================================
# 2. WELLS
# =============================================================================

# The wells you currently have cuttings for. Use whatever naming appears in
# your folder structure; script 01 will tell you what that is.
WELLS = ["24_9-3", "24_9-4", "34_4-6", "34_4-7", "34_7-1",
         "34_7-4", "34_7-9", "34_7-10", "34_7-6", "34_8-3", "34_8-3_A"]

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

# =============================================================================
# v2 LABEL DESIGN (2026-11-05) -- eleven wells, one rule for all of them
# =============================================================================
# RULE 1  ONE ZONE = ONE OPEN-HOLE LOGGING RUN. A zone and BOTH its anchors
#         must lie inside the same wireline run, below the casing shoe the run
#         was logged under. Casing depths: Sodir FactPages casing table
#         (wellbore_casing_and_lot, downloaded 2026-11-05). Run ranges: the
#         individual run LAS files (<tool>-1, -2, ...) beside each composite.
#         Why: calibration differs run to run (34/7-4 run 1 reads ~71 API in
#         Nordland clay, run 2 ~33 API in Hordaland clay), and GR logged
#         through casing is attenuated and looks like sand (the step at the
#         20" shoe is visible in 34/7-9 899 m, 34/7-10 901 m, 34/4-7 902 m,
#         34/7-6 935 m; at the 13 3/8" shoe in 34/8-3 1302 m and 34/8-3 A
#         944 m; at the 30" shoe in 34/7-1 476 m).
# RULE 2  EXCLUDE KNOWN GR PITFALLS from every zone:
#           Balder Fm  -- tuff beds read LOW GR but are tuffaceous shale
#           Ness Fm    -- coals read LOW GR
#           Rannoch Fm -- micaceous sandstone reads HIGH GR
#           Draupne Fm -- hot shale (U-rich), off-scale
# RULE 3  SAND ANCHOR = interior of the cleanest blocky sand in that run,
#         taken from a named unit (NPD tops, operator picks, or the unnamed
#         Hordaland Gp sandstone units that NPD lists as "NO FORMAL NAME").
#         SHALE ANCHOR = thick homogeneous marine claystone in the same run
#         (Hordaland Gp or Lista Fm; Drake/Heather Fm in the Jurassic).
# A well with no clean sand inside an open-hole run gets NO labels (34/7-1),
# rather than a cross-run or through-casing anchor.
# Literature basis (summary, full list in V2_LABEL_DECISIONS.md):
#   Utsira poorly developed / thin and glauconitic in Snorre-Visund-Tampen
#   (Eidvin & Rundberg 2001; Gregersen & Johannessen 2007); unnamed Eocene and
#   Oligocene Hordaland sands on the Tampen Spur (Rundberg & Eidvin 2005);
#   Pleistocene sand intrusion/extrusion around the top-Hordaland
#   unconformity in blocks 34/4 and 34/7 (Loseth et al. 2013; Rundberg &
#   Eidvin 2016).
#
# GR source per well (path relative to SSD_ROOT/Wells), second item unused.
GR_SOURCES = {
    "24_9-3": ("24_9-3/LOGS/24_9-3_ISF_LSS_GR__COMPOSITED.LAS", None),
    "24_9-4": ("24_9-4/LOGS/24_9-4_LDT_CNT_SGT_AMS__COMPOSIT.LAS", None),
    "34_4-6": ("34_4-6/LOGS/34_4-6_ISF_LSS_GR__COMPOSITED.LAS", None),
    "34_4-7": ("34_4-7/LOGS/34_4-7_DIFL_AC_GR__COMPOSITED.LAS", None),
    "34_7-4": ("34_7-4/LOGS/34_7-4_DIFL_AC_GR__COMPOSITED.LAS", None),
    "34_7-9": ("34_7-9/LOGS/34_7-9_DIFL_AC_GR__COMPOSITED.LAS", None),
    "34_7-10": ("34_7-10/LOGS/34_7-10_DIFL_AC_GR__COMPOSITED.LAS", None),
    "34_7-6": ("34_7-6/34_7-6_DIFL_AC_GR__COMPOSITED.LAS", None),
    "34_8-3": ("34_8-3/LOGS/34_8-3_DIS_LSS_GR__COMPOSITED.LAS", None),
    "34_8-3_A": ("34_8-3_A/LOGS/34_8-3_A_DIL_LSS_GR__COMPOSITED.LAS", None),
    # 34_7-1: no GR source on purpose -- no clean sand in any open-hole run
    # (v1 sand anchor 360-460 m sat inside the 30" conductor, shoe 476 m).
}

def _z(rng, name, sand, shale):
    return {"range": rng, "name": name, "sand": sand, "shale": shale}

LABEL_ZONES = {
    # 24/9-3. 30" 208 m, 20" 503 m, 13 3/8" 1587 m, 9 5/8" 3051 m.
    # Runs ISF_LSS-1 134-517, -2 465-1589, -3 1558-2044, -4 1917-3051.
    "24_9-3": [
        _z((212, 460), "r1_nordland",                      # 26" open hole
           (405, 435, "Utsira Fm sand interior"),
           (240, 265, "Nordland Gp claystone")),
        _z((520, 1555), "r2_hordaland",
           (1205, 1250, "Grid Fm sand interior"),
           (900, 1030, "Hordaland Gp claystone")),
        _z((1595, 1912), "r3_upper",                       # Balder 1918-1981 out
           (1988, 2012, "Hermod Fm sand interior"),
           (1840, 1910, "Hordaland Gp claystone (unnamed unit 1831-1918)")),
        _z((1985, 2014), "r3_hermod",                      # through-casing 2016-2036 out
           (1988, 2012, "Hermod Fm sand interior"),
           (1840, 1910, "Hordaland Gp claystone (unnamed unit 1831-1918)")),
        _z((2040, 2830), "r4_rogaland",                    # to top Jorsalfare 2836
           (2220, 2300, "Heimdal Fm sand interior"),
           (2065, 2200, "Sele Fm claystone")),
    ],
    # 24/9-4. 20" 750 m, 13 3/8" 1179 m, 9 5/8" 1585 m. Wireline only.
    # Runs SGT_AMS-1 579-1173, -2 1123-1628, -3 1563-1858 (no clean sand in
    # run 3 -> unlabelled).
    "24_9-4": [
        _z((760, 1168), "r1_hordaland",
           (1100, 1155, "Grid Fm sand interior (upper Grid)"),
           (950, 1060, "Hordaland Gp claystone")),
        _z((1185, 1580), "r2_hordaland",
           (1210, 1236, "Grid Fm sand interior"),
           (1250, 1320, "Hordaland Gp claystone")),
    ],
    # 34/4-6. 20" 904 m (run change visible), 13 3/8" 1841 m.
    # Lunde zones of v1 dropped: no sand AND shale anchor inside one run.
    "34_4-6": [
        _z((915, 1653), "r2_hordaland",
           (1361, 1375, "Hordaland Gp unnamed sand (NPD 1359-1387)"),
           (1695, 1765, "Lista Fm claystone")),
        _z((1692, 1770), "r2_lista",                        # Balder 1658-1688 out
           (1361, 1375, "Hordaland Gp unnamed sand (NPD 1359-1387)"),
           (1695, 1765, "Lista Fm claystone")),
    ],
    # 34/4-7. 20" 902 m, 13 3/8" 1872 m. DIFL-1 888-1889 (v1 exclusion for
    # run-splice jumps is resolved by staying inside run 1).
    "34_4-7": [
        _z((915, 1695), "r1_hordaland",                     # Balder 1700-1733 out
           (1078, 1098, "sand above NPD Utsira top (Utsira/Pleistocene sand)"),
           (1740, 1820, "Lista Fm claystone")),
        _z((1736, 1820), "r1_lista",
           (1078, 1098, "sand above NPD Utsira top (Utsira/Pleistocene sand)"),
           (1740, 1820, "Lista Fm claystone")),
    ],
    # 34/7-4. 20" 953 m, 13 3/8" 1915 m. DIFL-1 326-972 | -2 902-1935.
    "34_7-4": [
        _z((978, 1680), "r2_hordaland",                     # Balder 1685-1712 out
           (1622, 1662, "Hordaland Gp unnamed Eocene sand (NPD 1625-1675)"),
           (1240, 1350, "Hordaland Gp claystone")),
        _z((1716, 1825), "r2_lista",
           (1622, 1662, "Hordaland Gp unnamed Eocene sand (NPD 1625-1675)"),
           (1240, 1350, "Hordaland Gp claystone")),
    ],
    # 34/7-9. 20" 899 m, 13 3/8" 1821 m. DIFL-1 345-1840 (through 20" above 899).
    "34_7-9": [
        _z((915, 1652), "r1_hordaland",                     # Balder 1657-1681 out
           (1452, 1505, "Hordaland Gp unnamed Eocene sand (NPD 1445-1511)"),
           (1690, 1780, "Lista Fm claystone")),
        _z((1685, 1780), "r1_lista",
           (1452, 1505, "Hordaland Gp unnamed Eocene sand (NPD 1445-1511)"),
           (1690, 1780, "Lista Fm claystone")),
    ],
    # 34/7-10. 20" 901 m, 13 3/8" 1907 m. DIFL-1 297-1913.
    "34_7-10": [
        _z((915, 1677), "r1_hordaland",                     # Balder 1682-1728 out
           (995, 1035, "Utsira Fm sand (operator pick 993-1045 m)"),
           (1400, 1470, "Hordaland Gp claystone")),
        _z((1730, 1845), "r1_sele_lista",
           (995, 1035, "Utsira Fm sand (operator pick 993-1045 m)"),
           (1400, 1470, "Hordaland Gp claystone")),
    ],
    # 34/7-6. 20" 935 m, 13 3/8" 1876 m. Composite only (single DIFL run
    # assumed below the 20" shoe; no splice step seen 950-1840 m).
    "34_7-6": [
        _z((950, 1670), "hordaland",                        # Balder 1676-1705 out
           (1222, 1275, "Hordaland Gp Oligocene sand"),
           (1770, 1840, "Lista Fm claystone")),
        _z((1710, 1840), "sele_lista",
           (1222, 1275, "Hordaland Gp Oligocene sand"),
           (1770, 1840, "Lista Fm claystone")),
    ],
    # 34/8-3. 13 3/8" 1302 m, 9 5/8" 2598 m. Tertiary open hole (1305-1820)
    # has no clean sand (the "sand" at 1092-1300 m is GR through 13 3/8"
    # casing) -> Jurassic only, run DIS_LSS-2 2547-3334.
    "34_8-3": [
        _z((2867, 2897), "etive",
           (2868, 2879, "Etive Fm sand interior"),
           (2968, 3002, "Drake Fm claystone")),
        _z((2965, 3278), "dunlin",
           (2868, 2879, "Etive Fm sand interior"),
           (2968, 3002, "Drake Fm claystone")),
        _z((3278, 3310), "statfjord",
           (2868, 2879, "Etive Fm sand interior"),
           (2968, 3002, "Drake Fm claystone")),
    ],
    # 34/8-3 A. 13 3/8" 944 m, 9 5/8" 2442 m. No Tertiary sand below 944 m
    # (Utsira 1120-1180 reads 70-80 API: poorly developed at Visund).
    # Jurassic only, run DIL_LSS-2 2400-3239.
    "34_8-3_A": [
        _z((3012, 3071), "heather_tarbert",
           (3098, 3112, "Etive Fm sand interior"),
           (3186, 3225, "Drake Fm claystone")),
        _z((3101, 3131), "etive",
           (3098, 3112, "Etive Fm sand interior"),
           (3186, 3225, "Drake Fm claystone")),
        _z((3184, 3227), "drake",
           (3098, 3112, "Etive Fm sand interior"),
           (3186, 3225, "Drake Fm claystone")),
    ],
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
