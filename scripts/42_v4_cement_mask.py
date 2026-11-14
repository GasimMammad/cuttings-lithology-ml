"""
v4 B -- robustness of the pre-registered shallow XRF test (35_v3_xrf_shallow.py,
run 2) to shoe-track cement: identical analysis, but photographs 0-15 m
below every 30", 20" and 13 3/8" shoe (Sodir casing table) are removed
before high-passing. Run 2 stays the reported result; this is a check only.

Run:  python 42_v4_cement_mask.py
"""
from importlib import import_module

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon

import config as C
from features import FEATURE_NAMES

EV = import_module("29_v2_evaluate")
BL = import_module("34_v3_baselines")
XS = import_module("35_v3_xrf_shallow")
MASK_M = 15.0


def shoe_mask(base):
    cas = pd.read_csv("results/v3/sodir_casing_table.csv")
    cas["wlbName"] = cas.wlbName.str.strip()
    cas = cas[cas.wlbCasingType.str.strip().isin(["CONDUCTOR", "SURF.COND.", "INTERM."])]
    m = np.zeros(len(base), bool)
    for w in base.well.unique():
        shoes = cas[cas.wlbName == w.replace("_", "/").replace("/A", " A")].wlbCasingDepth.values
        sel = (base.well == w).values
        d = base.depth_m.values
        for s in shoes:
            m |= sel & (d >= s) & (d <= s + MASK_M)
    return m


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
    # signals exactly as in 35 (same code path)
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
    for name in ("D1", "E2"):
        X, use_pca = inputs[name]
        ok = np.isfinite(X).all(axis=1)
        clf = EV.make_clf(use_pca).fit(X[labelled & ok], lab[labelled & ok] == "sand")
        m = (wells == "34_7-1") & ok
        sig[name][m] = clf.predict_proba(X[m])[:, 1]

    sel = np.isin(lab, ["excluded_zone", "no_log"]) & np.isfinite(sial)
    sel &= base.depth_m.values < np.array([XS.TOP_SHETLAND[w] for w in wells])
    masked = shoe_mask(base)
    print(f"photos removed by the shoe mask inside the test set: {int((sel & masked).sum())} of {int(sel.sum())}")
    sel &= ~masked
    rows = []
    for w in sorted(set(wells[sel])):
        m = sel & (wells == w)
        d = base.depth_m.values[m]
        x = XS.highpass(d, sial[m])
        for name, p in sig.items():
            y = XS.highpass(d, p[m])
            ok = np.isfinite(x) & np.isfinite(y)
            if ok.sum() < XS.MIN_N:
                continue
            rows.append({"signal": name, "well": w, "n": int(ok.sum()), "rho": spearmanr(y[ok], x[ok])[0]})
    t = pd.DataFrame(rows)
    t.to_csv(C.WORK_DIR / "v3_results" / "xrf_shallow_cement_masked.csv", index=False)
    print(t.pivot_table(index="well", columns="signal", values="rho").round(3).to_string())
    for name, g in t.groupby("signal"):
        r = g.rho.values
        print(f"{name:12} median rho {np.median(r):+.3f}  {int((r > 0).sum())}/{len(r)} > 0  "
              f"Wilcoxon p {wilcoxon(r, alternative='greater').pvalue:.4f}")


if __name__ == "__main__":
    main()
