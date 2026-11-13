# Rules for reading the mud-log cuttings column (v7 step 3; version 3: version 2 plus one clarification for 24/9-3, made after the first agreement check)

You are reading scanned mud logs from 1981-1988. Each tile is a 40 m piece of
ONE track: the "cuttings lithology %" column. The wellsite geologist drew,
for each sample (usually 3-10 m), what percentage of the cuttings was each
rock type. Your job is to write those percentages down.

## What you may open
Only the tile images you are given, the legend image of that well, and this
file. Open nothing else: no other folders, no photographs, no data tables,
no other reader's output. Do not use your knowledge of the area to guess.

## What the tile shows
- The column lies between the blue "0" and "100" marks. The blue numbers and
  faint blue lines are a percentage ruler added by a script. Things left of 0
  or right of 100 are other tracks: ignore them.
- Red numbers on the left are depths in metres, added by a script. The two
  green lines mark the 40 m you must report. Ignore what is above the upper
  green line and below the lower one.

## How to read it
1. **Blocks.** The column is a stack of sample blocks. A block ends where the
   heavy outline steps sideways or a heavy horizontal line closes it. Give
   each block its top and bottom depth, to the nearest metre, from the red
   ruler. If nothing changes for the whole tile, that is one block. A thin
   white or grey line right across the tile is a paper seam, not a boundary.
2. **Widths are percentages.** Inside a block, rock types sit side by side,
   separated by heavy vertical lines. Read where each heavy line crosses the
   blue ruler. A clay part from 0 to 80 and a sand part from 80 to 100 is
   clay 80, sand 20. Exlog and Gearhart-Owen sheets are drawn in steps of 10;
   Anadrill (34/4-6) can be any width, so read it to the nearest 5.
3. **Classify each part by its pattern, never by its position,** using the
   legend image of that well. Classes:
   - `clay`: clay, claystone, shale, mudstone.
   - `sand`: sand or sandstone: dots that are NOT sitting on a line or dash.
   - `silt`: silt or siltstone: lines with dots on them (dash-dot lines), or
     ditto-like tick marks on the 34/8 sheets. This is not sand.
   - `carb`: limestone, dolomite, chalk. Bricks: the vertical joints are
     short and STAGGERED from one row to the next.
   - `marl`: marl (wavy "~" marks; 34/4-6 only).
   - `glauc`: glauconite drawn as a fill (asterisks "*").
   - `tuff`: tuff, "v" marks drawn as a fill.
   - `coal`: solid black or dense black hatching.
   - `other`: any other fill.
   - `unread`: a part of the width you cannot classify.
   The widths of a block, including `unread`, must add up to 100. Never
   stretch the readable parts to fill the block.
4. **Fill or trace?**
   - A **fill** is a pattern repeated down the FULL height of the block
     inside its own stripe, which is bounded by heavy vertical lines. On the
     Exlog sheets a fill is drawn with one symbol per cell: a stripe with one
     dot in every cell is sand; a stripe with a "*" every cell or every
     second cell, all the way down, is glauconite; a stripe of "v" is tuff.
   - A **trace** is not a percentage. It is one glyph (or two) sitting on top
     of another fill, for example a "*", "v", "P", "M", "K", a shell arc, a
     fossil mark, a "T" or a digit on the clay ruling, or a single small
     outlined cell holding one glyph. Ignore traces: count them as the fill
     around them.
5. **Do not guess what you cannot see.** Use "flag":
   - `""` readable.
   - `"faded"`: the ruling has faded from the scan but the heavy outline is
     clear. Read the widths from the outline. Name a class only where its
     symbol is plainly visible; call the rest `unread`. Dots that survive in
     a faded block are NOT enough to call sand: add `"unsure": true`.
   - `"mask:no_returns"` (no returns, "NR", or an empty column at the top of
     the hole), `"mask:no_sample"`, `"mask:cement"` (dense diagonal
     hatching), `"mask:core"` (core boxes or text), `"mask:unreadable"` (more
     than a fifth of the block cannot be read). For a masked block give the
     depths and leave the percentages out.
   - Add `"unsure": true` if you could not decide between two readings, and
     say which in "notes".

