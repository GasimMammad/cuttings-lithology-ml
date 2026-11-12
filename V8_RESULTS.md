# v8 results (plan: V8_PLAN.md with the reviewer's amendments; each part run once)

v7 is closed and unchanged. Scripts were committed before each run.
Result files: results/v8/.

## A. More elements from the same photographs (63_v8_elements_when.py A)

Set S, model R-D, leave-one-well-out, per-well +/-50 m high-passed Spearman,
11 wells, as step 1. Targets: within-well z of log10(element / Al).

| target | median rho | wells > 0 | Holm p | mud partial | beyond Si and Al (Holm p) | Si/Al model reused (paired p) | colour model R-E (paired p) | counts |
|---|---|---|---|---|---|---|---|---|
| K/Al | +0.20 | 11 | 0.002 | +0.18 | +0.06 (0.051) | +0.19 (0.48) | +0.08 (0.002) | no |
| Fe/Al | +0.28 | 11 | 0.002 | +0.29 | +0.14 (0.002) | +0.09 (0.002) | +0.23 (0.23) | **yes** |
| Ca/Al | +0.19 | 11 | 0.002 | +0.17 | +0.13 (0.010) | +0.13 (0.005) | +0.18 (0.58) | **yes** |
| Ti/Al | +0.27 | 10 | 0.003 | +0.21 | +0.16 (0.004) | +0.26 (0.55) | +0.18 (0.087) | **yes** |
| Zr/Al | +0.10 | 10 | 0.003 | +0.03 | +0.12 (0.019) | +0.02 (0.027) | +0.15 (0.45) | no |

Columns: "mud partial" = partial rho given high-passed Ba and Cl (plus S
for Ca, plus Sr for Zr). "Beyond Si and Al" = partial rho given high-passed
log Si and log Al. "Si/Al model reused" = the step-1 prediction scored
against this target, sign fixed from the other wells; the p is the paired
test that the element's own model does better. "R-E" = engineered colour
and texture features; the p is the paired test that R-D does better.

- **All five targets pass** the step-1 rule (Holm p < 0.05, median >= 0.10).
- **Three count under the pre-declared rule** (pass, beyond Si and Al, mud
  partial): Fe/Al, Ca/Al, Ti/Al. The rule needed two, so the pre-declared
  wording applies: **the photographs give a rough chemical log, not only a
  quartz-clay axis.**
- K/Al misses the "beyond" criterion (median +0.06, 7 of 11 wells
  positive, Holm p 0.051) and is not counted. Zr/Al fails the mud control
  (+0.03).
- What tempers this:
  - **Fe and Ti move together** in every well (high-passed rho(Fe, Ti)
    0.39 to 0.74). They may be one axis (Fe-Ti-bearing clay and heavy
    minerals, or a contaminant), not two. Counting them as one still leaves
    two (Fe-Ti and Ca). The Ba/Cl control does not cover an ilmenite
    weighting agent, which carries Fe and Ti together. The mud reports
    should be checked for it before Fe-Ti is called geological.
  - **For all three counting targets, simple colour and texture features
    do as well as the embeddings** (paired p: Fe 0.23, Ca 0.58, Ti 0.087;
    Zr 0.45, where R-E is higher). The photographs carry this chemistry
    mostly as colour. Only for K, which does not count, do the embeddings
    clearly add (p 0.002).
  - **For Ti and K the Si/Al model reused does as well as the element's own
    model** (paired p 0.55, 0.48). Their own models are not specific. Ti
    still counts because its partial given Si and Al is positive in 10 of
    11 wells.
  - **The "beyond" partials are upper bounds.** Measured Si and Al are
    noisy, so partialling them out removes only part of the quartz-clay
    axis. This matters most for Ti. The robust count is two specific
    targets, Fe(-Ti) and Ca, whose own models beat the Si/Al model reused
    (paired p 0.002 and 0.005).
  - The sizes are small: +0.2 to +0.3 at bag scale, as for Si/Al.
- Flags: rho(K, Cl) is 0.27 to 0.40 in three wells (24/9-4, 34/7-6,
  34/8-3), a sign of KCl mud; K was not counted anyway.
- Ca/Al here (+0.19) against step 1's Ba-residualised Ca (+0.12): the same
  direction, a different target.

## B. When does the method work? (63_v8_elements_when.py B)

Hypothesis fixed beforehand: agreement is higher where the measured Si/Al
varies more.

