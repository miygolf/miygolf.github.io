#!/usr/bin/env python3
"""Ball in the sky: per-frame |frame - temporal median| on the red channel (the white ball against blue sky), sky pixels only.
   python3 tools/track_sky.py START DUR X0 Y0 X1 Y1 -> work/sky_cands.json"""
import sys, json, subprocess, numpy as np
from scipy.ndimage import maximum_filter, median_filter
a, d = float(sys.argv[1]), float(sys.argv[2]); x0, y0, x1, y1 = map(int, sys.argv[3:7])
W, H = x1 - x0, y1 - y0
p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{a}", "-t", f"{d}", "-i", ".src/clip1.mov", "-vf", f"crop={W}:{H}:{x0}:{y0}",
                      "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
F = []
while True:
    b = p.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    F.append(np.frombuffer(b, np.uint8).reshape(H, W, 3))
R = np.stack([f[..., 0] for f in F]).astype(np.int16)
Bc = np.stack([f[..., 2] for f in F]).astype(np.int16)
med = np.median(R, axis=0)
sky = (np.median(Bc, axis=0) > 170) & (np.median(Bc, axis=0) - med > 15)     # blue-ish bright = sky
sky = median_filter(sky.astype(np.uint8), 9) > 0
dt = 1001 / 60000; out = []
for i in range(len(F)):
    df = (R[i] - med) * sky
    pk = (df == maximum_filter(df, 31)) & (df > 14)
    ys, xs = np.nonzero(pk); v = df[ys, xs]; o = np.argsort(v)[::-1][:5]
    out.append({"t": round(a + i * dt, 4), "c": [[int(xs[k] + x0), int(ys[k] + y0), int(v[k])] for k in o]})
json.dump(out, open("work/sky_cands.json", "w"))
for q in out: print(q["t"], q["c"][:4])
