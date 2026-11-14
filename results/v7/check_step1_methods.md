# Methods check of v7 steps 1 and 2 (machine learning and computer vision)

Date: 2026-11-09. A check of the plan (see Use of AI in the README).
Read-only work. The scripts and outputs of these checks were working files and are not kept.
**I did not compute any photo -> target skill**, so the step-1 primary stays uncontaminated
before it is pre-registered. Every number below comes from chemistry, EXIF or the existing v6 G table.

---------------------------------------------------------------------------
## 0. Recommendations first

### Step 1 (photos -> barite-corrected within-well z log10(Si/Al))
1. **Keep the planned primary unchanged** for continuity: per-well z ResNet-50 RGB, PCA32, Ridge.
   - Ridge alpha = 1 on 32 standardised PCs with about 4,500 rows is effectively OLS.
     An "alpha = 10" sensitivity will change almost nothing, so drop it.
   - Instead, pre-declare ONE regularised alternative: raw 2048-d, standardised, RidgeCV with
     alpha in logspace(-1, 5). Choose alpha by an inner leave-one-well-out loop on the training
     wells only, and report it as secondary. Do not choose between the two models after seeing results.
   - Weight wells equally in training (sample weight 1/n_well). Bags per well range from 243 to 615.
   - No fine-tuning and no attention-MIL here:
     - The C1/C2 fine-tuning in v3 gave no gain over frozen features.
     - With 11 wells, extra capacity mostly learns well and batch cues.
     - A linear model on the depth-mean embedding equals the mean of tile-level linear predictions,
       so tile-level linear training adds nothing.
2. **Barite correction: say what it is.**
   - Barite dilution scales Si and Al equally, so it cannot change Si/Al. The observed Si/Al-Ba
     slope must come from something else:
     - (a) a handheld-XRF matrix/absorption effect on the light elements in a Ba-heavy matrix; or
     - (b) geology or operations: heavier mud in deeper, shalier sections.
   - Under (b) the "correction" removes real signal. Under (a) it is legitimate.
   - The checks show it does not remove the local Ba relation in any case. After high-pass,
     rho(T, Ba) ranges from -0.43 to +0.31, with 6 wells positive and 5 negative.
   - So report **partial Spearman** (high-passed photo prediction vs high-passed T, controlling
     high-passed log Ba, log Ca/Al and log Cl) as a co-reported endpoint. Do not rely on the
     global b alone.
3. **Mandatory leakage and negative controls** (all cheap, all pre-declared):
   - **Circular-shift null.** Within each well, shift T against the photos by at least 100 m,
     wrapping around inside continuous segments. This replaces any "shuffle within well" null,
     which is invalid here because high-passed T keeps lag-1 autocorrelation of 0.06-0.76.
   - **Lag profile.** Correlate photo(bag k) with T(bag k+m) for m = -6..+6.
     - Same-bag information shows as a peak at m = 0.
     - A flat profile out to 15-30 m means only interval-scale smearing. This is the direct test
       of the "sample-matched" claim behind v7.
   - **Photo -> Ba diagnostic.** Train the same pipeline on high-passed log Ba.
     - If photos predict Ba much better than T, the barite coating is visible and is a leakage channel.
     - Also report the T result stratified by within-well Ba tercile.
   - **"Photo-blind" chemistry negative control.** No raw element qualifies: Pb, Zn, Cu, Rb, Nb,
     Mn, Zr, Ti and Sr all correlate with high-passed Si/Al at about -0.1 to -0.67.
     Use the **pipe-dope excess** instead: the residual of high-passed log Zn (and Pb) after
     within-well regression on high-passed T and Ba. Photos should not predict it (expected rho about 0).
   - **Capture-session control** (EXIF; see section 3). Extract DateTimeOriginal for all 5,038 W_1
     photos, which is header-only and takes about 10-12 min of USB reads.
     - Define sessions as capture gaps over 30 min or a new day.
     - Run the high-pass within sessions as a sensitivity.
     - **Reshoot test:** bags photographed days after their neighbours should not have
       prediction-minus-neighbour residuals that differ from other bags.
