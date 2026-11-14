# v9 results: checks that close open caveats (plan: V9_PLAN.md with the reviewer's amendments)

v8 is closed and unchanged. Everything here is EXPLORATORY. Each stage was
run once, with code committed first (68_v9_checks.py, b8d1187).
Result files: results/v9/.

## K2b. Does the deep mud-log result depend on the twin being in training? (68_v9_checks.py k2b)

The pre-Tertiary R-D model of v8 D was refitted with 34/8-3 and 34/8-3 A
held out together. Bags, labels, high-pass and the six wells are those of
the amended test of v8 D. The script first reproduced the v8 D predictions
to 1e-6.

| | 34/4-6 | 34/7-10 | 34/7-4 | 34/7-9 | 34/8-3 | 34/8-3 A | median | wells > 0 | p |
|---|---|---|---|---|---|---|---|---|---|
| v8 D (each well held out alone) | 0.16 | 0.31 | 0.51 | 0.52 | 0.63 | 0.53 | +0.52 | 6 of 6 | 0.016 |
| twins held out together | 0.16 | 0.31 | 0.51 | 0.52 | 0.51 | 0.49 | +0.50 | 6 of 6 | 0.016 |

Twins merged as one unit: +0.50, 5 of 5, p 0.031 (v8 D: +0.51).

Reference (fixed in the plan): dropping any one OTHER training well moves
34/8-3 by -0.02 to +0.02 (largest fall 0.016) and 34/8-3 A by -0.02 to
+0.02 (largest fall 0.019). Dropping the twin lowers 34/8-3 by 0.12 and
34/8-3 A by 0.04.

**By the pre-declared rule: the result depends in part on the twin being in
training.** Both twins stay above +0.30, but each falls more when its twin
is dropped than when any other well is dropped. 34/8-3 falls by 0.12, eight
times the largest fall from dropping any other well (0.016). 34/8-3 A falls
by 0.04 (other wells at most 0.019). The six-well p cannot go below 0.016,
so it is uninformative here. The number to quote for v8 D from now on is
**+0.50 with the twins held out together (five locations: 5 of 5, p 0.031;
EXPLORATORY); +0.52 leave-one-well-out.** +0.50 is not to be paired with
p 0.016.

Main Si/Al result (K2a): nothing was run. v7 step 1 already reports
leave-one-area-out, +0.31 in 10 of 11 wells.

## K3. Gamma-ray key for the digitised sand fraction (68_v9_checks.py k3)

No human key exists and none will be made. This is an instrument key: it
shows whether the digitised sand fraction follows the formation as a
wireline tool recorded it. It does not show that a given percentage was
read correctly.

**Sheet check, done first (results/v9/k3_sheet_check.md).** All eight
sheets are wellsite mud logs made while drilling (six Exlog, one
Gearhart-Owen Geodata, one Anadrill). None prints a gamma-ray track, so no
well is left out.

**Statistic.** Per well, Spearman between the high-passed sand fraction and
the high-passed mean gamma ray over the label's own interval (D_prev, D];
stretches split at casing shoes. Expected sign: negative. One-sided
Wilcoxon over wells.

| set | row | median | wells < 0 | p | 95 % CI |
|---|---|---|---|---|---|
| Below base Cretaceous (v8 D, 6 wells, 891 bags) | **key: sand fraction against gamma ray** | **-0.26** | 6 of 6 | 0.016 | -0.46 to -0.21 |
| | without carbonate >= 30 % or coal bags | -0.29 | 6 of 6 | 0.016 | -0.46 to -0.18 |
| | point gamma ray at the bag depth (descriptive) | -0.24 | 6 of 6 | 0.016 | -0.46 to -0.03 |
| | reference: measured Si/Al against gamma ray | -0.26 | 6 of 6 | 0.016 | -0.43 to -0.19 |
| | reference: photo prediction against gamma ray (not independent) | -0.27 | 6 of 6 | 0.016 | -0.44 to -0.20 |
| Tertiary (v7 step 3, 6 wells, 1,097 bags) | **key: sand fraction against gamma ray** | **-0.14** | 5 of 6 | 0.047 | -0.20 to +0.01 |
| | step 3's own high-pass, no split at shoes | -0.15 | 5 of 6 | 0.047 | -0.20 to +0.02 |
| | point gamma ray at the bag depth (descriptive) | -0.09 | 5 of 6 | 0.031 | -0.17 to -0.01 |
| | reference: measured Si/Al against gamma ray | -0.21 | 6 of 6 | 0.016 | -0.29 to -0.05 |
| | reference: photo prediction against gamma ray (not independent) | -0.08 | 5 of 6 | 0.078 | -0.13 to +0.03 |

Per well, key row. Below base Cretaceous: 34/4-6 -0.23, 34/7-10 -0.37,
34/7-4 -0.30, 34/7-9 -0.23, 34/8-3 -0.20, 34/8-3 A -0.56. Tertiary: 24/9-3
-0.16, 34/4-6 -0.13, 34/4-7 +0.13, 34/7-10 -0.15, 34/7-4 -0.24, 34/7-9
-0.11. In the Tertiary set 29 bags of 34/4-7 have no gamma ray and drop
out; no bag drops out below base Cretaceous.

