# v7 plan: sample-matched targets

The user's order: (1) photos predict cuttings chemistry, then (2) a photo
glauconite detector, then (3) mud-log lithology labels. This file fixes
step 1; steps 2 and 3 get their own sections before they run.
Status: exploratory; the same wells were used before.

**Step 1 status:** FINAL (reviewer round 15: APPROVE WITH CHANGES, applied), merging:
- the draft (e0588e9);
- reviewer round 14;
- Agent 2 (geochemist, `v7/agent2_target_notes.md`);
- Agent 4 (ML/CV, `v7/agent4_notes.md`).

No photo-to-chemistry skill has been computed by anyone. The agents looked
only at chemistry against chemistry, GR, EXIF and the v6 G table.

## Step 1: can cuttings photographs predict the chemistry of the same bag?

**Why:** GR labels measure the formation at a point; the photograph and the
XRF measure the same bag. All 5,038 W_1 photographs in 11 wells have a
matched XRF analysis, against 590 GR labels.

### Data selection (fixed before computing)
- **Tertiary only:** depth < TOP_SHETLAND[well] (35_v3_xrf_shallow.py).
  The pre-Tertiary is reported separately, descriptively.
- **Exclude bags 0-15 m below every 30", 20" and 13 3/8" shoe** (Sodir
  casing table; the same mask as 42_v4_cement_mask.py).
- Bags with no XRF Si or Al are dropped.
- **Normalisation set:** every per-well z-score (inputs AND targets) uses this same
  Tertiary, shoe-masked bag set (not all photos as in v2).
- Bags with Al below the well's 5th percentile are kept in the primary and
  excluded in sensitivity S-Al.

### Targets
- **T1 (primary): z_well(log10(Si/Al)), uncorrected.**
  - Barite dilution scales Si and Al equally, so the ratio already cancels
    it (Agents 2 and 4 agree). The round-14 Theil-Sen Ba correction moved
    local agreement with GR Vsh the wrong way (median local rho -0.19
    uncorrected vs -0.15 corrected, 8 wells; Agent 2).
  - Disclosure: the target was chosen after a chemistry-vs-GR check (no photo
    skill seen); the difference was small (-0.19 vs -0.15; partialled -0.16).
  - Name: "detrital quartz + biogenic silica vs clay", not "sand".
    Oligocene ooze is biosiliceous.
- **T1 sensitivities:**
  - T1-TS: Theil-Sen Ba-corrected, with the slope clipped at 0.
  - T1-P: a partial Spearman controlling high-passed log Ba, log(Ca/Al) and
    log Cl.
- **T2 (secondary): z_well(log10 Ca), Ba-partialled (Theil-Sen).**
  - It captures shell and foram debris, carbonate cement and calcareous
    mud, as well as gypsum, lime and cement additives.
  - Report rho(Ca, S) per well as a gypsum flag.

### Inputs and models (existing features, unchanged)
- **R-D (primary):** ResNet-50 RGB embeddings, per-well z ->
  StandardScaler -> PCA 32 -> Ridge (alpha = 1). Fitted on training wells
  only. Kept for continuity with v2.
  (alpha chosen per outer fold for R-RAW is reported.)
- **R-RAW (pre-declared alternative):** raw 2048-d per-well z -> Ridge,
  with alpha chosen from {1, 10, 100, 1e3, 1e4} by inner LOWO on the
  training wells (median per-well high-passed rho), and equal well weights.
- **R-E (secondary):** the 15 engineered features, per-well z -> Ridge
  (alpha = 1).
- The alpha = 10 sensitivity from round 14 is dropped: on 32 PCs it is
  effectively OLS (Agent 4); R-RAW replaces it.

### Validation
- Leave-one-well-out over all 11 wells (primary).
- Leave-one-area-out as a stress test: 24/9 (2), 34/4 (2), 34/7 (5),
  34/8 (2). Leaving out 34/7 trains on 6 wells.
- Note: 34/8-3 and 34/8-3 A are near-twins, so LOWO is mildly optimistic
  for them.

