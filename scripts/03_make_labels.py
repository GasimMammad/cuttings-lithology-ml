"""
STEP 3 -- Attach gamma ray to every cuttings photo and turn it into a label.
Reworked 2026-07-31, zoned version.

Labels come from shale volume, not absolute API:
    Vsh = (GR - GR_clean) / (GR_shale - GR_clean), clipped to [0, 1]
with GR_clean / GR_shale taken as median GR over NAMED known-lithology
anchor intervals -- per ZONE, because one calibration does not hold along a
whole well (composited logs splice runs; Triassic red beds are a different
GR regime; the Cretaceous Shetland Gp is carbonate-prone, where low GR means
marl, not sand). Photos outside every zone are "excluded_zone".

Thresholds (single pair across all wells and zones):
    Vsh < VSH_SAND_MAX -> sand,  Vsh > VSH_CLAY_MIN -> clay,  else mixed.

Stability (class consistency): a label is kept only if EVERY Vsh sample of
that zone within +/- GR_STABILITY_WINDOW_M falls in the same class as the
centre value, so metres of cuttings-lag error cannot flip the label.

Outputs (dry run): per-well QC figures (GR vs depth with tops, zones and
anchors + per-zone histograms), a cross-well Vsh histogram, label counts.
--commit additionally writes the labels CSV and the endmember table.

Run:  python 03_make_labels.py            (dry run)
      python 03_make_labels.py --commit
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config as C

try:
    import lasio
except ImportError:
    raise SystemExit("Missing lasio. Run:  pip install lasio")


# =============================================================================
# data loading
# =============================================================================

def load_gr(las_path: Path, depth_range=None) -> pd.Series:
    """Depth-indexed GR series from a specific LAS file (config.GR_SOURCES)."""
    las = lasio.read(str(las_path), engine="normal")
    df = las.df()
    upper = {c.upper(): c for c in df.columns}
    for alias in C.GR_ALIASES:
        if alias.upper() in upper:
            s = df[upper[alias.upper()]].dropna()
            s = s[(s > 0) & (s < 500)]
            if len(s) > 50:
                s = s.sort_index()
                if depth_range is not None:
                    s = s[(s.index >= depth_range[0]) & (s.index <= depth_range[1])]
                return s
    raise ValueError(
        f"No usable GR curve in {las_path.name}. Curves present: {list(df.columns)}")


def load_tops(well: str) -> pd.DataFrame:
    """NPD formation tops from Wells/files/, if present (for QC figures)."""
    f = C.SSD_ROOT / "Wells" / "files" / f"Well_{well.replace('_', '-', 1)}_FormationTops.txt"
    if not f.exists():
        # v2: some wells keep tops in their own folder (34_7-6)
        alt = C.SSD_ROOT / "Wells" / well / "Formation_tops.txt"
        if alt.exists():
            t = pd.read_csv(alt, sep="\t")
            return pd.DataFrame({"MD_TOP_mMD_RKB": t.iloc[:, 0],
                                 "SURFACE_NAME": t.iloc[:, 1].str.strip()})
        return pd.DataFrame(columns=["SURFACE_NAME", "MD_TOP_mMD_RKB"])
    return pd.read_csv(f, sep="\t")


# =============================================================================
# labelling machinery
# =============================================================================

def anchored_endmembers(gr: pd.Series, zone: dict):
    """Median GR over the zone's named anchor intervals -> (clean, shale, info)."""
    info, out = {}, {}
    for kind in ("sand", "shale"):
        top, base, name = zone[kind]
        seg = gr[(gr.index >= top) & (gr.index <= base)]
        if len(seg) < 20:
            raise ValueError(f"anchor '{name}' ({top}-{base} m): only {len(seg)} samples")
        out[kind] = float(seg.median())
        info[kind] = {"top": top, "base": base, "name": name, "median": out[kind],
                      "p10": float(seg.quantile(0.10)),
                      "p90": float(seg.quantile(0.90)), "n": len(seg)}
    if out["shale"] - out["sand"] < 10:
        raise ValueError(f"endmembers too close: clean {out['sand']:.0f}, "
                         f"shale {out['shale']:.0f} API")
    return out["sand"], out["shale"], info


