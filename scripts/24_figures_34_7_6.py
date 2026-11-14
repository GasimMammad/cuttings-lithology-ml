"""
Figures and deliverable CSV for the 34/7-6 case.

  stage3lite_34_7_6.png/.pdf   two panels, the LOAD-BEARING evidence for the well
  provenance_34_7_6.png/.pdf   green index vs depth, windows, background, 10x line
  25_eleven_well_compare.*     eleven-well comparison, 34/7-6 flagged as lacking
                               an Utsira control
  green_index_34_7_6.csv       one row per target-window photograph

Thresholds FROZEN (a* < -5.0, C* >= 12.0, 15 < L* < 80). Nothing here recalibrates.
All figures 170 mm wide, vector PDF beside every PNG, no em dashes in captions.
"""
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import config as C

MM = 1 / 25.4
W170 = 170 * MM                       # 170 mm, the agreed figure width
plt.rcParams.update({"font.size": 7.5, "axes.labelsize": 7.5,
                     "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
                     "axes.titlesize": 8, "legend.fontsize": 6.5,
                     "pdf.fonttype": 42, "ps.fonttype": 42})

# palette carried over from 18_partD_figures.py so the chapter matches
GREEN_L, GREEN_F = "#2d6a3e", "#4a9c68"
C_UTS, C_OLIG, C_THGU, C_BLUE, C_RED = "#55A868", "#DD8452", "#C44E52", "#4C72B0", "#C44E52"

WELL = "34_7-6"
THGU_76 = 1036.5
SANDTOP = 1218.0
BG = None                              # filled from the control file

WINDOWS = [("Utsira",      1030.0, 1036.5, C_UTS),
           ("near-THGU",   1036.5, 1066.5, C_THGU),
           ("ooze",        1066.5, 1218.0, C_BLUE),
           ("target",      1218.0, 1283.0, C_OLIG),
           ("extended",    1283.0, 1310.0, C_OLIG)]

# 34/4-6 calibrated impedance populations (frozen, from the calibration well)
CAL_446 = {"ooze": 3540, "Oligocene sand": 4314, "Utsira sand": 5312}


# ----------------------------------------------------------------- LAS reader
def read_las(path):
    lines = Path(path).read_text(errors="ignore").splitlines()
    mnem, null, i_a = [], -999.25, None
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.upper().startswith("~A"):
            i_a = i
            break
        if s.upper().startswith("NULL"):
            m = re.search(r"[-\d.]+", s.split(".", 1)[1])
            if m:
                null = float(m.group())
    in_curve = False
    for ln in lines[:i_a]:
        s = ln.strip()
        if s.upper().startswith("~C"):
            in_curve = True
            continue
        if s.startswith("~"):
            in_curve = False
        if in_curve and s and not s.startswith("#"):
            mnem.append(s.split(".")[0].strip())
    rows = []
    for ln in lines[i_a + 1:]:
        p = ln.split()
        if len(p) == len(mnem):
            rows.append([float(x) for x in p])
    df = pd.DataFrame(rows, columns=mnem).replace(null, np.nan)
    return df.rename(columns={mnem[0]: "DEPT"})


def load_logs():
    root = C.SSD_ROOT / "Wells" / "34_7-6"
    a = read_las(root / "34_7-6_DIFL_AC_GR__COMPOSITED.LAS")[["DEPT", "GR", "AC", "CAL"]]
    b = read_las(root / "34_7-6_CDL_CNL_SL__COMPOSITED.LAS")[["DEPT", "DEN"]]
    a["DEPT"] = a.DEPT.round(3)
    b["DEPT"] = b.DEPT.round(3)
    d = a.merge(b, on="DEPT", how="outer").sort_values("DEPT").reset_index(drop=True)
    d.loc[(d.AC < 40) | (d.AC > 200), "AC"] = np.nan      # pre-registered clips
    d.loc[(d.DEN < 1.5) | (d.DEN > 3.0), "DEN"] = np.nan
    lo, hi = np.nanpercentile(d.GR, 5), np.nanpercentile(d.GR, 95)
    d["VSH"] = ((d.GR - lo) / (hi - lo)).clip(0, 1)
    d["VP"] = 304800.0 / d.AC                              # us/ft -> m/s
    d["AI"] = d.DEN * d.VP
    return d


