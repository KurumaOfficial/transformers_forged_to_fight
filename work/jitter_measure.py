import json
import sys
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image

src = Path(sys.argv[1])
outdir = Path("docs/jitter")
outdir.mkdir(parents=True, exist_ok=True)

reader = imageio.get_reader(str(src), "ffmpeg")
meta = reader.get_meta_data()
fps = meta.get("fps", 0)
rows = []
for idx, frame in enumerate(reader):
    if idx % 1:
        continue
    # RGB frame; crop the model showcase area.
    a = np.asarray(frame)
    crop = a[80:980, 200:980]
    r = crop[:, :, 0].astype(np.int16)
    g = crop[:, :, 1].astype(np.int16)
    b = crop[:, :, 2].astype(np.int16)
    mask = (r > 110) & (r > g + 25) & (r > b + 15)
    n = int(mask.sum())
    if n < 3000:
        continue
    ys, xs = np.nonzero(mask)
    rows.append({
        "i": idx,
        "n": n,
        "cx": float(xs.mean()),
        "cy": float(ys.mean()),
        "x0": int(xs.min()), "x1": int(xs.max()),
        "y0": int(ys.min()), "y1": int(ys.max()),
        "w": int(xs.max() - xs.min() + 1),
        "h": int(ys.max() - ys.min() + 1),
    })
reader.close()

if len(rows) < 5:
    raise SystemExit("too few frames with model mask")

cx = np.array([r["cx"] for r in rows])
cy = np.array([r["cy"] for r in rows])
w = np.array([r["w"] for r in rows])
h = np.array([r["h"] for r in rows])
dx = np.diff(cx)
dy = np.diff(cy)
# High-frequency: residual from a 5-frame moving average of the position.
def hp(v, k=5):
    kernel = np.ones(k) / k
    smooth = np.convolve(v, kernel, mode="same")
    return v - smooth

resx = hp(cx)
resy = hp(cy)

summary = {
    "source": str(src),
    "fps_meta": fps,
    "frames_with_model": len(rows),
    "duration_s": round(len(rows) / fps, 3) if fps else None,
    "centroid_x_mean": round(float(cx.mean()), 3),
    "centroid_y_mean": round(float(cy.mean()), 3),
    "frame_dx_mean_abs": round(float(np.abs(dx).mean()), 3),
    "frame_dy_mean_abs": round(float(np.abs(dy).mean()), 3),
    "frame_dx_max_abs": round(float(np.abs(dx).max()), 3),
    "frame_dy_max_abs": round(float(np.abs(dy).max()), 3),
    "hp_x_std": round(float(resx.std()), 3),
    "hp_y_std": round(float(resy.std()), 3),
    "bbox_w_std": round(float(w.std()), 3),
    "bbox_h_std": round(float(h.std()), 3),
    "bbox_w_minmax": [int(w.min()), int(w.max())],
    "bbox_h_minmax": [int(h.min()), int(h.max())],
}
(outdir / "jitter_info.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
(outdir / "jitter_info.csv").write_text(
    "i,cx,cy,w,h,n\n" + "\n".join(
        f"{r['i']},{r['cx']:.3f},{r['cy']:.3f},{r['w']},{r['h']},{r['n']}" for r in rows),
    encoding="utf-8")

# Plot centroid and bbox height.
W, H = 1000, 420
img = Image.new("RGB", (W, H), (20, 20, 24))
px = img.load()
def plot(vals, color, y0, y1):
    lo, hi = min(vals), max(vals)
    span = hi - lo or 1
    for x in range(W):
        idx = int(x * (len(vals) - 1) / (W - 1))
        y = int(y0 + (y1 - y0) * (vals[idx] - lo) / span)
        for yy in range(max(y0, y - 1), min(y1, y + 2)):
            px[x, yy] = color
plot(cx, (255, 80, 80), 20, 190)
plot(cy, (80, 180, 255), 220, 390)
img.save(outdir / "jitter_info_plot.png")
print(json.dumps(summary, ensure_ascii=False, indent=1))
