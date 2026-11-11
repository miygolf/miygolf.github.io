"""Build the soundtrack for the swing edit: original swing audio (real-time + pitched-down slow-mo),
a synthesized lo-fi bed, and whooshes/pops/dings synced to the render timeline.

Usage: python3 audio.py <workdir>   (needs work/orig.wav and work/timeline.json from render.py; writes work/audio.wav)
"""
import json, sys, wave
import numpy as np
from scipy.signal import butter, lfilter, sosfilt

D = sys.argv[1]
SR = 48000
TL = json.load(open(f"{D}/work/timeline.json"))
FPS = 30
DUR = TL["frames"] / FPS
n_total = int(DUR * SR)
rng = np.random.default_rng(7)

def load(path):
    with wave.open(path) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, w.getnchannels()).astype(np.float32) / 32768
    return x.mean(axis=1)
orig = load(f"{D}/work/orig.wav")
orig = orig / (np.abs(orig).max() + 1e-9) * 0.9

def env_adsr(n, a, r):
    e = np.ones(n); A = int(a * SR); R = int(r * SR)
    if A: e[:A] = np.linspace(0, 1, A)
    if R: e[-R:] *= np.linspace(1, 0, R)
    return e

def place(buf, sig, t, gain=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if j > i: buf[i:j] += sig[: j - i] * gain

voice = np.zeros(n_total)   # swing sounds
sfx = np.zeros(n_total)
music = np.zeros(n_total)

M = TL["marks"]
def at(name): return M[name] / FPS

# --- S1: real-time hook
HK = TL["hook"]
t_s1 = at("slow")
seg = orig[int(HK["t0"] * SR): int(HK["t0"] * SR) + int(t_s1 * SR)].copy()
seg *= env_adsr(len(seg), 0.05, 0.25)
place(voice, seg, 0, 1.0)

# --- S2: slow-mo, pitched down (tape-style) to match the playback speed, with a hold at impact
stretch = TL["slow_fps"] / FPS
s0 = TL["slow_t0"]; s1 = s0 + TL["n_slow"] / TL["slow_fps"]
src = orig[int(s0 * SR): int(s1 * SR)]
slow = np.interp(np.arange(int(len(src) * stretch)) / stretch, np.arange(len(src)), src)
slow = lfilter(*butter(2, 2500 / (SR / 2)), slow)
cut = int((TL["k_imp"] - 1) / FPS * SR)
hold = TL["hold"] / FPS
s2_start = t_s1
place(voice, slow[:cut] * env_adsr(cut, 0.3, 0.0) * 2.2, s2_start)
place(voice, slow[cut:] * 2.2 * env_adsr(len(slow) - cut, 0.0, 1.5), s2_start + cut / SR + hold)

def boom(dur=1.6):
    t = np.arange(int(dur * SR)) / SR
    f = 38 + 90 * np.exp(-t * 18)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    n = rng.standard_normal(len(t)) * np.exp(-t * 30) * 0.5
    return s + lfilter(*butter(2, 1800 / (SR / 2)), n)
t_imp_out = s2_start + cut / SR
place(sfx, boom(), t_imp_out, 0.9)

def whoosh(dur=0.55, up=True):
    n = int(dur * SR); x = rng.standard_normal(n)
    out = np.zeros(n); blk = 512
    for b in range(0, n, blk):
        u = b / n; fc = (300 + 4200 * u) if up else (4500 - 4000 * u)
        sos = butter(2, [max(fc * 0.6, 60) / (SR / 2), min(fc * 1.4, SR / 2 - 100) / (SR / 2)], btype="band", output="sos")
        out[b:b + blk] = sosfilt(sos, x[b:b + blk])
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return out * e / (np.abs(out).max() + 1e-9)

def pop(f=900):
    t = np.arange(int(0.12 * SR)) / SR
    return np.sin(2 * np.pi * f * t * (1 + 0.6 * np.exp(-t * 60))) * np.exp(-t * 38)

def ding():
    t = np.arange(int(1.8 * SR)) / SR
    return sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in
               ((1318.5, 1, 2.2), (1975.5, .5, 3), (2637, .3, 4.5), (659.25, .4, 2)))

def thud():
    t = np.arange(int(0.4 * SR)) / SR
    return np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 25)) * t) * np.exp(-t * 9)

place(sfx, whoosh(0.5), t_s1 - 0.3, 0.35)
cards = sorted(k for k in M if k.startswith("card"))
c0 = at(cards[0])
for name in cards + ["tempo", "rating"]:
    t = at(name)
    place(sfx, whoosh(0.45), t - 0.25, 0.3)
    if name.startswith("card"): place(sfx, pop(880), t + 8 / FPS, 0.35)
    if name == "card3": place(sfx, thud(), t + 30 / FPS, 0.6)
