"""Procedurally synthesised ~128.6 BPM electro-house track, cut to the edit.

No samples or third-party audio: every sound is generated here, so the
track is royalty-free. Section changes follow timeline.build().
"""
import numpy as np
from scipy.signal import butter, sosfilt

from timeline import BAR, BEAT, build

SR = 44100
rng = np.random.default_rng(7)

# A minor: Am - F - C - G
CHORDS = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
ROOTS = [45, 41, 48, 43]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n, a=0.002, d=0.2, s=0.0, r=0.0, hold=None):
    t = np.arange(n) / SR
    e = np.minimum(t / max(a, 1e-4), 1.0)
    e *= s + (1 - s) * np.exp(-np.maximum(t - a, 0) / max(d, 1e-4))
    if hold is not None and r > 0:
        e *= np.clip(1 - (t - hold) / r, 0, 1)
    return e


def lp(x, fc, order=2):
    return sosfilt(butter(order, min(fc, SR / 2 - 100), "low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)


def saw(f, n, detune=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for d in ([0.0] if detune == 0 else [-detune, 0.0, detune]):
        ph = (t * f * (1 + d) + rng.random()) % 1.0
        out += 2 * ph - 1
    return out / (1 if detune == 0 else 3)


def kick(n=int(0.45 * SR)):
    t = np.arange(n) / SR
    f = 45 + 120 * np.exp(-t / 0.03)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.28)
    click = hp(rng.standard_normal(n), 3000) * np.exp(-t / 0.004) * 0.3
    return np.tanh(1.6 * (body + click))


def clap(n=int(0.3 * SR)):
    t = np.arange(n) / SR
    nz = hp(lp(rng.standard_normal(n), 6000), 900)
    e = np.zeros(n)
    for o in (0, 0.011, 0.022):
        e += (t >= o) * np.exp(-np.maximum(t - o, 0) / (0.008 if o < 0.02 else 0.12))
    return nz * e * 0.7


def hat(n, decay):
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-t / decay)


def crash(n=int(2.0 * SR)):
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 4000) * np.exp(-t / 0.7) * 0.5


def riser(n):
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    out = np.zeros(n)
    steps = 32
    for i in range(steps):
        a, b = i * n // steps, (i + 1) * n // steps
        out[a:b] = hp(x[a:b], 300 + 7000 * (i / steps) ** 2, 1)
    return out * (t / t[-1]) ** 2 * 0.5


def boom(n=int(1.5 * SR)):
    t = np.arange(n) / SR
    f = 35 + 60 * np.exp(-t / 0.08)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.6)


def place(buf, x, t, gain=1.0):
    i = int(round(t * SR))
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i] * gain


