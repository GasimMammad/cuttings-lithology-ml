"""
v2 EVALUATION -- implements V2_PLAN.md exactly (written before any v2 fit).

Leave-one-well-out over the 10 labelled wells, depth-level, six models:
  E1  engineered 15, raw                           (v1 eng_full on v2 labels)
  E2  engineered 15, label-free per-well z         PRIMARY
  E3  engineered 9 (no colour), per-well z
  D1  ResNet-50 RGB embeddings, raw, PCA32
  D2  ResNet-50 RGB embeddings, per-well z, PCA32
  D3  ResNet-50 greyscale embeddings, per-well z, PCA32
Per-well z = z-score of each input column within its well over ALL W_1
photographs of that well. No labels are used in that step.

Primary endpoint: per-well ROC AUC on held-out wells with >=3 sand and >=3
clay; one-sided Wilcoxon signed-rank against 0.5.

Outputs (WORK_DIR/v2_results/):
  per_well.csv       one row per model x held-out well (AUC, counts, BA...)
  predictions.csv    p(sand) for EVERY depth of every held-out well
  summary.json       primary test, secondary tests (Holm), pooled metrics,
                     Tertiary-only, within-zone, leakage, regression
  report.txt         the same, human-readable

Run:  python 29_v2_evaluate.py
"""
import json
import math

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr, wilcoxon
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import config as C
from features import COLOUR_FREE_NAMES, FEATURE_NAMES

OUT = C.WORK_DIR / "v2_results"
EMB = C.WORK_DIR / "embeddings"
IN_ZONE = ["sand", "clay", "mixed", "unstable"]
JURASSIC_ZONES = {"etive", "dunlin", "statfjord", "heather_tarbert", "drake"}
ELIG_MIN = 3
RNG = np.random.default_rng(42)


# =============================================================================
# data
# =============================================================================
def load_tables():
    """Depth-level tables keyed by (well, depth_m), one per input type."""
    meta = pd.read_csv(EMB / "meta.csv")
    rgb = np.load(EMB / "resnet50_rgb.npy")
    gray = np.load(EMB / "resnet50_gray.npy")

    f = pd.read_csv(C.WORK_DIR / "28_features.csv")
    eng = (f.groupby(["well", "depth_m"], as_index=False)[FEATURE_NAMES].median())
    ref = (f[f.tile == "r1c1"].groupby(["well", "depth_m"], as_index=False)[FEATURE_NAMES].first()
           .rename(columns={c: "ref_" + c for c in FEATURE_NAMES}))
    eng = eng.merge(ref, on=["well", "depth_m"], how="left")
    base = meta.merge(eng, on=["well", "depth_m"], how="left")

    p = pd.read_csv(C.PATCHES_CSV, usecols=["well", "depth_m", "ba_ppm", "formation"])
    p = p.groupby(["well", "depth_m"], as_index=False).first()
    base = base.merge(p, on=["well", "depth_m"], how="left")
    base["zone_name"] = base.zone_name.fillna("")
    base["jurassic"] = base.zone_name.isin(JURASSIC_ZONES)
    assert len(base) == len(rgb) == len(gray)
    return base, {"rgb": rgb, "gray": gray}


def per_well_z(X, wells, ref=None):
    """Label-free: z-score each column within its well over all photos.
    `ref` (same shape as X) supplies the values the well mean/SD are taken
    from; default X itself. For the engineered features ref = tile r1c1 of
    every photo, so every photo of a well contributes the same one-tile
    measurement (not every out-of-zone photo has all 16 tiles computed)."""
    ref = X if ref is None else ref
    Z = np.empty_like(X, dtype=np.float64)
    for w in np.unique(wells):
        m = wells == w
        mu = np.nanmean(ref[m], axis=0)
        sd = np.nanstd(ref[m], axis=0)
        sd[sd < 1e-9] = 1.0
        Z[m] = (X[m] - mu) / sd
    return Z


