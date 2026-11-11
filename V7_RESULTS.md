# v7 results: step 1, photos -> cuttings XRF chemistry (2026-11-10). Reviewer round 16/16b: ACCEPTED, step 1 CLOSED

- **Plan:** V7_PLAN.md FINAL (b1eeb05).
- **Scripts:** 52_v7_photo_to_xrf.py (bdf7850, committed before the run) and
  52a_v7_capture_sessions.py.
- **Outputs:** results/v7/.
- **Status:** exploratory (the same wells were used in earlier rounds), but
  every choice was fixed before the run.

## Data
- Tertiary bags: 2,051. Shoe-masked: 30. Selected: 2,021 in 11 wells, all
  with XRF.
- Pre-Tertiary (descriptive): 2,928.

## Primary (R-D, LOWO, T1 = z log10 Si/Al uncorrected, +/-50 m high-pass)
- **Median per-well rho +0.32**, positive in **11/11 wells**, one-sided
  Wilcoxon p = 0.0005 (the minimum possible with 11 wells).
- Well-bootstrap 95% CI of the median: 0.18-0.49.
- **The pre-declared claim condition passes** (p < 0.05 and median >= 0.10).
- Per well:

  | well | rho |
  |---|---|
  | 24/9-3 | 0.46 |
  | 24/9-4 | 0.17 |
  | 34/4-6 | 0.49 |
  | 34/4-7 | 0.30 |
  | 34/7-1 | 0.19 |
  | 34/7-10 | 0.51 |
  | 34/7-4 | 0.48 |
  | 34/7-6 | 0.32 |
  | 34/7-9 | 0.53 |
  | 34/8-3 | **0.02** |
  | 34/8-3 A | 0.18 |

## Checks
| check | result |
|---|---|
| Not-mud condition, T1-P (partial on hp Ba, Ca/Al, Cl) | median +0.33, 11/11 -> PASS |
| Circular-shift null, per well | p <= 0.015 in 10/11 (34/8-3 p 0.43); Fisher (secondary) 3e-12 |
| Lag profile (median) | rho(0) 0.32 vs shoulders 0.06 (lag -1) and 0.13 (lag +1); no-skill shoulders 0.04. Rho(0) exceeds the shoulders in 9/11 wells (not in 24/9-4 or 34/8-3) |
| High-pass +/-25 m / +/-5 bags | 0.27 (10/11) / 0.33 (10/11) |
| T1-TS (Ba-corrected target) | 0.40 (10/11) |
| S-Al (Al < p5 removed) | 0.30 (11/11) |
| R-E (15 engineered features) | 0.30 (11/11) |
| R-RAW (2048-d, inner-LOWO alpha 100-1e4) | 0.29 (10/11) |
| Leave-one-area-out | 0.31 (10/11) |
| High-pass within capture sessions | 0.31 (11/11) |
| Unfiltered | 0.84 (shared depth trends; not the claim) |
| Baseline: relative depth (hp) | 0.04; R-D better, paired p 0.001 |
| Baseline: bag dry weight (hp) | -0.09; R-D better, paired p 0.0005 |
| Leakage: photo -> Ba | **0.31 (11/11)**: photos see barite too. The Si/Al skill survives partialling Ba (above) |
| Leakage: rho(pred T1, hp Ba) / (hp Cl) | -0.12 / -0.05 |
| Negative control: Zn+Pb residual | median 0.05 (< 0.10 expected) but 8/11 positive, p 0.012; 34/8-3 0.20. Pre-declared AMBIGUOUS |
| Reshoots (58 bags; descriptive) | median abs error higher than other bags in 4 wells and lower in 3; no clear session effect |
| Secondary T2 Ca (Ba-partialled) | 0.12 (10/11), p 0.003 |
| Pre-Tertiary (descriptive, own normalisation) | 0.51 (9/10) |
| Downstream GR labels (exploratory, 5 wells inside S) | predicted-T1 AUC 0.48-0.77; v2 E2 is better in 4/5. Local AUC 0.40-0.87 |

