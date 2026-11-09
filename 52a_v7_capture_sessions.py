"""
v7 step 1, capture-session table (V7_PLAN.md: "capture sessions, always run").
Reads only the EXIF header of every W_1 photograph (no pixels) and writes
well, depth, capture time, software, and a session id.

A new session starts when consecutive photographs (in capture-time order) are
more than 2 hours apart. A "reshoot" is a photograph taken more than 24 hours
after the median capture time of its 10 nearest bags in depth.

Run:  python 52a_v7_capture_sessions.py [--reuse]
"""
from datetime import datetime

import numpy as np
import pandas as pd
from PIL import Image

import config as C

OUT = C.WORK_DIR / "v7"
GAP_H = 2.0
RESHOOT_H = 24.0


def exif_time(path):
    with Image.open(path) as im:
        ex = im.getexif()
        sub = ex.get_ifd(0x8769)
        t = sub.get(36867) or ex.get(306)
        sw = ex.get(305)
    return (datetime.strptime(t.strip(), "%Y:%m:%d %H:%M:%S") if t else None), sw


def main():
    import sys
    OUT.mkdir(parents=True, exist_ok=True)
    if "--reuse" in sys.argv:  # recompute sessions/reshoots from the saved EXIF times
        flag(pd.read_csv(OUT / "capture_sessions.csv")[["well", "depth_m", "stem", "capture_time", "software"]])
        return
    idx = pd.read_csv(C.WORK_DIR / "02_index.csv")
    meta = pd.read_csv(C.WORK_DIR / "embeddings" / "meta.csv")
    idx = idx[idx.stem.isin(set(meta.stem))]
    rows = []
    for i, r in enumerate(idx.itertuples()):
        try:
            t, sw = exif_time(r.path)
        except Exception as e:  # unreadable header: keep the row, no time
            t, sw = None, f"ERR {e}"
        rows.append({"well": r.well, "depth_m": r.depth_m, "stem": r.stem,
                     "capture_time": t, "software": sw})
        if i % 500 == 0:
            print(i, r.well, r.depth_m, t, flush=True)
    flag(pd.DataFrame(rows))


def flag(t):
    t["capture_time"] = pd.to_datetime(t.capture_time)
    t["session"] = -1
    t["reshoot"] = False
    for w, g in t.groupby("well"):
        g = g.dropna(subset=["capture_time"]).sort_values("capture_time")
        new = g.capture_time.diff().dt.total_seconds().fillna(0) / 3600 > GAP_H
        t.loc[g.index, "session"] = new.cumsum().values
        gd = g.sort_values("depth_m")
        ct = (gd.capture_time - pd.Timestamp("2000-01-01")).dt.total_seconds().values / 3600  # hours
        d = gd.depth_m.values
        for k, ix in enumerate(gd.index):
            nn = np.argsort(np.abs(d - d[k]))[1:11]
            t.loc[ix, "reshoot"] = ct[k] - np.median(ct[nn]) > RESHOOT_H
    t.to_csv(OUT / "capture_sessions.csv", index=False)
    s = t.groupby("well").agg(n=("stem", "size"), no_time=("capture_time", lambda x: x.isna().sum()),
                              sessions=("session", "nunique"), reshoots=("reshoot", "sum"),
                              first=("capture_time", "min"), last=("capture_time", "max"),
                              software=("software", lambda x: "; ".join(sorted(set(map(str, x))))[:80]))
    print(s.to_string())


if __name__ == "__main__":
    main()
