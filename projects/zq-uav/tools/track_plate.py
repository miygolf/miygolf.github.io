"""Track the car number plate in assets/footage/edit.mp4 from hand-picked seeds (film time, x, y).
Each frame takes the LK track from its nearest seed. Writes src/plate_track.json {frame: [x, y, w, h]}."""
import cv2, json, numpy as np, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
FPS = 30
# (segment start, segment end, [(t, x, y, w, h), ...]) — box size grows as the camera nears the car
SEGMENTS = [
    (13.0, 17.5, [(13.0, 350, 90, 150, 60), (13.4, 438, 96, 156, 70), (13.7, 528, 100, 170, 100), (14.0, 590, 110, 170, 100), (14.3, 632, 135, 170, 96), (15.0, 730, 150, 170, 80),
                  (16.0, 710, 210, 180, 80), (17.3, 870, 240, 180, 80)]),
    (19.2, 21.5, [(20.0, 1000, 416, 170, 70), (20.7, 640, 340, 160, 64), (21.4, 370, 206, 160, 64)]),
]
cap = cv2.VideoCapture(str(ROOT / "assets/footage/edit_clean.mp4"))
frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
lk = dict(winSize=(81, 81), maxLevel=4, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))

def track(i0, x, y, i1):
    out = {i0: (x, y)}; p = np.array([[[x, y]]], np.float32); i = i0
    step = 1 if i1 > i0 else -1
    while i != i1:
        j = i + step
        p, st, _ = cv2.calcOpticalFlowPyrLK(frames[i], frames[j], p, None, **lk)
        out[j] = (float(p[0, 0, 0]), float(p[0, 0, 1])); i = j
    return out

res = {}
for a, b, seeds in SEGMENTS:
    fa, fb = round(a * FPS), min(round(b * FPS), len(frames)) - 1
    sf = [round(s[0] * FPS) for s in seeds]
    for k, (t, x, y, w, h) in enumerate(seeds):
        lo = fa if k == 0 else (sf[k - 1] + sf[k]) // 2 + 1
        hi = fb if k == len(seeds) - 1 else (sf[k] + sf[k + 1]) // 2
        tr = {**track(sf[k], x, y, lo), **track(sf[k], x, y, hi)}
        # box size eases between neighbouring seeds
        for f in range(lo, hi + 1):
            nb = seeds[k + 1] if f > sf[k] and k + 1 < len(seeds) else (seeds[k - 1] if f < sf[k] and k > 0 else seeds[k])
            fn = round(nb[0] * FPS); u = 0 if fn == sf[k] else min(1, abs(f - sf[k]) / abs(fn - sf[k])) * 0.5
            ww, hh = w + (nb[3] - w) * u, h + (nb[4] - h) * u
            res[f] = [round(tr[f][0]), round(tr[f][1]), round(ww), round(hh)]
json.dump(res, open(ROOT / "src/plate_track.json", "w"))
print(len(res), "frames;", [(f / FPS, res[f]) for f in sorted(res)[::15]])
