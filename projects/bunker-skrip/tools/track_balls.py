#!/usr/bin/env python3
"""Tracks the two balls that landed by the yellow flag in IMG_0413 (5.9-8.2 s, the phone settles on the green but drifts),
so the punch-in can keep them centred and the ring stays on them. Writes edit/ball_track.json: [[src_t, x, y], ...] in the upright
1080x1920 frame (mean of the two balls). Run from the project folder: python3 tools/track_balls.py"""
import json, os, subprocess
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T0, T1, FPS = 5.9, 8.25, 15
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(T0), "-t", str(T1 - T0), "-i", os.path.join(ROOT, ".src", "IMG_0413.MOV"),
                      "-vf", f"fps={FPS},scale=1080:1920", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, 1920, 1080, 3)
est = np.array([450.0, 1022.0]); out = []
for i, f in enumerate(fr):
    x0, y0 = int(est[0]) - 160, int(est[1]) - 110
    win = f[y0:y0 + 220, x0:x0 + 320].astype(int)
    bright = (win.min(axis=2) > 190) & (win.max(axis=2) - win.min(axis=2) < 40)      # white, unsaturated = ball
    ys, xs = np.nonzero(bright)
    if len(xs) > 6:
        est = np.array([x0 + xs.mean(), y0 + ys.mean()])
    out.append([round(T0 + i / FPS, 3), round(float(est[0]), 1), round(float(est[1]), 1), int(len(xs))])
json.dump(out, open(os.path.join(ROOT, "edit", "ball_track.json"), "w"))
for r in out[::3]: print(r)
