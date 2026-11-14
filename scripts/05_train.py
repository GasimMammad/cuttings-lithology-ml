"""
STEP 5 -- Train the classifier. Reworked 2026-07-31 to the
training requirements for the first run.

TWO-TIER VALIDATION, never merged:
  Tier 2 (cross-well): leave-one-well-out. Tests WELL generalisation.
    Sand n is tiny outside 24_9-3, so depth-level sand recall carries a
    Wilson binomial confidence interval.
  Tier 1 (within 24_9-3): leave-one-sand-body-out. Tests DEPTH/FORMATION
    generalisation with usable n. Explicitly NOT a well-generalisation
    claim.

METRICS: sand recall, sand precision, balanced accuracy, full confusion
matrix. The majority-class (always-clay) baseline is printed beside every
accuracy so it can never be read as success.

LEAKAGE CHECKS (from held-out tier-2 predictions only):
  - predicted sand probability vs per-sample barite (Ba, XRF)
  - predicted sand probability vs depth
FAILURE CASES: montages of the 20 most confidently wrong and 20 most
confidently right held-out patches, annotated with well/depth/formation/Ba.

PROBE SET: mud-log-labelled 34_7-1 patches are excluded from ALL training
and headline metrics; they are predicted with the hold-out-34_7-1
checkpoint only (rule 3) and reported separately.

Run:  python 05_train.py               (tier 2 then tier 1, full protocol)
      python 05_train.py --tier 2      (cross-well only)
      python 05_train.py --tier 1      (sand-body folds only)
"""

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from PIL import Image, ImageDraw
from sklearn.metrics import balanced_accuracy_score, confusion_matrix
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

import config as C

PRED_CV_DIR = C.WORK_DIR / "predictions_cv"
PRED_CV_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

train_tf = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.RandomRotation(15),
    # mild only: strong colour jitter would destroy the lithological signal
    transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.10),
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
])
eval_tf = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
])


class PatchDataset(Dataset):
    def __init__(self, df, classes, transform):
        self.df = df.reset_index(drop=True)
        self.cls2idx = {c: i for i, c in enumerate(classes)}
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, i):
        r = self.df.iloc[i]
        img = Image.open(r.patch_path).convert("RGB")
        return self.transform(img), self.cls2idx[r.label], i


def build_model(n_classes, device):
    m = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    for p in m.parameters():
        p.requires_grad = False
    m.fc = nn.Linear(m.fc.in_features, n_classes)
    return m.to(device)


def unfreeze_last_block(model):
    for p in model.layer4.parameters():
        p.requires_grad = True


