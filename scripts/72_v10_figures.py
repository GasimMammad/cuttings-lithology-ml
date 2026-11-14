"""
Figures for the closed v9 and v10 results. No new statistic: everything drawn is read from saved result files.

  fig_v10_tops          photo stratigraphy (v10 S): units assigned from photographs against Sodir units,
                        and the error of every evaluated top against the nearest offset well
  fig_v9_mudlog_tile    one mud-log tile with both readings and the bag labels made from them (v8 D)

Run:  python 72_v10_figures.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from PIL import Image

import config as C

BLUE, ORANGE = "#2a78d6", "#eb6834"                                   # categorical slots 1 and 2 (validated: CVD dE 24.7)
RAMP = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"]       # ordinal blue ramp, steps 250-700 (validated --ordinal)
INK, INK2, GRID, SURF, NEUTRAL = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#c9c8c3"
UNITS = ["Nordland Gp", "Hordaland Gp", "Rogaland Gp", "Cretaceous", "below base Cretaceous"]
BOUND = ["top Hordaland", "top Rogaland", "top Cretaceous", "base Cretaceous"]
WELLS = ["24_9-3", "24_9-4", "34_4-6", "34_4-7", "34_7-1", "34_7-4", "34_7-6", "34_7-9", "34_7-10", "34_8-3"]
plt.rcParams.update({"font.family": "Helvetica", "font.size": 8, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF,
                     "savefig.facecolor": SURF, "axes.linewidth": 0.8})
name = lambda w: w.replace("_", "/", 1).replace("_", " ")


def save(fig, stem):
    for ext in ("png", "pdf"):
        fig.savefig(Path("results") / stem.split("_")[1] / f"{stem}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def strip(ax, x, w, d, u):
    """One column of bags coloured by unit; each bag is drawn from the bag above down to its own depth."""
    top = np.concatenate([[d[0] - np.median(np.diff(d))], d[:-1]])
    start = 0
    for i in range(1, len(d) + 1):
        if i == len(d) or u[i] != u[start]:
            ax.fill_between([x, x + w], top[start], d[i - 1], color=RAMP[int(u[start])], lw=0)
            start = i


def tops():
    bags = pd.read_csv("results/v10/S_bag_units.csv")
    T = pd.read_csv("results/v10/S_tops.csv")
    T = T[T.well.isin(WELLS)]
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 4.5), gridspec_kw={"width_ratios": [1.55, 1], "wspace": 0.46})

    for i, w in enumerate(WELLS):
        g = bags[bags.well == w].sort_values("depth_m")
        d = g.depth_m.values
        strip(a, i - 0.40, 0.38, d, g.unit.values)
        strip(a, i + 0.02, 0.38, d, g.pred_unit.values)
    a.set_xlim(-0.6, len(WELLS) - 0.4)
    a.set_ylim(3400, 100)
    a.set_xticks(range(len(WELLS)))
    a.set_xticklabels([name(w) for w in WELLS], rotation=50, ha="right", fontsize=7)
    a.set_ylabel("depth (m RKB)")
    a.yaxis.grid(True, color=GRID, lw=0.5)
    a.set_axisbelow(True)
    a.tick_params(length=0)
    for s in ("top", "right", "bottom"):
        a.spines[s].set_visible(False)
    a.set_title("In each pair: Sodir units (left), units assigned from photographs (right)", loc="left", fontsize=8, color=INK2, pad=32)
    a.legend(handles=[Patch(color=RAMP[k], label=UNITS[k]) for k in range(5)], loc="lower left", bbox_to_anchor=(-0.02, 1.0),
             ncol=3, frameon=False, fontsize=6.5, handlelength=1.0, columnspacing=0.9, handletextpad=0.4)

    rows = []
    for k, bd in enumerate(BOUND):
        x = T[T.boundary == bd]
        for j, (col, c, lab) in enumerate((("err_photo", BLUE, "photographs"), ("err_offset", ORANGE, "nearest offset well"))):
            y = k + (0.17 if j else -0.17)
            v = np.clip(x[col].values, 1.5, None)
            b.scatter(v, np.full(len(v), y), s=22, color=c, edgecolor=SURF, linewidth=0.7, zorder=3, label=lab if k == 0 else None)
            med = float(x[col].median())
            b.plot([med, med], [y - 0.13, y + 0.13], color=INK, lw=1.4, zorder=4)
            rows.append((k, j, med))
        b.text(1.02, k, f"{np.floor(rows[-2][2] + 0.5):.0f} m\n{np.floor(rows[-1][2] + 0.5):.0f} m", transform=b.get_yaxis_transform(), va="center", ha="left",
               fontsize=7, color=INK, linespacing=1.55)
    b.text(1.02, -0.62, "median", transform=b.get_yaxis_transform(), va="center", ha="left", fontsize=7, color=INK2)
    b.set_xscale("log")
    b.set_xlim(1.2, 1500)
    b.set_xticks([3, 10, 30, 100, 300, 1000])
    b.set_xticklabels(["3", "10", "30", "100", "300", "1000"])
    b.set_ylim(3.5, -0.75)
    b.set_yticks(range(4))
    b.set_yticklabels([f"{bd}\n({int((T.boundary == bd).sum())} tops)" for bd in BOUND], color=INK)
    b.set_xlabel("distance from the Sodir top (m, log scale)")
    b.xaxis.grid(True, color=GRID, lw=0.5)
    b.set_axisbelow(True)
    b.tick_params(length=0)
    for s in ("top", "right", "left"):
        b.spines[s].set_visible(False)
    b.set_title("Each dot is one top; black bar = median", loc="left", fontsize=8, color=INK2, pad=32)
    b.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=2, frameon=False, fontsize=7, handletextpad=0.2, columnspacing=1.0)
    fig.suptitle("Photographs place major tops less well than the nearest well",
                 x=0.06, y=1.135, ha="left", fontsize=10, color=INK, weight="bold")
    fig.text(0.06, 1.085, "34 tops in 10 held-out locations; the model sees no depth. Median error: photographs 65 m, offset well 43 m (v10 S).\n"
                         "Base Cretaceous is the exception; it was singled out after the results and is descriptive.",
             fontsize=8, color=INK2, ha="left", va="top")
    save(fig, "fig_v10_tops")


def blocks_of(reader, well, tile):
    for ln in open(f"results/v8/readers/{reader}_{well}.jsonl"):
        o = json.loads(ln)
        if o["tile"] == tile:
            return o["blocks"]
    raise KeyError(tile)


def tile():
    well, d0, tname = "34_7-9", 2800.0, "34_7-9_2800.png"
    im = np.array(Image.open(C.WORK_DIR / "v7" / "step3" / "tiles_jt" / well / tname).convert("RGB"))
    g = (im[:, :, 1].astype(int) > 110) & (im[:, :, 0] < 90) & (im[:, :, 2] < 90)       # green lines: tile top and bottom depth
    rows = np.flatnonzero(g.sum(1) > 200)
    y0, y1 = rows[rows < im.shape[0] / 2].mean(), rows[rows > im.shape[0] / 2].mean()
    pxm = (y1 - y0) / 40.0
    ext = (0, im.shape[1], d0 + (im.shape[0] - y0) / pxm, d0 - y0 / pxm)
    lab = pd.read_csv("results/v8/jt_bag_labels_A.csv")
    lab = lab[(lab.well == well) & (lab.depth_m > d0) & (lab.depth_m <= d0 + 40)]

    fig, ax = plt.subplots(1, 4, figsize=(7.4, 6.4), sharey=True, gridspec_kw={"width_ratios": [1.5, 1, 1, 1], "wspace": 0.16})
    ax[0].imshow(im, extent=ext, aspect="auto", interpolation="lanczos")
    ax[0].set_xticks([])
    ax[0].set_ylabel("depth (m RKB)")
    ax[0].set_title("1  Tile cut by a script from the\n    1986 wellsite mud log", loc="left", fontsize=8, color=INK, pad=6)
    for r, (reader, ttl) in enumerate((("JA", "2  Reader A\n    (reads every tile)"), ("JB", "3  Reader B, other model\n    (a random 20 % of tiles)"))):
        a = ax[r + 1]
        for bl in blocks_of(reader, well, tname):
            sand = bl.get("sand", 0) + bl.get("ssst", 0)
            a.barh((bl["top"] + bl["bottom"]) / 2, sand, height=(bl["bottom"] - bl["top"]) - 0.25, color=BLUE, lw=0)
            a.barh((bl["top"] + bl["bottom"]) / 2, 100 - sand, left=sand, height=(bl["bottom"] - bl["top"]) - 0.25, color=NEUTRAL, lw=0)
        a.set_xlim(0, 100)
        a.set_xticks([0, 50, 100])
        a.set_xlabel("% of cuttings")
        a.set_title(ttl, loc="left", fontsize=8, color=INK, pad=6)
    a = ax[3]
    for r in lab.itertuples():
        a.barh((r.a + r.depth_m) / 2, 100 * r.Y, height=(r.depth_m - r.a) - 0.25, color=BLUE, lw=0)
        a.text(100 * r.Y + 3, (r.a + r.depth_m) / 2, f"{100 * r.Y:.0f}", va="center", fontsize=6.5, color=INK2)
    a.set_xlim(0, 118)
    a.set_xticks([0, 50, 100])
    a.set_xlabel("sand fraction of the bag (%)")
    a.set_title("4  Label of each bag that\n    was photographed", loc="left", fontsize=8, color=INK, pad=6)
    for a in ax[1:]:
        a.xaxis.grid(True, color=GRID, lw=0.5)
        a.set_axisbelow(True)
        a.tick_params(length=0)
        for s in ("top", "right", "left"):
            a.spines[s].set_visible(False)
    for s in ("top", "right", "bottom"):
        ax[0].spines[s].set_visible(False)
    ax[0].set_ylim(ext[2], ext[3])
    ax[0].tick_params(length=0)
    ax[1].legend(handles=[Patch(color=BLUE, label="sand and sandstone"), Patch(color=NEUTRAL, label="everything else")],
                 loc="upper left", bbox_to_anchor=(0.0, -0.075), ncol=2, frameon=False, fontsize=7, handlelength=1.0, columnspacing=1.0)
    fig.suptitle("From a 1986 mud log to a label for every bag: well 34/7-9, 2800 to 2840 m", x=0.06, y=1.06, ha="left",
                 fontsize=10, color=INK, weight="bold")
    fig.text(0.06, 1.012, "In the tile, dots are sand and dashes are clay; the script added the red depth ruler and the blue 0-100 % ruler.\n"
                          "Two readers (one model family; no human key) read the same tile without seeing each other,\n"
                          "the photographs or the chemistry.",
             fontsize=8, color=INK2, ha="left", va="top")
    save(fig, "fig_v9_mudlog_tile")


if __name__ == "__main__":
    tops()
    tile()
