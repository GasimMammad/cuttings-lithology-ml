# Reading 24/9-4 (extra X3, hand-drawn wellsite geologist log; frozen before reading)

Follow reader_rules.md (the general rules) with these changes for this sheet.

- **Depths come from the sheet itself.** There is no red ruler. The narrow
  strip on the left of each tile is the sheet's depth column with
  handwritten depth labels (every 20 m, e.g. "1220"); horizontal grid lines
  are every 2 m (heavier every 10 m). Read every block's top and bottom by
  counting grid lines from the nearest label. Report the labels you can read
  in "labels", top to bottom, e.g. [1220, 1240].
- There are no green lines: report the whole tile from its top to its bottom,
  to the nearest metre, as read from the labels.
- The cuttings column is between the blue 0 and 100 marks. The geologist drew
  the percentages by hand as stepped heavy lines.
- Patterns (no legend on the sheet): dots = `sand`; short horizontal dashes =
  `clay` (claystone/shale); dash-dot or dots on dashes = `silt`; bricks =
  `carb`; anything else `other`. Do not try to separate loose sand and
  sandstone.
- If you cannot read a label at all in a tile, set "labels": [] and add
  "unsure": true to every block.

Output line example (made-up values):
{"tile": "WELL_f00_1.png", "labels": [100, 120], "blocks": [{"top": 95, "bottom": 104, "clay": 70, "sand": 30, "flag": ""}], "notes": ""}