**By the pre-declared rule (median <= -0.20 and p < 0.05):**
- **Below base Cretaceous: the digitised sand fraction follows gamma ray**
  (-0.26, 6 of 6). It does so as well as the Si/Al measured on the same
  bags (-0.26).
- **Tertiary: does not meet the pre-declared bar** (median <= -0.20 and
  p < 0.05): -0.14, 5 of 6, p 0.047. By the rule this is written "no
  detectable agreement with gamma ray". Measured Si/Al reaches -0.21 there.

### Reading

1. Below base Cretaceous the labels pass an instrument check that no AI
   reader or photograph touched. Together with reader agreement (0.997)
   and the Si/Al check (+0.51) this supports the label chain of v8 D.
2. The agreement is modest in size (-0.26). Gamma ray is not sand: mica,
   potassium feldspar and heavy minerals raise it in sandstone, coal and
   limestone lower it, and a bag is a lagged 3 to 10 m mixture. Measured
   Si/Al does no better against gamma ray, so the size suggests a limit of
   cuttings against wireline more than a fault of the readers.
3. In the Tertiary the label is weakly tied to gamma ray, weaker than
   measured Si/Al. This fits step 3 (the sand fraction barely varies
   there; glauconitic sands and tuffs raise gamma ray) and is one more
   reason to treat the Tertiary mud-log result (+0.13) as weak.
4. The photo-prediction rows are context only. The image pipeline was
   developed against gamma-ray labels in v1 and v2, so they are not
   independent of gamma ray.
5. Limits: the composite curve does not name its runs, so open-hole and
   through-casing gamma ray cannot be told apart from the file; agreement
   supports the whole chain (wellsite geologist, sheet, reader, bag join),
   not the reader alone; "no human key" stays a stated limitation.

## K2c. Fine-tuned network at 34/8-3 without the sidetrack in training (59_v7_cnn_sial.py trainx; 68_v9_checks.py k2c)

The 34/8-3 fold was retrained with 34/8-3 A removed from training, and the
reverse, with the three seeds and fold seeds of v8 C. Six folds, trained
2026-11-12 (code 14789de), scored once. The script first reproduced the
step-1 R-D predictions of both wells to 1e-6.

| held-out well | model | seed 0 | seed 1000 | seed 2000 | mean of 3 |
|---|---|---|---|---|---|
| 34/8-3 | fine-tuned, twin in training (v8 C) | 0.31 | 0.21 | 0.41 | 0.31 |
| 34/8-3 | **fine-tuned, twin removed** | 0.40 | 0.17 | 0.23 | **0.27** |
| 34/8-3 | difference (with minus without) | -0.09 | +0.03 | +0.17 | +0.04 |
| 34/8-3 A | fine-tuned, twin in training (v8 C) | 0.19 | 0.25 | 0.15 | 0.20 |
| 34/8-3 A | fine-tuned, twin removed | 0.15 | 0.18 | 0.11 | 0.15 |
| 34/8-3 A | difference (with minus without) | +0.03 | +0.08 | +0.05 | +0.05 |

Frozen models, with the twin and without it: at 34/8-3, R-D +0.02 and
-0.00, frozen ResNet-18 control +0.01 and -0.01; at 34/8-3 A, R-D +0.18 and
+0.17, control +0.16 and +0.14.

**By the pre-declared rule (mean of three seeds >= 0.15 and all three above
zero): the 34/8-3 observation does not depend on the sidetrack being in
training.** The mean goes from +0.31 to +0.27; the change (0.04) is well
inside the seed noise at this well (seed SD 0.10 with the twin, 0.12
without). The frozen models stay at about zero either way.

### Reading

1. The sidetrack hypothesis of v8 C is not supported: without 34/8-3 A in
   training, three fine-tuned runs still give +0.17 to +0.40 where frozen
   features give nothing. Three seeds cannot exclude a contribution from
   the twin of up to about 0.2 (seed SD 0.10 to 0.12). The seed-by-seed
   differences in the table are not truly paired: a smaller training set
   changes the batch order, so the two runs of a seed are effectively
   independent.
2. The v8 C limits that remain: one well, singled out after the first run;
   the largest seed SD of all wells; no test of 34/8-3 alone and no p
   value. Removing a well also makes the training set one well smaller,
   which is not controlled. It stays an observation: at 34/8-3 the flat
   chemistry may not be all noise, and a fine-tuned network picks up part
   of it.
3. 34/8-3 A (descriptive, no rule): +0.20 with the twin, +0.15 without, in
   all three seeds slightly lower without; the frozen models barely move.

## K1. Mud weighting material (the ilmenite caveat of v8 A) (69_v9_k1_ocr.py; results/v9/k1_weighting_material.md)

