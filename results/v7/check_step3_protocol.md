# Protocol check of step 3 DRAFT v1 (C1–C4, C7)

AI check (see Use of AI in the README); "I" in this file is that check.

Source: the local scans in `~/sinkite_ml_work_v2/v7/step3/mudlogs/`. I read each sheet's legend at full resolution, made column montages from 400 to 2300 m for all 8 wells (and 2300 m to TD for 3), and made about 30 full-resolution detail crops. I opened no photographs and no model output. Pixel positions are full-resolution TIFF coordinates; they are approximate and drift from sheet to sheet, so **detect edges per sheet and never hard-code them**.

## 0. Points that change the draft (most important first)

1. **"Exlog" is not one rule set.** The legend is hand-made for each well:
   - **Saga sheets** (34/4-7, 34/7-4, 34/7-9, 34/7-10): CLAY is plain horizontal ruling.
   - **Norsk Hydro sheets** (34/8-3, 34/8-3_A): CLAY is staggered short dashes, CLAYSTONE is "┬" glyphs, SHALE is "╤" glyphs, SILT is "〃" ticks.
   - **34/7-10** also has a SHALE fill of long dashes, which is blank on the other Saga sheets.

   Use **one symbol table per sheet** (read from that sheet's legend), within a shared Exlog geometry. That makes four rule sets: Exlog geometry with a per-sheet table, Anadrill, and Gearhart-Owen.
2. **A 0.25 m row cannot be classified from its own pattern.** Exlog clay ruling repeats every ~1.0 m (23.5 px at 300 dpi, 15.7 px at 200 dpi). Anadrill clay boxes repeat every ~1.5 m. Gearhart-Owen cells are ~1 m. Most 0.25 m rows contain no ruling line and would read "blank".

   **Read the geometry, not the texture.**
   - In every row, the component boundaries are heavy vertical step-outline lines, continuous over a whole sample. Find their x positions per row; the segment widths *are* the percentages.
   - Then classify each segment's pattern over the whole sample block (between two horizontal step lines, typically 3–5 m), or over a ≥1.5 m window clipped to that block.
   - Exlog and Gearhart-Owen have a printed 10-stripe grid, so snap widths to 10% there. Anadrill has no stripe grid: it is computer-plotted with arbitrary widths, so measure continuously.
3. **Dots alone are sand; dots on a line are not.**
   - Gearhart-Owen "SILTY" (– · –) is used in 24/9-3 for the silty claystone itself; the descriptions read "1.CLST … sl slt".
   - Anadrill siltstone is "–•–•–" (big dots on lines).
   - Exlog silt is "–··–··".

   A dot-density detector will call all three sand. Require dots that are **not** collinear with dashes.
4. **Do not renormalise over "non-blank" on Exlog and Gearhart-Owen.** These columns are always drawn to 100%. Blank cells inside a drawn sample mean scan dropout or a missing sample, not unknown clay. Example: 34/7-9 at ~1136–1147 m, where the clay ruling vanishes in the 1-bit scan and only the dots survive, so renormalising would read about 100% sand.

   Rule: if more than 20% of a sample block is blank, mask the block. Do not stretch the rest.
5. **Single-cell boxes and isolated glyphs are traces, not percentages.** A real fill spans a whole sample (≥ 3 m, bounded by step lines). A 1-cell outlined box (about 1 m × 10%) holding one glyph, often at the right edge (34/7-4, 34/7-9, 34/7-10), is "tr". Score it as the underlying lithology, plus an optional trace flag. It is **not** 10% sand.
6. **The track right of the column is not lithology:**
   - Exlog: the OIL/show track carries solid black show bars (34/7-9 at 2090–2140 m; 34/4-7 at about 2480–2720 m).
   - Gearhart-Owen 24/9-3: the interpretive formation log is drawn **immediately against** the cuttings column, with only a heavy line between them.

   Stop at the heavy right-hand boundary line. Validate Exlog edges by checking for exactly 10 equal stripes between the two heavy lines.
7. **34/8-3 Tertiary is close to 100% claystone** from 1318 to 2300 m. Expect C4 "no label variance", and G2 cannot draw 10 intervals at ≥10% sand there.

## 1. How to read the cuttings column, per family

### A. Exlog Formation Evaluation Log (34/4-7, 34/7-4, 34/7-9, 34/7-10, 34/8-3, 34/8-3_A)

**Track layout, left to right:**
- ROP/WOB track, with narrow visual-porosity and CORE sub-tracks. Cored intervals are a vertical bar in the CORE sub-track: black = recovered, open = no recovery.
- DEPTH track, with rotated labels.
- Narrow TEST track. Holds ► sidewall core and ▷ (open triangle; probably SWC with no recovery). The black ◣ casing-seat triangle sits here or in the ROP track.
- **CUTTINGS LITHOLOGY**: 10 equal vertical stripes of 10% between two heavy lines. Stripes are ~30 px at 300 dpi and ~20 px at 200 dpi.
- OIL track (TRACE/FAIR/GOOD), with show bars, then the gas tracks.
- The interpreted-lithology column (34/4-7, 34/7-9, 34/7-10) is far to the right, next to the description, so it is safe.

Approximate column x-range (full resolution) at the depth checked:

| sheet | x-range | depth checked |
|---|---|---|
| 34/4-7 | 1040–1340 | 850 m |
| 34/7-4 | 1000–1305 | 1170 m |
| 34/7-9 | 510–716 | 2100 m |
| 34/7-10 | 557–762 | 1900 m |
| 34/8-3 | 2145–2441 | 1500 m |
| 34/8-3_A | 808–1111 | 1500 m |

The 34/8-3_A edges appear shifted at 1100 m, so detect them per sheet.

**Fill rules:**
- Each sample is a block bounded by a heavy horizontal step line at top and bottom.
- Inside a block, components are side by side, separated by heavy vertical lines that step at sample boundaries.
- Clay or claystone usually starts at the left edge. The others follow in no fixed order: sand is normally rightmost, tuff and glauconite are often in the middle, and limestone sometimes sits leftmost (34/7-10, ~1890–1915 m).
- **Classify by pattern, not position.**

**% fill patterns (right-hand legend boxes):**
- **Clay (Saga):** heavy horizontal ruling ~1 m apart, drawn only across the clay stripes and ending at the step line. The thin printed chart grid (lighter vertical and horizontal lines) shows in every stripe. Tell clay from blank by line weight and continuity: clay ruling is heavier and runs across the stripes it covers.
- **Clay (Hydro):** staggered short dashes. **Claystone (Hydro):** "┬" glyphs about one per cell, staggered (this fills almost all of 34/8-3 and 34/8-3_A). **Shale (Hydro):** "╤". Count all three as clay.
- **Shale (34/7-10):** long dashes "– – –". Count as clay.
- **Sand and sandstone (all):** one dot per cell, or 3–5 small dots per cell, on a regular lattice with no dashes. A single symbol covers both sand and sandstone.
- **Silt and siltstone:** dash-dot lines "–··–··" (Saga); "〃" ticks (Hydro). Not seen as a fill in the Tertiary sections I checked. Classify as silt, not sand.
- **Limestone:** bricks, i.e. horizontal lines with vertical joints **offset in alternate rows and mid-stripe**. Do not confuse with the stripe-grid verticals, which are always at stripe edges.
- **Dolomite:** slanted-joint bricks "/ /".
- **Tuff:** "V V" staggered (34/4-7 ~1705–1745 m, up to ~40%; 34/7-4 ~1670–1700 m, up to ~80%; 34/7-9 ~1580–1700 m).
- **Glauconite fill:** "*" one per cell over full stripes (34/4-7 ~1170–1200 m; 34/7-4 ~1150–1190 m; 34/8-3_A ~1080–1250 m). This is a real % fill.
- **Coal:** solid black or heavy black bars (34/7-9 legend).
- **Mica and pyrite fills** (34/7-10 legend: "M M", "P P"): exist in the legend. I saw them only as single glyphs.

**Marks that are not lithology:**
- **Trace glyphs** (the narrow left-hand legend box symbols): ▯ limestone, Z or ◸ dolomite, "/" anhydrite, ■ coal, "–" shale, "≡" silt, "•" sand. Single V, *, P, M and K are traces of tuff, glauconite, pyrite, mica and (probably) kaolinite. They are drawn either in the first stripe at the left edge or on the clay ruling ("—*—"). Treat their pixels as the underlying fill.
- **Single outlined cells** with one glyph: traces (see point 0.5).
- "NO RETURNS" / "NR" crosses in the top hole.
- **Outside the column** (do not let edge detection pick these up): ◣ casing seats, ►/▷ SWC marks, core bars, show bars, the "Cl" labels and gas step-lines.

### B. Anadrill-Schlumberger Physical Formation Log (34/4-6)

**Layout:** ROP/SWOB/RPM | DEPTH and show analysis | GAS ANALYSIS log grid (C1–C5) | **CUTTINGS LITHOLOGY** | DESCRIPTION text. There is no interpreted column.

- The column runs between heavy vertical lines at about x 3305–3611 (~305 px, 950–1300 m).
- **There is no printed 10% stripe grid.** Every component is an outlined block with arbitrary width, and the blocks fill 100%.
- Order: in the sections I saw, coal, marl and limestone sit at the left, clay in the middle or left, and siltstone, sand and tuff on the right. Classify by pattern.

**Patterns** (legend numbers 1–45 on the header; the numbers are not printed in the column):
- **Clay (31):** horizontal lines ~1.5 m apart, each box closed at the right.
- **Siltstone (44):** lines with dots and dashes, "–•–•–". Very common in 34/4-6 (e.g. 1200–1350 m and 1600–1700 m). **Not sand.**
- **Sand (43):** **sparse stipple with no lines.** The legend box for "Sand" prints almost blank, and so does "41 Top", which is blank. On the sheet, sand is a clear stipple (e.g. 950–960 m and 1030–1080 m). Make sure low-density stipple is not classed as blank.
- **Coal (36):** dense black hatching (e.g. a 20–40% block at ~1225–1250 m; the comments say "TOP COAL"). Keep it as coal, not as missing.
- **Marl (7):** "~ ~" (e.g. ~1800–1870 m, up to ~40%).
- **Tuff (16):** "V V" (e.g. ~1655–1700 m).
- **Limestone (17):** narrow brick stripe with vertical joints (e.g. ~1655–1670 m, ~10%).
- **Chalk (26), dolomite (22), glauconite (4), pyrite (6), shells (13):** as in the legend.
- **Not lithology:** isolated "∽" (shell), "*" (glauconite) and "□" (pyrite) glyphs inside other blocks are traces. Nothing else is drawn in the column. The column is empty 400–~535 m (returns to seabed).

### C. Gearhart-Owen mud log 1981 (24/9-3)

**Layout:** DRILLING & CORING data | DRILLING RATE | DEPTH (grey band; header misprinted "(ft)", labels in m) | **CUTTINGS LITHOLOGY %** (10 stripes ~20 px, 0–50–100 scale) | **INTERPRETIVE FORMATION LOG, directly adjacent** | ditch gas.

- The column is ~205 px wide.
- **Its x-position shifts by up to ~85 px between 100 m sheets:** x ≈ 1090–1295 at 500 m, ≈ 1165–1370 at 1100 m, ≈ 1175–1380 at 1870 m. Detect per sheet.
- Order varies: sand is on the left at 1090–1125 m, while numbered claystones are on the left at 1850–1900 m. Classify by pattern.

**Patterns, from the legend and checked against the adjacent descriptions:**
- **Clay class**, all of these:
  - dense black horizontal ruling ("CLAY, MUDSTONE, SHALE"; e.g. 2100–2125 m);
  - coarser heavy ruling (~1 m spacing; 1090–1125 m, where the text reads "CLY … v slty");
  - "– –" CLAYEY dashes;
  - "– · –" SILTY dash-dot. This one is the claystone itself in 24/9-3 ("1.CLST … sl slt"), so count it as clay in Y. For Y_coarse keep it as a separate "silty clay" class, not silt.
- **Siltstone:** solid lines with dotted lines between them.
- **Sand:** both the sparse "SANDY" dots and the dense "SANDSTONE, SAND" stipple, with dots off any dash line.
- **Limestone:** bricks. **Dolomite:** slanted bricks. **Miscellaneous carbonate:** brick variant.
- **Tuffaceous:** "–V–". **Coal:** solid black. **Cement:** dense diagonal hatching (see masks). **No samples:** a box with one diagonal.
- **Not lithology (ignore and score the surrounding pattern):**
  - **digits 1, 2, 3** inside cells: the index of the numbered claystone types in the description ("1.CLST", "2.CLST");
  - "T" (calcareous), "⌣" (macrofossil/shell), "6" (microfossil), "♣" (glauconite);
  - text "NO RETURNS – NO RISER", "CORE no n Rec %" in X-boxes, and "LOST IN TRIP" (~2010–2020 m);
  - a horizontal scanner seam at ~1107 m (thin light line; harmless).

## 2. Numerator (Q2)

- **Y = the single "sand and sandstone" symbol.** All three families use one symbol for both, so loose sand and cemented sandstone **cannot** be separated from the column. Only the text (SD vs SST) separates them.
  - In the Tertiary of these wells nearly all of it is loose sand (Utsira/Skade/Grid; Frigg/Hermod-type sands in 24/9-3), so the distinction hardly matters in Set S.
  - In Set W it matters (Jurassic sandstones photograph differently from loose sand). If needed later, it is a text-route job.
- **Excluded from Y:**
  - silt and siltstone;
  - Gearhart-Owen silty claystone;
  - glauconite fills: report as their own class, Y_glc. Glauconitic sands can be sand-sized, so add **Y + Y_glc** as a sensitivity;
  - tuff ("other");
  - arenaceous limestone (carbonate);
  - Exlog "silty sandstone", which exists only as a trace glyph.
- **Silt:** keep as its own class. Y_coarse = sand + silt is fine as a sensitivity, but its comparability between wells is weak:
  - Anadrill logged much siltstone in 34/4-6;
  - Exlog Saga sheets almost never fill silt;
  - Gearhart-Owen draws silt as a claystone adjective.

  Expect Y_coarse to behave very differently in 34/4-6.
- **Y_carb:** limestone + dolomite + chalk. Report marl (Anadrill only) as its own class; it is half clay.

## 3. Depth calibration (Q3)

- **Anadrill (34/4-6):** horizontal labels **every 50 m** ("950", "1000", "1050"), centred on heavy lines. Heavy lines every 50 m and medium lines every 10 m cross the gas grid. Best-behaved sheet: plotted, constant scale, ≈ 23.8 px/m.
- **Exlog:**
  - Labels **only every 100 m**, printed **rotated 90°** in the DEPTH track. Saga sheets read "1000m"; Hydro sheets have no "m".
  - Heavy full-width lines every **10 m** (≈ 235 px at 300 dpi, ≈ 157 px at 200 dpi). The label sits just below or on its line, so snap to the nearest full-width heavy line, not to the text centroid.
  - A leave-one-out test on 100 m labels alone is weak. Add the 10 m lines as knots (counted between label anchors) and run the leave-one-out test on all knots.
  - Do not confuse 10 m lines with step lines: step lines are heavy too but stop at the column edges, while 10 m lines cross ROP, column and gas tracks.
  - On the 1-bit sheets (34/7-9, 34/7-10) several labels are broken by speckle, so OCR will miss some. Count lines from the nearest legible label.
- **Gearhart-Owen (24/9-3):**
  - Horizontal labels **every 20 m** in the grey depth band.
  - Labels at the 100 m sheet joins (e.g. "1000", "1100") sit on the seam and may be clipped; prefer the labels inside the sheet.
  - The depth band shifts sideways at the joins.
  - Effective scale drifts: about 15.9 px/m by 1880 m against 15.7 nominal, so a single global fit is off by ~10 m at 1880 m. Fit piecewise per sheet.
- **Printed errors:**
  - I found no wrong depth label on the 8 sheets. The only label error is the 24/9-3 header "DEPTH (ft)"; the values are metres.
  - Scale is 1:500 throughout. Scanner stretch is ±1–2%, and paper seams roughly every 50–100 m can add small steps, so knots at every label and 10 m line handle both.
  - 34/8-3 has printed labels above the log start (1300 m), and 34/8-3_A has them above 996 m (900 m). These are valid for calibration but there is no column above.

## 4. Masks beyond casing shoes (Q4)

General rule: mask any sample block containing cement hatching, a "no samples" diagonal box, core text or X-boxes, "NR"/"no returns", or more than 20% blank. Also mask ≥10 m below each shoe for cement and junk; cement is visible in the column at 24/9-3.

| well | logging start / no returns | shoes (m) | other masks seen |
|---|---|---|---|
| 24/9-3 | no returns 145–207.6 | 207.6, 503.2, 1587.1, 2041.3 | **cement hatching in the column ~515–560 m** (mask 503–565); **cores 1–5 ~1777–1798 m** (X-boxes in the column; inside the Tertiary set); "LOST IN TRIP" ~2010–2020 m |
| 34/4-6 | returns to seabed; column empty 400–~535 | 521, 904.5, 1841, 2760 | none in 535–2300; coal block 1225–1250 is real (keep) |
| 34/4-7 | no returns 380–470 | 465, 902, 1872, 2921 | cored-interval bars ~2480–2720 m (CORE sub-track; read exact tops on the sheet); ► SWC marks outside the column (ignore) |
| 34/7-4 | first returns ~480 | 469, 953, 1915, 2745 | none seen 480–2300; check the CORE sub-track below 2300 |
| 34/7-9 | no returns to 471 | 465, 899, 1821, 2802 | **scan dropout ~1136–1147 m (mask)**; check ~1280–1290 m (light band); show bar 2090–2140 m (outside the column, exclude by edge); core and show bars below ~2480 m |
| 34/7-10 | no returns 326–428 | 423, 901, 1907, 2755 | none seen 428–2300 |
| 34/8-3 | logging from 1318 | 1302, 2598, 3312 | the column is ~100% claystone to 2300 m |
| 34/8-3_A | logging from 996 MD (KOP 945; bags ≥1000 are in the A-hole) | 944, 2442, 3227 | depths are MD (~20° at 1500 m); no other masks seen |

**Cores below 2300 m (Set W):** detect them from the Exlog CORE sub-track bars and from core text in the Anadrill comments. I could not read exact core depths at montage resolution.

**Sidetracks:** none inside these 8 sheets, apart from 34/8-3_A being itself the sidetrack. 24/9-4 is out of scope.

## 5. G2 visual reader (Q5)

**Is nearest 10% on a 5 m interval realistic?**
- **Exlog 300 dpi grey** (34/4-7, 34/7-4, 34/8-3, 34/8-3_A): yes. The 10% stripes are printed, so the reader counts stripes. Errors arise only where a 5 m interval straddles a sample step, and averaging two samples to the nearest 10 is fine.
- **Exlog 200 dpi 1-bit** (34/7-9, 34/7-10): yes, if tiles are shown at ≥2× and the dropout bands are excluded from the draw. Sand dots are 1–2 px, and speckle mimics sparse dots; the reader should use the step outline.
- **Anadrill (34/4-6):** yes to about ±10, but there is no stripe grid. Overlay a 0/10/…/100 tick ruler along the top of every tile.
- **Gearhart-Owen (24/9-3):** yes, but slower. The reader must be told that digits, T, 6 and shell glyphs are not lithology, and that "–·–" is silty claystone.
- **Every tile:** include that **sheet's own legend**, since legends differ within Exlog. Show **only** the depth track and cuttings column; the description and interpreted columns stay hidden.

**Is 20 per well enough?**
- **Not to catch a systematic symbol error.** Each family's risky symbols are rare: siltstone vs sand, glauconite fill, tuff, clay-ruling dropout, Gearhart-Owen dash-dot, Anadrill sparse stipple. Twenty stratified-random intervals per well will often contain none of them.
- **Add a symbol audit per sheet family:** about 3–5 intervals for each non-clay pattern that exists on that sheet. Pick them from the column images by pattern, with no photos or XRF. Examples: 34/4-6 siltstone, coal, marl; Exlog glauconite and tuff fills, single-cell trace boxes, and Hydro claystone; 24/9-3 "–·–", digits and cement.
- **Score the audit as a confusion matrix of class presence** (sand / silt / clay / carbonate / other / trace), separately from the Spearman gate.
- **The per-well Spearman gate is fragile:**
  - With n = 20, a true rho of 0.8 has a 95% CI of about 0.55–0.92.
  - For 34/8-3 (almost all 0% sand) Spearman is undefined, and the "half ≥10% sand" stratum cannot be filled.
  - Add per-well absolute agreement (mean absolute difference and bias in points) and use that where Y has no variance.
- **Draw tiles from bag intervals** (the (D_prev, D] windows), not arbitrary 5 m intervals. Then G2 tests the exact quantity the join uses.

## 6. C7 additions

- The scheme reads the step-outline geometry, not 0.25 m texture (point 0.2). Row-texture classification would misread most rows as blank.
- Dots on lines (silt or silty clay) vs dots alone (sand) is the main false-sand risk in all three families.
- Exlog legends differ by operator and well, so one Exlog rule set would misread the Hydro sheets entirely.
- Show bars and the Gearhart-Owen interpretive log adjoin the column, so a loose right-hand edge leaks non-lithology into the read.
- Wellsite % is in 10% steps on Exlog and Gearhart-Owen but continuous on Anadrill. Within-well rank statistics are fine; avoid pooled absolute thresholds across families.
