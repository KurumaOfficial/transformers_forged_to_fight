from PIL import Image
import numpy as np
from scipy import ndimage
im = Image.open(r".\work\battle5.png").convert("RGB")
a = np.array(im)
m = (a[:, :, 0] > 90) & (a[:, :, 1] > 90) & (a[:, :, 2] > 90)
m[:600, :] = False
m[900:, :] = False
lab, n = ndimage.label(m)
for i in range(1, n + 1):
    ys, xs = np.where(lab == i)
    if len(xs) > 200:
        print(len(xs), int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()),
              round(float(xs.mean()), 1), round(float(ys.mean()), 1))