def build_inputs(base, emb):
    wells = base.well.values
    E15 = base[FEATURE_NAMES].values.astype(float)
    E9 = base[COLOUR_FREE_NAMES].values.astype(float)
    R15 = base[["ref_" + c for c in FEATURE_NAMES]].values.astype(float)
    R9 = base[["ref_" + c for c in COLOUR_FREE_NAMES]].values.astype(float)
    return {
        "E1": (E15, False),
        "E2": (per_well_z(E15, wells, R15), False),
        "E3": (per_well_z(E9, wells, R9), False),
        "D1": (emb["rgb"].astype(float), True),
        "D2": (per_well_z(emb["rgb"].astype(float), wells), True),
        "D3": (per_well_z(emb["gray"].astype(float), wells), True),
    }


# =============================================================================
# metrics
# =============================================================================
def auc(y, s):
    y = np.asarray(y, bool); s = np.asarray(s, float)
    n1, n0 = y.sum(), (~y).sum()
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = rankdata(s)
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def wilson(k, n, z=1.96):
    if n == 0:
        return [float("nan"), float("nan")]
    p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [max(0.0, c - h), min(1.0, c + h)]


def cls_metrics(y, p):
    y = np.asarray(y, bool); pr = np.asarray(p) > 0.5
    tp, fn = int((pr & y).sum()), int((~pr & y).sum())
    tn, fp = int((~pr & ~y).sum()), int((pr & ~y).sum())
    rec = tp / (tp + fn) if tp + fn else float("nan")
    spec = tn / (tn + fp) if tn + fp else float("nan")
    return {"tp": tp, "fn": fn, "tn": tn, "fp": fp,
            "sand_recall": rec, "clay_recall": spec,
            "balanced_acc": (rec + spec) / 2 if tp + fn and tn + fp else float("nan"),
            "sand_precision": tp / (tp + fp) if tp + fp else float("nan")}


def boot_mean_ci(v, n=10000):
    v = np.asarray(v, float)
    bs = RNG.choice(v, (n, len(v))).mean(axis=1)
    return [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def holm(pvals):
    names = list(pvals); ps = np.array([pvals[k] for k in names])
    order = np.argsort(ps); adj = np.empty(len(ps)); run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (len(ps) - rank) * ps[i]); adj[i] = min(1.0, run)
    return dict(zip(names, adj.tolist()))


# =============================================================================
# model fitting
# =============================================================================
def make_clf(use_pca):
    steps = [StandardScaler()]
    if use_pca:
        steps.append(PCA(n_components=32, random_state=0))
    steps.append(LogisticRegression(C=1.0, max_iter=5000, class_weight="balanced"))
    return make_pipeline(*steps)


def lowo(base, X, use_pca, train_mask, label_col="label", shuffle=False):
    """Leave-one-well-out. Returns p(sand) for every row of base (NaN for
    rows whose well was never held out)."""
    wells = base.well.values
    lab = base[label_col].values
    ok = np.isfinite(X).all(axis=1)
    p_all = np.full(len(base), np.nan)
    test_wells = sorted(base.loc[base.label.isin(["sand", "clay"]) & train_mask, "well"].unique())
    for w in test_wells:
        tr = (wells != w) & np.isin(lab, ["sand", "clay"]) & train_mask & ok
        y = lab[tr] == "sand"
        if shuffle:
            y = y.copy()
            for ww in np.unique(wells[tr]):          # permute within well
                m = wells[tr] == ww
                y[m] = RNG.permutation(y[m])
        clf = make_clf(use_pca)
        if use_pca:
            # PCA fitted inside the pipeline on training rows only
            pass
        clf.fit(X[tr], y)
        te = (wells == w) & ok
        if te.any():
            p_all[te] = clf.predict_proba(X[te])[:, 1]
    return p_all, test_wells


def per_well_table(base, p, mask, model, extra=""):
    rows = []
    for w, g in base[mask & base.label.isin(["sand", "clay"])].groupby("well"):
        pw = p[g.index]
        if np.isnan(pw).all():
            continue
        y = (g.label == "sand").values
        m = cls_metrics(y, pw)
        rows.append({"model": model, "subset": extra, "well": w,
                     "n_sand": int(y.sum()), "n_clay": int((~y).sum()),
                     "auc": auc(y, pw), **m})
    return pd.DataFrame(rows)


