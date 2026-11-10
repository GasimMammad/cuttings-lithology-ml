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
so that sentence would be wrong too. Proposed wording (for the reviewer):

> Within 80 m of the top Hordaland unconformity, the pellet-blob score ranks
> the glauconitic bags above their neighbours beyond what depth position
> explains (Q 0.74, p 0.0003, 5 wells). It is not specific to glauconite: it
> fires on 22% of Lista Fm bags at the same threshold, and it is not shown to
> beat the simple green index (Q 0.70). It is a "green rounded grain" score,
> not a glauconite detector.

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
  0.94; 34/8-3 A 0.78 / 0.77 / 0.41. Depth position alone beats the photo
  score in 3 of 5 wells; only in 34/8-3 A does the photo clearly add.
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
(34/7-9 at 480 m). The detector does not flag them. Either these G values are
not pellet glauconite, or the pellets fall in the accepted-loss classes.

## Label-free observations
- Median S per well in the G set is 2.7-8.8, well above the Lunde median
  (0.98) and with strong well-to-well differences in the Lunde set itself
  (0.00 to 2.77). Absolute S is not comparable between wells or formations.
- S_brown (hue 40-95 deg, a* > 0) has per-well medians of 139-312, i.e. brown
  rounded blobs are 30-60 times more common than green ones everywhere. The
  shape gates alone select ordinary rounded cuttings chips.
- Run time was about 25 s per photo per worker with 4 workers (plan A14
  estimated 3.6 s): the detector is far slower than specified.

## Reading (draft, pending reviewer round 18)
1. A hand-built colour-and-shape detector sees something real at the
   unconformity: within the window it ranks the G > 0.2 bags higher than
   depth alone would (p 0.0003), and this survives every gate sensitivity.
2. It is not a glauconite detector. One in five Lista bags passes the same
   threshold, nearly all in the 34/8 area, and Lista's median score is above
   that of the Utsira bags.
3. It does not clearly improve on the old green index (Q 0.74 against 0.70;
   3/5 wells), which v6 already showed to be a non-specific green index.
4. So the v6 conclusion stands: photographs carry a green-grain signal that
   co-occurs with XRF glauconite near THGU, but colour and shape at 7 um/px
   do not separate glauconite pellets from other green material (green
   claystone chips, chlorite, tuff alteration). XRF K+Fe remains the usable
   glauconite indicator.
