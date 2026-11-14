# v8 plan (2026-11-11): five follow-ups to v7, written before any of them is run

Chosen on 2026-11-11 from the list of follow-ups (items 1, 2, 4, 5 and the
additional checks). v7 (steps 1-3 and extras X0-X3) is closed and is not
changed by anything here. Parts A, B, C, D are analyses; E is a figure; F is
writing. Each analysis part states what would count as a result before it is
run. Definitions not repeated here are those of V7_PLAN.md step 1 (set S,
target construction, R-D, leave-one-well-out, +/-50 m high-pass, per-well
Spearman, one-sided Wilcoxon over wells, well-bootstrap CI) and step 3
(tiles, readers, bag join, gates G1-G3, eligibility C4).

What I already know when writing this (so the reader can judge the
blindness of each part):
- Step 1 results, including: photo -> Ca (Ba-partialled) +0.12 (10 of 11,
  p 0.003); photo -> Ba +0.31; pre-Tertiary photo -> Si/Al, descriptive,
  median +0.51 (9 of 10 wells; 24/9-3 negative, 72 bags).
- X1 per-well values for one seed.
- Nothing about K, Fe, Ti or Zr against photographs. Nothing about any
  pre-Tertiary mud-log reading except the earlier pilot interval named
  in step 3 (34/7-10, 2510-2670 m).

## A. More elements from the same photographs (user item 4)

Question: do the photographs carry chemical information beyond the
quartz-clay axis (Si/Al)?

- **Set, model, validation, statistic:** set S of step 1, R-D unchanged,
  leave-one-well-out, per-well +/-50 m high-passed Spearman.
- **Targets** (within-well z over S of log10 ratios; element must be > 0):
  1. K/Al (illite, mica, K-feldspar, glauconite against kaolinite, smectite)
  2. Fe/Al (glauconite, Fe-smectite, siderite, pyrite)
  3. Ca/Al (carbonate)
  4. Ti/Al (heavy minerals, volcanic ash)
  5. Zr/Al (zircon: a silt and sand proxy independent of Si)
- **Coverage rule (counts only, checked before any correlation):** a well
  enters a target if at least 80 % of its S bags have the element > 0; a
  target is tested if at least 8 wells enter.
- **Test:** one-sided Wilcoxon of the per-well rho > 0, Holm-corrected over
  the targets tested. A target "passes" if Holm p < 0.05 and median rho >=
  0.10 (the step-1 rule).
- **For every target, pass or fail, reported:**
  - mud control: partial rho given high-passed Ba and Cl (for Ca/Al also S);
  - beyond Si/Al: partial rho of prediction against target given measured
    T1. A target is called "beyond Si/Al" only if this partial has median
    >= 0.05 and one-sided Wilcoxon p < 0.05 (uncorrected, stated as such);
  - specificity: paired Wilcoxon of rho(pred_E, E) against
    |rho(pred_T1, E)|, i.e. does a model trained for the element do better
    than the Si/Al model reused;
  - colour baseline: the engineered-feature model R-E, same folds, paired.
- **Wording, fixed now:** "a rough chemical log" only if at least 3 of the
  targets pass AND at least 2 are "beyond Si/Al". If targets pass but none
  is beyond Si/Al: "the photographs see one chemical axis; the other
  elements follow it". Zero passes: "no evidence beyond Si/Al".
- Ca/Al differs from step 1's Ca target (that one was Ba-residualised Ca,
  not a ratio to Al); both are shown side by side.

## B. When does the method work? (user item 5)

Hypothesis fixed now: agreement is higher where the measured Si/Al varies
more, because XRF noise is roughly constant in log units while the target is
z-scored within the well.

- **B1, between wells (n = 11, descriptive):** Spearman between the step-1
  per-well rho (R-D) and the SD of high-passed raw log10(Si/Al) in S.
  Exact permutation p reported. Also shown, no test: number of bags, median
  bag spacing, mean log Ba.
