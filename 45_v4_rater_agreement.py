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

D = C.WORK_DIR / ("core_digitised_v2" if "--v2" in sys.argv else "core_digitised")
NOCORE = {"NONE", "EMPTY", "RUBBLE", "PRESERVED-GAP"}


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
    t["cls5"] = t["class"].where(~t["class"].isin(NOCORE), "NOCORE")
    return t.drop_duplicates("key", keep="last").set_index("key")


def sand_frac(t, rubble=False):
    t = t.copy()
    if rubble and "rubble_lith" in t:
        r = (t["class"] == "RUBBLE") & t.rubble_lith.isin(["SAND", "HET", "MUD"])
        t.loc[r, "class"] = t.loc[r, "rubble_lith"]
    t = t[t["class"].isin(["SAND", "HET", "MUD", "OTHER"])].copy()
    t["m"] = np.floor(t.bin_top_m)
    s = t.assign(v=t["class"].map({"SAND": 1.0, "HET": 0.5, "MUD": 0.0, "OTHER": 0.0}))
    return s.groupby("m").v.mean()


def main(wells):
    for w in wells:
        a, b = load("A_opus", w), load("B_sonnet", w)
        k = a.index.intersection(b.index)
        ka, po, n = kappa(a.loc[k, "cls5"].tolist(), b.loc[k, "cls5"].tolist())
        both = k[(a.loc[k, "cls5"] != "NOCORE").values & (b.loc[k, "cls5"] != "NOCORE").values]
        kb, pob, nb = kappa((a.loc[both, "class"] == "SAND").tolist(), (b.loc[both, "class"] == "SAND").tolist())
        fa, fb = sand_frac(a), sand_frac(b)
        m = fa.index.intersection(fb.index)
        r = np.corrcoef(fa[m], fb[m])[0, 1] if len(m) > 2 else np.nan
        print(f"{w}: matched bins {n} (A {len(a)}, B {len(b)}); 5-class kappa {ka:.2f} (agree {po:.0%}); "
              f"SAND-vs-rest kappa {kb:.2f} on {nb} bins with core (agree {pob:.0%}); "
              f"per-metre sand fraction r {r:.2f} over {len(m)} m")
        fr_a, fr_b = sand_frac(a, True), sand_frac(b, True)
        mr = fr_a.index.intersection(fr_b.index)
        print(f"   rubble-as-lithology sensitivity: per-metre r {np.corrcoef(fr_a[mr], fr_b[mr])[0, 1]:.2f} over {len(mr)} m")
        print(pd.crosstab(a.loc[k, "class"], b.loc[k, "class"], rownames=["A"], colnames=["B"]).to_string())


if __name__ == "__main__":
    main([w for w in sys.argv[1:] if not w.startswith("--")] or ["34_4-6"])
