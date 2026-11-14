"""
v2 EXPLORATORY (not in V2_PLAN.md's tested set) -- fine-tuned CNN on v2 labels.

  C1  v1 recipe unchanged (ResNet-18, ImageNet weights, head 4 epochs + layer4
      6 epochs, class-weighted loss, flips/rotation/colour jitter)
  C2  C1 + label-free per-well colour normalisation: every tile is
      standardised with its own well's per-channel mean/SD (estimated from two
      tiles of every W_1 photo of that well, no labels) instead of ImageNet's
      mean/SD; colour jitter is dropped since the normalisation replaces it.

Leave-one-well-out over the 10 labelled wells. Prediction for every W_1 depth
of the held-out well (median p(sand) over its 16 tiles).

Output: WORK_DIR/v2_results/cnn_predictions.csv

Run:  python 31_v2_cnn.py
"""
import time

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

import config as C

OUT = C.WORK_DIR / "v2_results"
MEAN = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
STD = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
TILES = [f"r{j}c{i}" for j in range(4) for i in range(4)]


def well_stats(df):
    """Per-well channel mean/SD from a 2-tile-per-photo sample (label-free)."""
    st = {}
    for w, g in df.groupby("well"):
        px = []
        for r in g.itertuples():
            for t in ("r1c1", "r2c2"):
                a = np.asarray(Image.open(C.PATCH_DIR / w / f"{r.stem}__{t}.jpg").convert("RGB"),
                               np.float32)[::4, ::4] / 255.0
                px.append(a.reshape(-1, 3))
        px = np.concatenate(px)
        st[w] = (torch.tensor(px.mean(0)).view(3, 1, 1), torch.tensor(px.std(0)).view(3, 1, 1))
    return st


class DS(Dataset):
    def __init__(self, rows, train, stats=None):
        self.r = rows.reset_index(drop=True)
        self.stats = stats
        aug = [transforms.RandomHorizontalFlip(), transforms.RandomVerticalFlip(),
               transforms.RandomRotation(15)] if train else []
        if train and stats is None:
            aug.append(transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.10))
        self.tf = transforms.Compose(aug + [transforms.ToTensor()])

    def __len__(self):
        return len(self.r)

    def __getitem__(self, i):
        r = self.r.iloc[i]
        x = self.tf(Image.open(r.patch_path).convert("RGB"))
        if self.stats is not None:
            mu, sd = self.stats[r.well]
            x = (x - mu) / sd               # per-well standardised...
        else:
            x = (x - MEAN) / STD            # ...or plain ImageNet normalisation
        return x, int(r.label == "sand"), i


def fit_predict(tr, te, stats, dev):
    dl = DataLoader(DS(tr, True, stats), batch_size=C.BATCH_SIZE, shuffle=True,
                    num_workers=4, persistent_workers=True)
    m = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    for p in m.parameters():
        p.requires_grad = False
    m.fc = nn.Linear(m.fc.in_features, 2)
    m = m.to(dev)
    cnt = np.array([(tr.label == "clay").sum(), (tr.label == "sand").sum()], float)
    w = torch.tensor(cnt.sum() / np.maximum(cnt, 1), dtype=torch.float32)
    crit = nn.CrossEntropyLoss(weight=(w / w.mean()).to(dev))
    for stage, epochs, lr in (("head", C.EPOCHS_HEAD, C.LR_HEAD),
                              ("ft", C.EPOCHS_FINETUNE, C.LR_FINETUNE)):
        if stage == "ft":
            for p in m.layer4.parameters():
                p.requires_grad = True
        opt = torch.optim.AdamW([p for p in m.parameters() if p.requires_grad], lr=lr)
        for _ in range(epochs):
            m.train()
            for x, y, _ in dl:
                x, y = x.to(dev), y.to(dev)
                opt.zero_grad(); crit(m(x), y).backward(); opt.step()
    m.eval()
    te = te.reset_index(drop=True)
    pr = np.zeros(len(te))
    with torch.no_grad():
        for x, _, i in DataLoader(DS(te, False, stats), batch_size=128, num_workers=4):
            pr[i.numpy()] = torch.softmax(m(x.to(dev)), 1)[:, 1].cpu().numpy()
    te = te.assign(p=pr)
    return te.groupby(["well", "depth_m"], as_index=False).p.median()


def main():
    torch.manual_seed(C.SEED); np.random.seed(C.SEED)
    dev = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    lab = pd.read_csv(C.LABELS_CSV)
    lab = lab[(lab.processing == "standard") & (lab.well != "34_7-1")]
    tiles = pd.DataFrame([{"patch_path": str(C.PATCH_DIR / r.well / f"{r.stem}__{t}.jpg"),
                           "well": r.well, "depth_m": r.depth_m, "label": r.label}
                          for r in lab.itertuples() for t in TILES])
    t0 = time.time()
    stats = well_stats(lab)
    print(f"per-well colour stats in {time.time()-t0:.0f}s", flush=True)
    wells = sorted(lab[lab.label.isin(["sand", "clay"])].well.unique())
    out = []
    for tag, st in (("C1", None), ("C2", stats)):
        for w in wells:
            t0 = time.time()
            tr = tiles[(tiles.well != w) & tiles.label.isin(["sand", "clay"])]
            te = tiles[tiles.well == w]
            d = fit_predict(tr, te, st, dev)
            d["model"] = tag
            out.append(d)
            pd.concat(out).to_csv(OUT / "cnn_predictions.csv", index=False)
            print(f"  {tag} held-out {w}: {time.time()-t0:.0f}s", flush=True)
    print("written", OUT / "cnn_predictions.csv", flush=True)


if __name__ == "__main__":
    main()
