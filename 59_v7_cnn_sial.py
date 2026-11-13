"""
v7 extra X1 (V7_PLAN.md "Extras", EXPLORATORY): fine-tuned ResNet-18 on the
step-1 Si/Al target T1, leave-one-well-out over the 11 wells, v2 "C2" recipe
unchanged except a regression head and MSE loss.

  python 59_v7_cnn_sial.py train      LOWO training; writes cnn_sial_predictions.csv (resumes per fold)
  python 59_v7_cnn_sial.py eval       step-1 statistic, paired vs R-D, and vs the mud-log label
"""
import sys
import time
from importlib import import_module

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from PIL import Image
from scipy.stats import wilcoxon
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

import config as C

V2 = import_module("31_v2_cnn")
EV = import_module("29_v2_evaluate")
M = import_module("52_v7_photo_to_xrf")
OUT = C.WORK_DIR / "v7" / "x1"
TILES = V2.TILES


class DS(Dataset):
    def __init__(self, rows, train, stats):
        self.r = rows.reset_index(drop=True)
        self.stats = stats
        aug = [transforms.RandomHorizontalFlip(), transforms.RandomVerticalFlip(),
               transforms.RandomRotation(15)] if train else []
        self.tf = transforms.Compose(aug + [transforms.ToTensor()])

    def __len__(self):
        return len(self.r)

    def __getitem__(self, i):
        r = self.r.iloc[i]
        x = self.tf(Image.open(r.patch_path).convert("RGB"))
        mu, sd = self.stats[r.well]
        return (x - mu) / sd, torch.tensor(r.y, dtype=torch.float32), i


def fit_predict(tr, te, stats, dev):
    dl = DataLoader(DS(tr, True, stats), batch_size=C.BATCH_SIZE, shuffle=True, num_workers=4,
                    persistent_workers=True)
    m = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    for p in m.parameters():
        p.requires_grad = False
    m.fc = nn.Linear(m.fc.in_features, 1)
    m = m.to(dev)
    crit = nn.MSELoss()
    for stage, epochs, lr in (("head", C.EPOCHS_HEAD, C.LR_HEAD), ("ft", C.EPOCHS_FINETUNE, C.LR_FINETUNE)):
        if stage == "ft":
            for p in m.layer4.parameters():
                p.requires_grad = True
        opt = torch.optim.AdamW([p for p in m.parameters() if p.requires_grad], lr=lr)
        for _ in range(epochs):
            m.train()
            for x, y, _ in dl:
                x, y = x.to(dev), y.to(dev)
                opt.zero_grad(); crit(m(x).squeeze(1), y).backward(); opt.step()
    m.eval()
    te = te.reset_index(drop=True)
    pr = np.zeros(len(te))
    with torch.no_grad():
        for x, _, i in DataLoader(DS(te, False, stats), batch_size=128, num_workers=4):
            pr[i.numpy()] = m(x.to(dev)).squeeze(1).cpu().numpy()
    return te.assign(p=pr).groupby(["well", "depth_m"], as_index=False).p.median()


def table():
    base, _ = EV.load_tables()
    s1 = pd.read_csv(C.WORK_DIR / "v7" / "step1_predictions.csv")
    assert (s1.well.values == base.well.values).all()
    b = base[["well", "depth_m", "stem"]].assign(in_S=s1.in_S.values.astype(bool), T1=s1.T1.values)
    return b[b.in_S & np.isfinite(b.T1)].reset_index(drop=True)


def train():
    off = int(sys.argv[2]) if len(sys.argv) > 2 else 0  # v8 part C: seed offset (1000, 2000); 0 = X1 as run
    torch.manual_seed(C.SEED + off); np.random.seed(C.SEED + off)
    dev = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    OUT.mkdir(parents=True, exist_ok=True)
    b = table()
    tiles = pd.DataFrame([{"patch_path": str(C.PATCH_DIR / r.well / f"{r.stem}__{t}.jpg"), "well": r.well,
                           "depth_m": r.depth_m, "y": r.T1} for r in b.itertuples() for t in TILES])
    ok = tiles.patch_path.map(lambda p: __import__("os").path.exists(p))
    print(f"bags {len(b)}, patches {len(tiles)}, missing {int((~ok).sum())}", flush=True)
    tiles = tiles[ok]
    stats = V2.well_stats(b)
    f = OUT / ("cnn_sial_predictions.csv" if off == 0 else f"cnn_sial_predictions_seed{off}.csv")
    out = [pd.read_csv(f)] if f.exists() else []
    done = set(out[0].well) if out else set()
    import hashlib
    (OUT / "config_sha256.txt").write_text(hashlib.sha256(open("config.py", "rb").read()).hexdigest() + "\n")
    for k, w in enumerate(sorted(b.well.unique())):
        if w in done:
            continue
        torch.manual_seed(C.SEED + off + k); np.random.seed(C.SEED + off + k)
        t0 = time.time()
        d = fit_predict(tiles[tiles.well != w], tiles[tiles.well == w], stats, dev)
        out.append(d)
        pd.concat(out).to_csv(f, index=False)
        print(f"held-out {w}: {len(d)} bags, {time.time() - t0:.0f}s", flush=True)
    print("done", flush=True)


