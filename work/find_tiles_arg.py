from PIL import Image
import numpy as np
from scipy import ndimage
import sys
p = sys.argv[1] if len(sys.argv) > 1 else r".\work\r117.png"
im = Image.open(p).convert("RGB")
a = np.array(im)
mask = (a[:, :, 2] > 150) & (a[:, :, 1] > 130) & (a[:, :, 0] < 120)
lab, n = ndimage.label(mask)
print("size", im.size)
for i in range(1, n + 1):
    ys, xs = np.where(lab == i)
    if len(xs) < 800:
        continue
    print(len(xs), "bbox", int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()),
          "centroid", round(float(xs.mean()), 1), round(float(ys.mean()), 1))