- **B2, within wells (the test):** each well's S series is cut into
  consecutive 150 m windows (at least 15 bags). In each window: rho between
  high-passed prediction and high-passed T1, and SD of high-passed raw
  log10(Si/Al). Per well (at least 5 windows): Spearman of window rho
  against window SD. One-sided Wilcoxon of these over wells (> 0).
- **B3, a label-free indicator (descriptive):** the same as B1 and B2 with
  the SD of the high-passed PREDICTION in place of the SD of the measured
  ratio. This is the only version a user without XRF could compute.
- **B4, Tertiary against pre-Tertiary (descriptive):** for the wells with
  both, is rho higher in the section with the larger SD (sign count). The
  two sections have separately trained models; stated as a confound.
- **Wording:** "skill follows the spread of the chemistry" only if B2 has
  p < 0.05 and B1 has the same sign. A practical rule of thumb is offered
  only if B3 (within wells) also has p < 0.05. Otherwise "no usable
  predictor of where it works was found (11 wells)".

## C. Fine-tuned network, two more seeds (additional)

- X1 repeated twice with nothing changed except the seed: torch and numpy
  seed = SEED + 1000 + fold index, and SEED + 2000 + fold index.
- Reported: per-well rho for the three seeds, per-well seed SD, median seed
  SD.
- Tests (as X1, same wording rules): per-well mean over the three seeds,
  paired one-sided Wilcoxon against the frozen ResNet-18 control and
  against R-D. Secondary: the three-seed ensemble (mean prediction).
- 34/8-3: the X1 observation (+0.31) "reproduces" only if both new seeds
  give >= 0.15. Otherwise it is reported as seed noise.
- About 4.3 h of GPU.

## D. Pre-Tertiary mud-log labels (additional)

A new, separately declared test. It is NOT step 3's set W: step 3 had six
eligible Tertiary wells, so its test of record stays the Tertiary set and
is closed.

- **Wells:** the eight step-3 wells (34/4-6, 34/4-7, 34/7-4, 34/7-9,
  34/7-10, 34/8-3, 34/8-3 A, 24/9-3). Not 34/7-1 (zone text only), 24/9-4
  (no pre-Tertiary bags), 34/7-6 (no mud log).
- **Range:** from the bottom of each well's step-3 tiles to the deepest
  photographed bag, in 40 m tiles (about 220 tiles). Same scripts 54/55,
  same calibration tables.
- **G1:** every printed 100 m label in the new range checked on the contact
  sheets before tiles go to readers; table extended.
- **Readers:** as step 3. Reader A (the stronger model) reads every tile;
  reader B (a different model) a seeded 30 % (seeds 5611, 5612). Rules v3
  unchanged, plus a pre-Tertiary sheet-note addendum written from the
  legends and from the look of the column only (limestone, marl, coal,
  cored intervals, "no sample"). Cored or blank intervals are masked.
- **G2:** the eight step-3 gates, unchanged. No re-read this time (cost):
  if a pooled gate fails, the well with the worst per-well agreement is
  dropped once and the gates are recomputed; if they still fail, everything
  in D is descriptive and no test is made. First-pass result reported
  either way.
- **Label:** Y = sand fraction as in step 3 (bottom-of-interval bag join,
  cover >= 0.80). Reader A is the reader of record.
- **Set P:** pre-Tertiary (depth >= top Shetland), shoe-masked, XRF present.
- **Eligibility:** C4 unchanged (>= 30 bags, >= 15 informative in >= 3 depth
  clusters). A test is made only with at least 6 eligible wells; with fewer,
  descriptive.
- **G3:** Y against measured z log10(Si/Al) over P, as step 3 (median <= 0:
  stop; < 0.15: a failed photo test is "uninformative").
- **PRIMARY (no label used in training):** the pre-Tertiary R-D Si/Al
  predictions of step 1 (its "pre-Tertiary, descriptive" block: per-well z
  over P, leave-one-well-out over the wells with >= 30 bags). They are
  recomputed by the same code, saved and committed BEFORE any tile is read.
  Statistic and success rule as step 3 P2: per-well high-passed Spearman
  against Y, one-sided Wilcoxon over eligible wells, p < 0.05 and median
  >= 0.10.