def primary_stats(tab):
    el = tab[(tab.n_sand >= ELIG_MIN) & (tab.n_clay >= ELIG_MIN)]
    a = el.auc.values
    if len(a) < 2:
        return {"n_wells": int(len(a))}
    st = wilcoxon(a - 0.5, alternative="greater")
    return {"n_wells": int(len(a)), "wells": el.well.tolist(),
            "auc": dict(zip(el.well, np.round(a, 3).tolist())),
            "median_auc": float(np.median(a)), "mean_auc": float(np.mean(a)),
            "mean_auc_ci95": boot_mean_ci(a),
            "n_above_0p5": int((a > 0.5).sum()),
            "wilcoxon_p_one_sided": float(st.pvalue)}


def pooled(tab):
    tp, fn, tn, fp = (int(tab[c].sum()) for c in ("tp", "fn", "tn", "fp"))
    rec, spec = tp / (tp + fn), tn / (tn + fp)
    return {"sand_recall": rec, "sand_recall_ci95": wilson(tp, tp + fn),
            "clay_recall": spec, "clay_recall_ci95": wilson(tn, tn + fp),
            "balanced_acc": (rec + spec) / 2,
            "sand_precision": tp / (tp + fp) if tp + fp else float("nan"),
            "sand_precision_ci95": wilson(tp, tp + fp),
            "confusion": {"tp": tp, "fn": fn, "tn": tn, "fp": fp}}