## Reviewer round-16 checks (52b_v7_reviewer_checks.py, committed before running)
| check | result |
|---|---|
| Colour only: L* mean (1 feature), same LOWO and high-pass | 0.14 (9/11), p 0.009 |
| Colour only: mean L*a*b* (3 features) | **0.24 (11/11)**, p 0.0005. R-D beats it, paired p 0.016 |
| R-D partial on high-passed mean L*a*b* (my addition) | 0.26 (10/11), p 0.0015: the embedding carries information beyond mean colour |
| Primary above 950 m (7 wells, 359 bags) | 0.53 (7/7) |
| Primary below 950 m (11 wells, 1,662 bags) | 0.32 (11/11): not confined to the glacial top-hole section |
| Primary on S minus the v3 shallow-test bags (1,152 bags, 8 wells with >= 30) | 0.46 (8/8), p 0.004: not recycled v3 evidence |

## Reading (agreed wording, reviewer round 16)
In wells not used for training, ResNet-50 embeddings of cuttings photographs
predict the local (within +/-50 m) variation of the Si/Al ratio measured on
the same bag.
- Median per-well rho is +0.32, positive in 11/11 wells, and +0.33 after
  partialling barite, carbonate and chloride.
- Si/Al here contrasts detrital quartz and biogenic silica with clay, so this
  is chemical skill, not sand detection.
- Mean photo colour alone reaches 0.24 (brightness L* alone 0.14). The
  embeddings add modestly to it (partial on colour 0.26; paired p 0.016).
- The skill is not confined to the glacial section: 0.53 above 950 m
  (7 wells, 359 bags) and 0.32 below (11/11, 1,662 bags).
- Photos also predict barite content (0.31). Bentonite Al cannot be
  partialled out, so part of the skill may come from mud residue.
- One well (34/8-3) shows no Si/Al skill.
- The analysis was fully pre-specified, but it is exploratory because these
  wells were used in earlier rounds.

Further notes:
- **Scale:** bag scale (a bag integrates 3-10 m), not bed scale.
- **Relation to v3:** this builds on v3's shallow XRF test (D1 0.25), the
  first sign. Without the ~870 overlapping bags, rho is 0.46 (8 of the 8
  wells that keep >= 30 bags).
- **Lag asymmetry:** lag +1 is 0.13 and lag -1 is 0.06. That is what
  downhole mixing predicts (cavings and lag carry material from bag k's
  level into the deeper bag, never upward), consistent with v3b. A one-bag
  depth mislabel would move the peak; it does not move.
- **Zn+Pb control:** stays pre-declared ambiguous, consistent with photos
  seeing mud residue.
- **GR labels:** predicted Si/Al is not a better GR sand/clay classifier
  than v2. Bag mixture and formation-at-a-point measure different things.

---

# v7 step 2: glauconite-pellet blob detector on native-resolution photos

Run 2026-11-10. Plan: V7_PLAN.md step 2 (A1-A14 with the A15 amendments).
Scripts 53 (detector) and 53b (evaluation) were committed before any run on
G-labelled bags. Score files were committed with their hashes before the join
to G. The evaluation was run once, as frozen.

- Lunde calibration: 1,022 photos, sha256 c9f9f9a9...afdfe6 (commit 1c9de5d).
- G set: 873 photos, 0 errors, sha256 85b7f327...9b9a69 (commit 28e022c).
- Evaluation outputs: results/v7/step2_results.json, step2_eval_log.txt,
  g_scores_joined.csv (commit 96a697e).

## Outcome: the pre-registered criterion is NOT met
Criterion = (a) AND (c). (a) passes; (c) fails.

| part | result | verdict |
|---|---|---|
| (a) Primary: within +/-80 m of THGU, rank(S) residualised on [1, d, \|d\|], Q = mean within-well AUC for G > 0.2, residual-shift null | Q 0.741, p 0.0003 (5 wells, 22 positives of 88 bags) | pass |
| (c) Lista false positives at the LOWO 50%-interval-recall threshold | 28/125 = 22.4% (limit 5%) | **fail** |
| (b) S beats the green index GI per well (descriptive) | 3/5 wells | not shown |

No wording was pre-declared for "(a) passes, (c) fails". A12 said "all of
these, else 'photos add nothing to position for glauconite'", but (a) passed,
so that sentence would be wrong too. Wording agreed with the reviewer
(round 18):

