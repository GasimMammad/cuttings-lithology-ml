"""
FINAL ITERATION -- three-way model comparison on IDENTICAL folds.

Models (all evaluated on exactly the same folds, same metrics):
  cnn_colour     ResNet18 on RGB patches                     (B1)
  cnn_gray       ResNet18 on greyscale patches                (B2)  forces the
                 model off the global colour shortcut
  eng_full       L2 logistic regression, 15 frozen features   (B3)
  eng_nocolour   same, colour block removed (9 features)      CO-PRIMARY

Plus block ablations of the engineered model (free_grain / quartz / texture /
colour removed in turn) -- four robust numbers instead of sixteen unstable
L2-shrunk coefficients at 5.7 events per variable.

AGGREGATION (amendment 4): the 16 patches of a photo are combined to the depth
level by MEDIAN, for every model, so one patch catching a shadow or a tray edge
cannot drag the value. For the CNNs the median is taken over patch p_sand; for
the engineered models the median is taken over the patch feature vectors and
the classifier is fitted at the depth level (n = 448 depths).

TIER 1 REPORTING: 24_9-3's clay labels cluster at 240-260 m and
below 2065 m -- that is where lithologies are clean enough to label
confidently, i.e. the stratigraphy of the well, not a design flaw. Precision is
therefore NOT built from depth-distant clay (that would let the model separate
on burial, consolidation and barite loading rather than lithology). We report:
  (a) RECALL across all bodies, never called accuracy, caveat in the table;
  (b) full metrics + CIs for the bodies with labelled clay within +/-100 m;
  (c) an explicit statement for the remainder.

Run:  python 08_compare_models.py
"""

import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from PIL import Image
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

import config as C
from features import FEATURE_BLOCKS, FEATURE_NAMES, COLOUR_FREE_NAMES

OUT_DIR = C.WORK_DIR / "final_comparison"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SHALLOW_MAX_M = 700.0          # A3 split
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


# =============================================================================
# helpers
# =============================================================================
def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def depth_table(df, prob_col="p_sand"):
    """Collapse patches -> depths by MEDIAN (amendment 4)."""
    g = (df.groupby(["well", "depth_m", "label"], as_index=False)
           .agg(p_sand=(prob_col, "median"),
                in_body=("in_body", "first"),
                depth_class=("depth_class", "first"),
                ba_ppm=("ba_ppm", "first"),
                formation=("formation", "first")))
    g["pred_label"] = np.where(g.p_sand > 0.5, "sand", "clay")
    return g


def metrics_from_depths(d):
    y = (d.label == "sand").astype(int).values
    p = (d.pred_label == "sand").astype(int).values
    if len(y) == 0:
        return None
    cm = confusion_matrix(y, p, labels=[0, 1])
    tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])
    n_sand, n_clay = int((y == 1).sum()), int((y == 0).sum())
    return {
        "n_depths": len(d), "n_sand": n_sand, "n_clay": n_clay,
        "majority_baseline": float(max(n_sand, n_clay) / len(d)),
        "acc": float((y == p).mean()),
        "balanced_acc": (float(balanced_accuracy_score(y, p))
                         if n_sand and n_clay else float("nan")),
        "sand_recall": tp / n_sand if n_sand else float("nan"),
        "sand_recall_ci95": wilson(tp, n_sand),
        "sand_precision": tp / (tp + fp) if (tp + fp) else float("nan"),
        "sand_precision_ci95": wilson(tp, tp + fp) if (tp + fp) else (float("nan"),) * 2,
        "clay_recall": tn / n_clay if n_clay else float("nan"),
        "confusion": {"tn_clay": tn, "fp": fp, "fn": fn, "tp_sand": tp},
    }


# =============================================================================
# CNN
# =============================================================================
class PatchDS(Dataset):
    def __init__(self, df, tf):
        self.df = df.reset_index(drop=True)
        self.tf = tf

    def __len__(self):
        return len(self.df)

    def __getitem__(self, i):
        r = self.df.iloc[i]
        img = Image.open(r.patch_path).convert("RGB")
        return self.tf(img), int(r.label == "sand"), i


def make_tf(gray, train):
    ops = []
    if gray:
        ops.append(transforms.Grayscale(num_output_channels=3))
    if train:
        ops += [transforms.RandomHorizontalFlip(), transforms.RandomVerticalFlip(),
                transforms.RandomRotation(15)]
        if not gray:
            ops.append(transforms.ColorJitter(brightness=0.15, contrast=0.15,
                                              saturation=0.10))
    ops += [transforms.ToTensor(), transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD)]
    return transforms.Compose(ops)


