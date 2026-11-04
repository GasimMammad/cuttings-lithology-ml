"""
PART D4 — figures.
 (i)  comparison figure: green index vs DEPTH BELOW THGU, on-mound wells
      grouped separately from off-mound, so the same stratigraphic level is
      aligned across wells (THGU is 1093 m in 34/7-10 but 1250 m in 34/4-6).
 (ii) per-well detail figure in RAW depth with unit boundaries.
Reads 16_green_index_all.csv only; thresholds frozen upstream.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config as C

G = pd.read_csv(C.WORK_DIR / "16_green_index_all.csv")
THGU = {"34_7-4": 1187, "34_7-9": 1172, "34_7-10": 1093, "34_8-3": 1175,
        "34_8-3_A": 1180, "34_4-6": 1250, "34_4-7": 1200, "34_7-1": 1170}
UTS = {"34_7-4": (1118, 1187), "34_7-9": (1077, 1172), "34_7-10": (993, 1093),
       "34_8-3": None, "34_8-3_A": (1120, 1180), "34_4-6": (1210, 1250),
       "34_4-7": (1180, 1200), "34_7-1": (1150, 1170)}
OLIG = {"34_7-4": (1187, 1340), "34_7-9": (1172, 1340), "34_7-10": (1093, 1350),
        "34_8-3": (1320, 1500), "34_8-3_A": (1240, 1300), "34_4-6": (1250, 1390),
        "34_4-7": (1200, 1220), "34_7-1": (1170, 1200)}
GROUPS = [("ON-MOUND", ["34_7-4", "34_7-10"], "#C44E52"),
          ("UNCERTAIN", ["34_7-9", "34_7-1"], "#DD8452"),
          ("off-mound", ["34_4-6", "34_8-3", "34_8-3_A", "34_4-7"], "#4C72B0")]


def bg(w):
    s = G[(G.well == w) & (G.depth_m > 1450)].green_index
    return float(s.median()) if len(s) else np.nan


def fig_below_thgu():
    order = [w for _, ws, _ in GROUPS for w in ws]
    fig, axes = plt.subplots(1, len(order), figsize=(2.3 * len(order), 10),
                             sharey=True)
    for ax, w in zip(axes, order):
        col = next(c for _, ws, c in GROUPS if w in ws)
        grp = next(g for g, ws, _ in GROUPS if w in ws)
        d = G[G.well == w].sort_values("depth_m")
        y = d.depth_m - THGU[w]
        ax.plot(d.green_index, y, lw=.7, color="#2d6a3e")
        ax.fill_betweenx(y, 0, d.green_index, color="#4a9c68", alpha=.45)
        b = bg(w)
        ax.axvline(b, color="#888", ls=":", lw=.9)
        if UTS[w]:
            ax.axhspan(UTS[w][0] - THGU[w], UTS[w][1] - THGU[w],
                       color="#55A868", alpha=.28, zorder=0)
        a, bb = OLIG[w]
        ax.axhspan(a - THGU[w], bb - THGU[w], color="#DD8452", alpha=.22, zorder=0)
        ax.axhline(0, color="#C44E52", lw=1.4)
        ax.set_xscale("symlog", linthresh=1e-3)
        ax.set_xlim(0, 0.35)
        ax.set_ylim(320, -260)
        ax.set_title(w.replace("_", "/") + f"\n{grp}", fontsize=8.5,
                     fontweight="bold", color=col)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=.25)
    axes[0].set_ylabel("depth below THGU (m)   [common stratigraphic frame]")
    for ax in axes:
        ax.set_xlabel("green index", fontsize=8)
    fig.suptitle("PART D — glauconite green index vs DEPTH BELOW THGU.  "
                 "green band = Utsira control, orange band = Oligocene target, "
                 "red line = THGU, dotted = that well's deep background.\n"
                 "Thresholds FROZEN at a* < -5.0, C* >= 12.0 (calibrated on "
                 "34/4-6 only).", fontweight="bold", fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    p = C.FIG_DIR / "18_green_below_thgu.png"
    fig.savefig(p, dpi=150)
    print("figure:", p)


def fig_raw_depth():
    order = [w for _, ws, _ in GROUPS for w in ws] + ["24_9-3", "24_9-4"]
    fig, axes = plt.subplots(1, len(order), figsize=(2.1 * len(order), 10),
                             sharey=True)
    for ax, w in zip(axes, order):
        d = G[G.well == w].sort_values("depth_m")
        ax.plot(d.green_index, d.depth_m, lw=.6, color="#2d6a3e")
        ax.fill_betweenx(d.depth_m, 0, d.green_index, color="#4a9c68", alpha=.45)
        b = bg(w)
        if np.isfinite(b):
            ax.axvline(b, color="#888", ls=":", lw=.9)
        if w in UTS and UTS[w]:
            ax.axhspan(*UTS[w], color="#55A868", alpha=.28, zorder=0)
        if w in OLIG:
            ax.axhspan(*OLIG[w], color="#DD8452", alpha=.22, zorder=0)
        if w in THGU:
            ax.axhline(THGU[w], color="#C44E52", lw=1.2)
        ax.set_xscale("symlog", linthresh=1e-3)
        ax.set_xlim(0, 0.35)
        ax.set_ylim(3400, 380)
        ax.set_title(w.replace("_", "/"), fontsize=8.5, fontweight="bold")
        ax.tick_params(labelsize=6.5)
        ax.grid(alpha=.25)
    axes[0].set_ylabel("Depth (m RKB)")
    fig.suptitle("PART D — green index vs RAW DEPTH, all ten wells "
                 "(per-well detail).", fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    p = C.FIG_DIR / "18_green_raw_depth.png"
    fig.savefig(p, dpi=150)
    print("figure:", p)


if __name__ == "__main__":
    fig_below_thgu()
    fig_raw_depth()