def load_ba():
    x = read_las(C.SSD_ROOT / "Wells" / "34_7-6" / "DRILLING"
                 / "34_7-6_CUTTINGS_XRF_1.LAS")
    col = next(c for c in x.columns if c.lower() == "ba")
    return x[["DEPT", col]].rename(columns={col: "ba_ppm"}).dropna()


# ----------------------------------------------------------------- index data
def index_34_7_6():
    """Frozen index for 34/7-6. Diagnostic file already covers 1000-1895 m and
    was verified identical to the independent target run (max diff 0.00e+00)."""
    d = pd.read_csv(C.WORK_DIR / "21_diagnostic_34_7_6.csv")[["depth_m", "index_cropnorm"]]
    return d.rename(columns={"index_cropnorm": "green_index"}).sort_values("depth_m")


def window_of(z):
    for name, lo, hi, _ in WINDOWS:
        if lo <= z < hi or (name == "extended" and z == hi):
            return name
    if z > 1450:
        return "deep control"
    return "Oligocene below sand" if z >= 1310 else "above Utsira"


# ----------------------------------------------------------------- CSV
def make_csv(idx, ba):
    t = idx[(idx.depth_m >= 1218) & (idx.depth_m <= 1310)].copy()
    t["index"] = t.green_index
    t["index_over_background"] = t.green_index / BG
    # 'extension_only' marks the three photographs BELOW the primary window.
    # The extended window in the text is n=10 and CONTAINS the primary seven,
    # which is what in_extended records, so the CSV cannot be misread alone.
    t["window"] = ["primary" if z <= 1283 else "extension_only" for z in t.depth_m]
    t["in_primary"] = t.depth_m <= 1283
    t["in_extended"] = True
    t["depth_below_thgu_m"] = t.depth_m - THGU_76
    t["depth_below_sandtop_m"] = t.depth_m - SANDTOP
    t["ba_ppm"] = [float(ba.loc[(ba.DEPT - z).abs().idxmin(), "ba_ppm"])
                   if len(ba) else np.nan for z in t.depth_m]
    t["fires_10x"] = t.green_index > 10 * BG
    out = t[["depth_m", "index", "index_over_background", "window",
             "in_primary", "in_extended", "depth_below_thgu_m",
             "depth_below_sandtop_m", "ba_ppm", "fires_10x"]]
    p = C.WORK_DIR / "green_index_34_7_6.csv"
    out.to_csv(p, index=False, float_format="%.6f")
    print("CSV:", p)
    print(out.to_string(index=False))
    return out