| test | result |
|---|---|
| B1, between wells: step-1 rho against the spread (MAD) of measured high-passed log10(Si/Al) | Spearman +0.78, exact permutation p = 0.003 (n = 11) |
| B2, within wells: 150 m windows, window rho against window spread | median per-well Spearman +0.54; 7 positive, 1 zero, 2 negative of 10 wells; p = 0.014 |
| B3, label-free, within wells: window rho against the spread of the PREDICTION | median +0.48; 9 of 10 wells positive; p = 0.003 |
| B3, label-free, between wells | Spearman +0.47, p = 0.073 |
| B4, Tertiary against pre-Tertiary (descriptive) | the section with the larger spread has the higher rho in 8 of 10 wells |

- **Skill follows the spread of the chemistry** (B2 p < 0.05 and B1 the
  same sign: the pre-declared condition). A positive B2 is what
  attenuation by XRF and sampling noise predicts. It is equally expected if
  larger chemical contrasts are also larger visual contrasts. The two are
  not separated here.
- **A label-free indicator is supported within wells:** intervals where the
  model's own output varies more are the intervals where it agrees better
  with the chemistry. Between wells the same indicator is weaker (p 0.07).
  B2 and B3 are not independent tests: one strong contrast in a window
  raises both its spread and its rho.
- Consistent with this, 34/8-3 has the lowest rho (+0.03) and the
  second-smallest spread (MAD 0.0215 in log10 units). 34/8-3 A has the
  smallest spread (0.0201) but only the third-lowest rho (+0.18; 24/9-4 has
  +0.17). They are twin wells, not independent points. The four wells with
  the largest spread (24/9-3, 34/7-9, 34/7-4, 34/7-10; MAD 0.032 to 0.049)
  are four of the five wells with the highest rho (+0.46 to +0.53).
- Descriptive, no test: rho is unrelated to the number of bags (-0.02).
  It rises with bag spacing (+0.59) and falls with mean log Ba (-0.48).
  Spacing groups by area (3 m: the 24/9 wells; 5 m: the 34/8-3 pair), and
  the 3 m wells rank 5th and 10th. No interpretation is offered.
- B4: the pre-Tertiary has the larger spread in 9 of 10 wells, so B4 mostly
  restates that the pre-Tertiary scores higher (7 of 10). In 34/7-4 the two
  spreads are equal.
- Limits: 82 windows, most of them at the 15-bag minimum, so each window
  rho is noisy; B1 has 11 points; no threshold was pre-declared, so none is
  offered. The practical statement is qualitative: trust the photo log
  where it moves, not where it is flat. Changes in photography, mud or bit
  also make it move, so this ranks intervals within a well and certifies
  none.

## Reviewer (A and B, after results): ACCEPT WITH CHANGES, applied
Every number matched the result files; Holm and the counting rule were
applied as written. Changes applied above: one factual error about the twin
wells corrected; Ti added to the colour-baseline caveat; the "beyond"
partials stated as upper bounds, with the robust count given as two (Fe-Ti
and Ca); the ilmenite caveat; the attenuation sentence made two-sided; the
declared Ba result reported; B4 and the B2-B3 dependence stated.

## D. Wellsite sand fraction below base Cretaceous (Jurassic-Triassic) (scripts 64, 66, 67)

**Status: amended, exploratory test. By the letter of the pre-registered
eligibility rule only three wells qualified, so no test of record exists.**
Under an eligibility rule amended after the labels were read but before any
photograph was joined (commit 49d1d0a), six wells (five independent units)
qualify.

### Labels
- Seven wells, base Cretaceous to the deepest bag, 101 tiles of 40 m.
  Reader A (Opus) read all, reader B (Sonnet) a seeded 20 % (23 tiles).
  Rules v3 plus an addendum for these sheets, both written from the legends.
- **G1 (depth):** all 43 printed 100 m labels sit on their calibrated line.
- **G2 (reader agreement): passes every gate.** 283 bag intervals:
  Spearman 0.997, mean absolute difference 0.7 points, 1 interval differing
  by more than 20 points. Worst well 34/7-10 (Spearman 0.97, 3.2 points).
  Class presence differs mainly for silt (reader A alone in 20 intervals,
  the dash-dot pattern on 34/7-10) and thin limestone stripes (6 against 5).
  The readers never used the silty-sandstone class, so the primary Y is
  plain sand.
- Sand is the main lithology: mean 35 to 81 % per well over the labelled
  bags of the test set (34/7-9 in the Tertiary: 6 %).
- **Eligibility.** By the letter: 34/7-10, 34/7-9, 34/8-3. The step-3 rule
  asks for informative bags in three clusters more than 30 m apart; here
  informative bags are nearly continuous (they fill 23 and 20 thirty-metre
  bins in 34/4-6 and 34/7-4, and 5 in 34/8-3 A), so the cluster count is 1
  or 2. Amended
  rule: informative bags in at least 3 distinct 30 m bins spanning at least
  90 m. Six wells qualify. 34/4-7 does not: its scan has faded and only 17
  bags have a label. 34/8-3 A is small (44 bags).
