# Agent 5: mud-log inventory and digitisation route (v7 step 3)

Role: AI acting as a senior wellsite geologist and mud-log specialist. This is scouting only. I made no full digitisation. I looked at no cuttings photos and no model outputs, only bag depths taken from photo filenames. Every judgement below comes from 2–3 full-resolution crops per well, mostly at 1000 and 1500 m. Legibility ratings are my own visual calls.
Files: `agent5_inventory.csv` (one row per document) and `agent5_thumbs/` (headers and Tertiary crops, mud logs only).

## 1. Recommendations

1. **Wells usable for step 3: 10 of 11.** **34/7-6 has no mud log on the drive.** Its `MUD_LOG_1985-12-16_REPORT_1.PDF` is a Promud drilling-fluid diary, and the well has no strip log, no composite log and no WELL folder. Drop 34/7-6 from the mud-log label set; about 244 bags are lost.
2. **Primary target: cuttings % column → sand fraction (and clay, carbonate, other) per sample interval, by pixel classification.** The column is a true percentage fill in **8 wells**: 24/9-3, 34/4-6, 34/4-7, 34/7-4, 34/7-9, 34/7-10, 34/8-3 and 34/8-3_A. In the Exlog logs (six wells) each 10% stripe is filled with a lithology symbol, with clay as horizontal ruling, sand as dots, claystone as a "T" pattern and limestone as bricks. Samples step at about 5 m, which matches the bag spacing (mean 4.5–6.4 m). This method is already proven: the earlier 34/7-10 run (`mudlog_sand.csv`, cells `CCCCCCCCss`) gave rho ≈ 0.56 against XRF Si/Al.
3. **Secondary target: transcribe text descriptions → a per-bag class** (claystone / silty claystone / sandy claystone / sand(stone) / carbonate, plus a "sand mentioned" flag and the accessories). Use this where the column is not usable:
   - **34/7-1** (Gearhart 1984): the % column holds sparse minor-component symbols only, and claystone is left blank.
   - **24/9-4** (Fina 1991): handwritten Wellsite Geologist Log sheets on graph paper. The % steps can be read by eye but are hard to segment by machine.

   Also use the text everywhere as a cross-check on the column.
4. **34/7-9 bonus:** the operator's own Saga **Well Site Lithology Log** (`GEOLOGY/..._LITH_1986-04-13_REPORT_1_ENCL_1.PDF`) is a second, independent wellsite source. It has a cuttings % column, an interpretive column and typed descriptions under lithology headings. Use it in place of the "Poor Quality Original" Exlog scan where they disagree, and as a free inter-source reliability check.
5. **Do not use** the "Interpreted/Interpretive lithology" columns, or the composite/completion logs (`WELL/*.1.TIF`). Both are tuned to ROP and/or wireline logs, so they would leak GR-type information back into the label. Use only the *cuttings* column and the *cuttings* descriptions.

## 2. Per-well summary

