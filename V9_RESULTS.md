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
is dropped than when any other well is dropped. The size of the dependence
is small: the six-well median goes from +0.52 to +0.50, all six wells stay
positive, and both versions of the test give the same p values. The number
to quote for v8 D is therefore **+0.50 with the twins held out together**,
with +0.52 as the leave-one-well-out value.

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
| Below base Cretaceous (v8 D, 6 wells, 891 bags) | **key: sand fraction against gamma ray** | **-0.27** | 6 of 6 | 0.016 | -0.46 to -0.21 |
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
  (-0.27, 6 of 6). It does so as well as the Si/Al measured on the same
  bags (-0.26).
- **Tertiary: no detectable agreement with gamma ray** by the rule. The
  median (-0.14) misses the -0.20 bar although 5 of 6 wells are negative
  (p 0.047). Measured Si/Al reaches -0.21 there.

### Reading

1. Below base Cretaceous the labels pass an instrument check that no AI
   reader or photograph touched. Together with reader agreement (0.997)
   and the Si/Al check (+0.51) this supports the label chain of v8 D.
2. The agreement is modest in size (-0.27). Gamma ray is not sand: mica,
   potassium feldspar and heavy minerals raise it in sandstone, coal and
   limestone lower it, and a bag is a lagged 3 to 10 m mixture. Measured
   Si/Al does no better against gamma ray, so the size says more about
   cuttings against wireline than about the readers.
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

## K2c. Fine-tuned network at 34/8-3 without the sidetrack in training

PENDING (GPU, six folds; started 2026-11-12).

## K1. Mud weighting material (ilmenite caveat)

PENDING (OCR of the well reports running; then reading of the cited pages).
