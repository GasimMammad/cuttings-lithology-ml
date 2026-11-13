"""
v3 DIAGNOSTIC (not a test): are the strongest shallow false positives cement
drilled out of a casing-shoe track? Flags photos 0-30 m below a 30"/20"/13 3/8"
shoe (Sodir casing table, results/v3/sodir_casing_table.csv) and compares D1
(ResNet-50, leave-one-well-out; 34/7-1 from a model on all 10 labelled wells)
and XRF Ca/Al.

Run:  python 41_v3_shoe_cement_check.py
"""
from importlib import import_module

import lasio
import numpy as np
import pandas as pd

import config as C

EV = import_module("29_v2_evaluate")


def main():
    base, emb = EV.load_tables()
    pred = pd.read_csv(C.WORK_DIR / "v2_results" / "predictions.csv")
    cas = pd.read_csv("results/v3/sodir_casing_table.csv")
    cas["wlbName"] = cas.wlbName.str.strip()
    X, pca = EV.build_inputs(base, emb)["D1"]
    lab = base.label.values
    tr = np.isin(lab, ["sand", "clay"])
    clf = EV.make_clf(pca).fit(X[tr], lab[tr] == "sand")
    d1 = pred.p_D1.values.copy()
    m71 = (base.well == "34_7-1").values
    d1[m71] = clf.predict_proba(X[m71])[:, 1]
    rows = []
    for w in base.well.unique():
        f = C.SSD_ROOT / "Wells" / w / "DRILLING" / f"{w}_CUTTINGS_XRF_1.LAS"
        x = lasio.read(str(f), engine="normal").df()
        caal = (x["CA"] / x["AL"])
        caal.index = np.round(caal.index.values.astype(float), 2)
        sh = cas[cas.wlbName == w.replace("_", "/").replace("/A", " A")]
        shoes = sh[sh.wlbCasingType.str.strip().isin(["CONDUCTOR", "SURF.COND.", "INTERM."])].wlbCasingDepth.values
        for i in np.flatnonzero((base.well == w).values):
            D = base.depth_m.values[i]
            below = [D - s for s in shoes if 0 <= D - s <= 30]
            rows.append({"well": w, "depth_m": D, "d1": d1[i], "near_shoe": bool(below),
                         "m_below_shoe": min(below) if below else np.nan,
                         "ca_al": caal.get(round(D, 2), np.nan)})
    t = pd.DataFrame(rows).dropna(subset=["d1"])
    t.to_csv(C.WORK_DIR / "v3_results" / "shoe_cement_check.csv", index=False)
    n, e = t[t.near_shoe], t[~t.near_shoe]
    print(f"Ca/Al median: <=30 m below shoe {n.ca_al.median():.2f} vs elsewhere {e.ca_al.median():.2f}")
    print(f"D1 median:    <=30 m below shoe {n.d1.median():.2f} vs elsewhere {e.d1.median():.2f} (n {len(n)} vs {len(e)})")
    print(t[(t.ca_al > 2) & (t.d1 > 0.9)].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
