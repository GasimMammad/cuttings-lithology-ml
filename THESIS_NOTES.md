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
>    reliability gate. The source of the rater disagreement was
>    adjudicated blind by a panel of three further Claude agents, using plugs,
>    the operator core description and logs. This was not a human panel.
> 5. **Drafting text.** Drafting summaries, which the author checked and
>    edited.
>
> The geological interpretation, label design decisions and conclusions are
> the author's responsibility.

## 6. Methods text for the core-photo test (agreed with the reviewer agent)

Core photographs of 34/7-10 were digitised in 0.25 m bins by two AI raters
(Claude Opus and Claude Sonnet) following a written protocol. Their agreement
(SAND vs rest, kappa 0.50) failed a pre-set threshold of 0.6, so the
core-photo test was stopped. To find the source of the disagreement, a
stratified sample of 40 bins (25 disputed, 15 agreed) was adjudicated blind
to the raters by a panel of three AI agents. A label was assigned only where
two agents agreed and the call was supported at bin resolution by plugs, the
operator core description, or logs stable across the core-to-log shift
uncertainty. The consensus rules were committed before the rater labels were
unsealed; all panel agents were Claude models, the same family as rater A.

**Result sentence:** Where the panel could resolve a disputed bin, the
evidence almost always supported A's SAND call (14 of 15; p = 0.001), so
rater B under-called clean, plug-proven sandstone. A further 7 disputed bins
were siltstone or very fine sandstone with no grain-size data. If those count
as not-sand, the advantage of A is no longer significant (14 vs 8; p = 0.29),
so part of the disagreement is a class-boundary problem.

## 7. v7 and v8: chemistry and wellsite lithology from the same photographs

Sources: V7_RESULTS.md, V8_RESULTS.md and the result files they name
(results/v7/, results/v8/). **PS** = fully pre-specified (plan and code
committed before the run) but exploratory, because the same 11 wells were
used in earlier rounds. **EX** = exploratory or post hoc. Unless stated, the
statistic is the per-well Spearman correlation after removing a +/-50 m
running median, tested across wells with a one-sided Wilcoxon test; models
are trained without the test well.

### 7a. Consolidated results

| question | status | result | reading |
|---|---|---|---|
| Photo -> Si/Al of the same bag, Tertiary (v7 step 1) | PS | median +0.32; 11 of 11 wells; p 0.0005; CI 0.18 to 0.49 | **the solid result**; chemical skill at bag scale, not sand detection |
| same, with barite, carbonate and chloride partialled out | PS | +0.33 | not explained by those mud signals; bentonite cannot be excluded |
| mean colour alone | PS | +0.24 | embeddings add modestly (partial +0.26, paired p 0.016) |
| Photo -> Si/Al, pre-Tertiary | EX (descriptive) | +0.51; 9 of 10 wells | larger where the chemistry varies more |
| Photo glauconite-pellet detector (v7 step 2) | PS | criterion NOT met: 22 % false positives in Lista Fm | a green-pixel score, not a glauconite detector |
| Photo Si/Al model against the wellsite sand fraction, Tertiary, 6 wells (v7 step 3) | PS | +0.13; p 0.047; CI -0.03 to +0.27 | criterion narrowly met; no better than colour (+0.15); partial given Si/Al +0.02 |
| same with a 7th well, 24/9-4 | EX | +0.17; p 0.023 | supporting only; depends on a disclosed deviation from the plan |
| Two mud logs of one well, 34/7-9 (Exlog against Saga) | EX | Spearman +0.42 (CI 0.11 to 0.69) | the wellsite label is itself only moderately reproducible |
| Fine-tuned CNN against frozen features (X1) | EX | +0.46 against +0.33 medians; paired p 0.42 | no detectable gain from fine-tuning (11 wells, one seed) |
| Fine-tuned CNN, three seeds (v8 C) | EX | PENDING | |
| Photo -> K, Fe, Ca, Ti, Zr over Al (v8 A) | PS | +0.20, +0.28, +0.19, +0.27, +0.10; all pass | a rough chemical log; robustly two axes beyond Si and Al: Fe(-Ti) and Ca; mostly carried by colour |
| Where does it work? (v8 B) | PS | skill against spread of Si/Al: between wells +0.78 (p 0.003); within wells +0.54 (p 0.014) | skill follows the spread of the chemistry; 34/8-3 fails where Si/Al is nearly flat |
| Photo Si/Al model against the wellsite sand fraction, Jurassic-Triassic, 6 wells (v8 D) | EX (amended test; no test of record) | +0.52; 6 of 6 wells; p 0.016; twins merged +0.51, 5 of 5, p 0.031 | where sandstone is common the photo model follows the wellsite sand fraction as well as measured Si/Al does (+0.51); partial given Si/Al +0.15; colour features alone +0.47 |

