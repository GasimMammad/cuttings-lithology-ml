# v10 plan: photo stratigraphy and the resolution of cuttings (written 2026-11-12, before any of it is run)

User instruction (2026-11-12): "do whatever you think will be the best and
the most useful for our project". Of the four ideas put to the user, two
are taken up here because they need no credits and use an independent
reference: photo stratigraphy (S) and the step response of cuttings (R).
The zero-shot AI reader (costs credits) and the parentage test (high risk
from cavings) are not done.

v7 to v9 are closed and unchanged. Order of work: this plan committed ->
reviewer -> code committed -> run once -> reviewer. Both parts are new
tests on wells that were all used before; neither is a fresh hold-out.

## Why these two

Every earlier round ended on the same limit: the photographs carry signal
at the scale of zones, not beds. S asks whether that scale is useful as it
is: can photographs place the major stratigraphic boundaries in a well the
model has never seen? R asks where the limit comes from: how many metres
does a bag need to register a sharp boundary that the wireline tool saw?

## S. Photo stratigraphy: major tops in an unseen well

**Reference (independent of every AI reader and of the photographs).**
Sodir lithostratigraphy, group level, downloaded 2026-11-12 for all 11
wells (saved with the results). Five units in fixed order:

0. Nordland Group
1. Hordaland Group
2. Rogaland Group
3. Cretaceous (Shetland and Cromer Knoll Groups)
4. below base Cretaceous (Viking, Brent, Dunlin, Statfjord, Hegre)

Four boundaries: top Hordaland, top Rogaland, top Cretaceous, base
Cretaceous. A bag at depth D belongs to the unit that contains D.

**Tops that are evaluated (counted from labels only, before any model):**
a boundary inside the photographed range with at least 10 bags of the unit
above and 10 of the unit below. This gives 34 tops in 10 wells.

**Folds.** Leave one location out. 34/8-3 and 34/8-3 A are one location
and are always held out together. The primary comparison uses 10 wells =
10 locations; 34/8-3 A (deviated up to 25 degrees, depths in MD) is
evaluated descriptively only, and is never used as an offset well.

**Photo model (the R-D feature pipeline, unchanged).** ResNet-50 bag
embeddings, z-scored per well over all its photographed bags (no labels),
StandardScaler, PCA 32, then multinomial logistic regression (C = 1,
class_weight balanced) on the five units. No depth is given to the model.

**From bag probabilities to tops.** In the held-out well the bags are
sorted by depth. The unit sequence that maximises the sum of log
probabilities is found by dynamic programming under one constraint: going
down, the unit stays the same or moves to the next one. The well may start
and end in any unit. The predicted top of unit k+1 is the midpoint between
the last bag assigned to unit <= k and the first bag assigned to a deeper
unit. If no bag is assigned deeper, the top is put at the deepest bag; if
all are deeper, at the shallowest bag.

**Error.** Absolute difference in metres between predicted and Sodir top.
Per location: the median over its evaluated tops.

**Baselines (no photographs).**
- Regional prognosis: the median depth of that top in the other locations
  (34/8-3 A not used).
- Offset-well prognosis: the depth of that top in the nearest other
  location (UTM distance from the Sodir wellbore table). This is the hard
  baseline: five of the wells lie within a few kilometres of each other.

**Tests (paired one-sided Wilcoxon over the 10 locations, on the
per-location median error) and wording fixed now.**
- S1, primary: photographs against the regional prognosis. p < 0.05:
  "photographs place the major tops in an unseen well better than a
  regional depth prognosis". Otherwise: "no better than a regional depth
  prognosis".
- S2: photographs against the offset-well prognosis. p < 0.05: "better
  than an offset well". If the test in the other direction gives p < 0.05:
  "worse than an offset well". Otherwise: "not distinguishable from an
  offset well (n = 10)".
- Always reported with the words: median error in metres and in bags, per
  boundary; the share of tops within 30 m; every top listed.

