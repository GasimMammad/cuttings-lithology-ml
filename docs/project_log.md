# Project log

A dated record of the follow-up to the dissertation. Each round has a plan
committed before it was run and a results file that ends with the review
and the changes it required. The commits named here fix the order: plan,
then code, then a single run, then the write-up.

## 2026-11-05: v2 to v5

- **v2, sand against clay in ten wells.** Labels for eleven wells (one zone
  per open-hole run) and the analysis plan committed together (fae9a09).
  The primary test passed: median held-out AUC 0.73, Wilcoxon p 0.039
  (b11c7fb).
- **v3, baselines and the first XRF test.** Plan revised after review
  (92ebf1f); results with both XRF runs (e7435e5, 740e8b0). Depth within
  the well does as well as the photographs.
- **v3b, bag-interval labels.** Plan (3819cad) and amendment (edd7b4a)
  before computation; the criterion was not met (89b13d3).
- **v4, core photographs.** Plan (937ceab); pilot rater agreement
  (d59e67c); the hard-well pilot failed the agreement gate and core
  digitisation was stopped. Results a04665a, corrected 75e08e4.
- **v5, panel adjudication of the core raters.** Plan (18a22a9) and
  amendment (ec56735) while the rater key was sealed; key unsealed in
  a063025; write-up f903105.

## 2026-11-05 to 11-06: v6, glauconite and the sinkite question

- Plan fixed before any test (98440f5, final 8c58848). The pre-registered
  XRF glauconite test was uninformative (74bcb4e). Young-taxa check added
  (f5c9070); round closed (b493104). The cuttings cannot test the origin of
  the sands; the decisive test is age, and no sidewall cores exist.

## 2026-11-06 to 11-11: v7, photographs to chemistry

- **Step 1, photo to XRF Si/Al.** Plan draft fdaf336, final 68502f3;
  results b037b13, closed 8e64786. Median held-out rank correlation +0.32,
  positive in 11 of 11 wells.
- **Step 2, pellet detector.** Plan and detector frozen before any run
  (d8849af). The primary test passed but the Lista specificity failed
  (a4bebab, closed 71cfa4c).
- **Step 3, mud-log sand fraction.** Plan v1 to v3 (b838edc, 62999ab,
  9ba71d9); second-pass rule fixed before the second readings (6ca8c46);
  results ea99d68, closed 49b33f7 and 1f5b032.
- **Extras X0 to X3 (exploratory).** Plan 9d8a9de and 97720ec; results
  3055b71 and 0683b62; closed eafaa33.

## 2026-11-11 to 11-12: v8, more elements and where it works

- Plan 18fba28, amended before any run d28ac7a. Parts A and B run once
  (27add00, d34ec26). Part D, mud logs below the Cretaceous, run once as an
  amended, exploratory test (ec0a3f8, 435425c, a5e71b5). Part C, three
  fine-tuning seeds: no detectable gain over frozen features.

## 2026-11-12: v9 and v10

- **v9, checks that close caveats.** Plan 5ae822d, amended 2b5b65d; K2b and
  K3 results 13dca6e; K1 and K2c followed.
- **v10, stratigraphic tops and step response.** Plan 20a3884, amended
  f77ab23; results and review changes 0cc1e26. Photographs cannot place
  tops in an unseen well; the vertical resolution of cuttings could not be
  measured with these wells.
- Notes brought up to date (14d0cb0).

## 2026-11-13 to 11-14: repository

- Follow-up merged into main (645ddd4); the dissertation code is kept at
  the tag `v1-dissertation`.
- Repository reorganised into `scripts/`, `docs/` and `results/` (a2dfebc,
  c3279dd); a check that every script compiles and every link resolves
  added (8fc6e07).
