from PIL import Image
import numpy as np
from scipy import ndimage
import sys
im = Image.open(sys.argv[1]).convert("RGB")
a = np.array(im)
m = (a[:, :, 1] > 100) & (a[:, :, 0] < 100) & (a[:, :, 2] < 100)
lab, n = ndimage.label(m)
for i in range(1, n + 1):
    ys, xs = np.where(lab == i)
    if len(xs) > 1000:
        print(len(xs), int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()),
              round(float(xs.mean()), 1), round(float(ys.mean()), 1))