t_rating = at("rating")
place(sfx, ding(), t_rating + 34 / FPS, 0.32)
place(sfx, thud(), t_rating + 60 / FPS, 0.55)

# --- lo-fi bed: 88 bpm, Am9 - Fmaj7 - Cmaj7 - G6
BPM = 88; beat = 60 / BPM
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
CHORDS = [[57, 60, 64, 67, 71], [53, 57, 60, 64, 69], [48, 55, 59, 64, 67], [55, 59, 62, 64, 71]]
ROOTS = [45, 41, 48, 43]
bar = 4 * beat
t = np.arange(n_total) / SR
pad = np.zeros(n_total); bass = np.zeros(n_total)
nb = int(DUR / bar) + 1
for b in range(nb):
    ch = CHORDS[b % 4]; i0 = int(b * bar * SR); n = int(bar * SR) + int(0.4 * SR)
    tt = np.arange(n) / SR
    s = np.zeros(n)
    for m in ch:
        f = mtof(m)
        for det in (-0.12, 0.12):
            s += np.sin(2 * np.pi * f * (1 + det / 100) * tt + rng.uniform(0, 6.28))
            s += 0.25 * np.sin(2 * np.pi * 2 * f * tt)
    s *= env_adsr(n, 0.35, 0.6) * (0.85 + 0.15 * np.sin(2 * np.pi * 4.5 * tt))
    j = min(n_total, i0 + n); pad[i0:j] += s[: j - i0]
    for q in (0, 2.5):  # bass hits
        k0 = int((b * bar + q * beat) * SR); bn = int(beat * 1.4 * SR); bt = np.arange(bn) / SR
        bs = np.sin(2 * np.pi * mtof(ROOTS[b % 4]) * bt) * np.exp(-bt * 2.2) * env_adsr(bn, 0.01, 0.1)
        j = min(n_total, k0 + bn)
        if k0 < n_total: bass[k0:j] += bs[: j - k0]
pad = lfilter(*butter(2, 1600 / (SR / 2)), pad)
pad /= np.abs(pad).max() + 1e-9; bass /= np.abs(bass).max() + 1e-9

drums = np.zeros(n_total)
kt = np.arange(int(0.35 * SR)) / SR
kick = np.sin(2 * np.pi * np.cumsum(45 + 110 * np.exp(-kt * 35)) / SR) * np.exp(-kt * 9)
st = np.arange(int(0.25 * SR)) / SR
snare = lfilter(*butter(2, [900 / (SR / 2), 5000 / (SR / 2)], btype="band"), rng.standard_normal(len(st))) * np.exp(-st * 22)
snare /= np.abs(snare).max()
ht = np.arange(int(0.05 * SR)) / SR
hat = lfilter(*butter(2, 7000 / (SR / 2), btype="high"), rng.standard_normal(len(ht))) * np.exp(-ht * 90)
hat /= np.abs(hat).max()
for k in range(int(DUR / beat) + 1):
    tb = k * beat; pos = k % 4
    if pos in (0, 2): place(drums, kick, tb, 1.0)
    if pos == 2: place(drums, kick, tb + beat * 0.5, 0.55)
    if pos in (1, 3): place(drums, snare, tb + 0.012, 0.45)
    place(drums, hat, tb, 0.22); place(drums, hat, tb + beat * 0.55, 0.14)   # swung 8ths

music = pad * 0.30 + bass * 0.32 + drums * 0.42
# lo-fi: gentle lowpass + vinyl-ish noise
music = lfilter(*butter(1, 6000 / (SR / 2)), music) + lfilter(*butter(1, 3000 / (SR / 2)), rng.standard_normal(n_total)) * 0.006
# dynamics: quiet under the swing sounds, full under the cards; duck at impact hold
gain = np.interp(t, [0, t_s1 - 0.2, t_s1, c0 - 0.4, c0 + 0.2, DUR - 1.6, DUR], [0.30, 0.30, 0.45, 0.45, 0.85, 0.85, 0.0])
duck = 1 - 0.6 * np.exp(-np.maximum(t - t_imp_out, 0) * 2.5) * (t >= t_imp_out)
music *= gain * duck

mix = voice * 0.9 + sfx + music * 0.55
mix = np.tanh(mix * 1.1) * 0.9
mix *= np.interp(t, [0, 0.03, DUR - 0.05, DUR], [0, 1, 1, 0])
st = np.stack([mix, mix], axis=1)
with wave.open(f"{D}/work/audio.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())
print("audio", DUR, "s  peak", float(np.abs(mix).max()))
