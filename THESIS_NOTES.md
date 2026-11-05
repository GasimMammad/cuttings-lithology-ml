# Thesis notes: ML chapter (v2-v4 follow-up)

Material the reviewer (round 9) asked to have in one place before writing.
Numbers are taken from the committed result files named in section 4.

## 1. Consolidated results

**PR** = pre-registered before computation (plan committed first).
**EX** = exploratory / post hoc.
Test wells: the 7 with >= 3 sand and >= 3 clay GR-labelled depths, unless
stated otherwise.

### 1a. Held-out sand vs clay (GR labels)

| signal | status | median AUC | wells > 0.5 | vs relative depth | local AUC (< 50 m) wells > 0.5 |
|---|---|---|---|---|---|
| E2, engineered + per-well z (v2 primary) | PR | 0.73 | 6/7, p 0.039 | p 0.148 (EX) | 3/6 (EX) |
| E1, v1 recipe on v2 labels | PR (secondary) | 0.75 | 5/7, p 0.039 | - | - |
| D1, ResNet-50 frozen | PR (secondary) | 0.73 | 7/7, p 0.008 | p 0.039 (EX) | 5/6 (EX) |
| one feature, clear-grain size (chosen in fold) | EX | 0.84 | 6/7 | p 0.039 | 5/6 |
| C1 / C2, fine-tuned CNN | EX | 0.71 / 0.70 | 7/7 | p 0.055 / 0.023 | 3/6 / 5/6 |
| relative depth within well (baseline) | EX | 0.57 | 6/7 | - | 1/6 |
| bag dry weight (baseline) | EX | 0.84 | 6/7 | - | 6/6 |
| XRF Si/Al (reference) | EX | 0.81 | 6/7 | p 0.078 | 5/6 |

- Tertiary-only, E2 (PR secondary): 5/5 wells, p 0.031 (the minimum
  attainable with 5 wells).
- Permutation null for E2: mean AUC 0.64; observed 0.716, p 0.035 (PR).
- Photos added to bag weight: +0.03 to +0.05 AUC, not significant (EX).

### 1b. Unlabelled shallow overburden vs cuttings XRF Si/Al (high-passed +/-50 m)

| signal | status | median rho | wells > 0 | p |
|---|---|---|---|---|
| one feature (primary) | PR, run 2 | +0.11 | 7/10 | 0.014 |
| same, run 1 (single-tile flaw) | PR, run 1 | +0.09 | 7/10 | 0.080 |
| same, cement mask | robustness | +0.12 | 7/10 | 0.024 |
| D1 | PR (secondary) | +0.25 | 7/10 | 0.019 |
| E2 | PR (secondary) | +0.13 | 5/10 | 0.116 |

### 1c. Bag-interval support (v3b, six 10 m wells)

| test | status | result |
|---|---|---|
| XRF: 10 m bottom window vs point GR | PR control | rho 0.18 vs 0.11; 4/6 wells |
| images: interval minus point | PR | +0.05; 4/6; p 0.22 (primary). Criterion NOT met |
| bed-scale level after high-pass | PR | image rho -0.18 to +0.44 |

### 1d. Core and plug references (v4)

| test | status | result |
|---|---|---|
| core digitisation, 34/4-6 | pilot | AI-AI SAND kappa 0.98 |
| core digitisation, 34/7-10 | pilot, PR gate | AI-AI SAND kappa 0.50 < 0.6: STOPPED |
| plugs, 34/8-3 2839-2897 m | PR, descriptive | gate +0.48 (marginal); photo rho +0.33 / +0.39, n 18, n.s. |

## 2. Label limitations

- **GR index, not true shale volume.** Vsh is a linear GR index; no
  Larionov or other non-linear correction. Thresholds 0.30 / 0.60.
- **Support mismatch.** Labels use point GR with a +/-3 m consistency
  window, while a cuttings bag spans the interval since the previous bag
  (~10 m in the 34/x Tertiary). Chemistry supports bottom-of-interval support
  (v3b).
- **Mineral effects.** Glauconitic and micaceous sands read shale-like GR;
  Balder tuffs read sand-like GR. Balder, Ness, Rannoch and Draupne are
  excluded, which only partly mitigates this.
- **Weak-contrast zones.** 24/9-3 zone r3_upper (anchors 19 / 35 API)
  labelled a 3 D Frigg sand "clay". Removing the zone leaves the result
  unchanged.
- **Sample representativeness.** Cuttings may not record GR sand (washed-out
  loose sand, cavings). XRF fails to separate sand in 34/7-6 (AUC 0.41).
- **Concentration.** 59% of all sand labels come from one well (24/9-3).
  Each Tertiary test well has 1-3 sand beds.

## 3. Independence of test wells

- 34/8-3 and 34/8-3 A are one location (a well and its sidetrack). Both
  results are Jurassic.
- 34/7-4, 34/7-6, 34/7-9, 34/7-10 and 34/7-1 are clustered on the Tampen
  Spur, and 24/9-3 and 24/9-4 are neighbours. The effective number of
  independent sites is smaller than the well count.
- Leave-one-well-out does not hold out geography; leave-one-area-out was not
  run.

## 4. Reproducibility

- **Code:** `~/Projects/cuttings-lithology-ml-v2`, branch `v2-ten-wells`.
- **Data:** read-only, `/Volumes/T9/GasimMammadov_MasterProject2026/Wells`.
- **Features file:** `28_features.csv` (80,608 tiles), sha256 prefix
  `d546d8befbccd4b7`.
- **Python:** 3.13; key packages torch 2.15, scikit-learn 1.9.1, lasio 0.32.

| result | commit |
|---|---|
| v2 labels and V2_PLAN (pre-registration) | acc57e0 |
| v2 results | eaa36f4 |
| v3 plan after review; baselines | 6997552 |
| shallow XRF test run 1 / run 2 | 3a32a61 / 826d31c |
| V3_RESULTS headline | 730edb6 |
| v3b plan / amendment / results | 032d5cf / 1b3baa9 / 083813c |
| V4_PLAN / cement mask | 26499b5 / 129c639 |
| digitiser protocol v2 / hard pilot fails gate | 4778dcb / 1ffc019 |
| amendment E / plug check | 3d65d27 / 644e41c |
| V4_RESULTS (corrected) | baf2951 |

## 5. AI-use statement (DRAFT for the author to adapt to University of Manchester policy)

> Generative AI (Anthropic Claude, via Claude Code) was used in this chapter as
> follows:
>
> 1. **Code.** Writing and debugging analysis code, under the author's
>    direction. All code is in the project repository, and results can be
>    reproduced from the commits listed.
> 2. **Plans.** Drafting pre-registered analysis plans, which were committed
>    before each analysis was run.
> 3. **Internal review.** A separate Claude agent, prompted to act as a
>    senior geoscientist and machine-learning reviewer, critiqued plans and
>    results over nine rounds. This was not an independent human review.
> 4. **Core digitisation.** Two Claude agents (Opus and Sonnet) digitised
>    lithology from core photographs, blind to other data. Their agreement is
>    reported, and the approach was stopped when it failed a pre-set
>    reliability gate. A blind human spot-check by the author was used to
>    assess rater bias [complete once done].
> 5. **Drafting text.** Drafting summaries, which the author checked and
>    edited.
>
> The geological interpretation, label design decisions and conclusions are
> the author's responsibility.
