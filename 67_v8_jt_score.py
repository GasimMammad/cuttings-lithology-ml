"""
v8 part D (V8_PLAN.md with amendments): Jurassic-Triassic mud-log labels.
Readers JA (all tiles) and JB (seeded 20 %) -> bag labels -> G2 -> eligibility
-> G3 -> photograph tests. Written and committed before any reading was scored.

Stages (run in this order; photographs enter only at `photo`):
  check            format problems in the readings
  g2 [well ...]    reader agreement gates on these wells (default: all read)
  labels           bag labels of reader JA
  elig             eligibility (labels only)
  g3 [well ...]    label against measured Si/Al (no photographs)
  photo            the frozen photograph predictions against the label
"""
import json
import sys
from importlib import import_module

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon

import config as C

L = import_module("57_v7_mudlog_labels")
T = import_module("58_v7_mudlog_tests")
E = import_module("63_v8_elements_when")
M = E.M
SRC = C.WORK_DIR / "v7" / "step3"
OUT = C.WORK_DIR / "v8"
CL = L.CLASSES + ["ssst"]
PILOT = ("34_7-10", 2510.0, 2670.0)
TWINS = ["34_8-3", "34_8-3_A"]


# ------------------------------------------------------------------ readings
def read_reader(reader):
    rows, problems = [], []
    idx = pd.read_csv(SRC / "tiles_jt" / "index.csv").set_index("tile")
    for f in sorted((SRC / "readers" / reader).glob("*/out.jsonl")):
        seen = {}
        for ln in f.read_text().splitlines():
            if not ln.strip():
                continue
            try:
                j = json.loads(ln)
            except json.JSONDecodeError as e:
                problems.append((reader, f.parent.name, "bad json", str(e)[:60]))
                continue
            seen[j["tile"]] = j
        for t in (f.parent / "list.txt").read_text().split():
            if t not in seen:
                problems.append((reader, f.parent.name, "missing tile", t))
        for t, j in seen.items():
            if t not in idx.index:
                problems.append((reader, f.parent.name, "unknown tile", t))
                continue
            top, bot, well = idx.loc[t, "top_m"], idx.loc[t, "bottom_m"], idx.loc[t, "well"]
            bl = sorted(j.get("blocks", []), key=lambda b: b["top"])
            if bl and bl[0]["top"] == 0 and bl[-1]["bottom"] == bot - top:  # tile-relative depths (as in step 3)
                bl = [{**x, "top": x["top"] + top, "bottom": x["bottom"] + top} for x in bl]
                problems.append((reader, f.parent.name, "relative depths shifted (format fix)", t))
            # format fix (disclosed, added 2026-11-12 before any scoring): a reader may run a block past the
            # green line; blocks are clipped to the tile's 40 m and anything wholly outside is dropped
            if bl and (bl[0]["top"] < top - 0.5 or bl[-1]["bottom"] > bot + 0.5):
                problems.append((reader, f.parent.name, "blocks clipped to the tile (format fix)", t))
            bl = [{**x, "top": max(x["top"], top), "bottom": min(x["bottom"], bot)} for x in bl]
            bl = [x for x in bl if x["bottom"] > x["top"]]
            if not bl or abs(bl[0]["top"] - top) > 1 or abs(bl[-1]["bottom"] - bot) > 1:
                problems.append((reader, f.parent.name, "does not span tile", t))
            for a, b in zip(bl[:-1], bl[1:]):
                if abs(a["bottom"] - b["top"]) > 0.5:
                    problems.append((reader, f.parent.name, "gap or overlap", f"{t} at {a['bottom']}"))
            for b in bl:
                flag = b.get("flag", "") or ""
                r = {"well": well, "tile": t, "top": float(b["top"]), "bottom": float(b["bottom"]), "flag": flag,
                     "unsure": bool(b.get("unsure", False)), "masked": flag.startswith("mask")}
                for c in CL:
                    r[c] = float(b.get(c, 0) or 0)
                tot = sum(r[c] for c in CL)
                if not r["masked"] and abs(tot - 100) > 1:
                    problems.append((reader, f.parent.name, f"sums to {tot:.0f}", f"{t} {b['top']}-{b['bottom']}"))
                rows.append(r)
    return pd.DataFrame(rows), pd.DataFrame(problems, columns=["reader", "folder", "problem", "detail"])