### Primary endpoint
- **High-pass:** per held-out well, predicted and measured T1 are each
  high-passed by subtracting the centred running median over +/-50 m
  within continuous stretches (gaps > 30 m split; highpass() in
  35_v3_xrf_shallow.py).
- **Statistic:** the per-well Spearman rho of the two high-passed series.
  Sign: POSITIVE rho (predicted vs measured T1) = skill.
- **Test:** one-sided Wilcoxon of the 11 per-well rho against 0.
- **Interval:** a well-bootstrap 95% CI of the median rho.
- **Positive result:** "photos carry local chemical information" only if
  p < 0.05 AND median rho >= 0.10 (the effect-size floor).
- **Not-mud condition:** "not riding on barite/mud" may be added only if T1-P has
  the same sign with median partial rho >= 0.05; otherwise the claim is "photos
  predict Si/Al, possibly via mud residue".

### Per-well null and checks
- **Circular-shift null:** within each continuous stretch (gaps > 30 m split;
  no wrap-around across gaps), the high-passed prediction is circularly shifted
  against the target by every offset >= 10 bags (stretches < 30 bags excluded
  from the null). The per-well p is the rank of the observed rho.
  Shuffling is invalid because lag-1 autocorrelation after the high-pass
  is 0.06-0.76. Per-well p are descriptive; a Fisher combination is a
  SECONDARY test.
- **Lag profile:** rho of photo k against chemistry k+m for m = -5..+5.
  Shown against the no-skill curve rho(0) x ACF_T1(m). "Same bag" evidence =
  rho(0) clearly above that curve's shoulders, not merely a peak at m = 0.

### Sensitivities (reported, not tested for the claim)
- High-pass windows of +/-25 m and +/-5 bags.
- T1-TS, T1-P, S-Al.
- R-RAW and R-E.
- Leave-one-area-out.
- The unfiltered per-well Spearman.

### Baselines (same Tertiary series, same high-pass, paired Wilcoxon against R-D)
- Relative depth (expected near 0 after the high-pass).
- Bag dry weight, with the sign taken from the training wells.

### Leakage and negative controls
- **Photo -> Ba:** the same R-D pipeline with target z log10 Ba. If photos
  predict Ba much better than Si/Al, the barite coating is a channel; this
  is read together with T1-P.
- **High-passed Ba and Cl against prediction:** within-well rho.
- **Pipe-dope negative control:** residual Zn + Pb after regressing out
  Si/Al and Ba. Photos should NOT predict it (|median rho| < 0.10
  expected). Because barite carries Zn/Pb impurities, Zn+Pb are regressed on Ba
  first; a failure of this control is AMBIGUOUS, not proof of leakage.
- **Capture sessions (always run):** EXIF capture times -> session ids; high-pass
  within sessions as a sensitivity; reshoot test in 34/7-10. Run regardless of
  the primary outcome.

### Downstream (EXPLORATORY)
- The AUC of predicted T1 for the v2 GR sand/clay labels (7 wells), next to
  the v2/v3 signals.
- Local AUC (< 50 m).

### Interpretation guard
- 34/7-6 is expected to run the wrong way (biosiliceous ooze vs a
  glauconite-bearing sand). It stays in; no well is dropped after seeing
  results.
- Expected photo-XRF |rho|: unknown, likely < 0.3.
- If leave-one-area-out collapses (e.g. without 34/7), it is reported next to
  the primary, not in an appendix.

## Step 2: photo glauconite-pellet detector. FINAL (round 17 amendments below take precedence); nothing run on G bags

- **Source:** Agent 4's frozen specification (`v7/agent4_step2_spec.md`, part A), copied verbatim below.
- **Target:** binary G > 0.2 (v6 exploratory G without the Al floor, validated by the blind pellet check).
- **Blindness:** parameters come from the mineralogy literature, the pixel scale and 12 Lunde Fm photos
  (Triassic, continental; no glauconite possible). No G-labelled photo was viewed.
- **Disclosure:** Agent 4 had read the text notes of the v6 pellet rater (pellet size and crack networks).

