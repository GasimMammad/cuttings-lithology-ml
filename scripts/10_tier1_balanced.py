"""
TIER 1 part (b) -- the only CLEAN tier-1 evidence.

08_compare_models.py tests each sand body over its own depth span only, so no
labelled clay ever enters the test set and precision/balanced accuracy are
undefined (that is part (a), recall-only, and is correct as far as it goes).

Here, for the bodies that DO have labelled clay within +/-100 m, the test set
is the body's sand depths PLUS that nearby clay, and training excludes the
whole test window with a further 10 m gap. Depth-local clay only: clay from
800 m away is never used, because separating on burial, consolidation and
barite loading is exactly what tier 1 exists to exclude.

Results are appended to final_comparison/results.json as "tier1b".
"""
import json

import numpy as np
import pandas as pd

import config as C
from features import FEATURE_NAMES, COLOUR_FREE_NAMES
from importlib import import_module

cmp = import_module("08_compare_models")

CLAY_WINDOW_M = 100.0
TRAIN_GAP_M = 10.0


def main():
    device = cmp.get_device()
    f = pd.read_csv(C.WORK_DIR / "07_features.csv")
    f = f[(~f.probe_only) & f.label.isin(C.CLASSES)].dropna(subset=FEATURE_NAMES)
    bodies = json.load(open(__import__("pathlib").Path(__file__).with_name("sand_bodies.json")))
    f["in_body"] = f.apply(
        lambda r: any(a <= r.depth_m <= b for a, b in bodies.get(r.well, [])), axis=1)
    f["depth_class"] = np.where(f.depth_m < cmp.SHALLOW_MAX_M, "shallow", "deep")
    agg = {c: "median" for c in FEATURE_NAMES}
    agg.update({"in_body": "first", "depth_class": "first",
                "ba_ppm": "first", "formation": "first"})
    depths = f.groupby(["well", "depth_m", "label"], as_index=False).agg(agg)

    d24 = f[f.well == "24_9-3"]
    ds = np.sort(d24[d24.label == "sand"].depth_m.unique())
    clay24 = np.sort(d24[d24.label == "clay"].depth_m.unique())
    grp, cur = [], [ds[0]]
    for z in ds[1:]:
        if z - cur[-1] <= 12:
            cur.append(z)
        else:
            grp.append(cur)
            cur = [z]          # NB: rebind, never cur.clear() -- grp holds a
    grp.append(cur)            # reference, so clearing would empty it too
    bl = [b for b in grp if len(b) >= 3]
    print(f"{len(bl)} tier-1 bodies with >=3 sand depths", flush=True)

    out = {}
    for bi, b in enumerate(bl):
        lo, hi = min(b), max(b)
        clay_in = clay24[(clay24 >= lo - CLAY_WINDOW_M) & (clay24 <= hi + CLAY_WINDOW_M)]
        if len(clay_in) == 0:
            continue
        tlo, thi = min(lo, clay_in.min()), max(hi, clay_in.max())
        name = f"tier1b_body{bi}_{lo:.0f}-{hi:.0f}m"
        print(f"\n{name}: sand {len(b)} depths {lo:.0f}-{hi:.0f}, "
              f"clay {len(clay_in)} depths {clay_in.min():.0f}-{clay_in.max():.0f}",
              flush=True)

        in_test = lambda s: ((s.well == "24_9-3") &
                             (s.depth_m.between(lo, hi) |
                              s.depth_m.isin(clay_in)))
        in_train = lambda s: ((s.well == "24_9-3") &
                              ~s.depth_m.between(tlo - TRAIN_GAP_M, thi + TRAIN_GAP_M))

        te_p, tr_p = f[in_test(f)], f[in_train(f)]
        te_d, tr_d = depths[in_test(depths)], depths[in_train(depths)]
        print(f"   train {tr_d.label.value_counts().to_dict()} | "
              f"test {te_d.label.value_counts().to_dict()}", flush=True)
        if tr_d.label.nunique() < 2:
            print("   SKIP: training set has only one class", flush=True)
            continue

        for mdl in ["cnn_colour", "cnn_gray", "eng_full", "eng_nocolour"]:
            if mdl.startswith("cnn"):
                te = cmp.train_cnn(tr_p, te_p, gray=(mdl == "cnn_gray"), device=device)
                dd = cmp.depth_table(te)
            else:
                feats = FEATURE_NAMES if mdl == "eng_full" else COLOUR_FREE_NAMES
                dd, _ = cmp.fit_engineered(tr_d, te_d, feats)
            m = cmp.metrics_from_depths(dd)
            out.setdefault(mdl, {})[name] = m
            print(f"   {mdl:13} bal {m['balanced_acc']:.3f} "
                  f"sand {m['confusion']['tp_sand']}/{m['n_sand']} "
                  f"clay recall {m['clay_recall']:.2f} "
                  f"(base {m['majority_baseline']:.2f})", flush=True)

    p = C.WORK_DIR / "final_comparison" / "results.json"
    res = json.load(open(p))
    res["tier1b"] = out
    json.dump(res, open(p, "w"), indent=2, default=float)
    print(f"\nappended tier1b to {p}")


if __name__ == "__main__":
    main()