def classify(v):
    if not np.isfinite(v):
        return "no_log"
    if v < C.VSH_SAND_MAX:
        return "sand"
    if v > C.VSH_CLAY_MIN:
        return "clay"
    return "mixed"


def label_well(grp: pd.DataFrame, gr: pd.Series, zones: list):
    """
    Returns (vsh, label, zone_id) arrays for the photos of one well.
    Default label: no_log outside the logged range, excluded_zone inside the
    log but outside every zone.
    """
    depths = grp.depth_m.values.astype(float)
    d_all = gr.index.values.astype(float)
    v_all = gr.values.astype(float)
    w = C.GR_STABILITY_WINDOW_M

    vsh = np.full(len(depths), np.nan)
    zone_id = np.full(len(depths), -1)
    labels = np.array(
        ["no_log" if (z < d_all.min() or z > d_all.max()) else "excluded_zone"
         for z in depths], dtype=object)

    zinfo = []
    for zi, zone in enumerate(zones):
        zmin, zmax = zone["range"]
        gr_clean, gr_shale, info = anchored_endmembers(gr, zone)
        m = (d_all >= zmin) & (d_all <= zmax)
        dz, vz = d_all[m], np.clip((v_all[m] - gr_clean) / (gr_shale - gr_clean), 0, 1)
        zinfo.append({"zone": zi, "range": (zmin, zmax),
                      "clean": gr_clean, "shale": gr_shale, "info": info,
                      "d": dz, "vsh": vz})

        sel = (depths >= zmin) & (depths <= zmax) & (depths >= dz.min()) & (depths <= dz.max())
        if not sel.any():
            continue
        vs = np.interp(depths[sel], dz, vz)
        vsh[sel] = vs
        zone_id[sel] = zi
        lab = []
        for z, v in zip(depths[sel], vs):
            cls = classify(v)
            if cls in ("sand", "clay"):
                win = vz[(dz >= z - w) & (dz <= z + w)]
                if win.size < 3:
                    cls = "unstable"
                elif cls == "sand" and not (win < C.VSH_SAND_MAX).all():
                    cls = "unstable"
                elif cls == "clay" and not (win > C.VSH_CLAY_MIN).all():
                    cls = "unstable"
            lab.append(cls)
        labels[sel] = lab
    return vsh, labels, zone_id, zinfo


# =============================================================================
# QC figure per well
# =============================================================================

