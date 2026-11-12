#!/usr/bin/env python3
"""Finds the ball after impact at full 4K resolution by frame differencing (camera on a tripod).
Searches a crop of the upright 2160x3840 frame; prints the strongest small moving blobs per frame.
   python3 tools/track_ball.py START DUR X0 Y0 X1 Y1   (4K source pixels)  -> work/cands.json"""
import sys, json, subprocess, numpy as np
a, d = float(sys.argv[1]), float(sys.argv[2])
x0, y0, x1, y1 = map(int, sys.argv[3:7])
W, H = x1 - x0, y1 - y0
p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{a}", "-t", f"{d}", "-i", ".src/clip1.mov",
                      "-vf", f"crop={W}:{H}:{x0}:{y0}", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
fr = []
while True:
    b = p.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.int16)
    fr.append(f.sum(axis=2))
dt = 1001 / 60000
out = []
from scipy.ndimage import uniform_filter, maximum_filter
for i in range(2, len(fr) - 2):
    # pixel must differ from both neighbours two frames away (object passing) -> suppresses slow leaf/cloud drift a bit
    m = np.minimum(np.minimum(np.abs(fr[i] - fr[i - 2]), np.abs(fr[i] - fr[i + 2])), np.minimum(np.abs(fr[i] - fr[i - 1]), np.abs(fr[i] - fr[i + 1])))
    s = uniform_filter(m.astype(np.float32), 5)
    pk = (s == maximum_filter(s, 41)) & (s > float(sys.argv[7]) if len(sys.argv) > 7 else s > 18)
    ys, xs = np.nonzero(pk)
    v = s[ys, xs]
    o = np.argsort(v)[::-1][:6]
    out.append({"t": round(a + i * dt, 4), "c": [[int(xs[k] + x0), int(ys[k] + y0), round(float(v[k]), 1)] for k in o]})
json.dump(out, open("work/cands.json", "w"))
for q in out: print(q["t"], q["c"][:5])
