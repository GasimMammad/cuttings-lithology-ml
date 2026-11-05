# v3 plan (revised 2026-11-05 after independent review)

v2 stays frozen as run. v3 is a declared follow-up. The seven v2 test wells
have been seen, so v3 numbers on them are exploratory. The one new
validation (section C) is fixed here before it is computed.

## 1. What the review changed (draft of this file -> this version)

| draft item | decision | reason |
|---|---|---|
| A. 12-way nested selection (E2/D2/ensemble x smoothing x soft labels) | **dropped** | 9 inner wells; the choice flips on one 8 m Etive bed in 34/8-3 A; nesting cannot undo that the candidates were designed after seeing the wells |
| B. median smoothing over +/-1 photo | **dropped** | erases single-photo sands (34/7-4 1040 m, 34/7-9 1040 m, both 34/7-10 sands), i.e. exactly the thin bodies the thesis is about |
| C. soft labels | not run in v3 | code already excluded "unstable" depths and balanced by label mass, but the reviewer's point stands that the target should be averaged over the cuttings bag interval, not taken at the centre depth; that is a label redesign for later |
| D. 34/7-1 mud-log test as confirmatory | **demoted, not run** | not blind (34/7-1 was a v1 hold-out fold and the v1 mud-log probe used the same PDF); the open hole is almost all claystone (low power); the scanned 1984 column is sparse symbols plus text, and a fair test needs two independent digitisers |
| new | relative-depth baseline with a fair sign rule | v2's depth-only baseline learned its sign by pooling wells, which let deep 24/9-3 and Jurassic sands pick the wrong direction; with the sign from the mean of per-well training AUCs, relative depth alone reaches median AUC 0.57, 6/7 wells, p = 0.039 |
| new | local AUC (sand-clay pairs < 50 m apart) | asks whether a signal separates beds or only intervals |
| new | single-feature model chosen inside each fold | the 15-feature regression loses to one feature, because texture features flip sign between loose Tertiary sand and Jurassic sandstone chips |
| new | cuttings XRF Si/Al as a sample-matched reference | same bag as the photograph; independent of GR; shows what the cuttings themselves record |

## 2. Re-check of v2 (34_v3_baselines.py), already computed

| signal | median AUC | wells > 0.5 | minus rel. depth (paired p) | local50 wells > 0.5 |
|---|---|---|---|---|
| E2 (v2 primary) | 0.73 | 6/7 | p = 0.148 | 3/6 |
| D1 ResNet-50 raw | 0.73 | 7/7 | p = 0.039 | 5/6 (p = 0.047) |
| one feature (chosen in fold) | 0.84 | 6/7 | p = 0.039 | 5/6 (p = 0.109) |
| XRF Si/Al (reference) | 0.81 | 6/7 | p = 0.078 | 5/6 |
| relative depth | 0.57 | 6/7 | - | 1/6 |

The feature chosen in 9 of 10 folds is `bright_lowsat_meanarea` (mean size of bright, low-saturation
grains, i.e. clear quartz), from the feature list frozen in July 2026.

## 3. Pre-registered v3 validation: shallow unlabelled intervals vs cuttings XRF

Fixed before computation (no shallow-interval prediction has been compared
with XRF yet):

- **Depths:** every W_1 photograph WITHOUT a sand/clay/mixed/unstable label
  (labels excluded_zone or no_log) above the top of the Shetland Gp in each
  well (Tertiary overburden: through-casing stretches, Balder, zones without
  anchors, the whole of 34/7-1). XRF must exist at that depth.
- **Signals (each from a model that never saw that well):** ONE_FEATURE
  (primary), D1, E2. For 34/7-1, models are trained on all 10 labelled wells.
- **Detrending:** both the signal and Si/Al are high-passed within each
  continuous stretch: subtract the centred running median over +/-50 m.
  This removes depth/compaction trends and casing-section steps, so the
  test is local.
- **Statistic:** per-well Spearman rho between the high-passed signal and the
  high-passed Si/Al; wells with >= 30 such depths. Primary test: one-sided
  Wilcoxon of per-well rho > 0 across wells.
- **Known confounds, stated in advance:** biogenic silica in Hordaland /
  Brygge mudstones raises Si/Al without sand; barite dilution; cavings.
  A positive result means "photos and chemistry of the same cuttings agree on
  sandiness", not "GR-sand detected".

## 4. v3b: bag-interval labels (pre-registered 2026-11-05, before computation)

Motivation (review round 1, O4b): a cuttings bag at nominal depth D holds
material drilled since the previous sample, i.e. the interval (D_prev, D]
under the usual "sample depth = bottom of interval" convention (~10 m in the
34/x wells, ~3-5 m in 24/9-3), while v2 labels use GR Vsh at D +/- 3 m.

- **Targets per photo** (zone GR, zone anchors exactly as v2, interval wholly
  inside one zone else missing):
  Vsh_int = mean Vsh over (D_prev, D];  NSF = fraction of that interval with
  Vsh < 0.30 (net-sand fraction).
- **Signals (unchanged, existing blind predictions):** ONE_FEATURE
  (primary), D1, E2, bag dry weight (image-free reference).
- **Primary test:** per held-out labelled well, over all in-zone photos
  (sand/clay/mixed/unstable), Spearman rho(signal, -Vsh_int) minus
  rho(signal, -Vsh_point). One-sided Wilcoxon across the 10 labelled wells
  that it is > 0, i.e. photos track the bag interval better than the point.
- **Secondary:** local AUC (pairs < 50 m) with interval classes:
  sand = NSF >= 0.7, clay = NSF <= 0.1.
- **Sensitivity (not tests):** centred interval (D - s/2, D + s/2) and the
  interval below (D, D + s).
- No model is retrained in this step.
