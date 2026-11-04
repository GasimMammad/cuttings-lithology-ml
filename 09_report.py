"""
FINAL DELIVERABLES from 08_compare_models.py:
  1. side-by-side table: models x tiers x sand strata (body-interior vs
     interval; shallow vs deep)
  2. leakage plots (Ba and depth) for every model
  3. engineered-model coefficients AND block ablation
  4. tier-1 reported as (a) recall-only across bodies, (b) full metrics for
     bodies with clay within +/-100 m, (c) explicit statement for the rest

All stratified numbers use POOLED TIER-2 HELD-OUT predictions: every well is
predicted only by the fold that held that well out (methodology rule 3).
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import config as C
from features import FEATURE_BLOCKS, FEATURE_NAMES

OUT = C.WORK_DIR / "final_comparison"
MODELS = ["cnn_colour", "cnn_gray", "eng_full", "eng_nocolour"]
NICE = {"cnn_colour": "CNN colour", "cnn_gray": "CNN greyscale",
        "eng_full": "Engineered 15", "eng_nocolour": "Engineered no-colour"}


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def recall_str(sub):
    s = sub[sub.label == "sand"]
    k, n = int((s.pred_label == "sand").sum()), len(s)
    if n == 0:
        return "n/a"
    lo, hi = wilson(k, n)
    return f"{k}/{n}={k/n:.2f} [{lo:.2f}-{hi:.2f}]"


def main():
    res = json.load(open(OUT / "results.json"))
    P = pd.read_csv(OUT / "all_predictions.csv")
    t2 = P[P.tier == "tier2"]
    lines = []
    def w(s=""):
        print(s, flush=True)
        lines.append(s)

    # ---------------- 1. side-by-side ----------------
    w("=" * 112)
    w("TABLE 1 -- THREE-WAY COMPARISON, IDENTICAL FOLDS")
    w("  Depth-level metrics; the 16 patches of a photo aggregated by MEDIAN.")
    w("  Overall majority-class baseline (always predict clay) = 81.0%.")
    w("  CAPTION -- FOLD COUNT: tier 2 has FOUR leave-one-well-out folds, but")
    w("  fold 4 (hold out 34_7-1) contains NO SAND LABELS, so balanced accuracy")
    w("  is UNDEFINED there. Every tier-2 mean, SD and confidence interval below")
    w("  therefore rests on THREE folds (24_9-3, 24_9-4, 34_4-6), n=3.")
    w("  95% CI is a t-interval on the fold means (df=2, t=4.303); it is wide")
    w("  by construction at n=3 and is reported to make that width explicit.")
    w("=" * 112)
    hdr = (f"{'model':22} {'bal.acc mean':>13} {'SD':>7} {'95% CI':>18} "
           f"{'sand recall':>22} {'sand precision':>20}")
    w(hdr); w("-" * 112)
    stats = {}
    for m in MODELS:
        folds = res["tier2"][m]
        bals = np.array([v["balanced_acc"] for v in folds.values()
                         if v and np.isfinite(v["balanced_acc"])], dtype=float)
        n_f = len(bals)
        mean, sd = float(bals.mean()), float(bals.std(ddof=1)) if n_f > 1 else float("nan")
        half = 4.303 * sd / math.sqrt(n_f) if n_f > 1 else float("nan")
        lo_ci, hi_ci = mean - half, mean + half
        stats[m] = {"folds": bals, "mean": mean, "sd": sd, "ci": (lo_ci, hi_ci)}
        sub = t2[t2.model == m]
        s = sub[sub.label == "sand"]; c = sub[sub.label == "clay"]
        k, n = int((s.pred_label == "sand").sum()), len(s)
        tp, fp = k, int((c.pred_label == "sand").sum())
        prec = tp / (tp + fp) if (tp + fp) else float("nan")
        plo, phi = wilson(tp, tp + fp) if (tp + fp) else (float("nan"),) * 2
        rlo, rhi = wilson(k, n)
        w(f"{NICE[m]:22} {mean:13.3f} {sd:7.3f} [{lo_ci:6.3f}, {hi_ci:6.3f}] "
          f"{k:>4}/{n:<4}={k/n:.2f} [{rlo:.2f}-{rhi:.2f}] "
          f"{prec:9.2f} [{plo:.2f}-{phi:.2f}]")
    w()
    w("  per-fold balanced accuracy (and each fold's own majority baseline):")
    for m in MODELS:
        row = f"    {NICE[m]:22}"
        for fold, v in res["tier2"][m].items():
            if not v:
                continue
            wl = fold.replace("tier2_holdout_", "")
            b = v["balanced_acc"]
            row += (f" {wl}:{'n/a' if not np.isfinite(b) else f'{b:.3f}'}"
                    f"(b{v['majority_baseline']:.2f})")
        w(row)

    # ---- headline finding, stated only if the data support it ----
    all_contain_half = all(
        np.isfinite(v["ci"][0]) and v["ci"][0] <= 0.50 <= v["ci"][1]
        for v in stats.values())
    M = np.vstack([stats[m]["folds"] for m in MODELS])      # models x folds
    fold_spread = float(np.mean(M.std(axis=0, ddof=1)))      # across models, per fold
    model_spread = float(np.mean(M.std(axis=1, ddof=1)))     # across folds, per model
    w()
    w("-" * 112)
    w("HEADLINE FINDING")
    w("-" * 112)
    if all_contain_half:
        w("  Every model's 95% confidence interval for mean balanced accuracy")
        w("  CONTAINS 0.50. No model is distinguishable from chance, and no model")
        w("  is distinguishable from any other. The models are therefore NOT")
        w("  ranked here, none is described as best performing, and no winner is")
        w("  reported -- none of those statements would be supported by the data.")
    else:
        inside = [NICE[m] for m, v in stats.items()
                  if np.isfinite(v["ci"][0]) and v["ci"][0] <= 0.50 <= v["ci"][1]]
        w(f"  CIs containing 0.50: {inside if inside else 'none'}.")
        w("  Models are still NOT ranked: at n=3 folds the intervals overlap one")
        w("  another, so between-model differences are not resolvable.")
    ratio = model_spread / fold_spread
    w()
    w(f"  Spread ACROSS FOLDS (mean SD over folds, within a model): {model_spread:.3f}")
    w(f"  Spread ACROSS MODELS (mean SD over models, within a fold): {fold_spread:.3f}")
    w(f"  ratio = {ratio:.2f}x")
    if ratio >= 2.0:
        w(f"  Fold-to-fold spread is about {ratio:.0f}x the model-to-model spread:")
        w("  WHICH WELL YOU HOLD OUT MATTERS MORE THAN WHICH METHOD YOU USE.")
    else:
        w("  Fold-to-fold spread is COMPARABLE TO, and only marginally larger")
        w(f"  than, model-to-model spread ({ratio:.2f}x). The two sources of")
        w("  variation are of the same order: changing the held-out well moves")
        w("  the result about as much as changing the method entirely. Combined")
        w("  with every CI containing 0.50, the honest reading is that NEITHER")
        w("  choice is resolvable at this sample size -- not that one dominates.")
        w("  NOTE: an earlier working estimate put this ratio near 3x; the")
        w("  measured value is lower and the smaller figure is the correct one.")

    # ---------------- 2. strata ----------------
    w()
    w("=" * 108)
    w("TABLE 2 -- SAND STRATA (pooled tier-2 held-out predictions)")
    w("  A2 body-interior = sand-labelled depth inside a mapped sand body;")
    w("     interval = Vsh-labelled sand BETWEEN mapped bodies (the impure subset)")
    w("  A3 shallow < 700 m, deep >= 700 m")
    w("=" * 108)
    w(f"{'model':22} {'body-interior':>26} {'interval':>26} {'shallow':>26} {'deep':>26}")
    w("-" * 108)
    for m in MODELS:
        sub = t2[t2.model == m]
        w(f"{NICE[m]:22} {recall_str(sub[sub.in_body]):>26} "
          f"{recall_str(sub[~sub.in_body]):>26} "
          f"{recall_str(sub[sub.depth_class=='shallow']):>26} "
          f"{recall_str(sub[sub.depth_class=='deep']):>26}")

    # ---------------- 3. tier 1 ----------------
    w()
    w("=" * 108)
    w("TABLE 3 -- TIER 1, within 24_9-3 (depth generalisation)")
    w("  (a) RECALL ONLY. This is NOT accuracy and must never be quoted as such:")
    w("      most test windows contain no labelled clay, so precision is")
    w("      undefined or trivially 1.00 for those bodies.")
    w("=" * 108)
    bi = {b["i"]: b for b in res["body_info"]}
    folds = list(res["tier1"][MODELS[0]].keys())
    w(f"{'body (depth span)':28} {'n sand':>7} {'clay<=100m':>11} " +
      " ".join(f"{NICE[m]:>16}" for m in MODELS) + "   <- RECALL ONLY")
    w("-" * 108)
    for i, fold in enumerate(folds):
        info = bi.get(i, {})
        cells = []
        for m in MODELS:
            v = res["tier1"][m][fold]
            cells.append(f"{v['confusion']['tp_sand']}/{v['n_sand']}")
        span = fold.split("_", 2)[-1]
        w(f"{span:28} {info.get('n_sand',0):>7} {info.get('clay_within_100m',0):>11} " +
          " ".join(f"{c:>16}" for c in cells))
    w()
    t1b = res.get("tier1b", {})
    b_folds = sorted({fd for m in t1b for fd in t1b[m]}) if t1b else []
    w(f"  (b) FULL METRICS -- the {len(b_folds)} bodies with labelled clay within")
    w("      +/-100 m, tested against THAT DEPTH-LOCAL CLAY (test = body sand +")
    w("      nearby clay; training excludes the whole window plus a 10 m gap).")
    w("      This is the only clean tier-1 evidence.")
    w(f"      CAVEAT: n={len(b_folds)} bodies. INDICATIVE AT BEST. No mean is computed")
    w("      across them -- averaging two bodies would present a spread of two")
    w("      numbers as if it were an estimate. Each body is reported alone.")
    if b_folds:
        w()
        w(f"{'body':26} {'model':22} {'bal.acc':>8} {'base':>6} {'sand recall':>18} "
          f"{'clay recall':>12}")
        for fold in b_folds:
            for m in MODELS:
                v = t1b.get(m, {}).get(fold)
                if not v:
                    continue
                b = v["balanced_acc"]
                lo, hi = v["sand_recall_ci95"]
                w(f"{fold.split('_',1)[-1]:26} {NICE[m]:22} "
                  f"{'n/a' if not np.isfinite(b) else f'{b:.3f}':>8} "
                  f"{v['majority_baseline']:6.2f} "
                  f"{v['confusion']['tp_sand']}/{v['n_sand']} [{lo:.2f}-{hi:.2f}]".rjust(18)
                  + f" {v['clay_recall']:12.2f}")
    else:
        w("      NOT AVAILABLE -- run 10_tier1_balanced.py to generate.")
    w()
    w("  (c) The remaining bodies cannot be evaluated for precision or balanced")
    w("      accuracy. 24_9-3's clay labels cluster at 240-260 m and below")
    w("      2065 m because that is where lithologies are clean enough to label")
    w("      confidently -- this is the stratigraphy of the well, not a design")
    w("      flaw. Building precision from clay 800 m away would let the model")
    w("      separate on burial, consolidation and barite loading rather than")
    w("      lithology, which is exactly what tier 1 exists to exclude.")

    # ---------------- 4. ablation + coefficients ----------------
    w()
    w("=" * 108)
    w("TABLE 4 -- BLOCK ABLATION (engineered model, tier-2 mean balanced accuracy)")
    w("  85 sand events / 15 features = 5.7 events per variable, so individual")
    w("  L2-shrunk coefficients are unstable; the ablation is the robust read.")
    w("=" * 108)
    full = [v["balanced_acc"] for v in res["tier2"]["eng_full"].values()
            if v and np.isfinite(v["balanced_acc"])]
    w(f"  {'all 15 features':28} {np.mean(full):.3f}")
    for tag, folds_d in res["ablation"].items():
        vals = [v["balanced_acc"] for v in folds_d.values()
                if v and np.isfinite(v["balanced_acc"])]
        blk = tag.replace("minus_", "")
        w(f"  {'without ' + blk:28} {np.mean(vals):.3f}   "
          f"change {np.mean(vals)-np.mean(full):+.3f}")

    w()
    w("  Coefficients (standardised, tier-2 fold holding out 24_9-3; sign = towards SAND).")
    w("  Reported for completeness only -- at 5.7 events per variable these are")
    w("  unstable and must not be interpreted individually; cite the ablation.")
    ck = next(iter(res["coefs"]))
    co = res["coefs"][ck]
    for blk, feats in FEATURE_BLOCKS.items():
        for ft in feats:
            if ft in co:
                w(f"    {blk:11} {ft:24} {co[ft]:+.3f}")

    # ---- the colour reversal, as a QUALITATIVE pattern only ----
    cc = stats["cnn_colour"]["mean"]; cg = stats["cnn_gray"]["mean"]
    ef = stats["eng_full"]["mean"]; en = stats["eng_nocolour"]["mean"]
    w()
    w("-" * 112)
    w("THE COLOUR REVERSAL -- QUALITATIVE PATTERN, NOT A MEASURED EFFECT SIZE")
    w("-" * 112)
    w(f"  removing colour from the CNN:        {cc:.3f} -> {cg:.3f}  ({cg-cc:+.3f})")
    w(f"  removing colour from the engineered: {ef:.3f} -> {en:.3f}  ({en-ef:+.3f})")
    w("  The two changes go in OPPOSITE directions. Neither change is")
    w("  individually significant at n=3 folds, and the differences above must")
    w("  NOT be quoted as effect sizes. The reversal is reported as a")
    w("  qualitative pattern only, consistent with the amendment-3 instrument")
    w("  check, where lab_b_mean (3.45 IQR) out-separated every free-grain")
    w("  feature on the two photographs inspected at full resolution.")

    # ---------------- 5. leakage ----------------
    w()
    w("=" * 108)
    w("TABLE 5 -- LEAKAGE CHECKS, ALL MODELS (held-out tier-2 predictions)")
    w("  rho(p_sand, Ba) computed WITHIN CLAY-LABELLED DEPTHS ONLY, i.e. at")
    w("  fixed lithology: any correlation there is the model reading mud.")
    w("=" * 108)
    w(f"{'model':22} " + " ".join(f"{w_:>16}" for w_ in sorted(t2.well.unique())))
    w("-" * 108)
    for m in MODELS:
        row = f"{NICE[m]:22}"
        for well in sorted(t2.well.unique()):
            s = t2[(t2.model == m) & (t2.well == well) & (t2.label == "clay")]
            if len(s) > 8 and s.ba_ppm.notna().sum() > 8:
                r = spearmanr(s.p_sand, s.ba_ppm, nan_policy="omit").statistic
                row += f"{r:>16.2f}"
            else:
                row += f"{'n/a':>16}"
        w(row)

    fig, axes = plt.subplots(2, len(MODELS), figsize=(5 * len(MODELS), 9))
    cols = dict(zip(sorted(t2.well.unique()),
                    ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]))
    for j, m in enumerate(MODELS):
        for i, (xcol, xlab, logx) in enumerate(
                [("ba_ppm", "Ba (ppm, XRF)", True), ("depth_m", "depth (m)", False)]):
            ax = axes[i, j]
            sub = t2[t2.model == m]
            for well, g in sub.groupby("well"):
                ax.scatter(g[xcol], g.p_sand, s=12, alpha=.5, edgecolors="none",
                           color=cols[well], label=well if i == 0 and j == 0 else None)
            if logx:
                ax.set_xscale("log")
            ax.set_xlabel(xlab)
            ax.set_ylabel("held-out p_sand" if j == 0 else "")
            ax.set_title(NICE[m] if i == 0 else "", fontweight="bold")
            ax.grid(alpha=.3)
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("Leakage checks, all models: predicted sand probability vs "
                 "barite and depth", fontweight="bold")
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / "09_leakage_all_models.png", dpi=140)
    w(f"\nfigure: {C.FIG_DIR / '09_leakage_all_models.png'}")

    (OUT / "final_report.txt").write_text("\n".join(lines))
    print(f"written: {OUT / 'final_report.txt'}")


if __name__ == "__main__":
    main()