### A1. Input and geometry
- **Photos:** W_1 photographs (white light, 'standard' processing) only. U_1 (UV) and W_2 are never used.
- **Decoding:** full-resolution JPEG decode (6000 x 4000), with no draft or reduce.
  - **Scale:** 7.14 um/px (140 px per mm ruler tick, identical in all wells; PARTA2_scale_check.txt).
    The frame is 42.9 x 28.6 mm.
- **Analysed region:** the crop x 260-5980, y 260-3560 (the crop used by 04/26/16). It removes the
  digital ruler overlays (top and left) and the text label (bottom-left, y > 3600).
  - The region is 5720 x 3300 = 18.9 MP, which is 100% of the usable frame. No tiles are used.
- **Colour:** sRGB to CIELAB (D65, `skimage.color.rgb2lab`), in float32, processed in horizontal
  strips. Each channel is then smoothed with a Gaussian filter (sigma = 1.0 px) to suppress JPEG
  4:2:0 chroma blocking.
- **No colour normalisation** (absolute gates).
  - The camera, f/16, 1/8 s, ISO 200, manual white balance and 60 mm lens are identical in all
    wells (EXIF).
  - A per-well normalisation is a sensitivity only (A6).

### A2. Chip mask (the denominator)
- chip = L* >= 12 inside the analysed region. This excludes deep shadow and interstices.
- In the Lunde checks, chip pixels made up 99.5% of the region. The frame is fully covered with
  cuttings, and no tray background is visible.

### A3. Pellet colour gate (pixel level, applied to the smoothed L*, a*, b*)
| quantity | gate | why |
|---|---|---|
| hue angle h_ab = atan2(b*, a*) | 95 to 200 deg | Glauconite hue in rock-colour notation runs from 5GY (yellow-green) through 10GY and 5G to about 10G. In CIELAB that is roughly 100-180 deg. 95 deg leaves margin for the warm cast of this set-up: chip medians are a* +2 to +16, b* +15 to +33. 200 deg leaves margin for blue-green. |
| a* | <= -1.5 | Must lie on the green side of neutral. Under the warm cast, neutral grey renders a* of about +1 to +3. |
| chroma C* | 4 to 30 | Fresh, evolved glaucony is dark and only moderately saturated: Munsell chroma 1-4 is about C* 3-20. Below C* 4 the hue is noise. The upper bound of 30 allows for processing saturation and excludes vivid artefacts. |
| lightness L* | 15 to 50 | Glauconite is "dark green to greenish black", Munsell value 2-4, about L* 20-42. The upper bound of 50 leaves margin for glossy faces and excludes pale green-grey clay. In Lunde, green-grey mudstone pixels have a median L* of 47-78. |
- **Clean-up:**
  - Binary opening with a disk of radius 2 px (about 14 um). Use `scipy.ndimage.binary_opening`
    to avoid the deprecated skimage call.
  - Then fill holes of 30 px or less (specular highlights and light-green crack networks inside
    pellets).

### A4. Blob segmentation and shape gates (native resolution)
- **Touching pellets are split** by watershed:
  - on minus the Euclidean distance transform of the gate mask;
  - markers = `peak_local_max` with min_distance 7 px, threshold_abs 5 px, and labels = connected
    components.
  - Without splitting, an abundant greensand would merge into large components and be missed.
- **Accepted blob = all of:**
  | property | gate | in physical units |
  |---|---|---|
  | equivalent diameter d_eq = sqrt(4A/pi) | 14 to 72 px | 0.10 to 0.51 mm (fine to medium sand; the main glaucony size mode) |
  | solidity | >= 0.80 | admits ovoid and lobate (mammillated) pellets |
  | circularity 4 pi A / P^2 (skimage perimeter) | >= 0.50 | |
  | minor / major axis ratio | >= 0.40 | excludes slivers and edges of platy green mudstone chips |
  | blob mean L* | <= 45 | blob-level darkness |
  | blob mean C* | >= 5 | blob-level greenness |