- 908 labelled bags after the masks (Sodir cored intervals, 15 m below
  every shoe including liners, 10 bags in irregular depth-grid intervals).
- **G3 (label against measured Si/Al, no photographs):** median +0.51, 6 of
  6 wells, p = 0.016. In the Tertiary this was +0.18.

### Photograph test (run once)
Predictor: the step-1 pre-Tertiary Si/Al model, trained without the test
well, frozen and committed before any tile was read (40b5c49).

| | wells or units | median rho | positive | p | 95 % CI |
|---|---|---|---|---|---|
| **Amended test** | 6 wells | **+0.52** | 6 of 6 | 0.016 | +0.23 to +0.58 |
| Amended test, 34/8-3 pair merged | 5 units | +0.51 | 5 of 5 | 0.031 | +0.16 to +0.58 |
| By the letter (descriptive, no test) | 3 wells | +0.52 | 3 of 3 | - | - |

Per well: 34/4-6 +0.16; 34/7-10 +0.31; 34/7-4 +0.51; 34/7-9 +0.52; 34/8-3
+0.63; 34/8-3 A +0.53. Both versions reach p < 0.05 (each is the smallest p
its number of units allows) and a median above 0.10, which was the pass
condition set with the amendment.

| context and sensitivities (6 wells) | median rho | positive | p |
|---|---|---|---|
| Colour and texture features (R-E) against Y | +0.47 | 5 of 6 | 0.031 |
| Measured Si/Al against Y (= G3) | +0.51 | 6 of 6 | 0.016 |
| **Photo prediction given measured Si/Al (partial)** | **+0.15** | 6 of 6 | 0.016 |
| Relative depth, sign from the other wells | -0.10 | 1 of 6 | 0.92 |
| Model trained on the Jurassic-Triassic range only | +0.50 | 6 of 6 | 0.016 |
| Without the earlier pilot interval (34/7-10, 2510-2670 m) | +0.52 | 6 of 6 | 0.016 |
| Without bags with carbonate + marl >= 30 % or any coal | +0.52 | 6 of 6 | 0.016 |
| Y = sand + silt | +0.51 | 6 of 6 | 0.016 |

Exploratory, carbonate (limestone + half of marl): measured Ca/Al against
the mud-log carbonate is itself only +0.12 (5 of 5 wells with any
carbonate). The photo Ca/Al model gives +0.03 (5 of 5, p 0.031): nominally
positive, negligible in size. With Cl partialled out, +0.03 (5 of 6, p
0.078); this line includes 34/8-3, which the other two drop because its
label has no carbonate.

### Reading (reviewer: ACCEPT WITH CHANGES, applied)
1. Where sandstone is common, the photograph model follows the wellsite
   sand fraction about as well as the measured chemistry does (+0.52
   against +0.51), in every well tested. In the Tertiary (step 3: a
   Tertiary-trained model, the unamended rule, a label that barely varied)
   it gave +0.13, and measured Si/Al +0.18. The contrast is descriptive and
   mainly reflects how much the label varies.
2. Given measured Si/Al, a partial of +0.15 remains (6 of 6; three wells
   +0.02 to +0.05). As in part A, it is an upper bound. Measured Si/Al is a
   noisy and imperfect sand proxy (arkosic and kaolinitic sandstones). The
   mud logger and the photographs also judge the same cuttings by eye
   (colour and texture alone +0.47), so the residual may be shared visual
   information rather than skill beyond chemistry.
3. Colour and texture features alone reach +0.47. The deep-network
   embeddings are not clearly better; no paired test was declared.
4. The depth baseline after the same high-pass is negative (-0.10). The
   high-pass already removes trends longer than about 100 m, so this only
   rules out short residual trends.
5. Limits: an amended test, not a test of record; six wells from one area
   (Tampen), two of them twins; AI readers with no human key (very high
   agreement between readers says the sheets are clear, not that the
   wellsite geologist was right); 34/4-6, the one Anadrill sheet and the
   most strongly skewed scan, is the weakest (+0.16); cavings, cored
   intervals and the first 15 m below shoes are handled by masks only.
   Both p values are the smallest possible for 6 and 5 units, so one
   negative unit would fail the five-unit version. Each twin was in the
   other's training fold. The readers worked in separate folders and their
   block lists differ in 18 of 23 shared tiles, so agreement reflects clear
   10 %-step drawings, not copying. It cannot exclude errors shared by one
   model family.
6. Together with step 3 this fits part B: the model agrees with a
   reference where the rock varies, and has little to agree with where it
   does not.
