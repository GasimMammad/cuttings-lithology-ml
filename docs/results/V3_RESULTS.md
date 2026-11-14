# v3 results (2026-11-05)

Review (by AI, not an independent human review; see Use of AI in the README):
3 rounds; its objections and the changes they caused are in
V3_PLAN.md section 1 and below. Features file used: `28_features.csv`, sha256
prefix d546d8befbccd4b7, 80,608 tiles.

## Headline (agreed with the review)

Photographs of archived cuttings from ten Norwegian North Sea wells carry a
sand-clay signal that transfers to wells the model never saw (pre-registered
v2: median held-out AUC 0.73, 6/7 wells, p = 0.04). It works at **interval
scale**:

- The primary model shows no demonstrated bed-scale skill (local AUC over
  sand-clay pairs < 50 m apart: 3/6 wells).
- It does not significantly beat relative depth within the well (paired
  p = 0.15).
- Within the labelled zones, the bag's dry weight does about as well; photos
  add +0.03 to +0.05 AUC over weight, none significant.

In the unlabelled shallow overburden, a pre-registered single image feature
(clear-grain size) agrees with cuttings XRF Si/Al of the same bags in 7/10
wells (median rho +0.11, p = 0.014). An ImageNet-embedding model agrees more
strongly (median rho +0.25). It separates gravelly-sandy glacial diamicton
from clay, but it also fires on bright carbonate or cement.

Photographs are a usable interval-scale indicator of how coarse and clay-poor
the cuttings are, not yet a sinkite (bed-scale sand) detector.

## Numbers

### Labelled zones, 7 eligible held-out wells (34_v3_baselines.py)

| signal | median AUC | wells > 0.5 | vs relative depth | local AUC < 50 m, wells > 0.5 |
|---|---|---|---|---|
| E2 (v2 primary) | 0.73 | 6/7 | p = 0.148 | 3/6 |
| D1 ResNet-50 | 0.73 | 7/7 | p = 0.039 | 5/6 |
| clear-grain size (1 feature, chosen in fold) | 0.84 | 6/7 | p = 0.039 | 5/6 |
| XRF Si/Al (reference) | 0.81 | 6/7 | p = 0.078 | 5/6 |
| bag dry weight (exploratory) | 0.84 | 6/7 | - | 6/6 |
| relative depth (fair sign) | 0.57 | 6/7 | - | 1/6 |

### Unlabelled Tertiary overburden vs XRF Si/Al (35_v3_xrf_shallow.py, pre-registered)

| signal | run 1 (flawed) | run 2 (corrected) |
|---|---|---|
| clear-grain size (primary) | +0.09, 7/10, p = 0.080 | **+0.11, 7/10, p = 0.014** |
| D1 ResNet-50 | +0.25, 7/10, p = 0.019 | +0.25, 7/10, p = 0.019 |
| E2 | +0.13, 5/10, p = 0.116 | +0.13, 5/10, p = 0.116 |

- **Run 1 flaw:** in run 1 the 247 test depths of 34/8-3 and 34/8-3 A had
  engineered features from one tile, not 16, because feature extraction was
  stopped early.
- **How run 2 was done:** the review specified the remedy (compute the
  missing tiles, rerun the committed script unchanged) before run 2 existed.
  Run 1 was committed first (c7b7fc2), and the script is unchanged since then.
- **Audit bias:** the flaw was found during review of a null result. Only
  34/8-3 and 34/8-3 A changed between runs, and both have no GR sand in the
  Tertiary.
- **Robustness:** dropping the strongest well (34/7-10) still gives p ≈ 0.027.

### Above the 20" shoe (exploratory, post hoc)

| well | rho(bag weight, Si/Al) | rho(D1, Si/Al) |
|---|---|---|
| 34/7-9 | -0.59 | +0.66 |
| 34/7-10 | -0.11 | +0.51 |
| 34/4-7 | -0.24 | +0.29 |
| 34/7-4 | -0.39 | +0.40 |
| 34/7-1 | -0.22 | n/a |

Bag weight reverses sign between sections, which makes it a processing
artefact. The image signal does not reverse.