def train_notwin():
    """v9 K2c: the 34/8-3 fold retrained without its sidetrack in training, and the reverse.
    Seeds 0, 1000, 2000 with the fold seed of the original runs, so only the training set changes."""
    PAIRS = [("34_8-3", "34_8-3_A"), ("34_8-3_A", "34_8-3")]  # (held-out, also removed from training)
    dev = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    b = table()
    tiles = pd.DataFrame([{"patch_path": str(C.PATCH_DIR / r.well / f"{r.stem}__{t}.jpg"), "well": r.well,
                           "depth_m": r.depth_m, "y": r.T1} for r in b.itertuples() for t in TILES])
    tiles = tiles[tiles.patch_path.map(lambda q: __import__("os").path.exists(q))]
    stats = V2.well_stats(b)
    order = sorted(b.well.unique())
    f = OUT / "cnn_sial_predictions_notwin.csv"
    out = [pd.read_csv(f)] if f.exists() else []
    done = set(zip(out[0].well, out[0].seed)) if out else set()
    print(f"bags {len(b)}, patches {len(tiles)}", flush=True)
    for w, drop in PAIRS:
        for off in (0, 1000, 2000):
            if (w, off) in done:
                continue
            k = order.index(w)
            torch.manual_seed(C.SEED + off + k); np.random.seed(C.SEED + off + k)
            t0 = time.time()
            d = fit_predict(tiles[~tiles.well.isin([w, drop])], tiles[tiles.well == w], stats, dev).assign(seed=off)
            out.append(d)
            pd.concat(out).to_csv(f, index=False)
            print(f"held-out {w} without {drop}, seed {off}: {len(d)} bags, {time.time() - t0:.0f}s", flush=True)
    print("done", flush=True)


def embed18():
    """X1 control: frozen ResNet-18 (ImageNet) avgpool features, same patches and
    per-well colour standardisation, mean over the 16 patches of each bag."""
    dev = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    b = table()
    tiles = pd.DataFrame([{"patch_path": str(C.PATCH_DIR / r.well / f"{r.stem}__{t}.jpg"), "well": r.well,
                           "depth_m": r.depth_m, "y": 0.0} for r in b.itertuples() for t in TILES])
    tiles = tiles[tiles.patch_path.map(lambda p: __import__("os").path.exists(p))].reset_index(drop=True)
    stats = V2.well_stats(b)
    m = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    m.fc = nn.Identity()
    m = m.to(dev).eval()
    F = np.zeros((len(tiles), 512), np.float32)
    with torch.no_grad():
        for x, _, i in DataLoader(DS(tiles, False, stats), batch_size=128, num_workers=4):
            F[i.numpy()] = m(x.to(dev)).cpu().numpy()
    df = pd.DataFrame(F).assign(well=tiles.well, depth_m=tiles.depth_m)
    df.groupby(["well", "depth_m"], as_index=False).mean().to_pickle(OUT / "frozen_r18_bag_features.pkl")
    print("frozen ResNet-18 features written", flush=True)


