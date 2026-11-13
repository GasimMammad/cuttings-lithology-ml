"""
v6 D (V6_SINKITE_PLAN.md section D + FINAL AMENDMENTS): pre-registered XRF
glauconite proxy and caving-vs-sinking test.

Depth windows (fixed before computing; NPD tops in Wells/files, operator
biostrat for THGU/base Oligocene where available; 34/7-6 from the Saga
biostrat table used throughout the original project):
  UTSIRA   NPD Utsira top -> THGU
  OLIG     THGU -> base Oligocene (operator) ; NPD/Bulletin 10 otherwise
  LISTA    NPD Lista top -> next top
G = min( log10(K'/Al / base), log10(Fe*/Al / base) ), K' = K - b*(Cl - median Cl)
(b from within-well regression of K on Cl over Tertiary bags, only if b > 0),
Fe* = Fe - 0.87*S, base = median over OLIG bags > 30 m below THGU that are
not GR-sand. Bags with Al below the well's Tertiary 10th percentile are
excluded. Fire = G > 0.2.
Sand bag = mean Vsh < 0.30 over (D-10, D] using the v2 GR zone anchors
(wells without a Tertiary zone cannot enter the sand test).

Run:  python 51_v6_xrf_glauconite.py
"""
from importlib import import_module

import lasio
import numpy as np
import pandas as pd
from scipy.stats import combine_pvalues, fisher_exact

import config as C

T40 = import_module("40_v3b_interval_test")
OUT = C.WORK_DIR / "v6"

W = {  # well: (utsira_top, thgu, olig_base, lista_top, lista_base)
    "34_4-6": (1210, 1250, 1390, 1688, 1775),
    "34_4-7": (1180, 1200, 1220, 1733, 1824),
    "34_7-1": (1150, 1170, 1200, 1696, 1823),
    "34_7-4": (1118, 1187, 1340, 1712, 1848),
    "34_7-6": (1030, 1036.5, 1310, 1764, 1846),
    "34_7-9": (1077, 1172, 1340, 1681, 1807),
    "34_7-10": (1084, 1093, 1350, 1800, 1863),
    "34_8-3": (1119, 1175, 1500, 1862, 2012),
    "34_8-3_A": (1120, 1180, 1300, 1920, 2088),
}


