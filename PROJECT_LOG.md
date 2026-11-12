# PROJECT LOG: cuttings-photo lithology ML (MSc "Looking for Sinkites")

Single reference file for the whole follow-up work (started 2026-11-05).
**Read this first after any context reset.** Keep it updated at every step.

---------------------------------------------------------------------------
## 0. Ground rules from the user

- **Do not delete the original project.**
  - The original repo `~/Projects/cuttings-lithology-ml` and its outputs
    `~/sinkite_ml_work` stay intact.
  - The only change to the original repo: `config.py` SSD path ->
    `/Volumes/T9/...`, a header added to `12_glauconite_test.py`, and a
    `.venv` (gitignored). All uncommitted.
- All new work lives in a separate copy: `~/Projects/cuttings-lithology-ml-v2`
  (git branch `v2-ten-wells`, repo-local git identity = original author).
- Work autonomously. The user is often away.
- **Use the senior reviewer agent** for the rest of the project. It should
  question every step: before computing (plan review) and after (results
  review).
- **"Don't rush":** wait for the reviewer before computing anything new.
- **Think twice, question yourself.**
- No conference slide deck for now.
- Conference is in about 1 month (early Dec 2026).
- **Keep this log updated** to survive auto-compaction.

## 1. Environment and paths

| what | where |
|---|---|
| Data drive (read-only) | `/Volumes/T9/GasimMammadov_MasterProject2026/Wells/<well>/` (DRILLING, LOGS, ROCK_AND_CORE, GEOLOGY ...); `Wells/files/` = NPD formation tops |
| v2 repo | `~/Projects/cuttings-lithology-ml-v2` |
| v2 outputs | `~/sinkite_ml_work_v2/` (labels, features, embeddings, `v2_results/`, `v3_results/`, `logs/`, `core_thumbs/`) |
| tiles (224 px) | `~/sinkite_ml_data_v2/patches/<well>/<stem>__r{j}c{i}.jpg` (80,608 tiles = 5,038 W_1 photos x 16) |
| Python | `~/Projects/cuttings-lithology-ml/.venv/bin/python` (v2 has a symlink `.venv`) |
| Scratch | `/private/tmp/claude-501/-Users-gasimmammadov-Projects-cuttings-lithology-ml/6549f91e-15d0-4896-b785-21197e925e4a/scratchpad/` (`dl/casing.csv`, `dl/core.csv` = Sodir tables; `page/` = results page; `mud/` = 34/7-1 mud-log scan) |
| Results page (artifact) | https://claude.ai/artifact/RwqvWSiQp2PEkypgCq87u7 (publish from `scratchpad/page/cuttings_lithology_v2.html`, same path keeps the URL) |
| Memory | `~/.claude/projects/-Users-gasimmammadov-Projects-cuttings-lithology-ml/memory/` |

**Gotchas**
- Mac is an Apple M4 (4 performance + 6 efficiency cores), 16 GB RAM.
  - On battery it throttled badly (about 2 h lost). Keep long jobs for AC power.
  - Set `OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1` for parallel CPU jobs.
- T9 reads at only about 33 MB/s (USB 2 speed), so big reads take long.
- python.org Python has no SSL certificates. Download with `curl` (the
  ResNet-50 weights were fetched with curl and the sha256 checked).
- lasio has no `ignore_data_errors` kwarg here.
- Sodir CSV tables: `https://factpages.sodir.no/public?/Factpages/external/tableview/<table>&rs:Command=Render&rc:Toolbar=false&rc:Parameters=f&IpAddress=not_used&CultureCode=en&rs:Format=CSV&Top100=false`
  (tables used: `wellbore_casing_and_lot`, `wellbore_core`).
- **Reviewer agent:** agentId `ac906ee9f47edc97f`. Resume with SendMessage
  `to: ac906ee9f47edc97f`. Persona: senior North Sea geoscientist (30+ yr) and
  ML expert. It runs read-only.

## 2. Timeline and decisions (chronological)

### 2.1 v2: eleven wells, label audit, pre-registered test

- **Label audit** (`config.py` "v2 LABEL DESIGN", `V2_LABEL_DECISIONS.md`).
  Rules:
  1. One label zone = one open-hole wireline run, both anchors in that run,
     below the casing shoe (Sodir casing table).
  2. Exclude Balder (tuff, low GR), Ness (coal), Rannoch (micaceous, high
     GR), Draupne (hot).
  3. Sand anchor = cleanest blocky named sand; shale anchor = homogeneous
     Hordaland/Lista claystone (Drake in the Jurassic).
