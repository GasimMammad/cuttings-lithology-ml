# Project log

A dated record of the follow-up to the dissertation. Each round has a plan
committed before it was run and a results file that ends with the review
and the changes it required. The commits named here fix the order: plan,
then code, then a single run, then the write-up.

## 2026-11-05: v2 to v5

- **v2, sand against clay in ten wells.** Labels for eleven wells (one zone
  per open-hole run) and the analysis plan committed together (acc57e0).
  The primary test passed: median held-out AUC 0.73, Wilcoxon p 0.039
  (eaa36f4).
- **v3, baselines and the first XRF test.** Plan revised after review
  (6997552); results with both XRF runs (826d31c, 730edb6). Depth within
  the well does as well as the photographs.
- **v3b, bag-interval labels.** Plan (032d5cf) and amendment (1b3baa9)
  before computation; the criterion was not met (083813c).
- **v4, core photographs.** Plan (26499b5); pilot rater agreement
  (eee8bed); the hard-well pilot failed the agreement gate and core
  digitisation was stopped. Results 77fa436, corrected baf2951.
- **v5, panel adjudication of the core raters.** Plan (2963df1) and
  amendment (e9e58cb) while the rater key was sealed; key unsealed in
  d37141b; write-up 55fcf82.

## 2026-11-05 to 11-06: v6, glauconite and the sinkite question

- Plan fixed before any test (4198ddd, final 6cf30fb). The pre-registered
  XRF glauconite test was uninformative (e336bfc). Young-taxa check added
  (d89a285); round closed (2648e70). The cuttings cannot test the origin of
  the sands; the decisive test is age, and no sidewall cores exist.

## 2026-11-06 to 11-11: v7, photographs to chemistry

- **Step 1, photo to XRF Si/Al.** Plan draft e0588e9, final b1eeb05;
  results 9b76a2f, closed c01b131. Median held-out rank correlation +0.32,
  positive in 11 of 11 wells.
- **Step 2, pellet detector.** Plan and detector frozen before any run
  (d10e3f1). The primary test passed but the Lista specificity failed
  (5f6ef44, closed 632f9e6).
- **Step 3, mud-log sand fraction.** Plan v1 to v3 (3f6fbbc, 7b44c45,
  b328931); second-pass rule fixed before the second readings (0e3ec1d);
  results 5d5cfe9, closed e9d3896 and 676af22.
- **Extras X0 to X3 (exploratory).** Plan 400d764 and 00465b1; results
  8f87fd1 and b2d3c02; closed 0b41978.

## 2026-11-11 to 11-12: v8, more elements and where it works

- Plan 4152f8b, amended before any run c675477. Parts A and B run once
  (ad06c38, 76886b9). Part D, mud logs below the Cretaceous, run once as an
  amended, exploratory test (60818cd, 998efaf, 37991e5). Part C, three
  fine-tuning seeds: no detectable gain over frozen features.

## 2026-11-12: v9 and v10

- **v9, checks that close caveats.** Plan a062be2, amended de7b78b; K2b and
  K3 results 4ac036a; K1 and K2c followed.
- **v10, stratigraphic tops and step response.** Plan b0f01f5, amended
  0925a5d; results and review changes 54099fb. Photographs cannot place
  tops in an unseen well; the vertical resolution of cuttings could not be
  measured with these wells.
- Notes brought up to date (6acfac0).

## 2026-11-13 to 11-14: repository

- Follow-up merged into main (f3d49b5); the dissertation code is kept at
  the tag `v1-dissertation`.
- Repository reorganised into `scripts/`, `docs/` and `results/` (026ed25,
  947c71c); a check that every script compiles and every link resolves
  added (3157ea6).