**Casing and mud confound (the main threat).** Casing points and mud
changes are often placed near stratigraphic boundaries (top Cretaceous is
14 to 67 m from the 13 3/8" shoe in most Tampen wells), and the photographs
are known to see mud residue. Pre-declared diagnostic: tops are split into
"near" (a casing shoe or a Sodir mud-type change within 50 m of the true
top) and "far". Reported: median photo error in each group, and for near
tops whether the pick lies closer to the true top or to the shoe or mud
change. Wording: if the far-group median error is more than twice the
near-group median error, the result is written as "the picks are helped by
casing or mud changes" and S1 is restated on the far tops only.

**Reference rows (descriptive, same dynamic programme).**
- measured XRF chemistry (log ratios of Si, K, Fe, Ca, Ti, Zr, Sr over Al,
  z per well; bags without XRF dropped): what a measurement on the same
  bags achieves;
- the 15 colour and texture features;
- embeddings without the per-well z-score;
- bag-level balanced accuracy and confusion matrix of the photo model;
- 34/8-3 A.

**Not done on purpose.** No combination of photographs with a depth prior
(it needs a prior width, a free choice). No tuning of C, of the PCA size or
of the constraint. No formation-level tops.

**Limits to state with any result.** Eleven wells, two areas, all used
before. The Sodir tops were picked by people from logs, cuttings and
biostratigraphy, so "truth" has its own error of metres to tens of metres.
Bags are 3 to 10 m apart. The per-well z-score depends on which units a
well's photographs cover. A top picked from photographs is a change in the
look of the cuttings; it is not a stratigraphic age.

## R. Step response: how fast do cuttings register a sharp boundary?

**Idea.** The wireline gamma-ray curve shows where the formation changes
sharply. At each such step, the bags above and below give two plateaus.
Scaled so that the upper plateau is 0 and the lower plateau is 1, the bags
in between trace how the cuttings cross the boundary. Stacked over many
steps this is the step response of the cuttings system. The same stack for
gamma ray averaged over each bag's own interval is what an ideal bag would
show.

**Steps (chosen from gamma ray only; no cuttings data used).** For each of
the 10 wells with a gamma-ray curve, on the curve smoothed with a 5 m
running median: s(z) = median over [z, z+30 m] minus median over
[z-30 m, z]. A step is a local maximum of |s| with |s| >= 1.0 robust SD of
the well's curve (1.4826 x MAD), at least 80 m from any stronger step, and
sharp: at least half of the change happens within +/-5 m of z. Excluded:
steps within 60 m of a casing shoe, inside a cored interval, or outside the
photographed range.

**Cuttings variables.** Measured z log10(Si/Al) (primary) and log10 K
(secondary), and the photograph prediction of Si/Al (step 1 held-out
predictions in the Tertiary, the pre-Tertiary model below it; each used
only inside its own range).

**Per step.** Upper plateau: bags 20 to 60 m above. Lower plateau: bags 20
to 60 m below. Needs at least 4 bags in each plateau and at least 4 bags
between -20 and +40 m. A step enters a variable's stack only if that
variable's plateau difference is at least 1.0 pooled SD of the plateau bags
(a transition cannot be measured without contrast; this rule uses the
plateaus only, never the bags in between). Each variable is scaled 0 to 1
by its own plateau means.

**Stack and fit.** All scaled bags against x = bag depth minus step depth,
-60 to +60 m. A logistic step y = 1 / (1 + exp(-(x - x0) / w)) is fitted by
least squares. Reported for the ideal bag, measured Si/Al, K and the photo
prediction: lag x0 (m), 10-90 % width (4.39 w, m), number of steps and
wells, and 95 % intervals from a bootstrap over wells (2,000 resamples).

**Wording fixed now.** No pass or fail; R is a measurement.
- "Cuttings register a sharp boundary over about W m (10 to 90 %), against
  W0 m for an ideal bag."
- "Beds thinner than about W m cannot be resolved by any method that works
  on these bags" only if the lower end of the 95 % interval of W is above
  the upper end of the interval of W0. Otherwise: "no smearing beyond the
  bag length is detected".
- Photographs: "as fast as the chemistry" if the intervals of the photo
  and the measured widths overlap; otherwise slower or faster, with the
  numbers.

**Limits to state.** A gamma-ray step is not always a Si/Al step (hence
the contrast rule, which also selects the clearest boundaries). Driller's
and logger's depths differ by metres. The lag includes the convention that
a bag is labelled with the bottom of its interval. Ten wells; steps within
a well are not independent, which is why the bootstrap resamples wells.
The contrast rule and the windows (30 m, 20 to 60 m, 80 m) are choices made
here once and not tuned.

## Order

S and R are independent. Each is scored once. If the reviewer asks for a
change after results, it is reported as post hoc.