# ----------------------------------------------------------------- figure 1
def fig_stage3lite(logs):
    fig = plt.figure(figsize=(W170, 6.45))
    gsA = fig.add_gridspec(1, 3, left=.07, right=.60, top=.895, bottom=.395,
                           wspace=.10)
    axg = fig.add_subplot(gsA[0, 0])
    axa = fig.add_subplot(gsA[0, 1], sharey=axg)
    axb = fig.add_subplot(gsA[0, 2], sharey=axg)
    axP = fig.add_axes([.70, .395, .27, .50])

    m = (logs.DEPT >= 1000) & (logs.DEPT <= 1450)
    d = logs[m]
    for ax, col, lab, xlim, colr in [
            (axg, "GR", "GR (gAPI)", (0, 120), "#444444"),
            (axa, "VSH", "Vsh (GR)", (0, 1), "#7A5195"),
            (axb, "AI", "AI (g/cc x m/s)", (2500, 6500), C_BLUE)]:
        ax.plot(d[col], d.DEPT, lw=.55, color=colr)
        ax.set_xlim(*xlim)
        ax.set_xlabel(lab)
        ax.grid(alpha=.25, lw=.4)
        for name, lo, hi, cc in WINDOWS:
            ax.axhspan(lo, hi, color=cc, alpha=.30 if name != "ooze" else .16, zorder=0)
        ax.axhline(THGU_76, color=C_THGU, lw=1.0)
    axb.axvline(CAL_446["Oligocene sand"], color=C_OLIG, ls="--", lw=.9)
    axb.axvline(CAL_446["Utsira sand"], color=C_UTS, ls="--", lw=.9)
    axg.set_ylim(1450, 1000)
    axg.set_ylabel("Depth (m RKB)")
    for ax in (axa, axb):
        plt.setp(ax.get_yticklabels(), visible=False)

    # the point of the panel: Vsh and AI disagree in the Utsira
    axa.annotate("Utsira\nVsh 0.75", xy=(0.75, 1033.2), xytext=(0.24, 1108),
                 fontsize=6.5, color=C_UTS, fontweight="bold", linespacing=1.3,
                 arrowprops=dict(arrowstyle="->", color=C_UTS, lw=.8))
    axb.annotate("Utsira AI 5162,\nsand range", xy=(5162, 1033.2),
                 xytext=(2680, 1108), fontsize=6.5, color=C_UTS, fontweight="bold",
                 linespacing=1.3,
                 arrowprops=dict(arrowstyle="->", color=C_UTS, lw=.8))
    axa.annotate("target Vsh 0.03", xy=(0.03, 1250), xytext=(0.32, 1330),
                 fontsize=6.5, color=C_OLIG, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color=C_OLIG, lw=.8))
    axg.set_title("A.  Logs, 34/7-6", fontsize=8, fontweight="bold", loc="left")

    # ---- panel B: the three populations against the 34/4-6 calibration
    # All 34/7-6 values recomputed under the single documented convention in
    # load_logs(), so the note, the table and this panel agree to the digit.
    obs = [("ooze\n1066.5-1218", 3564, 151.5, "ooze", C_BLUE),
           ("target\n1218-1283", 4449, 65.0, "Oligocene sand", C_OLIG),
           ("Utsira\n1030-1036.5", 5162, 6.5, "Utsira sand", C_UTS)]
    for i, (lab, ai, thick, calkey, cc) in enumerate(obs):
        cal = CAL_446[calkey]
        axP.hlines(cal, i - .26, i + .26, color="#888888", lw=1.6, ls="--", zorder=2)
        sz = 26 + 62 * (thick / 151.5)
        axP.scatter([i], [ai], s=sz, color=cc, edgecolor="black", lw=.6, zorder=3)
        axP.annotate(f"{ai:.0f}", (i, ai), textcoords="offset points",
                     xytext=(-30, -2.5), fontsize=6.5, fontweight="bold", color=cc)
        axP.annotate(f"{cal:.0f} ({abs(ai-cal)/cal*100:.1f}%)", (i + .26, cal),
                     textcoords="offset points", xytext=(2, -2.5), fontsize=6.2,
                     color="#777777")
    axP.text(2, 4790, "thin window,\nshoulder affected", ha="center", fontsize=5.8,
             color=C_RED, fontweight="bold")
    axP.set_xticks(range(3))
    axP.set_xticklabels([f"{o[0].split(chr(10))[0]}\n{o[2]:.1f} m" for o in obs],
                        fontsize=6.5)
    axP.set_xlim(-1.3, 3.4)
    axP.set_ylim(3300, 5850)
    axP.set_ylabel("AI_PIMP (g/cc x m/s)")
    axP.grid(axis="y", alpha=.25, lw=.4)
    axP.set_title("B.  AI against 34/4-6 calibration", fontsize=8,
                  fontweight="bold", loc="left")
    axP.legend(handles=[Line2D([], [], color="#888888", ls="--", lw=1.6,
                               label="34/4-6 calibration"),
                        Line2D([], [], marker="o", ls="", color="#555555",
                               label="34/7-6 measured")],
               loc="upper left", frameon=False, handlelength=1.6)

    fig.suptitle("Well 34/7-6: gamma ray, shale volume and acoustic impedance "
                 "against depth,\nwith the four analysis windows.",
                 fontsize=8.5, fontweight="bold", y=.985, linespacing=1.4)
    fig.text(.02, .022, "\n".join([
        "These are log measurements, independent of the cuttings photographs, the sample tray, the lighting and "
        "the colour thresholds, all of",
        "which are implicated in the control failure reported in the companion figure.",
        "Panel A: shaded bands are the analysis windows, red line the Top Hordaland Group Unconformity at "
        "1036.5 m. Dashed vertical lines in",
        "the AI track are the 34/4-6 calibrated Oligocene sand (4314) and Utsira sand (5312) values. The core "
        "observation is stated in raw curve values: the",
        "Utsira reads 40.44 gAPI and the ooze 36.01 gAPI, which are near identical, while their impedances are "
        "5162 and 3564, a difference of 45 per cent.",
        "Gamma ray tracking clay content cannot produce that, so something other than clay is generating the "
        "Utsira gamma ray while the rock behaves",
        "acoustically like a sand. The target reads 17.62 gAPI and 4449, placing it in the clean-sand "
        "population. Shale volume is shown for illustration only",
        "and is NOT the basis of the argument: it is normalised to per-well endmembers taken over 1000 to "
        "1450 m, and over the whole logged well the",
        "same intervals read 0.42 and 0.01, so the strength of any Vsh-based inference would change with that "
        "choice.",
        "Panel B: 34/7-6 values use the single convention documented in the script. The 34/4-6 calibration "
        "windows differ from one another and are stated",
        "here for the record: Utsira sand 5312 is the whole 1210-1250 m interval, Oligocene sand 4314 is the "
        "picked sand body 1359.8-1376.5 m, and ooze",
        "3540 is 1250-1390 m. Those values reconstruct from the logs to within 1.6 per cent, so the agreement "
        "shown here is at the few-per-cent level and the",
        "comparison does not resolve finer than that. The Utsira window spans only 6.5 m and its median is "
        "shoulder affected; the same contrast is shown",
        "independently over a 40 m interval in the calibration well, where the Utsira is known to be "
        "glauconitic."]),
        fontsize=5.9, va="bottom", linespacing=1.5)
    save(fig, "stage3lite_34_7_6")