> Within 80 m of the top Hordaland unconformity, a native-resolution
> dark-olive-green pixel score co-locates with the XRF glauconite bags after
> a piecewise-linear trend in distance from the unconformity is removed
> (Q 0.74, p < 0.001, 5 wells, about 6 intervals). Distance from the
> unconformity alone ranks the same bags as well or better in 4 of 5 wells;
> only in 34/8-3 A does the score follow glauconite away from the
> unconformity. The score is not specific: it flags 22% of Lista Fm bags at
> the same threshold, and it does not beat the old green index (Q 0.70). Its
> shape gates add nothing (score against colour-gate pixel fraction,
> rho 0.99). The pre-registered criterion is not met; this is not a
> glauconite detector.

The A13 learned model (ResNet crops) was NOT run, as fixed in A15.

## Primary and sensitivities (per-well residualised AUC)

| test | Q | p | 34/4-6 | 34/7-10 | 34/7-4 | 34/7-9 | 34/8-3 A |
|---|---|---|---|---|---|---|---|
| PRIMARY S, [1, d, \|d\|], residual-shift null | 0.741 | 0.0003 | 0.92 | 0.56 | 0.81 | 0.56 | 0.86 |
| Secondary S, [1, d] | 0.842 | 0.0001 | 1.00 | 0.69 | 0.96 | 0.75 | 0.81 |
| Original null (shift S) | 0.741 | 0.0001 | | | | | |
| GI comparator, [1, d, \|d\|] | 0.705 | 0.0002 | 0.95 | 0.69 | 0.73 | 0.36 | 0.79 |
| S_area | 0.711 | 0.0002 | 0.92 | 0.53 | 0.77 | 0.53 | 0.81 |
| Pixel L* upper 45 | 0.723 | 0.0002 | 0.92 | 0.55 | 0.77 | 0.58 | 0.79 |
| Pixel L* upper 55 | 0.744 | 0.0001 | 0.92 | 0.56 | 0.88 | 0.56 | 0.79 |
| Hole filling off | 0.728 | 0.0001 | 0.95 | 0.49 | 0.81 | 0.58 | 0.81 |
| G > 0.15 (28 positives) | 0.715 | 0.0001 | 0.92 | 0.56 | 0.72 | 0.56 | 0.81 |
| G > 0.3 (12 positives, 4 wells) | 0.691 | 0.015 | 0.92 | 0.46 | 0.57 | n/a | 0.81 |
| Window +/-120 m (132 bags) | 0.794 | 0.0001 | 1.00 | 0.59 | 0.98 | 0.62 | 0.79 |

- The primary is carried by three wells (34/4-6, 34/7-4, 34/8-3 A). In
  34/7-10 and 34/7-9 the residualised AUC is 0.56, i.e. near chance.
- Raw AUC per well (S / GI / distance alone): 34/4-6 1.00 / 1.00 / 0.95;
  34/7-10 0.62 / 0.75 / 0.85; 34/7-4 1.00 / 0.96 / 1.00; 34/7-9 0.81 / 0.78 /
  0.94; 34/8-3 A 0.78 / 0.77 / 0.41. Distance alone equals or beats the photo
  score in 4 of 5 wells; only in 34/8-3 A does the photo clearly add.
