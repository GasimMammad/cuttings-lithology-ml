"""
v2 REPORT -- human-readable summary of 29_v2_evaluate.py (+ 31_v2_cnn.py if run).

Writes WORK_DIR/v2_results/report.txt and prints it.

Run:  python 32_v2_report.py
"""
import json

import numpy as np
import pandas as pd
from scipy.stats import rankdata, wilcoxon

import config as C

R = C.WORK_DIR / "v2_results"
ORDER = ["E2", "E1", "E3", "D1", "D2", "D3"]
DESC = {"E1": "engineered 15, raw (v1 recipe)", "E2": "engineered 15, per-well z  [PRIMARY]",
        "E3": "engineered 9 no-colour, per-well z", "D1": "ResNet-50 RGB, raw",
        "D2": "ResNet-50 RGB, per-well z", "D3": "ResNet-50 grey, per-well z",
        "C1": "fine-tuned ResNet-18, v1 recipe (exploratory)",
        "C2": "fine-tuned ResNet-18, per-well colour norm (exploratory)"}


def auc(y, s):
    y = np.asarray(y, bool); r = rankdata(s); n1, n0 = y.sum(), (~y).sum()
    return (r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0) if n1 and n0 else np.nan


def fmt_ps(ps):
    if "median_auc" not in ps:
        return "n/a"
    lo, hi = ps["mean_auc_ci95"]
    return (f"median {ps['median_auc']:.3f} | mean {ps['mean_auc']:.3f} [{lo:.3f}-{hi:.3f}] | "
            f"{ps['n_above_0p5']}/{ps['n_wells']} wells > 0.5 | Wilcoxon p = {ps['wilcoxon_p_one_sided']:.4f}")


def main():
    s = json.load(open(R / "summary.json"))
    tab = pd.read_csv(R / "per_well.csv")
    L = []
    L.append("=" * 100)
    L.append("v2 RESULTS -- leave-one-well-out, 10 labelled wells, depth level")
    L.append("Pre-registered in V2_PLAN.md. Primary: per-well AUC, wells with >=3 sand & >=3 clay.")
    L.append("=" * 100)
    L.append("\nPRIMARY ENDPOINT (all zones)")
    for m in ORDER:
        L.append(f"  {m}  {DESC[m]:40} {fmt_ps(s['models'][m]['primary_stats_all'])}")
    L.append(f"  --  {'depth only (leakage baseline)':40} {fmt_ps(s['depth_only_baseline'])}")
    L.append("\n  Holm-adjusted p (secondary models): " +
             ", ".join(f"{k} {v:.4f}" for k, v in s["secondary_holm_adjusted_p"].items()))
    pm = s["E2_permutation"]
    L.append(f"  E2 permutation test (labels shuffled within training wells, 200x): "
             f"observed mean AUC {pm['observed_mean_auc']:.3f}, null mean {pm['null_mean']:.3f}, "
             f"null 95th pct {pm['null_p95']:.3f}, p = {pm['p_value']:.4f}")

    L.append("\nTERTIARY ONLY (Jurassic zones removed from training and test)")
    for m in ORDER:
        L.append(f"  {m}  {DESC[m]:40} {fmt_ps(s['models'][m]['primary_stats_tertiary'])}")

    L.append("\nPER-WELL AUC (all zones; * = eligible for the primary test)")
    piv = tab[(tab.subset == "all")].pivot_table(index="well", columns="model", values="auc")
    cnt = tab[(tab.subset == "all") & (tab.model == "E2")].set_index("well")[["n_sand", "n_clay"]]
    cols = [c for c in ORDER + ["DEPTH_ONLY"] if c in piv.columns]
    L.append(f"  {'well':10} {'sand':>4} {'clay':>4}  " + " ".join(f"{c:>10}" for c in cols))
    for w in piv.index:
        if w not in cnt.index:
            continue
        ns, nc = cnt.loc[w]
        star = "*" if ns >= 3 and nc >= 3 else " "
        L.append(f" {star}{w:10} {ns:4d} {nc:4d}  " + " ".join(f"{piv.loc[w, c]:10.3f}" for c in cols))

    L.append("\nPOOLED CLASSIFICATION at p = 0.5 (all held-out labelled depths)")
    for m in ORDER:
        p = s["models"][m]["pooled_all"]
        L.append(f"  {m}: balanced acc {p['balanced_acc']:.3f} | sand recall {p['sand_recall']:.2f} "
                 f"[{p['sand_recall_ci95'][0]:.2f}-{p['sand_recall_ci95'][1]:.2f}] | clay recall "
                 f"{p['clay_recall']:.2f} | sand precision {p['sand_precision']:.2f} | {p['confusion']}")

    L.append("\nWITHIN-ZONE AUC (sand and clay from the same label zone)")
    for m in ("E2", "D2"):
        for z in s["models"][m]["within_zone"]:
            L.append(f"  {m} {z['well']:9} {z['zone']:16} sand {z['n_sand']:3d} clay {z['n_clay']:3d}  AUC {z['auc']:.3f}")

    L.append("\nLEAKAGE CHECKS (within clay-labelled depths; |rho| < 0.3 = no flag)")
    for m in ORDER:
        r = s["models"][m]
        b = r["leak_rho_ba_within_clay"]
        L.append(f"  {m}: rho(p, Ba) = {b:+.3f}   rho(p, depth) = {r['leak_rho_depth_within_clay']:+.3f}")

    L.append("\nCONTINUOUS TARGET -- ridge on Vsh, all in-zone depths (sand+clay+mixed+unstable)")
    for m in ORDER:
        g = s["vsh_regression"][m]
        L.append(f"  {m}: median per-well Spearman rho {g['median_rho']:+.3f} | "
                 f"{g['n_positive']}/{g['n_wells']} wells positive | Wilcoxon p {g['wilcoxon_p_rho_gt_0']:.4f}")

    cp = R / "cnn_predictions.csv"
    if cp.exists():
        c = pd.read_csv(cp)
        lab = pd.read_csv(C.LABELS_CSV)
        lab = lab[lab.processing == "standard"][["well", "depth_m", "label"]]
        c = c.merge(lab, on=["well", "depth_m"])
        L.append("\nEXPLORATORY: FINE-TUNED CNN (not in the pre-registered test set)")
        for m, g in c.groupby("model"):
            rows = []
            for w, gw in g[g.label.isin(["sand", "clay"])].groupby("well"):
                y = gw.label == "sand"
                if y.sum() >= 3 and (~y).sum() >= 3:
                    rows.append((w, auc(y.values, gw.p.values)))
            if len(rows) >= 2:
                a = np.array([r[1] for r in rows])
                p = wilcoxon(a - 0.5, alternative="greater").pvalue
                L.append(f"  {m}  {DESC[m]:52} median {np.median(a):.3f} | {int((a > .5).sum())}/{len(a)} "
                         f"> 0.5 | p {p:.4f} | " + ", ".join(f"{w} {x:.2f}" for w, x in rows))
    txt = "\n".join(L)
    (R / "report.txt").write_text(txt)
    print(txt)


if __name__ == "__main__":
    main()