def xrf(well):
    d = lasio.read(str(C.SSD_ROOT / "Wells" / well / "DRILLING" / f"{well}_CUTTINGS_XRF_1.LAS"), engine="normal").df()
    d.index = np.round(d.index.values.astype(float), 2)
    return d


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for well, (ut, thgu, ob, lt, lb) in W.items():
        d = xrf(well)
        tert = d[(d.index >= 400) & (d.index <= lb)].copy()
        al10 = tert.AL.quantile(0.10)
        b = np.polyfit(tert.CL.fillna(0), tert.K, 1)[0] if tert.CL.notna().sum() > 10 else 0.0
        b = max(b, 0.0)
        tert["Kc"] = tert.K - b * (tert.CL.fillna(tert.CL.median()) - tert.CL.median())
        tert["Fes"] = tert.FE - 0.87 * tert.S.fillna(0)
        tert["kal"], tert["fal"] = tert.Kc / tert.AL, tert.Fes / tert.AL
        tert["al_ok"] = tert.AL >= al10
        z = np.array(tert.index)
        tert["window"] = np.select([(z >= ut) & (z < thgu), (z >= thgu) & (z <= ob), (z >= lt) & (z < lb)],
                                   ["UTSIRA", "OLIG", "LISTA"], "other")
        tert["dist"] = z - thgu
        # GR sand flag (v2 zones)
        tert["sand"] = np.nan
        if well in C.LABEL_ZONES:
            curves = T40.zone_curves(well)
            for zname, lo, hi, dz, vz in curves:
                for D in tert.index[(tert.index >= lo) & (tert.index <= hi)]:
                    if D - 10 >= lo:
                        v = T40.window_mean(curves, zname, D, 0, 10)
                        if np.isfinite(v):
                            tert.loc[D, "sand"] = float(v < C.VSH_SAND_MAX)
        basemask = (tert.window == "OLIG") & (tert.dist > 30) & tert.al_ok & (tert.sand != 1)
        bk, bf = tert.loc[basemask, "kal"].median(), tert.loc[basemask, "fal"].median()
        tert["G"] = np.minimum(np.log10(tert.kal / bk), np.log10(tert.fal / bf))
        tert["fire"] = (tert.G > 0.2) & tert.al_ok
        tert["well"] = well
        tert["cl_flag"] = tert.CL > 5000
        rows.append(tert.reset_index().rename(columns={"index": "depth_m", "DEPTH": "depth_m"}))
        print(f"{well}: K-Cl slope {b:.3f}; Al floor {al10:.0f}; base K/Al {bk:.3f} Fe*/Al {bf:.3f}; n base {int(basemask.sum())}")
    t = pd.concat(rows, ignore_index=True)
    t.to_csv(OUT / "D_xrf_glauconite_bags.csv", index=False)

    print("\nCONTROLS (Al-floor bags only)")
    ctl = []
    for well, g in t[t.al_ok].groupby("well"):
        u, l = g[g.window == "UTSIRA"], g[g.window == "LISTA"]
        ctl.append({"well": well, "utsira_n": len(u), "utsira_fire": int(u.fire.sum()),
                    "lista_n": len(l), "lista_fire": int(l.fire.sum())})
    ctl = pd.DataFrame(ctl)
    print(ctl.to_string(index=False))
    with_u = ctl[ctl.utsira_n > 0]
    pos_ok = (with_u.utsira_fire > 0).mean() >= 0.5
    lista_rate = ctl.lista_fire.sum() / max(ctl.lista_n.sum(), 1)
    print(f"positive control: Utsira fires in {(with_u.utsira_fire > 0).sum()}/{len(with_u)} wells with Utsira bags -> "
          f"{'PASS' if pos_ok else 'FAIL -> D UNINFORMATIVE'}; Lista fire rate {lista_rate:.1%} -> "
          f"{'PASS' if lista_rate < 0.05 else 'FAIL'}")

    print("\nSAND TEST within Oligocene (firing in GR-sand vs non-sand bags; one-sided Fisher per well)")
    res, ps, ps30 = [], [], []
    for well, g in t[(t.window == "OLIG") & t.al_ok & t.sand.notna()].groupby("well"):
        for tag, gg in (("all", g), (">30m", g[g.dist > 30])):
            a = int(((gg.sand == 1) & gg.fire).sum()); b_ = int(((gg.sand == 1) & ~gg.fire).sum())
            c = int(((gg.sand == 0) & gg.fire).sum()); d_ = int(((gg.sand == 0) & ~gg.fire).sum())
            p = fisher_exact([[a, b_], [c, d_]], alternative="greater")[1] if (a + b_) and (c + d_) else np.nan
            res.append({"well": well, "subset": tag, "sand_fire": a, "sand_n": a + b_, "mud_fire": c, "mud_n": c + d_, "p": p})
            if np.isfinite(p):
                (ps if tag == "all" else ps30).append(p)
    res = pd.DataFrame(res)
    print(res.to_string(index=False))
    for tag, pl in (("all", ps), (">30m", ps30)):
        if pl:
            print(f"combined (Fisher's method) {tag}: p {combine_pvalues(pl, method='fisher')[1]:.4f} over {len(pl)} wells")
    res.to_csv(OUT / "D_sand_test.csv", index=False)

    print("\nDISTANCE BANDS (Oligocene, Al-floor bags): fire / n, sand bags in brackets")
    t2 = t[(t.window == "OLIG") & t.al_ok].copy()
    t2["band"] = pd.cut(t2.dist, [-1, 30, 60, 100, 1000], labels=["0-30", "30-60", "60-100", ">100"])
    print(t2.groupby(["well", "band"], observed=False).agg(n=("fire", "size"), fire=("fire", "sum"),
                                                           sand=("sand", "sum")).unstack("band").to_string())

    print("\nNAMED TARGETS")
    for well, a, b2 in (("34_7-6", 1218, 1283), ("34_7-10", 1314, 1328), ("34_4-6", 1359, 1387)):
        g = t[(t.well == well) & t.depth_m.between(a, b2)]
        print(f"  {well} {a}-{b2} m: n {len(g)}, G {g.G.round(2).tolist()}, fire {int(g.fire.sum())}, "
              f"sand flags {g.sand.tolist()}, Cl>5000 {int(g.cl_flag.sum())}")


if __name__ == "__main__":
    main()
