"""
34/8-A-14 H mud-log lithology plotted against TVD and against horizontal
distance. LITH codes are plotted RAW (documented in the mud-log INF file only
as "NPD Codes"; the code table is not present in these files, so nothing is
decoded or interpreted here).
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import config as C

D = C.WORK_DIR / "mudlog_34_8-A-14_H.csv"
OUT = C.FIG_DIR / "13_A14H_lithology.png"
TOPS = {"Utsira Fm": 1538, "Top Utsira 2": 2137, "Base Utsira 2": 2540,
        "Top Hordaland": 2747, "Top Sand Hordaland": 3110,
        "Base Sand Hordaland": 3745.7}
CMAP = {300: "#E8C15A", 300.17: "#E0B040", 330.17: "#C89A3A", 600: "#7FA8C9",
        600.27: "#6E95B8", 610: "#5C82A6", 620: "#4A6E93", 620.27: "#3A5A80"}


def main():
    d = pd.read_csv(D)
    codes = sorted(d.LITH.dropna().unique())
    fig, axes = plt.subplots(2, 1, figsize=(15, 9))
    for ax, xcol, xlab in [
            (axes[0], "DVER", "TRUE VERTICAL DEPTH (m RKB)"),
            (axes[1], "HD", "HORIZONTAL DISTANCE from slot (m)")]:
        x = d[xcol].values
        sub = d.dropna(subset=["LITH"])
        for c in codes:
            s = sub[sub.LITH == c]
            ax.bar(s[xcol].values, 1.0, width=6.0, bottom=1.0,
                   color=CMAP.get(c, "#999999"), linewidth=0)
        ax.plot(x, 0.55 + 0.4 * d.ROPA / d.ROPA.max(), lw=0.5, color="#333333")
        ax.plot(x, 0.02 + 0.45 * d.GASX / max(d.GASX.max(), 1e-9),
                lw=0.5, color="#B5462F")
        a = np.interp(TOPS["Top Sand Hordaland"], d.DEPT, x)
        b = np.interp(TOPS["Base Sand Hordaland"], d.DEPT, x)
        ax.axvspan(a, b, color="#E8C15A", alpha=0.16, zorder=0)
        for k, md in TOPS.items():
            xi = np.interp(md, d.DEPT, x)
            ax.axvline(xi, color="#333333", lw=0.8, ls="--")
            ax.text(xi, 2.05, k, rotation=90, fontsize=6.5, va="bottom", ha="center")
        ax.set_xlabel(xlab)
        ax.set_ylim(0, 2.0)
        ax.set_yticks([])
        ax.text(0.002, 0.93, "LITH code", transform=ax.transAxes,
                fontsize=8, fontweight="bold")
        ax.text(0.002, 0.55, "ROP (scaled)", transform=ax.transAxes,
                fontsize=8, color="#333333")
        ax.text(0.002, 0.06, "total gas (scaled)", transform=ax.transAxes,
                fontsize=8, color="#B5462F")
        ax.grid(alpha=0.25, axis="x")
    axes[1].legend(handles=[Patch(facecolor=CMAP.get(c, "#999"), label=f"{c:g}")
                            for c in codes],
                   title="LITH (NPD code — NOT decoded)", fontsize=7,
                   title_fontsize=7, ncol=4, loc="upper right")
    fig.suptitle("34/8-A-14 H mud log — LITH codes plotted RAW, no geological "
                 "interpretation applied.  Shaded = Top→Base Sand Hordaland "
                 "(3110–3745.7 m MD).", fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUT, dpi=140)
    print("figure:", OUT)


if __name__ == "__main__":
    main()
