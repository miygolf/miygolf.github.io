#!/usr/bin/env python3
# Swing metrics from edit/pose.json at hand-picked key frames (checked on frame strips). Frame = 0-based index at 59.94 fps.
# Coordinates are converted to pixels of the upright 2160x3840 frame (x*2160, y*3840) so angles are true.
import json, math
import numpy as np
FPS = 59.94
KEYS = {  # address (last still frame), takeaway, top, impact, finish
    "clip3": dict(view="dtl", phase="before", address=134, takeaway=137, top=168, impact=183, finish=230),
    "clip1": dict(view="dtl", phase="after", address=48, takeaway=51, top=84, impact=100, finish=170),
    "clip2": dict(view="face", phase="before", address=8, takeaway=10, top=54, impact=69, finish=110),
    "clip4": dict(view="face", phase="after", address=33, takeaway=36, top=84, impact=105, finish=150),
}
d = json.load(open("edit/pose.json"))
def P(c, k, i):
    q = d[c][k][i]; return np.array([q[0] * 2160, q[1] * 3840])
def mid(c, k, a, b): return (P(c, k, a) + P(c, k, b)) / 2
def avg(c, k, i, n=2):  # smooth +-n frames
    return np.mean([P(c, j, i) for j in range(k - n, k + n + 1)], axis=0)
def amid(c, k, a, b, n=2): return (avg(c, k, a, n) + avg(c, k, b, n)) / 2
out = {}
for c, K in KEYS.items():
    a, t, im = K["address"], K["top"], K["impact"]
    sh = lambda k: amid(c, k, 11, 12); hp = lambda k: amid(c, k, 23, 24); hd = lambda k: avg(c, k, 0)
    torso = np.linalg.norm(sh(a) - hp(a))
    spine = lambda k: math.degrees(math.atan2(abs(sh(k)[0] - hp(k)[0]), hp(k)[1] - sh(k)[1]))  # forward tilt from vertical
    r = dict(view=K["view"], phase=K["phase"],
             backswing_s=round((t - K["takeaway"]) / FPS, 3), downswing_s=round((im - t) / FPS, 3),
             tempo=round((t - K["takeaway"]) / (im - t), 2))
    if K["view"] == "dtl":
        r.update(spine_address=round(spine(a), 1), spine_top=round(spine(t), 1), spine_impact=round(spine(im), 1),
                 spine_loss=round(spine(a) - spine(im), 1),
                 hip_to_ball_pct=round(100 * (hp(im)[0] - hp(a)[0]) / torso, 1),      # + = hips pushed toward the ball (early extension)
                 head_drop_impact_pct=round(100 * (hd(im)[1] - hd(a)[1]) / torso, 1),  # + = head lower than at address
                 head_rise_top_pct=round(100 * (hd(a)[1] - hd(t)[1]) / torso, 1))
    else:
        sw = lambda k: abs(avg(c, k, 11)[0] - avg(c, k, 12)[0]); hw = lambda k: abs(avg(c, k, 23)[0] - avg(c, k, 24)[0])
        r.update(head_sway_top_pct=round(100 * (hd(t)[0] - hd(a)[0]) / torso, 1),       # - = away from target
                 head_move_impact_pct=round(100 * (hd(im)[0] - hd(a)[0]) / torso, 1),
                 hip_sway_top_pct=round(100 * (hp(t)[0] - hp(a)[0]) / torso, 1),
                 hip_slide_impact_pct=round(100 * (hp(im)[0] - hp(a)[0]) / torso, 1),
                 shoulder_width_top_ratio=round(sw(t) / sw(a), 2),                         # smaller = more shoulder turn
                 hip_width_impact_ratio=round(hw(im) / hw(a), 2),                          # smaller = hips more open
                 spine_tilt_impact=round(math.degrees(math.atan2(hp(im)[0] - sh(im)[0], hp(im)[1] - sh(im)[1])), 1))
    out[c] = r
    print(c, r)
json.dump({"keys": KEYS, "metrics": out}, open("edit/metrics.json", "w"), indent=1)
