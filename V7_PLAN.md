# v7 plan: sample-matched targets

The user's order: (1) photos predict cuttings chemistry, then (2) a photo
glauconite detector, then (3) mud-log lithology labels. This file fixes
step 1; steps 2 and 3 get their own sections before they run.
Status: exploratory; the same wells were used before.

**Step 1 status:** FINAL (reviewer round 15: APPROVE WITH CHANGES, applied), merging:
- the draft (e0588e9);
- reviewer round 14;
- Agent 2 (geochemist, `v7/agent2_target_notes.md`);
- Agent 4 (ML/CV, `v7/agent4_notes.md`).

No photo-to-chemistry skill has been computed by anyone. The agents looked
only at chemistry against chemistry, GR, EXIF and the v6 G table.

## Step 1: can cuttings photographs predict the chemistry of the same bag?

**Why:** GR labels measure the formation at a point; the photograph and the
XRF measure the same bag. All 5,038 W_1 photographs in 11 wells have a
matched XRF analysis, against 590 GR labels.

### Data selection (fixed before computing)
- **Tertiary only:** depth < TOP_SHETLAND[well] (35_v3_xrf_shallow.py).
  The pre-Tertiary is reported separately, descriptively.
- **Exclude bags 0-15 m below every 30", 20" and 13 3/8" shoe** (Sodir
  casing table; the same mask as 42_v4_cement_mask.py).
- Bags with no XRF Si or Al are dropped.
- **Normalisation set:** every per-well z-score (inputs AND targets) uses this same
  Tertiary, shoe-masked bag set (not all photos as in v2).
- Bags with Al below the well's 5th percentile are kept in the primary and
  excluded in sensitivity S-Al.

### Targets
- **T1 (primary): z_well(log10(Si/Al)), uncorrected.**
  - Barite dilution scales Si and Al equally, so the ratio already cancels
    it (Agents 2 and 4 agree). The round-14 Theil-Sen Ba correction moved
    local agreement with GR Vsh the wrong way (median local rho -0.19
    uncorrected vs -0.15 corrected, 8 wells; Agent 2).
  - Disclosure: the target was chosen after a chemistry-vs-GR check (no photo
    skill seen); the difference was small (-0.19 vs -0.15; partialled -0.16).
  - Name: "detrital quartz + biogenic silica vs clay", not "sand".
    Oligocene ooze is biosiliceous.
- **T1 sensitivities:**
  - T1-TS: Theil-Sen Ba-corrected, with the slope clipped at 0.
  - T1-P: a partial Spearman controlling high-passed log Ba, log(Ca/Al) and
    log Cl.
- **T2 (secondary): z_well(log10 Ca), Ba-partialled (Theil-Sen).**
  - It captures shell and foram debris, carbonate cement and calcareous
    mud, as well as gypsum, lime and cement additives.
  - Report rho(Ca, S) per well as a gypsum flag.

### Inputs and models (existing features, unchanged)
- **R-D (primary):** ResNet-50 RGB embeddings, per-well z ->
  StandardScaler -> PCA 32 -> Ridge (alpha = 1). Fitted on training wells
  only. Kept for continuity with v2.
  (alpha chosen per outer fold for R-RAW is reported.)
- **R-RAW (pre-declared alternative):** raw 2048-d per-well z -> Ridge,
  with alpha chosen from {1, 10, 100, 1e3, 1e4} by inner LOWO on the
  training wells (median per-well high-passed rho), and equal well weights.
- **R-E (secondary):** the 15 engineered features, per-well z -> Ridge
  (alpha = 1).
- The alpha = 10 sensitivity from round 14 is dropped: on 32 PCs it is
  effectively OLS (Agent 4); R-RAW replaces it.

### Validation
- Leave-one-well-out over all 11 wells (primary).
- Leave-one-area-out as a stress test: 24/9 (2), 34/4 (2), 34/7 (5),
  34/8 (2). Leaving out 34/7 trains on 6 wells.
- Note: 34/8-3 and 34/8-3 A are near-twins, so LOWO is mildly optimistic
  for them.

### Primary endpoint
- **High-pass:** per held-out well, predicted and measured T1 are each
  high-passed by subtracting the centred running median over +/-50 m
  within continuous stretches (gaps > 30 m split; highpass() in
  35_v3_xrf_shallow.py).
