# v4 results (2026-11-05): core photographs, plugs, robustness checks

Plan: V4_PLAN.md, with amendment E after review round 8. Review rounds 1-9.
This was not an independent human expert review. Nothing here changes the v2/v3
headline (V3_RESULTS.md).

## 1. What was tried

Core photographs were meant to give bed-scale ground truth that does not come
from gamma ray. Cores exist in all eleven wells. Cuttings bags were taken every
2.5-3 m straight through the cored intervals: 337 cuttings photographs in 7
wells. The cores are mostly the deep reservoir section (Triassic/Jurassic red
beds, Brent), not the shallow overburden. The only Tertiary cores (24/9-3,
24/9-4) have few bags.

## 2. Core-photo digitisation: stopped (pre-set gate failed)

- **Raters:** A and B, two models (see Use of AI in the README). They were blind
  to everything but the white-light core photographs, and followed one
  written protocol (V4_DIGITISER_PROTOCOL.md, version 2 after review).
- Both raters are models from one family, so their errors are likely
  correlated. Agreement is an upper bound on reliability, not a measure of
  accuracy.

| pilot well | bins | SAND-vs-rest kappa | 5-class kappa | per-metre sand fraction r |
|---|---|---|---|---|
| 34/4-6 (thick sandstone, protocol v1) | 244 | 0.98 | 0.90 | 0.99 |
| 34/7-10 (basal Amundsen, Statfjord Gp Nansen/Eiriksson/Raude, 2522-2663 m; protocol v2) | 524 | **0.50** (gate 0.6) | 0.75 | 0.70 |

- **Bias is one-directional.** In 34/7-10, A called SAND in 51 bins where B
  called HET (26) or MUD (25); the reverse happened 2 times. So one rater is
  biased; the v5 panel found it is B, under-calling clean, plug-proven
  sandstone (V5_RESULTS.md).
- **Confident calls agree.** Where both raters were confident, kappa is
  0.97 (64 bins). Keeping only those bins leaves 2 of 48 bags with >= 50%
  coverage, which is unusable and selects the easy beds.
- **The core record is poor.** 44% of the 34/7-10 bins are rubble, mostly
  mudstone chips. Colour agreement is 0.61.
- **Protocol deviation.** A's last 6 photographs were done in a separate
  run that corrected a cyan cast with the grey scale; B's were not
  corrected.
- **Finding (rewritten after the v5 panel, V5_RESULTS.md):**
  - The pre-set agreement gate failed (kappa 0.50).
  - A blind, evidence-based adjudication showed this was mainly one rater
    (B) calling clean sandstone HET or MUD, plus a real silt / very fine
    sand boundary problem.
  - The core photographs themselves are readable for clean sandstone.
  - The test is not reopened (the stop rule was pre-registered).

## 3. Plug-referenced check, 34/8-3, 2839-2897 m (descriptive)

- 18 bags (2.5 m spacing), all with plugs; bottom-interval support.
- **Gate** (XRF Si/Al vs median log-permeability): rho +0.48, PASS (95% CI 0.02 to 0.77: a marginal pass).

| signal | rho vs median log-k | rho vs median porosity |
|---|---|---|
| clear-grain size (ONE_FEATURE) | +0.33 | +0.29 |
| ResNet-50 (D1) | +0.39 | +0.22 |
| E2 | +0.09 | +0.19 |
| colour (-a*) | -0.30 | -0.46 |
| bag dry weight | +0.21 | +0.08 |
| core gamma (not independent of GR) | +0.73 | +0.69 |
| XRF Si/Al | +0.48 | +0.32 |

- With n = 18, rho of 0.33 to 0.39 has a 95% CI of about -0.16 to 0.72 even
  before allowing for autocorrelation, so it cannot be told from zero.
- The colour baseline's pre-specified direction (less red = sand) was
  designed for the Lunde. The grey Brent has no red beds, so its negative sign
  is uninformative.
- This is one interval in one well, in GR-labelled zones where the held-out
  AUC was already 0.97-0.99.
- **Reading:** consistent with weak bed-scale information where bags
  represent the rock. Not a demonstration of it.

## 4. Robustness and other checks

- **Cement mask:** the pre-registered shallow XRF test was rerun without
  photographs 0-15 m below every 30"/20"/13 3/8" shoe (24 of 893 removed).
  ONE_FEATURE +0.124, 7/10, p 0.024 (run 2: 0.014); D1 p 0.024. Unchanged.
- **24/9-3 label validity.**
  - The only Tertiary core with plugs (1778-1797 m, Frigg Fm) is 3 D sand at
    38% porosity.
  - The v2 GR rule labelled its cuttings depths clay or mixed: zone
    r3_upper, anchors 19/35 API, so a sand reading 30-35 API becomes "clay".
  - This is the only check of the GR labels against direct core evidence in
    the Tertiary. (XRF and the 34/8-3 plugs are other non-GR checks.) It shows
    the labels can call a high-porosity sand clay.
  - Only 2 of the 15 r3_upper clay labels lie inside the core (1789, 1792 m).
    12 are inside the suspect shale-anchor interval (1840-1910 m) and 1 is
    just above it (1837 m).
  - Dropping all 15 r3_upper clay labels: E2 median AUC 0.694, 6/7, p 0.039;
    D1 0.743, 7/7. Unchanged.
- **Fine-tuned CNN (exploratory).** Its numbers were computed, p-values
  included, before the review asked for "no test" to be declared in
  advance.

  | model | median AUC | wells > 0.5 | local50 wells > 0.5 | vs relative depth |
  |---|---|---|---|---|
  | C1 (v1 recipe) | 0.71 | 7/7 | 3/6 | p 0.055 |
  | C2 (per-well colour normalisation) | 0.70 | 7/7 | 5/6 | p 0.023 |

  No better than frozen ResNet-50 embeddings.
- **Data hygiene found.**
  - `24_9-3_708-12023.SPW` is mislabelled: its header says well 16/10-1
    (AGIP). Excluded.
  - The 34/8-3 A plug block has blank fixed-width fields that misalign
    token parsing. Excluded by a validity gate.

## 5. Bottom line after v4

Unchanged: a signal at interval scale that transfers between wells, and
no demonstrated bed-scale skill. v4 adds three things for the methods chapter:
1. Two model raters agree on thick sandstone and disagree directionally in a
   red-bed core (agreement, not accuracy; one well each).
2. Plugs give weak, non-significant support for some bed-scale information
   where bags represent the rock.
3. GR-derived labels can be wrong in weak-contrast zones (the 24/9-3 Frigg
   sand).

## 6. Open: human spot-check

- **Page:** an online labelling page (not kept). 40 bins of
  34/7-10, blind (25 disputed, 15 agreed). The answer key is in
  `results/v4/spotcheck_key.csv`; do not open it before labelling.
- When it is done: rater-human kappa per rater, and which rater is biased.
