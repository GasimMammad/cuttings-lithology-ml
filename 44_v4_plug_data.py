"""
v4 -- parse digital core-analysis files (plug data, core gamma) for the
precision check of the core digitisers (V4_PLAN.md A2).

Formats:
  *.SPW    NORCORE/SPWLA fixed-width, no line breaks: blocks "17 n n" (curve
           definitions, names follow "0NORCORE"/"0<lab>") then "25 ..." data:
           rows of n floats (depth first).
  *.SPWLA  line-based SPWLA: "15 n n" curve list, "30" sample depth line,
           "40 1 n" values (missing = -1009).

Output: WORK_DIR/v4_results/plug_data.csv  (well, file, block, depth_m, curve, value)

Run:  python 44_v4_plug_data.py
"""
import re
from pathlib import Path

import pandas as pd

import config as C

# NB 24_9-3_708-12023.SPW is mislabelled: its header says well 16/10-1 (AGIP) -> excluded
FILES = {"24_9-3": ["24_9-3_CORE_CONV_RAW_1.SPWLA"],
         "34_8-3": ["34_8-3_708-6463.SPW"],
         "34_8-3_A": ["34_8-3_A_708-6478.SPW"]}
FLOAT = re.compile(r"^-?\d+\.\d*$")


def parse_spw(path):
    """Curve blocks: '15'|'17' n n + n definitions (3 integer codes + name
    words). Data blocks: '25' nrows ncols + floats. Each data block is matched
    to the nearest PRECEDING curve block with the same number of curves
    (definitions and data are not always adjacent)."""
    tok = path.read_text(errors="ignore").split()
    isint = lambda t: re.match(r"^-?\d+$", t) is not None
    defs, data, i = [], [], 0
    while i < len(tok) - 6:
        if (tok[i] in ("15", "17") and isint(tok[i + 1]) and tok[i + 1] == tok[i + 2]
                and all(isint(t) for t in tok[i + 3:i + 6])):
            n = int(tok[i + 1])
            j, names = i + 3, []
            while len(names) < n and j + 3 < len(tok) and all(isint(t) for t in tok[j:j + 3]):
                k, words = j + 3, []
                while k < len(tok) and not isint(tok[k]) and not FLOAT.match(tok[k]):
                    words.append(tok[k]); k += 1
                names.append(" ".join(w for w in words if w not in ("NORCORE", "LAB", "0NORCORE")))
                j = k
            if len(names) == n:
                defs.append((i, n, names))
                i = j
                continue
        if tok[i] in ("25", "40") and isint(tok[i + 1]) and isint(tok[i + 2]) and FLOAT.match(tok[i + 3]):
            nrow, ncol, j, vals = int(tok[i + 1]), int(tok[i + 2]), i + 3, []
            while j < len(tok) and FLOAT.match(tok[j]):
                vals.append(float(tok[j])); j += 1
            data.append((i, ncol, vals[:nrow * ncol]))
            rest = vals[nrow * ncol:]
            if rest:   # headerless continuation block (seen in 34_8-3_A)
                data.append((i + 1, None, rest))
            i = j
            continue
        i += 1
    rows = []
    for b, (pos, ncol, vals) in enumerate(data, 1):
        if ncol is None:   # pick the curve block whose width gives increasing depths
            for d in defs:
                n = d[1]
                if len(vals) % n == 0 and len(vals) >= 2 * n:
                    dep = vals[0::n]
                    steps = [y - x for x, y in zip(dep, dep[1:])]
                    if sum(st >= 0 for st in steps) >= 0.95 * len(steps) and 1000 < dep[0] < 6000:
                        ncol = n
                        break
            if ncol is None:
                continue
        cand = [d for d in defs if d[0] < pos and d[1] == ncol]
        if not cand:
            continue
        names = cand[-1][2]
        for r in range(len(vals) // ncol):
            row = vals[r * ncol:(r + 1) * ncol]
            for name, v in zip(names[1:], row[1:]):
                if v > -999:
                    rows.append((b, row[0], name, v))
    return rows


def parse_spwla(path):
    lines = path.read_text(errors="ignore").splitlines()
    names, rows, depth, k = [], [], None, 0
    while k < len(lines):
        t = lines[k].split()
        if t[:1] == ["15"]:
            n = int(t[1])
            names = [re.split(r"\s{2,}", lines[k + 1 + m].strip())[-1] for m in range(n)]
            k += n + 1
            continue
        if t[:1] == ["30"]:
            depth = float(lines[k + 1].split()[0])
            k += 2
            continue
        if t[:1] == ["40"]:
            n = int(t[2])
            vals = []
            m = k + 1
            while len(vals) < n:
                vals += [float(x) for x in lines[m].split()]
                m += 1
            for name, v in zip(names, vals):
                if v > -999:
                    rows.append((1, depth, name, v))
            k = m
            continue
        k += 1
    return rows


def main():
    out = []
    for w, fs in FILES.items():
        for f in fs:
            p = C.SSD_ROOT / "Wells" / w / "ROCK_AND_CORE" / f
            rows = parse_spwla(p) if f.endswith("SPWLA") else parse_spw(p)
            out += [{"well": w, "file": f, "block": b, "depth_m": d, "curve": n, "value": v} for b, d, n, v in rows]
    t = pd.DataFrame(out)
    bad = ~t.depth_m.between(1000, 6000)
    print(f"dropped {int(bad.sum())} rows with implausible depth (parser misalignment at block ends)")
    t = t[~bad]
    dest = C.WORK_DIR / "v4_results"
    dest.mkdir(parents=True, exist_ok=True)
    t.to_csv(dest / "plug_data.csv", index=False)
    print(t.groupby(["well", "file", "curve"]).agg(n=("value", "size"), dmin=("depth_m", "min"),
                                                   dmax=("depth_m", "max"), med=("value", "median")).to_string())


if __name__ == "__main__":
    main()
