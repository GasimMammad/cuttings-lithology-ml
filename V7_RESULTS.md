# v7 results: step 1, photos -> cuttings XRF chemistry (2026-11-10). DRAFT, awaiting reviewer round 16

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

## Reading (draft, for the reviewer)
- Within a well, at bag scale (after removing +/-50 m trends), cuttings
  photographs carry information about the Si/Al chemistry of the same bag,
  in wells the model never saw.
- This is the first bed-scale positive in the project. v3 found no
  bed-scale skill against GR labels; GR is a point log, not the bag.
- **34/8-3 is the exception.** There the photos track Ba and Zn+Pb rather
  than Si/Al, consistent with heavy mud residue.
- **The photos also see barite.** The Si/Al claim is conditional on the
  partial test, which passes.
- Predicted Si/Al is not a better GR sand/clay classifier than v2. The two
  measure different things: bag mixture against formation at a point.