| well | contractor / year | sheet | scale, resolution | logged (m) | % column | legibility | route |
|---|---|---|---|---|---|---|---|
| 24/9-3 | Gearhart-Owen 1981 | MD_PLOT_1.TIF | 1:500, 15.7 px/m, grey | 145–3051 | true fill | good | A + text |
| 24/9-4 | Fina WSG log 1991 (handwritten) | MD_PLOT_4.TIF (23 frames) | 1:500, 16 px/m, 1-bit | 0–2083 main bore; ST 1753–2030+ | hand-drawn steps | fair | text, plus manual % read |
| 34/4-6 | Anadrill-Schlumberger 1985 | MD_PLOT_1.TIF | 1:500, 23.6 px/m, grey | 400–3282 | true bar (plotted) | column good, text variable | A (easiest) |
| 34/4-7 | Exlog 1987 | MD_PLOT_1.TIF (PDF duplicate) | 1:500, 23.4 px/m | 380–2950 | true fill | good | A + text |
| 34/7-1 | Gearhart 1984 (film) | MD_PLOT_1.TIF | 1:500, 24.2 px/m | 478–2905 | sparse symbols | fair | text (B) |
| 34/7-4 | Exlog 1984-85 | MD_PLOT_1.TIF | 1:500, 23.6 px/m | 480–3115 | true fill (clay ruling looks like grid) | text good, auto fair | A + text |
| 34/7-6 | (none) | — | — | — | — | — | not usable |
| 34/7-9 | Exlog 1986; Saga WSL log | ENCL_1.TIF; LITH PDF | 1:500, 15.75 px/m, 1-bit | 471–3240 | true fill (both) | Exlog fair; Saga good | A + Saga text |
| 34/7-10 | Exlog 1986 | ENCL_1.TIF | 1:500, 15.75 px/m, 1-bit | 326–3000 | true fill | fair-good | A (proven) |
| 34/8-3 | Exlog 1988 | MD_PLOT_1.TIF | 1:500, 23.4 px/m | 1318–3328 | true fill | good | A + text |
| 34/8-3_A | Exlog 1988 | MD_PLOT_1.TIF | 1:500, 23.6 px/m | 996–3230 MD | true fill | good | A + text |

All logs are 1:500 measured depth below RKB. All have a text column, and all except 24/9-4 and 34/4-6 also have an "interpreted lithology" column. Text density in the Tertiary is one entry per about 10–50 m on the Exlog logs and per about 25–100 m on 34/7-1.

**Other documents**
- The final well reports (`WELL/*PB-706*.PDF`, 131–264 pages) and the contractor end-of-well reports give prose lithology per 20–300 m interval. These are useful for context and sanity checks, not for per-bag labels.
- The Exlog ENCL_2–10 sheets (34/7-9, 34/7-10, 34/4-7) are pressure, drilling-parameter, bit, gas-ratio and survey plots.

## 3. Protocol (bag ↔ mud log)

1. **Depth calibration.** For each strip, fit a piecewise-linear pixel→depth function from the printed depth labels (every 20, 50 or 100 m) and the heavy grid lines. Do not trust one nominal px/m figure: the scans stretch, sheets are joined at 100 m seams, and some PDFs are rescaled to a 200-inch page. Require the residual at each label to be under 0.5 m, and store the fit.
2. **Column read (route A).** Crop the cuttings column only. Split it into rows of 0.25 m, and split each row into 10 stripes (10% each). Classify each stripe by symbol (C clay or claystone, s sand, z silt, L limestone or dolomite, other, blank). Build one symbol library per contractor family: Exlog (×6), Anadrill, Gearhart-Owen.
3. **Bag matching.** A bag at depth D represents the interval (D_prev, D], with bag depth taken as the bottom of the drilled interval. Average the row fractions over that interval. Both the mud log and the bag labels are already lag-corrected drilled depth from the same crew, so no extra lag shift is needed. Test a ±1 sample (±5 m) offset as a sensitivity check, not as a correction.
4. **Text read (route B).** Transcribe each description block with its top and bottom depth, verbatim. Then map it to a class with a fixed, pre-registered rule table: first-named lithology = dominant; "tr" = <5%; "occ/rr" = minor; "a/a" carries the previous entry forward; "/" = interbedded. Assign each bag the description block whose depth range covers the bag interval.
5. **Blinding.** Digitisers receive only mud-log crops and depth tiles. They get no photos, no GR or wireline curves, no model predictions, and no bag list. The join to bags is a separate script run afterwards. Tiles are served in random order with well and depth printed, so continuity cannot be "smoothed" by eye.
6. **Reliability.**
   - **Two independent digitisers** (separate agent runs, different tile order) on about 20% of intervals: 2 wells × about 500 m, one 300 dpi grey and one 200 dpi 1-bit. Report ICC/Spearman on sand %, weighted kappa on class, and the share of bags with a difference over 20% sand.
   - **Human spot-check:** Gasim reviews 50 random intervals (crop next to digitised value), about 1–2 h.
   - **Independent physics check:** XRF Si/Al from `DRILLING/*CUTTINGS_ANALYSIS*ENCL_1.CSV` exists for all 11 wells (including 34/7-6), so the 34/7-10 rho ≈ 0.56 comparison can be repeated in every well.
   - **34/7-9:** compare the Exlog and Saga logs against each other.

