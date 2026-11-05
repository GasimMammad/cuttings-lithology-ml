"""
v3 PRE-REGISTERED TEST (V3_PLAN.md section 3): do photo-based sand signals
agree with cuttings XRF Si/Al in the UNLABELLED Tertiary overburden?

Depths: W_1 photos labelled excluded_zone or no_log, above top Shetland Gp.
Signals, all from models that never saw the well: ONE_FEATURE (primary), D1, E2.
Both series high-passed within continuous stretches (minus centred running
median over +/-50 m); per-well Spearman; one-sided Wilcoxon across wells.

Run:  python 35_v3_xrf_shallow.py
"""
from importlib import import_module

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon

import config as C
from features import FEATURE_NAMES

EV = import_module("29_v2_evaluate")
BL = import_module("34_v3_baselines")
OUT = C.WORK_DIR / "v3_results"

# top of the Shetland Gp / first Cretaceous unit, NPD tops (Wells/files);
# 24/9-4 tops stop in the Lista Fm, so its whole photographed section is Tertiary
TOP_SHETLAND = {"24_9-3": 2836, "24_9-4": 9999, "34_4-6": 1775, "34_4-7": 1824,
                "34_7-1": 1823, "34_7-4": 1848, "34_7-9": 1807, "34_7-10": 1863,
                "34_7-6": 1846, "34_8-3": 2012, "34_8-3_A": 2088}
MIN_N = 30


def highpass(d, v, half=50.0, gap=30.0):
    out = np.full(len(v), np.nan)
    o = np.argsort(d)
    d, v = d[o], v[o]
    brk = np.r_[0, np.flatnonzero(np.diff(d) > gap) + 1, len(d)]
    hp = np.full(len(v), np.nan)
    for a, b in zip(brk[:-1], brk[1:]):
        for k in range(a, b):
            m = (d[a:b] >= d[k] - half) & (d[a:b] <= d[k] + half)
            hp[k] = v[k] - np.median(v[a:b][m])
    out[o] = hp
    return out


def main():
    base, emb = EV.load_tables()
    inputs = EV.build_inputs(base, emb)
    pred = pd.read_csv(C.WORK_DIR / "v2_results" / "predictions.csv")
    wells = base.well.values
    lab = base.label.values
    labelled = np.isin(lab, ["sand", "clay"])
    lab_wells = sorted(set(wells[labelled]))
    Z = inputs["E2"][0]
    sial = BL.xrf_sial(base)

    sig = {"D1": pred.p_D1.values.copy(), "E2": pred.p_E2.values.copy()}
    one = np.full(len(base), np.nan)
    for w in lab_wells + ["34_7-1"]:
        trw = [x for x in lab_wells if x != w]
        best = None
        for j in range(len(FEATURE_NAMES)):
            a = [EV.auc(lab[labelled & (wells == v)] == "sand", Z[labelled & (wells == v), j]) for v in trw]
            a = np.nanmean([x for x in a if np.isfinite(x)])
            if best is None or max(a, 1 - a) > best[0]:
                best = (max(a, 1 - a), j, 1.0 if a >= 0.5 else -1.0)
        one[wells == w] = best[2] * Z[wells == w, best[1]]
    sig["ONE_FEATURE"] = one
    # 34/7-1 for the trained models: fit on all 10 labelled wells
    for name in ("D1", "E2"):
        X, use_pca = inputs[name]
        ok = np.isfinite(X).all(axis=1)
        tr = labelled & ok
        clf = EV.make_clf(use_pca).fit(X[tr], lab[tr] == "sand")
        m = (wells == "34_7-1") & ok
        sig[name][m] = clf.predict_proba(X[m])[:, 1]

    sel = np.isin(lab, ["excluded_zone", "no_log"]) & np.isfinite(sial)
    sel &= base.depth_m.values < np.array([TOP_SHETLAND[w] for w in wells])
    rows = []
    for w in sorted(set(wells[sel])):
        m = sel & (wells == w)
        d = base.depth_m.values[m]
        x = highpass(d, sial[m])
        for name, p in sig.items():
            y = highpass(d, p[m])
            ok = np.isfinite(x) & np.isfinite(y)
            if ok.sum() < MIN_N:
                continue
            r = spearmanr(y[ok], x[ok])[0]
            rows.append({"signal": name, "well": w, "n": int(ok.sum()),
                         "depth_range": f"{d.min():.0f}-{d.max():.0f}", "rho": r})
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "xrf_shallow.csv", index=False)
    print(t.pivot_table(index=["well"], columns="signal", values="rho").round(3).to_string())
    print(t[t.signal == "ONE_FEATURE"][["well", "n", "depth_range"]].to_string(index=False))
    for name, g in t.groupby("signal"):
        r = g.rho.values
        p = wilcoxon(r, alternative="greater").pvalue
        print(f"{name:12} median rho {np.median(r):+.3f}  {int((r > 0).sum())}/{len(r)} wells > 0  Wilcoxon p {p:.4f}")


if __name__ == "__main__":
    main()
