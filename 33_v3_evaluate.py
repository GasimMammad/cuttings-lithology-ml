"""
v3 EVALUATION (exploratory follow-up; see V3_PLAN.md). Reuses the v2 inputs.

Components, each a switch in a configuration dict:
  model   : "E2" | "D2" | "E2+D2"   (ensemble = mean of within-well ranks)
  smooth  : 0 | 1   running median of p(sand) over +/-1 photo, same zone only,
                    neighbours <= 12 m apart; predictions only, never labels
  soft    : 0 | 1   mixed depths enter training with target
                    t = clip((0.60 - Vsh) / 0.30, 0, 1) (duplicated-row trick)

Two evaluations:
  plain   every configuration, ordinary leave-one-well-out
  nested  per outer held-out well, the configuration with the best mean inner
          AUC (inner leave-one-well-out over the remaining wells) is used

Outputs: WORK_DIR/v3_results/{plain_per_well.csv, nested_per_well.csv,
         nested_choices.csv, v3_predictions.csv, summary.json}

Run:  python 33_v3_evaluate.py
"""
import itertools
import json
from importlib import import_module

import numpy as np
import pandas as pd
from scipy.stats import rankdata, wilcoxon
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import config as C

EV = import_module("29_v2_evaluate")
OUT = C.WORK_DIR / "v3_results"
ELIG = 3
SOFT_LABELS = ["sand", "clay", "mixed"]          # see V3_PLAN.md section C
CONFIGS = [dict(model=m, smooth=s, soft=f) for m, s, f in
           itertools.product(["E2", "D2", "E2+D2"], [0, 1], [0, 1])]


def cfg_name(c):
    return f"{c['model']}|smooth{c['smooth']}|soft{c['soft']}"


def complexity(c):
    return (c["model"] == "E2+D2") + c["smooth"] + c["soft"]


# -----------------------------------------------------------------------------
def fit_predict(base, X, use_pca, train_wells, test_wells, soft):
    """Train on train_wells, return p(sand) for every row of test_wells."""
    wells = base.well.values
    lab = base.label.values
    ok = np.isfinite(X).all(axis=1)
    if soft:
        tr = np.isin(wells, train_wells) & np.isin(lab, SOFT_LABELS) & ok & np.isfinite(base.vsh.values)
        t = np.clip((0.60 - base.vsh.values[tr]) / 0.30, 0, 1)
        t[lab[tr] == "sand"] = 1.0
        t[lab[tr] == "clay"] = 0.0
        Xtr = np.vstack([X[tr], X[tr]])
        y = np.r_[np.ones(tr.sum()), np.zeros(tr.sum())]
        w = np.r_[t, 1 - t]
        w = np.where(y == 1, w / max(w[y == 1].sum(), 1e-9), w / max(w[y == 0].sum(), 1e-9))
        keep = w > 0
        Xtr, y, w = Xtr[keep], y[keep], w[keep] * keep.sum()
    else:
        tr = np.isin(wells, train_wells) & np.isin(lab, ["sand", "clay"]) & ok
        Xtr, y = X[tr], (lab[tr] == "sand").astype(int)
        w = None
    steps = [StandardScaler()] + ([PCA(32, random_state=0)] if use_pca else [])
    steps.append(LogisticRegression(C=1.0, max_iter=5000,
                                    class_weight=None if soft else "balanced"))
    clf = make_pipeline(*steps)
    if w is None:
        clf.fit(Xtr, y)
    else:
        clf.fit(Xtr, y, logisticregression__sample_weight=w)
    te = np.isin(wells, test_wells) & ok
    p = np.full(len(base), np.nan)
    p[te] = clf.predict_proba(X[te])[:, 1]
    return p


def within_well_rank(base, p):
    r = np.full(len(p), np.nan)
    for w in np.unique(base.well.values):
        m = (base.well.values == w) & np.isfinite(p)
        if m.any():
            r[m] = rankdata(p[m]) / m.sum()
    return r


def smooth(base, p):
    """Running median over +/-1 photo within the same zone, gaps <= 12 m."""
    out = p.copy()
    for (w, z), g in base.groupby(["well", "zone_name"]):
        if not z:
            continue
        idx = g.sort_values("depth_m").index.values
        d = base.depth_m.values[idx]
        for k, i in enumerate(idx):
            nb = [i]
            if k > 0 and d[k] - d[k - 1] <= 12:
                nb.append(idx[k - 1])
            if k < len(idx) - 1 and d[k + 1] - d[k] <= 12:
                nb.append(idx[k + 1])
            v = p[nb]
            v = v[np.isfinite(v)]
            if len(v):
                out[i] = np.median(v)
    return out


def predict_cfg(base, inputs, cfg, train_wells, test_wells):
    parts = []
    for m in cfg["model"].split("+"):
        X, use_pca = inputs[m]
        p = fit_predict(base, X, use_pca, train_wells, test_wells, cfg["soft"])
        parts.append(p)
    p = parts[0] if len(parts) == 1 else np.nanmean(
        [within_well_rank(base, q) for q in parts], axis=0)
    if cfg["smooth"]:
        p = smooth(base, p)
    return p