def aggregate(blocks, a, b):
    """Length-weighted class means over (a, b], as step 3 (cover >= 0.80), with the extra class ssst."""
    ov = np.clip(np.minimum(blocks.bottom.values, b) - np.maximum(blocks.top.values, a), 0, None)
    if ov.sum() < 0.999 * (b - a):
        return None
    bad = blocks.masked.values | (blocks.flag.values == "faded")
    w = np.where(bad, 0.0, ov)
    usable = w.sum() - (w * blocks.unread.values / 100.0).sum()
    if usable < L.MIN_COVER * (b - a):
        return None
    r = {c: float((w * blocks[c].values).sum() / w.sum()) for c in CL}
    r["cover"] = float(usable / (b - a))
    return r


def bag_table(blocks, per_tile=False):
    rows = []
    for well, g in blocks.groupby("well"):
        iv = L.bag_intervals(well)
        for t, gt in (g.groupby("tile") if per_tile else [(None, g)]):
            lo, hi = gt.top.min(), gt.bottom.max()
            for r in iv[(iv.b > lo) & (iv.a < hi)].itertuples():
                if per_tile and not (lo - 1e-6 <= r.a and r.b <= hi + 1e-6):
                    continue
                v = aggregate(gt, r.a, r.b)
                if v is not None:
                    rows.append({"well": well, "depth_m": r.b, "a": r.a, "tile": t, **v})
    t = pd.DataFrame(rows)
    t["sandy"] = t.sand + t.ssst  # primary: silty sandstone counts as sand
    return t