def qc_figure(well, gr, zones_info, tops, photo_depths):
    ncols = 1 + max(1, len(zones_info))
    fig = plt.figure(figsize=(4 + 3.2 * (ncols - 1), 11))
    gs = fig.add_gridspec(1, ncols, width_ratios=[1.6] + [1] * (ncols - 1))

    # ---- track: GR vs depth ----
    ax = fig.add_subplot(gs[0])
    ax.plot(gr.values, gr.index.values, lw=0.4, color="#333333")
    ax.invert_yaxis()
    ax.set_xlabel("GR (API)")
    ax.set_ylabel("Depth (m MD RKB)")
    ax.set_xlim(0, np.percentile(gr.values, 99.5) * 1.15)
    for _, t in tops.iterrows():
        ax.axhline(t.MD_TOP_mMD_RKB, color="#888888", lw=0.6, ls=":")
        ax.text(ax.get_xlim()[1] * 0.99, t.MD_TOP_mMD_RKB, t.SURFACE_NAME,
                fontsize=5.5, va="bottom", ha="right", color="#555555")
    for zi in zones_info:
        zmin, zmax = zi["range"]
        ax.axhspan(zmin, max(zmin, gr.index.min()) if zmin == 0 else zmin,
                   color="none")
        ax.axhspan(max(zmin, gr.index.min()), min(zmax, gr.index.max()),
                   color="#55A868", alpha=0.08)
        for kind, colour in (("sand", "#DD8452"), ("shale", "#C44E52")):
            i = zi["info"][kind]
            ax.axhspan(i["top"], i["base"], color=colour, alpha=0.35)
    if len(photo_depths):
        ax.plot(np.full(len(photo_depths), ax.get_xlim()[1] * 0.02),
                photo_depths, "|", color="#4C72B0", ms=3, alpha=0.5)
    ax.set_title(f"{well}\ngreen = label zones, orange/red = anchors,\n"
                 f"blue ticks = photo depths", fontsize=9, fontweight="bold")

    # ---- one histogram per zone ----
    for k, zi in enumerate(zones_info):
        axh = fig.add_subplot(gs[1 + k])
        zmin, zmax = zi["range"]
        seg = gr[(gr.index >= zmin) & (gr.index <= zmax)]
        axh.hist(seg.values, bins=60, color="#4C72B0", edgecolor="none")
        axh.axvline(zi["clean"], color="#DD8452", lw=2, label=f"clean {zi['clean']:.0f}")
        axh.axvline(zi["shale"], color="#C44E52", lw=2, label=f"shale {zi['shale']:.0f}")
        g_sand = zi["clean"] + C.VSH_SAND_MAX * (zi["shale"] - zi["clean"])
        g_clay = zi["clean"] + C.VSH_CLAY_MIN * (zi["shale"] - zi["clean"])
        axh.axvline(g_sand, color="#DD8452", ls="--", lw=1.3, label=f"Vsh .3 = {g_sand:.0f}")
        axh.axvline(g_clay, color="#C44E52", ls="--", lw=1.3, label=f"Vsh .6 = {g_clay:.0f}")
        axh.set_xlim(0, np.percentile(seg.values, 99.5) * 1.1)
        axh.set_title(f"zone {zi['zone']}: {zmin:.0f}-{zmax:.0f} m\n"
                      f"sand: {zi['info']['sand']['name']}\n"
                      f"shale: {zi['info']['shale']['name']}", fontsize=8)
        axh.set_xlabel("GR (API)")
        axh.legend(fontsize=7)
        axh.spines[["top", "right"]].set_visible(False)

    if not zones_info:
        axh = fig.add_subplot(gs[1])
        axh.hist(gr.values, bins=60, color="#999999", edgecolor="none")
        axh.set_xlim(0, np.percentile(gr.values, 99.5) * 1.1)
        axh.set_title("NO LABEL ZONES\n(well excluded from labelling)", fontsize=9)
        axh.set_xlabel("GR (API)")
        axh.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    out = C.FIG_DIR / f"03_qc_{well}.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# =============================================================================