**What was read.** 29 drilling, mud and completion reports of the 11 wells,
3,474 pages. 800 pages had a text layer; 2,674 were scans and were read by
a local OCR. Keywords were fixed before the search. Every page counted was
then opened and read as an image by me, and the products were copied word
for word.

**Deviations from the plan.** (1) OCR over every multi-page PDF replaced
the contents-based page list (more coverage). The cited pages were read as
images by one reader, the AI assistant running the analysis. No second
reader and no human checked them (less verification). (2) The no-hit check
read 11 of 173 candidate pages (6 %, below the planned 10 %). The pool was
the OCR pages that mention mud three or more times and have no keyword
hit; one page per well was drawn with seed 911. 34/7-6 had no such page
(its report has a text layer), so its page was drawn the same way from its
text-layer pages. (3) Unweighted sections were taken from the materials
tables, not from the Sodir mud-weight table.

**Result.**

| | wells |
|---|---|
| Complete mud-materials table found, barite the only solid weighting material | 10: 24/9-4, 34/4-6, 34/4-7, 34/7-1, 34/7-10, 34/7-4, 34/7-6, 34/7-9, 34/8-3, 34/8-3 A |
| Weighted mud, weighting material not named | 1: 24/9-3 (mud summary gives mud types and weights up to 11.0 ppg, but no materials list) |
| Ilmenite, hematite, iron oxide or any titanium-bearing name | none, in the text layer or OCR of any of the 3,474 pages |

- The ten tables are well totals or cover every hole section, so they cover
  the sections that hold the v8 A bags.
- Unweighted sections (no weighting agent at all): the 36" holes; in 34/8-3
  also the 17 1/2" hole to 1317 m (bentonite and caustic soda only).
- Trade-named products (polymers, thinners, lost-circulation material such
  as "Mica") are listed in the evidence file and are not interpreted.

**By the pre-declared rule: the caveat is reworded for ten wells and stays
for 24/9-3.** New wording for v8 A: "The mud-materials tables of ten wells
list barite as the only solid weighting material and no product named
ilmenite, hematite or iron oxide (trade-named additives not interpreted).
24/9-3 has no materials list, so an iron-titanium weighting agent is not
excluded there." KCl and CaCl2 brines also raise mud density; they carry no
iron or titanium.

**Post hoc, descriptive (no model refitted; from the saved per-well values
of v8 A).** Fe/Al and Ti/Al with and without 24/9-3. p: one-sided Wilcoxon,
not Holm-adjusted (v8 A quoted Holm).

| ratio | row | wells | median | wells > 0 | p |
|---|---|---|---|---|---|
| Fe/Al | photo prediction against measured | 11 wells | +0.28 | 11 of 11 | 0.0005 |
| Fe/Al | photo prediction against measured | without 24/9-3 | +0.29 | 10 of 10 | 0.001 |
| Fe/Al | partial given Ba and Cl | 11 wells | +0.29 | 11 of 11 | 0.0005 |
| Fe/Al | partial given Ba and Cl | without 24/9-3 | +0.29 | 10 of 10 | 0.001 |
| Fe/Al | partial given Si and Al | 11 wells | +0.14 | 11 of 11 | 0.0005 |
| Fe/Al | partial given Si and Al | without 24/9-3 | +0.13 | 10 of 10 | 0.001 |
| Ti/Al | photo prediction against measured | 11 wells | +0.27 | 10 of 11 | 0.001 |
| Ti/Al | photo prediction against measured | without 24/9-3 | +0.27 | 9 of 10 | 0.003 |
| Ti/Al | partial given Ba and Cl | 11 wells | +0.21 | 10 of 11 | 0.001 |
| Ti/Al | partial given Ba and Cl | without 24/9-3 | +0.19 | 9 of 10 | 0.003 |
| Ti/Al | partial given Si and Al | 11 wells | +0.16 | 10 of 11 | 0.001 |
| Ti/Al | partial given Si and Al | without 24/9-3 | +0.17 | 9 of 10 | 0.002 |

This table was not pre-declared (no iron-titanium material was found, so the
planned re-scoring did not apply). Removing the one well without a materials
list moves no median by more than 0.02.

**Limits.** A materials table says what was mixed into the mud, not what
is in a given bag. Barite is a natural product and may carry iron
impurities (not checked). Steel wear adds iron but no titanium; in 34/8-3 A
a casing window was milled at about 945 to 985 m. Natural iron-titanium
minerals in the rock are what the Fe-Ti signal is taken to be; this check
only removes one alternative. The OCR could miss a word on a poor scan;
the tables themselves were read as images.

## Reviewer (K1, K2b, K3 after results): ACCEPT WITH CHANGES, applied

Every number was checked against the result files. One rounding error
(K3 key median -0.2646 was printed as -0.27; now -0.26), the K2b reading
sharpened (which p belongs to +0.50), two wrong row labels in the K1 table,
the K1 deviations restated (more coverage, less verification), and the
ilmenite wording narrowed to "solid weighting material". K2c was reviewed after it ran (ACCEPT WITH CHANGES: the limit of three
seeds added to its Reading 1).
