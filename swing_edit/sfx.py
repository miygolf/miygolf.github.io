"""Shared audio building blocks: loading, placement, synthesized SFX and a lo-fi music bed."""
import wave
import numpy as np
from scipy.signal import butter, lfilter, sosfilt

SR = 48000
rng = np.random.default_rng(7)

def load(path):
    with wave.open(path) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, w.getnchannels()).astype(np.float32) / 32768
    x = x.mean(axis=1)
    return x / (np.abs(x).max() + 1e-9) * 0.9

def env_adsr(n, a, r):
    e = np.ones(n); A = int(a * SR); R = int(r * SR)
    if A: e[:A] = np.linspace(0, 1, A)
    if R: e[-R:] *= np.linspace(1, 0, R)
    return e

def place(buf, sig, t, gain=1.0):
    i = int(t * SR)
    if i < 0: sig = sig[-i:]; i = 0
    j = min(len(buf), i + len(sig))
    if j > i: buf[i:j] += sig[: j - i] * gain

def tape_slow(src, stretch, cutoff=2500):
    """Slow down by `stretch` with pitch drop (like slowing a tape), then soften the highs."""
    out = np.interp(np.arange(int(len(src) * stretch)) / stretch, np.arange(len(src)), src)
    return lfilter(*butter(2, cutoff / (SR / 2)), out)

def boom(dur=1.6):
    t = np.arange(int(dur * SR)) / SR
    f = 38 + 90 * np.exp(-t * 18)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    n = rng.standard_normal(len(t)) * np.exp(-t * 30) * 0.5
    return s + lfilter(*butter(2, 1800 / (SR / 2)), n)

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

def music_bed(dur, bpm=88):
    """Lo-fi loop (Am9 - Fmaj7 - Cmaj7 - G6): pads, bass, swung drums, vinyl hiss. Unscaled."""
    n_total = int(dur * SR); beat = 60 / bpm; bar = 4 * beat
    def mtof(m): return 440 * 2 ** ((m - 69) / 12)
    CHORDS = [[57, 60, 64, 67, 71], [53, 57, 60, 64, 69], [48, 55, 59, 64, 67], [55, 59, 62, 64, 71]]
    ROOTS = [45, 41, 48, 43]
    pad = np.zeros(n_total); bass = np.zeros(n_total)
    for b in range(int(dur / bar) + 1):
        ch = CHORDS[b % 4]; i0 = int(b * bar * SR); n = int(bar * SR) + int(0.4 * SR)
        tt = np.arange(n) / SR; s = np.zeros(n)
        for m in ch:
            f = mtof(m)
            for det in (-0.12, 0.12):
                s += np.sin(2 * np.pi * f * (1 + det / 100) * tt + rng.uniform(0, 6.28))
                s += 0.25 * np.sin(2 * np.pi * 2 * f * tt)
        s *= env_adsr(n, 0.35, 0.6) * (0.85 + 0.15 * np.sin(2 * np.pi * 4.5 * tt))
        j = min(n_total, i0 + n); pad[i0:j] += s[: j - i0]
        for q in (0, 2.5):
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
    for k in range(int(dur / beat) + 1):
        tb = k * beat; pos = k % 4
        if pos in (0, 2): place(drums, kick, tb, 1.0)
        if pos == 2: place(drums, kick, tb + beat * 0.5, 0.55)
        if pos in (1, 3): place(drums, snare, tb + 0.012, 0.45)
        place(drums, hat, tb, 0.22); place(drums, hat, tb + beat * 0.55, 0.14)
    music = pad * 0.30 + bass * 0.32 + drums * 0.42
    return lfilter(*butter(1, 6000 / (SR / 2)), music) + lfilter(*butter(1, 3000 / (SR / 2)), rng.standard_normal(n_total)) * 0.006

def write_mix(path, voice, sfx, music, dur):
    t = np.arange(len(voice)) / SR
    mix = voice * 0.9 + sfx + music * 0.55
    mix = np.tanh(mix * 1.1) * 0.9
    mix *= np.interp(t, [0, 0.03, dur - 0.05, dur], [0, 1, 1, 0])
    st = np.stack([mix, mix], axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())
    return float(np.abs(mix).max())
