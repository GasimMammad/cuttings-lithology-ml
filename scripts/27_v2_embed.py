"""
v2 -- frozen ImageNet ResNet-50 embeddings for every W_1 photograph.

No training here: the network is used as a fixed feature extractor (2048-d
global-average-pooled output of the last conv block). Each of the 16 tiles is
embedded and the 16 vectors are averaged to one vector per depth.
Two passes: RGB, and greyscale replicated to 3 channels.

Outputs (WORK_DIR/embeddings/):
  meta.csv              one row per depth (well, depth_m, label, vsh, ...)
  resnet50_rgb.npy      float32 [n_depths, 2048]
  resnet50_gray.npy     float32 [n_depths, 2048]

Run:  python 27_v2_embed.py
"""
import time

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

import config as C

OUT = C.WORK_DIR / "embeddings"
MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
TILES = [f"r{j}c{i}" for j in range(4) for i in range(4)]


class Tiles(Dataset):
    def __init__(self, paths, gray):
        self.paths = paths
        ops = [transforms.Grayscale(num_output_channels=3)] if gray else []
        self.tf = transforms.Compose(ops + [transforms.ToTensor(),
                                            transforms.Normalize(MEAN, STD)])

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, i):
        return self.tf(Image.open(self.paths[i]).convert("RGB")), i


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(C.LABELS_CSV)
    df = df[df.processing == "standard"].sort_values(["well", "depth_m"]).reset_index(drop=True)
    paths = [str(C.PATCH_DIR / r.well / f"{r.stem}__{t}.jpg")
             for r in df.itertuples() for t in TILES]
    missing = [p for p in paths if not __import__("os").path.exists(p)]
    if missing:
        raise SystemExit(f"{len(missing)} tiles missing, e.g. {missing[0]} -- run 26 first")
    keep = ["well", "depth_m", "label", "vsh", "gr", "zone_name", "stem"]
    df[keep].to_csv(OUT / "meta.csv", index=False)

    dev = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    net = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
    net.fc = torch.nn.Identity()
    net = net.eval().to(dev)

    for gray in (False, True):
        tag = "gray" if gray else "rgb"
        dl = DataLoader(Tiles(paths, gray), batch_size=128, num_workers=4)
        emb = np.zeros((len(paths), 2048), np.float32)
        t0 = time.time()
        with torch.no_grad():
            for b, (x, i) in enumerate(dl):
                emb[i.numpy()] = net(x.to(dev)).cpu().numpy()
                if b % 50 == 0:
                    print(f"{tag}: {b * 128:,}/{len(paths):,}  {time.time()-t0:.0f}s", flush=True)
        depth_emb = emb.reshape(len(df), len(TILES), 2048).mean(axis=1)
        np.save(OUT / f"resnet50_{tag}.npy", depth_emb)
        print(f"{tag}: done in {time.time()-t0:.0f}s -> {OUT / f'resnet50_{tag}.npy'}", flush=True)


if __name__ == "__main__":
    main()
