"""
v4 -- agreement between core-photo raters (V4_PLAN.md A2).
Matches bins by depth (bin top rounded to 1 cm) and reports Cohen's kappa
on the 5-class label, on a binary SAND-vs-rest label (bins where both raters
saw core), and the correlation of per-metre sand fractions.

Run:  python 45_v4_rater_agreement.py [well ...]
"""
import sys

import numpy as np
import pandas as pd

import config as C

D = C.WORK_DIR / "core_digitised"


def kappa(a, b):
    cats = sorted(set(a) | set(b))
    n = len(a)
    po = np.mean(np.array(a) == np.array(b))
    pa = pd.Series(a).value_counts(normalize=True)
    pb = pd.Series(b).value_counts(normalize=True)
    pe = sum(pa.get(c, 0) * pb.get(c, 0) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else np.nan, po, n


def load(rater, well):
    t = pd.read_csv(D / rater / f"{well}.csv")
    t["key"] = (t.bin_top_m * 100).round().astype(int)
    return t.drop_duplicates("key", keep="last").set_index("key")


def sand_frac(t):
    t = t[t["class"].isin(["SAND", "HET", "MUD", "OTHER"])].copy()
    t["m"] = np.floor(t.bin_top_m)
    s = t.assign(v=t["class"].map({"SAND": 1.0, "HET": 0.5, "MUD": 0.0, "OTHER": 0.0}))
    return s.groupby("m").v.mean()


def main(wells):
    for w in wells:
        a, b = load("A_opus", w), load("B_sonnet", w)
        k = a.index.intersection(b.index)
        ka, po, n = kappa(a.loc[k, "class"].tolist(), b.loc[k, "class"].tolist())
        both = k[(a.loc[k, "class"] != "NONE").values & (b.loc[k, "class"] != "NONE").values]
        kb, pob, nb = kappa((a.loc[both, "class"] == "SAND").tolist(), (b.loc[both, "class"] == "SAND").tolist())
        fa, fb = sand_frac(a), sand_frac(b)
        m = fa.index.intersection(fb.index)
        r = np.corrcoef(fa[m], fb[m])[0, 1] if len(m) > 2 else np.nan
        print(f"{w}: matched bins {n} (A {len(a)}, B {len(b)}); 5-class kappa {ka:.2f} (agree {po:.0%}); "
              f"SAND-vs-rest kappa {kb:.2f} on {nb} bins with core (agree {pob:.0%}); "
              f"per-metre sand fraction r {r:.2f} over {len(m)} m")
        print(pd.crosstab(a.loc[k, "class"], b.loc[k, "class"], rownames=["A"], colnames=["B"]).to_string())


if __name__ == "__main__":
    main(sys.argv[1:] or ["34_4-6"])