def well_auc(base, p, w):
    m = (base.well.values == w) & base.label.isin(["sand", "clay"]).values & np.isfinite(p)
    y = base.label.values[m] == "sand"
    return EV.auc(y, p[m]), int(y.sum()), int((~y).sum())


def eligible(base, wells):
    out = []
    for w in wells:
        g = base[(base.well == w)]
        if (g.label == "sand").sum() >= ELIG and (g.label == "clay").sum() >= ELIG:
            out.append(w)
    return out


def summarise(rows):
    t = pd.DataFrame(rows)
    el = t[(t.n_sand >= ELIG) & (t.n_clay >= ELIG)]
    a = el.auc.values
    tert = el[~el.well.isin(["34_8-3", "34_8-3_A"])].auc.values
    return {"median_auc": float(np.median(a)), "mean_auc": float(np.mean(a)),
            "n_above": int((a > 0.5).sum()), "n": int(len(a)),
            "wilcoxon_p": float(wilcoxon(a - 0.5, alternative="greater").pvalue),
            "tertiary_median": float(np.median(tert)), "tertiary_n_above": int((tert > 0.5).sum()),
            "tertiary_n": int(len(tert)),
            "auc": dict(zip(el.well, np.round(a, 3).tolist()))}


# -----------------------------------------------------------------------------
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    base, emb = EV.load_tables()
    inputs = EV.build_inputs(base, emb)
    lab_wells = sorted(base[base.label.isin(["sand", "clay"])].well.unique())
    summary = {"configs": {}, "nested": {}}

    # ---------- plain ----------
    plain_rows, preds = [], base[["well", "depth_m", "label", "vsh", "zone_name"]].copy()
    for cfg in CONFIGS:
        name = cfg_name(cfg)
        pall = np.full(len(base), np.nan)
        rows = []
        for w in lab_wells:
            p = predict_cfg(base, inputs, cfg, [x for x in lab_wells if x != w], [w])
            m = base.well.values == w
            pall[m] = p[m]
            a, ns, nc = well_auc(base, p, w)
            rows.append({"config": name, "well": w, "auc": a, "n_sand": ns, "n_clay": nc})
        preds[f"p_{name}"] = pall
        plain_rows += rows
        summary["configs"][name] = summarise(rows)
        s = summary["configs"][name]
        print(f"  plain {name:24} median {s['median_auc']:.3f} mean {s['mean_auc']:.3f} "
              f"{s['n_above']}/{s['n']}  p {s['wilcoxon_p']:.4f} | Tertiary median "
              f"{s['tertiary_median']:.3f} {s['tertiary_n_above']}/{s['tertiary_n']}", flush=True)

    # ---------- nested ----------
    nested_rows, choices = [], []
    pn = np.full(len(base), np.nan)
    for w in lab_wells:
        inner = [x for x in lab_wells if x != w]
        inner_el = eligible(base, inner)
        scores = {}
        for cfg in CONFIGS:
            aucs = []
            for v in inner_el:
                p = predict_cfg(base, inputs, cfg, [x for x in inner if x != v], [v])
                aucs.append(well_auc(base, p, v)[0])
            scores[cfg_name(cfg)] = (float(np.mean(aucs)), -complexity(cfg), cfg)
        best_name, (best_score, _, best_cfg) = max(scores.items(), key=lambda kv: kv[1][:2])
        p = predict_cfg(base, inputs, best_cfg, inner, [w])
        m = base.well.values == w
        pn[m] = p[m]
        a, ns, nc = well_auc(base, p, w)
        nested_rows.append({"well": w, "auc": a, "n_sand": ns, "n_clay": nc, "chosen": best_name})
        choices.append({"outer_well": w, "chosen": best_name, "inner_mean_auc": best_score,
                        **{k: v[0] for k, v in scores.items()}})
        print(f"  nested outer {w:9} chose {best_name:24} (inner {best_score:.3f}) -> AUC {a:.3f}", flush=True)
    preds["p_nested"] = pn
    summary["nested"] = summarise(nested_rows)
    summary["nested"]["choices"] = pd.DataFrame(nested_rows).chosen.value_counts().to_dict()
    s = summary["nested"]
    print(f"\n  NESTED: median {s['median_auc']:.3f} mean {s['mean_auc']:.3f} {s['n_above']}/{s['n']} "
          f"p {s['wilcoxon_p']:.4f} | Tertiary median {s['tertiary_median']:.3f} "
          f"{s['tertiary_n_above']}/{s['tertiary_n']}", flush=True)

    pd.DataFrame(plain_rows).to_csv(OUT / "plain_per_well.csv", index=False)
    pd.DataFrame(nested_rows).to_csv(OUT / "nested_per_well.csv", index=False)
    pd.DataFrame(choices).to_csv(OUT / "nested_choices.csv", index=False)
    preds.to_csv(OUT / "v3_predictions.csv", index=False)
    json.dump(summary, open(OUT / "summary.json", "w"), indent=2, default=float)
    print(f"written: {OUT}")


if __name__ == "__main__":
    main()
