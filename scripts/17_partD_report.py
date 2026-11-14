"""
PART D2/D3 — per-well tables, fraction-firing statistics, Ba correlation.
Thresholds frozen; this script only reads 16_green_index_all.csv.
"""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import config as C

G = pd.read_csv(C.WORK_DIR / "16_green_index_all.csv")
BA = pd.read_csv(C.WORK_DIR / "15_ba_all_wells.csv")

MOUND = {"34_7-4": "ON-MOUND", "34_7-10": "ON-MOUND",
         "34_7-9": "UNCERTAIN", "34_7-1": "UNCERTAIN",
         "34_4-6": "off-mound", "34_4-7": "off-mound", "34_8-3": "off-mound",
         "34_8-3_A": "off-mound", "24_9-3": "off-mound", "24_9-4": "off-mound"}
UTSIRA = {
    "34_7-4": [("NPD", 1118, 1187), ("operator", 1080, 1187)],
    "34_7-9": [("NPD", 1077, 1172), ("operator", 1100, 1172)],
    "34_7-10": [("NPD", 1084, 1093), ("operator_sand", 993, 1045),
                ("operator_full", 993, 1093)],
    "34_8-3": [],
    "34_8-3_A": [("Bulletin10", 1120, 1180)],
    "34_4-6": [("Bulletin10", 1210, 1250)],
    "34_4-7": [("Bulletin10", 1180, 1200)],
    "34_7-1": [("Bulletin10", 1150, 1170)],
}
OLIG = {"34_7-4": (1187, 1340), "34_7-9": (1172, 1340), "34_7-10": (1093, 1350),
        "34_8-3": (1320, 1500), "34_8-3_A": (1240, 1300), "34_4-6": (1250, 1390),
        "34_4-7": (1200, 1220), "34_7-1": (1170, 1200)}
THGU = {"34_7-4": 1187, "34_7-9": 1172, "34_7-10": 1093, "34_8-3": 1175,
        "34_8-3_A": 1180, "34_4-6": 1250, "34_4-7": 1200, "34_7-1": 1170}
PRIMARY = ["34_7-4", "34_7-10", "34_4-6", "34_8-3"]
THIN = {"34_4-7", "34_7-1", "34_8-3_A"}
TOPS = {  # for naming the deep-control formation
 "34_4-6":[(1250,"HORDALAND"),(1658,"BALDER"),(1688,"LISTA"),(1775,"JORSALFARE"),
           (2056,"KYRRE"),(2577,"LUNDE"),(3153,"LOMVI")],
 "34_4-7":[(1200,"HORDALAND"),(1700,"BALDER"),(1733,"LISTA"),(1824,"JORSALFARE"),
           (2076,"KYRRE"),(2502,"LUNDE")],
 "34_7-1":[(1170,"HORDALAND"),(1673,"BALDER"),(1696,"LISTA"),(1823,"JORSALFARE"),
           (1933,"KYRRE"),(2392,"LUNDE")],
 "34_7-4":[(1187,"HORDALAND"),(1685,"BALDER"),(1712,"LISTA"),(1848,"JORSALFARE"),
           (1998,"KYRRE"),(2628,"LUNDE")],
 "34_7-9":[(1172,"HORDALAND"),(1657,"BALDER"),(1681,"LISTA"),(1807,"JORSALFARE"),
           (2025,"KYRRE"),(2443,"LUNDE")],
 "34_7-10":[(1093,"HORDALAND"),(1682,"BALDER"),(1728,"SELE"),(1800,"LISTA"),
            (1863,"JORSALFARE"),(2145,"KYRRE"),(2683,"LUNDE")],
 "34_8-3":[(1175,"HORDALAND"),(1820,"BALDER"),(1862,"LISTA"),(2012,"JORSALFARE"),
           (2300,"KYRRE"),(2827,"DRAUPNE")],
 "34_8-3_A":[(1180,"HORDALAND"),(1873,"BALDER"),(1920,"LISTA"),(2088,"JORSALFARE"),
             (2395,"KYRRE"),(3003,"DRAUPNE")],
 "24_9-3":[(1918,"BALDER"),(1981,"HERMOD"),(2060,"SELE"),(2215,"HEIMDAL"),
           (2567,"LISTA"),(2757,"VALE"),(2836,"JORSALFARE")],
 "24_9-4":[(1974,"BALDER"),(2098,"SELE"),(2170,"LISTA")],
}


def fm(w, z):
    t = [x for x in TOPS.get(w, []) if x[0] <= z]
    return t[-1][1] if t else "above tops"


def bg(w):
    s = G[(G.well == w) & (G.depth_m > 1450)].green_index
    return float(s.median()) if len(s) else float("nan")


def block(w, a, b):
    return G[(G.well == w) & (G.depth_m >= a) & (G.depth_m <= b)].sort_values("depth_m")


def stats(sub, b):
    n = len(sub)
    if n == 0:
        return dict(n=0, n_fire=0, frac=float("nan"), mx=float("nan"))
    fire = int((sub.green_index > b).sum())
    return dict(n=n, n_fire=fire, frac=fire / n, mx=float(sub.green_index.max()))