### What D1 sees (38_v3_montage.py)

- **High scores:** polymict sandy-gravelly material with free rounded quartz,
  crystalline and dark erratics, red clasts and shells. This is glacial
  diamicton.
- **Low scores:** homogeneous olive-brown soft claystone aggregates, probably
  balled by the bit.
- **False positives:** shoe-track cement at 34/7-10 430 m, 7 m below the 30"
  shoe (D1 0.99, Ca/Al 8.4 against 0.4-1.0 in its neighbours), and large
  shells. The cream clasts in 34/7-4 at 500 and 570 m are NOT carbonate
  (Ca/Al 0.4-0.6). 24/9-3 at 510 m next to the 20" shoe (Ca/Al 13) matches
  the surrounding shelly Utsira/Pliocene sand (Ca/Al 6-21), so it is a true
  sand, not cement (41_v3_shoe_cement_check.py).
- **34/4-7:** the ranking is among diamicts, not sand against clay.
- **Consequence:** for sinkite work in the glacial section, tills and bright
  carbonate or cement will be the main false-positive classes.

## v3b: what each cuttings bag represents (V3_PLAN.md sections 4 and 4b)

Six wells with 10 m bags (34/4-6, 34/4-7, 34/7-4, 34/7-6, 34/7-9, 34/7-10);
all series high-passed over +/-50 m; scripts 39 and 40.

### Chemistry, no images

XRF Si/Al of the same bags agrees better with GR averaged over the 10 m
interval ending at the nominal depth than with GR at that depth (mean rho
0.18 vs 0.11). Per well, the pre-specified bottom window beats the point in
4/6: strongly in 34/7-10 (0.03 -> 0.43) and 34/7-4 (0.37 -> 0.51), but it is
worse in 34/7-6 and 34/7-9. Offsets from about -5 to +4 m cannot be told
apart; the best of the 124 windows tried, (D-12, D+3], carries a winner's
curse. This supports bottom-of-interval labelling for future wells, but it
cannot resolve a few metres of smear or depth-tie error. Chemistry-GR
agreement at bed scale is itself weak and uneven. In 34/7-6 it is negative
at every support.

### Images

The pre-registered criterion ("interval clearly wins": p < 0.05 and >= 5/6
wells) was NOT met.

| signal | median rho shift, point -> interval | wells improving | p |
|---|---|---|---|
| clear-grain size (primary) | +0.05 | 4/6 | 0.22 |
| D1 | +0.05 | 4/6 | 0.11 |
| E2 | +0.06 | 4/6 | 0.078 |
| bag weight (exploratory) | +0.14 | 6/6 | 0.016 (smallest possible with 6 wells) |

The more important number is the level, not the shift. After
high-passing, the interval rho is -0.18 to +0.44 for the primary and -0.17 to
+0.18 for D1, near zero or negative in about half the wells. This is a
continuous-measure confirmation that the photographs have no reliable
bed-scale skill. No retraining on interval labels (decided by the
pre-registered rule).

## Caveats for any slide

- 7 test wells, 5 Tertiary. p = 0.031 is the smallest p-value 5 wells can
  give.
- 1-3 sand beds per Tertiary well; 59% of all sand depths are in 24/9-3.
- With training labels shuffled within wells, AUC is already about 0.64.
- Labels are a linear GR index on a ±3 m window, while a cuttings bag spans
  ~10 m.
- v3 is exploratory: the test wells had been seen.
- The Si/Al reference itself fails in 34/7-6 (AUC 0.41): the cuttings there
  do not record the GR sand.
- 34/7-1 is not blind; it was a v1 hold-out fold. Its mud-log test was not
  run.
- v2's original depth-only baseline (sign from pooled wells, 0/7) was too
  weak. With a fair sign rule, relative depth reaches 0.57.

## Not done

- Soft labels with bag-interval targets (pre-registered rule said no; see v3b).
- 34/7-1 mud-log digitisation, which needs two independent digitisers.
- Fine-tuned CNN.
- Masking cement and chalk with Ca/Al.
