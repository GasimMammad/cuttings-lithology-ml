# v6 plan: sinkite / glauconite tests with existing data. DRAFT for review; nothing computed.

## Hypothesis under test (as reconstructed by the review, round 11)

On the Snorre-Visund mound, the Oligocene (Hordaland Gp) sand bodies just
below the Top Hordaland Unconformity (THGU) are **sinkites**: younger sand
that sank from above into soft biosiliceous ooze (Løseth et al. 2013 style).
The alternative is that they were deposited in place in the Oligocene
(Rundberg & Eidvin).

- **Support would be:** a younger-than-host age of the sand itself; a
  composition matching an overlying source; sand-locked (not caving-like)
  signals.
- **Refutation would be:** in-situ Oligocene fauna inside the sand and no
  younger fauna, in samples that cannot be cavings; composition unlike every
  candidate source.
- The glauconite tests can refute only a glauconitic (Utsira) source.

## A. Corrections (no new analysis)

- Correct the claims in the v2 copy only; the original repo stays untouched.
  Write `GLAUCONITE_CORRECTIONS.md`:
  - the Utsira-control count is about 1-2 of 6 independent wells, not "5 of 7";
  - rename "glauconite index" to "green index" (not glauconite-specific; fires
    25-100x on Lista/Lunde green-grey claystones);
  - "fire > background" is a noise-level threshold;
  - the STAGE3lite GR/AI "glauconite" labels are confounded by opal-CT and
    compaction;
  - the calibration script is lost (12_glauconite_test.py holds Fig A7 code);
    the thresholds are frozen and reproducible, their derivation is not.

## B. Biostratigraphy of the Oligocene sands (the decisive test)

- **Reader:** one reader of the
  operator biostratigraphy and well report PDFs on T9:
  - 34/7-6, 34/7-10, 34/7-4, 34/7-9 (`GEOLOGY/*BIOSTRAT_REPORT*.PDF`);
  - 34/4-6, 34/4-7, 34/7-1 (Bulletin 10 compilation already in
    `~/sinkite_ml_work/biostrat`).
- **Per mapped Oligocene sand interval:**
  - sample types inside the sand (ditch cuttings DC, sidewall core SWC,
    conventional core);
  - the fauna and flora reported;
  - any Neogene or Quaternary taxa, and how the operator interpreted them
    (caved, reworked, in situ).
- **Evidence rule, fixed now:**

| outcome | criterion |
|---|---|
| SUPPORT | Neogene/Quaternary taxa reported in an SWC or core sample inside the sand, not attributed to contamination |
| AGAINST | in-situ Oligocene assemblage in SWC/core inside the sand with no younger taxa |
| INCONCLUSIVE | DC only (young taxa in DC = expected cavings), or no samples inside the sand |

- Sand intervals: from the operator lithology and the GR logs (PARTB_*,
  sand_bodies.json, NPD "no formal name" units), fixed before reading the
  fauna.

## C. Spectral gamma ray (Th/K)

- **Wells:** 34/4-6 (NGT 514-3288 m), 34/7-1, 34/8-3, where NGT
  POTA/THOR/URAN exist.
- **Compare:** Utsira (glauconite expected: low Th/K), the Oligocene sand
  bodies (34/4-6 1359-1387 m), the Hordaland ooze/mudstone, and Lista.
- **Rule:** glauconite = Th/K below the well's Oligocene-mudstone 10th
  percentile AND K above that well's mudstone median, within open-hole log
  segments only.
- Report per interval: median Th/K, K and the fraction of samples meeting the
  rule.

## D. XRF glauconite proxy, pre-registered (from the geochemistry check)

- **Index:** G = min(log10(K/Al / base), log10(Fe*/Al / base)), where Fe* =
  Fe - 0.87 S and base = the well's Oligocene-mudstone median more than 30 m
  below THGU. Fire = G > 0.2.
- **Exclusions:** Cl > 5000 ppm; Mn > 1000 ppm (siderite); 34/8-3 K-Cl
  suspect section flagged.
- **Controls:**
  - positive: Utsira fires in >= half of the Tampen wells with Utsira bags;
  - negative: Lista and deep Oligocene mudstone fire in < 5% of bags.
- **Discriminating test** (caving vs sinking): within the Oligocene of each
  well, a logistic or permutation test of firing against (i) distance below
  THGU and (ii) a log-defined sand indicator (frozen intervals).
  - Caving predicts decay with distance and no sand effect.
  - Sinking predicts a sand effect at any distance.
  - Wilcoxon / Fisher across wells.