# ------------------------------------------------------------------ G2
def g2(wells=None):
    A, _ = read_reader("JA")
    B, _ = read_reader("JB")
    if wells:
        A, B = A[A.well.isin(wells)], B[B.well.isin(wells)]
    common = sorted(set(A.tile) & set(B.tile))
    ta, tb = bag_table(A[A.tile.isin(common)], True), bag_table(B[B.tile.isin(common)], True)
    m = ta.merge(tb, on=["well", "depth_m", "a", "tile"], suffixes=("_A", "_B"))
    d = m.sandy_A - m.sandy_B
    res = {"wells": sorted(m.well.unique()), "n_tiles_common": len(common), "n_bag_intervals": int(len(m)),
           "n_only_one_reader_usable": int(len(ta) + len(tb) - 2 * len(m)),
           "pooled_spearman": float(spearmanr(m.sandy_A, m.sandy_B)[0]),
           "share_diff_gt20": float((d.abs() > 20).mean()), "mean_signed_diff": float(d.mean()),
           "mean_abs_diff": float(d.abs().mean())}
    a20, b20 = m.sandy_A >= 20, m.sandy_B >= 20
    res["presence_A20_then_B10"] = float((m.sandy_B[a20] >= 10).mean()) if a20.any() else None
    res["presence_B20_then_A10"] = float((m.sandy_A[b20] >= 10).mean()) if b20.any() else None
    inf = (m.sandy_A >= 10) | (m.sandy_B >= 10)
    res["informative"] = {"n": int(inf.sum()), "mean_abs_diff": float(d[inf].abs().mean()) if inf.any() else None,
                          "spearman": float(spearmanr(m.sandy_A[inf], m.sandy_B[inf])[0]) if inf.sum() > 2 else None}
    per = {}
    for w, g in m.groupby("well"):
        dd = g.sandy_A - g.sandy_B
        ok = len(g) >= 15 and g.sandy_A.nunique() > 1 and g.sandy_B.nunique() > 1
        per[w] = {"n": int(len(g)), "spearman": float(spearmanr(g.sandy_A, g.sandy_B)[0]) if ok else None,
                  "mean_abs_diff": float(dd.abs().mean()), "bias_A_minus_B": float(dd.mean())}
        per[w]["ok"] = bool(per[w]["spearman"] >= 0.60) if per[w]["spearman"] is not None else bool(per[w]["mean_abs_diff"] <= 10)
    res["per_well"] = per
    res["class_presence"] = {c: {"both": int(((m[c + "_A"] >= 10) & (m[c + "_B"] >= 10)).sum()),
                                 "A_only": int(((m[c + "_A"] >= 10) & (m[c + "_B"] < 10)).sum()),
                                 "B_only": int(((m[c + "_A"] < 10) & (m[c + "_B"] >= 10)).sum())} for c in CL}
    gates = {"pooled_spearman>=0.80": res["pooled_spearman"] >= 0.80, "share_diff_gt20<=0.15": res["share_diff_gt20"] <= 0.15,
             "|mean_signed_diff|<=5": abs(res["mean_signed_diff"]) <= 5,
             "presence_both_ways>=0.80": min(res["presence_A20_then_B10"] or 0, res["presence_B20_then_A10"] or 0) >= 0.80,
             "informative_n>=30": res["informative"]["n"] >= 30,
             "informative_mad<=10": (res["informative"]["mean_abs_diff"] or 99) <= 10,
             "informative_spearman>=0.60": (res["informative"]["spearman"] or -1) >= 0.60,
             "wells_ok": all(v["ok"] for v in per.values())}
    res["gates"] = {k: bool(v) for k, v in gates.items()}
    res["G2_pass"] = bool(all(gates.values()))
    tag = "_" + "+".join(wells) if wells else ""
    OUT.mkdir(parents=True, exist_ok=True)
    m.to_csv(OUT / f"jt_G2_bag_intervals{tag}.csv", index=False)
    with open(OUT / f"jt_G2_results{tag}.json", "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("per_well", "class_presence")}, indent=1))
    print(pd.DataFrame(per).T.to_string())
    print(pd.DataFrame(res["class_presence"]).T.to_string())


# ------------------------------------------------------------------ labels, sets
def labels():
    A, prob = read_reader("JA")
    t = bag_table(A)
    t["Y"] = t.sandy / 100.0
    t["Y_sand_only"] = t.sand / 100.0
    t["Y_with_silt"] = (t.sand + t.ssst + t.silt) / 100.0
    t["Y_carb"] = (t.carb + 0.5 * t.marl) / 100.0
    OUT.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT / "jt_bag_labels_A.csv", index=False)
    print(t.groupby("well").agg(n=("Y", "count"), mean_sandy=("sandy", "mean"), mean_ssst=("ssst", "mean"), mean_silt=("silt", "mean"),
                                mean_carb=("carb", "mean"), mean_coal=("coal", "mean")).round(1).to_string())


def load(wells_only=None):
    base, emb, wells, d, s1, S, Lg = E.load()
    q = pd.read_csv(OUT / "preT_predictions.csv")
    assert (q.well.values == wells).all()
    lab = pd.read_csv(OUT / "jt_bag_labels_A.csv")
    lab["depth_m"] = lab.depth_m.round(2)
    t = pd.DataFrame({"well": wells, "depth_m": np.round(d, 2)}).merge(
        lab.drop(columns=["a", "tile"]), on=["well", "depth_m"], how="left")
    assert len(t) == len(wells)
    J = q.in_J.values.astype(bool) & np.isfinite(t.Y.values)
    if wells_only:
        J &= np.isin(wells, wells_only)
    return wells, d, q, t, J, Lg


def hp(d, v, m, grp):
    return M.highpass(d[m], v[m], groups=grp[m])  # stretches split at every casing shoe


