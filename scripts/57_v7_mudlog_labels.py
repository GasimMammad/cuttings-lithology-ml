"""
v7 step 3 (V7_PLAN.md C2.3, C3, C4): from the readers' tiles to bag labels,
the reader-agreement gate G2 and the eligibility table.

Reads the readers' JSON lines, the calibration-independent bag list (photo
index and NOROG bag list: depths only), and nothing else. No photograph
content, no XRF, no wireline log.

  python 57_v7_mudlog_labels.py check      completeness and format of the readings
  python 57_v7_mudlog_labels.py g2         reader agreement at bag-interval level
  python 57_v7_mudlog_labels.py labels     bag labels from reader A + eligibility (C4)
"""
import json
import sys
from importlib import import_module

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import config as C

IT = import_module("39_v3b_interval_targets")
XS = import_module("35_v3_xrf_shallow")
OUT = C.WORK_DIR / "v7" / "step3"
CLASSES = ["clay", "sand", "silt", "carb", "marl", "glauc", "tuff", "coal", "other", "unread"]
MAX_GAP, FALLBACK = 15.0, 5.0
MIN_COVER = 0.80


def read_reader(reader):
    """All blocks of one reader as rows; later lines for the same tile win."""
    rows, problems = [], []
    idx = pd.read_csv(OUT / "tiles" / "index.csv").set_index("tile")
    for f in sorted((OUT / "readers" / reader).glob("*/out.jsonl")):
        seen = {}
        for ln in f.read_text().splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                j = json.loads(ln)
            except json.JSONDecodeError as e:
                problems.append((f.parent.name, "bad json", str(e)[:60]))
                continue
            seen[j["tile"]] = j
        want = [t for t in (f.parent / "list.txt").read_text().split() if t]
        for t in want:
            if t not in seen:
                problems.append((f.parent.name, "missing tile", t))
        for t, j in seen.items():
            if t not in idx.index:
                problems.append((f.parent.name, "unknown tile", t))
                continue
            top, bot, well = idx.loc[t, "top_m"], idx.loc[t, "bottom_m"], idx.loc[t, "well"]
            bl = sorted(j.get("blocks", []), key=lambda b: b["top"])
            # format fix (disclosed): one reader batch wrote depths relative to the tile top (0-40),
            # copying the made-up example in the rules. Shift them to absolute depth.
            if bl and top > 0 and bl[0]["top"] == 0 and bl[-1]["bottom"] == bot - top:
                bl = [{**x, "top": x["top"] + top, "bottom": x["bottom"] + top} for x in bl]
                problems.append((f.parent.name, "relative depths shifted (format fix)", t))
            if not bl or abs(bl[0]["top"] - top) > 1 or abs(bl[-1]["bottom"] - bot) > 1:
                problems.append((f.parent.name, "does not span tile", t))
            for a, b in zip(bl[:-1], bl[1:]):
                if abs(a["bottom"] - b["top"]) > 0.5:
                    problems.append((f.parent.name, "gap or overlap", f"{t} at {a['bottom']}"))
            for b in bl:
                flag = b.get("flag", "") or ""
                r = {"well": well, "tile": t, "top": float(b["top"]), "bottom": float(b["bottom"]), "flag": flag,
                     "unsure": bool(b.get("unsure", j.get("unsure", False)))}
                tot = 0.0
                for c in CLASSES:
                    r[c] = float(b.get(c, 0) or 0)
                    tot += r[c]
                if not flag.startswith("mask") and abs(tot - 100) > 1:
                    problems.append((f.parent.name, f"sums to {tot:.0f}", f"{t} {b['top']}-{b['bottom']}"))
                r["masked"] = flag.startswith("mask")
                rows.append(r)
    return pd.DataFrame(rows), pd.DataFrame(problems, columns=["folder", "problem", "detail"])


def bag_intervals(well):
    """(D_prev, D] for every W_1 photo depth; bag sequence as in v3b."""
    idx = pd.read_csv(C.WORK_DIR / "02_index.csv")
    d = np.round(idx[(idx.well == well) & idx.stem.str.endswith("_W_1")].depth_m.values.astype(float), 2)
    bags = IT.bag_depths(well, d)
    out = []
    for D in np.unique(d):
        k = np.searchsorted(bags, D)
        prev = bags[k - 1] if k > 0 else np.nan
        if not np.isfinite(prev) or D - prev > MAX_GAP:
            prev = D - FALLBACK
        out.append((prev, D))
    return pd.DataFrame(out, columns=["a", "b"]).assign(well=well)


