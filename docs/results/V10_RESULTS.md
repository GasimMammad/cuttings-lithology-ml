# v10 results: photo stratigraphy (S) and the step response of cuttings (R)

Plan: V10_PLAN.md with the review amendments (0925a5d). Each part was
run once, with code committed first (70_v10_strat.py de44ec2 plus one label
fix found in a label-only smoke test before the run; 71_v10_step.py
2a1b808). Result files: results/v10/. Both parts are new tests on wells
that were all used before.

**In one line: S is a negative result and R is inconclusive.**

## S. Can photographs place the major tops in an unseen well? No, not as well as an offset well

Reference: Sodir group tops. Four boundaries, 34 evaluated tops in 10 wells
(10 locations; 34/8-3 A descriptive). Leave one location out. The photo
model gets no depth.

| estimator of the top | median error, 34 tops | median of the 10 location medians | tops within 30 m |
|---|---|---|---|
| **Photographs** | **65 m** (9 bags) | 72 m | 29 % |
| Offset well (nearest other location, median 3.4 km away) | 43 m | 35 m | 44 % |
| Regional prognosis (median depth below sea floor) | 50 m | 46 m | 26 % |
| Measured XRF chemistry, same method (reference) | 52 m | 74 m | 41 % |

**Pre-declared tests (paired one-sided Wilcoxon over the 10 locations).**
- **S2, primary: photographs are worse than an offset well.** The photo
  error is smaller in 2 of 10 locations; p (worse) = 0.019; median paired
  difference +29 m.
- **S1, secondary: not shown to be better than a regional depth prognosis
  (n = 10 locations, two areas, all used before).** Smaller in 3 of 10;
  the test in the other direction gives p = 0.042.

Per location, median error in metres (photo / offset / regional): 24/9-3
430 / 102 / 432; 24/9-4 935 / 58 / 491; 34/4-6 41 / 50 / 83; 34/4-7 48 /
36 / 37; 34/7-1 52 / 17 / 43; 34/7-10 91 / 19 / 49; 34/7-4 52 / 35 / 35;
34/7-6 250 / 9 / 8; 34/7-9 39 / 17 / 44; 34/8-3 141 / 191 / 121.

Per boundary (10 primary wells):

| boundary | tops | photo median error | signed median (+ = too deep) | within 30 m | offset | regional | XRF |
|---|---|---|---|---|---|---|---|
| top Hordaland | 7 | 55 m (6 bags) | -15 m | 2 | 21 m | 50 m | 23 m |
| top Rogaland | 10 | 128 m (18 bags) | +51 m | 2 | 35 m | 33 m | 138 m |
| top Cretaceous | 9 | 80 m (22 bags) | +76 m | 1 | 17 m | 57 m | 43 m |
| base Cretaceous | 8 | 25 m (8 bags) | -11 m | 5 | 65 m | 53 m | 21 m |

No top was left without a bag in the deeper unit; at one top (24/9-3 top
Hordaland) every bag was assigned deeper. Bag level: balanced accuracy
0.68 after segmentation, 0.60 for single bags; the Rogaland Group is the
unit that is lost (64 of 530 bags right). Every top is listed in
results/v10/S_tops.csv.

**Casing and mud diagnostic (pre-declared).** Eight tops have a casing
shoe or a mud-system change within 70 m: seven are top Cretaceous and one
is base Cretaceous (34/7-10). At seven of the eight the photo pick is
closer to the shoe or change than to the true top, and no closer to the
true top than the shoe itself would be (the exception is 34/4-7).
**By the rule: at these tops the picks cannot be separated from casing or
mud changes.** The top Cretaceous picks are 76 m too deep in the median,
at the nine top Cretaceous tops. At the seven near ones the 13 3/8" shoe lies
14 to 67 m (median 44 m) below the top: four picks fall 8 to 28 m below the
shoe, two overshoot it by 66 and 222 m, and one (34/4-7) lies 34 m above
it. On the 26 far tops alone: photo
56 m; S2 still "worse than an offset well" (2 of 10, p 0.049); S1 not
shown to be better (3 of 10).

34/8-3 A (descriptive, MD): errors 70, 254, 986 and 93 m.

### Reading

1. The photographs do not place major tops as well as the nearest well
   does. In this densely drilled area the nearest well is 1.9 to 6 km away
   for nine of ten locations, and its tops are a hard baseline. For one
   top (24/9-3 top Cretaceous) the offset well is 34/7-10, 228 km away,
   because 24/9-4 did not reach the Cretaceous (per the amended rule).
2. The shortfall is not specific to the photographs. Measured XRF
   chemistry, through the same method, is also worse than the offset well
   (smaller error in 3 of 10 locations; post hoc, p = 0.014). Per location
   it cannot be told apart from the photographs (photo smaller in 5 of
   10). Per top it is somewhat closer (52 against 65 m; 41 against 29 %
   within 30 m). Whether the limit lies in the method or in the bags is
   not tested.
3. The two 24/9 wells fail outright (430 and 935 m). They are the other
   area, their Rogaland Group is thick and sandy where Tampen's is thin
   and clay-rich, and 24/9-4 covers only two units, which shifts its
   per-well z-score. With 24/9-3 held out, the model has one 24/9 well to
   learn from, and the reverse.
