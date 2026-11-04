"""
STEP 6 -- Turn the classifier into a geological product: a sand-fraction log.

An accuracy number is not a result. A CURVE is a result. This script runs the
model over every patch in a well, averages the sand probability into depth
bins, and plots it next to gamma ray in standard well-log format.

The figure this produces is the one that goes in your thesis. It shows:
  - where the model agrees with GR (the logged interval, validation)
  - what the model says where GR does not exist (the unlogged shallow
    interval, which is the actual scientific contribution)

CRITICAL: use the checkpoint that HELD OUT this well. Predicting a well with
a model that was trained on it tells you nothing.

Run:  python 06_predict_log.py --well 34_4-6
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

import config as C
from importlib import import_module

_train = import_module("05_train") if Path("05_train.py").exists() else None

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

eval_tf = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
])


def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


class InferDataset(Dataset):
    def __init__(self, df):
        self.df = df.reset_index(drop=True)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, i):
        p = self.df.iloc[i].patch_path
        return eval_tf(Image.open(p).convert("RGB")), i


def load_model(ckpt_path, device):
    ck = torch.load(ckpt_path, map_location=device, weights_only=False)
    classes = ck["classes"]
    m = models.resnet18(weights=None)
    m.fc = nn.Linear(m.fc.in_features, len(classes))
    m.load_state_dict(ck["state_dict"])
    return m.to(device).eval(), classes


def main(well):
    if not C.PATCHES_CSV.exists():
        raise SystemExit("Run 04_prepare_patches.py --all first.")

    df = pd.read_csv(C.PATCHES_CSV)
    sub = df[df.well == well].copy()
    if sub.empty:
        raise SystemExit(f"No patches for well {well}. Available: {sorted(df.well.unique())}")

    ckpt = C.MODEL_DIR / f"resnet18_holdout_{well.replace('/', '_')}.pt"
    if not ckpt.exists():
        raise SystemExit(
            f"No held-out checkpoint for {well}.\n"
            f"Run:  python 05_train.py --fold {well}\n"
            "Do NOT substitute another checkpoint. Predicting a well with a model\n"
            "trained on that well is circular and the result is meaningless."
        )

    device = get_device()
    model, classes = load_model(ckpt, device)
    sand_idx = classes.index("sand")
    print(f"Well {well}: {len(sub):,} patches, model {ckpt.name}, device {device}")

    dl = DataLoader(InferDataset(sub), batch_size=C.BATCH_SIZE, shuffle=False,
                    num_workers=C.NUM_WORKERS)
    probs = np.zeros(len(sub))
    with torch.no_grad():
        for x, idx in dl:
            out = torch.softmax(model(x.to(device)), dim=1)[:, sand_idx]
            probs[idx.numpy()] = out.cpu().numpy()

    sub["p_sand"] = probs

    # ---- aggregate: patches -> photograph -> depth bin ----
    per_photo = (sub.groupby(["source_stem", "depth_m"], as_index=False)
                 .agg(p_sand=("p_sand", "mean"),
                      n_patches=("p_sand", "size"),
                      gr=("gr", "first"),
                      label=("label", "first")))

    b = C.OUTPUT_BIN_M
    per_photo["bin"] = (per_photo.depth_m // b) * b + b / 2
    binned = (per_photo.groupby("bin", as_index=False)
              .agg(sand_fraction=("p_sand", "mean"),
                   sand_std=("p_sand", "std"),
                   n_photos=("p_sand", "size"),
                   gr=("gr", "mean")))
    binned = binned.sort_values("bin")

    out_csv = C.PRED_DIR / f"sandfraction_{well}.csv"
    binned.to_csv(out_csv, index=False)
    print(f"Written: {out_csv}")

    # ---- validation where GR exists ----
    val = per_photo[np.isfinite(per_photo.gr)]
    if len(val) > 10:
        r = np.corrcoef(val.p_sand, val.gr)[0, 1]
        print(f"\nVALIDATION over the logged interval ({len(val)} photos)")
        print(f"  correlation between predicted sand probability and GR: {r:+.3f}")
        print("  A strong NEGATIVE correlation is what you want: high predicted")
        print("  sand should coincide with low gamma ray.")

    unlogged = per_photo[~np.isfinite(per_photo.gr)]
    print(f"\nPREDICTIONS IN THE UNLOGGED INTERVAL: {len(unlogged)} photos")
    if len(unlogged):
        print(f"  depth range {unlogged.depth_m.min():.0f} to {unlogged.depth_m.max():.0f} m")
        print("  This is your contribution: lithology where no wireline exists.")

    # ---- the thesis figure ----
    fig, axes = plt.subplots(1, 2, figsize=(9, 11), sharey=True)

    ax = axes[0]
    g = per_photo[np.isfinite(per_photo.gr)].sort_values("depth_m")
    if len(g):
        ax.plot(g.gr, g.depth_m, color="#333333", lw=0.8)
    ax.axvline(C.GR_SAND_MAX, color="#DD8452", ls="--", lw=1)
    ax.axvline(C.GR_CLAY_MIN, color="#C44E52", ls="--", lw=1)
    ax.set_xlabel("Gamma ray (API)")
    ax.set_ylabel("Depth (m MD)")
    ax.set_title("Wireline GR", fontweight="bold")
    ax.grid(alpha=0.3)

    ax = axes[1]
    ax.plot(binned.sand_fraction, binned.bin, color="#4C72B0", lw=1.4)
    ax.fill_betweenx(binned.bin, 0, binned.sand_fraction, color="#4C72B0", alpha=0.35)
    if binned.sand_std.notna().any():
        ax.fill_betweenx(binned.bin,
                         (binned.sand_fraction - binned.sand_std).clip(0, 1),
                         (binned.sand_fraction + binned.sand_std).clip(0, 1),
                         color="#4C72B0", alpha=0.12)
    ax.axvline(0.5, color="grey", ls=":", lw=1)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Predicted sand fraction from cuttings")
    ax.set_title("Cuttings classifier", fontweight="bold")
    ax.grid(alpha=0.3)

    # shade the interval with no wireline coverage
    if len(g):
        logged_top, logged_base = g.depth_m.min(), g.depth_m.max()
        for a in axes:
            lo, hi = per_photo.depth_m.min(), per_photo.depth_m.max()
            if logged_top > lo:
                a.axhspan(lo, logged_top, color="#FFD9A0", alpha=0.35, zorder=0)
            if logged_base < hi:
                a.axhspan(logged_base, hi, color="#FFD9A0", alpha=0.35, zorder=0)
        axes[1].text(0.02, 0.99, "shaded = no wireline coverage",
                     transform=axes[1].transAxes, va="top", fontsize=9)

    axes[0].invert_yaxis()
    fig.suptitle(f"Well {well}: cuttings-derived lithology vs wireline",
                 fontweight="bold", y=0.995)
    fig.tight_layout()
    out_png = C.FIG_DIR / f"06_sandfraction_{well}.png"
    fig.savefig(out_png, dpi=200, bbox_inches="tight")
    print(f"\nFigure written: {out_png}")
    print("""
NEXT: add your Petrel horizon depths to this figure as horizontal lines
(THGU, top and base of the Oligocene sand, diagenetic boundary). That single
panel is where the seismic half and the ML half of your thesis meet.
""")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--well", required=True, help="e.g. 34_4-6")
    main(ap.parse_args().well)
