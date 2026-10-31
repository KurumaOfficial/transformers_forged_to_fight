from PIL import Image
import numpy as np
from scipy import ndimage
im = Image.open(r".\work\r102.png").convert("RGB")
a = np.array(im)
# cyan discs: blue/green high, red lower
mask = (a[:, :, 2] > 150) & (a[:, :, 1] > 130) & (a[:, :, 0] < 120)
lab, n = ndimage.label(mask)
print("components", n, "size", im.size)
for i in range(1, n + 1):
    ys, xs = np.where(lab == i)
    if len(xs) < 500:
        continue
    print(i, "pixels", len(xs), "bbox", int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()),
          "centroid", round(float(xs.mean()), 1), round(float(ys.mean()), 1))