- **Context, reported with the primary:** R-E (engineered colour and
  texture) the same way; measured Si/Al against Y (= G3); partial rho of
  the primary given measured Si/Al; relative depth baseline signed from the
  other wells; the primary without the pilot interval 34/7-10 2510-2670 m.
- **Exploratory, declared:** mud-log carbonate fraction (limestone + half
  of marl) against measured Ca/Al and against a pre-Tertiary R-D model
  trained on Ca/Al.
- **Wording, fixed now:** pass: "in the pre-Tertiary, where sandstones are
  common, the chemistry model follows the wellsite sand fraction (median
  rho x)". It is "better than in the Tertiary" only as a description (the
  two tests have different models and wells are the same). If the partial
  given Si/Al is near zero, say so as in step 3. Fail with G3 >= 0.15: "the
  photographs do not follow the wellsite sand fraction even where sand is
  common".
- **Known weaknesses, named now:** no human key; readers of one model family;
  deeper sections have more cavings and oil-based or heavier muds; cored
  intervals have no cuttings; the readers have seen Tertiary sheets, not
  these; I know the step-1 pre-Tertiary chemistry result (+0.51), so the
  expectation is positive.

## E. Figure (user item 2)

Descriptive figure of closed results; no new statistic.
- One overview: 11 wells as small panels, measured z log10(Si/Al) and the
  held-out R-D prediction against depth (both shown high-passed and
  lightly smoothed, stated on the figure), top Hordaland/Shetland markers.
- Three detail panels chosen by rank of the step-1 per-well rho, not by
  look: best (34/7-9), middle (34/7-6), worst (34/8-3). Each with gamma ray
  where a log exists and the mud-log sand column where digitised.
- Every panel prints its rho. The failing well is shown, not dropped.

## F. Writing (user item 1)

- THESIS_NOTES.md: new section for v7 and v8 (consolidated table, methods
  text, limitations, update of the AI-use statement).
- CONFERENCE_NOTES.md: 250-word abstract, key messages, a talk outline with
  what each slide must show, figure list, expected questions with answers.
  No slide deck (not requested).
- Every number traced to a results file; the review checks claims against
  those files.

## Order and review

1. This plan goes to review. Nothing below starts before changes are
   applied and committed.
2. C starts (GPU, background). A and B run once. D's pre-Tertiary
   predictions committed; D tiles and G1; sheet-note addendum.
3. Review: A, B results and D's addendum (before readers start).
4. D readers; meanwhile E and a first draft of F.
5. C and D scored once; review; F finalised; review on F.

## Review (v8 plan): approved with changes. Amendments, applied before anything is run; they take precedence over the text above

### A (elements)
- **Why:** all five targets share the Al denominator with Si/Al, so a
  model that only sees clay would make all five "pass".
- **A target counts** only if (a) it passes (Holm p < 0.05 and median rho
  >= 0.10), (b) its partial rho given high-passed log10 Si AND log10 Al
  (two controls) has median >= 0.05 with Holm p < 0.05 over the tested
  targets, and (c) its mud-control partial has the same sign with median
  >= 0.05. "A rough chemical log" needs at least 2 counting targets. The
  partial given T1 alone is dropped as the criterion (still shown).
- **Specificity comparator:** rho(pred_T1, E) with its sign fixed from the
  training wells (mean sign of the other wells), not the absolute value.
- **Coverage:** the LAS files carry no detection limits; non-detects are
  stored as 0 (counts checked 2026-11-11, no correlation looked at: K, Fe,
  Ca, Sr 100 % above zero; Ti and Zr >= 97 % in every well). Rule: element
  > 0, no offset added. All five targets are tested in all 11 wells.