def per_well(pred, y, wells, d, sel, grp, ws):
    out = {}
    for w in ws:
        m = sel & (wells == w) & np.isfinite(pred) & np.isfinite(y)
        if m.sum() >= T.MIN_BAGS:
            out[w] = M.rho(hp(d, pred, m, grp), hp(d, y, m, grp))
    return pd.Series(out, dtype=float)


def eligibility(wells, d, Y, J, grp):
    rows = []
    for w in np.unique(wells[J]):
        m = J & (wells == w)
        r = {"well": w, "n_bags": int(m.sum()), "n_informative": 0, "n_clusters": 0}
        if m.sum() >= 3:
            inf = np.abs(hp(d, Y, m, grp)) >= T.INF_THR
            r.update(n_informative=int(inf.sum()), n_clusters=T.clusters(d[m][inf]), mean_Y=float(Y[m].mean()))
        r["eligible"] = bool(r["n_bags"] >= T.MIN_BAGS and r["n_informative"] >= T.MIN_INF and r["n_clusters"] >= T.MIN_CLUST)
        rows.append(r)
    return pd.DataFrame(rows)


def stage_elig():
    wells, d, q, t, J, Lg = load()
    e = eligibility(wells, d, t.Y.values, J, q.n_shoes_above.values)
    e.to_csv(OUT / "jt_eligibility.csv", index=False)
    n = int(e.eligible.sum())
    with open(OUT / "jt_set_of_record.json", "w") as f:
        json.dump({"n_eligible": n, "min_wells": T.MIN_WELLS, "test": bool(n >= T.MIN_WELLS),
                   "eligible_wells": e[e.eligible].well.tolist(), "n_bags_J_with_label": int(J.sum())}, f, indent=1)
    print(e.round(3).to_string(index=False))
    print(f"eligible wells: {n} -> {'TEST' if n >= T.MIN_WELLS else 'descriptive only'}")


def stage_g3(ws=None):
    wells, d, q, t, J, Lg = load()
    ws = ws or sorted(np.unique(wells[J]))
    s = per_well(q.T1_J.values, t.Y.values, wells, d, J, q.n_shoes_above.values, ws)
    r = T.summ(s)
    r["stop"] = bool(r.get("median", s.median() if len(s) else 0) <= 0)
    r["median_all"] = float(s.median()) if len(s) else None
    tag = "_" + "+".join(ws) if len(ws) < len(np.unique(wells[J])) else ""
    with open(OUT / f"jt_G3_results{tag}.json", "w") as f:
        json.dump(r, f, indent=1)
    print(json.dumps(r, indent=1))