- Vermiform (accordion) glaucony and pellets embedded in chips at under 0.1 mm are accepted
  losses; disclose them.

### A5. Per-photo scores
- **S (primary)** = number of accepted blobs per 10^6 chip pixels. 10^6 px is 51 mm^2, so
  S = 1 means about 19 blobs per frame.
- **S_area (secondary)** = accepted blob area / chip pixels.
- **Diagnostics** (written, not tested):
  - gate pixel fraction;
  - the number of candidates before the shape gates;
  - the area fraction of green components larger than 72 px (green chips);
  - the mean L*, a* and b* of chip pixels;
  - read and compute time.
- **Bag score** = the photo score (one W_1 photo per bag).

### A6. Pre-declared sensitivities (reported; the claim does not rest on them)
- L* upper gate of 45 and 55 (pixel), with everything else fixed.
- Per-well colour normalisation: subtract the per-well median a* and b* of chip pixels over ALL
  W_1 photos of the well (label-free), then apply the same gates.
- A glauconite-G threshold of 0.15 or 0.3 instead of 0.2.
- A conditional window of +/-120 m instead of +/-80 m.

### A7. Comparator: the existing green index (exact definition, v1/v2 code)
- Source: `16_green_index_all.py` (identical to `20_controls_34_7_6.py`, `12_glauconite_test.py`).
- **Decoding:** JPEG draft decode at 1/8 scale (about 750 x 500 px, so about 57 um/px; a pellet is
  only 2-9 px). The image is cropped at fractions (260/6000, 260/4000, 5980/6000, 3560/4000).
- **Colour:** `skimage.color.rgb2lab` on [0,1] float RGB.
- **GI** = the fraction of crop pixels with a* < -5.0 AND C* >= 12.0 AND 15 < L* < 80.
  The thresholds are FROZEN; their calibration is not reproducible (GLAUCONITE_CORRECTIONS.md
  item 6). No shape or size criteria are used.
- **Existing values:** `~/sinkite_ml_work/16_green_index_all.csv` holds 4,795 photos in 10 wells.
  - 34/7-6 is missing: only 10 depths are in `green_index_34_7_6.csv`.
  - **Action:** compute GI for all 34/7-6 W_1 photos with the unchanged `green_index()` function.
    This is needed only for the Lista and false-positive rows.
- Note: GI is saturated-green area at coarse resolution. It is not a pellet detector, so the
  comparison is "pellet morphology at native resolution vs green area".

### A8. Order of operations (blind protocol)
1. Commit this specification into V7_PLAN.md step 2, plus the detector script
   (`53_v7_pellet_blobs.py`) and the evaluation script (`53b_v7_pellet_eval.py`), BEFORE any run.
2. **Calibration run on G-free bags only:** all W_1 photos in the Lunde Fm of 34/4-6, 34/4-7,
   34/7-1, 34/7-4, 34/7-9 and 34/7-10 (1,022 photos).
   - Output: the distribution of S and tau_L = the 99th percentile of S over Lunde.
   - A montage of the 30 highest-S Lunde detections may be inspected (G-free) to catch CODE bugs.
   - **Parameters are not changed.** A suspected parameter problem is recorded and run as a
     labelled sensitivity; the primary stays as frozen.
   - Commit tau_L and the Lunde file hash.
3. **Score run:** S, S_area and the diagnostics for every W_1 photo of every bag with a defined G
   (7 wells, 926 bags, Lista included), plus GI for 34/7-6.
   - Written WITHOUT joining to G. Commit the score file and its sha256.
4. **Evaluation:** `53b` joins scores to G and runs A9 to A11 exactly.
5. Only after step 4 may anyone look at detections on G-labelled bags (montages, error analysis).
   Anything learned there is exploratory.

### A9. Primary test: conditional, inside +/-80 m of THGU
- **Analysis set:**
  - Bags with defined G (no Al floor) and |depth - THGU| <= 80 m.
  - THGU from the W table in `51_v6_xrf_glauconite.py`.
  - From the G table: 92 bags in 6 wells at 10 m spacing. 34/8-3 has no photos above 1,320 m, so
    it has no window bags.
  - Positives (G > 0.2): 22 bags in 5 wells (34/4-6: 3, 34/7-10: 5, 34/7-4: 2, 34/7-9: 3,
    34/8-3 A: 9).
  - 34/7-6 (14 window bags, 0 positives) contributes nothing to the rank statistic.