- **Controls per element:** Zr also controls Sr (Sr K-beta overlaps Zr
  K-alpha; barite carries Sr). Reported flags: rho(K, Cl) per well (KCl
  mud); rho(Fe, Ti) per well (weighting agent, steel). Cl as a control
  keeps step 1's log10(Cl + 1), since 26 % of bags have Cl = 0.
- **Zr wording:** "detrital heavy-mineral proxy, insensitive to biogenic
  silica". Not "independent of Si".

### B (when it works)
- High-pass the full series first, then window. Windows start at the top
  of each continuous stretch; windows with fewer than 15 bags are dropped,
  not merged. Spread = MAD, not SD (in B1, B2, B3 and B4).
- Wording adds: "a positive B2 is what measurement-error attenuation
  predicts".

### C (seeds)
- Optional extra seeding declined: the two new runs must differ from X1 in
  the seed only. C runs on idle GPU and costs no credits.

### D (now "Jurassic-Triassic mud-log labels")
- **Range:** from base Cretaceous (Sodir lithostratigraphy, saved in
  results/v8/sodir_litho_tops.csv) to the deepest bag. Shetland and Cromer
  Knoll are left out: mostly mudstone and marl, near-zero sand, and
  limestone stringers break the link between Si/Al and sand.
  Base Cretaceous used: 34/4-6 2577 m, 34/4-7 2502, 34/7-10 2400, 34/7-4
  2517, 34/7-9 2443, 34/8-3 2827, 34/8-3 A 3003. 24/9-3 has no section
  below the Cretaceous and leaves D. About 100 tiles.
- **Feasibility (label-free counts, done 2026-11-11):** usable bags (below
  base Cretaceous, XRF present, outside Sodir cored intervals, outside 15 m
  below every shoe including liners): 34/4-6 208, 34/7-4 186, 34/7-9 179,
  34/7-10 152, 34/8-3 145, 34/4-7 82, 34/8-3 A 44. Seven wells have >= 30,
  so D runs. Readers take the wells in this order.
- **Masks:** Sodir cored intervals (results/v4/sodir_core_table.csv), not
  reader flags. Shoe mask extended to liner shoes. High-pass stretches are
  split at every shoe. The Sodir mud table lists water-based mud at every
  depth in all seven wells (results/v8/sodir_mud_table.csv), so no
  mud-system split is needed; oil-based mud is not a factor here.
- **Primary predictor, made precise:** the step-1 pre-Tertiary R-D
  predictions exactly as that code makes them (trained on all pre-Tertiary
  bags of the other wells), evaluated on the bags of the range above. One
  sensitivity: the same model trained on the Jurassic-Triassic range only.
- **G1** also checks the depth scale of each sheet in the new range
  (reservoir sections are sometimes drawn at 1:200).
- **G2 without re-read:** a well that fails its per-well gate is dropped.
  If a pooled gate fails, the worst well (lowest per-well Spearman; mean
  absolute difference where Spearman is undefined) is dropped once.
  Informative top-up allowed. Order: G2, eligibility, commit, G3.
  Reader B reads a seeded 20 % (not 30 %), with the floor of 30
  informative intervals kept by top-up.
- **Futility stop:** after the first three wells are read, G2 and G3 are
  computed for them (no photographs). If the G3 median is <= 0, D stops.
- **Twin wells:** 34/8-3 and 34/8-3 A are also reported merged as one unit
  (mean rho). If the result holds only with them counted separately, the
  wording adds "depends on the twin wells".
- **Sensitivity:** without bags where the reader gives carbonate + marl
  >= 30 % or any coal.
- **Carbonate exploratory test** carries a Cl partial.
- **Weaknesses added:** mud loggers leave recognised cavings out of the %,
  while bags and photographs include them; PDC or turbine bits make rock
  flour and sand washes out of the bags; arkosic or kaolinitic sandstones
  (Lunde, Statfjord, Brent) lower Si/Al inside sandstone; the primary is
  largely predictable from (Si/Al against Y) x (photo against Si/Al), so
  the informative number is the partial given Si/Al.