def main(commit: bool):
    if not C.INDEX_CSV.exists():
        raise SystemExit("Run 02_build_index.py --commit first.")

    idx = pd.read_csv(C.INDEX_CSV)
    print(f"Loaded {len(idx):,} indexed photographs across {idx.well.nunique()} wells.\n")

    frames, endmember_rows = [], []
    for well, grp in idx.groupby("well"):
        grp = grp.copy()
        if well not in C.GR_SOURCES:
            print(f"[{well}] no GR source configured -- all photos no_log")
            grp["gr"] = np.nan; grp["vsh"] = np.nan; grp["zone"] = -1
            grp["zone_name"] = ""; grp["label"] = "no_log"; grp["las_file"] = ""
            frames.append(grp)
            continue

        rel, rng = C.GR_SOURCES[well]
        las_path = C.SSD_ROOT / "Wells" / rel
        gr = load_gr(las_path, rng)
        d = gr.index.values.astype(float)
        zones = C.LABEL_ZONES.get(well, [])

        depths = grp.depth_m.values.astype(float)
        grp["gr"] = np.interp(depths, d, gr.values, left=np.nan, right=np.nan)
        grp.loc[(depths < d.min()) | (depths > d.max()), "gr"] = np.nan
        vsh, labels, zone_id, zinfo = label_well(grp, gr, zones)
        grp["vsh"] = vsh; grp["label"] = labels; grp["zone"] = zone_id
        # human-readable zone tag, kept on every sample so per-zone
        # performance can be reported later (2026-07-31)
        grp["zone_name"] = [zones[i].get("name", f"z{i}") if i >= 0 else ""
                            for i in zone_id]
        grp["las_file"] = las_path.name
        frames.append(grp)

        print(f"[{well}] {las_path.name}  GR {d.min():.0f}-{d.max():.0f} m, "
              f"{len(zones)} label zone(s)")
        for zi in zinfo:
            for kind in ("sand", "shale"):
                i = zi["info"][kind]
                endmember_rows.append({"well": well, "zone": zi["zone"],
                                       "endmember": kind, **i})
                print(f"    zone {zi['zone']} GR_{'clean' if kind == 'sand' else 'shale'}"
                      f" = {i['median']:5.1f} API  <- {i['name']} "
                      f"({i['top']:.0f}-{i['base']:.0f} m, n={i['n']}, "
                      f"P10-P90 {i['p10']:.0f}-{i['p90']:.0f})")

        w1_depths = grp[grp.processing == "standard"].depth_m.values
        out = qc_figure(well, gr, zinfo, load_tops(well), w1_depths)
        print(f"    QC figure: {out}")

    df = pd.concat(frames, ignore_index=True)

    # ---- cross-well Vsh histogram (W_1 only) ----
    fig2, ax2 = plt.subplots(figsize=(9, 5))
    for well, grp in df[np.isfinite(df.vsh)].groupby("well"):
        w1 = grp[grp.processing == "standard"]
        if len(w1):
            ax2.hist(w1.vsh, bins=40, histtype="step", lw=1.8, label=well, density=True)
    ax2.axvline(C.VSH_SAND_MAX, color="#DD8452", ls="--", lw=2)
    ax2.axvline(C.VSH_CLAY_MIN, color="#C44E52", ls="--", lw=2)
    ax2.set_xlabel("Vsh at photo depths (zoned)")
    ax2.set_ylabel("density")
    ax2.set_title("Vsh at W_1 photo depths, by well", fontweight="bold")
    ax2.legend()
    ax2.spines[["top", "right"]].set_visible(False)
    fig2.tight_layout()
    out2 = C.FIG_DIR / "03_vsh_histogram.png"
    fig2.savefig(out2, dpi=150)
    print(f"\nFigure written: {out2}")

    # ---- counts (W_1 photos = unique sampled depths) ----
    w1 = df[df.processing == "standard"]
    print("\n" + "=" * 72)
    print("LABEL COUNTS (W_1 photos = unique sampled depths)")
    print("=" * 72)
    tab = pd.crosstab(w1.well, w1.label)
    for col in ("sand", "clay", "mixed", "unstable", "excluded_zone", "no_log"):
        if col not in tab:
            tab[col] = 0
    tab = tab[["sand", "clay", "mixed", "unstable", "excluded_zone", "no_log"]]
    tab.loc["TOTAL"] = tab.sum()
    print(tab.to_string())

    trainable = w1[w1.label.isin(C.CLASSES)]
    print(f"\nTRAINABLE DEPTHS: {len(trainable):,} "
          f"(x16 tiles = {16 * len(trainable):,} training patches)")
    if len(trainable):
        ratio = trainable.label.value_counts()
        print(ratio.to_string())
        if ratio.min() / ratio.max() < 0.15:
            print("\n  WARNING: heavy class imbalance across the pooled set.")

    if not commit:
        print("\n>>> DRY RUN. Nothing written. Inspect figures, then --commit")
        return

    df.to_csv(C.LABELS_CSV, index=False)
    pd.DataFrame(endmember_rows).to_csv(C.WORK_DIR / "03_endmembers.csv", index=False)
    print(f"\nWritten: {C.LABELS_CSV}")
    print(f"Written: {C.WORK_DIR / '03_endmembers.csv'}")
    print("Next: 04_prepare_patches.py")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true", help="write the labels file")
    main(ap.parse_args().commit)
