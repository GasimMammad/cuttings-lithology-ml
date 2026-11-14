"""
v9 K1 (V9_PLAN.md): text of the drilling, mud and completion reports of the 11 wells, for a search for
the mud weighting material. Read-only on /Volumes/T9.

Pages with a text layer use it; pages without one are rendered (long side 1700 px) and read by the macOS
Vision OCR (scripts/ocr.swift, compiled to ~/sinkite_ml_work_v2/v9/k1/ocr). OCR text is used ONLY to find
candidate pages: every page that is counted is opened and read as an image (see results/v9/k1_*.md).

Needs PyMuPDF, which is not in the project environment: run with a throwaway venv that has it.
  <venv>/bin/python 69_v9_k1_ocr.py ocr      writes pages.jsonl (resumes)
  <venv>/bin/python 69_v9_k1_ocr.py search   keyword hits per well and document -> k1_hits.csv
"""
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = "/Volumes/T9/GasimMammadov_MasterProject2026/Wells"
WELLS = ["24_9-3", "24_9-4", "34_4-6", "34_4-7", "34_7-1", "34_7-10", "34_7-4", "34_7-6", "34_7-9", "34_8-3", "34_8-3_A"]
OUT = os.path.expanduser("~/sinkite_ml_work_v2/v9/k1")
SKIP = re.compile(r"CUTTINGS_|SITE_SURVEY")
# weighting materials and the headings under which they are listed (English and Norwegian); fixed before the search
KW = {"ilmenite": r"ilmenit", "hematite": r"h[ae]{1,2}matit|iron\s*oxide|fer-?ox|micaceous", "barite": r"bar[iy]t[et]?s?\b|barytt|baritt",
      "weighting": r"weight(ing)?\s*(material|agent)|weighted|weight\s*up|vektmaterial|oppvekt",
      "materials table": r"material\s*(consumption|usage|used|cost)|materials\s*used|chemical\s*consumption|mud\s*(consumption|materials|cost)|product\s*(usage|consumption)|forbruk",
      "titanium": r"titan"}


def documents():
    for w in WELLS:
        fs = sorted(glob.glob(f"{ROOT}/{w}/DRILLING/*.[Pp][Dd][Ff]") + glob.glob(f"{ROOT}/{w}/WELL/*.[Pp][Dd][Ff]"))
        for f in fs:
            if not SKIP.search(f):
                yield w, f


def ocr():
    import pymupdf
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, "pages.jsonl")
    done = set()
    if os.path.exists(dst):
        for ln in open(dst):
            o = json.loads(ln); done.add((o["file"], o["page"]))
    with open(dst, "a") as fo, tempfile.TemporaryDirectory() as tmp:
        for w, f in documents():
            try:
                doc = pymupdf.open(f)
            except Exception as e:
                print("cannot open", f, e, flush=True); continue
            if doc.page_count < 2:
                continue  # single-sheet enclosures (plots and logs)
            name, batch = os.path.basename(f), []

            def flush():
                if not batch:
                    return
                r = subprocess.run([os.path.join(OUT, "ocr"), *[b[1] for b in batch]], capture_output=True, text=True).stdout
                got = {json.loads(x)["file"]: json.loads(x)["text"] for x in r.splitlines() if x.strip()}
                for pno, png in batch:
                    fo.write(json.dumps({"well": w, "file": name, "page": pno, "source": "ocr", "text": got.get(png, "")}) + "\n")
                    os.remove(png)
                fo.flush(); batch.clear()

            for i in range(doc.page_count):
                if (name, i + 1) in done:
                    continue
                try:
                    pg = doc[i]
                    tx = pg.get_text()
                    if len(tx.strip()) >= 50:
                        fo.write(json.dumps({"well": w, "file": name, "page": i + 1, "source": "layer", "text": tx}) + "\n")
                        continue
                    z = 1700 / max(pg.rect.width, pg.rect.height)
                    png = os.path.join(tmp, f"p{i + 1}.png")
                    pg.get_pixmap(matrix=pymupdf.Matrix(z, z), colorspace=pymupdf.csGRAY).save(png)
                    batch.append((i + 1, png))
                except Exception as e:
                    fo.write(json.dumps({"well": w, "file": name, "page": i + 1, "source": "error", "text": "", "err": str(e)[:200]}) + "\n")
                if len(batch) >= 16:
                    flush()
            flush()
            print("done", w, name, doc.page_count, flush=True)
    print("ALL DONE", flush=True)


def search():
    import csv
    rows, npages = [], {}
    for ln in open(os.path.join(OUT, "pages.jsonl")):
        o = json.loads(ln)
        k = (o["well"], o["file"]); npages.setdefault(k, [0, 0, 0])
        npages[k][0] += 1; npages[k][1] += o["source"] == "ocr"; npages[k][2] += len(o["text"].strip()) < 20
        for name, pat in KW.items():
            for m in re.finditer(pat, o["text"], re.I):
                a, b = max(0, m.start() - 70), min(len(o["text"]), m.end() + 70)
                rows.append({"well": o["well"], "file": o["file"], "page": o["page"], "source": o["source"], "term": name,
                             "context": " ".join(o["text"][a:b].split())})
    with open(os.path.join(OUT, "k1_hits.csv"), "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=["well", "file", "page", "source", "term", "context"]); wr.writeheader(); wr.writerows(rows)
    for (w, f), (n, no, ne) in sorted(npages.items()):
        h = {}
        for r in rows:
            if r["file"] == f:
                h.setdefault(r["term"], set()).add(r["page"])
        print(f"{w:9s} {f[:52]:52s} {n:4d} p ({no} ocr, {ne} empty)  " + "; ".join(f"{k}: {len(v)} p" for k, v in sorted(h.items())))


if __name__ == "__main__":
    {"ocr": ocr, "search": search}[sys.argv[1]]()