## 4. Effort and coverage

- **Route A:**
  - About 3 h per contractor family to build the symbol library and classifier (3 families).
  - About 1.5 h per well for calibration, extraction and overlay QC (8 wells).
  - Total ≈ 20 agent-hours. Whole-well extraction costs little extra once calibration is done.
- **Route B:**
  - About 1.5–2.5 h per well per digitiser for 500–2000 m: about 15 sheets, read as 30–40 crops of 40–50 m.
  - About 4–6 h for the whole well.
  - All 10 wells, plus a 20% second digitiser, plus the 34/7-9 Saga log ≈ 25–35 agent-hours.
- **Coverage** (bags in the mud-log range; ≤2000 m first, whole well in brackets): 24/9-3 268 (616), 24/9-4 ≈300 (≈330: main bore to 2083 m; FEL fragment to ~2200 m), 34/4-6 155 (503), 34/4-7 171 (423), 34/7-1 186 (468, text only), 34/7-4 194 (552), 34/7-9 173 (527), 34/7-10 172 (453), 34/8-3 99 (451), 34/8-3_A 129 (439), 34/7-6 0 (0).
  - **≈1850 bags ≤2000 m, ≈4.8k for the whole well.**
  - Effective per-bag resolution is lower where one text block spans several bags.

## 5. Pitfalls (wellsite view)

- **Cavings.** The % column records what was on the shaker, so caved Tertiary claystone can show up as a real percentage. Watch for "cvgs", "caved" and "a/a w/ cvgs" in the text. Flag those bags rather than trusting the %, especially below casing points and after trips.
- **Trace conventions.** "tr" (<5%) and accessories (glauconite, pyrite, shell, mica) are drawn as single symbols, not as stripes. Do not count them toward sand %.
- **Clay ruling vs grid (Exlog).** On 34/7-4 especially, the clay symbol is horizontal ruling that looks like the chart grid. Train on blank-versus-clay examples, or the clay fraction will come out as "blank".
- **Washing loss.** Soft, hydrated Tertiary clays ("disp", "hydrtd") wash through the sieve, so the wellsite % tends to over-state sand and accessories. The archived washed (W) photos carry the same bias; the unwashed (U) photos do not.
- **Lagged depths.** These are already lag-corrected, but lag errors of one sample are common in fast top-hole drilling, at 20–30 m/h in the 17½" hole.
- **Core intervals.** Core-chip and core-description sheets (24/9-4 frames 3, 4 and 6, and Jurassic cores elsewhere) are not cuttings. Exclude bags inside cored intervals or mark them.
- **Boreholes and sidetracks.**
  - 24/9-4 has a sidetrack (ST) below about 1753 m, so bags there must be assigned to the right bore.
  - 34/8-3_A shares the 34/8-3 top hole down to the kick-off point (945 m). Its depths are MD, about 20° deviated at 1500 m.
  - 34/8-3 logging starts at 1318 m.
- **Scanning distortion.** Seams every 100 m, film stipple (34/7-1), bitonal speckle (34/7-9 and 34/7-10), and PDFs rescaled to the 200-inch maximum page size (34/7-9 LITH log, 34/4-7 enclosures). Calibrate per sheet.
- **Label quirks.** The 24/9-3 depth column header says "(ft)" but the labels are metres. The 24/9-4 frames are stored in reverse depth order.
- **Text sparsity.** On 34/7-1 one Tertiary description can cover 50–100 m, so treat its class as a zone label, not a per-bag label.