def train_cnn(tr, te, gray, device):
    tr_dl = DataLoader(PatchDS(tr, make_tf(gray, True)), batch_size=C.BATCH_SIZE,
                       shuffle=True, num_workers=C.NUM_WORKERS,
                       persistent_workers=C.NUM_WORKERS > 0)
    te_dl = DataLoader(PatchDS(te, make_tf(gray, False)), batch_size=C.BATCH_SIZE,
                       shuffle=False, num_workers=C.NUM_WORKERS)
    m = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    for p in m.parameters():
        p.requires_grad = False
    m.fc = nn.Linear(m.fc.in_features, 2)
    m = m.to(device)

    counts = np.array([(tr.label == "clay").sum(), (tr.label == "sand").sum()], float)
    w = torch.tensor(counts.sum() / np.maximum(counts, 1), dtype=torch.float32)
    crit = nn.CrossEntropyLoss(weight=(w / w.mean()).to(device))

    opt = torch.optim.AdamW([p for p in m.parameters() if p.requires_grad], lr=C.LR_HEAD)
    for _ in range(C.EPOCHS_HEAD):
        m.train()
        for x, y, _ in tr_dl:
            x, y = x.to(device), y.to(device)
            opt.zero_grad(); crit(m(x), y).backward(); opt.step()
    for p in m.layer4.parameters():
        p.requires_grad = True
    opt = torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],
                            lr=C.LR_FINETUNE)
    for _ in range(C.EPOCHS_FINETUNE):
        m.train()
        for x, y, _ in tr_dl:
            x, y = x.to(device), y.to(device)
            opt.zero_grad(); crit(m(x), y).backward(); opt.step()

    m.eval()
    te = te.reset_index(drop=True).copy()
    probs = np.zeros(len(te))
    with torch.no_grad():
        for x, _, i in te_dl:
            pr = torch.softmax(m(x.to(device)), 1)[:, 1].cpu().numpy()
            probs[i.numpy()] = pr
    te["p_sand"] = probs
    return te


# =============================================================================
# engineered
# =============================================================================
def fit_engineered(tr_d, te_d, feats):
    clf = make_pipeline(StandardScaler(),
                        LogisticRegression(penalty="l2", C=1.0, max_iter=2000,
                                           class_weight="balanced"))
    X = tr_d[feats].values
    y = (tr_d.label == "sand").astype(int).values
    if len(set(y)) < 2:
        te = te_d.copy(); te["p_sand"] = np.nan; return te, None
    clf.fit(X, y)
    te = te_d.copy()
    te["p_sand"] = clf.predict_proba(te[feats].values)[:, 1]
    te["pred_label"] = np.where(te.p_sand > 0.5, "sand", "clay")
    coefs = dict(zip(feats, clf[-1].coef_[0]))
    return te, coefs