- **Statistic:** the per-well Spearman rho of the two high-passed series.
  Sign: POSITIVE rho (predicted vs measured T1) = skill.
- **Test:** one-sided Wilcoxon of the 11 per-well rho against 0.
- **Interval:** a well-bootstrap 95% CI of the median rho.
- **Positive result:** "photos carry local chemical information" only if
  p < 0.05 AND median rho >= 0.10 (the effect-size floor).
- **Not-mud condition:** "not riding on barite/mud" may be added only if T1-P has
  the same sign with median partial rho >= 0.05; otherwise the claim is "photos
  predict Si/Al, possibly via mud residue".

### Per-well null and checks
- **Circular-shift null:** within each continuous stretch (gaps > 30 m split;
  no wrap-around across gaps), the high-passed prediction is circularly shifted
  against the target by every offset >= 10 bags (stretches < 30 bags excluded
  from the null). The per-well p is the rank of the observed rho.
  Shuffling is invalid because lag-1 autocorrelation after the high-pass
  is 0.06-0.76. Per-well p are descriptive; a Fisher combination is a
  SECONDARY test.
- **Lag profile:** rho of photo k against chemistry k+m for m = -5..+5.
  Shown against the no-skill curve rho(0) x ACF_T1(m). "Same bag" evidence =
  rho(0) clearly above that curve's shoulders, not merely a peak at m = 0.

### Sensitivities (reported, not tested for the claim)
- High-pass windows of +/-25 m and +/-5 bags.
- T1-TS, T1-P, S-Al.
- R-RAW and R-E.
- Leave-one-area-out.
- The unfiltered per-well Spearman.

### Baselines (same Tertiary series, same high-pass, paired Wilcoxon against R-D)
- Relative depth (expected near 0 after the high-pass).
- Bag dry weight, with the sign taken from the training wells.

### Leakage and negative controls
- **Photo -> Ba:** the same R-D pipeline with target z log10 Ba. If photos
  predict Ba much better than Si/Al, the barite coating is a channel; this
  is read together with T1-P.
- **High-passed Ba and Cl against prediction:** within-well rho.
- **Pipe-dope negative control:** residual Zn + Pb after regressing out
  Si/Al and Ba. Photos should NOT predict it (|median rho| < 0.10
  expected). Because barite carries Zn/Pb impurities, Zn+Pb are regressed on Ba
  first; a failure of this control is AMBIGUOUS, not proof of leakage.
- **Capture sessions (always run):** EXIF capture times -> session ids; high-pass
  within sessions as a sensitivity; reshoot test in 34/7-10. Run regardless of
  the primary outcome.

### Downstream (EXPLORATORY)
- The AUC of predicted T1 for the v2 GR sand/clay labels (7 wells), next to
  the v2/v3 signals.
- Local AUC (< 50 m).

### Interpretation guard
- 34/7-6 is expected to run the wrong way (biosiliceous ooze vs a
  glauconite-bearing sand). It stays in; no well is dropped after seeing
  results.
- Expected photo-XRF |rho|: unknown, likely < 0.3.
- If leave-one-area-out collapses (e.g. without 34/7), it is reported next to
  the primary, not in an appendix.

## Step 2 (outline; final section before it runs)
- **Target:** binary G > 0.2 (no Al floor; v6 exploratory, validated by
  the pellet check). Sensitivities at 0.15 and 0.3.
- **Data:** 27 positives over 5 wells. Position relative to THGU alone
  gives AUC 0.75-0.99.
- **Primary feature:** a pre-declared full-resolution dark-green round-blob
  count. Secondary: full-resolution ResNet crops with a regularised
  logistic regression.
- **Test:** conditional within +/-80 m of THGU, stratified rank-sum with a
  block null. Lista false positives must be <= 5%, and the detector must
  beat the green index in >= 4/5 wells. Feasibility claim only.
- Round 15: the blob parameters (hue/chroma/lightness gates, size px at full res,
  min circularity, tile coverage) are fixed in this file before running; the
  distance-to-THGU model is the baseline INSIDE the conditional test; effective
  positives are counted as independent intervals (~5-10), not bags.

## Step 3 (outline)
- Agent 5's mud-log inventory first; then decide on a digitisation route
  with a two-digitiser agreement gate.
