"""
v10 part R (V10_PLAN.md with the review amendments): step response of cuttings.
How many metres does a bag need to register a sharp gamma-ray step? Run once.

  python 71_v10_step.py     writes ~/sinkite_ml_work_v2/v10/R_results.json, R_steps.csv, R_stack.csv
"""
import json
from importlib import import_module

import numpy as np
import pandas as pd
from scipy.ndimage import median_filter
from scipy.optimize import curve_fit

import config as C

M = import_module("52_v7_photo_to_xrf")
E = import_module("63_v8_elements_when")
ML = import_module("57_v7_mudlog_labels")
L3 = import_module("03_make_labels")
OUT = C.WORK_DIR / "v10"
WIN, MIN_SEP, SHARP_M, SHARP_FRAC, SHOE_M = 30.0, 80.0, 5.0, 0.5, 60.0
PLAT = (20.0, 60.0)          # plateaus: 20 to 60 m above and below the step
MID = (-20.0, 40.0)          # bags in between
MIN_BAGS, CONTRAST = 4, 1.0
NBOOT, NNOISE = 2000, 200
VARS = ["ideal", "sial", "k", "photo"]
NAMES = {"ideal": "ideal bag (gamma ray over the bag interval)", "sial": "measured Si/Al", "k": "measured K",
         "photo": "photo prediction of Si/Al"}
K9 = 2 * np.log(9.0)         # 10-90 % width of a logistic = 4.394 w


def logistic(x, a, b, x0, w):
    return a + b / (1.0 + np.exp(-(x - x0) / w))


def fit(x, y):
    """Free asymptotes. Returns lag x0, 10-90 % width, amplitude b (NaN if the fit fails)."""
    if len(x) < 30:
        return np.nan, np.nan, np.nan
    try:
        p, _ = curve_fit(logistic, x, y, p0=[0.0, 1.0, 5.0, 5.0], bounds=([-1, 0.1, -40, 0.1], [1, 3, 40, 40]), maxfev=4000)
        return float(p[2]), float(K9 * p[3]), float(p[1])
    except Exception:
        return np.nan, np.nan, np.nan


def find_steps(z, v):
    """Sharp steps of the gamma-ray curve (5 m running median), strongest first, >= MIN_SEP apart."""
    dz = float(np.median(np.diff(z)))
    k = max(3, int(round(5.0 / dz)) | 1)
    vs = median_filter(v, size=k, mode="nearest")
    rsd = 1.4826 * np.median(np.abs(vs - np.median(vs)))
    grid = np.arange(np.ceil(z.min() + WIN), np.floor(z.max() - WIN), 1.0)
    s = np.full(len(grid), np.nan)
    for i, g in enumerate(grid):
        a0, a1, b1 = np.searchsorted(z, [g - WIN, g, g + WIN])
        if a1 - a0 > 5 and b1 - a1 > 5:
            s[i] = np.median(vs[a1:b1]) - np.median(vs[a0:a1])
    order = np.argsort(-np.abs(np.nan_to_num(s)))
    acc = []
    for i in order:
        if not np.isfinite(s[i]) or abs(s[i]) < rsd:
            break
        if all(abs(grid[i] - grid[j]) >= MIN_SEP for j in acc):
            acc.append(i)
    out = []
    for i in acc:
        g = grid[i]
        near = np.interp([g - SHARP_M, g + SHARP_M], z, vs)
        out.append({"z": float(g), "s": float(s[i]), "s_over_sd": float(abs(s[i]) / rsd), "sharp": float((near[1] - near[0]) / s[i])})
    return out, float(rsd)


def step_record(x, v, g):
    """One step, one variable. x: bag depth minus step depth; v: variable; g: ideal-bag gamma ray at the same bags."""
    m = np.isfinite(v) & np.isfinite(g) & (np.abs(x) <= PLAT[1])
    x, v, g = x[m], v[m], g[m]
    up, lo = (x >= -PLAT[1]) & (x <= -PLAT[0]), (x >= PLAT[0]) & (x <= PLAT[1])
    mid = (x > MID[0]) & (x < MID[1])
    if up.sum() < MIN_BAGS or lo.sum() < MIN_BAGS or mid.sum() < MIN_BAGS:
        return None
    dg = g[lo].mean() - g[up].mean()
    if dg == 0:
        return None
    delta = v[lo].mean() - v[up].mean()
    sd = float(np.sqrt((v[up].var(ddof=1) + v[lo].var(ddof=1)) / 2))
    ok = bool(sd > 0 and abs(delta) >= CONTRAST * sd)
    return {"x": x, "u": (g - g[up].mean()) / dg, "delta": float(delta), "sd": sd, "ok": ok,
            "y": (v - v[up].mean()) / delta if ok else None, "up": up, "lo": lo}