### 7b. Methods text (draft)

**Chemistry from photographs.** Each cuttings bag has a photograph and a
handheld-XRF analysis. For every Tertiary bag outside 15 m below a casing
shoe (2,021 bags, 11 wells), the photograph was summarised by ImageNet
ResNet-50 embeddings, standardised within the well, reduced to 32 principal
components and regressed (ridge, alpha 1) on the within-well z-score of
log10(Si/Al). The model was fitted on ten wells and applied to the eleventh.
Because both the photographs and the chemistry drift slowly with depth, a
+/-50 m running median was removed from predicted and measured series
before the Spearman correlation was computed in each well. A claim required
a one-sided Wilcoxon p < 0.05 across wells and a median correlation of at
least 0.10; both were fixed before the run.

**Wellsite sand fraction from mud logs.** The "cuttings lithology %" column
of eight scanned mud logs (1981-1988) was cut into 40 m tiles by a script
that calibrates depth from the printed 10 m grid and adds a depth ruler and
a percentage ruler, and does nothing else. Two AI readers of different
models read the tiles following written rules taken from each sheet's
legend: one read every tile, the other a seeded sample. Agreement gates,
well eligibility and the test were fixed beforehand; photographs entered
only after the labels were committed. The label for a bag is the
length-weighted sand percentage over the interval since the previous bag.
No human key exists for these readings.

**More elements; where it works.** The same model and validation were
applied to log10 ratios of K, Fe, Ca, Ti and Zr to Al. A target was counted
only if it passed the step-1 rule with Holm correction, kept a partial
correlation given measured Si and Al, and survived a drilling-mud control
(Ba, Cl; S for Ca; Sr for Zr). To ask where the Si/Al model works, its
per-well and per-150 m-window correlation was compared with the spread
(median absolute deviation) of the measured ratio and of the prediction
itself.

### 7c. Limitations to state

- Eleven wells, all used in earlier rounds; nothing here is a fresh
  hold-out. The tests are pre-specified, not confirmatory.
- Bag scale. A bag integrates 3-10 m and includes cavings.
- Si/Al is not sand: biogenic silica, tuff and glauconite move it in the
  Hordaland Group. "Chemical skill", not "sand detection".
- Photographs also predict barite (+0.31). Mud residue contributes an
  unknown part of every result. An ilmenite weighting agent would explain
  the Fe-Ti result and has not been excluded.
- Most of the element signal is colour: simple colour and texture features
  do as well as the deep network for Fe, Ca and Ti.
- Mud-log labels: AI readers of one model family, no human key; two logs of
  the same well agree only at +0.42.
- The Jurassic-Triassic mud-log result is an amended test. The eligibility
  rule written for the Tertiary failed by its letter (three wells) and was
  changed after the labels were read, before any photograph was joined.
  Six wells from one area, two of them twins.
- The "where it works" result is what measurement noise alone predicts, and
  also what real contrast predicts; the two are not separated.
- Fine-tuning brought no detectable gain; the frozen model stays the model
  of record.

### 7d. Reproducibility (v7, v8)

| result | commit |
|---|---|
| V7_PLAN final / step-1 script | b1eeb05 / bdf7850 |
| step 2 closed | 632f9e6 |
| step 3 closed (and block-boundary addition) | e9d3896 (676af22) |
| extras X0-X3 and reviewer changes | b2d3c02, 95b5cde, 0b41978, 3d2b4f4 |
| V8_PLAN with reviewer amendments | c675477 |
| v8 D photograph predictions frozen before tiles | 40b5c49 |
| v8 A and B results | ad06c38 (write-up f51869e) |
| v8 figures | 120dec2 |
| v8 D raw readings / eligibility amendment / results | 4c047ec, 633470a / 49d1d0a / 60818cd |

### 7e. Additions to the AI-use statement (section 5)

> 6. **Mud-log digitisation.** Scanned mud logs were cut into tiles by a
>    script. AI agents (Claude Opus and Claude Sonnet) read the lithology
>    percentages from the tiles under written rules, blind to photographs
>    and chemistry. Their agreement is reported; there is no human key.
> 7. **Specialist and review agents.** Further Claude agents, prompted as a
>    geochemist, a computer-vision specialist, a wellsite geologist and a
>    senior reviewer, critiqued plans before each run and results after it.
>    These were not human reviews.
