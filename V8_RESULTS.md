# v8 results (plan: V8_PLAN.md with the reviewer's amendments; each part run once)

v7 is closed and unchanged. Scripts were committed before each run.
Result files: results/v8/.

## A. More elements from the same photographs (63_v8_elements_when.py A)

Set S, model R-D, leave-one-well-out, per-well +/-50 m high-passed Spearman,
11 wells, as step 1. Targets: within-well z of log10(element / Al).

| target | median rho | wells > 0 | Holm p | mud partial | beyond Si and Al (Holm p) | Si/Al model reused (paired p) | colour model R-E (paired p) | counts |
|---|---|---|---|---|---|---|---|---|
| K/Al | +0.20 | 11 | 0.002 | +0.18 | +0.06 (0.051) | +0.19 (0.48) | +0.08 (0.002) | no |
| Fe/Al | +0.28 | 11 | 0.002 | +0.29 | +0.14 (0.002) | +0.09 (0.002) | +0.23 (0.23) | **yes** |
| Ca/Al | +0.19 | 11 | 0.002 | +0.17 | +0.13 (0.010) | +0.13 (0.005) | +0.18 (0.58) | **yes** |
| Ti/Al | +0.27 | 10 | 0.003 | +0.21 | +0.16 (0.004) | +0.26 (0.55) | +0.18 (0.087) | **yes** |
| Zr/Al | +0.10 | 10 | 0.003 | +0.03 | +0.12 (0.019) | +0.02 (0.027) | +0.15 (0.45) | no |

Columns: "mud partial" = partial rho given high-passed Ba and Cl (plus S
for Ca, plus Sr for Zr). "Beyond Si and Al" = partial rho given high-passed
log Si and log Al. "Si/Al model reused" = the step-1 prediction scored
against this target, sign fixed from the other wells; the p is the paired
test that the element's own model does better. "R-E" = engineered colour
and texture features; the p is the paired test that R-D does better.

- **All five targets pass** the step-1 rule (Holm p < 0.05, median >= 0.10).
- **Three count under the pre-declared rule** (pass, beyond Si and Al, mud
  partial): Fe/Al, Ca/Al, Ti/Al. The rule needed two, so the pre-declared
  wording applies: **the photographs give a rough chemical log, not only a
  quartz-clay axis.**
- K/Al misses the "beyond" criterion by a hair (Holm p 0.051) and is not
  counted. Zr/Al fails the mud control (+0.03).
- What tempers this:
  - **Fe and Ti move together** in every well (high-passed rho(Fe, Ti)
    0.39 to 0.74). They may be one axis (Fe-Ti-bearing clay and heavy
    minerals, or a contaminant), not two. Counting them as one still leaves
    two (Fe-Ti and Ca).
  - **For Fe, Ca and Zr the deep-network features do no better than simple
    colour and texture features** (paired p 0.23, 0.58, 0.45). The
    photographs carry this chemistry mostly as colour. Only for K do the
    embeddings clearly add (p 0.002).
  - **For Ti and K the Si/Al model reused does as well as the element's own
    model** (paired p 0.55, 0.48). Their own models are not specific. Ti
    still counts because its partial given Si and Al is positive in 10 of
    11 wells.
  - The sizes are small: +0.2 to +0.3 at bag scale, as for Si/Al.
- Flags: rho(K, Cl) is 0.27 to 0.40 in three wells (24/9-4, 34/7-6,
  34/8-3), a sign of KCl mud; K was not counted anyway.
- Ca/Al here (+0.19) against step 1's Ba-residualised Ca (+0.12): the same
  direction, a different target.

## B. When does the method work? (63_v8_elements_when.py B)

Hypothesis fixed beforehand: agreement is higher where the measured Si/Al
varies more.

| test | result |
|---|---|
| B1, between wells: step-1 rho against the spread (MAD) of measured high-passed log10(Si/Al) | Spearman +0.78, exact permutation p = 0.003 (n = 11) |
| B2, within wells: 150 m windows, window rho against window spread | median per-well Spearman +0.54; 7 positive, 1 zero, 2 negative of 10 wells; p = 0.014 |
| B3, label-free, within wells: window rho against the spread of the PREDICTION | median +0.48; 9 of 10 wells positive; p = 0.003 |
| B3, label-free, between wells | Spearman +0.47, p = 0.073 |
| B4, Tertiary against pre-Tertiary (descriptive) | the section with the larger spread has the higher rho in 8 of 10 wells |

- **Skill follows the spread of the chemistry** (B2 p < 0.05 and B1 the
  same sign: the pre-declared condition). A positive B2 is what
  measurement-error attenuation predicts: where the true Si/Al hardly
  changes, XRF noise dominates the target and nothing can correlate with
  it.
- **A label-free indicator is supported within wells:** intervals where the
  model's own output varies more are the intervals where it agrees better
  with the chemistry. Between wells the same indicator is weaker (p 0.07).
- This explains the failing well. 34/8-3 and 34/8-3 A have the smallest
  spread of Si/Al of the 11 wells (MAD 0.022 and 0.020 in log10 units) and
  the lowest rho (+0.03, +0.18). The four wells with the largest spread
  (24/9-3, 34/7-9, 34/7-4, 34/7-10; MAD 0.032 to 0.049) have the highest
  rho but one (+0.46 to +0.53).
- Descriptive, no test: rho is unrelated to the number of bags (-0.02),
  and wells with 10 m sampling score higher than wells with 3 m sampling
  (+0.59 with spacing), which is the same effect seen another way (a 10 m
  composite averages more rock).
- Limits: 82 windows, most of them at the 15-bag minimum, so each window
  rho is noisy; B1 has 11 points; no threshold was pre-declared, so none is
  offered. The practical statement is qualitative: trust the photo log
  where it moves, not where it is flat.