4. Base Cretaceous is the one boundary where the photographs do well
   (median 25 m, 5 of 8 within 30 m). Post hoc count, not a test: the
   photo pick is closer than the offset well at 6 of 8 (a sign test would
   give p = 0.14). This is the unconformity, where the offset well is
   weakest (65 m; regional 53 m). The picks are within 30 m in three of
   the four wells with Hegre Group directly below the unconformity (the
   fourth, 34/4-7, is 51 m off), and in 34/8-3 (Viking then Brent below)
   and 34/7-4. The two large misses (34/7-10 and 34/7-6, 199 and 250 m)
   have Dunlin Group directly below. Measured chemistry does the same
   overall (21 m).
5. Near tops are almost all one boundary (7 of 8 are top Cretaceous, and
   every Tampen top Cretaceous is near a 13 3/8" shoe), so a shoe effect
   cannot be separated from the boundary type. Four picks sit just below
   the shoe. This is consistent with a casing or mud imprint (or with
   cavings stopping at the shoe), but it is not direct evidence for one.
6. Limits: eleven wells, two areas, all used before; Sodir tops have their
   own error; bags 3 to 10 m apart; mud-system changes are known for six
   wells only (shoes for all); the dynamic programme assumes no unit is
   missing between the first and last unit of a well; a top picked from
   photographs is a change in the look of the cuttings, not an age.

**What may be said:** "Photographs cannot replace an offset well for
placing major tops. At the base Cretaceous unconformity the median photo
error was 25 m (5 of 8 tops within 30 m; two misses of about 200 and
250 m), close to the bag chemistry (21 m); this boundary was singled out
after the results and is descriptive."
**What may not be said:** that photographs pick formation tops, or that
they beat any depth prognosis.

## R. How fast do cuttings register a sharp gamma-ray step? Not measurable with these data

Steps were chosen from gamma ray alone: 80 found in 10 wells; 40 were not
sharp, 7 near a casing shoe, 7 outside the photographed range, 2 cored;
**24 kept, in 9 wells** (24/9-3 6, 34/4-6 5, 34/7-4 5, 34/7-9 2, 34/8-3 2,
one each in four wells). After the bag-count and contrast rules each stack
holds 11 to 14 steps from 5 or 6 wells.

| variable | steps (wells) in stack | lag | 10-90 % width W | 95 % interval of W | noise-matched ideal W0 | W - W0, 95 % interval |
|---|---|---|---|---|---|---|
| ideal bag (gamma ray over the bag interval) | 14 (6) | +2 m | 5 m | 0.4 to 26 m | - | - |
| measured Si/Al | 12 (6) | +3 m | 14 m | 0.4 to 39 m | 4 m | -59 to +28 m |
| measured K | 11 (6) | -10 m | 44 m | 0.4 to 87 m | 2 m | -28 to +85 m |
| photo prediction of Si/Al | 12 (5) | -1 m | 18 m | 0.4 to 31 m | 3 m | -56 to +27 m |

Fitted amplitudes are 1.02 to 1.18. Photo against Si/Al on the 9 common
steps: 20 m against 16 m; W_photo - W_Si/Al interval -28 to +21 m.
10 of the 8,000 bootstrap fits of W failed.

**By the pre-declared rules:** smearing is not detected for any variable
(every interval of W - W0 includes zero), and the photographs are "as fast
as the chemistry" (the interval includes zero). The pre-declared sentence
"The stacked transition is W m wide ..." is not used: the lower end of
every W interval (0.4 m) is the fit's minimum width, so the intervals are
set by the fit bounds.

### Reading

1. **These sentences are true by the rule and empty in content.** The
   intervals run from under a metre to tens of metres. With 12 steps from
   6 wells the stack cannot tell 5 m from 30 m. R gives no number for the
   resolution of cuttings, and none may be quoted.
2. The point estimates are in the table for completeness only. The
   bootstrap medians of W - W0 (4 m for Si/Al and for the photo
   prediction, 18 m for K) lie inside intervals about 85 m wide and show
   no direction.
3. Why it fell short: 40 of the 80 steps failed the sharpness rule. The
   rule also rejects about a quarter of perfectly sharp steps, because the
   step statistic locates a step only to about +/-15 m (review's
   synthetic check), so "not sharp" does not mean gradual. Of the 24 kept
   steps, 10 to 13 failed the bag-count or contrast rules. Loosening the
   rules now would be tuning after the result, so it was not done.
4. The earlier evidence on this question stands unchanged: bag support at
   the bottom of the interval (v3b), agreement that follows the spread of
   the chemistry (v8 B), and the gamma-ray key of v9 K3, where sand
   fraction and Si/Al reach only -0.14 to -0.26 against gamma ray.
5. The photo pipeline is not independent of gamma ray (v1, v2).

## What v10 adds to the thesis

- A clear limit, tested against an independent reference: zone-scale
  signal does not make the photographs a stratigraphic tool. An offset
  well is better.
- One place where they do carry usable information: the base Cretaceous
  unconformity (descriptive).
- Picks at top Cretaceous that cannot be separated from the 13 3/8" shoe.
- No resolution number. R should be repeated only with more wells, with
  the rules of V10_PLAN unchanged.

## Review (v10 results): accepted with changes for S and R, applied

Every number was recomputed from the result files; no code bug that changes
a verdict (labels without gaps, twins kept together in the folds, dynamic
programme correct, depth conversions as amended). Changes applied above:
the offset distances stated exactly, the casing paragraph and Reading 5
toned down from "direct evidence" to "cannot be separated", Reading 2
replaced by what was tested, the base Cretaceous note made exact, and in R
the point estimates demoted, the sharpness explanation corrected and the
pre-declared width sentence withdrawn because the intervals hit the fit
bounds.