def evaluate():
    import json
    b = table()
    p = pd.read_csv(OUT / "cnn_sial_predictions.csv")
    base, _ = EV.load_tables()
    s1 = pd.read_csv(C.WORK_DIR / "v7" / "step1_predictions.csv")
    wells, d = base.well.values, base.depth_m.values.astype(float)
    S = s1.in_S.values.astype(bool) & np.isfinite(s1.T1.values)
    cnn = base[["well", "depth_m"]].merge(p, on=["well", "depth_m"], how="left").p.values
    s_cnn = M.per_well_hp(cnn, s1.T1.values, wells, d, S)
    s_rd = M.per_well_hp(s1.pred_RD.values, s1.T1.values, wells, d, S)
    both = pd.concat([s_cnn, s_rd], axis=1, keys=["cnn", "rd"]).dropna()
    fz = pd.read_pickle(OUT / "frozen_r18_bag_features.pkl")
    X18 = base[["well", "depth_m"]].merge(fz, on=["well", "depth_m"], how="left").drop(columns=["well", "depth_m"]).values.astype(float)
    S18 = S & np.isfinite(X18).all(1)
    p18, _ = M.cv_predict(M.zwell_mat(X18, wells, S18), s1.T1.values, wells, d, S18, "RD", lambda w: w)
    s_18 = M.per_well_hp(p18, s1.T1.values, wells, d, S)
    b18 = pd.concat([s_cnn, s_18], axis=1, keys=["cnn", "r18"]).dropna()
    res = {"CNN vs T1": {**M.summarise(s_cnn), "per_well": s_cnn.round(4).to_dict()},
           "CONTROL frozen ResNet-18 + R-D pipeline vs T1": {**M.summarise(s_18), "per_well": s_18.round(4).to_dict()},
           "paired CNN > frozen R18 p (fine-tuning claim)": float(wilcoxon(b18.cnn - b18.r18, alternative="greater").pvalue),
           "paired CNN < frozen R18 p": float(wilcoxon(b18.cnn - b18.r18, alternative="less").pvalue),
           "R-D vs T1 (step 1)": {**M.summarise(s_rd), "per_well": s_rd.round(4).to_dict()},
           "paired CNN > R-D p": float(wilcoxon(both.cnn - both.rd, alternative="greater").pvalue),
           "paired CNN < R-D p": float(wilcoxon(both.cnn - both.rd, alternative="less").pvalue)}
    T = import_module("58_v7_mudlog_tests")
    _, _, w3, d3, s13, t3, S3 = T.load()
    e = pd.read_csv(T.OUT / "C4_eligibility.csv")
    elig = e[e.eligible].well.tolist()
    res["CNN vs mud-log sand (6 wells, descriptive)"] = T.summ(T.per_well(cnn, t3.Y.values, w3, d3, S3, elig))
    with open(OUT / "x1_results.json", "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


def evaluate_seeds():
    """v8 part C: X1 with two more seeds (offsets 1000 and 2000). Same statistic and comparisons as X1."""
    import json
    base, _ = EV.load_tables()
    s1 = pd.read_csv(C.WORK_DIR / "v7" / "step1_predictions.csv")
    wells, d = base.well.values, base.depth_m.values.astype(float)
    S = s1.in_S.values.astype(bool) & np.isfinite(s1.T1.values)
    T1 = s1.T1.values
    files = {0: "cnn_sial_predictions.csv", 1000: "cnn_sial_predictions_seed1000.csv", 2000: "cnn_sial_predictions_seed2000.csv"}
    P, R = {}, {}
    for k, f in files.items():
        p = pd.read_csv(OUT / f)
        P[k] = base[["well", "depth_m"]].merge(p, on=["well", "depth_m"], how="left").p.values
        R[k] = M.per_well_hp(P[k], T1, wells, d, S)
    R = pd.DataFrame(R)
    fz = pd.read_pickle(OUT / "frozen_r18_bag_features.pkl")
    X18 = base[["well", "depth_m"]].merge(fz, on=["well", "depth_m"], how="left").drop(columns=["well", "depth_m"]).values.astype(float)
    S18 = S & np.isfinite(X18).all(1)
    p18, _ = M.cv_predict(M.zwell_mat(X18, wells, S18), T1, wells, d, S18, "RD", lambda w: w)
    t = pd.DataFrame({"mean3": R.mean(1), "seed_sd": R.std(1, ddof=1), "r18": M.per_well_hp(p18, T1, wells, d, S),
                      "rd": M.per_well_hp(s1.pred_RD.values, T1, wells, d, S),
                      "ensemble": M.per_well_hp(np.nanmean(np.column_stack(list(P.values())), axis=1), T1, wells, d, S)})
    w = lambda a, b, alt: float(wilcoxon(t[a] - t[b], alternative=alt).pvalue)
    res = {"per_well_by_seed": R.round(4).to_dict(orient="index"), "per_well": t.round(4).to_dict(orient="index"),
           "median_by_seed": R.median().round(4).to_dict(), "median_seed_sd": float(t.seed_sd.median()),
           "mean over 3 seeds vs T1": M.summarise(t.mean3), "ensemble of 3 seeds vs T1": M.summarise(t.ensemble),
           "paired mean3 > frozen R18 p (fine-tuning claim)": w("mean3", "r18", "greater"), "paired mean3 < frozen R18 p": w("mean3", "r18", "less"),
           "wells mean3 > frozen R18": int((t.mean3 > t.r18).sum()),
           "paired mean3 > R-D p": w("mean3", "rd", "greater"), "wells mean3 > R-D": int((t.mean3 > t.rd).sum()),
           "paired ensemble > frozen R18 p": w("ensemble", "r18", "greater"), "paired ensemble > R-D p": w("ensemble", "rd", "greater"),
           "34_8-3 by seed": R.loc["34_8-3"].round(4).to_dict(),
           "34_8-3 reproduces (both new seeds >= 0.15)": bool((R.loc["34_8-3", [1000, 2000]] >= 0.15).all())}
    with open(OUT / "x1_seeds_results.json", "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(pd.concat([R.round(3), t.round(3)], axis=1).to_string())
    print(json.dumps({k: v for k, v in res.items() if not k.startswith("per_well")}, indent=1, default=float))


if __name__ == "__main__":
    {"train": train, "trainx": train_notwin, "embed": embed18, "eval": evaluate, "evalseeds": evaluate_seeds}[sys.argv[1]]()
