"""Soundtrack for the side-by-side comparison edit.

Usage: python3 compare_audio.py <outdir> <workdir_left> <workdir_right>
Needs <outdir>/timeline.json from compare.py and work/orig.wav in each workdir; writes <outdir>/audio.wav.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sfx import *

OUT, WL, WR = sys.argv[1:4]
TL = json.load(open(f"{OUT}/timeline.json"))
FPS = 30
DUR = TL["frames"] / FPS
n_total = int(DUR * SR)
M = TL["marks"]
def at(name): return M[name] / FPS
voice = np.zeros(n_total); fx = np.zeros(n_total)
aL, aR = load(f"{WL}/work/orig.wav"), load(f"{WR}/work/orig.wav")
impL, impR = TL["left"]["impact"], TL["right"]["impact"]

# real speed: both clips lined up on impact, so the two strikes land together
pre = TL["rt_pre"]; t_slow = at("slow")
for a, imp in ((aL, impL), (aR, impR)):
    seg = a[int((imp - pre) * SR): int((imp - pre + t_slow) * SR)].copy()
    place(voice, seg * env_adsr(len(seg), 0.05, 0.3), 0, 0.65)

# slow-mo: pitched-down swing audio arriving at impact exactly at the hold
lead = TL["f_imp"] / 120                      # common-timeline source seconds before impact
t_hold = t_slow + TL["f_imp"] / FPS
before = tape_slow(aR[int((impR - lead) * SR): int(impR * SR)], 4)
after = tape_slow(aR[int(impR * SR): int((impR + 0.5) * SR)], 4)
place(voice, before * env_adsr(len(before), 0.4, 0.0) * 2.0, t_hold - len(before) / SR)
place(voice, after * env_adsr(len(after), 0.0, 1.2) * 2.0, t_hold + TL["hold"] / FPS)
place(fx, boom(), t_hold, 0.9)
place(fx, whoosh(0.5), t_slow - 0.3, 0.35)

cards = sorted(k for k in M if k.startswith("card"))
for name in cards + ["tempo", "score", "learn"]:
    t = at(name)
    place(fx, whoosh(0.45), t - 0.25, 0.3)
    if name.startswith("card") or name == "tempo": place(fx, pop(880), t + 34 / FPS, 0.35)
place(fx, thud(), at("score") + 50 / FPS, 0.5)
place(fx, ding(), at("score") + 78 / FPS, 0.35)

t = np.arange(n_total) / SR
c0 = at(cards[0])
gain = np.interp(t, [0, t_slow - 0.2, t_slow, c0 - 0.4, c0 + 0.2, DUR - 1.6, DUR], [0.30, 0.30, 0.45, 0.45, 0.85, 0.85, 0.0])
duck = 1 - 0.6 * np.exp(-np.maximum(t - t_hold, 0) * 2.5) * (t >= t_hold)
peak = write_mix(f"{OUT}/audio.wav", voice, fx, music_bed(DUR) * gain * duck, DUR)
print("audio", DUR, "s  peak", peak)