def main():
    lines = []
    def w_(s=""):
        print(s); lines.append(s)

    w_("=" * 108)
    w_("PART D — TABLE 1: UTSIRA CONTROL MAGNITUDE, ALL WELLS SIDE BY SIDE")
    w_("  criterion: fires CLEARLY ABOVE ITS OWN background. Agreement between")
    w_("  wells is NOT required (34/4-6 0.0358 vs 34/7-1 0.2509 = 7x spread).")
    w_("=" * 108)
    w_(f"{'well':10} {'group':10} {'window':14} {'n':>3} {'bkg':>8} {'max':>9} "
       f"{'max/bkg':>8} {'>bkg':>6}  per-photograph values")
    for wl in C.ALL_WELLS:
        b = bg(wl)
        if not UTSIRA.get(wl):
            reason = ("NO PHOTOS above 1320 m" if wl == "34_8-3"
                      else "no Utsira assigned (Viking Graben)")
            w_(f"{wl:10} {MOUND[wl]:10} {'--':14} {'--':>3} {b:8.4f} {'--':>9} "
               f"{'--':>8} {'--':>6}  {reason}")
            continue
        for nm, a, bb in UTSIRA[wl]:
            sub = block(wl, a, bb)
            st = stats(sub, b)
            vals = "  ".join(f"{r.depth_m:.0f}:{r.green_index:.4f}"
                             for _, r in sub.iterrows())
            ratio = st["mx"] / b if b and np.isfinite(st["mx"]) else float("nan")
            w_(f"{wl:10} {MOUND[wl]:10} {nm:14} {st['n']:>3} {b:8.4f} "
               f"{st['mx']:9.4f} {ratio:8.1f} {st['n_fire']:>3}/{st['n']:<2}  {vals[:120]}")

    w_("")
    w_("=" * 108)
    w_("PART D — TABLE 2: DEEP POSITIVE CONTROL (below 1250 m)")
    w_("=" * 108)
    w_(f"{'well':10} {'bkg':>8} {'max':>9} {'depth':>7} {'formation':<12} "
       f"{'x bkg':>7} {'n>10x bkg':>10} {'n deep':>7}")
    for wl in C.ALL_WELLS:
        b = bg(wl)
        deep = G[(G.well == wl) & (G.depth_m > 1250)]
        if deep.empty:
            w_(f"{wl:10} {b:8.4f}  no photos below 1250 m"); continue
        i = deep.green_index.idxmax()
        r = deep.loc[i]
        n10 = int((deep.green_index > 10 * b).sum())
        w_(f"{wl:10} {b:8.4f} {r.green_index:9.4f} {r.depth_m:7.0f} "
           f"{fm(wl, r.depth_m):<12} {r.green_index/b:7.1f} {n10:>10} {len(deep):>7}")

    w_("")
    w_("=" * 108)
    w_("PART D — TABLE 3: OLIGOCENE TARGET INTERVAL (the test)")
    w_("  A null in a 3-photo window is WEAK evidence; a null in a 26-photo")
    w_("  window is STRONG evidence. Fraction firing is the reportable number.")
    w_("=" * 108)
    w_(f"{'well':10} {'group':10} {'interval':13} {'n':>3} {'fire':>5} {'frac':>6} "
       f"{'max':>9} {'max/bkg':>8}  weight")
    for wl in [x for x in C.ALL_WELLS if x in OLIG]:
        a, bb = OLIG[wl]
        b = bg(wl)
        sub = block(wl, a, bb)
        st = stats(sub, b)
        wt = ("PRIMARY" if wl in PRIMARY else
              "TOO THIN" if wl in THIN else "secondary")
        ratio = st["mx"] / b if b else float("nan")
        w_(f"{wl:10} {MOUND[wl]:10} {f'{a:.0f}-{bb:.0f}':13} {st['n']:>3} "
           f"{st['n_fire']:>5} {st['frac']:>6.2f} {st['mx']:9.4f} {ratio:8.1f}  {wt}")
    w_("")
    for wl in [x for x in C.ALL_WELLS if x in OLIG]:
        a, bb = OLIG[wl]
        sub = block(wl, a, bb)
        w_(f"  {wl} Oligocene {a:.0f}-{bb:.0f} m, per photograph:")
        w_("    " + "  ".join(f"{r.depth_m:.0f}:{r.green_index:.4f}"
                              for _, r in sub.iterrows()))

    w_("")
    w_("  Fig. 6 published Oligocene sand picks (reported separately):")
    for wl, a, bb in [("34_7-10", 1314, 1328), ("34_4-6", 1360, 1389)]:
        sub = block(wl, a, bb)
        b = bg(wl)
        w_(f"    {wl} {a}-{bb} m  n={len(sub)}  "
           + "  ".join(f"{r.depth_m:.0f}:{r.green_index:.4f}" for _, r in sub.iterrows())
           + (f"   [n=1 — cannot be a headline result either way]" if len(sub) == 1 else ""))

    w_("")
    w_("=" * 108)
    w_("PART D3 — INDEX vs Ba WITHIN EACH WELL (is the index reading mud?)")
    w_("=" * 108)
    w_(f"{'well':10} {'n':>5} {'spearman(index, Ba)':>21}")
    for wl in C.ALL_WELLS:
        g = G[G.well == wl][["depth_m", "green_index"]]
        b_ = BA[BA.well == wl][["depth_m", "ba_ppm"]]
        m = g.merge(b_, on="depth_m", how="inner").dropna()
        if len(m) > 10:
            r = spearmanr(m.green_index, m.ba_ppm).statistic
            w_(f"{wl:10} {len(m):>5} {r:>21.2f}")
        else:
            w_(f"{wl:10} {len(m):>5} {'n/a':>21}")

    (C.WORK_DIR / "PARTD_report.txt").write_text("\n".join(lines))
    print(f"\nwritten: {C.WORK_DIR/'PARTD_report.txt'}")


if __name__ == "__main__":
    main()
