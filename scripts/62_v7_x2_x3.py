"""
v7 extras X2 (34/7-9 Saga log) and X3 (34/7-1 text route, 24/9-4 hand-drawn
sheets): readings -> bag labels -> agreement -> eligibility -> P2 with the new
wells added. EXPLORATORY; the closed step-3 result is not changed.

Run:  python 62_v7_x2_x3.py
"""
import json
from importlib import import_module

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import config as C

L = import_module("57_v7_mudlog_labels")
T = import_module("58_v7_mudlog_tests")
X = import_module("61_v7_x3_tiles")
M = T.M
OUT = C.WORK_DIR / "v7" / "step3"
SIDETRACK_M = 1753.0
SAND_MAP = {"main": 0.7, "interbedded": 0.3, "occ": 0.1, "trace": 0.03, "none": 0.0}
RNG = np.random.default_rng(62)


def boot_rho(a, b, block_m=50.0, d=None, n=2000):
    """Spearman with a moving-block (50 m) bootstrap CI over depth."""
    r = spearmanr(a, b)[0]
    if d is None or len(a) < 10:
        return float(r), None
    blk = np.floor((d - d.min()) / block_m).astype(int)
    ub = np.unique(blk)
    bs = []
    for _ in range(n):
        pick = RNG.choice(ub, len(ub))
        ix = np.concatenate([np.flatnonzero(blk == k) for k in pick])
        if np.unique(a[ix]).size > 1 and np.unique(b[ix]).size > 1:
            bs.append(spearmanr(a[ix], b[ix])[0])
    return float(r), [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def jsonl(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def blocks_from(rows, well):
    out = []
    for j in rows:
        for b in j.get("blocks", []):
            flag = b.get("flag", "") or ""
            r = {"well": well, "tile": j["tile"], "top": float(b["top"]), "bottom": float(b["bottom"]), "flag": flag,
                 "masked": flag.startswith("mask"), "unsure": bool(b.get("unsure", False))}
            for c in L.CLASSES:
                r[c] = float(b.get(c, 0) or 0)
            out.append(r)
    return pd.DataFrame(out)


# ---------------------------------------------------------------- X2 Saga
def x2():
    rows = jsonl(OUT / "readers" / "X2" / "34_7-9_saga_1" / "out.jsonl")
    saga = L.bag_table(blocks_from(rows, "34_7-9"))[["well", "depth_m", "sand"]].rename(columns={"sand": "sand_saga"})
    lab = pd.read_csv(OUT / "bag_labels_A.csv")
    m = lab[lab.well == "34_7-9"][["well", "depth_m", "sand"]].merge(saga, on=["well", "depth_m"])
    base, emb, wells, d, s1, t, S = T.load()
    k = pd.DataFrame({"well": wells, "depth_m": np.round(d, 2), "S": S, "T1": s1.T1.values, "P2": s1.pred_RD.values})
    m = m.assign(depth_m=m.depth_m.round(2)).merge(k, on=["well", "depth_m"], how="left")
    r_raw, ci_raw = boot_rho(m.sand.values, m.sand_saga.values, d=m.depth_m.values)
    ms = m[m.S.astype(bool)].sort_values("depth_m")
    hp = lambda v: M.highpass(ms.depth_m.values, v)
    res = {"n_bags_both": int(len(m)), "n_bags_S": int(len(ms)),
           "spearman_exlog_vs_saga": r_raw, "ci": ci_raw,
           "mean_abs_diff_points": float((m.sand - m.sand_saga).abs().mean()),
           "mean_sand_exlog": float(m.sand.mean()), "mean_sand_saga": float(m.sand_saga.mean()),
           "hp_spearman_exlog_vs_saga_S": float(M.rho(hp(ms.sand.values), hp(ms.sand_saga.values))),
           "P2_vs_saga_hp_S": float(M.rho(hp(ms.P2.values), hp(ms.sand_saga.values))),
           "P2_vs_exlog_hp_S": float(M.rho(hp(ms.P2.values), hp(ms.sand.values))),
           "SiAl_vs_saga_hp_S": float(M.rho(hp(ms.T1.values), hp(ms.sand_saga.values))),
           "SiAl_vs_exlog_hp_S": float(M.rho(hp(ms.T1.values), hp(ms.sand.values)))}
    m.to_csv(OUT / "X2_saga_vs_exlog.csv", index=False)
    return res


# ---------------------------------------------------------------- X3 34/7-1
def labels_3471(reader):
    ent = []
    for j in jsonl(OUT / "readers" / reader / "34_7-1" / "out.jsonl"):
        for e in j.get("entries", []):
            ent.append({"depth": float(e["depth"]), "main": e.get("main", "none"), "sand": e.get("sand", "none"),
                        "aa": bool(e.get("aa", False))})
    e = pd.DataFrame(ent).sort_values("depth").drop_duplicates("depth").reset_index(drop=True)
    vals, cur = [], np.nan
    for r in e.itertuples():
        if r.main == "none" and r.sand in ("none", "trace") and (r.aa or r.sand == "none"):
            vals.append(cur)  # accessory line or a/a: carry forward
            continue
        cur = SAND_MAP["main"] if r.main == "sand" else SAND_MAP.get(r.sand, 0.0)
        vals.append(cur)
    e["y"] = vals
    iv = L.bag_intervals("34_7-1")
    y = np.full(len(iv), np.nan)
    for i, r in enumerate(iv.itertuples()):
        k = np.searchsorted(e.depth.values, r.b, side="right") - 1
        if k >= 0:
            y[i] = e.y.values[k]
    return pd.DataFrame({"well": "34_7-1", "depth_m": iv.b.values, "Y": y}), e


# ---------------------------------------------------------------- X3 24/9-4
def labels_2494(reader):
    rows = jsonl(OUT / "readers" / reader / "24_9-4" / "out.jsonl")
    ix = pd.read_csv(OUT / "tiles" / "index_x3.csv")
    ix = ix[ix.well == "24_9-4"].set_index("tile")
    ok_rows, bad = [], []
    for j in rows:
        lab = [float(x) for x in j.get("labels", []) if x is not None]
        a, b = map(float, ix.loc[j["tile"], "sheet_interval"].split("-"))
        mono = all(np.diff(lab) > 0) and all(abs(np.diff(lab) - 20) < 0.5) if len(lab) > 1 else len(lab) == 1
        inside = all(a - 5 <= x <= b + 5 for x in lab) and len(lab) > 0
        bl = j.get("blocks", [])
        span_ok = bool(bl) and all(a - 10 <= x["top"] <= b + 10 and a - 10 <= x["bottom"] <= b + 10 for x in bl)
        (ok_rows if (mono and inside and span_ok) else bad).append(j["tile"] if not (mono and inside and span_ok) else j)
    blk = blocks_from(ok_rows, "24_9-4")
    blk = blk[blk.bottom <= SIDETRACK_M]
    t = L.bag_table(blk)
    return t, bad


def g2_like(a, b, key=("well", "depth_m")):
    m = a.merge(b, on=list(key), suffixes=("_A", "_B"))
    if len(m) < 3:
        return {"n": int(len(m))}
    d = m.Y_A - m.Y_B
    return {"n": int(len(m)), "spearman": float(spearmanr(m.Y_A, m.Y_B)[0]), "mean_abs_diff": float(d.abs().mean()),
            "share_diff_gt0.2": float((d.abs() > 0.2).mean()), "bias": float(d.mean())}


def main():
    res = {}
    res["X2 Saga vs Exlog (34/7-9)"] = x2()

    y71A, e71A = labels_3471("X3A")
    y71B, _ = labels_3471("X3B")
    res["X3 34/7-1 reader agreement"] = g2_like(y71A.dropna(), y71B.dropna())
    t94A, bad94A = labels_2494("X3A")
    t94B, bad94B = labels_2494("X3B")
    y94A = t94A.assign(Y=t94A.sand / 100.0)[["well", "depth_m", "Y"]]
    y94B = t94B.assign(Y=t94B.sand / 100.0)[["well", "depth_m", "Y"]]
    res["X3 24/9-4 reader agreement"] = g2_like(y94A, y94B)
    res["X3 24/9-4 tiles failing the depth-label check"] = {"A": bad94A, "B": bad94B}

    # eligibility and P2 with the new wells added (labels of reader A)
    base, emb, wells, d, s1, t, S = T.load()
    new = pd.concat([y71A, y94A])
    new["depth_m"] = new.depth_m.round(2)
    k = pd.DataFrame({"well": wells, "depth_m": np.round(d, 2)}).merge(new, on=["well", "depth_m"], how="left")
    Y = t.Y.values.copy()
    m_new = np.isin(wells, ["34_7-1", "24_9-4"])
    Y[m_new] = k.Y.values[m_new]
    S2 = s1.in_S.values.astype(bool) & np.isfinite(Y) & ~((wells == "24_9-4") & (d > SIDETRACK_M))
    e = T.eligibility(wells, d, Y, S2)
    res["X3 eligibility (all wells, labels A)"] = e.round(3).to_dict(orient="records")
    elig6 = pd.read_csv(OUT / "C4_eligibility.csv").query("eligible").well.tolist()
    add = [w for w in ("34_7-1", "24_9-4") if w in e[e.eligible].well.tolist()]
    res["X3 new wells eligible"] = add
    for tag, ws in (("P2, closed six wells (for reference)", elig6), ("P2 with eligible new wells added", elig6 + add)):
        s = T.per_well(s1.pred_RD.values, Y, wells, d, S2, ws)
        res[tag] = T.summ(s)
    if add:
        res["reference Si/Al, new wells"] = T.per_well(s1.T1.values, Y, wells, d, S2, add).round(4).to_dict()
    with open(OUT / "X2_X3_results.json", "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