## Notes for particular sheets (from each sheet's own legend)
- **34/4-7, 34/7-4, 34/7-9, 34/7-10 (Exlog, Saga legend).** Clay is plain
  horizontal ruling drawn across the clay stripes. The thin printed grid
  (one vertical line every 10 %, horizontal lines every 1-2 m) is everywhere
  and is not a pattern. On 34/7-10 long dashes are shale: clay.
- **34/8-3, 34/8-3 A (Exlog, Norsk Hydro legend).** Claystone is a "T"-like
  glyph in every cell, clay is staggered short dashes, shale is a double-bar
  "T": all three are `clay`. Silt is ditto-like ticks.
- **34/4-6 (Anadrill).** No printed 10 % grid. Clay is ruled boxes, each
  closed at the right. Siltstone is lines with dots and dashes on them:
  `silt`, not sand. Sand is a stipple of dots with no lines.
- **24/9-3 (Gearhart-Owen).** The hardest sheet; read it slowly.
  - Clay has several drawings, all `clay`: dense black ruling; coarse heavy
    ruling about 1 m apart (with the printed 10 % grid behind it this can
    look like bricks: it is clay unless the vertical joints are short and
    staggered); short dashes; dash-dot-dash; and cells holding short
    vertical ticks, often with a digit 1, 2 or 3 (these are numbered
    claystone types).
  - Sand is dots with no dashes, sparse or dense. A cell that holds only
    dots is sand, even where rows of single dots alternate with rows of two
    or three dots. Dash-dot clay has a clear dash, at least a third of a
    cell wide, in every row; a few specks beside the dots do not make it
    clay. (Added in version 3 after the two readers disagreed on this
    pattern.)
  - A long stripe that is blank except for a letter such as "R" is `unread`.
  - Digits, "T", "6", shell arcs and the clover-like glauconite mark are
    traces.

## Output
Append ONE line of JSON per tile to your output file, as soon as you finish
that tile (so nothing is lost if you are interrupted). Example with a
made-up tile name and made-up values:

{"tile": "WELL_0000.png", "blocks": [{"top": 0, "bottom": 22, "clay": 90, "carb": 10, "flag": ""}, {"top": 22, "bottom": 31, "clay": 60, "sand": 30, "unread": 10, "flag": "", "unsure": true}, {"top": 31, "bottom": 40, "flag": "mask:no_sample"}], "notes": "22-31 m: right-hand stripe smudged"}

Leave out classes that are 0. Blocks must cover the tile from the upper
green line to the lower one without gaps or overlaps. Read the tiles in the
order of your list. Do not go back and change earlier tiles to make them
look continuous with later ones.

## Sheet note for 34/7-9 Saga "Well Site Lithology Log" (extra X2; added before any Saga tile was read)
- This sheet has no lithology legend. Use the usual symbols: horizontal
  ruling = clay/claystone (`clay`); dots with no lines = `sand`; "~" marks =
  `marl`; bricks = `carb`; single letters (M, K, I, P), "*" and arcs are
  traces.
- **Each 10 m sample is drawn as a thin band** (a double heavy line holding
  the rock types side by side) sitting just above a heavy 10 m depth line D,
  for example just above 1130 m. The printed grid between bands is empty and
  is NOT clay. Report each band as one block from D-10 to D, with the band's
  composition. Example: a band just above 1130 m with ruling from 0 to 90 and
  dots from 90 to 100 gives {"top": 1120, "bottom": 1130, "clay": 90,
  "sand": 10}.
- Deeper on the sheet the bands may be joined by sloping lines; still read
  the composition at each band and report it the same way.
- Where no band sits above a 10 m line, report that 10 m block as
  `"mask:no_sample"`.
