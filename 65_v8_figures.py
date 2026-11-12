"""
v8 part E (V8_PLAN.md): descriptive figures of the closed step-1 result.
No new statistic: every rho printed is the step-1 per-well value, computed
on the unsmoothed high-passed series.

  fig_v8_overview  11 wells: measured and photo-predicted Si/Al against depth
  fig_v8_detail    best, middle and worst well by step-1 rho, with gamma ray
                   and the mud-log sand column where one was digitised

Run:  python 65_v8_figures.py
"""
from importlib import import_module

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config as C

M = import_module("52_v7_photo_to_xrf")
LB = import_module("03_make_labels")
OUT = C.REPO_DIR / "results" / "v8" if hasattr(C, "REPO_DIR") else __import__("pathlib").Path("results/v8")
BLUE, ORANGE = "#2a78d6", "#eb6834"      # categorical slots 1 and 2 (validated: CVD dE 24.7)
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
DETAIL = ["34_7-9", "34_7-6", "34_8-3"]  # best, middle, worst by step-1 rho (fixed in the plan)
plt.rcParams.update({"font.family": "Helvetica", "font.size": 8, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF,
                     "savefig.facecolor": SURF, "axes.linewidth": 0.8})


def r2(v):
    """Two decimals, halves rounded up (0.025 -> +0.03, as in the results tables)."""
    return f"{np.floor(v * 100 + 0.5) / 100:+.2f}"


def name(w):
    return w.replace("_", "/", 1).replace("_", " ")


def smooth(d, v, k=2):
    """5-bag running median within continuous stretches (display only)."""
    sid = M.stretch_ids(d)
    out = np.full(len(v), np.nan)
    for s in np.unique(sid):
        ix = np.flatnonzero(sid == s)
        ix = ix[np.argsort(d[ix])]
        for j in range(len(ix)):
            out[ix[j]] = np.nanmedian(v[ix[max(0, j - k):j + k + 1]])
    return out


def series(s1, w):
    m = (s1.well.values == w) & s1.in_S.values.astype(bool) & np.isfinite(s1.T1.values) & np.isfinite(s1.pred_RD.values)
    d = s1.depth_m.values[m]
    o = np.argsort(d)
    d = d[o]
    hy, hp = M.highpass(d, s1.T1.values[m][o]), M.highpass(d, s1.pred_RD.values[m][o])
    rho = M.rho(hp, hy)
    z = lambda v: v / np.nanstd(v)
    return d, smooth(d, z(hy)), smooth(d, z(hp)), rho, M.stretch_ids(d)


def draw(ax, d, a, b, sid, lw=1.1):
    for s in np.unique(sid):
        k = sid == s
        ax.plot(a[k], d[k], color=BLUE, lw=lw, solid_capstyle="round")
        ax.plot(b[k], d[k], color=ORANGE, lw=lw, solid_capstyle="round")


def tidy(ax, xlab=None):
    ax.grid(True, color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, pad=2)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    if xlab:
        ax.set_xlabel(xlab, fontsize=7.5)


def tops(w):
    t = pd.read_csv(OUT / "sodir_group_tops.csv")
    return t[t.well == w]


def overview(s1):
    wells = sorted(s1.well[s1.in_S].unique())
    S = {w: series(s1, w) for w in wells}
    order = sorted(wells, key=lambda w: -S[w][3])
    fig, axes = plt.subplots(1, len(order), figsize=(13.5, 6.6), sharex=True)
    for ax, w in zip(axes, order):
        d, a, b, rho, sid = S[w]
        for r in tops(w).itertuples():
            if d.min() < r.top < d.max():
                ax.axhline(r.top, color=INK2, lw=0.5, ls=(0, (2, 2)))
        draw(ax, d, a, b, sid, lw=0.9)
        ax.set_ylim(d.max() + 15, d.min() - 15)
        ax.set_xlim(-3.2, 3.2)
        ax.set_xticks([-2, 0, 2])
        ax.set_title(f"{name(w)}\n" + r"$\rho$" + f" = {r2(rho)}", fontsize=8.5, color=INK, pad=6)
        tidy(ax)
    axes[0].set_ylabel("Depth (m MD)")
    fig.supxlabel("Si/Al, departure from the local trend (within-well standard deviations)", fontsize=8.5, color=INK2, y=0.075)
    h = [plt.Line2D([], [], color=BLUE, lw=1.6), plt.Line2D([], [], color=ORANGE, lw=1.6),
         plt.Line2D([], [], color=INK2, lw=0.6, ls=(0, (2, 2)))]
    fig.legend(h, ["measured on the cuttings (XRF)", "predicted from the photograph (model never saw this well)", "group top (Sodir)"],
               loc="upper left", bbox_to_anchor=(0.045, 0.985), ncol=3, frameon=False, fontsize=8.5)
    fig.text(0.5, 0.022, "Tertiary overburden. Both curves: +/-50 m running median removed, then a 5-bag running median for display. "
             r"$\rho$" + ": Spearman on the unsmoothed series. Wells ordered by " + r"$\rho$" + ".", ha="center", va="bottom", fontsize=7.2, color=INK2)
    fig.subplots_adjust(left=0.045, right=0.99, top=0.86, bottom=0.14, wspace=0.46)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"fig_v8_overview.{ext}", dpi=220)
    plt.close(fig)


