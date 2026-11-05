"""
v3 -- independent re-check of the reviewer's objections to v2 (O1, O6).

For every v2 held-out prediction (and two reference signals) report, per
eligible well:
  auc        ordinary within-well AUC (sand vs clay), as in v2
  local50    AUC over sand-clay PAIRS less than 50 m apart only ("does it
             separate beds, or only intervals?")
Signals:
  E2, E3, D1, D2           v2 leave-one-well-out predictions
  REL_DEPTH                depth within the well, sign learned on the
                           training wells as the mean of per-well AUCs
                           (z-scored per well, as the features)
  QUARTZ_1F                single feature chosen INSIDE each fold: the one of
                           the 15 per-well-z features with the best mean
                           training-well AUC (sign learned there too)
  XRF_SIAL                 cuttings XRF Si/Al of the same bag (no training;
                           reference ceiling: what the cuttings themselves show)

Writes WORK_DIR/v3_results/baselines_per_well.csv and prints a table.

Run:  python 34_v3_baselines.py
"""
from importlib import import_module

import lasio
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

import config as C
from features import FEATURE_NAMES

EV = import_module("29_v2_evaluate")
OUT = C.WORK_DIR / "v3_results"
ELIG = 3


def local_auc(d, p, y, win):
    """Concordance over sand-clay pairs closer than `win` m."""
    s, c = np.flatnonzero(y), np.flatnonzero(~y)
    num = den = 0.0
    for i in s:
        near = c[np.abs(d[c] - d[i]) < win]
        if len(near):
            num += (p[i] > p[near]).sum() + 0.5 * (p[i] == p[near]).sum()
            den += len(near)
    return (num / den if den else np.nan), int(den)


def xrf_sial(base):
    v = np.full(len(base), np.nan)
    for w in base.well.unique():
        f = C.SSD_ROOT / "Wells" / w / "DRILLING" / f"{w}_CUTTINGS_XRF_1.LAS"
        if not f.exists():
            continue
        d = lasio.read(str(f), engine="normal").df()
        r = (d["SI"] / d["AL"]).replace([np.inf, -np.inf], np.nan)
        r.index = np.round(r.index.values.astype(float), 2)
        m = base.well.values == w
        v[m] = r.reindex(np.round(base.depth_m.values[m], 2)).values
    return v


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    base, emb = EV.load_tables()
    inputs = EV.build_inputs(base, emb)
    pred = pd.read_csv(C.WORK_DIR / "v2_results" / "predictions.csv")
    assert (pred.depth_m.values == base.depth_m.values).all()
    wells = base.well.values
    lab = base.label.values
    labelled = np.isin(lab, ["sand", "clay"])
    lab_wells = sorted(set(wells[labelled]))

    # relative depth, z-scored per well
    zdep = EV.per_well_z(base.depth_m.values[:, None].astype(float), wells)[:, 0]
    # per-well-z engineered features (E2 input)
    Z = inputs["E2"][0]

    sig = {k: pred[f"p_{k}"].values for k in ("E2", "E3", "D1", "D2")}
    sig["XRF_SIAL"] = xrf_sial(base)
    rel = np.full(len(base), np.nan)
    one = np.full(len(base), np.nan)
    chosen = {}
    for w in lab_wells:
        trw = [x for x in lab_wells if x != w]
        tr = labelled & np.isin(wells, trw)
        # relative depth: sign from pooled training wells
        # sign from the MEAN of per-well AUCs on the training wells (pooling
        # across wells let deep 24/9-3 and Jurassic sands set the wrong sign)
        a_tr = [EV.auc(lab[labelled & (wells == v)] == "sand", zdep[labelled & (wells == v)]) for v in trw]
        sgn = 1.0 if np.nanmean(a_tr) >= 0.5 else -1.0
        rel[wells == w] = sgn * zdep[wells == w]
        # single feature: best mean training-well AUC, sign learned there
        best = None
        for j, f in enumerate(FEATURE_NAMES):
            a = [EV.auc(lab[labelled & (wells == v)] == "sand", Z[labelled & (wells == v), j])
                 for v in trw]
            a = np.nanmean([x for x in a if np.isfinite(x)])
            s = 1.0 if a >= 0.5 else -1.0
            score = max(a, 1 - a)
            if best is None or score > best[0]:
                best = (score, j, s, f)
        one[wells == w] = best[2] * Z[wells == w, best[1]]
        chosen[w] = best[3]
    sig["REL_DEPTH"] = rel
    sig["ONE_FEATURE"] = one

    rows = []
    for name, p in sig.items():
        for w in lab_wells:
            m = labelled & (wells == w) & np.isfinite(p)
            y = lab[m] == "sand"
            if y.sum() < ELIG or (~y).sum() < ELIG:
                continue
            a = EV.auc(y, p[m])
            l50, npairs = local_auc(base.depth_m.values[m], p[m], y, 50.0)
            rows.append({"signal": name, "well": w, "n_sand": int(y.sum()), "n_clay": int((~y).sum()),
                         "auc": a, "local50": l50, "pairs50": npairs})
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "baselines_per_well.csv", index=False)

    print("single feature chosen per fold:", chosen)
    print(f"\n{'signal':12} {'median AUC':>10} {'n>0.5':>6} {'p':>7} | {'median local50':>14} {'n>0.5':>6} {'pooled local50':>14}")
    for name, g in t.groupby("signal", sort=False):
        a, l = g.auc.values, g.local50.values
        pa = wilcoxon(a - 0.5, alternative="greater").pvalue
        lk = np.isfinite(l)
        pooled = np.nansum(l * g.pairs50.values) / g.pairs50[lk].sum()
        print(f"{name:12} {np.median(a):10.3f} {int((a > .5).sum()):3d}/{len(a)} {pa:7.4f} | "
              f"{np.nanmedian(l):14.3f} {int((l[lk] > .5).sum()):3d}/{lk.sum()} {pooled:14.3f}")
    print("\nper well (auc / local50):")
    print(t.pivot_table(index="well", columns="signal", values=["auc", "local50"]).round(2).to_string())
    # paired comparison vs relative depth
    piv = t.pivot_table(index="well", columns="signal", values="auc")
    lpiv = t.pivot_table(index="well", columns="signal", values="local50")
    for k in ("E2", "D1", "ONE_FEATURE"):
        l = lpiv[k].dropna()
        print(f"{k} local50 vs 0.5: {int((l > .5).sum())}/{len(l)}, Wilcoxon p {wilcoxon(l - 0.5, alternative='greater').pvalue:.3f}")
    for k in ("E2", "D1", "ONE_FEATURE", "XRF_SIAL"):
        dlt = (piv[k] - piv["REL_DEPTH"]).dropna()
        print(f"{k} - REL_DEPTH: median diff {dlt.median():+.3f}, "
              f"{int((dlt > 0).sum())}/{len(dlt)} wells better, Wilcoxon p {wilcoxon(dlt, alternative='greater').pvalue:.3f}")


if __name__ == "__main__":
    main()