def stage_photo():
    wells, d, q, t, J, Lg = load()
    grp = q.n_shoes_above.values
    e = pd.read_csv(OUT / "jt_eligibility.csv")
    el = e[e.eligible].well.tolist()
    Y = t.Y.values
    pw = lambda pred, y=Y, sel=J, ws=el: per_well(pred, y, wells, d, sel, grp, ws)
    res = {"eligible_wells": el, "test_made": bool(len(el) >= T.MIN_WELLS)}
    prim = pw(q.pred_P.values)
    r = T.summ(prim)
    r["success"] = bool(len(el) >= T.MIN_WELLS and r.get("wilcoxon_p", 1) < 0.05 and r.get("median", 0) >= 0.10)
    res["PRIMARY step-1 pre-Tertiary R-D prediction vs Y"] = r
    res["context: R-E (colour and texture) vs Y"] = T.summ(pw(q.pred_P_RE.values))
    ref = pw(q.T1_J.values)
    res["context: measured Si/Al vs Y (G3)"] = T.summ(ref)
    par = {}
    for w in el:
        m = J & (wells == w) & np.isfinite(q.pred_P.values)
        par[w] = M.partial_rho(hp(d, q.pred_P.values, m, grp), hp(d, Y, m, grp), np.column_stack([hp(d, q.T1_J.values, m, grp)]))
    res["context: partial rho of the primary given measured Si/Al"] = T.summ(pd.Series(par))
    raw = pw(d.copy())
    dep = pd.Series({w: np.sign(raw.drop(w).mean()) * raw[w] for w in raw.index})
    res["context: relative depth, sign from the other wells"] = T.summ(dep)
    res["sensitivity: model trained on the Jurassic-Triassic range only"] = T.summ(pw(q.pred_J.values))
    notpilot = J & ~((wells == PILOT[0]) & (d >= PILOT[1]) & (d <= PILOT[2]))
    res["sensitivity: without the pilot interval 34/7-10 2510-2670 m"] = T.summ(pw(q.pred_P.values, sel=notpilot))
    clean = J & ~((t.carb.values + t.marl.values >= 30) | (t.coal.values > 0))
    res["sensitivity: without bags with carbonate+marl >= 30 % or any coal"] = T.summ(pw(q.pred_P.values, sel=clean))
    for k in ("Y_sand_only", "Y_with_silt"):
        res[f"sensitivity: {k}"] = T.summ(pw(q.pred_P.values, y=t[k].values))
    tw = prim.copy()
    if all(w in tw.index for w in TWINS):
        tw["34_8-3 pair"] = tw[TWINS].mean()
        tw = tw.drop(TWINS)
    res["sensitivity: 34/8-3 and 34/8-3 A merged as one unit"] = T.summ(tw)
    # exploratory: carbonate
    yc = t.Y_carb.values
    ok = J & np.isfinite(q.T_CaAl_P.values)
    car = {"measured Ca/Al vs mud-log carbonate": T.summ(pw(q.T_CaAl_P.values, y=yc, sel=ok)),
           "photo Ca/Al model vs mud-log carbonate": T.summ(pw(q.pred_P_CaAl.values, y=yc, sel=ok))}
    pc = {}
    for w in el:
        m = ok & (wells == w) & np.isfinite(q.pred_P_CaAl.values)
        if m.sum() >= T.MIN_BAGS:
            pc[w] = M.partial_rho(hp(d, q.pred_P_CaAl.values, m, grp), hp(d, yc, m, grp), np.column_stack([hp(d, Lg["CL"], m, grp)]))
    car["photo Ca/Al model vs mud-log carbonate, partial given Cl"] = T.summ(pd.Series(pc))
    res["EXPLORATORY carbonate (limestone + half of marl)"] = car
    with open(OUT / "jt_photo_results.json", "w") as f:
        json.dump(res, f, indent=1, default=float)
    pd.DataFrame({"well": wells, "depth_m": d, "in_J_labelled": J, "Y": Y, "pred_P": q.pred_P.values, "T1_J": q.T1_J.values})[J].to_csv(
        OUT / "jt_test_table.csv", index=False)
    for k, v in res.items():
        if isinstance(v, dict) and "per_well" in v:
            print(f"{k}: median {v.get('median', float('nan')):+.3f}, above 0 {v.get('n_above')}/{v['n_wells']}, p {v.get('wilcoxon_p', float('nan')):.4f}, "
                  f"CI {v.get('boot95_median')}  {v['per_well']}")
    print(json.dumps(res["EXPLORATORY carbonate (limestone + half of marl)"], indent=1, default=float))
    print("success:", r["success"])


def check():
    for rd in ("JA", "JB"):
        b, p = read_reader(rd)
        print(rd, "tiles", b.tile.nunique() if len(b) else 0, "blocks", len(b), "masked", int(b.masked.sum()) if len(b) else 0,
              "unsure", int(b.unsure.sum()) if len(b) else 0)
        print(p.to_string(index=False) if len(p) else "  no format problems")


if __name__ == "__main__":
    st, args = sys.argv[1], sys.argv[2:]
    {"check": check, "g2": lambda: g2(args or None), "labels": labels, "elig": stage_elig,
     "g3": lambda: stage_g3(args or None), "photo": stage_photo}[st]()