- **Findings from the audit:**
  - The PARTB 34/8-3 "sand bodies" at 1204-1311 m are casing attenuation
    (13 3/8" shoe at 1302 m).
  - The 34/7-1 v1 sand anchor sat inside the 30" conductor, so 34/7-1 gets
    no labels.
  - The 24/9-3 and 24/9-4 v1 anchors were cross-run.
  - 34/4-7 "body" 1701-1720 m = Balder.
- **Labels:** 123 sand / 467 clay W_1 depths in 10 wells (v1: 85 sand in 3
  testable wells).
- **Pipeline:**
  - 25 index, 03 labels, 26 tiles (sharded)
  - 28 engineered features: frozen 15 features; `features.py` got an exact
    18x faster disk opening, verified array-equal
  - 27 ResNet-50 embeddings, RGB + grey, frozen
  - 29 evaluation, 30 figures, 32 report
- **Pre-registered (`V2_PLAN.md`):**
  - Primary = E2 (engineered + label-free per-well z).
  - Endpoint = per-well AUC over 7 eligible wells, one-sided Wilcoxon.
- **Result:**
  - E2 median AUC 0.73, 6/7 wells, p = 0.039, permutation p = 0.035.
  - All 6 models pass Holm.
  - Tertiary-only 5/5 wells (p = 0.031, the minimum possible).
  - Report: `results/report.txt`.

### 2.2 v3: independent review (reviewer rounds 1-3)

- **Plan:** `V3_PLAN.md`. Results: `V3_RESULTS.md` (reviewer-agreed
  headline).
- **What the review overturned:**
  - The v2 depth-only baseline was a straw man (pooled sign). A fair
    relative-depth baseline gives AUC 0.57, 6/7 wells.
  - E2 does not beat it (paired p = 0.148).
  - E2 has local AUC (pairs < 50 m) 3/6: no bed-scale skill.
  - The permutation null is centred at 0.64.
  - One feature chosen in-fold (`bright_lowsat_meanarea`, clear-grain size)
    reaches 0.84. D1 (ResNet raw) 0.73, 7/7. Both beat relative depth
    (p = 0.039).
- **Bag dry weight** (NOROG cuttings-analysis CSV) alone: AUC 0.84; photos
  add +0.03 to +0.05, n.s.
  - But above the 20" shoe, weight is anti-correlated with Si/Al in 5/5
    wells, so it is a processing artefact.
- **Pre-registered shallow test** (unlabelled Tertiary vs cuttings XRF Si/Al,
  high-passed +/-50 m), script `35_v3_xrf_shallow.py`:
  - Run 1: p = 0.080, flawed. Single-tile features in 34/8-3 and 34/8-3 A.
    Committed 3a32a61 before the rerun.
  - Run 2: all tiles, script unchanged. ONE_FEATURE median rho +0.11,
    7/10 wells, p = 0.014. D1 +0.25, p = 0.019.
- **D1 montage above the 20" shoe:** glacial diamicton vs clay.
  - False positive: 34/7-10 430 m = shoe-track cement (Ca/Al 8.4,
    7 m below the 30" shoe).
  - 24/9-3 510 m is shelly Utsira sand, not cement.
  - The 34/7-4 cream clasts are not carbonate.

### 2.3 v3b: bag-interval labels (reviewer rounds 4-5)

- **Plan:** `V3_PLAN.md` sections 4/4b. Scripts 39 and 40.
- **XRF only:** Si/Al fits GR averaged over the 10 m ending at the bag depth
  better than point GR (rho 0.18 vs 0.11). The bottom window beats the point
  in 4/6 wells.
- **Images:** the shift was +0.05, not significant. The pre-registered "clearly
  wins" rule failed, so there was no retraining.
- **Bed-scale level:** after high-pass, image rho is about -0.18 to +0.44.
  This confirms there is no bed-scale skill.

### 2.4 v4: core photographs (reviewer round 6), IN PROGRESS

- The user pointed to core images (Sodir FactPages). They are already on T9:
  `ROCK_AND_CORE/*CORE_PHOTO_M_TOP<cm>_W_1.TIF`, 5 trays x 1 m per photo,
  printed tray depths, about 8000x9600 px.
- **Cores:** Sodir `wellbore_core` table. Mostly deep reservoir intervals
  (Lunde/Statfjord red beds, Brent). Tertiary cores only in 24/9-3
  (1778-1797 m) and 24/9-4 (1773-1787 m), with few bags.
- 337 cuttings photos lie inside cores in 7 wells. Bags continue every
  2.5-3 m through the cores. 247 core photos are needed.
- **Digital core analysis exists** (the reviewer found these):
  - `24_9-3_CORE_CONV_RAW_1.SPWLA`, `24_9-3_708-12023.SPW`
  - `34_8-3_708-6463.SPW` (Norcore format; includes CORE GAMMA: counts,
    Th, U, K, which could give a core-to-log shift)
  - `34_8-3_A_708-6478.SPW`
  - Also `24_9-3_CORE_DESC_1981-02-19_REPORT_1.PDF` (no PDF tool on this Mac).
- **Plan:** `V4_PLAN.md`, committed 26499b5. Key points:
  - **Gate first, model-free:** XRF Si/Al vs core sand fraction, and
    redness vs red-mud fraction. Both must be positive in >= 2/3 of wells,
    else the image test is uninformative.
  - Trip-cavings sensitivity (drop the first bag after each core-run top),
    and a core-chip check.
  - **Digitisation:** 0.25 m bins; SAND / HET / MUD / OTHER / NONE, plus
    colour and confidence.
    - Raters: A Opus (all photos), B Sonnet (all), C Fable (random 20%). All
      blind; AI not human; recommend a human spot-check.
    - Kappa reported. Plug permeability > 1 mD as a check on SAND calls.
  - **Target:** f = (SAND + 0.5 HET) / (SAND + HET + MUD + OTHER), mean of
    A and B. Support (D - s + o, D + o]; o chosen by an XRF-only scan,
    -10..+5 m.
  - **Primary image test:** ONE_FEATURE, high-pass +/-15 m, per-well
    Spearman, Wilcoxon over wells with >= 10 bags.
    - Baselines: colour (-lab_a_mean, sign fixed), XRF, weight.
    - No GR reference (needs a core-to-log shift).
  - **Asymmetry stated:** a positive result is informative; a negative
    result is uninterpretable on its own.
  - **B, cement mask:** rerun the shallow XRF test without photos 0-15 m
    below the 30"/20"/13 3/8" shoes. Robustness only.
  - **C, 34/7-1 mud log:** DROPPED (not blind, low power).
  - **D, CNN:** exploratory, selects nothing.
  - **Disclosure:** the 34/7-1 cores overlap the v1 mud-log probe depths.

## 3. Current state (update every step)

- **Running in background:**
  - `31_v2_cnn.py` (C1/C2 LOWO, log `~/sinkite_ml_work_v2/logs/cnn.log`,
    output `v2_results/cnn_predictions.csv`).
  - `43_v4_core_thumbs.py` 2 shards: 1/4-res PNGs to
    `~/sinkite_ml_work_v2/core_thumbs/<well>/` (247 needed, about 50 min,
    USB-bound).
- **DONE, B cement mask** (`42_v4_cement_mask.py`): 24 of 893 test photos removed.
  ONE_FEATURE +0.124, 7/10, p 0.024; D1 +0.254, p 0.024; E2 p 0.138.
  Robust; run 2 stays the reported result.
- **PILOT running** (10:10): raters on 34/4-6 (14 photos), protocol `V4_DIGITISER_PROTOCOL.md`.
  - Rater A = Opus agent a7e52d99e92d7df45, output `core_digitised/A_opus/34_4-6.csv`.
  - Rater B = Sonnet agent a36c9997dfd73dfff, output `core_digitised/B_sonnet/34_4-6.csv`.
  - Check format and agreement before launching the other 6 wells.
- **Found:** the 24/9-3 Tertiary core (1780-1787 m) has plugs of 3-5 D permeability (clean sand),
  but the v2 GR labels at the cuttings depths there are clay/mixed. Either a
  core-to-log depth shift or a label problem (zone r3, weak GR contrast). Check later.
- **DONE, plug parser** `44_v4_plug_data.py` -> `v4_results/plug_data.csv`.
  - 24/9-3: 14 plugs, 1780-1795 m, ~3 D, phi 38%.
  - 34/8-3: 453 plugs plus core gamma.
  - 34/8-3 A: core gamma only. Its plug block was misaligned (blank fixed-width
    fields) and dropped by the >=90%-inside-cores validity gate.
  - NB `24_9-3_708-12023.SPW` is mislabelled (header = well 16/10-1, AGIP): excluded.
  - Formats: SPWLA line-based; NORCORE token-based, curve blocks 15/17, data headers 25/40,
    and headerless continuation blocks.
- **DONE, pilot digitisation** 34/4-6 (14 photos, 244 bins). A (Opus) vs B (Sonnet):
  5-class kappa 0.90, SAND-vs-rest kappa 0.98, per-metre sand fraction r 0.99.
  Script `45_v4_rater_agreement.py`. Copies in `results/v4/core_digitised_pilot/`.
  The reviewer was asked (round 7) whether to scale; its first attempt was stopped by
  a usage limit (reset 11:50) and it was resumed.
- **DONE, fine-tuned CNN (exploratory)**, `results/v3/cnn_exploratory_per_well.csv`:
  - C1: median AUC 0.71, 7/7; local50 3/6; vs rel. depth p 0.055.
  - C2: 0.70, 7/7; local50 5/6; vs rel. depth p 0.023.
  - No better than frozen D1.
  - All models fail locally in 34/7-9 (0.20-0.27).
- All 256 core thumbnails are ready.
- **Review round 7 verdict: do not scale yet.**
  - Protocol v2 (NONE split into EMPTY / RUBBLE (+ lithology) / PRESERVED-GAP; strict quarter-bins; DARK / LIGHT / MOTTLED colours).
  - Second pilot on a HARD well: 34/7-10 (Statfjord red beds), outputs in `core_digitised_v2/`.
  - Gate: SAND-vs-rest kappa >= 0.6 before scaling.
  - Add a core-gamma check (34/8-3, 34/8-3 A).
  - Human spot-check: I am not human, so I prepare ~50 stratified bins with crops for the USER to label.
  - 24/9-3 conflict: v2 r3_upper labels (0 sand, 15 clay) are suspect. The core shows a 3 D Frigg sand that the GR rule called clay (weak anchors 19/35 API). Disclose it, plus a descriptive sensitivity without r3_upper; the v2 primary stays as run.
  - CNN numbers were computed (with p-values) before the reviewer asked to pre-declare "no test"; disclose that order.
- **Hard-well pilot running** (34/7-10, protocol v2): A = Opus agent ac9c58799c349a567, B = Sonnet agent a971f6cdb793643ef.
- **DONE, r3_upper sensitivity** (`46_v4_r3_sensitivity.py`, descriptive). Dropping the 15 r3_upper clay labels:
  E2 median 0.694, 6/7, p 0.039; D1 0.743, 7/7. Conclusion unchanged.
- `45_v4_rater_agreement.py` now handles protocol v2 (`--v2`): no-core classes pooled; rubble-as-lithology sensitivity.
- **Next steps, in order:**
  2. When thumbnails are done: write the digitiser prompt (protocol in
     V4_PLAN A2); launch raters A (Opus) and B (Sonnet) per well in the
     background; C (Fable) on a random 20%. Output CSV per rater and well.
  3. Parse the plug data (SPW/SPWLA) for the precision check.
  4. Kappa, then targets, then the XRF offset scan, then the GATE. Send to
     the reviewer.
  5. Image test only if the gate passes (report either way). Reviewer
     round on results.
  6. Update V3_RESULTS/V4 results, the results page, memory, and this log.
- **Open items not planned:** fine-tuned CNN results interpretation,
  human spot-check by the user, pre-registered depth mask in the main tests.


---------------------------------------------------------------------------
## >>> RESUME HERE (paused 2026-11-05 ~12:45 at the user's request) <<<

RESUMED (evening): rater A finished 34/7-10 (a new Opus session did the last 6 photos;
it colour-corrected a cyan cast with the grey scale, which earlier sessions may not have done).
**HARD-WELL PILOT RESULT (34/7-10): GATE FAILED.**
- SAND-vs-rest kappa 0.50 (< 0.6); 5-class kappa 0.75; per-metre sand fraction r 0.70;
  rubble-as-lithology r 0.74.
- High-confidence-both bins: kappa 0.97 (n 64).
- A calls SAND where B says HET (26) or MUD (25).
- 44% of bins are RUBBLE; colour agreement 0.61.
- Do NOT scale as is. Asked the reviewer (round 8) for the way forward. Option raised:
  core gamma (34/8-3, 34/8-3 A) as an objective rater-free bed-scale reference.
- **Review round 8 decision:**
  - Stop the digitisation; report the failure as a finding (directional bias A->SAND,
    44% rubble; 34/4-6 kappa 0.98 as contrast).
  - Narrowed plug check in 34/8-3 (pre-registered in V4_PLAN.md section E).
  - Small human spot-check (40 bins of 34/7-10) for the methods chapter.
  - Then STOP new analyses and write up.
- **DONE, plug check** (`48_v4_plug_check.py`, descriptive), 34/8-3, 2839-2897 m, 18 bags at 2.5 m:
  - GATE rho(XRF Si/Al, median log-perm) +0.48: PASS.
  - rho vs log-perm: ONE_FEATURE +0.33, D1 +0.39, E2 +0.09, colour -0.30, weight +0.21,
    core gamma +0.73, XRF +0.48.
  - n = 18, so rho ~0.35 is not distinguishable from 0 (approx. CI -0.1 to 0.7).
- **DONE, spot-check page:** https://claude.ai/artifact/KYeehqu5ZkBi6ViMVHRonr (db capability; collection `labels`,
  doc per item i01..i40 {cls, conf, t}). Items/key: `49_v4_spotcheck_items.py`; key in
  `results/v4/spotcheck_key.csv` (25 disputed + 15 agreed, seed 42; the user must NOT open the key before labelling).
  Page source: `scratchpad/spot/core_spot_check.html`.
  When the user has labelled: ArtifactData list `labels`, then compare with A/B (which rater is biased).
- **DONE, write-up:**
  - `V4_RESULTS.md` with the reviewer's round-9 corrections (baf2951).
  - `THESIS_NOTES.md`: consolidated table (PR vs EX), label limitations, well independence,
    reproducibility hashes, AI-use statement draft (2080b5d).
  - Results page v4 section published (version 4).
- **Analysis phase is CLOSED** (reviewer round 8: stop new analyses). Remaining:
  1. The USER labels the 40-bin spot-check (https://claude.ai/artifact/KYeehqu5ZkBi6ViMVHRonr).
  2. Then: ArtifactData list `labels`; join with `results/v4/spotcheck_key.csv`; agent-human
     kappa for A and for B (disputed vs agreed strata); say which rater is biased; update
     V4_RESULTS section 6, THESIS_NOTES AI-use item 4, and the results page.
  3. Thesis chapter writing (the user leads).
- **v5 PANEL (user request, evening).** The user could not label the spot-check themselves and asked for an
  expert-agent panel. Plan: `V5_PANEL_PLAN.md` (2963df1). Blind items in `~/sinkite_ml_work_v2/v5_panel/items_blind.csv`.
  - Agent 1 = petrophysicist/core analyst (Opus) a7e33b0c9bb0d6af6 -> `agent1_R1.csv`.
  - Agent 2 = geochemist (Opus) a72aa7c4ecae9154e -> `agent2_R1.csv`.
  - Agent 3 = reviewer ac906ee9f47edc97f.
  - Independent evidence: operator core description PDFs, CORE_CONV_RAW SPWLA plugs, CDL/CNL/DIFL logs,
    cuttings XRF, literature.
  - Rounds: R1 independent -> R2 reviewer critique -> revisions (max 3) -> consensus -> reveal key.
  - Told the user: '100% correct' is not achievable; this is AI agents, not a human panel.
- **v5 DONE.**
  - Consensus locked (f595585), unsealed (d37141b).
  - A (Opus) 23/24 vs B (Sonnet) 10/24; disputed 14:1 for A (p 0.001); S1 (silt = not-sand) n.s. (p 0.29).
  - B under-calls clean plug-proven sandstone. The v4 conclusion is rewritten; the core test is NOT reopened.
  - Files: `V5_RESULTS.md`, `results/v5/`, `50_v5_unseal.py`.
  - The spot-check page for the user is no longer needed (optional).

**No background jobs are running.** Everything is committed.

1. **Hard-well pilot (34/7-10, protocol v2) is unfinished.**
   - Rater B (Sonnet) DONE: `~/sinkite_ml_work_v2/core_digitised_v2/B_sonnet/34_7-10.csv`,
     524 bins. 44% RUBBLE (219 MUD-chip rubble); 64% low confidence.
   - Rater A (Opus) STOPPED after 27/33 photos (last: TOP263550). File:
     `core_digitised_v2/A_opus/34_7-10.csv`, 428 bins.
   - To finish: first check that the last photo's rows are complete (5 trays x 4 bins,
     unless the tray count is shorter); if in doubt, delete that photo's rows. Then launch
     a NEW Opus rater for the remaining photos only: TOP263550 (if removed), TOP264000,
     TOP264150, TOP264600, TOP265100, TOP265500, TOP266000. Append to the same CSV.
     Use the same prompt as before; the protocol is `V4_DIGITISER_PROTOCOL.md` v2.
2. Then run `python 45_v4_rater_agreement.py 34_7-10 --v2`.
   - Gate (review round 7): SAND-vs-rest kappa >= 0.6 before scaling.
3. Send the pilot result to the reviewer (agentId ac906ee9f47edc97f, round 8) and WAIT
   for its verdict (user: "don't rush").
4. If approved, scale to 34/4-7, 34/7-1, 34/7-9, 34/8-3, 34/8-3 A, and redo 34/4-6
   under protocol v2.
   - Raters A (Opus) and B (Sonnet) on all; C (Fable) on a random 20%.
   - Run `47_v4_core_gamma_check.py --v2` (core gamma / plugs).
   - Build the human spot-check set for the USER: ~50 bins, stratified to over-sample
     HET, low-confidence, RED and RUBBLE, from >= 2 hard wells, with crops. I am not
     human; the user labels them.
5. Then: target f per bag; XRF offset scan; GATE; image test (V4_PLAN.md A3-A5).
   Reviewer round on the results. Update V3/V4 results, the results page, memory and
   this log.

**Usage note:** the reviewer agent hit a 5-hour account usage limit once (reset
11:50). If agents fail with a rate limit, wait for the reset and resume them with
SendMessage.
---------------------------------------------------------------------------

## 4. Key result numbers (for quick reference)

| test | number |
|---|---|
| v2 E2 held-out AUC (7 wells) | median 0.73, 6/7, p 0.039 |
| fair relative-depth baseline | 0.57, 6/7 |
| E2 vs relative depth | paired p 0.148 |
| ONE_FEATURE / D1 vs relative depth | p 0.039 each |
| local AUC < 50 m: E2 / D1 / ONE_FEATURE | 3/6 / 5/6 / 5/6 wells > 0.5 |
| bag weight AUC | 0.84; photos add +0.03 to +0.05 (n.s.) |
| shallow XRF test run 2 (ONE_FEATURE) | rho +0.11, 7/10, p 0.014 (run 1: 0.080) |
| v3b XRF bag support | bottom 10 m: rho 0.18 vs point 0.11, 4/6 wells |

## 5. Commits in the v2 repo (branch v2-ten-wells)

```
c6f1aca original
acc57e0 v2 labels + V2_PLAN
c84c181 v2 scripts, fast opening
eaa36f4 v2 results
6997552 v3 plan + baselines
3a32a61 v3 XRF test run 1
826d31c v3 run 2, weight, increment, montage
730edb6 V3_RESULTS
032d5cf v3b plan
1b3baa9 v3b amendment
083813c v3b results, cement diagnostic
26499b5 V4_PLAN
```

---------------------------------------------------------------------------
## Glauconite / sinkite part review (started after v5; the user asked: did we prove anything about sinkites?)
- **Answer given:** the ML part neither proves nor disproves sinkites (interval-scale only).
- **Now reviewing** the original green-index work (scripts 15-24, ~/sinkite_ml_work reports).
- **My provisional points:**
  1. The index is not glauconite-specific: deep control fires 25-100x in Lista/Lunde; the chroma gate is inert.
  2. Utsira control is strong in 34/4-6, 34/7-1, 34/8-3 A and weak (~3x) in the mound wells.
  3. Oligocene green is concentrated 0-30 m below THGU (caving/lag pattern).
  4. 34/7-6: the photo null is uninformative by rule; the GR/AI log test says the target sand is clean with no K
     excess (strong negative for glauconite).
  5. Script 12 does not hold the calibration (reproducibility gap).
- **Sent to the reviewer** (critique, reruns) and to the geochemist (XRF K/Al-Fe/Al glauconite proxy feasibility).
- **Reviewer verdict (glauconite part):**
  - No evidence FOR sinkites.
  - The only meaningful result: in 34/7-6 the logs show the Oligocene target sand has little or no glauconite (against a
    glauconitic Utsira source there).
  - My point 3 was wrong: the near-THGU pattern fits BOTH caving and sinkites.
  - Overclaims: README "Utsira fired in 5 of 7" (circular + single photos; honest ~1-2 of 6); index should be named
    "green index"; "fire > background" is noise-level.
  - STAGE3lite's GR/AI "glauconite" labels are confounded by opal-CT.
- **Geochemist (XRF feasibility, exploratory, not pre-registered):**
  - Combined K-and-Fe excess G (within-well normalised) is a feasible bag-scale proxy.
  - Utsira fires in ~5/7 Tampen wells; Lista 0/87.
  - The Oligocene targets (34/7-6 1218-1283 m; 34/7-10 1314-1328 m) are NOT glauconitic.
  - The signal below THGU sits in the first ~40 m (caving and sinking still not separated).
  - KCl mud absent in checked Tertiary sections; 34/8-3 suspect (K tracks Cl).
  - Output: `results/v5/xrf_glauconite_feasibility_windows.csv`.
- **Recommended reruns (ranked):**
  1. spectral GR (Th/K) in 34/4-6, 34/7-1, 34/8-3;
  2. pre-registered XRF G test (in- vs out-of-sand, caving vs sinking);
  3. biostratigraphy of the target sands (decisive);
  4. formal caving regression;
  5. blind pellet check on full-res photos;
  6. the GR/AI test in 34/7-10 and 34/4-6 with fixes;
  7. README/figure corrections.
- **Awaiting the user's choice** of which to run.

## v6 (sinkite tests) STARTED. The user said: go ahead with corrections + reruns; save everything.
- Plan draft: `V6_SINKITE_PLAN.md`:
  - A corrections;
  - B biostrat of the Oligocene sands (decisive; SWC/core rule);
  - C spectral GR Th/K;
  - D pre-registered XRF G test (caving vs sinking);
  - E pellet check;
  - F GR/AI redo.
- The existing biostrat compilation is in `~/sinkite_ml_work/biostrat`:
  - 34/4-6 Oligocene sand 1359-1387 m sits in the "latest Early Oligocene" unit, described as "coarse white
    quartzose sand";
  - Sr ages exist only for mudstones and Utsira.
- **Next:** reviewer check of V6 plan -> commit -> run B (Agent 1), C, D (Agent 2 / me) -> reviewer.
- **V6 plan FINAL** (reviewer round 12): C dropped (no NGT coverage); B rule tightened; D fixes. Next: A (me), B (Agent 1), D (me), E (agent), F (me).
- **v6 D DONE** (`51_v6_xrf_glauconite.py`; `results/v6/D_*`):
  - PRE-REGISTERED VERDICT = UNINFORMATIVE. The Utsira control fired 1/5: the Al floor removed most low-Al Utsira
    sand bags, and 34/4-7 and 34/7-1 have no Oligocene baseline.
  - Lista 0% (pass).
  - Sand test empty (GR-sand bags only in 34/7-6 (6) and 34/4-6 (1); none fire).
  - Named targets 34/7-6, 34/7-10, 34/4-6: G <= 0.03, none fire (not glauconitic).
  - EXPLORATORY (no Al floor): Utsira fires in 4/5 wells with baseline + Utsira bags; Lista 0/147.
- **v6 A DONE:** `GLAUCONITE_CORRECTIONS.md`.
- **v6 B running:** Agent 1 (a7e33b0c9bb0d6af6), outputs in `~/sinkite_ml_work_v2/v6/B_*.csv`.
- **v6 E running:** blind pellet rater (Opus agent a56b10b9849c191a3), 20 photos (10 high-G, 10 low-G Oligocene), items `v6/E_items_blind.csv`; sealed key `results/v6/E_pellet_key.csv`; output `v6/E_ratings.csv`.
- v6 F (GR/AI redo) NOT started; lowest priority.
- **v6 E DONE** (blind pellet rater; unsealed `results/v6/E_unsealed.csv`):
  - High-G bags: 8/10 PRESENT (2 uncertain). Low-G Oligocene bags: 8/10 ABSENT, 1 trace (34/4-6 1390 m, base of
    Oligocene), 1 uncertain. => The XRF G proxy detects real glauconite pellets.
  - High-G pellet bags are the Utsira (34/4-6, 34/7-4, 34/8-3 A) plus just below THGU (34/4-6 1250 m; 34/7-10
    1100-1130 m = 7-37 m below THGU; greensand at 1110 m). Caving vs near-THGU glauconitic sand is not separable.
- 2026-11-06 09:45: Agent 1 (task B) had hit the usage limit after writing only `B_sand_intervals.csv`; resumed via SendMessage.
- **v6 B DONE** (Agent 1; `results/v6/B_*.csv`): ALL in-scope Oligocene sands are INCONCLUSIVE (DC only; no SWC/core
  inside any of them; confirmed by Rundberg & Eidvin 2016: 'No cores or sidewall cores have been taken in the
  Oligocene sands').
  - 34/7-6 1217-1282 m: young benthics in DC, flagged as caving.
  - 34/7-10 1314-1325.5 m: rare young taxa in DC (caved).
  - 34/4-6 1358.5-1387 m: no Neogene taxa in 3 datasets (leans in-situ).
  - 34/4-7 1175-1200 m: SWCs 4.7-5.1 Ma, but it is basal Utsira above THGU (mislabelled 'late Oligocene').
  - FLAG: Løseth 2013 apparently proposed upward injection from a Paleocene parent sand, not sinking; the plan's
    attribution may be wrong (second-hand).
- **NEXT:** reviewer final sinkite verdict (round 13), then write `V6_RESULTS.md` and update the page and memory.
- **Reviewer round 13 FINAL VERDICT:**
  - No evidence for sinkites. Limited compositional evidence against a glauconitic Utsira source for the
    34/7-6 and 34/7-10 target sands.
  - The decisive age test is impossible (no SWC/core).
  - The pre-registered D failed via MY reviewer-proposed Al floor (say so).
  - Hypothesis framing: (i) in-situ turbidite, (ii) upward injection, (iii) sinkite.
  - Don't attribute "sinkite" to Løseth without reading it; the definition should come from the supervisor.
  - Skip F. One cheap check G (young-taxa distribution in DC, 34/7-6 and 34/7-10) is pre-registered in the plan; then STOP.
  - Future work: Sr dating of hand-picked forams from archived bags.
  - Thesis conclusion text: see V6_RESULTS.md once written.
- **v6 G DONE:** 34/7-6 SCATTERED (young taxa 72% above, 2/7 in, 40% below: cavings); 34/7-10 INCONCLUSIVE (1 sand sample).
  Agent 1 corrected its 34/7-10 B rows; the verdicts are unchanged. `results/v6/G_young_taxa.csv`.
- **v6 CLOSED.** Final answer: no evidence for sinkites; limited compositional evidence against a glauconitic Utsira source
  for the target sands; the age test is impossible without SWC/core. Future work: Sr dating of hand-picked forams from
  archived bags. See `V6_RESULTS.md`.

## v7 (user: do 1 -> 2 -> 3): sample-matched targets
- Step 1 = photos -> XRF chemistry; step 2 = photo glauconite detector trained on validated XRF G; step 3 = mud-log
  lithology labels.
- All 5,038 W_1 photos have matched XRF.
- `V7_PLAN.md` step-1 draft is with the reviewer (round 14).
- **v7 agents** (the user wants agents for this and all further improvements):
  - Agent 4 = ML/computer-vision specialist (a6b26e272331d83c3), notes in `v7/agent4_notes.md`.
  - Agent 5 = wellsite geologist / mud-log specialist (a4ab14a584f6ec6fd), files `v7/agent5_inventory.*`.
  - Agent 2 = geochemist (target design), `v7/agent2_target_notes.md`.
  - Agent 3 = reviewer.
  - Agent 1 = petrophysicist (available).
- **Reviewer round 14 on step 1** (to fold into the final plan):
  - Si/Al target with robust Theil-Sen Ba slope; report also UNCORRECTED and Ba-partialled.
  - Tertiary only, excluding 0-15 m below shoes (pre-Tertiary separately).
  - Ca as a secondary target.
  - ±50 m primary, with ±25 m and ±5-bag sensitivities.
  - LOAO next to the primary.
  - Effect-size floor: median rho >= 0.10.
  - Leakage: Ba high-passed, NOROG box batch steps.
  - Ridge alpha=10 sensitivity; raw embeddings for continuity.
  - Baselines on the same series with paired tests.
  - Step 2: use the no-Al-floor G (exploratory), scored by within-well ranking.
  - Step 3: list which wells have digitisable mud logs first.
- **2026-11-09 23:30:** the weekly limit has reset. Agents 2, 4 and 5 were resumed via SendMessage. Their earlier runs left nothing in `v7/`. Next: merge their notes with reviewer round 14 into the FINAL V7_PLAN.md, commit, then implement `52_v7_photo_to_xrf.py`.
- **Agent 2 (geochemist) done** (`v7/agent2_target_notes.md`; scratch v7b.py / v7_target_check.csv). Local check: high-passed ±50 m Spearman vs v2 GR Vsh, Tertiary, 8 wells.
  - Primary target: z log10(Si/Al) UNCORRECTED. Median local rho with Vsh is −0.19 (right sign in 7/8 wells), against −0.15 with the Theil-Sen Ba correction. The ratio already cancels barite dilution.
  - OLS and Theil-Sen Ba slopes are immaterial (they differ by ≤ 0.06). Theil-Sen-corrected and fully Ba-partialled versions go in as sensitivities.
  - Rename the target "quartz + biogenic silica vs clay". Oligocene ooze is biosiliceous (Si/Al 4.0–5.4 vs Lista 3.3); 34/7-6 runs the wrong way (+0.22) but stays in.
  - Secondary target: z log10(Ca), Ba-partialled; local rho with Vsh is only −0.08. Report rho(Ca, S) as a gypsum check (34/8-3_A +0.59).
  - Exclusions: Tertiary only, 0–15 m below shoes, flag Al below the 5th percentile; never use Ti, Mg or K/Al.
  - Leakage: high-passed log Ba / log Cl, plus a block-permuted target null (10-bag blocks).
- **Agent 4 (ML/CV) done** (`v7/agent4_notes.md`; scratch a4/). No photo-to-target skill computed.
  - Keep R-D (PCA32, Ridge α=1). Drop the α=10 sensitivity (it changes nothing on 32 PCs). Pre-declare raw 2048-d ridge with α chosen inside the training wells (LOWO) and equal well weights. No fine-tuning or MIL.
  - Agrees with agent 2: dilution cancels in Si/Al. After high-pass, the Si/Al–Ba correlation runs from −0.43 to +0.31 (positive in 6 wells, negative in 5). Report a partial Spearman controlling high-passed Ba, Ca/Al and Cl.
  - Controls:
    - within-well CIRCULAR-SHIFT null: lag-1 autocorrelation after high-pass is 0.06–0.76, so shuffling is invalid;
    - lag profile k±m, expecting a peak at m=0;
    - photo→Ba diagnostic;
    - Zn/Pb pipe-dope negative control;
    - relative depth after the same high-pass.
  - Photo batches: camera settings are identical everywhere, but each well has its own Photoshop session; 34/7-10 spans 3 days with 8 reshoots. Proposed: a capture-session table and a reshoot test as a sensitivity.
  - Statistics: Wilcoxon over 11 wells is fine; add a well-bootstrap CI. LOAO is a stress test only. 34/8-3 and 34/8-3 A are near-twins.
  - Step 2:
    - data: only 27 bags with G>0.2 in 5 wells, and position alone gives AUC 0.75–0.99;
    - design: a full-resolution dark-green round-blob count (pellets are 7–14 px in the tiles, 20–45 px at native resolution);
    - primary test: conditional ±80 m of THGU, stratified rank-sum with a block null; Lista false positives ≤ 5%; must beat the green index in ≥ 4 of 5 wells; feasibility claim only.
- **V7_PLAN.md step 1 FINAL candidate** written (agents 2 and 4 plus round 14) and sent to the reviewer (round 15). Nothing has been computed.
- **Reviewer round 15: APPROVE WITH CHANGES** (uncorrected T1 accepted; R-RAW accepted). Applied: EXIF sessions always run; the same Tertiary normalisation set for inputs and targets; circular shift within stretches with Fisher as secondary; lag profile against rho0×ACF; Zn/Pb ambiguity; not-mud condition on T1-P (≥ 0.05); positive sign = skill; expectation removed; step-2 blob parameters to be fixed and the THGU-distance baseline put inside the test. Plan FINAL → implement 52_v7_photo_to_xrf.py.
- **Capture sessions** (`v7/capture_sessions.csv`, 52a): every W_1 photo has an EXIF time. Sessions break at gaps > 2 h (2–4 per well). There are 58 reshoots (> 24 h after their 10 depth-neighbours; 7 in 34/7-10, matching agent 4). One Photoshop version per well (21.0, 22.2, 22.4). Bug fixed: datetime64[us] was read as ns, so the first run flagged 0 reshoots.
- **Agent 5 (mud logs) done** (`v7/agent5_inventory.{csv,md}`, agent5_thumbs/).
  - 10/11 wells have a usable mud log; 34/7-6 has none.
  - 8 wells have a pixel-readable % cuttings column: 24/9-3, 34/4-6, 34/4-7, 34/7-4, 34/7-9, 34/7-10, 34/8-3, 34/8-3_A.
  - 34/7-1 and 24/9-4 need the text route (24/9-4 is handwritten). For 34/7-9, the Saga typed lithology log in GEOLOGY is the better source.
  - Do NOT use interpreted lithology or composite logs (GR leakage).
  - Protocol: sand/clay/carbonate fraction per bag interval, blinded digitisers, a second digitiser on 20%, XRF Si/Al as a cross-check.
  - Pitfalls: cavings, trace symbols, clay symbol confused with the grid, wash-out bias, lag, per-sheet calibration.
  - Effort: ~20 agent-hours (pixel route), 25–35 (text route).
- **v7 STEP 1 RAN** (bdf7850 script, outputs in results/v7/, draft V7_RESULTS.md 9b76a2f).
  - **Primary: median hp rho +0.32, 11/11, p 0.0005, CI 0.18–0.49 → claim condition PASS.**
  - T1-P 0.33 (not-mud PASS); circular null 10/11; lag peak at 0; all sensitivities 0.27–0.40; baselines ~0.
  - Weak spots: photo→Ba 0.31; Zn+Pb control ambiguous (median 0.05, p 0.012); 34/8-3 fails (0.02); lag asymmetry (+1: 0.13); downstream GR AUC worse than v2.
  - Sent to the reviewer, round 16. Do NOT report it to the user as final before the reviewer verdict.
- **Reviewer round 16: ACCEPT WITH CHANGES.** No bug or leakage found. 52b checks: colour L*a*b* alone 0.24 (11/11); R-D beats it (paired p 0.016); partial on colour 0.26; below 950 m 0.32 (11/11); S minus v3 shallow set 0.46 (8/8). Wording updated in V7_RESULTS.md (bag scale, chemical not sand, colour does much of it, mud-residue caveat, 34/8-3 fails). Sent to the reviewer for final sign-off.
- **Round 16b: step 1 SIGNED OFF and CLOSED** (3 wording edits applied). Agent 4 is drafting the step-2 spec (`v7/agent4_step2_spec.md`; blob parameters fixed from mineralogy and pixel scale, not from the 27 positives).
- **Step-2 spec** from agent 4 copied into V7_PLAN.md (candidate, round 17): CIELAB dark-green gate, 14–72 px blobs at native 7.14 µm/px, score = blobs per 10^6 chip px, Lunde calibration, conditional ±80 m test with a distance residual, Lista FP ≤ 5%, must beat the green index in ≥ 4/5 wells. Sent to the reviewer and the geochemist. Nothing has been run on G bags.
- **Round 17 (step-2 spec): reviewer APPROVE WITH CHANGES; geochemist says freeze the gates** (`v7/agent2_step2_review.md`). Amendments are in V7_PLAN.md A15:
  - null = shift the residual; [1,d] as secondary;
  - success = (a) conditional p < 0.05 AND (c) Lista FP ≤ 5%; (b) beating GI is descriptive only;
  - hole-fill-off sensitivity;
  - A13 learned model NOT run; per-well normalisation NOT run;
  - diagnostics: brown blobs, size/hue bins, Balder FP row, Spearman against continuous G;
  - run ONCE as frozen.
- 53_v7_pellet_blobs.py reproduces agent 4's prototype S exactly on 3 Lunde photos (4.503, 12.496, 0.054). It takes ~12 s per photo single-core with all sensitivities.
- **Step-2 runs started 2026-11-10 ~11:40:** 53b committed (0bceef0), dry-run only on fake scores (H0 false-alarm rate 6.5% over 200 reps). The Lunde calibration (1,022 photos, 4 nohup shards) writes to `v7/step2/lunde_shard_*.csv`. NEXT: combine (`python 53_v7_pellet_blobs.py lunde`), commit tau_L and the hash, then run set `g` (873 photos) the same way, commit the score hash, then `python 53b_v7_pellet_eval.py` ONCE, then the reviewer.
- **Lunde calibration done** (1,022 photos, 0 errors, sha256 c9f9f9a9…afdfe6, results/v7/step2_lunde_scores.csv). tau_L is the 99th percentile of S (see the commit message). The background differs strongly between wells (median S: 34/7-10 0.00, 34/7-4 0.06, 34/7-1 2.77), so absolute S is not comparable across wells. No parameter was changed. The G-set score run (873 photos) is started next.

## 2026-11-10 ~14:45: v7 step 2 evaluated (run once, frozen). Criterion NOT met.
- G-set scores: 873 photos, 0 errors, sha256 85b7f327a8bd2d695decaaf288e3086226ec85aa578701ad070aeadf4c9b9a69 (commit 28e022c, before the join to G).
- `53b_v7_pellet_eval.py` run once (commit 96a697e): outputs in results/v7/ (step2_results.json, step2_eval_log.txt, g_scores_joined.csv).
- (a) primary Q 0.741, p 0.0003: PASS. (c) Lista FP 28/125 = 22.4% (limit 5%): FAIL. (b) S beats GI in 3/5 wells (descriptive). GI comparator Q 0.705.
- 26 of 28 Lista FPs are in 34/8-3 (18/30) and 34/8-3 A (8/34). Lista median S 18.7 > Lunde p99 16.47.
- Position alone beats S in 3/5 wells (raw AUC); photo adds clearly only in 34/8-3 A.
- V7_RESULTS.md has the step-2 section (commit 5f6ef44) with a PROPOSED wording, since none was pre-declared for "(a) passes, (c) fails".
- Sent to the reviewer (round 18) and to the geochemist (what is green in Lista of 34/8). Geochemist notes will be at ~/sinkite_ml_work_v2/v7/agent2_step2_results_notes.md.
- I have NOT looked at overlays or individual bags yet. Any such look is exploratory and waits for the reviewer.
- NEXT: apply reviewer round-18 changes to V7_RESULTS.md, close step 2, update memory, then step 3 (write the step-3 plan from results/v7/agent5_inventory.md, reviewer approval, blinded digitisers).

## 2026-11-10 ~19:45: v7 step 2 CLOSED (reviewer round 18: ACCEPT WITH CHANGES, applied)
- V7_RESULTS.md step-2 section revised (commit 632f9e6). Agreed wording: a native-resolution dark-olive-green PIXEL score (not a pellet count: rho with colour-gate fraction 0.99) co-locates with G > 0.2 bags within +/-80 m of THGU after a piecewise-linear distance trend is removed (Q 0.74, p < 0.001 pre-registered; rank-only Fisher about 0.06; carried by 3 wells). Distance alone does as well or better in 4/5 wells. 22% Lista FP; does not beat the green index. NOT a glauconite detector. v6 conclusion stands.
- Exploratory (labelled so): 93-100% of accepted blobs are hue 95-120 deg (olive); hue >= 120 only gives 0/125 Lista FP but Q 0.687 and only 2/6 intervals; 12/22 window positives score below Lunde p99.
- Geochemist notes: results/v7/agent2_step2_results_notes.md. Lista FPs are green Fe-smectite claystone (G about 0), not glaucony. Out-of-window G > 0.2 bags are index artefacts (salt, Nordland mineralogy): G is a sound label only inside the Hordaland/Utsira window. Q1 literature in the notes is from memory: verify before citing.
- A13 learned model NOT run (as fixed in A15).
- STEP 3 STARTED: mud-log TIFs being copied to ~/sinkite_ml_work_v2/v7/step3/mudlogs/ (about 2.3 GB). The earlier pilot is scratchpad/mudlog_sand.csv (34/7-10, 2510-2670 m only).
- NEXT: write V7_PLAN.md step 3 (digitiser = script on the cuttings % column, blind to photos by construction; independent visual reader agent on a random 20%; XRF Si/Al as a validity gate; then LOWO photo -> mud-log sand fraction with the step-1 model family and baselines), send to the reviewer BEFORE any join to photos.

## 2026-11-11: v7 step 3 state (safe restart point; read this section after a /clear)
- **Plan:** V7_PLAN.md "Step 3 ... v2" (line ~406). Reviewer round 19 (APPROVE WITH CHANGES) and Agent 5's protocol check (results/v7/agent5_step3_protocol_check.md) are applied. Primary = P2 (step-1 held-out Si/Al predictions vs mud-log sand fraction, no retraining); P1 (retrain) secondary. Test of record = Tertiary set S if >= 6 eligible wells, else digitise the pre-Tertiary and use the whole well.
- **Digitiser design changed:** script does geometry only; two independent AI readers of different models read the tiles (A all 300, B a random 30 % + symbol audit). G2 = A vs B at bag-interval level.
- **Done:**
  - Scans copied to ~/sinkite_ml_work_v2/v7/step3/mudlogs/ (8 wells + 24/9-4 + 34/7-9 Saga PDF).
  - `54_v7_mudlog_geometry.py`: comb tracker of the 10 m grid lines from one anchor per sheet -> calib/<well>_depth_table.csv and calib/<well>_labels.png. G1 checked by eye: every 100 m label in the Tertiary sits on its line in all 8 sheets.
  - `55_v7_mudlog_tiles.py`: 300 tiles of 40 m in step3/tiles/<well>/ with index.csv (depth ruler left, 0-100 % ruler top/bottom). Column borders verified on 34/7-4, 34/4-7, 24/9-3 (24/9-3 column is 200 px wide, corrected).
  - Legends per sheet: step3/legends/ and results/v7/step3/. Reader rules FROZEN: results/v7/step3/reader_rules.md (commit 5d0aeaf).
- **Observations (label side only):** 34/8-3 Tertiary is ~100 % claystone (no variance expected). 34/4-7 has bands where horizontal ruling has faded from the scan (readers flag "faded"). The mud logs record glauconite as a % fill near THGU (34/7-10 1080-1120 m, 34/4-7 ~1170-1200, 34/7-4 ~1150-1190, 34/8-3 A ~1080-1250): exploratory cross-check of XRF G declared as C8.
- **Running now:** (a) fresh reviewer for round 19b on the reader-based digitiser (the old reviewer instance had grown to 325k tokens per resume, so it was replaced to save usage); (b) a 4-tile reader pilot, sonnet vs opus, in step3/reader_pilot/ (tiles 34_8-3_A_1080, 34_4-6_1040, 24_9-3_1080, 34_7-10_1080; my own reading of 34_4-6_1040: 1040-1070 clay 60 / sand 40, 1070-1079 80/20, 1079-1080 90/10; of 34_7-10_1080: 1080-1090 clay 70, dotted 20, glauconite 10; 1090-1110 clay 80, glauc 20; 1110-1120 clay 90, glauc 10).
- **NEXT:** apply 19b changes; pick reader models from the pilot (cheapest model that reads correctly); draw reader B's 30 % by seed; launch reader A per well (one fresh agent per well, tiles in random order, output JSONL per well in step3/readers/A/); then B; then a join script (56) for bags, G2, G3 (XRF), C4 eligibility commit, and only then the photo tests (57).
- **Usage note (user request 2026-11-11):** keep subagent cost down. Use fresh agents with short briefs instead of resuming large ones; cheaper models for mechanical reading; keep the strong model for the reviewer. Do not load the `update-config` skill again (it prints the full settings schema).

## 2026-11-11 (later): v7 step 3 RUN; results drafted; reviewer round 20 pending
- **Scripts:** 54 (depth calibration), 55 (tiles), 56 (reader folders; `fix_24_9-3`), 57 (`check`, `g2`, `g2fix`, `labels fix`), 58 (`elig`, `g3`, `photo`, `c8`). Outputs in ~/sinkite_ml_work_v2/v7/step3/ and results/v7/step3/.
- **Readers:** A (opus) all 300 tiles; B (sonnet) 100 tiles. First G2 pass FAILED one of eight gates (informative Spearman 0.596 < 0.60), all from one 24/9-3 tile (2360-2400 m, dots read as silty clay by A, as sand by B). Pre-declared one fix used: rules v3 (cells holding only dots are sand), reader C (opus) re-read all 69 tiles of 24/9-3, reader D (sonnet) a fresh 21. Second pass PASSES all gates (24/9-3 C vs D: Spearman 0.94, MAD 1.0). C is reader of record for 24/9-3.
- **Eligibility (labels only):** 6 of 8 wells eligible in the Tertiary (34/8-3 and 34/8-3 A have too little sand variation). Set of record = S, 1,372 bags. Pre-Tertiary NOT digitised.
- **G3 (label vs measured Si/Al):** median rho +0.18 (5/6). Weak.
- **P2 PRIMARY (step-1 Si/Al model, no retraining) vs mud-log sand fraction:** median rho +0.125, 5/6 wells, p 0.047, CI -0.03..+0.27. Criterion met, marginally. Pair concordance 0.68 (p 0.031).
- **Context:** colour only +0.153 (photo models do NOT beat it); P1 retrained +0.135; reference chemistry +0.177; depth +0.06; bag weight -0.07. Carried by 24/9-3, 34/7-4, 34/7-9 (drop any one: median 0.08). Lag +1 equals lag 0 (0.13 vs 0.125).
- **C8 (exploratory):** where the mud log draws a glauconite fill, 17 of 24 bags have XRF G > 0.2; elsewhere 9 of 762. Supports the v6 G index; nothing for the step-2 photo score.
- **Usage settings changed 2026-11-11 (user approved):** 11 personal skills off via `skillOverrides`, `syncClaudeAiPlugins: false`; backup ~/.claude/settings.json.bak-2026-11-11. `syncClaudeAiSkills` left on (figure/slide skills may be wanted for the conference). Academic-research plugin left on.
- **NEXT:** apply reviewer round-20 wording to V7_RESULTS.md step 3; close step 3; update memory; final summary of v7 (steps 1-3) for the user. Open offers: human audit key for the symbol-audit tiles; 34/7-9 Saga log as a second source; text route for 34/7-1 and 24/9-4.

## 2026-11-11 evening: v7 step 3 CLOSED (reviewer round 20: ACCEPT WITH CHANGES, applied). v7 programme (steps 1-3) complete.
- V7_RESULTS.md step-3 section final (commit e9d3896). Post hoc checks in results/v7/step3/step3_reviewer_checks.json.
- **Agreed headline:** in six held-out wells a photograph model trained only on Si/Al agreed weakly with the wellsite sand fraction (median per-well Spearman +0.13; one-sided p = 3/64 = 0.047; CI -0.03 to +0.27), narrowly meeting the pre-registered criterion, no better than mean colour (+0.15) and below measured chemistry (+0.18). Four wells positive, one zero, one negative.
- **Given measured Si/Al the photographs add about nothing** (partial +0.02): step 3 shows little beyond step 1 x the weak chemistry-mud-log link.
- **Disclosures:** the G2 fix was legitimate in spirit, not by the letter (a pooled gate failed, not a well); the fix moved 24/9-3 towards sand (21 % -> 26 %); the primary is unchanged with reader A's original labels (+0.123, p 0.047); leave-one-area-out P2 fails (p 0.078); no human key for the readings.
- **C8 wording:** mud-log glauconite is consistent with the XRF index in two of four wells; exploratory, not a validation.
- **v7 in three lines:** (1) photos predict bag Si/Al chemistry in unseen wells (+0.32, 11/11): the solid result; (2) the pellet-blob glauconite detector failed its specificity test: it is a green-pixel score; (3) against wellsite sand fractions the photo model agrees weakly and marginally, not beyond colour or chemistry.
- **Open offers, none started:** human key for the 17 symbol-audit tiles; 34/7-9 Saga log as a second source; text route for 34/7-1 and 24/9-4; pre-Tertiary digitisation; fine-tuned CNN.
- NEXT is the user's call: thesis/conference write-up, or one of the open offers.

## 2026-11-11 night: v7 extras X0-X3 DONE (all EXPLORATORY; user request "do the 17-tile check yourself and with an agent, then the extras")
- Plan and an earlier reviewer's changes: V7_PLAN.md "Extras after v7". Results: V7_RESULTS.md "Extras after v7" (commits b2d3c02, 95b5cde). Scripts 59 (X1), 60 (X0), 61 (X3 tiles), 62 (X2, X3).
- **X0 (17 audit tiles read twice more: main session + a dedicated audit agent):** both agree with the reader of record (sand MAD 0.01 points; one tuff stripe, one thin limestone differ). Consistency of AI readers, NOT accuracy; no human key; 3 tiles were not blind for the main session.
- **X2 (34/7-9 Saga wellsite log vs Exlog log):** sand Spearman +0.42 (CI 0.11-0.69), high-passed +0.53, MAD 7.7 points. P2 vs Exlog / Saga +0.19 / +0.16. The wellsite label itself is only moderately reproducible (one well, one reader).
- **X3:** 34/7-1 text route: readers identical, but only 7 informative bags -> NOT eligible (zone label, not bag label). 24/9-4 hand-drawn log: reader agreement 0.96, eligible (197 bags, 62 informative); P2 +0.27, Si/Al +0.35. With it added: 7 wells, median +0.172, p 0.023, CI +0.00..+0.27. Supporting evidence, not a second test (added after the six-well result was known).
- **X1 (fine-tuned ResNet-18 on Si/Al, C2 recipe, 11 LOWO folds, 2 h 07 min on the M4 GPU, run once):** fine-tuned median +0.46 (mean +0.41); frozen ResNet-18 control +0.33 (mean +0.39); R-D +0.32 (mean +0.33); all 11/11. Paired: CNN vs frozen control p 0.42 (5 wells up, 6 down) -> **no detectable gain from fine-tuning (n = 11)**. CNN vs R-D: 9/11 higher, p 0.005. Post hoc: frozen ResNet-18 control vs R-D 7/11, one-sided p 0.027. 34/8-3 goes 0.03 -> 0.31 with fine-tuning (one well, observation). CNN vs mud-log sand +0.12, p 0.078: no better than R-D. Step 1 stands with R-D as model of record.
- **Why the "7 stopped agents" (user question):** they hit the 5-hour usage limit with their readings saved; fresh agents finished every tile. Nothing was left unread.
- **Usage events:** an agent started on model "fable" failed with "out of usage credits"; agents now run on opus (reviewer, careful reading) or sonnet (mechanical reading). X1 files: ~/sinkite_ml_work_v2/v7/x1/ and results/v7/x1/.
- **Reviewer (extras, after results): ACCEPT WITH CHANGES, applied (commit after 608ead1).** Numbers matched except one wrong bag count for 34/7-1 (467 labelled bags, 130 in S; not 139). Disclosed deviations: the per-tile depth-uncertainty exclusion was not applied in X3 (it would have removed 24/9-4), no shoe check for 34/7-1. Wording softened for X2 (not a strict ceiling), X1 (signal reappears with two other ResNet pipelines; no detectable gain from fine-tuning, one seed), 34/8-3 (sidetrack shows no such change). Extras CLOSED.
- **Still open, not requested:** thesis/conference text (THESIS_NOTES.md has no v7 content), pre-Tertiary digitisation, a human key for the audit tiles.

## 2026-11-12 00:10: v8 started (user: "do 1, 2, 4, 5 and the additionals", order left to me)
- **Plan:** V8_PLAN.md (parts A elements, B when it works, C two more fine-tuning seeds, D mud-log labels below base Cretaceous, E figures, F writing). Reviewer before run: APPROVE WITH CHANGES, applied (amendments section in the plan).
- **A DONE (63 A, run once; reviewer ACCEPT WITH CHANGES, applied):** K/Al +0.20, Fe/Al +0.28, Ca/Al +0.19, Ti/Al +0.27, Zr/Al +0.10; all pass. Counting targets (pass + partial given Si and Al + mud partial): Fe, Ca, Ti -> pre-declared wording "a rough chemical log". Caveats: Fe-Ti covary (0.4-0.7) so robust count is two (Fe-Ti, Ca); colour features R-E do as well as embeddings for all three; "beyond" partials are upper bounds; ilmenite weighting agent not excluded.
- **B DONE (63 B):** rho vs spread (MAD) of measured hp log Si/Al: between wells +0.78 (exact p 0.003); within wells (150 m windows) median +0.54, p 0.014; label-free (spread of the prediction) within wells +0.48, p 0.003; between +0.47, p 0.073. Wording: skill follows the spread of the chemistry; ranks intervals within a well, certifies none. 34/8-3 = lowest rho, second-smallest spread.
- **C RUNNING:** `59_v7_cnn_sial.py train 1000` then `train 2000`, started 23:13 on 2026-11-11, log ~/sinkite_ml_work_v2/v7/x1/run_log_seeds.txt, about 4.3 h. Then run ONCE: `python 59_v7_cnn_sial.py evalseeds` (writes x1/x1_seeds_results.json).
- **D IN PROGRESS:** range = base Cretaceous to deepest bag, 7 wells, 101 tiles (script 64, tiles in step3/tiles_jt/). G1 passed (43 labels on contact sheets calib/jt_*). Photo predictions frozen BEFORE tiles: results/v8/preT_predictions.csv (commit 40b5c49). Reader rules = v3 + results/v7/step3/reader_rules_jt_addendum.md (reviewer-approved; new class `ssst` = silty sandstone, counted as sand in the primary). Folders step3/readers/JA/<well> (all tiles, opus) and JB/<well> (20 %, sonnet), script 66. Stage 1 launched 00:00 on 2026-11-12: JA 34_4-6, 34_7-4, 34_7-9 and JB for the same three. Scoring script 67 (committed dad2dd7 before any scoring): `check`, `g2 <wells>`, `labels`, `elig`, `g3 <wells>`, `photo`.
  - NEXT for D: when stage-1 readers finish: `67 check`, `67 g2 34_4-6 34_7-4 34_7-9`, `67 labels`, `67 g3 34_4-6 34_7-4 34_7-9` (futility: stop if G3 median <= 0). If it continues: launch JA/JB for 34_7-10, 34_8-3, 34_4-7, 34_8-3_A; then g2 (all), labels, elig (commit), g3, photo (once). Unfinished reader folders resume from out.jsonl with a fresh agent and the same brief.
- **E DONE:** results/v8/fig_v8_overview.(png|pdf), fig_v8_detail.(png|pdf), script 65 (dataviz skill palette blue/orange, validated).
- **F TODO:** THESIS_NOTES.md section for v7+v8; CONFERENCE_NOTES.md (abstract, key messages, talk outline, figure list, Q&A). Then reviewer on C, D and F.

## 2026-11-12 08:45: v8 D DONE and reviewed; F drafted and reviewed; only C (GPU) left
- **Overnight:** the 5-hour usage limit stopped the four stage-2 reader agents before they wrote anything; resumed at 07:56 with SendMessage and all finished. The Mac slept from ~01:15 to 07:54 (GPU job paused; resumed by itself; `caffeinate -i -s -w <pid>` now keeps it awake).
- **D labels:** 7 wells, 101 tiles (JA all, JB 23). G1 pass (43 labels). G2 PASS on all gates: 283 intervals, Spearman 0.997, MAD 0.7 points. `ssst` class never used.
- **D eligibility:** by the letter of C4 only 3 wells (34/7-10, 34/7-9, 34/8-3) -> NO TEST OF RECORD. Cause: the "3 clusters > 30 m apart" criterion misfires when informative bags are continuous. Reviewer-approved amendment BEFORE any photograph was joined (commit 49d1d0a): informative bags in >= 3 distinct 30 m bins spanning >= 90 m -> 6 wells (not 34/4-7: faded scan, 17 labelled bags). Status: "amended, exploratory test". Pass needs the six-well AND five-unit (twins merged) versions.
- **D results (67 photo, run once, commit 60818cd):** G3 label vs measured Si/Al +0.51 (6/6, p 0.016). Photo (step-1 pre-Tertiary R-D, frozen in 40b5c49) vs sand fraction: **median +0.52, 6/6, p 0.016**; twins merged +0.51, 5/5, p 0.031 -> pass. Per well: 34/4-6 +0.16, 34/7-10 +0.31, 34/7-4 +0.51, 34/7-9 +0.52, 34/8-3 +0.63, 34/8-3 A +0.53. Context: R-E colour/texture +0.47; partial given Si/Al +0.15 (upper bound); depth -0.10; sensitivities all +0.50 to +0.52. Carbonate exploratory: negligible (+0.03).
- **Reviewer (D and write-up): ACCEPT WITH CHANGES, applied (commit bd20ef3).** Readers judged independent (B finished before A in every well; block lists differ in 18 of 23 shared tiles). Wording: contrast with the Tertiary (+0.13) is descriptive (different model, rule, label spread); +0.15 partial is an upper bound and may be shared visual information.
- **F:** THESIS_NOTES.md section 7 and CONFERENCE_NOTES.md are complete except the part C lines (marked PENDING).
- **C STILL RUNNING:** seed 1000 at 7 of 11 folds at 08:23; then seed 2000 (11 folds). Expected end about 14:00 on 2026-11-12 if the Mac stays awake and on AC. THEN run ONCE: `python 59_v7_cnn_sial.py evalseeds`; copy x1/x1_seeds_results.json to results/v8/; write part C into V8_RESULTS.md with the pre-declared wording (mean of 3 seeds vs frozen control and vs R-D; 34/8-3 "reproduces" only if both new seeds >= 0.15); fill the PENDING lines in THESIS_NOTES.md (7a row) and CONFERENCE_NOTES.md ("Why does 34/8-3 fail?"); compact reviewer check; final report to the user.
- **Open caveat for the user:** mud reports not checked for an ilmenite weighting agent (would explain the Fe-Ti signal of part A).

## 2026-11-12 14:10: v8 C DONE and reviewed. v8 is COMPLETE (A, B, C, D, E, F)

- GPU runs for seeds 1000 and 2000 finished 09:29 and 13:29 (11 folds each,
  2,021 bags). Scored ONCE: `python 59_v7_cnn_sial.py evalseeds`.
- Result (V8_RESULTS.md part C): per-well mean of three seeds +0.38 median
  (seed medians +0.46 / +0.31 / +0.41), 11 of 11. Against frozen ResNet-18
  control: higher in 4 of 11, p 0.52 -> "no detectable gain". Against R-D:
  8 of 11, p 0.027. Median seed SD 0.03. 34/8-3: +0.31 / +0.21 / +0.41
  against about 0 for frozen models -> "reproduces" by the rule (one well,
  post hoc, sidetrack in the training fold).
- Quote +0.38 for the fine-tuned network, never +0.46.
- Reviewer (fresh opus agent): ACCEPT WITH CHANGES, nine changes applied.
- PENDING lines in THESIS_NOTES.md and CONFERENCE_NOTES.md filled.
- Files: results/v8/x1_seeds_results.json, evalseeds_stdout.txt,
  cnn_sial_predictions_seed1000.csv / _seed2000.csv, run_log_seeds.txt.
- Nothing is running. Open, not requested: mud reports not checked for
  ilmenite; no human key for audit tiles; no slide deck; one annotated
  mud-log tile for slide 9.

## 2026-11-12 afternoon: v9 started (checks that close caveats); K2b and K3 DONE, K2c and K1 running

- User (2026-11-12): will NOT make a human key ("I want you to do it. I
  won't look at them"); no new wells available; presentation waits; asked
  for the most original further ideas. Four ideas were put to the user and
  wait for a decision (V9_PLAN.md "Not in this plan"): A photo stratigraphy
  against Sodir tops, B zero-shot AI reader of bag photos, C resolution
  limit of cuttings (GR against XRF K), D parentage test for target sands.
  My recommendation: A, then C, then B.
- V9_PLAN.md (a062be2) reviewed: APPROVE WITH CHANGES, amendments de7b78b.
- K2b DONE (run once): v8 D with twins held out together: 34/8-3 0.63 ->
  0.51, 34/8-3 A 0.53 -> 0.49; median +0.50, 6 of 6, p 0.016; five units
  +0.50, p 0.031. By the rule "depends in part on the twin" (falls 0.12 and
  0.04 against <= 0.02 for any other well). Quote +0.50.
- K3 DONE (run once): gamma-ray key. Sheets checked first: 8 wellsite mud
  logs, none prints GR. Below base Cretaceous: sand fraction vs interval
  mean GR -0.27, 6 of 6, p 0.016 -> "follows gamma ray" (measured Si/Al
  -0.26). Tertiary: -0.14, 5 of 6, p 0.047 -> by the rule "no detectable
  agreement" (bar was -0.20).
- K2c RUNNING: `59_v7_cnn_sial.py trainx` (six folds, log
  ~/sinkite_ml_work_v2/v7/x1/run_log_notwin.txt, caffeinate inside the
  command). When it prints "done": run ONCE
  `python -W ignore 68_v9_checks.py k2c`, copy
  ~/sinkite_ml_work_v2/v9/k2c_results.json to results/v9/.
- K1 RUNNING: `69_v9_k1_ocr.py ocr` with the throwaway venv
  (scratchpad pdfenv, has PyMuPDF; the project venv has no PDF library) and
  the Vision OCR tool ~/sinkite_ml_work_v2/v9/k1/ocr (source
  tools/ocr.swift). Output ~/sinkite_ml_work_v2/v9/k1/pages.jsonl. Then
  `69_v9_k1_ocr.py search` -> k1_hits.csv; then every counted page is read
  as an image; a seeded 10 % of "not stated" pages too. Deviation from the
  plan to disclose: OCR over ALL pages replaces "contents pages fix the
  page list" as the way pages are found (more thorough).
- K1 DONE 2026-11-12 (results/v9/k1_weighting_material.md): 10 wells have a complete mud-materials table with barite as the only weighting material; 24/9-3 has no materials list; no ilmenite, hematite or titanium word on any of 3,474 pages. Old text-layer note follows.
  34/7-1 drilling programmes and in the 34/7-4 and 34/7-6 mud-log reports;
  no ilmenite or hematite hit yet. Not yet read as images.
- Then: fill K2c and K1 in V9_RESULTS.md, reviewer check of all four,
  update THESIS_NOTES.md / CONFERENCE_NOTES.md (D number +0.50 with twins
  out; gamma-ray key; ilmenite wording), memory, commit.
