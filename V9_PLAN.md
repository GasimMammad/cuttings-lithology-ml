# v9 plan: three checks that close open caveats (written 2026-11-12, before any of it is run)

v8 is closed and unchanged. Nothing here is a new headline test. Each part
either removes a caveat or states that it stands. All parts are
EXPLORATORY and are labelled so wherever they are quoted. Order of work for
every part: this plan committed -> reviewer -> code committed -> run once
-> reviewer.

User decisions (2026-11-12): no human key will be made (the user will not
read the audit tiles); no new well is available; presentation work waits.

## K1. Was an iron-titanium weighting agent used? (the ilmenite caveat of v8 A)

**Question.** v8 A found that photographs predict Fe/Al and Ti/Al. The
Ba/Ca/Cl controls do not cover ilmenite (FeTiO3) or hematite used to weight
the mud. Do the well documents say which weighting material was used?

**Sources (read-only, /Volumes/T9/.../Wells/<well>/).** For each of the 11
wells: every PDF in DRILLING (drilling programme, drilling report, drilling
fluids report, mud-log report) and the completion report in WELL. Also the
Sodir mud table already saved (results/v8/sodir_mud_table.csv).

**Method.**
1. Text layer where one exists (PyMuPDF); search for: ilmenite, hematite,
   haematite, iron oxide, barite, baryte, barytes, weight material,
   weighting, mud materials, mud consumption, and Norwegian equivalents
   (ilmenitt, baritt, vektmateriale).
2. Scanned reports without a text layer: pages of the mud / drilling-fluid
   sections and the materials-consumption tables are rendered and read by
   one AI reader (sonnet), who records well, document, page, hole section,
   mud system, weighting material and the quoted phrase. The reader is told
   to write "not stated" when a page does not name the material, and never
   to infer it from the mud weight or the year.
3. I open every page the reader cites and confirm the quoted phrase before
   it is counted.

**Outcome per well:** "barite stated", "iron-titanium weighting material
stated (which, which hole section)", or "not stated in the documents on
hand".

**Pre-declared consequences (no model is refitted).**
- Iron-titanium material stated for any well or section: v8 A's Fe/Al and
  Ti/Al rows are re-scored from the saved per-well values without those
  wells, and both versions are reported. The Fe-Ti axis is then worded as
  "may partly reflect the weighting agent in wells X".
- Barite stated for all wells with a statement and no iron-titanium
  material anywhere: the caveat is reworded to "the documents on hand name
  barite only (n wells); n wells have no statement".
- Fewer than 6 of 11 wells with any statement: the caveat stays as it is,
  with the count.
- A document statement says what was planned or bought, not what was in a
  given bag. This is said with the result.

## K2. Do the results depend on the sidetrack being in the training data?

34/8-3 and 34/8-3 A are one location. With one held out, the other is in
training.

**K2a. Main Si/Al result (step 1).** Already done in v7: leave-one-area-out
gives +0.31, 10 of 11 (V7_RESULTS.md step 1). Nothing is run. The sentence
is added where the twin is discussed.

**K2b. Deep mud-log test (v8 D).** The pre-Tertiary R-D model of D is
refitted with two other fold schemes, nothing else changed (same bags, same
labels, same high-pass, same six wells of the amended test):
- location-out: 34/8-3 and 34/8-3 A held out together;
- area-out: 34/4, 34/7, 34/8 (and 24/9 where present) held out as blocks.
Reported for each: per-well rho against the sand fraction Y, median, wells
above zero, one-sided Wilcoxon p, and the five-unit (twins merged) version.
Wording, fixed now: "does not depend on the twin" if the location-out
median is >= +0.40 with all six wells positive; otherwise "depends in part
on the twin being in training", with both numbers. Area-out is descriptive
(it leaves as few as four training wells).

**K2c. Fine-tuned network at 34/8-3 (v8 C).** The 34/8-3 fold is retrained
with 34/8-3 A removed from training, and the 34/8-3 A fold with 34/8-3
removed. Seeds 0, 1000 and 2000 with the same fold seed as before (SEED +
offset + fold index 9 and 10), so only the training set changes. Six folds,
about 2 h of GPU. The frozen ResNet-18 control and R-D are refitted with
the same wells removed (seconds).
- Reported: per-seed rho for both wells with and without the twin, mean of
  three, and the two frozen models with and without the twin.
- Wording for 34/8-3, fixed now: mean of three seeds >= 0.15 and all three
  above zero: "the 34/8-3 observation does not depend on the sidetrack
  being in training". Mean below 0.15: "it depends on the sidetrack being
  in training". Anything else: "unclear".
- The seed SD at this well is 0.10, so a change smaller than about 0.2
  between with and without is within seed noise and is said to be so.
- One well, singled out after X1. No p value is attached.

## K3. Gamma-ray key for the digitised mud-log labels (in place of a human key)

**Why.** No human key exists and none will be made. Three AI readings
agree, which shows consistency. Wireline gamma ray is an instrument
record, independent of the AI readers and of the photographs. It can show
whether the digitised sand fraction follows the formation. It cannot show
that a given percentage was read correctly, and it does not replace a human
key. The limitation "no human key" stays in every write-up.

**Sets.** (i) v8 D: the six wells and the bags of the amended test.
(ii) v7 step 3: the six Tertiary wells and bags of its test of record.
No bag is added or removed. Bags without gamma ray drop out and are counted.

**Statistic.** Per well, Spearman between the high-passed sand fraction and
the high-passed gamma ray at the bag depth (the `gr` column of the base
table: the wireline curve interpolated at the bag depth, script 03). Same
high-pass and same stretch splitting as each test used. Expected sign:
negative. One-sided Wilcoxon across wells, bootstrap CI of the median.

**Wording, fixed now, for each set separately.** "The digitised sand
fraction follows gamma ray" if the median is <= -0.20 and p < 0.05.
Otherwise "no detectable agreement with gamma ray", with the numbers.

**Reference rows (descriptive, same bags):** measured Si/Al against gamma
ray (what a measurement on the same bag achieves); the photograph
prediction of each test against gamma ray. These are context for the key,
not new tests of the photographs.

**Limits stated with the result.** Gamma ray is not sand: mica (Rannoch
Formation), potassium feldspar and heavy minerals raise it in sandstone.
A bag covers 3 to 10 m and is lagged; the gamma ray is a point value at the
bag depth. The percentage column is drawn at the wellsite before wireline
logs exist, but later redrafting cannot be excluded from the sheets alone.
Agreement supports the whole chain (wellsite geologist, sheet, reader, bag
join) and not the reader alone.

## Not in this plan

Ideas put to the user on 2026-11-12 and waiting for a decision: photo
stratigraphy against Sodir formation tops; a zero-shot AI reader of the bag
photographs; the resolution limit of cuttings from gamma ray against XRF
potassium; a parentage test for the target sands. Each would get its own
plan and review.