def wilson(k, n, z=1.96):
    """Wilson score interval for a binomial proportion."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def run_epoch(model, loader, criterion, optimizer, device, train):
    model.train() if train else model.eval()
    total_loss, correct, n = 0.0, 0, 0
    preds, probs, idxs = [], [], []
    with torch.set_grad_enabled(train):
        for x, y, i in loader:
            x, y = x.to(device), y.to(device)
            out = model(x)
            loss = criterion(out, y)
            if train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            total_loss += loss.item() * y.size(0)
            correct += (out.argmax(1) == y).sum().item()
            n += y.size(0)
            if not train:
                probs.append(torch.softmax(out, 1).detach().cpu().numpy())
                preds.append(out.argmax(1).cpu().numpy())
                idxs.append(i.numpy())
    res = {"loss": total_loss / max(n, 1), "acc": correct / max(n, 1)}
    if not train and idxs:
        res["prob"] = np.concatenate(probs)
        res["pred"] = np.concatenate(preds)
        res["idx"] = np.concatenate(idxs)
    return res


def fold_metrics(test_df, classes):
    """Patch- and depth-level metrics with baselines and CIs."""
    sand_i = classes.index("sand")
    y = (test_df.label == "sand").astype(int).values
    p = (test_df.pred_label == "sand").astype(int).values

    cm = confusion_matrix(y, p, labels=[0, 1])   # rows truth (clay,sand)
    tp = int(cm[1, 1]); fn = int(cm[1, 0]); fp = int(cm[0, 1]); tn = int(cm[0, 0])
    out = {
        "n_patches": len(test_df),
        "majority_baseline": float(max((y == 0).mean(), (y == 1).mean())),
        "acc": float((y == p).mean()),
        "balanced_acc": float(balanced_accuracy_score(y, p)) if len(set(y)) > 1 else float("nan"),
        "sand_recall": tp / (tp + fn) if (tp + fn) else float("nan"),
        "sand_precision": tp / (tp + fp) if (tp + fp) else float("nan"),
        "confusion": {"tn_clay": tn, "fp": fp, "fn": fn, "tp_sand": tp},
    }
    # depth level: a depth is called sand if >half its patches are called sand
    d = (test_df.groupby(["depth_m", "label"], as_index=False)
         .agg(p_sand=("p_sand", "mean"), votes=("pred_label", lambda s: (s == "sand").mean())))
    d["pred"] = np.where(d.votes > 0.5, "sand", "clay")
    ds = d[d.label == "sand"]; dc = d[d.label == "clay"]
    k = int((ds.pred == "sand").sum()); n = len(ds)
    kp = int((d.pred == "sand").sum())
    tp_d = k; fp_d = int((dc.pred == "sand").sum())
    out["depth_level"] = {
        "n_sand_depths": n, "sand_depths_recalled": k,
        "sand_recall": k / n if n else float("nan"),
        "sand_recall_ci95": wilson(k, n),
        "sand_precision": tp_d / (tp_d + fp_d) if (tp_d + fp_d) else float("nan"),
        "sand_precision_ci95": wilson(tp_d, tp_d + fp_d) if (tp_d + fp_d) else (float("nan"),) * 2,
        "n_clay_depths": len(dc),
        "clay_recall": float((dc.pred == "clay").mean()) if len(dc) else float("nan"),
    }
    return out


def train_one_fold(tr, te, fold_name, device, save_ckpt=None):
    classes = list(C.CLASSES)
    print(f"\n{'=' * 72}\nFOLD {fold_name}\n{'=' * 72}")
    print(f"  train {len(tr):,} patches ({dict(tr.label.value_counts())}) | "
          f"test {len(te):,} ({dict(te.label.value_counts())})")

    tr_dl = DataLoader(PatchDataset(tr, classes, train_tf), batch_size=C.BATCH_SIZE,
                       shuffle=True, num_workers=C.NUM_WORKERS,
                       persistent_workers=C.NUM_WORKERS > 0)
    te_dl = DataLoader(PatchDataset(te, classes, eval_tf), batch_size=C.BATCH_SIZE,
                       shuffle=False, num_workers=C.NUM_WORKERS,
                       persistent_workers=C.NUM_WORKERS > 0)

    counts = tr.label.value_counts().reindex(classes).fillna(0).values.astype(float)
    weights = torch.tensor(counts.sum() / np.maximum(counts, 1), dtype=torch.float32)
    weights = (weights / weights.mean()).to(device)
    criterion = nn.CrossEntropyLoss(weight=weights)

    model = build_model(len(classes), device)
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=C.LR_HEAD)
    for ep in range(C.EPOCHS_HEAD):
        t0 = time.time()
        trm = run_epoch(model, tr_dl, criterion, opt, device, True)
        print(f"  [head {ep + 1}/{C.EPOCHS_HEAD}] train acc {trm['acc']:.3f} "
              f"| {time.time() - t0:.0f}s")
    unfreeze_last_block(model)
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=C.LR_FINETUNE)
    for ep in range(C.EPOCHS_FINETUNE):
        t0 = time.time()
        trm = run_epoch(model, tr_dl, criterion, opt, device, True)
        print(f"  [fine {ep + 1}/{C.EPOCHS_FINETUNE}] train acc {trm['acc']:.3f} "
              f"| {time.time() - t0:.0f}s")

    tem = run_epoch(model, te_dl, criterion, None, device, False)
    te = te.reset_index(drop=True).copy()
    sand_i = classes.index("sand")
    te.loc[tem["idx"], "p_sand"] = tem["prob"][:, sand_i]
    te.loc[tem["idx"], "pred_label"] = [classes[k] for k in tem["pred"]]

    m = fold_metrics(te, classes)
    d = m["depth_level"]
    print(f"\n  RESULT {fold_name}  (majority-clay baseline = {m['majority_baseline']:.1%})")
    print(f"    patch: acc {m['acc']:.3f} | balanced {m['balanced_acc']:.3f} | "
          f"sand recall {m['sand_recall']:.3f} | sand precision {m['sand_precision']:.3f}")
    cm = m["confusion"]
    print(f"    confusion (patches): clay->clay {cm['tn_clay']}, clay->sand {cm['fp']}, "
          f"sand->clay {cm['fn']}, sand->sand {cm['tp_sand']}")
    lo, hi = d["sand_recall_ci95"]
    print(f"    depth: sand recall {d['sand_depths_recalled']}/{d['n_sand_depths']}"
          f" = {d['sand_recall']:.2f} (95% CI {lo:.2f}-{hi:.2f}) | "
          f"clay recall {d['clay_recall']:.2f} (n={d['n_clay_depths']})")

    if save_ckpt:
        torch.save({"state_dict": model.state_dict(), "classes": classes}, save_ckpt)
        print(f"    checkpoint: {save_ckpt}")
    te.to_csv(PRED_CV_DIR / f"pred_{fold_name}.csv", index=False)
    return m, te, model


# =============================================================================
def sand_bodies(df24):
    """Cluster 24_9-3 sand-labelled depths into bodies (gap <= 12 m)."""
    ds = np.sort(df24[df24.label == "sand"].depth_m.unique())
    bodies, cur = [], [ds[0]]
    for z in ds[1:]:
        if z - cur[-1] <= 12:
            cur.append(z)
        else:
            bodies.append(cur); cur = [z]
    bodies.append(cur)
    return [b for b in bodies if len(b) >= 3]


def leakage_and_montages(all_te, device):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    per_photo = (all_te.groupby(["well", "depth_m", "label"], as_index=False)
                 .agg(p_sand=("p_sand", "mean"), ba=("ba_ppm", "first")))

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    cols = {"24_9-3": "#4C72B0", "24_9-4": "#DD8452",
            "34_4-6": "#55A868", "34_7-1": "#8172B3"}
    print("\nLEAKAGE CHECKS (held-out tier-2 predictions, photo level)")
    print(f"  {'well':9} {'spearman(p_sand, Ba)':>22} {'spearman(p_sand, depth)':>24}")
    stats = {}
    for w, g in per_photo.groupby("well"):
        r_ba = g.p_sand.corr(g.ba, method="spearman")
        r_z = g.p_sand.corr(g.depth_m, method="spearman")
        # within-label version: is the correlation there even at fixed lithology?
        gc = g[g.label == "clay"]
        r_ba_clay = gc.p_sand.corr(gc.ba, method="spearman") if len(gc) > 10 else float("nan")
        stats[w] = {"ba": None if pd.isna(r_ba) else float(r_ba),
                    "depth": None if pd.isna(r_z) else float(r_z),
                    "ba_within_clay": None if pd.isna(r_ba_clay) else float(r_ba_clay)}
        print(f"  {w:9} {r_ba:22.2f} {r_z:24.2f}   (within clay only: Ba {r_ba_clay:+.2f})")
        for ax, xcol in zip(axes, ["ba", "depth_m"]):
            for lab, mk in (("clay", "o"), ("sand", "^")):
                gg = g[g.label == lab]
                ax.scatter(gg[xcol], gg.p_sand, s=14, alpha=.5, marker=mk,
                           color=cols.get(w, "k"),
                           label=f"{w} {lab}" if lab == "sand" else None)
    axes[0].set_xscale("log"); axes[0].set_xlabel("Ba (ppm, XRF)")
    axes[1].set_xlabel("depth (m)")
    for ax in axes:
        ax.set_ylabel("held-out predicted P(sand), photo mean")
        ax.grid(alpha=.3); ax.set_ylim(-0.02, 1.02)
    axes[0].legend(fontsize=7)
    axes[0].set_title("barite leakage check", fontweight="bold")
    axes[1].set_title("depth leakage check", fontweight="bold")
    fig.tight_layout()
    out = C.FIG_DIR / "05_leakage_checks.png"
    fig.savefig(out, dpi=140); plt.close(fig)
    print(f"  figure: {out}")

    # ---- montages: most confidently wrong / right ----
    at = all_te.dropna(subset=["p_sand"]).copy()
    at["p_true"] = np.where(at.label == "sand", at.p_sand, 1 - at.p_sand)
    def montage(rows, fname, title):
        cell, pad, cap = 224, 10, 46
        n = len(rows); ncol = 5; nrow = int(np.ceil(n / ncol))
        M = Image.new("RGB", (ncol * (cell + pad) + pad,
                              nrow * (cell + cap + pad) + pad + 26), (25, 25, 25))
        dr = ImageDraw.Draw(M)
        for k, (_, r) in enumerate(rows.iterrows()):
            i, j = k % ncol, k // ncol
            x, y = pad + i * (cell + pad), pad + j * (cell + cap + pad)
            try:
                M.paste(Image.open(r.patch_path), (x, y))
            except Exception:
                continue
            dr.text((x + 2, y + cell + 2),
                    f"{r.well} {r.depth_m:.0f}m {str(r.formation)[:14]}",
                    fill=(255, 255, 255))
            dr.text((x + 2, y + cell + 16),
                    f"true {r.label} p_sand {r.p_sand:.2f}",
                    fill=(255, 120, 120) if r.p_true < .5 else (140, 255, 140))
            dr.text((x + 2, y + cell + 30), f"Ba {r.ba_ppm:.0f} ppm",
                    fill=(180, 180, 255))
        dr.text((pad, nrow * (cell + cap + pad) + pad), title, fill=(255, 255, 255))
        M.save(C.FIG_DIR / fname, quality=92)
        print(f"  montage: {C.FIG_DIR / fname}")
    montage(at.nsmallest(20, "p_true"), "05_most_confidently_wrong.jpg",
            "20 most confidently WRONG held-out patches (tier 2)")
    montage(at.nlargest(20, "p_true"), "05_most_confidently_right.jpg",
            "20 most confidently RIGHT held-out patches (tier 2)")
    return stats


def probe_eval(df, device):
    """Predict the mud-log probe patches with the hold-out-34_7-1 checkpoint."""
    ck = C.MODEL_DIR / "resnet18_holdout_34_7-1.pt"
    probe = df[df.probe_only].copy()
    if probe.empty or not ck.exists():
        print("\nPROBE: skipped (no probe patches or no 34_7-1 checkpoint)")
        return None
    mlp = pd.read_csv(C.WORK_DIR / "03_mudlog_probe.csv")
    lut = dict(zip(np.round(mlp.depth_m, 2), mlp.mudlog_label))
    probe["mudlog_label"] = [lut.get(round(z, 2), "?") for z in probe.depth_m]

    ckd = torch.load(ck, map_location=device, weights_only=False)
    classes = ckd["classes"]
    m = models.resnet18(weights=None)
    m.fc = nn.Linear(m.fc.in_features, len(classes))
    m.load_state_dict(ckd["state_dict"]); m = m.to(device).eval()
    sand_i = classes.index("sand")

    tmp = probe.copy(); tmp["label"] = "clay"      # dummy for the Dataset
    dl = DataLoader(PatchDataset(tmp, classes, eval_tf),
                    batch_size=C.BATCH_SIZE, shuffle=False, num_workers=C.NUM_WORKERS)
    ps = np.zeros(len(probe))
    with torch.no_grad():
        for x, _, i in dl:
            ps[i.numpy()] = torch.softmax(m(x.to(device)), 1)[:, sand_i].cpu().numpy()
    probe = probe.reset_index(drop=True); probe["p_sand"] = ps
    per = (probe.groupby(["depth_m", "mudlog_label"], as_index=False)
           .agg(p_sand=("p_sand", "mean")))
    print("\nMUD-LOG PROBE (34_7-1, Lunde; model = hold-out-34_7-1 checkpoint)")
    print("  NOT part of any headline metric. n=11 depths, arkosic sands.")
    print(per.sort_values("depth_m").to_string(index=False))
    for lab, g in per.groupby("mudlog_label"):
        print(f"  {lab:5}: mean p_sand {g.p_sand.mean():.2f}  "
              f"called sand {(g.p_sand > .5).sum()}/{len(g)}")
    probe.to_csv(PRED_CV_DIR / "pred_probe_mudlog.csv", index=False)
    return per


# =============================================================================
def main(tier):
    torch.manual_seed(C.SEED)
    np.random.seed(C.SEED)
    if not C.PATCHES_CSV.exists():
        raise SystemExit("Run 04_prepare_patches.py first.")

    df = pd.read_csv(C.PATCHES_CSV)
    train_pool = df[(~df.probe_only) & df.label.isin(C.CLASSES)].copy()
    device = get_device()
    print(f"Device: {device}")
    print(f"Trainable patches: {len(train_pool):,} "
          f"({dict(train_pool.label.value_counts())})")
    n_clay = (train_pool.label == "clay").sum()
    print(f"MAJORITY BASELINE (always clay): {n_clay / len(train_pool):.1%} "
          f"patch accuracy -- every number below must beat context, not this bar\n")

    results = {"tier2": [], "tier1": []}

    if tier in ("2", "all"):
        print("#" * 72)
        print("# TIER 2 -- LEAVE-ONE-WELL-OUT (well generalisation)")
        print("#" * 72)
        all_te = []
        for w in sorted(train_pool.well.unique()):
            tr = train_pool[train_pool.well != w]
            te = train_pool[train_pool.well == w]
            if len(te) < 20:
                continue
            ck = C.MODEL_DIR / f"resnet18_holdout_{w}.pt"
            m, te_pred, _ = train_one_fold(tr, te, f"tier2_holdout_{w}", device, ck)
            m["fold"] = w
            results["tier2"].append(m)
            all_te.append(te_pred)
        all_te = pd.concat(all_te, ignore_index=True)
        results["leakage"] = leakage_and_montages(all_te, device)
        results["probe"] = None
        pe = probe_eval(df, device)
        if pe is not None:
            results["probe"] = pe.to_dict(orient="records")

    if tier in ("1", "all"):
        print("\n" + "#" * 72)
        print("# TIER 1 -- LEAVE-ONE-SAND-BODY-OUT within 24_9-3 (depth generalisation)")
        print("#" * 72)
        d24 = train_pool[train_pool.well == "24_9-3"]
        for bi, body in enumerate(sand_bodies(d24)):
            lo, hi = min(body), max(body)
            te_mask = ((train_pool.well == "24_9-3")
                       & (train_pool.depth_m >= lo - 40)
                       & (train_pool.depth_m <= hi + 40))
            buf_mask = ((train_pool.well == "24_9-3")
                        & (train_pool.depth_m >= lo - 50)
                        & (train_pool.depth_m <= hi + 50))
            te = train_pool[te_mask]
            tr = train_pool[~buf_mask]
            if (te.label == "sand").sum() < 16:
                continue
            name = f"tier1_body{bi}_{lo:.0f}-{hi:.0f}m"
            fm = te[te.label == "sand"].formation.mode()
            print(f"\n  body {bi}: {lo:.0f}-{hi:.0f} m "
                  f"({len(body)} sand depths, {fm.iloc[0] if len(fm) else '?'}), "
                  f"10 m train-test gap")
            m, _, _ = train_one_fold(tr, te, name, device)
            m["fold"] = name
            results["tier1"].append(m)

    # ---- summary ----
    print("\n" + "=" * 72)
    print("SUMMARY -- the two tiers measure different things; NEVER merge them")
    print("=" * 72)
    for key, label in (("tier2", "TIER 2 cross-well (well generalisation)"),
                       ("tier1", "TIER 1 within 24_9-3 (depth generalisation)")):
        rs = results.get(key, [])
        if not rs:
            continue
        print(f"\n{label}")
        for m in rs:
            d = m["depth_level"]
            lo, hi = d["sand_recall_ci95"]
            print(f"  {m['fold']:26} balanced {m['balanced_acc']:.3f} "
                  f"(baseline {m['majority_baseline']:.1%}) | depth sand recall "
                  f"{d['sand_depths_recalled']}/{d['n_sand_depths']}"
                  f" ({lo:.2f}-{hi:.2f}) | sand precision {d['sand_precision']:.2f} "
                  f"| clay recall {d['clay_recall']:.2f}")
        bal = [m["balanced_acc"] for m in rs if np.isfinite(m["balanced_acc"])]
        if bal:
            print(f"  MEAN balanced accuracy {np.mean(bal):.3f}  STD {np.std(bal):.3f}"
                  f"  ({len(bal)} folds)")

    with open(C.WORK_DIR / "05_cv_results.json", "w") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"\nWritten: {C.WORK_DIR / '05_cv_results.json'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", default="all", choices=["1", "2", "all"])
    main(ap.parse_args().tier)
