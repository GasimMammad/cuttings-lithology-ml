# v4 plan (2026-11-05), revised after review round 6. Nothing below has been computed.

v2 and v3 stand as reported. v4 adds bed-scale ground truth that does not
come from gamma ray: core photographs. The asymmetry is stated in advance:

- a **positive** image result means photographs can resolve beds where the
  bags represent the rock;
- a **negative** image result is uninterpretable on its own (different domain:
  consolidated Triassic/Jurassic red beds; core-head cuttings; trip cavings).

The thesis-relevant output is the **resolution ceiling of cuttings at about 3 m**,
reported for XRF, weight, colour and images side by side.

## A. Core-photo bed-scale test

### A1. Data

- Cores in seven wells contain cuttings bags: 34/4-6, 34/4-7, 34/7-1,
  34/7-9, 34/7-10, 34/8-3, 34/8-3 A. 247 white-light core photographs
  (CORE_PHOTO_M_TOP*_W_1) overlap those bags.
- The W2/W3 core photographs (likely white-light/UV pairs) are NOT shown to
  digitisers, because UV fluorescence biases toward sand.
- 24/9-3 and 24/9-4 (Tertiary cores, few bags) are reported descriptively only.
- **Disclosure:** the 34/7-1 cores (2394-2623 m) overlap the v1 mud-log probe
  depths (2417-2600 m), whose predictions were seen in v1.

### A2. Core digitisation

- **Bins:** 0.25 m along each 1 m tray, depths from the printed tray
  labels.
- **Classes:** SAND / HET (heterolithic or uncertain, incl. red siltstone vs
  very fine red sandstone) / MUD / OTHER (coal, carbonate or cemented bed) /
  NONE (no core, rubble, gap).
- **Per bin also recorded:** colour (RED / GREY-GREEN / OTHER) and confidence
  (high / low).
- **How to read:** judge the rock, not the plug holes. Rubble = NONE. Core
  loss = NONE at the bottom of a run (standard convention), checked against
  tray depths.
- **Raters:**
  - A: Claude Opus agent, all photos.
  - B: Claude Sonnet agent, all photos.
  - C: Claude Fable agent, a random 20% of photos.
  - All are blind to GR, cuttings photographs, XRF and every prediction.
  - They are not human raters. A human spot-check by the author is
    recommended before publication.
- **Agreement:** Cohen's kappa A-B on all bins; A-C and B-C on the subset.
- **Precision check:** plug permeability > 1 mD from the digital core-analysis
  files (24/9-3, 34/8-3, 34/8-3 A) should fall in SAND bins.

### A3. Target per bag

Core sand fraction over the bag interval:

  f = (SAND + 0.5 HET) / (SAND + HET + MUD + OTHER) bins

- **Primary:** the mean of raters A and B.
- **Sensitivity:** bins where A and B agree.
- A bag counts only if classified bins cover >= 50% of its interval.
- **Bag support:** (D - s + o, D + o], s = local bag spacing. The offset o is
  chosen by an XRF-only scan, o = -10..+5 m: the o that maximises mean
  high-passed rho(Si/Al, f); ties -> closest to 0.

### A4. Gate (model-free, before any image signal is scored)

- **Controls:**
  - high-passed rho(XRF Si/Al, f) > 0;
  - in Lunde/Statfjord red-bed cores, rho(redness, red-mud fraction) > 0,
    where redness = lab_a_mean of the photo and red-mud fraction = MUD
    bins coloured RED.
- **The image test is "informative" only if:** both controls are positive
  in >= 2/3 of the wells where they can be computed (>= 10 bags).
- **Trip-cavings sensitivity:** drop the first bag after each core-run top.
- **Core-chip check:** flag wells where bags inside cores sit at ~1 m
  spacing or show slab-like chips; report them separately.

### A5. Image test (only if the gate passes; reported either way)

- **Signals,** never trained on the well: ONE_FEATURE (primary), D1, E2.
  34/7-1 uses models trained on all 10 labelled wells.
- **Primary:**
  - per well, Spearman rho(signal, f) after both are high-passed (minus the
    centred running median over +/-15 m);
  - one-sided Wilcoxon over wells with >= 10 qualifying bags.
- **Baselines (same statistic):** colour (-lab_a_mean, sign fixed a priori:
  less red = sandier), XRF Si/Al, bag dry weight.
- **Secondary:** unfiltered Spearman (interval scale); AUC of bags with
  f >= 0.7 against f <= 0.1.
- No GR reference: GR is in wireline depth and would need a core-to-log
  shift that is not available.

## B. Cement mask (robustness only)

Rerun of the section-3 shallow XRF test (V3_PLAN.md), excluding photographs
0-15 m below every 30", 20" and 13 3/8" shoe. ONE_FEATURE primary. Run 2
stays the reported result. This is only a robustness check.

## C. 34/7-1 mud log: dropped

It is not blind and has low power. Two agents reading a 1984 scan add little
(review round 6).

## D. Fine-tuned CNN (running, exploratory)

C1/C2 leave-one-well-out. Selects nothing. Reported alongside the others.