- **Targets:** report 34/7-6 1218-1283 m and 34/7-10 1314-1328 m explicitly.

## E. Blind pellet check on photographs (optional, after D)

The 10 highest-G bags and 10 random Oligocene mudstone bags, at full
resolution, rated blind for rounded green pellets vs green clay chips by one
reader. Descriptive only.

## F. GR/AI test (re-done with fixes; lowest priority)

34/7-10 1314-1328 m and 34/4-6 1360-1389 m, with:
- clean-sand end member from an independent interval;
- an explicit K-excess detection limit;
- the opal-CT confound stated.
Descriptive.

## Reporting

- Every test reports its pre-set outcome category.
- No "proof".
- Overall verdict reviewed.

---
## FINAL AMENDMENTS after review round 12 (binding; committed before any test runs)

- **A.** Add one correction: "firing concentrated 0-30 m below THGU" does NOT
  separate caving from sinking; both predict it.
- **C, DROPPED.** Valid POTA/THOR intervals: 34/4-6 2499-2776 m, 34/7-1
  1831-2913 m, 34/8-3 2572-3331 m. None covers the Utsira or Oligocene.
  Reported as "considered, not possible".
- **B, rule replaced.**
  - The reader first extracts a RAW sample table (well, depth, sample type
    DC/SWC/core, inside which sand interval, taxa with abundance, age markers,
    operator remark), then applies the rule.
  - **SUPPORT:** >= 2 SWC/core samples inside the sand with a coherent
    younger assemblage (Pliocene/Pleistocene markers, one biozone), with or
    without reworked Oligocene taxa. Operator "caved/contamination" remarks
    are recorded but not decisive.
  - **AGAINST:** >= 2 SWC/core samples inside the sand with in-place
    Oligocene markers in good abundance AND no younger taxa.
  - **INCONCLUSIVE:** DC only; BARREN samples; ages from bracketing
    mudstones (e.g. the 34/7-10 1230-1350 m chart; the 34/4-6 unit age).
  - Prior evidence: published Sr ages from inside these sands, where they
    exist (Eidvin & Rundberg; Rundberg & Eidvin 2016). Citations verified,
    never from memory.
- **D, fixes.**
  1. **Al floor:** bags with Al below the 10th percentile of that well's
     Tertiary bags are excluded (K/Al and Fe/Al too noisy).
  2. **Negative control = Lista only** (deep Oligocene mudstone is G's
     baseline).
  3. **KCl:** K is replaced by its residual after a within-well regression on
     Cl; the Cl > 5000 ppm cut is a sensitivity only.
  4. **Uninformative rule:** if the Utsira positive control fires in fewer
     than half of the Tampen wells with Utsira bags, D is UNINFORMATIVE, not
     negative.
  5. **Sand bags from GR alone**, before XRF or photos: v2 zone anchors,
     mean Vsh < 0.30 over (D - 10, D]. Wells without a Tertiary GR zone cannot
     enter the caving-vs-sinking test.
     - Sand effect: an exact/permutation test per well (firing in sand bags
       vs non-sand bags, Oligocene only), combined across wells (Fisher).
     - The sand effect is also required in bags > 30 m below THGU.
     - Report sand-bag counts per distance band.
  - G keeps min(K/Al, Fe/Al), so a single elevated ratio (K-feldspar,
    Fe-smectite) cannot fire.
- **E, F:** descriptive. F cites measured Utsira glauconite contents if
  found.

## G. Young-taxa distribution check (added after review round 13; exploratory; rule fixed before tabulating)

- **Wells:** 34/7-6 and 34/7-10.
- **Taxa:** every DC sample from THGU down to 50 m below the target sand.
  Young markers: Cibicides grossa, Ammonia (beccarii group), Elphidium
  spp., Cassidulina teretis, Neogloboquadrina pachyderma/atlantica, plus
  any other Pliocene/Pleistocene taxon the report names.
- **Interpretation (fixed now):**
  - **Confined to the sand:** young taxa present in >= 2 sand samples and
    in <= 10% of the samples in the ooze above and in the mud below. Simple
    caving explains this poorly: a weak hint of a young component.
  - **Scattered:** young taxa at similar frequency above, in and below the
    sand. Cavings.
  - Otherwise (too few samples or productive samples): INCONCLUSIVE.
- **Not a test of the hypothesis.** DC only.
