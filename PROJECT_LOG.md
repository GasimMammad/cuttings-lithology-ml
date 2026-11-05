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
- **Next steps, in order:**
  1. B: cement-mask robustness run (cheap; plan approved).
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
