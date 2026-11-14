"""STAGE 2 step 3: the pre-registered target run for 34/7-6.
Thresholds frozen. Positive-only interpretation."""
import re, sys
from pathlib import Path
import numpy as np, pandas as pd
from PIL import Image
from skimage.color import rgb2lab
import config as C
Image.MAX_IMAGE_PIXELS=None
A_MAX,C_MIN=-5.0,12.0; L_MIN,L_MAX=15.0,80.0
CROP=(260/6000,260/4000,5980/6000,3560/4000)
RX=re.compile(r"_CUTTINGS_PHOTO_M_(\d+)_W_1\.JPG$")
DIR = C.SSD_ROOT / "Wells" / "34_7-6" / "DRILLING"
def gi(path):
    with Image.open(path) as im:
        im.draft("RGB",(im.size[0]//8,im.size[1]//8)); im=im.convert("RGB")
        w,h=im.size; x0,y0,x1,y1=CROP
        im=im.crop((round(x0*w),round(y0*h),round(x1*w),round(y1*h)))
        a=np.asarray(im,dtype=np.float64)/255.
    lab=rgb2lab(a); L,A,B=lab[...,0],lab[...,1],lab[...,2]
    ch=np.sqrt(A*A+B*B)
    return float(((A<A_MAX)&(ch>=C_MIN)&(L>L_MIN)&(L<L_MAX)).mean())
rows=[]
for p in sorted(DIR.iterdir()):
    m=RX.search(p.name)
    if not m: continue
    z=float(m.group(1))/100.
    if 1218<=z<=1310: rows.append({"depth_m":z,"green_index":gi(str(p))})
pd.DataFrame(rows).to_csv(C.WORK_DIR/"23_target_34_7_6.csv",index=False)
print("done",len(rows))