# ----------------------------------------------------------------- figure 2
def fig_provenance(idx):
    fig, ax = plt.subplots(figsize=(W170, 4.6))
    fig.subplots_adjust(left=.085, right=.985, top=.875, bottom=.335)
    d = idx[(idx.depth_m >= 1000) & (idx.depth_m <= 1450)]
    for name, lo, hi, cc in WINDOWS:
        ax.axhspan(lo, hi, color=cc, alpha=.30 if name != "ooze" else .16, zorder=0)
        ax.text(1.35e-4, (lo + hi) / 2, name, fontsize=6.2, va="center",
                color="#222222", fontweight="bold", zorder=6)
    ax.axhline(THGU_76, color=C_THGU, lw=1.1, zorder=4)
    ax.text(1.4e-5, THGU_76 - 3, "THGU 1036.5 m", fontsize=6.5, color=C_THGU,
            fontweight="bold", ha="left", zorder=6)
    ax.axvline(BG, color="#555555", ls=":", lw=1.0, zorder=4)
    ax.axvline(10 * BG, color=C_RED, ls="--", lw=1.1, zorder=4)
    ax.plot(d.green_index, d.depth_m, lw=.7, color=GREEN_L, zorder=3)
    ax.scatter(d.green_index, d.depth_m, s=7, color=GREEN_F, edgecolor=GREEN_L,
               lw=.35, zorder=3)
    for z in (1280.0, 1300.0):
        v = float(d.loc[d.depth_m == z, "green_index"].iloc[0])
        ax.annotate(f"{z:.0f} m, {v/BG:.2f}x", (v, z), textcoords="offset points",
                    xytext=(13, -1), fontsize=6.3, fontweight="bold",
                    color=GREEN_L, arrowprops=dict(arrowstyle="->", lw=.7,
                                                   color=GREEN_L))
    nt = d[(d.depth_m >= 1036.5) & (d.depth_m <= 1066.5)]
    ax.annotate("GLAUCONITE CONTROL FAILED\nn = 3, at 0.05x background, which is far\n"
                "BELOW ordinary background, not merely\nbelow the firing criterion",
                (float(nt.green_index.median()), 1054), xytext=(2.6e-3, 1082),
                fontsize=6.4, fontweight="bold", color=C_RED, linespacing=1.35,
                va="top", zorder=6,
                arrowprops=dict(arrowstyle="->", lw=.9, color=C_RED,
                                connectionstyle="arc3,rad=-0.12"))
    ax.set_xscale("log")
    ax.set_xlim(1.2e-5, 7e-2)
    ax.set_ylim(1450, 1000)
    ax.set_xlabel("green index (fraction of cropped-frame pixels), log scale")
    ax.set_ylabel("Depth (m RKB)")
    ax.grid(alpha=.25, lw=.4)
    ax.set_title("Glauconite green index against depth, well 34/7-6.\n"
                 "Thresholds frozen at a* < -5.0 and C* >= 12.0.",
                 fontsize=8.5, fontweight="bold", loc="left", linespacing=1.4)
    ax.legend(handles=[Patch(color=C_OLIG, alpha=.30, label="target sand body, 1218 to 1283 m"),
                       Patch(color=C_BLUE, alpha=.16, label="ooze reference, 1066.5 to 1218 m"),
                       Patch(color=C_THGU, alpha=.30, label="near-THGU control, FAILED"),
                       Patch(color=C_UTS, alpha=.30, label="Utsira, no cuttings photographs"),
                       Line2D([], [], color="#555555", ls=":",
                              label=f"deep background, {BG:.6f}"),
                       Line2D([], [], color=C_RED, ls="--",
                              label=f"10x strict criterion, {10*BG:.6f}")],
              loc="lower left", frameon=True, framealpha=.94, ncol=2)
    fig.text(.02, .028, "\n".join([
        "The target does not fire. Median 0.39x background over the primary window (n = 7), maximum 1.40x, and "
        "no photograph anywhere in the sand",
        "body reaches the 10x strict criterion. Because the glauconite-specific control below the unconformity "
        "failed, returning 0.05x background rather",
        "than firing, the test lacks demonstrated sensitivity in this depth range. Under the rule registered "
        "before any target value was computed, this",
        "null is therefore UNINFORMATIVE and is not reported as a negative result. The load-bearing evidence "
        "for this well is the log measurement",
        "shown in the Stage 3-lite figure."]),
        fontsize=6.0, va="bottom", linespacing=1.5)
    save(fig, "provenance_34_7_6")


