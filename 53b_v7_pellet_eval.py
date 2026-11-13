"""
v7 step 2 evaluation (V7_PLAN.md step 2, A9-A12 with the A15 amendments).
Joins the photo scores (53_v7_pellet_blobs.py, written without G) to the v6
XRF glauconite index G and runs, exactly once:

  primary   within +/-80 m of THGU: rank(S) residualised on [1, d, |d|] per
            well; Q = mean within-well AUC of the residual for G > 0.2;
            null = circular shifts of the residual against G (A15)
  Lista     false positives at the LOWO 50%-interval-recall threshold (<= 5%)
  success   primary p < 0.05 with Q > 0.5 AND Lista FP <= 5%
  the rest  descriptive / sensitivities, as listed in the plan

Run:  python 53b_v7_pellet_eval.py
"""
import json

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

import config as C

OUT = C.WORK_DIR / "v7" / "step2"
RNG = np.random.default_rng(53)
N_MC = 10000
WIN, GTHR, MERGE_M = 80.0, 0.2, 20.0


def auc(pos, s):
    pos = np.asarray(pos, bool)
    n1, n0 = pos.sum(), (~pos).sum()
    if n1 == 0 or n0 == 0:
        return np.nan
    r = rankdata(s)
    return float((r[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def resid(s, d, design):
    r = rankdata(s)
    A = np.c_[np.ones(len(d)), d] if design == "d" else np.c_[np.ones(len(d)), d, np.abs(d)]
    return r - A @ np.linalg.lstsq(A, r, rcond=None)[0]


def shifts(n):
    return list(range(2, n - 1))  # k = 2 .. n-2


def conditional(t, col, gthr=GTHR, win=WIN, design="d|d|", null="resid"):
    """t: joined table. Returns Q, p and per-well detail."""
    w_ = t[(t.dist.abs() <= win) & np.isfinite(t.G) & np.isfinite(t[col])]
    per, nulls = {}, []
    for w, g in w_.groupby("well"):
        g = g.sort_values("depth_m")
        pos = (g.G > gthr).values
        if pos.sum() == 0 or (~pos).sum() == 0:
            continue
        s, d = g[col].values.astype(float), g.dist.values.astype(float)
        e = resid(s, d, design)
        a = auc(pos, e)
        ks = shifts(len(g))
        if null == "resid":  # A15 primary: shift the residual against G
            na = [auc(pos, np.roll(e, k)) for k in ks]
        else:                # A9 original: shift S against (G, d), then residualise
            na = [auc(pos, resid(np.roll(s, k), d, design)) for k in ks]
        per[w] = {"n": int(len(g)), "n_pos": int(pos.sum()), "auc_resid": a,
                  "auc_raw": auc(pos, s), "auc_dist_only": auc(pos, -np.abs(d)),
                  "rho_S_G": float(spearmanr(s, g.G.values)[0])}
        nulls.append(np.array(na))
    if not per:
        return {"Q": np.nan, "p": np.nan, "per_well": {}}
    Q = float(np.mean([v["auc_resid"] for v in per.values()]))
    draw = np.mean([RNG.choice(na, N_MC) for na in nulls], axis=0)
    p = float((1 + (draw >= Q - 1e-12).sum()) / (N_MC + 1))
    return {"Q": Q, "p": p, "n_wells": len(per), "n_bags": int(len(w_)),
            "n_pos": int(sum(v["n_pos"] for v in per.values())), "per_well": per}


def intervals(t, gthr=GTHR, win=WIN):
    """Positive intervals inside the window: positives <= MERGE_M apart merge."""
    rows = []
    w_ = t[(t.dist.abs() <= win) & np.isfinite(t.G)]
    for w, g in w_.groupby("well"):
        g = g.sort_values("depth_m")
        dp = g.depth_m.values[(g.G > gthr).values]
        if len(dp) == 0:
            continue
        grp = np.r_[0, np.cumsum(np.diff(dp) > MERGE_M)]
        for k in np.unique(grp):
            dd = dp[grp == k]
            rows.append({"well": w, "top": float(dd.min()), "base": float(dd.max()), "n_bags": int(len(dd))})
    return pd.DataFrame(rows)


def interval_max(t, iv, col):
    out = []
    for r in iv.itertuples():
        m = (t.well == r.well) & (t.depth_m >= r.top) & (t.depth_m <= r.base)
        out.append(np.nanmax(t.loc[m, col].values) if m.any() else np.nan)
    return np.array(out)


def lowo_tau(iv, imax, well):
    """Highest threshold that still recovers >= 50% of the positive intervals
    of the OTHER wells (interval recovered = max score in it >= tau)."""
    m = np.sort(imax[(iv.well != well).values & np.isfinite(imax)])[::-1]
    if len(m) == 0:
        return np.nan
    return float(m[int(np.ceil(0.5 * len(m))) - 1])


def lista_block(t, lun, col, iv):
    imax = interval_max(t, iv, col)
    lis = t[(t.window == "LISTA") & np.isfinite(t[col])]
    taus, fp, n = {}, 0, 0
    for w, g in lis.groupby("well"):
        tau = lowo_tau(iv, imax, w)
        taus[w] = {"tau_w": tau, "n_lista": int(len(g)), "fp": int((g[col] >= tau).sum())}
        fp += taus[w]["fp"]; n += len(g)
    tauL = float(np.nanpercentile(lun[col].values, 99))
    return {"fp": int(fp), "n": int(n), "fp_rate": fp / n if n else np.nan, "per_well": taus,
            "tau_L_lunde_p99": tauL, "fp_at_tau_L": int((lis[col] >= tauL).sum()),
            "interval_recall_at_tau_L": float(np.mean(imax >= tauL)) if len(imax) else np.nan,
            "interval_max": [round(float(x), 3) for x in imax]}


def main():
    sc = pd.read_csv(OUT / "g_scores.csv")
    lun = pd.read_csv(OUT / "lunde_scores.csv")
    g = pd.read_csv("results/v6/D_xrf_glauconite_bags.csv")[["well", "depth_m", "window", "dist", "G"]]
    g = g[np.isfinite(g.G)]
    g["depth_m"] = g.depth_m.round(2); sc["depth_m"] = sc.depth_m.round(2)
    t = g.merge(sc, on=["well", "depth_m"], how="left")
    form = pd.read_csv(C.PATCHES_CSV, usecols=["well", "depth_m", "formation"]).drop_duplicates(["well", "depth_m"])
    form["depth_m"] = form.depth_m.round(2)
    t = t.merge(form, on=["well", "depth_m"], how="left")
    res = {"n_G_bags": int(len(g)), "n_with_photo_score": int(t.S.notna().sum()),
           "n_pos_total": int((t.G > GTHR).sum()), "n_pos_with_score": int(((t.G > GTHR) & t.S.notna()).sum())}

    # ---- A9 primary + declared variants
    res["PRIMARY S [1,d,|d|] resid-shift null"] = conditional(t, "S")
    res["secondary S [1,d]"] = conditional(t, "S", design="d")
    res["sens original null (shift S)"] = conditional(t, "S", null="raw")
    res["GI [1,d,|d|] (comparator)"] = conditional(t, "GI")
    for c in ("S_area", "S_L45", "S_L55", "S_nofill"):
        res[f"sens {c}"] = conditional(t, c)
    for thr in (0.15, 0.3):
        res[f"sens G>{thr}"] = conditional(t, "S", gthr=thr)
    res["sens window 120 m"] = conditional(t, "S", win=120.0)

    # ---- (b) descriptive: residualised AUC of S vs GI per well
    ps, pg = res["PRIMARY S [1,d,|d|] resid-shift null"]["per_well"], res["GI [1,d,|d|] (comparator)"]["per_well"]
    wins = {w: bool(ps[w]["auc_resid"] > pg[w]["auc_resid"]) for w in ps if w in pg}
    res["(b) S beats GI (descriptive)"] = {"wins": int(sum(wins.values())), "of": len(wins), "per_well": wins}

    # ---- intervals
    iv = intervals(t)
    top = []
    for r in iv.itertuples():
        ww = t[(t.well == r.well) & (t.dist.abs() <= WIN) & t.S.notna()]
        thr = np.nanpercentile(ww.S, 80)
        inside = ww[(ww.depth_m >= r.top) & (ww.depth_m <= r.base)]
        top.append(bool((inside.S >= thr).any()))
    iv["has_top20pct_S"] = top
    res["intervals"] = iv.to_dict("records")

    # ---- A10 Lista
    res["LISTA S"] = lista_block(t, lun, "S", iv)
    res["LISTA GI"] = lista_block(t, lun, "GI", iv)
    tauL = res["LISTA S"]["tau_L_lunde_p99"]
    for tag, m in (("Balder Fm", t.formation.astype(str).str.upper().eq("BALDER FM")),
                   ("Oligocene > 60 m below THGU, G < 0.05", (t.window == "OLIG") & (t.dist > 60) & (t.G < 0.05))):
        x = t[m & t.S.notna()]
        res[f"FP row: {tag}"] = {"n": int(len(x)), "above_tau_L": int((x.S >= tauL).sum()),
                                 "S_median": float(x.S.median()) if len(x) else np.nan,
                                 "S_max": float(x.S.max()) if len(x) else np.nan}

    # ---- A11 out-of-window positives
    rows = []
    for r in t[(t.G > GTHR) & (t.dist.abs() > WIN) & t.S.notna()].itertuples():
        ref = t[(t.well == r.well) & (t.dist.abs() > WIN) & t.S.notna()].S.values
        rows.append({"well": r.well, "depth_m": r.depth_m, "dist": r.dist, "G": round(r.G, 3), "S": round(r.S, 2),
                     "S_pctile_in_well": round(float((ref < r.S).mean() * 100), 1)})
    res["out-of-window positives"] = rows

    # ---- descriptive extras
    res["per-well medians (label-free)"] = t.groupby("well")[["S", "GI", "S_brown", "a_med", "b_med", "L_mean"]].median().round(3).to_dict("index")
    res["lunde"] = {"n": int(len(lun)), "S_median": float(lun.S.median()), "S_p99": tauL, "S_max": float(lun.S.max())}
    res["S by window (median, p90, max)"] = {k: [round(float(v.median()), 2), round(float(v.quantile(.9)), 2), round(float(v.max()), 2)]
                                             for k, v in t.groupby("window").S}
    try:  # concordance with the v6 blind pellet check (10 high-G, 10 low-G bags)
        e = pd.read_csv("results/v6/E_unsealed.csv")
        e["depth_m"] = e.depth_m.round(2)
        e = e.merge(t[["well", "depth_m", "S", "GI"]], on=["well", "depth_m"], how="left")
        res["pellet-check bags"] = e.round(3).to_dict("records")
    except Exception as ex:
        res["pellet-check bags"] = f"not joined: {ex}"

    P, Lz = res["PRIMARY S [1,d,|d|] resid-shift null"], res["LISTA S"]
    a_ok = bool(P["p"] < 0.05 and P["Q"] > 0.5)
    c_ok = bool(Lz["fp_rate"] <= 0.05)
    res["SUCCESS"] = {"a_primary": a_ok, "c_lista": c_ok, "criterion_pass": a_ok and c_ok,
                      "b_descriptive": res["(b) S beats GI (descriptive)"]["wins"]}
    t.to_csv(OUT / "g_scores_joined.csv", index=False)
    with open(OUT / "step2_results.json", "w") as f:
        json.dump(res, f, indent=1, default=float)

    print(json.dumps({k: res[k] for k in ("n_G_bags", "n_with_photo_score", "n_pos_total", "n_pos_with_score")}))
    for k, v in res.items():
        if isinstance(v, dict) and "Q" in v:
            pw = {w: round(x["auc_resid"], 2) for w, x in v["per_well"].items()}
            print(f"{k:40s} Q {v['Q']:.3f}  p {v['p']:.4f}  wells {v.get('n_wells')}  pos {v.get('n_pos')}/{v.get('n_bags')}  {pw}")
    print("raw AUC per well (S, GI, dist-only):",
          {w: (round(ps[w]["auc_raw"], 2), round(pg[w]["auc_raw"], 2), round(ps[w]["auc_dist_only"], 2)) for w in ps})
    print("rho(S, G) in window:", {w: round(ps[w]["rho_S_G"], 2) for w in ps})
    print("(b)", res["(b) S beats GI (descriptive)"])
    print(iv.to_string())
    for k in ("LISTA S", "LISTA GI"):
        v = res[k]
        print(k, f"FP {v['fp']}/{v['n']} = {v['fp_rate']:.3f} | tau_L {v['tau_L_lunde_p99']:.3f}: FP {v['fp_at_tau_L']}, "
                 f"interval recall {v['interval_recall_at_tau_L']:.2f}", {w: round(x['tau_w'], 3) for w, x in v["per_well"].items()})
    for k in res:
        if k.startswith("FP row"):
            print(k, res[k])
    print("out-of-window positives:", rows)
    print("S by window:", res["S by window (median, p90, max)"])
    print("lunde:", res["lunde"])
    print("SUCCESS:", res["SUCCESS"])


if __name__ == "__main__":
    main()