def render(impact_sfx=None):
    segs, total = build()
    nbars = int(round(total / BAR))
    n = int((total + 2.5) * SR)
    drums, bass, synth, fx = (np.zeros(n) for _ in range(4))

    titles = {int(round(s["t0"] / BAR)) for s in segs if s["kind"] == "title"}
    summary_bar = int(round(next(s["t0"] for s in segs if s["kind"] == "summary") / BAR))
    drop = 2

    K, C = kick(), clap()
    OH, CH = hat(int(0.25 * SR), 0.06), hat(int(0.08 * SR), 0.015)
    duck = np.ones(n)
    dl = int(BEAT * SR)
    dshape = 1 - 0.75 * np.exp(-np.arange(dl) / SR / 0.09)

    for b in range(nbars):
        t0 = b * BAR
        ch = CHORDS[b % 4]
        root = ROOTS[b % 4]
        main = drop <= b < summary_bar
        outro = b >= summary_bar
        last_outro = b == nbars - 1

        # Drums
        if main:
            for k in range(4):
                place(drums, K, t0 + k * BEAT)
                i = int((t0 + k * BEAT) * SR)
                duck[i:i + dl] = np.minimum(duck[i:i + dl], dshape[: len(duck[i:i + dl])])
            for k in (1, 3):
                place(drums, C, t0 + k * BEAT, 0.8)
            for k in range(4):
                place(drums, OH, t0 + (k + 0.5) * BEAT, 0.25)
            for k in range(16):
                place(drums, CH, t0 + k * BEAT / 4, 0.12 if k % 2 else 0.07)
            if b + 1 in titles or b + 1 == summary_bar:  # snare fill into each new movement
                for k in range(8):
                    place(drums, C, t0 + 3 * BEAT + k * BEAT / 8, 0.25 + 0.06 * k)
        elif outro and not last_outro:
            for k in (0, 2):
                place(drums, K, t0 + k * BEAT, 0.9)
            place(drums, C, t0 + 3 * BEAT, 0.6)
            for k in range(8):
                place(drums, CH, t0 + k * BEAT / 2, 0.08)
        elif last_outro:
            place(drums, K, t0)
        elif b == drop - 1:  # intro build: snare roll
            for k in range(16):
                place(drums, C, t0 + k * BEAT / 4, 0.1 + 0.035 * k)

        if b in titles or b == drop or b == summary_bar or last_outro:
            place(fx, crash(), t0, 0.6)
        if b + 1 in titles:
            place(fx, riser(int(BAR * SR)), t0, 0.35)

        # Bass: off-beat 8ths with a short pluck envelope
        if main:
            nlen = int(BEAT / 2 * SR)
            for k in range(8):
                if k % 2 == 0:
                    continue
                note = saw(hz(root - 12), nlen) * env(nlen, 0.003, 0.09, 0.2)
                place(bass, lp(note, 900), t0 + k * BEAT / 2, 0.5)
            sub = np.sin(2 * np.pi * hz(root - 12) * np.arange(int(BAR * SR)) / SR)
            place(bass, sub, t0, 0.25)
        elif outro:
            nlen = int(BAR * SR)
            place(bass, np.sin(2 * np.pi * hz(root - 12) * np.arange(nlen) / SR) * env(nlen, 0.01, 1.2), t0, 0.4)

        # Pad (always) - opens up at the drop
        nlen = int(BAR * SR)
        pad = sum(saw(hz(m), nlen, 0.006) for m in ch) / 3
        fc = 600 + 2200 * (b / max(drop, 1)) if b < drop else (3200 if main else 1800)
        place(synth, lp(pad, fc) * env(nlen, 0.05, 10, 1.0, 0.05, BAR - 0.05), t0, 0.22)

        # Pluck arpeggio (16ths) in the main section
        if main or (outro and not last_outro):
            seq = [ch[0], ch[1], ch[2], ch[1] + 12, ch[2] + 12, ch[1] + 12, ch[2], ch[0] + 12]
            step = BEAT / 4 if main else BEAT / 2
            plen = int(step * SR)
            for k in range(int(round(BAR / step))):
                m = seq[k % len(seq)] + 12
                p = (saw(hz(m), plen) * 0.6 + np.sign(np.sin(2 * np.pi * hz(m) * np.arange(plen) / SR)) * 0.4)
                place(synth, lp(p * env(plen, 0.002, 0.07), 5000), t0 + k * step, 0.16)

    if impact_sfx is not None:
        for t, x, g in impact_sfx:
            place(fx, x, t, g)
    for s in segs:
        if s["kind"] in ("slow", "intro"):
            place(fx, boom(), s["t0"] + s["impact"], 0.5)

    mix = drums * 0.9 + (bass + synth) * duck + fx
    mix = hp(mix, 25)
    tail = int(total * SR)
    fade = np.ones(n)
    fade[tail:] = np.linspace(1, 0, n - tail)
    mix *= fade
    mix = np.tanh(mix * 1.1)
    mix /= np.abs(mix).max() / 0.89
    return mix[: int((total + 0.5) * SR)]


if __name__ == "__main__":
    import sys
    import wave
    x = render()
    with wave.open(sys.argv[1] if len(sys.argv) > 1 else "music.wav", "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
