"""
v2 STEP 2 -- master photo index for all eleven wells (replaces 01 + 02).

Walks SSD_ROOT/Wells/<well>/DRILLING for every well in config.WELLS, keeps
white-light cuttings photos only (NOROG DCP naming, depth in centimetres),
and tags W_1 as "standard" (training) and W_2 as "dynamic" (never trained on).
Read-only on the data drive.

Output: config.INDEX_CSV (in the v2 work folder).

Run:  python 25_v2_index.py
"""
import re

import pandas as pd

import config as C

RX = re.compile(r"_CUTTINGS_PHOTO_M_(\d+)_W_(\d)$")


def main():
    rows = []
    for well in C.WELLS:
        d = C.drilling_dir(well)
        for p in sorted(d.iterdir()):
            if p.name.startswith(".") or p.suffix.lower() not in C.IMAGE_EXTS:
                continue
            m = RX.search(p.stem)
            if not m:
                continue
            depth = int(m.group(1)) / 100.0
            if not 0 < depth < 6000:
                continue
            rows.append({"path": str(p), "filename": p.name, "stem": p.stem,
                         "well": well, "depth_m": depth, "how": "norog_cm",
                         "processing": {"1": "standard", "2": "dynamic"}.get(m.group(2), ""),
                         "size_mb": round(p.stat().st_size / 1e6, 2)})
    df = pd.DataFrame(rows)
    df.to_csv(C.INDEX_CSV, index=False)
    w1 = df[df.processing == "standard"]
    print(w1.groupby("well").depth_m.agg(["size", "min", "max"]).to_string())
    print(f"\n{len(w1):,} W_1 photos, {len(df):,} white-light photos in total")
    print(f"Written: {C.INDEX_CSV}")


if __name__ == "__main__":
    main()