# =============================================================================
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    base, emb = load_tables()
    inputs = build_inputs(base, emb)
    labelled = base.label.isin(["sand", "clay"])
    print(f"{len(base):,} depths; labelled: "
          f"{base[labelled].groupby('label').size().to_dict()}", flush=True)

    all_mask = np.ones(len(base), bool)
    tert_mask = ~base.jurassic.values
    summary = {"primary_model": "E2", "models": {}}
    tabs, preds = [], base[["well", "depth_m", "label", "vsh", "gr", "zone_name",
                            "jurassic", "ba_ppm"]].copy()

    for name, (X, use_pca) in inputs.items():
        p, _ = lowo(base, X, use_pca, all_mask)
        preds[f"p_{name}"] = p
        t_all = per_well_table(base, p, all_mask, name, "all")
        # Tertiary-only: train AND test without the Jurassic zones
        pt, _ = lowo(base, X, use_pca, tert_mask)
        preds[f"p_{name}_tertiary"] = pt
        t_ter = per_well_table(base, pt, tert_mask, name, "tertiary")
        tabs += [t_all, t_ter]

        res = {"primary_stats_all": primary_stats(t_all),
               "primary_stats_tertiary": primary_stats(t_ter),
               "pooled_all": pooled(t_all), "pooled_tertiary": pooled(t_ter)}

        # within-zone AUC (sand and clay from the same zone)
        wz = []
        lab_df = base[labelled].copy(); lab_df["p"] = p[lab_df.index]
        for (w, z), g in lab_df.groupby(["well", "zone_name"]):
            y = (g.label == "sand").values
            if y.sum() >= ELIG_MIN and (~y).sum() >= ELIG_MIN:
                wz.append({"well": w, "zone": z, "n_sand": int(y.sum()),
                           "n_clay": int((~y).sum()), "auc": auc(y, g.p.values)})
        res["within_zone"] = wz

        # leakage checks, within clay only
        clay = lab_df[lab_df.label == "clay"]
        okb = clay.ba_ppm.notna()
        res["leak_rho_ba_within_clay"] = (float(spearmanr(clay.p[okb], clay.ba_ppm[okb])[0])
                                          if okb.sum() > 10 else None)
        res["leak_rho_depth_within_clay"] = float(spearmanr(clay.p, clay.depth_m)[0])
        summary["models"][name] = res
        ps = res["primary_stats_all"]
        print(f"  {name}: median AUC {ps.get('median_auc', float('nan')):.3f}  "
              f"mean {ps.get('mean_auc', float('nan')):.3f}  "
              f"{ps.get('n_above_0p5')}/{ps.get('n_wells')} wells > 0.5  "
              f"Wilcoxon p {ps.get('wilcoxon_p_one_sided', float('nan')):.4f}  | "
              f"Tertiary median {res['primary_stats_tertiary'].get('median_auc', float('nan')):.3f}",
              flush=True)

    # ---- depth-only baseline (sign chosen on training wells) ----
    rows = []
    lab_df = base[labelled]
    for w in sorted(lab_df.well.unique()):
        tr, te = lab_df[lab_df.well != w], lab_df[lab_df.well == w]
        sign = np.sign(spearmanr(tr.depth_m, tr.label == "sand")[0]) or 1.0
        rows.append({"model": "DEPTH_ONLY", "subset": "all", "well": w,
                     "n_sand": int((te.label == "sand").sum()),
                     "n_clay": int((te.label == "clay").sum()),
                     "auc": auc(te.label == "sand", sign * te.depth_m.values)})
    t_depth = pd.DataFrame(rows); tabs.append(t_depth)
    summary["depth_only_baseline"] = primary_stats(t_depth)

    # ---- secondary tests, Holm ----
    sec = {k: summary["models"][k]["primary_stats_all"]["wilcoxon_p_one_sided"]
           for k in ["E1", "E3", "D1", "D2", "D3"]}
    summary["secondary_holm_adjusted_p"] = holm(sec)

    # ---- permutation null for the primary model (labels shuffled within
    #      each training well, 200 repeats) ----
    X, use_pca = inputs["E2"]
    obs = summary["models"]["E2"]["primary_stats_all"]["mean_auc"]
    null = []
    for k in range(200):
        pn, _ = lowo(base, X, use_pca, all_mask, shuffle=True)
        tn_ = per_well_table(base, pn, all_mask, "perm")
        el = tn_[(tn_.n_sand >= ELIG_MIN) & (tn_.n_clay >= ELIG_MIN)]
        null.append(el.auc.mean())
    null = np.array(null)
    summary["E2_permutation"] = {"observed_mean_auc": obs,
                                 "null_mean": float(null.mean()),
                                 "null_p95": float(np.percentile(null, 95)),
                                 "p_value": float((1 + (null >= obs).sum()) / (1 + len(null)))}
    print(f"  E2 permutation p = {summary['E2_permutation']['p_value']:.4f}", flush=True)

    # ---- continuous target: ridge on Vsh over all in-zone depths ----
    reg = {}
    inz = base.label.isin(IN_ZONE).values & np.isfinite(base.vsh.values)
    for name, (X, use_pca) in inputs.items():
        ok = np.isfinite(X).all(axis=1)
        rhos = {}
        for w in sorted(base.loc[inz, "well"].unique()):
            tr = inz & ok & (base.well.values != w)
            te = inz & ok & (base.well.values == w)
            if te.sum() < 10:
                continue
            steps = [StandardScaler()] + ([PCA(32, random_state=0)] if use_pca else []) + [Ridge(alpha=1.0)]
            m = make_pipeline(*steps).fit(X[tr], base.vsh.values[tr])
            rhos[w] = float(spearmanr(m.predict(X[te]), base.vsh.values[te])[0])
        v = np.array(list(rhos.values()))
        # positive rho = predicted Vsh rises with log Vsh (correct direction)
        reg[name] = {"rho_per_well": rhos, "median_rho": float(np.median(v)),
                     "n_positive": int((v > 0).sum()), "n_wells": int(len(v)),
                     "wilcoxon_p_rho_gt_0": float(wilcoxon(v, alternative="greater").pvalue)}
        print(f"  Vsh ridge {name}: median rho {np.median(v):+.3f}  "
              f"({(v > 0).sum()}/{len(v)} wells positive)  "
              f"p {reg[name]['wilcoxon_p_rho_gt_0']:.4f}", flush=True)
    summary["vsh_regression"] = reg

    tab = pd.concat(tabs, ignore_index=True)
    tab.to_csv(OUT / "per_well.csv", index=False)
    preds.to_csv(OUT / "predictions.csv", index=False)
    with open(OUT / "summary.json", "w") as fh:
        json.dump(summary, fh, indent=2, default=float)
    print(f"\nwritten: {OUT}", flush=True)


if __name__ == "__main__":
    main()
