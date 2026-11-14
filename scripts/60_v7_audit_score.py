"""
v7 extra X0: score the 17 symbol-audit tiles. Two further readings (audit
readers 1 and 2) against the reader of record (A; C for
24/9-3) and the checking reader (B; D for 24/9-3), at bag-interval level:
class presence (>= 10 %) and sand %.

Run:  python 60_v7_audit_score.py
"""
import json
from importlib import import_module

import numpy as np
import pandas as pd

import config as C

L = import_module("57_v7_mudlog_labels")
OUT = C.WORK_DIR / "v7" / "step3"
NOT_BLIND = {"24_9-3_1080.png", "34_7-10_1080.png", "34_8-3_A_1080.png"}
CL = ["clay", "sand", "silt", "carb", "marl", "glauc", "tuff", "coal"]


def read_file(path, well_of):
    rows = []
    for ln in open(path):
        if not ln.strip():
            continue
        j = json.loads(ln)
        for b in j["blocks"]:
            flag = b.get("flag", "") or ""
            r = {"well": well_of(j["tile"]), "tile": j["tile"], "top": float(b["top"]), "bottom": float(b["bottom"]),
                 "flag": flag, "masked": flag.startswith("mask"), "unsure": bool(b.get("unsure", False))}
            for c in L.CLASSES:
                r[c] = float(b.get(c, 0) or 0)
            rows.append(r)
    return pd.DataFrame(rows)


def main():
    well_of = lambda t: t.rsplit("_", 1)[0]
    tiles = [t for t in (OUT / "audit" / "reader2" / "list.txt").read_text().split() if t]
    R = {"audit reader 1": read_file(OUT / "audit" / "reader1" / "out.jsonl", well_of),
         "audit reader 2": read_file(OUT / "audit" / "reader2" / "out.jsonl", well_of)}
    A, B = L.readers(fix=True)
    R["record (A, C)"] = A[A.tile.isin(tiles)]
    R["checker (B, D)"] = B[B.tile.isin(tiles)]
    tabs = {k: L.bag_table(v, tiles=True) for k, v in R.items()}
    keys = ["well", "depth_m", "a", "tile"]
    res = {}
    for blind in (False, True):
        sub = {k: (v[~v.tile.isin(NOT_BLIND)] if blind else v) for k, v in tabs.items()}
        tag = "blind tiles only (14)" if blind else "all 17 tiles"
        out = {}
        for ref in ("record (A, C)", "checker (B, D)"):
            for new in ("audit reader 1", "audit reader 2"):
                m = sub[new].merge(sub[ref], on=keys, suffixes=("_n", "_r"))
                d = m.sand_n - m.sand_r
                pres = {}
                for c in CL:
                    a, b = m[c + "_n"] >= 10, m[c + "_r"] >= 10
                    pres[c] = {"both": int((a & b).sum()), "new_only": int((a & ~b).sum()), "ref_only": int((~a & b).sum())}
                out[f"{new} vs {ref}"] = {"n_intervals": int(len(m)), "sand_mad": float(d.abs().mean()),
                                          "sand_share_diff_gt20": float((d.abs() > 20).mean()),
                                          "sand_bias": float(d.mean()), "class_presence": pres}
        m = sub["audit reader 1"].merge(sub["audit reader 2"], on=keys, suffixes=("_n", "_r"))
        out["audit reader 1 vs audit reader 2"] = {"n_intervals": int(len(m)), "sand_mad": float((m.sand_n - m.sand_r).abs().mean())}
        res[tag] = out
    with open(OUT / "audit" / "X0_results.json", "w") as f:
        json.dump(res, f, indent=1)
    for tag, out in res.items():
        print("==", tag)
        for k, v in out.items():
            print(f"  {k:38s} n {v['n_intervals']:3d}  sand MAD {v['sand_mad']:.2f}" +
                  (f"  >20 pts {v['sand_share_diff_gt20']:.2f}  bias {v['sand_bias']:+.2f}" if "sand_bias" in v else ""))
            if "class_presence" in v:
                print("     ", {c: (x["both"], x["new_only"], x["ref_only"]) for c, x in v["class_presence"].items() if sum(x.values())})


if __name__ == "__main__":
    main()
