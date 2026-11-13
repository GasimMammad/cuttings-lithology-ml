# Reading 34/7-1 (extra X3, text route; frozen before reading)

You are reading a scanned 1984 mud log (Gearhart). Each tile shows 80 m: on
the left a red depth ruler added by a script (with the sheet's own printed
depths beside it), then the cuttings column and an adjoining column, and on
the right the DESCRIPTION column. Read ONLY the description text. The green
lines mark the 80 m to report; ignore text above the upper or below the lower
green line except to finish an entry that starts inside.

For each description entry that starts inside the green lines, write:
- "depth": the depth of the entry's first line on the red ruler, nearest metre;
- "text": the text, copied as written (abbreviations kept);
- "main": the rock the sample mainly consists of, from the text:
  "claystone", "siltstone", "sand" (sand or sandstone), "limestone", "marl",
  "other", or "none" for a line that names no main rock (e.g. "TR SHELL
  FRAGS", mud data in a box, "a/a" with nothing else);
- "sand": how sand is mentioned: "main" (sand/sandstone is the main rock),
  "interbedded" (interbedded / with sand stringers / sandy), "occ"
  (occasional), "trace" (tr, rr, rare, "tr only in spl"), or "none".
  If the main rock word is SD or SST but the text says it is a trace only,
  use main "none" and sand "trace".
- "aa": true if the entry says a/a or "as above".

Ignore boxes with mud data (MW, PV, YP...). Do not interpret, do not use the
cuttings column. Append ONE JSON line per tile to out.jsonl:

{"tile": "WELL_0000.png", "entries": [{"depth": 12, "text": "CLYST: gy, sft", "main": "claystone", "sand": "none", "aa": false}], "notes": ""}

Write "entries": [] if no entry starts inside the green lines.
