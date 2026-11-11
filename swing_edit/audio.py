"""Build the soundtrack for a single-swing edit: original swing audio (real-time + pitched-down slow-mo),
a synthesized lo-fi bed, and whooshes/pops/dings synced to the render timeline.

Usage: python3 audio.py <workdir>   (needs work/orig.wav and work/timeline.json from render.py; writes work/audio.wav)
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sfx import *

D = sys.argv[1]
TL = json.load(open(f"{D}/work/timeline.json"))
FPS = 30
DUR = TL["frames"] / FPS
n_total = int(DUR * SR)
orig = load(f"{D}/work/orig.wav")
voice = np.zeros(n_total); fx = np.zeros(n_total)
M = TL["marks"]
def at(name): return M[name] / FPS

# real-time hook
HK = TL["hook"]; t_s1 = at("slow")
seg = orig[int(HK["t0"] * SR): int(HK["t0"] * SR) + int(t_s1 * SR)].copy()
place(voice, seg * env_adsr(len(seg), 0.05, 0.25), 0)

# slow-mo, pitched down to match playback speed, with a hold at impact
s0 = TL["slow_t0"]; s1 = s0 + TL["n_slow"] / TL["slow_fps"]
slow = tape_slow(orig[int(s0 * SR): int(s1 * SR)], TL["slow_fps"] / FPS)
cut = int((TL["k_imp"] - 1) / FPS * SR); hold = TL["hold"] / FPS
place(voice, slow[:cut] * env_adsr(cut, 0.3, 0.0) * 2.2, t_s1)
place(voice, slow[cut:] * 2.2 * env_adsr(len(slow) - cut, 0.0, 1.5), t_s1 + cut / SR + hold)
t_imp_out = t_s1 + cut / SR
place(fx, boom(), t_imp_out, 0.9)

place(fx, whoosh(0.5), t_s1 - 0.3, 0.35)
cards = sorted(k for k in M if k.startswith("card"))
c0 = at(cards[0])
for name in cards + ["tempo", "rating"]:
    t = at(name)
    place(fx, whoosh(0.45), t - 0.25, 0.3)
    if name.startswith("card"): place(fx, pop(880), t + 8 / FPS, 0.35)
    if name == "card3": place(fx, thud(), t + 30 / FPS, 0.6)
t_rating = at("rating")
place(fx, ding(), t_rating + 34 / FPS, 0.32)
place(fx, thud(), t_rating + 60 / FPS, 0.55)

# music: quiet under the swing sounds, full under the cards; duck at impact hold
t = np.arange(n_total) / SR
music = music_bed(DUR)
gain = np.interp(t, [0, t_s1 - 0.2, t_s1, c0 - 0.4, c0 + 0.2, DUR - 1.6, DUR], [0.30, 0.30, 0.45, 0.45, 0.85, 0.85, 0.0])
duck = 1 - 0.6 * np.exp(-np.maximum(t - t_imp_out, 0) * 2.5) * (t >= t_imp_out)
peak = write_mix(f"{D}/work/audio.wav", voice, fx, music * gain * duck, DUR)
print("audio", DUR, "s  peak", peak)