- **How strong is p = 0.0003?** It is valid by the pre-registered statistic,
  but each well has only 12-13 possible shifts. Shifts scoring at or above
  the observed AUC: 34/4-6 0 of 13, 34/7-10 4 of 13, 34/7-4 1 of 12, 34/7-9
  5 of 12, 34/8-3 A 0 of 13. A rank-only (Fisher) combination of those
  per-well p-values gives about 0.06 (reviewer's arithmetic). Report as:
  "p < 0.001 by the pre-registered statistic; carried by three wells; a
  rank-only combination gives about 0.06."
- **What the null tests.** S and G both peak at the THGU greensand, so the
  shift null tests co-location within the window, not independence from
  position.
- Spearman of S against continuous G in the window: 0.11, -0.08, 0.73, 0.34,
  0.63 (same well order).
- The gate sensitivities barely move Q (0.71-0.74), so the result does not
  hang on one gate value.

## Lista (specificity)

| | S | GI |
|---|---|---|
| FP at the LOWO 50%-interval-recall threshold | 28/125 = 22.4% | 35/125 = 28.0% |
| FP at the Lunde p99 threshold | 73/125 (tau_L 16.47) | 32/125 (0.018) |
| Interval recall at the Lunde p99 threshold | 4/6 | 3/6 |

- Lista false positives by well: 34/8-3 18/30, 34/8-3 A 8/34, 34/4-6 1/8,
  34/7-10 1/8, 34/7-4 0/24, 34/7-6 0/8, 34/7-9 0/13. So 26 of the 28 are in
  the two 34/8 wells.
- Median S by window: Lista 18.7, Utsira 2.5, Oligocene 0.17, other 6.7,
  against a Lunde median of 0.98. Lista as a whole scores above the Lunde p99.
- Other negative rows: Balder Fm 1/34 above tau_L (median 3.1, max 20.4);
  Oligocene more than 60 m below THGU with G < 0.05: 0/90 (median 0.11).
- Six positive intervals (interval maximum S): 187.4, 41.5, 29.9, 8.9,
  119.5, 3.3. Five of six contain a bag in the well's top 20% of S; the
  deeper 34/8-3 A interval (1190-1240 m) does not.

## Out-of-window positives (descriptive)
Five bags with G > 0.2 lie 147-692 m above THGU. Their within-well S
percentiles are 34, 68, 31, 28 (34/7-4 at 840, 900, 920, 1040 m) and 43
(34/7-9 at 480 m). The detector does not flag them. The geochemist's reading
(exploratory, below) is that these are artefacts of the index, which is
consistent with the detector not flagging them.

## Label-free observations
- Median S per well in the G set is 2.7-8.8, well above the Lunde median
  (0.98) and with strong well-to-well differences in the Lunde set itself
  (0.00 to 2.77). Absolute S is not comparable between wells or formations.
- S_brown (hue 40-95 deg, a* > 0) has per-well medians of 139-312, i.e. brown
  rounded blobs are 30-60 times more common than green ones everywhere. The
  shape gates alone select ordinary rounded cuttings chips.
- Run time was about 25 s per photo per worker with 4 workers (plan A14
  estimated 3.6 s): the detector is far slower than specified.

## Exploratory, post hoc (after unsealing; none of this changes the outcome)
Checked by the reviewer and reproduced by me on g_scores_joined.csv.
- **S is the colour-gate pixel fraction, not a pellet count.** Spearman of S
  against gate_frac is 0.99 pooled and 0.95-1.00 within Lista in every well.
  gate_frac alone gives Q 0.737. The shape gates add nothing.
- **The accepted blobs are olive, not green.** 93% of accepted blobs in the
  window positives and 99.8% in Lista fall in hue 95-120 deg, the margin
  added for the warm colour cast. 81-87% are in the smallest size bin
  (0.10-0.17 mm).
- **Sensitivity is poor too.** 12 of the 22 window positives score below the
  Lunde p99 (16.5). All three in 34/7-9 score 0.5, 2.6 and 8.9; the deeper
  34/8-3 A interval scores 0.5-3.3.
- **Blobs with hue >= 120 deg only** (from counts already in the committed
  score file; chosen after seeing the hue shares): Lista false positives
  0/125 (Lista maximum 1.3), Q 0.687, p 0.0007, per-well residual AUC 1.00,
  0.44, 0.92, 0.36, 0.71. Only 2 of 6 intervals stand out. So the 95 deg
  lower hue bound is what let Lista in; true-green blobs are specific but too
  rare to detect most glauconitic bags. Not a rescue; no further tuning.
- **Geochemistry of the Lista false positives** (geochemist,
  results/v7/agent2_step2_results_notes.md): flagged and unflagged Lista bags
  in the 34/8 wells do not differ chemically (K/Al, Fe/Al, G, Si/Al;
  Mann-Whitney p 0.09-0.89), and Lista G is about 0 (maximum 0.12). Within
  the 34/8 Lista, S against the photo's median a* is -0.96 and -0.92. The
  detector is counting green claystone, not glaucony.
- **Out-of-window positives:** K/Al 0.36-0.44 and Fe/Al 0.71-1.02, ordinary
  mudstone values, three of four with Cl of 35,000-114,000 ppm. They are
  probably artefacts of the index, so G > 0.2 is a sound label only inside
  the Hordaland/Utsira window.
- **Hypotheses only, not shown:** barite coating masks the green in heavily
  weighted bags (one p of 0.04 among several tests); the 34/8-3 Lista is
  either genuinely greener clay or rendered greener by that well's photo
  processing (XRF cannot separate the two).

## Reading (reviewer round 18: ACCEPT WITH CHANGES, applied; step 2 CLOSED)
1. Within the window, a dark-olive-green pixel score co-locates with the
   G > 0.2 bags after a piecewise-linear trend in distance is removed
   (p < 0.001 by the pre-registered statistic, carried by three wells; about
   0.06 by a rank-only combination). Distance from the unconformity alone
   does as well or better in 4 of 5 wells.
2. It is not a glauconite detector. One in five Lista bags passes the same
   threshold, nearly all in the 34/8 area, and Lista's median score is above
   that of the Utsira bags.
3. It does not improve on the old green index (Q 0.74 against 0.70; 3/5
   wells), which v6 already showed to be non-specific.
4. This gate set did not separate glauconite pellets from other green
   material; its hue margin admitted olive claystone. XRF K+Fe remains the
   usable glauconite indicator. The v6 conclusion stands.
5. Run time was about 7 times the estimate (note only).

---

# v7 step 3: the mud-log "cuttings lithology %" column as a wellsite label

Run 2026-11-10/11. Plan: V7_PLAN.md step 3 (v3; reviewer rounds 19 and 19b
and the wellsite geologist's protocol check applied). Order of commits:
plan, reader rules, reader folders and seeded selections, raw readings,
agreement script, first agreement result, second-pass rule, second
agreement result, eligibility and set of record, chemistry check, test
script, photograph tests. Nothing was joined to XRF or photographs before
the labels and the set of record were committed.

## Outcome in one paragraph
The pre-registered primary test passes, but only just, and it is a small
effect. In wells it never saw, the step-1 model (taught only Si/Al
chemistry, frozen before these labels existed) follows the local (within
+/-50 m) variation of the sand fraction the wellsite geologist logged:
median per-well rho +0.125, positive in 5 of 6 wells, p 0.047. Measured
Si/Al itself reaches only 0.18 against the same label, and mean photo colour
alone does as well as the photo models (0.15). So the photographs agree
with the wellsite sand estimate about as well as chemistry does, which is
weakly, and not beyond what colour gives.

## Label construction
- **Sheets:** 8 wells, 300 tiles of 40 m from the first logged sample to
  40 m below top Shetland.
- **Depth (gate G1):** the 10 m grid lines were followed from one printed
  label per sheet; every printed 100 m label in the digitised range sits on
  its calibrated line (checked by eye on contact sheets at about 0.6 of
  native resolution; results/v7/step3/G1_labels.csv). Four labels were faded
  or out of frame; their lines are on the grid.
- **Reading:** reader A (stronger model) read all 300 tiles; reader B
  (a different, cheaper model) read a seeded 30 % plus 17 symbol-audit
  tiles (100 tiles). Readers saw only tiles, the sheet legend and the rules.
- **Format fix, disclosed:** one batch of 18 tiles gave depths counted from
  the tile top; they were shifted to absolute depth by script.

## Gate G2: reader agreement (bag-interval level)

| check | limit | first pass (A vs B, 481 intervals) | second pass (24/9-3 re-read, 470 intervals) |
|---|---|---|---|
| Pooled Spearman of sand % | >= 0.80 | 0.890 | 0.955 |
| Share differing by > 20 points | <= 15 % | 2.5 % | 0 % |
| Mean signed difference | within +/-5 | -1.9 | -0.1 |
| Sand presence, both ways | >= 80 % | 100 % and 87 % | 100 % and 100 % |
| Informative intervals: number | >= 30 | 163 | 145 |
| Informative: mean absolute difference | <= 10 | 6.6 | 0.9 |
| Informative: Spearman | >= 0.60 | **0.596 (fail)** | 0.974 |
| No well below its limit | | pass | pass |
| **G2** | | **FAIL** | **PASS** |

- **First pass failed one gate by 0.004.** The whole disagreement was one
  tile of 24/9-3 (2360-2400 m): reader A called a dotted pattern silty clay
  (0 % sand), reader B called it sand (75 %). The other seven wells agreed
  almost exactly (mean absolute difference 0 to 0.35 points; without 24/9-3
  the informative Spearman is 0.999).
- **The pre-declared one fix was used.** The rule for 24/9-3 was clarified
  from the legend (cells holding only dots are sand), reader C re-read all
  69 tiles of that well and reader D a fresh 30 % (21 tiles reader B had not
  read). The second-pass rule was committed before C and D reported. C
  against D on 24/9-3: Spearman 0.94, mean absolute difference 1.0. Reader C
  is the reader of record for 24/9-3.
- **What G2 does not show.** On 24/9-3 the two readers still disagree on
  clay against carbonate (44 intervals where C reads clay and D reads
  bricks). The sand fraction is not affected, but a carbonate label from
  this sheet would not be reliable.
- **Symbol audit:** no confusion of sand with silt, glauconite or tuff on
  the audit tiles (class presence agreed in 29 silt, 17 glauconite and 12
  tuff intervals, none one-sided). There is no human key, so accuracy, as
  opposed to agreement, rests on G3.
- **Reader A's seams:** in 23 % of tile seams the sand % changes by 10
  points or more. Real sample steps often fall on 10 m multiples, so this is
  an upper bound on reader inconsistency, not a measure of it.

## Eligibility and set of record (labels only, committed before G3)

| well | bags in S | informative bags | depth clusters | mean sand | eligible |
|---|---|---|---|---|---|
| 24/9-3 | 478 | 212 | 7 | 27 % | yes |
| 34/4-6 | 120 | 35 | 7 | 12 % | yes |
| 34/4-7 | 113 | 26 | 7 | 5 % | yes |
| 34/7-10 | 142 | 30 | 5 | 4 % | yes |
| 34/7-4 | 144 | 29 | 6 | 7 % | yes |
| 34/7-9 | 129 | 19 | 7 | 6 % | yes |
| 34/8-3 | 100 | 6 | 1 | 1 % | no (no label variance) |
| 34/8-3 A | 146 | 12 | 3 | 4 % | no (12 informative bags) |

Six wells are eligible, so the Tertiary set S (1,372 bags) is the test of
record and the pre-Tertiary was not digitised. With six wells the smallest
possible p is 0.016.

## Gate G3: the label against measured Si/Al (no photographs)
Per-well high-passed Spearman: 24/9-3 +0.37, 34/7-4 +0.31, 34/7-9 +0.23,
34/7-10 +0.13, 34/4-7 +0.05, 34/4-6 -0.09. Median +0.18 (5/6 positive). Not
stopped; just above the 0.15 line below which a failed photo test would
have been called uninformative. The wellsite sand fraction and bag
chemistry agree only weakly at bag scale.

## Photograph tests (run once)

| test | median rho | wells > 0 | p | 95 % CI of median | pair concordance |
|---|---|---|---|---|---|
| **P2 PRIMARY: step-1 Si/Al model, no retraining** | **+0.125** | **5/6** | **0.047** | -0.03 to +0.27 | 0.68 (5/6), p 0.031 |
| P2 with the 15 engineered features | +0.114 | 5/6 | 0.047 | -0.01 to +0.20 | 0.63 |
| P2 from the leave-one-area-out model | +0.134 | 4/6 | 0.078 | -0.03 to +0.26 | 0.71 |
| Reference: measured Si/Al | +0.177 | 5/6 | 0.047 | -0.02 to +0.34 | 0.69 (6/6) |
| P1: R-D retrained on the label, LOWO | +0.135 | 5/6 | 0.031 | +0.04 to +0.22 | 0.66 (6/6) |
| P1 with equal well weights | +0.130 | 6/6 | 0.016 | +0.04 to +0.25 | 0.65 |
| P1 leave-one-area-out | +0.160 | 5/6 | 0.031 | +0.04 to +0.24 | 0.65 |
| R-E retrained on the label | +0.131 | 5/6 | 0.031 | +0.02 to +0.23 | 0.70 |
| **Colour only (mean L\*a\*b\*) retrained on the label** | **+0.153** | 5/6 | 0.078 | -0.06 to +0.23 | 0.69 |
| Baseline: relative depth | +0.063 | 5/6 | 0.16 | | |
| Baseline: bag dry weight | -0.073 | 0/6 | 1.0 | | |

- **Criterion met:** p < 0.05 and median >= 0.10. It is a marginal pass: the
  bootstrap interval of the median includes zero.
- **Per well, P2 follows the chemistry reference:** 24/9-3 +0.35 (reference
  +0.37), 34/7-9 +0.19 (+0.23), 34/7-4 +0.17 (+0.31), 34/7-10 +0.08
  (+0.13), 34/4-7 0.00 (+0.05), 34/4-6 -0.06 (-0.09). The photographs agree
  with the mud log where chemistry does and fail where chemistry fails. The
  median ratio is 0.66.
- **Not beyond colour.** Mean colour alone, fitted on the label, gives
  +0.153. Neither P1 nor P2 beats it (paired p 0.50 and 0.42).
- **Fragile to single wells (exploratory).** Leaving out 24/9-3, 34/7-4 or
  34/7-9 drops the median to +0.08, below the 0.10 floor; leaving out any of
  the other three raises it to +0.17.
- **Circular-shift null per well:** p 0.005 (24/9-3), 0.005 (34/7-4), 0.045
  (34/7-9), 0.24 (34/7-10), 0.64 (34/4-7), 0.78 (34/4-6). Three wells carry
  the result.
- **Lag profile (median):** lag -1 0.06, lag 0 0.125, lag +1 0.13, against a
  no-skill value of 0.03 at +/-1. The photograph agrees with the label of
  the next bag down as well as with its own. That is what a one-sample lag
  between logged depth and bag depth, or downhole mixing, would give.
- **Label sensitivities of P2:** with glauconite added to sand +0.141; sand
  plus silt +0.133; faded blocks included +0.125; label shifted one bag
  either way +0.11 and +0.05.

## C8 (exploratory, declared before reading): the mud log's own glauconite
- Only 34/8-3 A has 10 or more bags with a glauconite fill (15): Spearman of
  glauconite % against the XRF index G is +0.52; median G is 0.23 where the
  mud log draws glauconite and -0.07 elsewhere; the step-2 photo score is
  unrelated (+0.03).
- Pooled over the six wells with both (786 bags): where the mud log draws a
  glauconite fill, 17 of 24 bags have G > 0.2; where it does not, 9 of 762.
- All five G > 0.2 bags of 34/7-10 and all nine of 34/8-3 A carry a
  mud-log glauconite fill; the three of 34/4-6 and four of the six in
  34/7-4 do not (the out-of-window 34/7-4 bags among them).
- Reading: a wellsite geologist in 1984-88 and the XRF index, made
  independently, point at the same bags. This supports the v6 index as a
  glauconite label near the unconformity. It does nothing for the step-2
  photo score.

## Reading (draft, pending reviewer round 20)
1. Wellsite sand fractions can be recovered from old mud logs with high
   reader agreement on seven sheets, and on the eighth after one clarified
   rule.
2. The pre-registered wording applies, with its limits: "a model taught only
   chemistry, in wells it never saw, follows the local (within +/-50 m)
   variation of the sand fraction that the wellsite geologist estimated by
   eye on the same cuttings; agreement with a wellsite estimate, not ground
   truth; exploratory but fully pre-specified".
3. The effect is small (+0.125), marginal (p 0.047, six wells), carried by
   three wells, and no larger than what mean colour gives. It is about
   two-thirds of what measured chemistry achieves against the same label.
4. The weak link is the label, not only the photograph: chemistry itself
   agrees with the wellsite sand fraction at only +0.18. A 10 % estimate by
   eye per 5-10 m sample, with cavings and a possible one-sample lag, is a
   noisy bag-scale reference.
5. Not a sand detector, and not bed scale.
