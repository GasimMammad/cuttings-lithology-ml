# v5 results: expert-agent panel adjudication of the 40 spot-check bins (34/7-10)

- **Plan:** V5_PANEL_PLAN.md (2963df1), amended after reviewer round 1
  (e9e58cb).
- **Consensus locked before unsealing:** f595585. Unsealed: d37141b.
- **Panel (all Claude Opus agents; not human experts):**
  - Agent 1, petrophysicist / core analyst: operator core description,
    plugs, logs, photos, literature.
  - Agent 2, geochemist: cuttings XRF, literature.
  - Agent 3, reviewer: challenged both.
- **Rounds:** 2 rounds of revisions, then final adjudication by Agent 3.

## Result

The primary scoring is SAND vs NOT-SAND (MUD, OTHER). UNRESOLVED,
UNRESOLVED-SILT and NO-CORE are left out.

**Primary result (24 resolved bins):**

| rater | correct | 95% CI (Wilson) |
|---|---|---|
| A (Opus) | 23/24 | 0.80-0.99 |
| B (Sonnet) | 10/24 | 0.24-0.61 |

- **Disputed stratum (15 resolved):** the consensus was SAND 14 times (A
  right) and NOT-SAND 1 time (B right). P(A right) 0.93 [0.68-1.00], exact
  binomial p 0.001.
- **Agreed stratum:** both raters wrong together 0/9.

**Sensitivities:**

| check | A | B | disputed A:B | p |
|---|---|---|---|---|
| S1: UNRESOLVED-SILT = NOT-SAND | 27/35 | 21/35 | 14:8 | 0.29 |
| S2: UNRESOLVED-SILT = SAND | 30/35 | 10/35 | 21:1 | < 0.001 |
| S3: drop i29, i35 | 21/22 | 9/22 | - | 0.002 |
| S4: i27 = MUD | 24/25 | 11/25 | - | 0.001 |

**Consensus labels (all 40 bins):**

| label | n |
|---|---|
| SAND | 19 |
| MUD | 5 |
| UNRESOLVED-SILT | 11 |
| UNRESOLVED | 4 |
| NO-CORE | 1 |

## Interpretation (agreed with Agent 3)

- Where the panel could resolve a disputed bin, the evidence almost always
  supported A's SAND call (14 of 15; p = 0.001). Rater B under-called clean,
  plug-proven sandstone.
- A further 7 disputed bins were siltstone or very fine sandstone with no
  grain-size data. If those count as not-sand, A's advantage is no longer
  significant (14 vs 8; p = 0.29). Part of the disagreement is therefore a
  class-boundary problem, not a bias of one rater.
- **Resolution is uneven between classes.** Plugs are taken mostly in
  sandstone, so sand bins resolve easily. Mud and silt bins rely on 1 m
  operator descriptions and stay unresolved (10 of 25 disputed). The claim is
  therefore "B under-calls clean, plug-proven sandstone", not "B is wrong in
  general".
- **Shared-family caveat** (panel = Opus = rater A): weak here. 14 of the 15
  resolved disputed bins are SAND by plugs (k from mD to D), not by the photo.
- **The earlier suspicion was wrong.** In V4_RESULTS the bias was suspected
  to be A over-calling sand. That was wrong; the panel shows B
  under-calling.

## Consequence for v4

V4_RESULTS.md section 2 is rewritten as follows.
- The pre-set agreement gate failed (kappa 0.50).
- A blind, evidence-based adjudication showed this was mainly one rater
  (Sonnet) calling clean sandstone HET or MUD, plus a real silt / very fine
  sand boundary problem.
- The core photographs themselves are readable for clean sandstone.
- The core test is NOT reopened. The stop rule was pre-registered; choosing
  rater A after seeing which rater was right would be post hoc; and 24
  resolved bins in one well are too few to validate a single rater.
- Future work: single-rater digitisation validated against plugs.

## Data hygiene notes from the panel

- The operator core description is completion report Enclosure III, PDF
  p.168, in 1 m steps. Agent 2 OCR'd scanned PDFs with macOS Vision; Agent 1
  installed PyMuPDF into the scratch folder only.
- The lab plug descriptions (SPWLA) and the wellsite description disagree
  over 2522-2531.5 m (calcareous very fine sandstone vs siltstone). This is
  the origin of most UNRESOLVED-SILT labels.
- Drilling mud: KCl-barite. Ba reaches 8.8% in the cuttings bags and corrupts
  Si/Al and K/Al. Ba-residualised Si/Al tracks the logs (rho about -0.45 to
  -0.50 at bag scale).
- Two literature references were cited from memory and not verified; do not
  cite them without checking.
