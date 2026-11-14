# v7 step 2: photo glauconite-pellet detector. Proposed FROZEN specification

Date: 2026-11-10. Drafted in the methods check (see Use of AI in the README).

**Blindness statement.**
- I looked at NO photograph of any G-labelled bag. The Tertiary bags of 34/4-6, 34/7-4, 34/7-6, 34/7-9,
  34/7-10, 34/8-3 and 34/8-3 A from 400 m to the Lista base were not looked at.
- No detector output was computed on any G-labelled bag.
- Image statistics come ONLY from 12 Lunde Fm photographs (Triassic, continental, so glauconite is
  impossible; no XRF G), plus one Lunde photo viewed for the frame layout.
- **Disclosure:** earlier (v7 notes) I read the TEXT of the v6 blind pellet rater's notes on the
  10 high-G bags. They describe "dark-green rounded cracked pellets 0.15-0.3 mm", "lighter-green
  crack networks" and "pale olive-green grains". The size range below comes from the literature
  and is wider than those notes. The hole-filling step was partly motivated by the
  "crack networks" remark.
- Prototype code (the parameters exactly as below):
  a working file (not kept).
  Lunde check outputs: a working file (not kept).

---------------------------------------------------------------------------
## PART A. Specification (to copy into V7_PLAN.md step 2 and freeze)

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

---------------------------------------------------------------------------
## PART B. Rationale and what the Lunde check showed

### B1. Why these colour gates
- **Glaucony colour** (standard sources; quoted from memory, so verify before citing):
  - Odin & Matter (1981), Amorosi (1997): colour changes with maturity, from pale or light green
    (nascent, low K2O) to dark green (evolved, highly evolved, K2O > 6-8%). Oxidised grains are
    brown or yellow-brown.
  - Wellsite and rock-colour-chart practice describes glauconite as "dark green", "dusky green
    (5G 3/2)", "greenish black (5G/5GY 2/1)" or "greyish olive green (5GY 3/2)".
- **Approximate Munsell to CIELAB conversion:** L* is about 10 x value (value 2-4 gives L* about
  20-42). Chroma 1, 2 and 4 give C* of about 3-5, 6-10 and 14-20. Hue 5GY is about 100-110 deg,
  10GY about 125-140 deg and 5G about 155-170 deg.
  - The gates therefore target DARK, MODERATELY saturated yellow-green to green.
  - **This is the opposite of the old GI**, which requires C* >= 12 and allows L* up to 80. GI
    favours vivid and pale greens (green-grey Lista, Lunde, Jorsalfare mudstone) and is coarse
    (57 um/px).
- **The warm rendering of this set-up** shifts every hue toward yellow. Hence the lower hue bound
  of 95 deg together with a* <= -1.5, so that a neutral-but-warm grey cannot pass.
  - Lunde chip medians are a* +1.9 to +16.7 and b* +15 to +33 (red beds included).
- **Light-green, nascent glaucony is deliberately excluded** (L* > 50). The XRF G index is a K and
  Fe excess, which favours evolved, K-rich glaucony anyway. Pale-green pellets are the known blind
  spot, matching the "pale olive-green grains" seen by the v6 rater. The L* 55 sensitivity probes it.

### B2. Why native resolution and these shape gates
- Glaucony grains are mainly fine to medium sand size (about 0.1-0.5 mm) and rounded: ovoid,
  lobate or mammillated, and capsule-shaped (Triplehorn 1966).
- At 7.14 um/px that is 14-70 px across. At the 21 um/px of the existing tiles it is 5-24 px, and
  at the 57 um/px of GI it is 2-9 px, too small for any shape test.
- Shape plus darkness is the only discriminant from green-grey mudstone chips, which are larger
  (over 1 mm, over 140 px), lighter and angular or platy.
- The watershed split protects abundant greensand from merging into one "chip".

### B3. Lunde (glauconite-impossible) check, 12 photos, 2 per well, random
| quantity | value |
|---|---|
| chip fraction | about 0.995 |
| pellet-gate pixel fraction | 0.00002-0.016 (median about 0.002) |
| S, accepted blobs per 10^6 chip px | 0.0, 0.0, 0.05, 0.92, 0.97, 0.97, 1.42, 2.06, 3.79, 4.50, 4.91, 12.5 (median about 1.2) |
| greenish pixels (h 95-200, C* >= 4, a* <= -1.5), L* 10/50/90th percentiles | median L* 47-78; the 10th percentile 24-54 |
| old GI on the same photos | 0.000-0.014 |

What this means:
- The false-positive floor is about 1 blob per 10^6 px (about 20 per frame), from the darker
  faces of green-grey mudstone chips.
- A bag whose chip area is about 1% pellets of 0.2 mm would give S of about 20. So abundant
  greensand should stand clear, while traces (under about 1%) will sit inside the Lunde background.
- **Detection limit:** roughly a few % pellets by area. State this in the thesis.
- These 12 photos were used ONLY to check the pipeline and the time cost. **No gate was changed
  after seeing them.** The gates in A3 and A4 are exactly those in the prototype run.

### B4. Why the test is built this way
- Position relative to THGU alone gives within-well AUC 0.75-0.99 (all depths). So only a test
  conditioned on position can show that the photo adds anything. The test therefore uses the
  window plus the residual on [1, d, |d|].
- **Bags are not independent.** Positives come in runs (caving and bag mixing over 10 m). Hence the
  circular-shift null and the interval count: about 6 effective positives.
- **Power is low.** Even a good detector may give p of about 0.05-0.2 with 5 wells and about
  6 intervals. Say so in advance, so that a null is not over-read.
- **The Lunde tau_L** is a label-free operating point that cannot be tuned on G. The LOWO
  recall-matched threshold is the operating point that gives "FP <= 5%" its meaning; a very high
  threshold would pass FP trivially with zero recall.
- **Lista** is the right hard negative: green-grey marine mudstone, G 0/125, and the place where
  the old GI fired 25-100x.

### B5. Known risks
- **Per-well Photoshop versions** (21.0, 22.2, 22.4) may shift colour. The absolute gates are
  primary; the per-well normalisation is a sensitivity. The within-well ranking test is immune to
  per-well score offsets, but not to gate-crossing shifts.
- **Barite and mud coating** (photos see Ba, step 1: rho 0.31) lightens and desaturates grains.
  This may hide pellets in heavily weighted bags. Report S against within-well log Ba
  descriptively.
- **Glauconitic caving** into non-positive bags (and the reverse) blurs the labels. G > 0.2 is
  itself pellet-confirmed in only 8/10 bags.
- **Shells and green-stained carbonate:** a* is rarely negative there; accepted.
