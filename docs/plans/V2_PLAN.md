# v2 analysis plan (written 2026-11-05, BEFORE any v2 model was fitted)

This file fixes what counts as the v2 result before any v2 model was run. The v1
result (four models, three usable folds, every 95% CI containing 0.50) stays
the primary thesis finding. v2 is a declared follow-up that tests two
diagnoses of why v1 failed:

1. **Too little labelled data and too few testable wells.** v1 had 85 sand depths, 65 of them from
   one well, and 3 folds with sand.
2. **Well-level domain shift.** In v1's held-out predictions the whole
   well moved together: the colour CNN gave p(sand) ~0.98 to almost every depth of 24/9-4
   and ~0.03 to almost every depth of 24/9-3, sand or clay.

## Data and labels (fixed before modelling)

- 11 wells with W_1 cuttings photographs; 10 receive labels (34/7-1 has no
  clean sand in any open-hole run and gets none).
- Label rules: see `config.py` (v2 LABEL DESIGN block) and
  `V2_LABEL_DECISIONS.md`. Same Vsh thresholds (0.30 / 0.60) and the same
  +/-3 m class-consistency filter as v1.
- Resulting labelled depths (W_1): 123 sand, 467 clay.
- Unit of analysis: one depth (one photograph, 16 tiles aggregated).

## Validation

- Leave-one-well-out over the 10 labelled wells. A held-out well is never
  used for fitting, feature scaling, PCA or threshold choice, except as
  stated for label-free per-well normalisation below.
- **Label-free per-well normalisation** ("per-well z"): each feature is
  z-scored within its own well using the mean and SD over ALL W_1 photographs
  of that well (labelled or not). No labels enter this step. It needs
  only the held-out well's own photographs, which are available in any real
  application.

## Primary endpoint

- **Per-well ROC AUC** of predicted p(sand) on the held-out well's labelled
  depths (threshold-free, so it is immune to calibration shift between wells).
- **Eligible wells**: at least 3 sand AND at least 3 clay labelled depths. With the
  fixed labels these are 24/9-3, 24/9-4, 34/7-4, 34/7-6, 34/7-9, 34/8-3,
  34/8-3 A (n = 7). The other three labelled wells are used for training and
  reported, but are not in the primary test.
- **Test**: one-sided Wilcoxon signed-rank test of the 7 per-well AUCs
  against 0.5, alpha = 0.05. Summary: median and mean AUC, with a
  well-level bootstrap 95% CI for the mean.

## Primary model

**E2**: the frozen 15 engineered features (`features.py`, unchanged), depth
level = median over 16 tiles, per-well z, then the v1 classifier unchanged
(L2 logistic regression, C = 1, class_weight = balanced, StandardScaler fitted
on training wells).

Rationale: it differs from v1's `eng_full` in exactly one step, the
normalisation aimed at diagnosis 2.

## Secondary models (Holm correction across these five)

| id | description |
|----|-------------|
| E1 | v1 `eng_full` unchanged (no per-well z): v1 method on v2 labels |
| E3 | engineered, colour block removed, per-well z |
| D1 | frozen ImageNet ResNet-50 embeddings (2048-d, mean over 16 tiles), PCA to 32 dims fitted on training wells, same logistic regression; no per-well z |
| D2 | D1 with per-well z (applied before PCA) |
| D3 | D2 on greyscale input |

## Secondary analyses (descriptive, no correction)

- Pooled balanced accuracy at p = 0.5, sand recall and precision (Wilson CIs).
- **Tertiary-only** per-well AUC (Jurassic zones of 34/8-3 and 34/8-3 A
  removed), because the thesis question is about the shallow overburden.
- **Within-zone** AUC (sand and clay from the same label zone).
- **Leakage checks**: Spearman rho of p(sand) against Ba (ppm) and against
  depth, within clay-labelled depths only; and a **depth-only baseline**
  (AUC of depth alone, sign chosen on the training wells) per well.
- **Continuous target**: ridge regression of Vsh on the same inputs, using
  every in-zone depth (sand, clay, mixed, unstable); per-well Spearman rho
  between predicted and log Vsh; Wilcoxon against 0.
- Blind sand-fraction logs for held-out wells against GR.

## What would count as "it works"

Primary test p < 0.05 AND the Tertiary-only per-well AUCs mostly above 0.5 AND
no leakage flag (|rho| with Ba or depth within clay below 0.3, and the model
beating the depth-only baseline). Anything less is reported as it stands.
