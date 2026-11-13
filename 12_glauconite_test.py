"""
Fig. A7 -- tier-2 balanced accuracy per model with 95% confidence intervals.

Reads the leave-one-well-out (tier 2) fold results written by
08_compare_models.py to final_comparison/results.json and plots, for each of
the four models (cnn_colour, cnn_gray, eng_full, eng_nocolour), the mean
balanced accuracy across held-out wells with a t-interval error bar.
Folds with a missing or non-finite balanced accuracy are skipped.

Reference lines: chance (0.50) and the majority-class (always-clay) baseline
(0.81, hard-coded), so no accuracy is read as success on its own.

NB the t critical value (4.303) is fixed for df = 2, i.e. three folds. If the
fold count changes, the interval width is wrong.

Outputs (in C.FIG_DIR): FigA7_balanced_accuracy.pdf (vector, Type 42 fonts)
and FigA7_balanced_accuracy.png (400 dpi).

Run:  python 12_glauconite_test.py
"""
import json
import math
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import config as C

# 1. PUBLICATION FORMATTING
mpl.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'pdf.fonttype': 42, 
    'ps.fonttype': 42,
})

# 2. LOAD CV RESULTS
results_path = C.WORK_DIR / "final_comparison" / "results.json"
if not results_path.exists():
    print(f"[ERROR] Could not find results file at {results_path}")
    exit(1)

with open(results_path, "r") as f:
    res = json.load(f)

models = ["cnn_colour", "cnn_gray", "eng_full", "eng_nocolour"]
labels = ["CNN Colour", "CNN Greyscale", "Engineered 15", "Engineered No-Colour"]
means, errs = [], []

# 3. COMPUTE METRICS & 95% CONFIDENCE INTERVALS (t-interval, df=2, n=3 folds)
for m in models:
    bals = [v["balanced_acc"] for v in res["tier2"][m].values() if v and np.isfinite(v["balanced_acc"])]
    mean = np.mean(bals)
    sd = np.std(bals, ddof=1) if len(bals) > 1 else 0.0
    half_ci = 4.303 * sd / math.sqrt(len(bals)) if len(bals) > 1 else 0.0
    means.append(mean)
    errs.append(half_ci)

# 4. ADVANCED PUBLICATION PLOTTING
fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
x_pos = np.arange(len(models))

# Base reference lines
ax.axhline(0.50, color='#C0392B', linestyle='--', linewidth=1.5, label='Chance (0.50)')
ax.axhline(0.81, color='#7F8C8D', linestyle=':', linewidth=1.5, label='Majority-Class Baseline (0.81)')

# Error bars & points
ax.errorbar(x_pos, means, yerr=errs, fmt='o', color='#2980B9', ecolor='#2980B9', 
            elinewidth=2, capsize=6, capthick=2, markersize=8, zorder=3)

ax.set_xticks(x_pos)
ax.set_xticklabels(labels, fontsize=9.5, fontweight='bold', color='#2C3E50')
ax.set_ylabel('Balanced Accuracy', fontsize=10, fontweight='bold')
ax.set_ylim(0.3, 0.95)
ax.set_title('Fig. A7: Tier-2 Model Balanced Accuracy with 95% Confidence Intervals\n(Leave-One-Well-Out Cross-Validation)', 
             fontsize=11, fontweight='bold', pad=15)
ax.grid(axis='y', linestyle='-', alpha=0.3, zorder=0)
ax.legend(loc='upper right', fontsize=9, framealpha=0.95)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

fig.tight_layout()

# 5. EXPORT
pdf_out = C.FIG_DIR / "FigA7_balanced_accuracy.pdf"
png_out = C.FIG_DIR / "FigA7_balanced_accuracy.png"
fig.savefig(pdf_out, format='pdf', bbox_inches='tight')
fig.savefig(png_out, dpi=400, bbox_inches='tight')
print(f"Success! Fig A7 generated at: {png_out}")