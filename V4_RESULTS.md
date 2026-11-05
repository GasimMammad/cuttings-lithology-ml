# v4 results (2026-11-05): core photographs, plugs, robustness checks

Plan: V4_PLAN.md, with amendment E after review round 8. Reviewer: senior
geoscientist / ML persona agent, rounds 6-8. Nothing here changes the v2/v3
headline (V3_RESULTS.md).

## 1. What was tried

Core photographs were meant to give bed-scale ground truth that does not come
from gamma ray. Cores exist in all eleven wells. Cuttings bags were taken every
2.5-3 m straight through the cored intervals: 337 cuttings photographs in 7
wells. The cores are mostly the deep reservoir section (Triassic/Jurassic red
beds, Brent), not the shallow overburden. The only Tertiary cores (24/9-3,
24/9-4) have few bags.

## 2. Core-photo digitisation: stopped (pre-set gate failed)

- **Raters:** Claude Opus (A) and Claude Sonnet (B) agents. They were blind
  to everything but the white-light core photographs, and followed one
  written protocol (V4_DIGITISER_PROTOCOL.md, version 2 after review).

| pilot well | bins | SAND-vs-rest kappa | 5-class kappa | per-metre sand fraction r |
|---|---|---|---|---|
| 34/4-6 (thick sandstone, protocol v1) | 244 | 0.98 | 0.90 | 0.99 |
| 34/7-10 (Statfjord red beds, protocol v2) | 524 | **0.50** (gate 0.6) | 0.75 | 0.70 |

- **Bias is one-directional.** In 34/7-10, A called SAND in 51 bins where B
  called HET (26) or MUD (25); the reverse happened 2 times. So one LLM rater
  is biased, most likely A toward sand. A human check is needed to say which
  (section 6).
- **Confident calls agree.** Where both raters were confident, kappa is
  0.97 (64 bins). Keeping only those bins leaves 2 of 48 bags with >= 50%
  coverage, which is unusable and selects the easy beds.
- **The core record is poor.** 44% of the 34/7-10 bins are rubble, mostly
  mudstone chips. Colour agreement is 0.61.
- **Protocol deviation.** A's last 6 photographs were done by a fresh
  session that corrected a cyan cast with the grey scale; B's were not
  corrected.
- **Finding:** in red-bed cores, the photographic core record does not
  support a reliable bed-scale lithology reference from AI digitisation. On
  thick sandstone it does.

## 3. Plug-referenced check, 34/8-3, 2839-2897 m (descriptive)

- 18 bags (2.5 m spacing), all with plugs; bottom-interval support.
- **Gate** (XRF Si/Al vs median log-permeability): rho +0.48, PASS.

| signal | rho vs median log-k | rho vs median porosity |
|---|---|---|
| clear-grain size (ONE_FEATURE) | +0.33 | +0.29 |
| ResNet-50 (D1) | +0.39 | +0.22 |
| E2 | +0.09 | +0.19 |
| colour (-a*) | -0.30 | -0.46 |
| bag dry weight | +0.21 | +0.08 |
| core gamma (not independent of GR) | +0.73 | +0.69 |
| XRF Si/Al | +0.48 | +0.32 |

- With n = 18, rho around 0.35 cannot be told from zero (approx. 95% CI -0.1
  to 0.7).
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
  - This is the only direct non-GR check of the GR labels. It shows they can
    call a high-porosity sand clay.
  - Dropping all 15 r3_upper clay labels: E2 median AUC 0.694, 6/7, p 0.039;
    D1 0.743, 7/7. Unchanged.
- **Fine-tuned CNN (exploratory).** Its numbers were computed, p-values
  included, before the reviewer asked for "no test" to be declared in
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
1. AI digitisation of core photographs is reliable on thick sandstone and
   unreliable in red beds (directional bias, rubble).
2. Plugs give weak, non-significant support for some bed-scale information
   where bags represent the rock.
3. GR-derived labels can be wrong in weak-contrast zones (the 24/9-3 Frigg
   sand).

## 6. Open: human spot-check

- **Page:** https://claude.ai/artifact/KYeehqu5ZkBi6ViMVHRonr. 40 bins of
  34/7-10, blind (25 disputed, 15 agreed). The answer key is in
  `results/v4/spotcheck_key.csv`; do not open it before labelling.
- When it is done: agent-human kappa per rater, and which rater is biased.