def aggregate(blocks, a, b, use_faded=False):
    """Length-weighted class means over (a, b]; None if too little is usable."""
    ov = np.clip(np.minimum(blocks.bottom.values, b) - np.maximum(blocks.top.values, a), 0, None)
    if ov.sum() < 0.999 * (b - a):
        return None  # interval not fully inside the digitised range
    bad = blocks.masked.values | ((blocks.flag.values == "faded") & (not use_faded))
    w = np.where(bad, 0.0, ov)
    unread = (w * blocks.unread.values / 100.0).sum()
    usable = w.sum() - unread
    if usable < MIN_COVER * (b - a):
        return None
    r = {c: float((w * blocks[c].values).sum() / w.sum()) for c in CLASSES}
    r["cover"] = float(usable / (b - a))
    return r


def bag_table(blocks, wells=None, tiles=None, use_faded=False):
    rows = []
    for well, g in blocks.groupby("well"):
        if wells is not None and well not in wells:
            continue
        iv = bag_intervals(well)
        for t, gt in (g.groupby("tile") if tiles is not None else [(None, g)]):
            for r in iv.itertuples():
                if tiles is not None:  # agreement: only bags lying wholly inside this tile
                    if not (gt.top.min() - 1e-6 <= r.a and r.b <= gt.bottom.max() + 1e-6):
                        continue
                v = aggregate(gt, r.a, r.b, use_faded)
                if v is not None:
                    rows.append({"well": well, "depth_m": r.b, "a": r.a, "tile": t, **v})
    return pd.DataFrame(rows)


FIX_WELL = "24_9-3"  # the one well re-read after the first G2 pass (V7_PLAN.md C3)


def readers(fix):
    """Reader of record and checking reader. After the fix, readers C and D
    replace A and B for FIX_WELL only."""
    A, _ = read_reader("A")
    B, _ = read_reader("B")
    if fix:
        Cc, _ = read_reader("C")
        Dd, _ = read_reader("D")
        A = pd.concat([A[A.well != FIX_WELL], Cc], ignore_index=True)
        B = pd.concat([B[B.well != FIX_WELL], Dd], ignore_index=True)
    return A, B


