"""LK-track anchor points in assets/footage/edit.mp4 from a seed frame, forwards and backwards.
Writes src/tracks.json: {name: [[t, x, y], ...]} sampled every 0.1 s."""
import cv2, json, numpy as np, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
FPS = 30
JOBS = {  # name: (seed_t, t0, t1, x, y)
    "tail": (11.2, 9.0, 13.0, 697, 922),
    "rotor": (11.2, 9.0, 13.0, 900, 1042),
    "rotorL": (11.2, 9.0, 13.0, 360, 975),
}
cap = cv2.VideoCapture(str(ROOT / "assets/footage/edit_clean.mp4"))
frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
lk = dict(winSize=(61, 61), maxLevel=4, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
out = {}
for name, (ts, t0, t1, x, y) in JOBS.items():
    s = round(ts * FPS); pos = {s: (x, y)}
    for step, end in ((1, round(t1 * FPS)), (-1, round(t0 * FPS))):
        p = np.array([[[x, y]]], np.float32); i = s
        while i != end:
            j = i + step
            if j >= len(frames): break
            p, st, _ = cv2.calcOpticalFlowPyrLK(frames[i], frames[j], p, None, **lk)
            pos[j] = tuple(p[0, 0]); i = j
    out[name] = [[round(k / FPS, 2), round(float(v[0])), round(float(v[1]))] for k, v in sorted(pos.items()) if k % 3 == 0]
json.dump(out, open(ROOT / "src/tracks.json", "w"))
for k, v in out.items(): print(k, v[::5])