- **Distance baseline inside the test:**
  - In each well's window, regress rank(S) by OLS on [1, d, |d|], where d = depth - THGU.
  - Take the residual e. This removes whatever the photo score shares with position relative to
    THGU (asymmetric and V-shaped trends).
- **Statistic Q:** the mean over the 5 positive wells of AUC_w(e for G > 0.2).
  - Within-well AUC; ties count 0.5.
- **Null:**
  - Within each well's window, in depth order, circularly shift S against (G, d) by k in
    {2, ..., n_w - 2}.
  - Recompute the residuals and AUC, with an independent shift per well.
  - Use 10,000 Monte Carlo joint draws (or full enumeration if it is cheaper).
  - p = (1 + #{Q* >= Q}) / 10,001, one-sided.
- **Also report (descriptive):**
  - the per-well raw AUC of S, of GI and of the distance-only score -|d|;
  - a Firth logistic model, G > 0.2 ~ well + d + |d| + z(S), with the likelihood-ratio p for S.
- **Effective positives:**
  - Positives are merged into independent intervals when consecutive positive bags in a well are
    <= 20 m apart (adjacent bags, or one non-positive bag between them).
  - **Window count by this rule: about 6 intervals in 5 wells.** With a 15 m rule it is 11.
  - Report per interval: does it contain at least one bag in the top 20% of S within its
    well-window?

### A10. Specificity: Lista
- **Lista set:** bags in the LISTA window of the G table: 125 bags in 7 wells, all with G <= 0.2.
- **Operating threshold (primary):**
  - For each well w, tau_w = the lowest S value at which >= 50% of the positive INTERVALS in the
    OTHER positive wells have at least one bag with S >= tau_w (LOWO).
  - Lista bags of w are scored against tau_w.
- **Primary FP rate** = the pooled fraction of the 125 Lista bags above their tau_w. **Pass if <= 5%**
  (<= 6 of 125).
- **Also report:**
  - the FP rate at tau_L (the Lunde 99th percentile, label-free) together with the interval recall
    at tau_L;
  - the same two numbers for GI, with GI thresholds built the same way (GI LOWO 50%, and the GI
    Lunde 99th percentile);
  - FP among Oligocene bags more than 60 m below THGU with G < 0.05.

### A11. Out-of-window positives (descriptive only)
- 5 bags with G > 0.2 lie 147-692 m above THGU: 34/7-4 at 840, 900, 920 and 1040 m, and 34/7-9
  at 480 m. Here, position predicts nothing.
- Report the within-well percentile of S for each, among that well's bags outside the window.

### A12. Success criterion (all of these, else "photos add nothing to position for glauconite")
- (a) Primary conditional test p < 0.05 with Q > 0.5.
- (b) Residualised per-well AUC of S > residualised per-well AUC of GI in >= 4/5 positive wells.
  - Residualisation is the same as in A9, applied to GI.
  - Ties do not count as wins.
- (c) Lista FP <= 5% at the LOWO 50%-interval-recall threshold.
- **Wording if all pass:** "a feasibility demonstration on about 6 independent glauconitic
  intervals in 5 wells". Never "a validated detector".
- **Wording if (a) fails:** "not detectable beyond stratigraphic position with this data". With
  about 6 effective positives this is low-power, so it is not evidence of absence.

### A13. Secondary learned model (fixed hyperparameters; same evaluation)
- **Features:**
  - 32 native-resolution 224-px crops per photo (1.6 mm). Crop origins are uniform random within
    the analysed region, seed = hash of the stem.
  - ImageNet ResNet-50 avgpool, mean-pooled to 2048-d, then per-well z over ALL W_1 photos of the
    well (label-free).
- **Model:** L2 logistic regression, C = 0.01, class_weight = balanced.
  - Trained LOWO on all G-defined bags of the training wells. 34/7-6 and 34/8-3 are used as
    negative-only training wells.
  - Scored on the held-out well, then put through A9 to A12 in place of S.
- **Cost:** about 30k crops, a few minutes on MPS. Compute it in the SAME pass as S, so the photos
  are read from T9 only once.

### A14. Run-time estimate (measured on Lunde photos, M4 on AC power)
- **One photo, one process:** read and decode 0.67 s, Lab and smoothing 1.8 s, segmentation 1.1 s
  (about 3.6 s).
  - About 0.8 GB of RAM per worker at float32. Use 4 workers on the P-cores.
- **T9 I/O:** about 15.8 MB per photo at 33 MB/s, i.e. 0.48 s per photo.
  - With 4 workers, throughput is CPU-limited at about 0.8-0.9 s per photo.
- **Workload:**
  - Lunde calibration: 1,022 photos, about 15 min.
  - G bags: 926 photos, about 14 min.
  - GI for 34/7-6: 243 draft decodes, I/O-bound, about 2 min.
  - The ResNet crops in the same pass add about 2-4 min of MPS time.
  - **Total about 30-35 min.** Single process: about 2 h. Throttles on battery.

### A15. Round-17 amendments (reviewer: APPROVE WITH CHANGES; geochemist: freeze gates). These override A1-A14 where they differ.
Fixed before any run on G-labelled bags. Sources: reviewer round 17 and
`v7/agent2_step2_review.md`.

**Detector (A3-A6)**
- The gates are unchanged.
- **New sensitivity: hole filling off** (S_nofill). Hole filling is the one
  parameter that traces to the v6 rater's notes on G-labelled bags.
- **Per-well colour normalisation is NOT run.** It would need a second read
  of every photo. Instead, the per-well median chip a* and b* over the
  scored Tertiary bags are reported beside the result (label-free).
- **Descriptive diagnostics, not tested:**
  - counts of accepted blobs by size bin and hue bin;
  - S_brown: the same shape gates with hue 40-95 deg and a* > 0 (oxidised
    pellets).
- large_green_frac is measured on connected components before the watershed
  split.

**Primary test (A9)**
- **Null changed:** residualise rank(S) on [1, d, |d|] once per well, then
  circularly shift the RESIDUAL e against G within the well's window (shifts
  k = 2..n_w-2, independent per well, 10,000 joint draws). Raw S has a trend
  across THGU, so its shifts are not exchangeable.