### E
- Smoothing stated on the figure (5-bag running median); every rho printed
  is computed unsmoothed.

### Order (changed)
C on the GPU now. A and B run once. E and a first draft of F. Then D in the
reduced form. Review after A/B (with D's sheet-note addendum), after C/D,
and on F.

### D details fixed on 2026-11-11 after the tiles were made, before any tile was read
- 101 tiles (34/4-6 18, 34/4-7 12, 34/7-10 15, 34/7-4 16, 34/7-9 20,
  34/8-3 14, 34/8-3 A 6), script 64. The column was followed down from the
  last step-3 tile; one tile per sheet family was looked at to confirm the
  right column.
- **G1 passed:** all 43 printed 100 m labels in the new range sit on their
  calibrated line (contact sheets calib/jt_*_labels.png, checked visually (see Use of AI in the README)). The 10 m line spacing equals the nominal spacing in every
  sheet, so no sheet changes scale in this range.
- **Reader rules:** rules v3 unchanged plus
  results/v7/step3/reader_rules_jt_addendum.md. One decision in it matters
  for Y: the Exlog "silty sandstone" cell symbol (a dot above a dash) is
  read as `sand` (the legend names it a sandstone); siltstone stays `silt`.
  Readers note where they used it. **Sensitivity, declared:** Y = sand +
  silt.
- The cuttings column is drawn through the cored intervals on these sheets
  (probably from core chips). Readers read it; the bags inside Sodir cored
  intervals are excluded by the mask, as declared.
- Reader A: one folder per well. Reader B: seeded 20 % per well (at least
  2 tiles). Stage 1 = 34/4-6, 34/7-4, 34/7-9; then the futility check.
- **After the review's check of the addendum (2026-11-12, before any tile
  was read):** silty sandstone gets its own reader class `ssst`. Primary Y
  = sand + ssst. Sensitivities: ssst counted as silt (Y = sand only), and
  Y = sand + ssst + silt. The addendum no longer says what to expect in
  these sections.

### D eligibility amendment (2026-11-12; after the labels were read, BEFORE any photograph was joined)
- **What happened.** All seven wells were read; G2 passes (283 intervals,
  Spearman 0.997, mean absolute difference 0.7 points). By the letter of
  rule C4 only three wells are eligible (34/7-10, 34/7-9, 34/8-3), because
  C4 asks for informative bags in at least 3 depth clusters more than 30 m
  apart. Below base Cretaceous sand is 35-80 % of the column and informative
  bags are nearly continuous, so a well whose informative bags span 600 m
  counts as one cluster. **By the letter no test of record exists.**
- **What was known when amending:** the labels, reader agreement, and the
  label-against-Si/Al futility values of the first three wells read
  (34/4-6 +0.25, 34/7-4 +0.53, 34/7-9 +0.50). No photograph had been joined.
  The photograph predictions were frozen in commit d9543df. A positive
  result is expected from step 1.
- **Amended rule (review's wording):** at least 30 bags with Y; at least
  15 informative bags (|high-passed Y| >= 0.05); informative bags in at
  least 3 distinct 30 m bins on a fixed grid from 0 m MD, spanning at least
  90 m. Six wells qualify (all but 34/4-7, which has 17 labelled bags
  because its scan is faded). 34/8-3 A (44 bags) is flagged as small.
- **Status: amended, exploratory test.** Not "pre-specified": the rule
  changed after the label-against-Si/Al values of two of the wells it adds
  were known.
- **Pass** only if both the six-well version and the five-unit version
  (34/8-3 and 34/8-3 A merged by the plain mean of their two rho) reach
  p < 0.05 and median >= 0.10. The G3 rules still apply. The three
  by-the-letter wells are shown beside it.
- **Other changes made before scoring, both label-free:** reader blocks are
  clipped to the tile; bags inside a 10 m grid interval whose pixel height
  differs from the sheet median by more than 5 % are excluded (10 bags: the
  foot of the 34/7-9 log, and one paper seam each in 34/4-6 and 34/4-7).
