# v7 plan: sample-matched targets. DRAFT for review; nothing computed.

The user's order: (1) photos predict cuttings chemistry, then (2) a photo
glauconite detector, then (3) mud-log lithology labels. This file fixes
step 1; steps 2 and 3 get their own sections before they run.
Status: exploratory; the same wells were used before.

## Step 1: can cuttings photographs predict the chemistry of the same bag?

**Why:** GR labels measure the formation at a point; the photograph and the
XRF measure the same bag. All 5,038 W_1 photographs in 11 wells have a
matched XRF analysis, against 590 GR labels.

**Target T** (sandiness proxy):
- log10(Si/Al), corrected for barite dilution within each well:
  T = log10(Si/Al) - b*(log10 Ba - median log10 Ba), with b from an OLS of
  log10(Si/Al) on log10(Ba) over that well's bags (only if b < 0).
- Then z-scored within the well, since wells have analytical offsets.

**Inputs** (existing, unchanged):
- **R-D (primary):** ResNet-50 RGB embeddings, per-well z.
- **R-E:** the 15 engineered features, per-well z.
- **Model:** StandardScaler -> [PCA 32 for R-D] -> Ridge (alpha = 1.0),
  fitted on the training wells only.

**Validation:**
- Leave-one-well-out over all 11 wells (primary).
- Leave-one-area-out (secondary): areas 24/9 (2 wells), 34/4 (2), 34/7
  (5: -1, -4, -6, -9, -10), 34/8 (2).

**Primary endpoint:**
- Per held-out well, Spearman rho between predicted and measured T after
  both are high-passed: minus the centred running median over +/-50 m
  within continuous stretches (gaps > 30 m split). This measures LOCAL
  skill, not shared depth trends.
- One-sided Wilcoxon of the 11 per-well rho against 0.

**Secondary:**
- Unfiltered per-well Spearman.
- Leave-one-area-out version of the primary.
- **Baselines with the same statistics:** relative depth (sign from
  training wells) and bag dry weight (sign from training wells).
- **Leakage:** within-well rho(prediction, log Ba) and rho(prediction,
  Cl).
- **Downstream:** the AUC of predicted T for the v2 GR sand/clay labels
  (7 eligible wells), next to the v2/v3 signals, plus local AUC (< 50 m).

**What counts:**
- "Photos carry local chemical information" if the primary p < 0.05 and
  the median high-passed rho > 0.
- Anything else is reported as it stands.
