"""
v2 FIGURES for the results summary / conference.

  v2_fig1_per_well_auc     per-well held-out AUC for every model (+ v1 and
                           a depth-only baseline), chance line, eligible wells
  v2_fig2_domain_shift     p(sand) on held-out wells, raw vs per-well z:
                           the whole-well offset that sank v1, and its fix
  v2_fig3_blind_logs       blind sand logs: GR-derived Vsh vs model
                           prediction for held-out wells
  v2_fig4_labels           labelled depths per well, v1 vs v2

All figures 170 mm wide, PNG (300 dpi) + vector PDF, written to
WORK_DIR/v2_results/figures/.

Run:  python 30_v2_figures.py [MODEL]     (MODEL for fig 2-3, default E2)
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config as C

R = C.WORK_DIR / "v2_results"
FIG = R / "figures"
V1 = C.WORK_DIR.parent / "sinkite_ml_work"
MM = 1 / 25.4
plt.rcParams.update({"font.family": "sans-serif",
                     "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
                     "font.size": 8, "pdf.fonttype": 42, "axes.spines.top": False,
                     "axes.spines.right": False})
WELL_COL = {"24_9-3": "#1f77b4", "24_9-4": "#ff7f0e", "34_7-4": "#2ca02c",
            "34_7-6": "#d62728", "34_7-9": "#9467bd", "34_8-3": "#8c564b",
            "34_8-3_A": "#e377c2", "34_4-6": "#7f7f7f", "34_4-7": "#bcbd22",
            "34_7-10": "#17becf"}
NAMES = {"E1": "Engineered\nraw (v1)", "E2": "Engineered\nper-well z",
         "E3": "Eng. no colour\nper-well z", "D1": "ResNet-50\nraw",
         "D2": "ResNet-50\nper-well z", "D3": "ResNet-50 grey\nper-well z",
         "DEPTH_ONLY": "Depth\nonly", "V1": "v1 eng_full\n(old labels)"}


def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print("written", FIG / f"{name}.png")


def v1_auc():
    p = V1 / "final_comparison" / "all_predictions.csv"
    if not p.exists():
        return pd.DataFrame()
    d = pd.read_csv(p)
    d = d[(d.tier == "tier2") & (d.model == "eng_full")]
    rows = []
    from scipy.stats import rankdata
    for w, g in d.groupby("well"):
        y = (g.label == "sand").values
        if y.sum() == 0 or (~y).sum() == 0:
            continue
        r = rankdata(g.p_sand.values)
        a = (r[y].sum() - y.sum() * (y.sum() + 1) / 2) / (y.sum() * (~y).sum())
        rows.append({"model": "V1", "well": w, "auc": a, "n_sand": int(y.sum()),
                     "n_clay": int((~y).sum())})
    return pd.DataFrame(rows)


def fig1(tab, summ, subset="all", tag=""):
    t = tab[(tab.subset == subset) & (tab.n_sand >= 3) & (tab.n_clay >= 3)]
    v1 = v1_auc()
    order = ["V1", "E1", "E2", "E3", "D1", "D2", "D3", "DEPTH_ONLY"]
    if subset != "all":
        order = [o for o in order if o not in ("V1", "DEPTH_ONLY")]
    fig, ax = plt.subplots(figsize=(170 * MM, 80 * MM))
    for i, m in enumerate(order):
        g = v1[(v1.n_sand >= 3) & (v1.n_clay >= 3)] if m == "V1" else t[t.model == m]
        if g.empty:
            continue
        jit = np.linspace(-0.18, 0.18, len(g))
        for (_, r), j in zip(g.sort_values("well").iterrows(), jit):
            ax.scatter(i + j, r.auc, s=22, color=WELL_COL.get(r.well, "k"),
                       edgecolor="white", lw=0.4, zorder=3)
        ax.hlines(np.median(g.auc), i - 0.3, i + 0.3, color="k", lw=1.6, zorder=4)
        key = "primary_stats_all" if subset == "all" else "primary_stats_tertiary"
        if m in summ.get("models", {}):
            p = summ["models"][m][key].get("wilcoxon_p_one_sided")
            if p is not None:
                ax.text(i, 1.03, f"p={p:.3f}", ha="center", fontsize=6.5,
                        fontweight="bold" if p < 0.05 else "normal")
    ax.axhline(0.5, color="#C0392B", ls="--", lw=1)
    ax.text(len(order) - 0.5, 0.505, "chance", color="#C0392B", fontsize=7, ha="right", va="bottom")
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([NAMES[o] for o in order], fontsize=6.8)
    ax.set_ylabel("Held-out well ROC AUC (sand vs clay)")
    ax.set_ylim(0.0, 1.08)
    if "E2" in order:
        ax.axvspan(order.index("E2") - 0.45, order.index("E2") + 0.45, color="#F4D03F", alpha=0.18, zorder=0)
    hs = [plt.Line2D([], [], marker="o", ls="", color=WELL_COL[w], label=w.replace("_", "/").replace("/A", " A"))
          for w in sorted(set(t.well) | set(v1.well)) if w in WELL_COL]
    ax.legend(handles=hs, fontsize=6, ncol=5, loc="lower left", frameon=False)
    ttl = "Leave-one-well-out, wells with >=3 sand and >=3 clay depths; bar = median; p = one-sided Wilcoxon vs 0.5"
    ax.set_title(ttl + ("" if subset == "all" else "\nTertiary only (Jurassic zones removed from training and test)"),
                 fontsize=7, loc="left")
    save(fig, f"v2_fig1_per_well_auc{tag}")


def fig2(pred, raw="E1", fix="E2"):
    tag = "" if raw == "E1" else f"_{raw}_{fix}"
    lab = pred[pred.label.isin(["sand", "clay"])]
    wells = [w for w in WELL_COL if w in set(lab.well)]
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 70 * MM), sharey=True)
    for ax, m, ttl in ((axs[0], raw, "raw features (v1 recipe)"),
                       (axs[1], fix, "label-free per-well z")):
        for i, w in enumerate(wells):
            g = lab[lab.well == w]
            for k, (cls, col, off) in enumerate((("clay", "#7F8C8D", -0.17), ("sand", "#E67E22", 0.17))):
                v = g.loc[g.label == cls, f"p_{m}"].dropna().values
                if len(v):
                    ax.boxplot(v, positions=[i + off], widths=0.28, patch_artist=True,
                               showfliers=False, medianprops={"color": "k"},
                               boxprops={"facecolor": col, "alpha": 0.8, "lw": 0.5},
                               whiskerprops={"lw": 0.5}, capprops={"lw": 0.5})
        ax.axhline(0.5, color="#C0392B", ls="--", lw=0.8)
        ax.set_xticks(range(len(wells)))
        ax.set_xticklabels([w.replace("_", "/").replace("/A", " A") for w in wells], rotation=60, fontsize=6.5)
        ax.set_title(ttl, fontsize=8)
    axs[0].set_ylabel("p(sand) on held-out well")
    axs[1].legend(handles=[plt.Rectangle((0, 0), 1, 1, color="#7F8C8D"),
                           plt.Rectangle((0, 0), 1, 1, color="#E67E22")],
                  labels=["clay-labelled depths", "sand-labelled depths"], fontsize=6.5,
                  frameon=False, loc="upper right")
    save(fig, f"v2_fig2_domain_shift{tag}")


def fig3(pred, m="E2", wells=("24_9-3", "24_9-4", "34_7-4", "34_7-6", "34_7-9")):
    wells = [w for w in wells if w in set(pred.well)]
    fig, axs = plt.subplots(1, len(wells), figsize=(170 * MM, 120 * MM))
    for ax, w in zip(np.atleast_1d(axs), wells):
        g = pred[(pred.well == w) & pred.label.isin(["sand", "clay", "mixed", "unstable"])].sort_values("depth_m")
        if g.empty:
            continue
        ps = g[f"p_{m}"].rolling(3, center=True, min_periods=1).median().values
        z = g.depth_m.values.astype(float)
        v = (1 - g.vsh).values.astype(float)
        gap = np.r_[False, np.diff(z) > 20]          # do not draw across excluded stretches
        z, v, ps = (np.insert(a, np.flatnonzero(gap), np.nan) for a in (z, v, ps))
        ax.plot(v, z, color="#2C3E50", lw=0.9, label="1 - Vsh from GR (truth)")
        ax.plot(ps, z, color="#E67E22", lw=1.2, label="p(sand) from photos, blind")
        for cls, col in (("sand", "#E67E22"), ("clay", "#7F8C8D")):
            z = g[g.label == cls].depth_m
            ax.scatter(np.full(len(z), -0.06), z, marker="s", s=6, color=col, clip_on=False)
        # gaps between zones: do not draw across them
        ax.set_ylim(g.depth_m.max() + 10, g.depth_m.min() - 10)
        ax.set_xlim(-0.1, 1.02)
        ax.set_title(w.replace("_", "/").replace("/A", " A"), fontsize=8)
        ax.set_xlabel("sand-ness", fontsize=7)
        ax.grid(alpha=0.25, lw=0.4)
    np.atleast_1d(axs)[0].set_ylabel("Depth (m MD RKB)")
    h, l = np.atleast_1d(axs)[0].get_legend_handles_labels()
    fig.legend(h, l, fontsize=7, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.03))
    fig.subplots_adjust(wspace=0.45)
    fig.suptitle(f"Blind predictions (model {m}, well never seen in training) vs GR-derived 1 - Vsh; "
                 "squares = labelled sand / clay depths", fontsize=7, x=0.01, ha="left")
    save(fig, f"v2_fig3_blind_logs_{m}")


def fig4():
    v2 = pd.read_csv(C.LABELS_CSV)
    v2 = v2[v2.processing == "standard"]
    v1p = V1 / "03_labelled.csv"
    v1 = pd.read_csv(v1p); v1 = v1[v1.processing == "standard"]
    wells = [w for w in ["24_9-3", "24_9-4", "34_4-6", "34_4-7", "34_7-1", "34_7-4",
                         "34_7-9", "34_7-10", "34_7-6", "34_8-3", "34_8-3_A"]]
    fig, ax = plt.subplots(figsize=(170 * MM, 60 * MM))
    x = np.arange(len(wells))
    for off, d, a, lbl in ((-0.2, v1, 0.45, "v1"), (0.2, v2, 0.95, "v2")):
        s = [int(((d.well == w) & (d.label == "sand")).sum()) for w in wells]
        c = [int(((d.well == w) & (d.label == "clay")).sum()) for w in wells]
        ax.bar(x + off, s, 0.38, color="#E67E22", alpha=a, label=f"{lbl} sand")
        ax.bar(x + off, c, 0.38, bottom=s, color="#7F8C8D", alpha=a, label=f"{lbl} clay")
    ax.set_xticks(x)
    ax.set_xticklabels([w.replace("_", "/").replace("/A", " A") for w in wells], rotation=45, fontsize=7)
    ax.set_ylabel("labelled depths")
    ax.legend(fontsize=6.5, ncol=4, frameon=False)
    ax.set_title("Labelled depths per well: v1 (5 wells, cross-run anchors) vs v2 "
                 "(11 wells, one zone = one open-hole run)", fontsize=7, loc="left")
    save(fig, "v2_fig4_labels")


def main():
    m = sys.argv[1] if len(sys.argv) > 1 else "E2"
    tab = pd.read_csv(R / "per_well.csv")
    pred = pd.read_csv(R / "predictions.csv")
    summ = json.load(open(R / "summary.json"))
    fig1(tab, summ)
    fig1(tab, summ, subset="tertiary", tag="_tertiary")
    fig2(pred)
    fig2(pred, raw="D1", fix="D2")
    for mm in dict.fromkeys([m, "E2", "D1"]):
        fig3(pred, mm)
    fig4()


if __name__ == "__main__":
    main()