def detail(s1):
    lab = pd.read_csv(C.WORK_DIR / "v7" / "step3" / "bag_labels_A.csv")
    fig = plt.figure(figsize=(12.5, 7.0))
    gs = fig.add_gridspec(1, 11, width_ratios=[1, 1.7, 0.8, 0.35, 1, 1.7, 0.8, 0.35, 1, 1.7, 0.8])
    tags = ["highest agreement", "middle", "lowest agreement"]
    for i, w in enumerate(DETAIL):
        d, a, b, rho, sid = series(s1, w)
        lim = (d.max() + 15, d.min() - 15)
        ax0, ax1, ax2 = (fig.add_subplot(gs[0, 4 * i + j]) for j in range(3))
        src, _ = C.GR_SOURCES[w]
        gr = LB.load_gr(C.SSD_ROOT / "Wells" / src, (d.min() - 15, d.max() + 15))
        g = gr.rolling(9, center=True, min_periods=1).median()
        ax0.plot(g.values, g.index.values, color=INK2, lw=0.7)
        ax0.set_xlim(np.nanpercentile(g.values, 0.5) - 5, np.nanpercentile(g.values, 99.5) + 5)
        tidy(ax0, "Gamma ray (API)")
        ax0.set_ylabel("Depth (m MD)" if i == 0 else "")
        draw(ax1, d, a, b, sid)
        ax1.set_xlim(-3.2, 3.2)
        ax1.set_xticks([-2, 0, 2])
        tidy(ax1, "Si/Al, departure from\nlocal trend (SD)")
        y = lab[(lab.well == w) & lab.Y.notna() & (lab.depth_m >= d.min()) & (lab.depth_m <= d.max())].sort_values("depth_m")
        if len(y):
            ax2.fill_betweenx(y.depth_m.values, 0, 100 * y.Y.values, step="pre", color="#b7b6ae", lw=0)
            ax2.set_xlim(0, 100)
            ax2.set_xticks([0, 50, 100])
        else:
            ax2.text(0.5, 0.5, "no mud log\nfor this well", transform=ax2.transAxes, ha="center", va="center", fontsize=7.5, color=INK2)
            ax2.set_xticks([])
        tidy(ax2, "Mud-log sand (%)")
        for ax in (ax0, ax1, ax2):
            ax.set_ylim(*lim)
            for r in tops(w).itertuples():
                if d.min() < r.top < d.max():
                    ax.axhline(r.top, color=INK2, lw=0.5, ls=(0, (2, 2)))
        for r in tops(w).itertuples():
            if d.min() < r.top < d.max():
                ax0.text(ax0.get_xlim()[0], r.top + 8, " top " + r.group.title(), fontsize=6.5, color=INK2, va="top",
                         bbox=dict(facecolor=SURF, edgecolor="none", pad=0.6, alpha=0.85))
        for ax in (ax1, ax2):
            ax.set_yticklabels([])
        ax1.set_title(f"{name(w)}: {tags[i]}, " + r"$\rho$" + f" = {r2(rho)}", fontsize=9, color=INK, pad=8)
    h = [plt.Line2D([], [], color=BLUE, lw=1.6), plt.Line2D([], [], color=ORANGE, lw=1.6)]
    fig.legend(h, ["measured on the cuttings (XRF)", "predicted from the photograph (model never saw this well)"],
               loc="upper left", bbox_to_anchor=(0.045, 0.99), ncol=2, frameon=False, fontsize=8.5)
    fig.text(0.955, 0.978, "Wells chosen by rank of " + r"$\rho$" + " (best, middle, worst), not by appearance. Si/Al curves: +/-50 m running median removed,\n"
             "5-bag running median for display; " + r"$\rho$" + " on the unsmoothed series. Mud-log sand: wellsite cuttings %, digitised (step 3).",
             ha="right", va="top", fontsize=7.2, color=INK2)
    fig.subplots_adjust(left=0.05, right=0.99, top=0.87, bottom=0.09, wspace=0.12)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"fig_v8_detail.{ext}", dpi=220)
    plt.close(fig)


def main():
    s1 = pd.read_csv(C.WORK_DIR / "v7" / "step1_predictions.csv")
    overview(s1)
    detail(s1)
    print("written to", OUT)


if __name__ == "__main__":
    main()
