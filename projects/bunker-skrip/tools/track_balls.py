#!/usr/bin/env python3
"""Tracks the ball that landed right of the middle pin in IMG_0413 (owner v6: "dia duduk belah kanan. Pin tengah belah kanan") (5.9-8.2 s, the phone settles on the green but drifts),
so the punch-in keeps it centred and the ring stays on it. Writes edit/ball_track.json: [[src_t, x, y, n], ...] in the upright
1080x1920 frame. At 6.6 s it sits at (700, 978), right of the middle pin (x 572), near the right pin's base; tracked backwards and forwards. Run from the project folder: python3 tools/track_balls.py"""
import json, os, subprocess
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T0, T1, FPS = 5.9, 8.25, 15
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(T0), "-t", str(T1 - T0), "-i", os.path.join(ROOT, ".src", "IMG_0413.MOV"),
                      "-vf", f"fps={FPS},scale=1080:1920", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, 1920, 1080, 3)
REF_T, REF = 6.6, np.array([700.0, 978.0])
def find(f, est):
    x0, y0 = int(est[0]) - 34, int(est[1]) - 26                 # small window: the next ball is ~70 px away
    win = f[y0:y0 + 52, x0:x0 + 68].astype(int)
    lum = win.mean(axis=2)
    bright = lum > max(np.median(lum) + 40, lum.max() - 30)                          # the ball: much brighter than the green
    ys, xs = np.nonzero(bright)
    return (np.array([x0 + xs.mean(), y0 + ys.mean()]), len(xs)) if len(xs) > 3 and lum.max() > np.median(lum) + 45 else (est, 0)
iref = int(round((REF_T - T0) * FPS)); res = {}
for rng in (range(iref, len(fr)), range(iref, -1, -1)):
    est = REF.copy()
    for i in rng:
        est, n = find(fr[i], est); res[i] = (est, n)
out = [[round(T0 + i / FPS, 3), round(float(res[i][0][0]), 1), round(float(res[i][0][1]), 1), int(res[i][1])] for i in sorted(res)]
json.dump(out, open(os.path.join(ROOT, "edit", "ball_track.json"), "w"))
for r in out[::3]: print(r)