4. **Statistics.**
   - Wells are the unit of replication. A one-sided Wilcoxon over 11 wells has a minimum
     p of 1/2048 (about 0.0005), so it is adequate.
   - Add a well-bootstrap 95% CI on the median rho. Keep the review's effect-size floor
     (median rho >= 0.10).
   - Per-well significance comes from the circular-shift null, not from a naive Spearman p.
     Effective n after high-pass is about 60-400 per well (sum about 2,500 of 5,037 bags).
     The per-well SE of rho is therefore about 0.05-0.13.
   - **LOAO caveat.** Leaving out 34/7 removes 5 of 11 wells and trains on 6, so the training
     size changes. 34/8-3 and 34/8-3 A are near-twins: Si/Al at 392 shared depths has
     rho 0.33, with separate measurements. LOWO with 34/8-3 A in training is mildly optimistic
     for 34/8-3 and vice versa. Treat LOAO as a stress test, not a second primary.
5. **Per-well z-scoring is fine** because it is label-free.
   - Fix its reference set in advance: all W_1 photos of the well, as in v2.
   - Do NOT z on the analysed Tertiary subset in one run and on all depths in another.
   - Spearman per well is invariant to target z, so target z only changes how wells are
     weighted in training.

### Step 2 (photo glauconite detector, target XRF G)
- **The data are tiny and spatially clustered.**
  - G > 0.2 (no Al floor) holds in **27 bags in 5 wells**:
    34/4-6: 3, 34/7-10: 5, 34/7-4: 6, 34/7-9: 4, 34/8-3 A: 9.
  - Only 4 of the 27 pass the Al floor.
  - 34/7-6 and 34/8-3 have no positives. 34/4-7 and 34/7-1 have no G (no Oligocene baseline).
    24/9 is not computed.
  - G > 0.15: 50 bags; G > 0.1: 74 bags.
  - The blind pellet check (E) used 10 positives, all with G >= 0.35.
- **Stratigraphic position alone almost solves the task.**
  - Score = closeness to THGU gives per-well AUC 0.99, 0.99, 0.77, 0.75 and 0.97
    (34/4-6, 34/7-10, 34/7-4, 34/7-9, 34/8-3 A).
  - Score = "in Utsira, or within 40 m below THGU" gives AUC 0.64-0.98.
  - So **raw within-well AUC of a photo score is uninformative.** Any photo model that tracks
    depth or facies (sandier, shellier Utsira) would score well.
- **Recommended design:**
  - **Target:** binary G > 0.2, with sensitivities at 0.15 and 0.3. Do not use continuous G as
    primary: below about 0.1, G is clay-mineralogy noise, and Spearman over all bags is dominated
    by that noise.
  - **Primary feature: a pre-declared, nearly parameter-free pellet feature at native resolution.**
    - Current tiles are 672 px resized to 224 px, so about 21 um/px. Pellets of 0.15-0.3 mm are
      only 7-14 px there.
    - At native 7 um/px they are 20-45 px. The feature is the density per cm^2 of imaged
      cuttings of dark-green (hue and chroma range fixed a priori), roundish, 15-60 px blobs.
    - Cost: read the about 930 Tertiary photos with G, about 14 GB, roughly 7-8 min at 33 MB/s;
      CPU blob detection about 10-20 min.
    - Thresholds may be set by eye on the 10 E photos only if those 10 are then dropped from
      the test, or the circularity is disclosed.
  - **Secondary:** native-resolution ResNet crops (for example 32 crops of 224 px per photo,
    1.6 mm at 7 um/px), mean-pooled, then logistic regression with strong L2 and balanced class
    weights, run LOWO over the 5 positive wells plus 2 negative-only wells. It will have high
    variance with 27 positives.
  - **Baselines the detector must beat:** (i) the existing photo "green index" (known to fire
    25-100x in Lista and Lunde); (ii) position (|distance to THGU|).
- **Metrics (honest set):**
  1. **Conditional test (primary):** within THGU -80 m to +80 m, does the photo score rank
     high-G above low-G bags?
     - Pool wells with a stratified rank-sum (van Elteren).
     - Use a circular-shift null inside the window, or a block permutation in 10 m blocks.
     - Alternatively, use logistic regression of G > 0.2 on photo score plus distance to THGU
       plus well, and test the photo term.
  2. **Specificity:** the false-positive rate in Lista (125 bags with G, 0 positive), and in
     the other green, non-glauconitic sections, at the threshold that gives 50% recall in the
     training wells.
  3. **Out-of-window positives:** 7 G > 0.2 bags lie 147-692 m above THGU ("other" window),
     where position fails. Report descriptively whether the detector finds them (n is tiny).