- The original null (shift S, then residualise) is a sensitivity.
- **Pre-declared secondary:** the same test with [1, d] only. The |d| term
  may absorb real signal, since glauconite sits at THGU.
- **Descriptive:** within-window Spearman of S against continuous G, per well.
- The Firth logistic model is dropped (no further engineering).

**Lista (A10)**
- Report tau_w for each well.
- Add a descriptive false-positive row for Balder Fm bags (tuff).
- Negatives are called "G <= 0.2", not "glauconite-free". Window bags below
  the threshold may hold up to ~10% pellets, plus cavings.

**Success (A12), revised**
- **Criterion = (a) AND (c).**
- (b) (beats GI in >= 4/5 wells) is descriptive only; it is a coin toss with
  2-3 positives per well.
- **Wordings:**
  - (a) and (c) pass and (b) holds: "feasibility demonstration on ~6
    independent glauconitic intervals".
  - (a) and (c) pass without (b): "detects glauconite beyond position; not
    shown to beat the green index".
  - (a) fails: "not detectable beyond stratigraphic position with this data"
    (low power; not evidence of absence).

**A13 learned model: NOT run in this pass** (reviewer: no further engineering
at this sample size). If it is ever run, it is exploratory and makes no claim.

**Detection limit, restated**
- The Lunde background reaches S = 12.5 (12 photos), and S is about 20 at
  1% pellets by area. The usable limit is therefore about 1-2% by area.
- G > 0.2 implies about 12-15 wt% evolved glaucony at minimum (geochemist's
  mixing model; the positive bags imply ~40-60%). Sensitivity should not be
  the limit; SPECIFICITY is.
