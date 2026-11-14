"""
v4 DESCRIPTIVE sensitivity (review round 7): the 24/9-3 core (1778-1797 m,
plugs ~3 D, phi 38%) shows that zone r3_upper's GR labels can call a clean
Frigg sand "clay" (anchors 19 / 35 API). v2 primary rerun with all r3_upper
labels removed from training AND testing. The v2 primary stays as run.

Run:  python 46_v4_r3_sensitivity.py
"""
from importlib import import_module

import numpy as np

EV = import_module("29_v2_evaluate")


def main():
    base, emb = EV.load_tables()
    print("r3_upper labels:", base[(base.well == "24_9-3") & (base.zone_name == "r3_upper")].label.value_counts().to_dict())
    inputs = EV.build_inputs(base, emb)
    b2 = base.copy()
    m = (b2.well == "24_9-3") & (b2.zone_name == "r3_upper") & b2.label.isin(["sand", "clay"])
    b2.loc[m, "label"] = "excluded_r3"
    allm = np.ones(len(b2), bool)
    for name in ("E2", "D1", "E1"):
        X, pca = inputs[name]
        for tag, bb in (("v2 as run", base), ("r3_upper dropped", b2)):
            p, _ = EV.lowo(bb, X, pca, allm)
            st = EV.primary_stats(EV.per_well_table(bb, p, allm, name))
            print(f"{name} {tag:17}: median AUC {st['median_auc']:.3f} mean {st['mean_auc']:.3f} "
                  f"{st['n_above_0p5']}/{st['n_wells']} p {st['wilcoxon_p_one_sided']:.4f}  24_9-3 AUC {st['auc'].get('24_9-3')}")


if __name__ == "__main__":
    main()