- **Honest success criterion** (state it before running):
  - "Photo glauconite detector works" only if ALL of these hold:
    - (a) the conditional test gives p < 0.05 with a positive photo term;
    - (b) it beats the green index in at least 4 of 5 wells;
    - (c) the Lista false-positive rate is <= 5%.
  - Otherwise report "the photographs do not add to stratigraphic position for glauconite".
  - With about 27 clustered positives (about 10 independent depth runs), even success is a
    feasibility demonstration, not a validated detector.

---------------------------------------------------------------------------
## 1. Evidence from quick checks (chemistry, EXIF, G table; no photo-target skill computed)

### 1.1 Si/Al target vs Ba, depth and Cl, per well
5,037 W_1 bags matched to XRF. T = log10(Si/Al) minus the Theil-Sen Ba slope times centred log Ba.
High-pass = minus the running median over +/-50 m (gaps over 30 m split).

| well | n | dz | b TS | rho(SiAl,Ba) raw | rho(T,Ba) HP | rho(T,depth) raw | rho(T,Cl) HP | var kept by HP | lag1 HP | n_eff HP | Ba median / p90 ppm |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 24/9-3 | 615 | 3 | -0.20 | -0.38 | +0.31 | -0.10 | +0.02 | 0.34 | 0.30 | 335 | 1.4k / 6.3k |
| 24/9-4 | 363 | 3 | -0.02 | -0.11 | +0.16 | -0.35 | -0.13 | 0.51 | 0.64 | 79 | 3.0k / 8.8k |
| 34/4-6 | 503 | 5 | -0.07 | -0.21 | -0.10 | +0.43 | -0.21 | 0.28 | 0.14 | 384 | 8.1k / 44k |
| 34/4-7 | 423 | 5 | -0.14 | -0.50 | +0.07 | +0.42 | -0.22 | 0.19 | 0.29 | 231 | 15k / 60k |
| 34/7-1 | 468 | 3 | -0.18 | -0.75 | +0.17 | +0.56 | -0.13 | 0.33 | 0.45 | 176 | 15k / 65k |
| 34/7-10 | 453 | 5 | -0.11 | -0.34 | -0.43 | +0.30 | -0.23 | 0.37 | 0.06 | 398 | 6.6k / 61k |
| 34/7-4 | 552 | 3 | -0.21 | -0.61 | -0.01 | +0.61 | +0.03 | 0.32 | 0.27 | 315 | 23k / 59k |
| 34/7-6 | 243 | 5 | -0.03 | -0.20 | -0.33 | +0.13 | -0.30 | 0.54 | 0.45 | 93 | 14k / 66k |
| 34/7-9 | 527 | 3 | -0.18 | -0.46 | +0.16 | +0.48 | +0.00 | 0.29 | 0.28 | 297 | 4.4k / 62k |
| 34/8-3 | 451 | 5 | -0.08 | -0.39 | -0.19 | +0.47 | -0.21 | 0.48 | 0.76 | 62 | 15k / 60k |
| 34/8-3 A | 439 | 5 | -0.08 | -0.33 | -0.01 | +0.06 | -0.09 | 0.34 | 0.46 | 161 | 17k / 48k |

What this shows:
- **Barite is everywhere and abundant.** The Ba p90 is about 5-6.6% in the Tampen wells. Barite
  residue on the chips (white powder, lower saturation) is plausibly visible in the photos.
- **The global correction leaves a local Ba-T relation of either sign** (HP rho -0.43 to +0.31).
  A pooled model that learns "whiteness" could therefore gain or lose spuriously in a held-out
  well. Partial correlation on high-passed Ba is required.
- **Depth trend:** raw T vs depth has rho +0.4 to +0.6 in 7 wells, so the unfiltered rho is
  inflated by shared trends. The high-pass removes 46-81% of the T variance.
- **Cl:** high-passed T vs Cl is negative in 8/11 wells (down to -0.30). Salt crusts or KCl mud
  could be visible, so include Cl in the partial correlation.
- **Effective sample size:** about 60-400 per well. In 34/8-3 and 24/9-4, n_eff is under 80
  because the high-passed series is still strongly autocorrelated. Expect wide per-well rho there.