def g2(fix=False, drop=None):
    A, B = readers(fix)
    if drop:
        A, B = A[A.well != drop], B[B.well != drop]
    tag = ("_fix" if fix else "") + (f"_without_{drop}" if drop else "")
    common = sorted(set(A.tile) & set(B.tile))
    ta = bag_table(A[A.tile.isin(common)], tiles=True)
    tb = bag_table(B[B.tile.isin(common)], tiles=True)
    m = ta.merge(tb, on=["well", "depth_m", "a", "tile"], suffixes=("_A", "_B"))
    only = len(ta) + len(tb) - 2 * len(m)
    d = m.sand_A - m.sand_B
    res = {"n_tiles_common": len(common), "n_bag_intervals": int(len(m)), "n_only_one_reader_usable": int(only),
           "pooled_spearman": float(spearmanr(m.sand_A, m.sand_B)[0]),
           "share_diff_gt20": float((d.abs() > 20).mean()), "mean_signed_diff": float(d.mean()),
           "mean_abs_diff": float(d.abs().mean())}
    a20, b20 = m.sand_A >= 20, m.sand_B >= 20
    res["presence_A20_then_B10"] = float((m.sand_B[a20] >= 10).mean()) if a20.any() else None
    res["presence_B20_then_A10"] = float((m.sand_A[b20] >= 10).mean()) if b20.any() else None
    inf = (m.sand_A >= 10) | (m.sand_B >= 10)
    res["informative"] = {"n": int(inf.sum()), "mean_abs_diff": float(d[inf].abs().mean()) if inf.any() else None,
                          "spearman": float(spearmanr(m.sand_A[inf], m.sand_B[inf])[0]) if inf.sum() > 2 else None}
    per = {}
    for w, g in m.groupby("well"):
        dd = g.sand_A - g.sand_B
        ok = len(g) >= 15 and g.sand_A.nunique() > 1 and g.sand_B.nunique() > 1
        per[w] = {"n": int(len(g)), "spearman": float(spearmanr(g.sand_A, g.sand_B)[0]) if ok else None,
                  "mean_abs_diff": float(dd.abs().mean()), "bias_A_minus_B": float(dd.mean()),
                  "n_informative": int(((g.sand_A >= 10) | (g.sand_B >= 10)).sum())}
    res["per_well"] = per
    # class presence (>= 10 %) confusion over the common bag intervals
    pres = {c: {"both": int(((m[c + "_A"] >= 10) & (m[c + "_B"] >= 10)).sum()),
                "A_only": int(((m[c + "_A"] >= 10) & (m[c + "_B"] < 10)).sum()),
                "B_only": int(((m[c + "_A"] < 10) & (m[c + "_B"] >= 10)).sum())} for c in CLASSES}
    res["class_presence"] = pres
    # reader A test-retest at tile seams: composition just above against just below, no step drawn there
    seams = []
    for w, g in A.groupby("well"):
        g = g.sort_values("top")
        tops = sorted(g.groupby("tile").top.min())
        for s_ in tops[1:]:
            up, dn = g[np.isclose(g.bottom, s_)], g[np.isclose(g.top, s_)]
            if len(up) == 1 and len(dn) == 1 and not up.masked.iloc[0] and not dn.masked.iloc[0]:
                seams.append(abs(up.sand.iloc[0] - dn.sand.iloc[0]))
    seams = np.array(seams)
    res["A_seams"] = {"n": int(len(seams)), "share_sand_differs_ge10": float((seams >= 10).mean()) if len(seams) else None}
    gates = {"pooled_spearman>=0.80": res["pooled_spearman"] >= 0.80, "share_diff_gt20<=0.15": res["share_diff_gt20"] <= 0.15,
             "|mean_signed_diff|<=5": abs(res["mean_signed_diff"]) <= 5,
             "presence_both_ways>=0.80": min(res["presence_A20_then_B10"] or 0, res["presence_B20_then_A10"] or 0) >= 0.80,
             "informative_n>=30": res["informative"]["n"] >= 30,
             "informative_mad<=10": (res["informative"]["mean_abs_diff"] or 99) <= 10,
             "informative_spearman>=0.60": (res["informative"]["spearman"] or -1) >= 0.60,
             "wells_ok": all((v["spearman"] >= 0.60) if v["spearman"] is not None else (v["mean_abs_diff"] <= 10) for v in per.values())}
    res["gates"] = {k: bool(v) for k, v in gates.items()}
    res["G2_pass"] = bool(all(gates.values()))
    m.to_csv(OUT / f"G2_bag_intervals{tag}.csv", index=False)
    with open(OUT / f"G2_results{tag}.json", "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("per_well", "class_presence")}, indent=1))
    print(pd.DataFrame(per).T.round(2).to_string())
    print(pd.DataFrame(pres).T.to_string())


def labels(fix=False, drop=None):
    A, _ = readers(fix)
    if drop:
        A = A[A.well != drop]
    t = bag_table(A)
    f = bag_table(A, use_faded=True)[["well", "depth_m", "sand"]].rename(columns={"sand": "sand_with_faded"})
    t = t.merge(f, on=["well", "depth_m"], how="outer")
    t["Y"] = t.sand / 100.0
    t["tertiary"] = t.depth_m < t.well.map(XS.TOP_SHETLAND)
    t.to_csv(OUT / "bag_labels_A.csv", index=False)
    print(t.groupby("well").agg(n=("Y", "count"), mean_sand=("sand", "mean"), n_sand_ge10=("sand", lambda x: (x >= 10).sum()),
                                n_glauc=("glauc", lambda x: (x > 0).sum()), n_faded_extra=("sand_with_faded", lambda x: x.notna().sum())).round(1).to_string())


def main():
    cmd = sys.argv[1]
    if cmd == "check":
        for r in ("A", "B", "C", "D"):
            if not (OUT / "readers" / r).exists():
                continue
            b, p = read_reader(r)
            print(r, "tiles", b.tile.nunique() if len(b) else 0, "blocks", len(b), "problems", len(p))
            if len(p):
                print(p.groupby("problem").size().to_string())
                print(p.head(25).to_string(index=False))
    elif cmd == "g2":
        g2()
    elif cmd == "g2fix":      # second pass: C and D replace A and B for the re-read well
        g2(fix=True)
    elif cmd == "g2drop":     # if the second pass fails: the re-read well is dropped
        g2(drop=FIX_WELL)
    elif cmd == "labels":     # labels [fix|drop]
        mode = sys.argv[2] if len(sys.argv) > 2 else ""
        labels(fix=mode == "fix", drop=FIX_WELL if mode == "drop" else None)


if __name__ == "__main__":
    main()