- **Accepted losses, named in advance:** black pellets (C* < 4), oxidised
  brown pellets, pale nascent pellets, pellets > 0.51 mm (lags at the
  unconformity), cracked or foram-infill pellets, pellets locked in mudstone
  chips, and barite-coated pellets.
- **Expected false positives:** rounded green-grey claystone granules (Lista,
  Hordaland), Balder tuff grains, chlorite flakes, and green paint or LCM.

**Label**
- G > 0.2 stays the positive label. The pellet check is used for concordance
  only (10 bags, visual).

**The run is done ONCE as frozen.** Only code bugs may be fixed, and any fix
is disclosed.

## Step 3: mud-log cuttings % as a wellsite lithology label (DRAFT v1, 2026-11-10; not final until the reviewer approves)

**Question.** Do the photographs predict what the wellsite geologist logged
in the same cuttings, in wells not used for training? The label is the
"% cuttings" column of the mud log. It is the only lithology label in the
data set that was made from the cuttings themselves and without wireline
logs.

**Why it is worth doing.** v1/v2 used GR labels (formation at a point).
Step 1 showed chemical skill at bag scale. The mud-log column describes the
bag, by eye, at the rig, so it is the label most like the photograph.

### C1. Scope
- **Wells (8, pixel route):** 24/9-3, 34/4-6, 34/4-7, 34/7-4, 34/7-9,
  34/7-10, 34/8-3, 34/8-3 A. Source: the cuttings % column of the sheets
  listed in results/v7/agent5_inventory.csv.
- **Not in this pass:** 34/7-1 and 24/9-4 (text route only), 34/7-6 (no mud
  log). Stated as a limitation, not hidden.
- **Never used:** interpreted lithology columns, composite logs, ROP, gas
  (they carry log-type information). Text descriptions are not used for the
  label in this pass.
- **Depths digitised:** the whole logged interval of each sheet (cheap once
  calibrated). Tests use the sets in C5.

### C2. Label construction (script; reads only the mud-log image)
1. **Depth calibration per sheet.** Printed depth labels are located on the
   image, and a piecewise-linear pixel-to-depth function is fitted through
   them. Every label must be within 0.5 m of a leave-one-out fit, or the
   sheet is inspected and the label list corrected (a reading error), never
   the fit loosened.
2. **Column read.** The cuttings column is cut into rows of 0.25 m. In each
   row, each pixel column is classified by its local pattern into clay
   (ruling), sand (stipple), carbonate (brick), other, or blank, with one
   rule set per contractor family (Anadrill; Exlog; Gearhart-Owen). The row
   gives fractions that sum to 1 over the non-blank part.
3. **Sample steps.** The wellsite % is drawn in steps of one sample. The
   script does not need to find the steps; it averages rows.
4. **Bag join (done by a separate script, after C3).** A bag at depth D
   stands for (D_prev, D] (bottom-of-interval, the v3b rule, with D_prev from
   the NOROG bag list). If D - D_prev > 15 m or there is no previous bag,
   the interval is (D - 5 m, D]. A bag needs at least 50% of its rows
   non-blank.
5. **Targets.** Y = sand fraction (sand + sandstone symbols). Sensitivities:
   Y_coarse = sand + silt; Y_carb = carbonate fraction; Y shifted by one
   sample up and down (+/-5 m).

The digitiser is developed looking at mud-log images only. It is frozen
(committed) before C3 and before any join to XRF or photographs.

