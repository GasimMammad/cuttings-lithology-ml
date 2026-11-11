# Rules for reading the mud-log cuttings column (v7 step 3, frozen before any reading)

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
- If a printed depth label on the sheet disagrees with the red ruler by more
  than 1 m, say so in "notes".

## How to read it
1. **Blocks.** The column is a stack of sample blocks. A block ends where the
   heavy outline steps sideways or a heavy horizontal line closes it. Give
   each block its top and bottom depth, to the nearest metre, from the red
   ruler. If nothing changes for the whole tile, that is one block.
2. **Widths are percentages.** Inside a block, rock types sit side by side,
   separated by heavy vertical lines. Read where each heavy line crosses the
   blue ruler. A clay part from 0 to 80 and a sand part from 80 to 100 is
   clay 80, sand 20. Exlog and Gearhart-Owen sheets are drawn in steps of 10;
   Anadrill (34/4-6) can be any width, so read it to the nearest 5.
3. **Classify each part by its pattern, never by its position,** using the
   legend image of that well. Classes:
   - `clay`: clay, claystone, shale, mudstone (ruled lines; staggered dashes;
     "T"-shaped glyphs on the 34/8 sheets; long dashes). On 24/9-3 the
     dash-dot-dash pattern is silty CLAYSTONE and counts as clay.
   - `sand`: sand or sandstone: dots that are NOT sitting on a line or dash.
   - `silt`: silt or siltstone: lines with dots on them (dash-dot lines).
     This is not sand. (Exception: 24/9-3 dash-dot is clay, see above.)
   - `carb`: limestone, dolomite, chalk (brick patterns).
   - `marl`: marl (wavy "~" marks; 34/4-6 only).
   - `glauc`: glauconite drawn as a FILL: asterisks "*" repeated down a whole
     stripe of a block.
   - `tuff`: tuff, "v" marks repeated as a fill.
   - `coal`: solid black or dense black hatching.
   - `other`: any other fill.
   The percentages of a block must add up to 100.
4. **Traces are not percentages.** Ignore, and count as the pattern around
   them: a single glyph (one "*", "v", "P", "M", "K", a shell arc, a fossil
   mark, a small box, "T", a digit 1/2/3), and a single small outlined cell
   holding one glyph. A fill is a pattern repeated over a whole block.
5. **Do not guess what you cannot see.** Use "flag":
   - `""` readable;
   - `"faded"` the ruling has faded from the scan but the heavy outline is
     clear: read the widths from the outline, classify what is visible, and
     flag it;
   - `"mask:no_returns"` no returns / "NR" / empty column at the top of the
     hole; `"mask:no_sample"`; `"mask:cement"` (dense diagonal hatching);
     `"mask:core"` (core boxes or text); `"mask:unreadable"` when more than a
     fifth of the block cannot be read. For a masked block give the depths
     and leave the percentages out.
   - Add `"unsure": true` if you could not decide between two readings, and
     say which in "notes".

## Output
Append ONE line of JSON per tile to your output file, as soon as you finish
that tile (so nothing is lost if you are interrupted):

{"tile": "34_4-6_1040.png", "blocks": [{"top": 1040, "bottom": 1070, "clay": 60, "sand": 40, "flag": ""}, {"top": 1070, "bottom": 1079, "clay": 80, "sand": 20, "flag": ""}, {"top": 1079, "bottom": 1080, "clay": 90, "sand": 10, "flag": ""}], "notes": "trace shell marks ignored"}

Leave out classes that are 0. Blocks must cover the tile from the upper
green line to the lower one without gaps or overlaps. Read the tiles in the
order of your list. Do not go back and change earlier tiles to make them
look continuous with later ones.
