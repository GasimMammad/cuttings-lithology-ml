"""
v4 -- local copies of the core photographs at 1/4 resolution (PNG), so that
digitisers can read them without the slow USB drive. Read-only on the drive.

Run:  python 43_v4_core_thumbs.py <shard> <nshards>
"""
import sys
from pathlib import Path

from PIL import Image

import config as C

Image.MAX_IMAGE_PIXELS = None
WELLS = ["34_4-6", "34_4-7", "34_7-1", "34_7-9", "34_7-10", "34_8-3", "34_8-3_A"]
OUT = C.WORK_DIR / "core_thumbs"


def main(shard, n):
    files = sorted(f for w in WELLS for f in (C.SSD_ROOT / "Wells" / w / "ROCK_AND_CORE").glob("*CORE_PHOTO_M_TOP*_W_1.TIF"))
    for k, f in enumerate(files[shard::n]):
        w = f.name.split("_CORE_PHOTO")[0]
        dst = OUT / w / (f.stem + ".png")
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(f) as im:
            im.draft("RGB", (im.width // 4, im.height // 4))
            im = im.convert("RGB")
            im.resize((im.width // 4 if im.width > 3000 else im.width, im.height // 4 if im.width > 3000 else im.height),
                      Image.LANCZOS).save(dst, optimize=True)
        print(f"shard {shard}: {k} {f.name}", flush=True)
    print(f"shard {shard}: DONE", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