### C3. Label gates (no photographs, no model output)
- **G1 depth.** Passes as in C2.1 for every sheet used.
- **G2 independent visual reader.** An agent that has seen neither the
  script output nor any photograph reads sand % (nearest 10) from image
  crops of 160 intervals of 5 m (20 per well; half drawn from intervals the
  script reads at >= 10% sand, half from the rest; the reader is not told
  which; tiles in random order with only the sheet's depth scale visible).
  - Pass: pooled Spearman >= 0.80, and at most 15% of intervals differ by
    more than 20 points, and no well below Spearman 0.60.
  - A well that fails is dropped from the label set, or its family rules
    are fixed ONCE and a FRESH sample of 20 is drawn. The first result is
    reported either way.
- **G3 chemistry check (XRF, still no photographs).** Per-well Spearman of Y
  against the within-well z of log10(Si/Al) on the test set of C5, after the
  +/-50 m high-pass. Expected sign: positive.
  - If the median over wells is <= 0, stop: "the mud-log sand fraction is
    not a usable bag-scale label here".
  - Otherwise report it as the reference for how well ANY bag measurement
    agrees with the mud log. It is not a significance test.

### C4. Eligibility (decided from the labels alone)
A well enters a test if it has at least 30 bags in the set with a defined Y
and at least 10 of them with |high-passed Y| >= 0.05. Wells logged as 100%
clay throughout cannot show skill and are listed as "no label variance".

### C5. Photograph tests (run once, after C3 and C4 are committed)
- **Set S (primary):** Tertiary (depth < TOP_SHETLAND), shoe-masked, the
  step-1 set restricted to bags with Y. **Set W (secondary):** all bags
  with Y in the well, same shoe mask.
- **P1 (primary).** R-D exactly as in step 1 (ResNet-50 embeddings, per-well
  z over the set, StandardScaler, PCA 32, Ridge alpha 1), trained
  leave-one-well-out on Y, scored on the held-out well. Statistic: per-well
  Spearman of prediction against Y after the +/-50 m high-pass; one-sided
  Wilcoxon across eligible wells; well-bootstrap CI.
  - Success: p < 0.05 with median rho > 0. With 8 wells the smallest
    possible p is 0.004; with fewer than 6 eligible wells the test is
    reported as underpowered and makes no claim.
- **P2 (pre-declared secondary, no new training).** The step-1 held-out
  Si/Al predictions (step1_predictions.csv, already made without the test
  well) against Y, same statistic. This asks whether a model taught only
  chemistry agrees with the wellsite geologist.
- **Baselines, same pipeline:** relative depth, bag dry weight, mean
  L*a*b* (colour only), and R-E (15 engineered features). Paired Wilcoxon
  of R-D against colour only.
- **Reference:** measured Si/Al against Y (from G3). Photo skill is read as
  a share of this.
- **Null and lag:** circular-shift null within stretches per well; lag
  profile -3..+3 bags against the no-skill curve, as in step 1.
- **Class view (descriptive):** within-well AUC for sandy bags (Y >= 0.5)
  against clay bags (Y <= 0.1), raw and after removing a linear depth
  trend, for wells with at least 5 bags in each class.
- **Set W** gets the same table, labelled secondary. It mixes the Tertiary
  with Cretaceous-Triassic rocks, where photo colour differs by formation,
  so the high-pass matters more there.

### C6. Wording, fixed in advance
- P1 passes: "in wells not used for training, photographs predict the local
  (within +/-50 m) variation of the sand fraction logged at the wellsite;
  exploratory but fully pre-specified".
- P1 fails with G2 and G3 passed: "no bag-scale agreement between
  photographs and the wellsite sand fraction was found, although chemistry
  agrees with it"; not evidence of absence if fewer than 8 wells are
  eligible.
- Never "sand detector", never "bed scale". The wellsite % is itself an
  estimate by eye in 10% steps and is affected by cavings and washing.

### C7. Known weaknesses, named before the run
- Cavings and washing loss bias the wellsite % (soft clay washes out, so
  sand is over-stated); the washed photographs share that bias, which helps
  agreement without being geology.
- Lag errors of one sample are common in fast top-hole drilling (tested by
  the +/-1 sample sensitivity, not corrected).
- The Exlog clay ruling resembles the chart grid (34/7-4); G2 is the check.
- 1-bit scans (34/7-9, 34/7-10) are speckled; G2 is reported per well.
- 34/8-3 is logged only from 1318 m and 34/8-3 A from 996 m MD.
- These wells were used in earlier rounds, so the result is exploratory.
