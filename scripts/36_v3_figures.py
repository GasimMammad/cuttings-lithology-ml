"""
v3 FIGURES.
  v3_fig1_baselines   per-well AUC (left) and local AUC, pairs < 50 m (right)
                      for E2, D1, one quartz feature, XRF Si/Al reference
                      and the relative-depth baseline
  v3_fig2_xrf_shallow per-well Spearman rho vs cuttings XRF Si/Al in the
                      unlabelled Tertiary overburden (pre-registered test)

Run:  python 36_v3_figures.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config as C

R = C.WORK_DIR / "v3_results"
FIG = R / "figures"
MM = 1 / 25.4
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
                     "font.size": 8, "pdf.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})
COL = {"24_9-3": "#1f77b4", "24_9-4": "#ff7f0e", "34_7-4": "#2ca02c", "34_7-6": "#d62728",
       "34_7-9": "#9467bd", "34_8-3": "#8c564b", "34_8-3_A": "#e377c2", "34_4-6": "#7f7f7f",
       "34_4-7": "#bcbd22", "34_7-10": "#17becf", "34_7-1": "#000000"}
SIG = [("REL_DEPTH", "Rel. depth\nbaseline"), ("E2", "E2\n(v2 primary)"),
       ("D1", "ResNet-50"), ("ONE_FEATURE", "Quartz-grain\nsize"),
       ("XRF_SIAL", "XRF Si/Al\nreference")]


def nice(w):
    return w.replace("_", "/").replace("/A", " A")


def strip(ax, t, col, title):
    for i, (s, lbl) in enumerate(SIG):
        g = t[t.signal == s].dropna(subset=[col]).sort_values("well")
        jit = np.linspace(-0.2, 0.2, max(len(g), 1))
        for (_, r), j in zip(g.iterrows(), jit):
            ax.scatter(i + j, r[col], s=20, color=COL[r.well], edgecolor="white", lw=0.4, zorder=3)
        if len(g):
            ax.hlines(np.median(g[col]), i - 0.3, i + 0.3, color="k", lw=1.6, zorder=4)
    ax.axhline(0.5, color="#C0392B", ls="--", lw=0.9)
    ax.set_xticks(range(len(SIG)))
    ax.set_xticklabels([l for _, l in SIG], fontsize=6.3, rotation=35, ha="right")
    ax.set_ylim(0, 1.03)
    ax.set_title(title, fontsize=8)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    t = pd.read_csv(R / "baselines_per_well.csv")
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 72 * MM), sharey=True)
    strip(axs[0], t, "auc", "Whole-well AUC (held-out well)")
    strip(axs[1], t, "local50", "Local AUC: sand-clay pairs < 50 m apart")
    axs[0].set_ylabel("AUC (0.5 = chance)")
    hs = [plt.Line2D([], [], marker="o", ls="", color=COL[w], label=nice(w)) for w in sorted(t.well.unique())]
    fig.legend(handles=hs, fontsize=6.5, ncol=7, loc="lower center", frameon=False, bbox_to_anchor=(0.5, -0.06))
    fig.savefig(FIG / "v3_fig1_baselines.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / "v3_fig1_baselines.pdf", bbox_inches="tight")
    plt.close(fig)

    x = pd.read_csv(R / "xrf_shallow.csv")
    order = ["ONE_FEATURE", "D1", "E2"]
    lbl = {"ONE_FEATURE": "Quartz-grain size\n(pre-registered primary)", "D1": "ResNet-50 embeddings",
           "E2": "E2 engineered"}
    fig, ax = plt.subplots(figsize=(120 * MM, 70 * MM))
    for i, s in enumerate(order):
        g = x[x.signal == s].sort_values("well")
        jit = np.linspace(-0.22, 0.22, len(g))
        for (_, r), j in zip(g.iterrows(), jit):
            ax.scatter(i + j, r.rho, s=22, color=COL[r.well], edgecolor="white", lw=0.4, zorder=3)
        ax.hlines(np.median(g.rho), i - 0.3, i + 0.3, color="k", lw=1.6)
    ax.axhline(0, color="#C0392B", ls="--", lw=0.9)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([lbl[o] for o in order], fontsize=7)
    ax.set_ylabel("Spearman rho with cuttings XRF Si/Al\n(high-passed, unlabelled Tertiary)")
    hs = [plt.Line2D([], [], marker="o", ls="", color=COL[w], label=nice(w)) for w in sorted(x.well.unique())]
    ax.legend(handles=hs, fontsize=6, ncol=2, frameon=False, loc="upper right", bbox_to_anchor=(1.32, 1))
    fig.savefig(FIG / "v3_fig2_xrf_shallow.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / "v3_fig2_xrf_shallow.pdf", bbox_inches="tight")
    plt.close(fig)
    print("written", FIG)


if __name__ == "__main__":
    main()