# =============================================================================
def main():
    device = get_device()
    print(f"device: {device}", flush=True)

    f = pd.read_csv(C.WORK_DIR / "07_features.csv")
    f = f[(~f.probe_only) & f.label.isin(C.CLASSES)].copy()
    f = f.dropna(subset=FEATURE_NAMES)

    # ---- A2 / A3 tags ----
    bodies = json.load(open(__import__("pathlib").Path(__file__).with_name("sand_bodies.json")))
    def in_body(row):
        return any(a <= row.depth_m <= b for a, b in bodies.get(row.well, []))
    f["in_body"] = f.apply(in_body, axis=1)
    f["depth_class"] = np.where(f.depth_m < SHALLOW_MAX_M, "shallow", "deep")
    print(f"{len(f):,} labelled patches | "
          f"{f.groupby('label').depth_m.nunique().to_dict()} depths", flush=True)

    # depth-level feature table (MEDIAN over the 16 patches)
    agg = {c: "median" for c in FEATURE_NAMES}
    agg.update({"in_body": "first", "depth_class": "first",
                "ba_ppm": "first", "formation": "first"})
    depths = f.groupby(["well", "depth_m", "label"], as_index=False).agg(agg)
    print(f"depth-level table: {len(depths)} rows", flush=True)

    # ---- folds (identical for every model) ----
    wells = sorted(f.well.unique())
    tier2 = [("tier2_holdout_" + w, w) for w in wells]

    d24 = f[f.well == "24_9-3"]
    ds = np.sort(d24[d24.label == "sand"].depth_m.unique())
    grp, cur = [], [ds[0]]
    for z in ds[1:]:
        if z - cur[-1] <= 12:
            cur.append(z)
        else:
            grp.append(cur); cur = [z]
    grp.append(cur)
    tier1_bodies = [b for b in grp if len(b) >= 3]
    clay24 = np.sort(d24[d24.label == "clay"].depth_m.unique())
    print(f"\ntier-1 bodies (>=3 sand depths, gap<=12 m): {len(tier1_bodies)}", flush=True)
    body_info = []
    for i, b in enumerate(tier1_bodies):
        lo, hi = min(b), max(b)
        n100 = int(((clay24 >= lo - 100) & (clay24 <= hi + 100)).sum())
        body_info.append({"i": i, "lo": lo, "hi": hi, "n_sand": len(b),
                          "clay_within_100m": n100})
        print(f"  body{i} {lo:.0f}-{hi:.0f} m  n_sand={len(b)}  "
              f"clay within +/-100 m: {n100}", flush=True)

    results = {"tier2": {}, "tier1": {}, "coefs": {}, "ablation": {},
               "body_info": body_info}
    preds = {}

    MODELS = ["cnn_colour", "cnn_gray", "eng_full", "eng_nocolour"]
    ABL = {"minus_free_grain": "free_grain", "minus_quartz": "quartz",
           "minus_texture": "texture", "minus_colour": "colour"}

    # ---------------- TIER 2 ----------------
    for name, w in tier2:
        tr_p, te_p = f[f.well != w], f[f.well == w]
        tr_d, te_d = depths[depths.well != w], depths[depths.well == w]
        for mdl in MODELS:
            t0 = time.time()
            if mdl.startswith("cnn"):
                te = train_cnn(tr_p, te_p, gray=(mdl == "cnn_gray"), device=device)
                dd = depth_table(te)
            else:
                feats = FEATURE_NAMES if mdl == "eng_full" else COLOUR_FREE_NAMES
                dd, coefs = fit_engineered(tr_d, te_d, feats)
                if coefs and mdl == "eng_full":
                    results["coefs"].setdefault(name, coefs)
            m = metrics_from_depths(dd)
            results["tier2"].setdefault(mdl, {})[name] = m
            preds[(mdl, name)] = dd
            bal = m["balanced_acc"] if m else float("nan")
            print(f"  [{name}] {mdl:13} balanced {bal:.3f} "
                  f"(base {m['majority_baseline']:.3f}) "
                  f"sand recall {m['sand_recall']:.2f} "
                  f"prec {m['sand_precision']:.2f} | {time.time()-t0:.0f}s", flush=True)
        # ablations (engineered only, cheap)
        for tag, blk in ABL.items():
            feats = [x for x in FEATURE_NAMES if x not in FEATURE_BLOCKS[blk]]
            dd, _ = fit_engineered(tr_d, te_d, feats)
            results["ablation"].setdefault(tag, {})[name] = metrics_from_depths(dd)

    # ---------------- TIER 1 ----------------
    for bi, b in enumerate(tier1_bodies):
        lo, hi = min(b), max(b)
        name = f"tier1_body{bi}_{lo:.0f}-{hi:.0f}m"
        te_mask_p = (f.well == "24_9-3") & f.depth_m.between(lo, hi)
        tr_mask_p = (f.well == "24_9-3") & ~f.depth_m.between(lo - 10, hi + 10)
        te_mask_d = (depths.well == "24_9-3") & depths.depth_m.between(lo, hi)
        tr_mask_d = (depths.well == "24_9-3") & ~depths.depth_m.between(lo - 10, hi + 10)
        for mdl in MODELS:
            if mdl.startswith("cnn"):
                te = train_cnn(f[tr_mask_p], f[te_mask_p],
                               gray=(mdl == "cnn_gray"), device=device)
                dd = depth_table(te)
            else:
                feats = FEATURE_NAMES if mdl == "eng_full" else COLOUR_FREE_NAMES
                dd, _ = fit_engineered(depths[tr_mask_d], depths[te_mask_d], feats)
            m = metrics_from_depths(dd)
            results["tier1"].setdefault(mdl, {})[name] = m
            preds[(mdl, name)] = dd
            print(f"  [{name}] {mdl:13} sand recall "
                  f"{m['confusion']['tp_sand']}/{m['n_sand']} "
                  f"clay n={m['n_clay']}", flush=True)

    # ---------------- save ----------------
    allp = []
    for (mdl, fold), dd in preds.items():
        d2 = dd.copy(); d2["model"] = mdl; d2["fold"] = fold
        d2["tier"] = "tier2" if fold.startswith("tier2") else "tier1"
        allp.append(d2)
    pd.concat(allp, ignore_index=True).to_csv(OUT_DIR / "all_predictions.csv", index=False)
    with open(OUT_DIR / "results.json", "w") as fh:
        json.dump(results, fh, indent=2, default=float)
    print(f"\nwritten: {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