# ----------------------------------------------------------------- figure 3
def fig_eleven(idx):
    G = pd.read_csv(C.WORK_DIR / "16_green_index_all.csv")
    THGU = {"34_7-4": 1187, "34_7-9": 1172, "34_7-10": 1093, "34_8-3": 1175,
            "34_8-3_A": 1180, "34_4-6": 1250, "34_4-7": 1200, "34_7-1": 1170,
            "34_7-6": THGU_76}
    UTS = {"34_7-4": (1118, 1187), "34_7-9": (1077, 1172), "34_7-10": (993, 1093),
           "34_8-3": None, "34_8-3_A": (1120, 1180), "34_4-6": (1210, 1250),
           "34_4-7": (1180, 1200), "34_7-1": (1150, 1170), "34_7-6": (1030, 1036.5)}
    OLIG = {"34_7-4": (1187, 1340), "34_7-9": (1172, 1340), "34_7-10": (1093, 1350),
            "34_8-3": (1320, 1500), "34_8-3_A": (1240, 1300), "34_4-6": (1250, 1390),
            "34_4-7": (1200, 1220), "34_7-1": (1170, 1200), "34_7-6": (1218, 1283)}
    # Utsira control outcome per well, from the Part D/E table
    UCTRL = {"34_7-1": 239, "34_4-6": 40, "34_8-3_A": 39, "34_7-4": 29,
             "34_7-10": 27, "34_7-9": 3.7, "34_4-7": 3.6, "34_8-3": None,
             "34_7-6": None}
    order = ["34_7-6", "34_7-1", "34_4-6", "34_8-3_A", "34_7-4", "34_7-10",
             "34_7-9", "34_4-7", "34_8-3"]
    fig, axes = plt.subplots(1, len(order), figsize=(W170, 4.5), sharey=True)
    fig.subplots_adjust(left=.075, right=.99, top=.80, bottom=.355, wspace=.13)
    for ax, w in zip(axes, order):
        d = (idx.rename(columns={"green_index": "green_index"}) if w == WELL
             else G[G.well == w].sort_values("depth_m"))
        y = d.depth_m - THGU[w]
        bgw = BG if w == WELL else float(G[(G.well == w) & (G.depth_m > 1450)]
                                        .green_index.median())
        ax.plot(d.green_index, y, lw=.55, color=GREEN_L)
        ax.fill_betweenx(y, 1e-6, d.green_index, color=GREEN_F, alpha=.45)
        ax.axvline(bgw, color="#888888", ls=":", lw=.8)
        if UTS[w]:
            ax.axhspan(UTS[w][0] - THGU[w], UTS[w][1] - THGU[w], color=C_UTS,
                       alpha=.30, zorder=0)
        ax.axhspan(OLIG[w][0] - THGU[w], OLIG[w][1] - THGU[w], color=C_OLIG,
                   alpha=.22, zorder=0)
        ax.axhline(0, color=C_THGU, lw=1.0)
        ax.set_xscale("log")
        ax.set_xlim(1.2e-5, 4e-1)
        ax.set_ylim(320, -260)
        ax.set_xticks([1e-4, 1e-2])
        u = UCTRL[w]
        tag = ("NO Utsira\ncontrol" if u is None else
               (f"Utsira {u:.0f}x" if u >= 10 else f"Utsira {u:.1f}x\nMISSED"))
        col = C_RED if u is None or u < 10 else "#2d6a3e"
        ax.set_title(w.replace("_", "/", 1).replace("_", " ") + "\n" + tag,
                     fontsize=6.6, fontweight="bold", color=col, linespacing=1.35)
        ax.grid(alpha=.22, lw=.35)
        ax.tick_params(labelsize=5.8)
        if w == WELL:
            for sp in ax.spines.values():
                sp.set_edgecolor(C_RED)
                sp.set_linewidth(1.5)
    axes[0].set_ylabel("Depth below THGU (m)")
    for ax in axes:
        ax.set_xlabel("index", fontsize=6.3)
    fig.suptitle("Glauconite green index against depth below the unconformity.\nThe nine "
                 "wells with an unconformity pick. Thresholds frozen at a* < -5.0 and "
                 "C* >= 12.0.",
                 fontsize=8.5, fontweight="bold", y=.985, linespacing=1.4)
    fig.text(.02, .028, "\n".join([
        "Green band is the Utsira control, orange band the Oligocene target, red line the unconformity, dotted "
        "line each well's own deep background. Panel",
        "titles give the Utsira control outcome. 24/9-3 and 24/9-4 are omitted from this figure only: they carry "
        "no Top Hordaland Group Unconformity pick, so",
        "they cannot be placed in this common stratigraphic frame. They are included in the eleven-well index and "
        "in the raw-depth figure. 34/7-6 is boxed in",
        "red because it has NO Utsira control. It does have an Utsira interval, picked from Saga Table 1 at 1030 "
        "to 1036.5 m and shaded green in its panel, and",
        "that interval has log coverage; what it lacks is any cuttings photograph inside it, because the "
        "formation is 6.5 m thick and falls in a 30 m sampling gap.",
        "34/8-3 is in the same position, an Utsira interval with no photographs in it. Because 34/7-6 has no "
        "Utsira control its null at the target is treated",
        "differently from the other wells and is reported as uninformative rather than negative. The index also "
        "missed the Utsira in 34/7-9 and 34/4-7, at 3.7x",
        "and 3.6x background, so its sensitivity is five of the seven wells with photographs inside their Utsira "
        "interval."]),
        fontsize=6.0, va="bottom", linespacing=1.5)
    save(fig, "25_eleven_well_compare")


def save(fig, stem):
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)
    for ext, kw in (("png", dict(dpi=400)), ("pdf", {})):
        p = C.FIG_DIR / f"{stem}.{ext}"
        fig.savefig(p, **kw)
        print("figure:", p)
    plt.close(fig)


if __name__ == "__main__":
    BG = float(pd.read_csv(C.WORK_DIR / "20_controls_34_7_6.csv")
               .query("depth_m > 1450").green_index.median())
    print(f"background = {BG:.6f}")
    idx = index_34_7_6()
    make_csv(idx, load_ba())
    fig_stage3lite(load_logs())
    fig_provenance(idx)
    fig_eleven(idx)