def simulate(rec, rng):
    """Ideal-bag shape with this variable's plateau difference and noise, through the same rule and scaling."""
    s = rec["delta"] * rec["u"] + rng.normal(0, rec["sd"], len(rec["u"]))
    up, lo = rec["up"], rec["lo"]
    d = s[lo].mean() - s[up].mean()
    sd = np.sqrt((s[up].var(ddof=1) + s[lo].var(ddof=1)) / 2)
    if sd > 0 and abs(d) >= CONTRAST * sd:
        return rec["x"], (s - s[up].mean()) / d
    return None


def stack(recs):
    r = [q for q in recs if q is not None and q["ok"]]
    if not r:
        return np.array([]), np.array([])
    return np.concatenate([q["x"] for q in r]), np.concatenate([q["y"] for q in r])


def stack_sim(recs, rng):
    xs, ys = [], []
    for q in recs:
        if q is not None:
            o = simulate(q, rng)
            if o is not None:
                xs.append(o[0]); ys.append(o[1])
    return (np.concatenate(xs), np.concatenate(ys)) if xs else (np.array([]), np.array([]))


def main():
    base, emb, wells, d, s1, S, L = E.load()
    q = pd.read_csv(C.WORK_DIR / "v8" / "preT_predictions.csv")
    assert (q.well.values == wells).all()
    top_sh = np.array([M.XS.TOP_SHETLAND[w] for w in wells])
    tert = d < top_sh
    photo_t = np.where(S, s1.pred_RD.values, np.nan)
    photo_p = np.where(q.in_P.values.astype(bool), q.pred_P.values, np.nan)
    var = {"sial": L["SI"] - L["AL"], "k": L["K"]}
    cas = pd.read_csv("results/v3/sodir_casing_table.csv", encoding="utf-8-sig"); cas["wlbName"] = cas.wlbName.str.strip()
    core = pd.read_csv("results/v4/sodir_core_table.csv", encoding="utf-8-sig"); core["wlbName"] = core.wlbName.str.strip()
    ft = core.wlbCoreIntervalUom.astype(str).str.contains("ft")
    for c in ("wlbCoreIntervalTop", "wlbCoreIntervalBottom"):
        core[c] = np.where(ft, core[c] * 0.3048, core[c])

    # bag intervals and ideal-bag gamma ray
    a = np.full(len(d), np.nan)
    for w in np.unique(wells):
        iv = ML.bag_intervals(w)
        mp = dict(zip(np.round(iv.b.values, 2), iv.a.values))
        a[wells == w] = [mp.get(round(float(x), 2), np.nan) for x in d[wells == w]]
    K9c = import_module("68_v9_checks")
    grm, _ = K9c.gr_interval_mean(wells, a, d)
    var["ideal"] = grm

    steps, recs, rsd = [], {v: [] for v in VARS}, {}
    for w in sorted(np.unique(wells)):
        if w not in C.GR_SOURCES:
            continue
        rel, rng_ = C.GR_SOURCES[w]
        gr = L3.load_gr(C.SSD_ROOT / "Wells" / rel, rng_)
        z, v = gr.index.values.astype(float), gr.values.astype(float)
        cand, rsd[w] = find_steps(z, v)
        mw = wells == w
        dw = d[mw]
        shoes = np.unique(cas[cas.wlbName == E.sodir(w)].wlbCasingDepth.values.astype(float))
        cores = core[core.wlbName == E.sodir(w)][["wlbCoreIntervalTop", "wlbCoreIntervalBottom"]].values
        for st in cand:
            zz = st["z"]
            why = ("not sharp" if st["sharp"] < SHARP_FRAC else
                   "near casing shoe" if len(shoes) and np.min(np.abs(shoes - zz)) < SHOE_M else
                   "cored" if any(lo <= zz <= hi for lo, hi in cores) else
                   "outside photographed range" if (zz - PLAT[1] < dw.min() or zz + PLAT[1] > dw.max()) else "")
            row = {"well": w, **st, "excluded": why}
            if not why:
                x = dw - zz
                side = tert[mw] == (zz < M.XS.TOP_SHETLAND[w])       # photo: only bags of the model that covers the step
                ph = np.where(side, np.where(zz < M.XS.TOP_SHETLAND[w], photo_t[mw], photo_p[mw]), np.nan)
                for name in VARS:
                    vv = ph if name == "photo" else var[name][mw]
                    r = step_record(x, vv, grm[mw])
                    if r is not None:
                        r["well"], r["z"] = w, zz
                    recs[name].append(r)
                    row[f"{name}_candidate"], row[f"{name}_in_stack"] = r is not None, bool(r is not None and r["ok"])
            steps.append(row)
    ST = pd.DataFrame(steps)
    OUT.mkdir(parents=True, exist_ok=True)
    ST.round(3).to_csv(OUT / "R_steps.csv", index=False)

    rng = np.random.default_rng(20261112)
    res = {"steps found (gamma ray only)": int(len(ST)), "excluded": ST.excluded.replace("", "kept").value_counts().to_dict(),
           "kept per well": ST[ST.excluded == ""].well.value_counts().sort_index().to_dict(), "variables": {}}
    rows = []
    for name in VARS:
        R = [r for r in recs[name] if r is not None]
        x, y = stack(R)
        x0, W, b = fit(x, y)
        sims = np.array([fit(*stack_sim(R, rng)) for _ in range(NNOISE)])
        res["variables"][NAMES[name]] = {
            "candidate steps": len(R), "steps in stack": int(sum(r["ok"] for r in R)), "wells in stack": len({r["well"] for r in R if r["ok"]}),
            "bags in stack": int(len(x)), "lag_x0_m": x0, "width_10_90_m": W, "amplitude_b": b,
            "noise-matched ideal: width_m (median of draws)": float(np.nanmedian(sims[:, 1])), "noise-matched ideal: lag_m": float(np.nanmedian(sims[:, 0])),
            "noise-matched ideal: amplitude": float(np.nanmedian(sims[:, 2]))}
        for r in R:
            if r["ok"]:
                rows.append(pd.DataFrame({"var": name, "well": r["well"], "step_z": r["z"], "x": r["x"], "y": r["y"]}))
    pd.concat(rows).round(4).to_csv(OUT / "R_stack.csv", index=False)

    # paired bootstrap over wells
    wl = sorted({r["well"] for v in VARS for r in recs[v] if r is not None})
    bywell = {v: {w: [r for r in recs[v] if r is not None and r["well"] == w] for w in wl} for v in VARS}
    common = {w: [(a_, b_) for a_, b_ in zip(recs["photo"], recs["sial"])
                  if a_ is not None and b_ is not None and a_["ok"] and b_["ok"] and a_["well"] == w] for w in wl}
    pc = [p for w in wl for p in common[w]]
    res["photo vs Si/Al on common steps"] = {"common steps": len(pc), "width photo m": fit(*stack([p[0] for p in pc]))[1],
                                             "width Si/Al m": fit(*stack([p[1] for p in pc]))[1]}
    B = {v: [] for v in VARS}
    Bc, fails = [], 0
    for _ in range(NBOOT):
        pick = rng.choice(wl, len(wl), replace=True)
        for v in VARS:
            R = [r for w in pick for r in bywell[v][w]]
            x0, W, _ = fit(*stack(R))
            x00, W0, _ = fit(*stack_sim(R, rng))
            B[v].append((W, W0, W - W0, x0, x0 - x00))
            fails += not np.isfinite(W)
        P = [p for w in pick for p in common[w]]
        Bc.append(fit(*stack([p[0] for p in P]))[1] - fit(*stack([p[1] for p in P]))[1])
    ci = lambda a_: [float(np.nanpercentile(a_, 2.5)), float(np.nanpercentile(a_, 97.5))]
    for v in VARS:
        arr = np.array(B[v], float)
        res["variables"][NAMES[v]].update({"width 95 % interval m": ci(arr[:, 0]), "W minus noise-matched W0: 95 % interval m": ci(arr[:, 2]),
                                           "W minus noise-matched W0: median m": float(np.nanmedian(arr[:, 2])),
                                           "lag minus noise-matched lag: 95 % interval m": ci(arr[:, 4]),
                                           "smearing detected (interval of W - W0 excludes zero)": bool(np.nanpercentile(arr[:, 2], 2.5) > 0)})
    res["photo vs Si/Al on common steps"]["W_photo - W_Si/Al: 95 % interval m"] = ci(np.array(Bc, float))
    lo_, hi_ = res["photo vs Si/Al on common steps"]["W_photo - W_Si/Al: 95 % interval m"]
    res["photo vs Si/Al on common steps"]["wording"] = ("as fast as the chemistry" if lo_ <= 0 <= hi_ else "slower than the chemistry" if lo_ > 0 else "faster than the chemistry")
    res["bootstrap"] = {"resamples": NBOOT, "wells": wl, "failed fits": int(fails)}
    res["robust SD of gamma ray per well"] = rsd
    with open(OUT / "R_results.json", "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
