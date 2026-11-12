
## Addendum for the deeper sheets (written from the legends and the look of the column only; rules above are unchanged)

These tiles come from deeper in the same wells. Samples are often drawn
every 1-2 m, so a tile can hold 20 or more blocks. Give every block; do not
merge blocks that differ.

- **Exlog sheets (34/4-7, 34/7-4, 34/7-9, 34/7-10, 34/8-3, 34/8-3 A).** A
  symbol may sit in every cell or in every second cell, staggered. Empty
  cells between belong to the same stripe. Widths come from the heavy
  vertical lines, never from counting symbols.
  - one dot per cell: `sand`. A dot that looks square on a coarse scan is
    still sand. Loose specks among clay ruling are scan noise;
  - **silty sandstone:** a dot ABOVE a short dash in each cell. Write it as
    class `ssst` (a class of its own; it is counted later). If you cannot
    see which is on top, add `"unsure": true` and note "T or ssst";
  - ONE short dash per cell is shale: `clay`. On the 34/8 sheets, short
    dashes staggered across the whole stripe are clay, and a bar with a stem
    or dot BELOW it ("T") is claystone: `clay`;
  - `silt` is two or three short dashes stacked in each cell, or a PAIR of
    short slanted ticks. A SINGLE "/" is anhydrite: `other`;
  - a small EMPTY box with straight sides inside each cell, or bricks:
    `carb` (limestone). A narrow stripe 10 % wide whose cells each hold a
    small upright box is limestone. A "Z" per cell or slanted bricks: `carb`
    (dolomite);
  - a small round circle per cell (conglomerate): `sand`, and say so in the
    notes. If you cannot tell a box from a circle: `unread`, `"unsure": true`;
  - a small FILLED black box per cell, solid black cells or a black stripe:
    `coal`;
  - "X" (igneous), "^" (chert), a hooked corner mark (halite), "P" in every
    cell of its own stripe (pyrite): `other`.
- **34/4-6 (Anadrill):** as before. Wavy "~" marks are `marl`; ruled boxes
  closed at the right are `clay`; a stipple of dots with no lines is `sand`.
- **Fill or trace.** A stripe is a fill only if its symbol repeats down the
  whole block. One glyph in one cell of a larger stripe is a trace. In a
  block one cell tall, a symbol in its own outlined stripe is a fill, not a
  trace. A horizontal line that stops at the edge of the clay stripe is clay
  ruling, not a block boundary.
- **Cored intervals.** Use `"mask:core"` only where no percentages are
  drawn. Otherwise read them as usual and note "core".
- **Words in the column** (cvgs, tr, calc, NR and the like): copy them to
  the notes with their depth. They do not change widths.
- The widths of a block, now including `ssst`, must still add up to 100.