- **Chemistry negative-control candidates:** no raw element is photo-blind. After high-pass, the
  correlation with T is: Pb -0.06 to -0.46, Zn -0.12 to -0.65, Rb -0.28 to -0.66, Nb -0.23 to
  -0.67. This is closure and dilution by quartz. Hence the residualised pipe-dope Zn/Pb proposal.
- **34/8-3 vs 34/8-3 A:** 392 shared depths, no identical values (separate bags), Si/Al
  rho 0.33. They are related but not duplicates. Keep both, and note the twin effect in LOWO.

### 1.2 Photo acquisition and processing (02_index, EXIF)
- The `processing` field is 'standard' for every W_1 and 'dynamic' for every W_2, so W_1 is
  uniform. No index-level processing differences exist between wells.
- **EXIF on 3 photos per well, all 11 wells:**
  - Same Canon EOS 80D, 60 mm, f/16, 1/8 s, ISO 200, manual white balance. Acquisition is fixed.
  - Edited in Adobe Photoshop: 21.0 for 7 wells, 22.4 for 34/4-6 and 34/7-6, 22.2 for 34/8-3 A.
  - One Photoshop save session per well, on dates from 2020-12 to 2021-07.
  - So each well is a separate post-processing batch. Per-well z absorbs linear offsets, but
    not nonlinear curve or colour-profile differences.
  - Implication: LOWO always crosses a processing batch, which is good for honesty but adds a
    domain shift that per-well z only partly fixes.
- **EXIF on all 453 photos of 34/7-10:**
  - Captured over 2021-03-19 to 03-23, mostly in depth order (97% monotone).
  - **Isolated reshoots** 3-4 days later at 1590, 2085, 2110, 2120, 2185, 2387, 2492 and 2945 m.
  - **A session break** at about 2390/2396 m (Friday evening, then Monday).
  - The exposure is fixed, but lamp warm-up, tray background or room light may differ between
    sessions.
  - A step change inside a +/-50 m window leaks through a running-median high-pass for up to
    50 m on each side.
  - The reshoots are a free natural experiment: same geology context, different session.

### 1.3 Step-2 data (v6 D_xrf_glauconite_bags.csv, G without the Al floor)
- 926 bags with G in 7 wells.
- 27 bags with G > 0.2: 11 in OLIG, 9 in UTSIRA, 7 in 'other'.
- Distances of positives from THGU: -692, -347, -287, -267, -147, -70, -60, -50, -40, -22, -20,
  -20, -13, -10, -7, -2, 0, 3, 7, 8, 10, 17, 27, 30, 37, 50, 60 m.
- Base rate per well: 2.5-6.2%.
- Position baseline (|dist to THGU|): per-well AUC 0.75-0.99; average precision 0.39-0.76.
- 10 of the 27 positives were already shown to the pellet rater (E). All of them have G >= 0.35.

---------------------------------------------------------------------------
## 2. Step-1 critique in more detail

### 2.1 Model choice
| option | verdict |
|---|---|
| PCA32 + Ridge(1), per-well z (planned) | keep as primary (continuity with D1/D2) |
| Raw 2048-d RidgeCV, nested group CV | one pre-declared secondary; smooth shrinkage beats a hard PCA cut, and the top PCs of pooled data carry illumination and batch variance |
| PLS (supervised components) | not needed; only a "flavour" variant |
| Engineered 15 features (R-E) | keep; interpretable; good for the barite check (bright_lowsat_frac, lab_L_mean are the obvious barite-sensitive ones) |
| Fine-tuning (MPS, about 1 GPU-hour) | not for step 1: 11 LOWO fine-tunes, and v3 C1/C2 showed no gain |
| Tile-level linear | identical in expectation to bag-mean linear; adds nothing |
| Attention-MIL / quantile pooling | exploratory at most; the only plausible gain is mixture information (the fraction of sand-like tiles); try cheap quantile pooling of the 15 engineered features before any MIL |
| More tiles or multi-scale | see section 4 (medium value) |

Training domain: train and test on the same domain. Tertiary, with 0-15 m below shoes masked (as
the review says). Training on all depths imports pre-Tertiary red beds and Brent sands, where the
Si/Al-appearance mapping differs.

### 2.2 Validation
- LOWO over 11 wells: primary. Wells are separate photo batches, so it is honest about the
  batch shift.
- LOAO: stress test only (unequal training size; 34/7 is 5 wells).
- Do not tune anything (alpha, PCA size, window) on the test well. All of it goes inside the
  inner loop or is fixed in advance.

### 2.3 Primary metric (high-passed per-well Spearman)
- **Good choice:** it removes shared depth and compaction trends and the between-well offsets.
- **Additions:**
  - (i) Report the lag profile (section 0, step 1, item 3). It is the most direct evidence for
    same-bag skill.
  - (ii) Report the partial rho with Ba, Ca/Al and Cl.
  - (iii) Use the circular-shift null per well.
  - (iv) Report ±25 m and ±5-bag windows as sensitivities, as the review asked; ±25 m keeps
    less trend.
  - (v) Report the relative-depth baseline after the same high-pass. It should be about 0. If not,
    the high-pass leaks trend and the machinery is suspect.
- **Edge effects:** at segment ends the running median is one-sided. This is minor, but exclude
  windows with fewer than 5 bags.

### 2.4 Leakage channels (ranked by how worried I am)
1. **Barite and mud coating** (visible, abundant, related to T with a sign that varies by well).
   Controls: partial rho on high-passed Ba, the photo->Ba diagnostic, and Ba-tercile stratification.
2. **Capture-session and post-processing batches.** One Photoshop batch per well; multi-day
   capture with reshoots inside a well. Controls: session-aware high-pass and the reshoot test.
3. **Cement, carbonate and shells** (known false positives in v3). Control: partial rho on
   Ca/Al, and the cement mask.
4. **Sample amount and tray background.** Bag weight is a known processing artefact. Control:
   the fraction of background pixels per photo as a nuisance covariate.
5. **Depth trends.** Handled by the high-pass; show that the relative-depth baseline is about 0.
6. **Twin wells 34/8-3 and 34/8-3 A.** Note it; LOAO covers it.
7. **Per-well z.** Label-free, so not leakage; fix the reference set.

---------------------------------------------------------------------------
## 3. Step-2 design: see section 0. Additional notes
- **Sample units:** bag-level score = a robust aggregate of crop scores (for example the 90th
  percentile of crop pellet density, since pellets may be a minority of the bag).
- **Do not train on Utsira positives against all negatives without conditioning:** the model
  learns "Utsira-ness". If a learned model is used, sample negatives matched in position (bags
  within ±80 m of THGU) for training as well as for testing.
- **Class imbalance:** use balanced class weights or focal loss only for the learned secondary.
  The hand-crafted primary needs no imbalance handling. Report average precision next to AUC
  (the base rate is 2.5-6%).
- **Spatial clustering:** positives come in runs. Use block or circular nulls, and count
  "independent detections" as runs, not bags.
- **Labels:** G > 0.2 is itself noisy (pellets in 8/10 high-G bags). Use G-band sensitivities.

---------------------------------------------------------------------------
## 4. Ranked improvements (expected value vs cost)
| rank | improvement | cost | value |
|---|---|---|---|
| 1 | Step-1 leakage and negative-control package: partial rho (Ba, Ca/Al, Cl), circular-shift null, lag profile, photo->Ba diagnostic, pipe-dope negative control, high-passed relative-depth check | CPU minutes | High: decides whether any positive result is believable |
| 2 | EXIF capture-session table for all 5,038 W_1 photos, plus the session-aware high-pass and the reshoot test | about 10-12 min of USB reads, no compute | High for leakage, cheap |
| 3 | Native-resolution pellet-blob feature for step 2, with the conditional (position-controlled) test and the Lista specificity check | about 8 min of reads plus 10-20 min CPU | The only route to a glauconite-specific detector; medium-high |
| 4 | Denser and multi-scale embeddings: 48-64 tiles per photo at the current scale plus native-scale crops; Tertiary only first | about 20-40 min of reads plus 20-30 min MPS | Medium: reduces bag-level sampling noise and adds grain-scale texture |
| 5 | Raw-2048 RidgeCV (nested group CV) with well-balanced weights | trivial | Low to medium: robustness, not new signal |
| - | Fine-tuning or attention-MIL | about 1 GPU-hour or more | Low expected value; high risk of batch cues; not recommended now |
