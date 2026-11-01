"""Generate a gentle, original piano + pad soundtrack for the Tingkat Valley memory video.

Usage: python3 music.py OUT.wav DURATION_SECONDS
"""
import sys
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile

SR = 44100
OUT = sys.argv[1]
DUR = float(sys.argv[2])
BPM = 72
BEAT = 60 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(7)

N = int((DUR + 6) * SR)
L = np.zeros(N)
R = np.zeros(N)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def piano(m, dur, vel):
    """Additive soft piano tone."""
    f = midi_hz(m)
    n = int((dur + 2.5) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(1, 8):
        fk = f * k * (1 + 0.0004 * k * k)  # slight inharmonicity
        if fk > 12000:
            break
        amp = 1 / k ** 1.6
        decay = 1.2 + 0.9 * k + f / 400
        out += amp * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * np.exp(-decay * t)
    att = np.minimum(1, t / 0.006)
    rel = np.where(t > dur, np.exp(-(t - dur) * 6), 1.0)
    return out * att * rel * vel


def pad(m, dur, vel):
    f = midi_hz(m)
    n = int((dur + 1.5) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for det in (-0.12, 0.0, 0.11):
        ff = f * 2 ** (det / 12)
        out += np.sin(2 * np.pi * ff * t) + 0.25 * np.sin(2 * np.pi * 2 * ff * t)
    env = np.minimum(1, t / 1.2) * np.where(t > dur, np.exp(-(t - dur) * 2.5), 1.0)
    return out * env * vel / 3


def add(sig, start, pan=0.0):
    i = int(start * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    R[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


# G major: G - D/F# - Em - C   |  Em - C - G - D
G, D, Em, C, Am = [55, 59, 62], [54, 57, 62], [52, 55, 59], [48, 52, 55], [45, 48, 52]
bass = {"G": 43, "D": 42, "Em": 40, "C": 36, "Am": 45}
chords = {"G": G, "D": D, "Em": Em, "C": C, "Am": Am}
prog = ["G", "D", "Em", "C"] * 2 + ["Em", "C", "G", "D"] + ["G", "D", "Em", "C"] + ["Am", "C", "D", "D"]

# Simple, singable melody (MIDI, beat offset, length in beats) per bar
mel = {
    4: [(74, 0, 1.5), (72, 1.5, 0.5), (71, 2, 2)],
    5: [(69, 0, 1.5), (71, 1.5, 0.5), (69, 2, 2)],
    6: [(67, 0, 1), (71, 1, 1), (74, 2, 2)],
    7: [(72, 0, 1.5), (71, 1.5, 0.5), (67, 2, 2)],
    8: [(71, 0, 1), (74, 1, 1), (76, 2, 2)],
    9: [(76, 0, 1), (74, 1, 1), (72, 2, 2)],
    10: [(71, 0, 1.5), (72, 1.5, 0.5), (74, 2, 2)],
    11: [(74, 0, 1), (72, 1, 1), (69, 2, 2)],
    12: [(74, 0, 1.5), (72, 1.5, 0.5), (71, 2, 2)],
    13: [(69, 0, 1.5), (71, 1.5, 0.5), (74, 2, 2)],
    14: [(79, 0, 1), (78, 1, 1), (76, 2, 2)],
    15: [(76, 0, 1.5), (74, 1.5, 0.5), (72, 2, 2)],
    16: [(72, 0, 1), (71, 1, 1), (69, 2, 2)],
    17: [(72, 0, 2), (71, 2, 2)],
    18: [(69, 0, 2), (66, 2, 2)],
    19: [(67, 0, 4)],
}

nbars = int(np.ceil(DUR / BAR))
for b in range(nbars):
    name = prog[b] if b < len(prog) else "G"
    if b >= nbars - 1:
        name = "G"
    t0 = b * BAR
    ch = chords[name]
    swell = min(1.0, 0.45 + b * 0.08)
    # pad underneath everything
    add(pad(bass[name] + 12, BAR, 0.05 * swell), t0)
    for m in ch:
        add(pad(m, BAR, 0.035 * swell), t0, pan=rng.uniform(-0.4, 0.4))
    # bass note
    add(piano(bass[name], BAR, 0.32 * swell), t0, pan=-0.15)
    # flowing 8th-note arpeggio
    if b >= 1 and b < nbars - 1:
        arp = [ch[0], ch[1], ch[2], ch[1] + 12, ch[2], ch[1], ch[0] + 12, ch[2]]
        for i, m in enumerate(arp):
            v = (0.16 if i % 2 == 0 else 0.11) * swell * rng.uniform(0.9, 1.05)
            add(piano(m, BEAT * 0.9, v), t0 + i * BEAT / 2 + rng.uniform(0, 0.012), pan=0.25)
    for (m, off, ln) in mel.get(b, []):
        add(piano(m, ln * BEAT, 0.30), t0 + off * BEAT + rng.uniform(0, 0.01), pan=0.05)

# final chord ring-out
tend = nbars * BAR - BAR
for m in [43, 55, 59, 62, 67, 71]:
    add(piano(m, 4.0, 0.22), tend + 0.02 * (m % 5))

# Reverb: decaying stereo noise impulse responses
irn = int(2.8 * SR)
ti = np.arange(irn) / SR
sos = butter(2, 5000, "low", fs=SR, output="sos")
irL = sosfilt(sos, rng.standard_normal(irn)) * np.exp(-ti * 2.3)
irR = sosfilt(sos, rng.standard_normal(irn)) * np.exp(-ti * 2.3)
irL /= np.sqrt(np.sum(irL ** 2))
irR /= np.sqrt(np.sum(irR ** 2))
wetL = fftconvolve(L, irL)[:N]
wetR = fftconvolve(R, irR)[:N]
outL = 0.72 * L + 0.45 * wetL
outR = 0.72 * R + 0.45 * wetR

# Trim to duration with gentle fade in/out
n = int(DUR * SR)
st = np.stack([outL[:n], outR[:n]], 1)
fade_in = np.minimum(1, np.arange(n) / (0.8 * SR))
fade_out = np.clip((n - np.arange(n)) / (3.5 * SR), 0, 1)
st *= (fade_in * fade_out)[:, None]
st /= np.max(np.abs(st)) / 0.89
wavfile.write(OUT, SR, (st * 32767).astype(np.int16))
print("wrote", OUT, DUR, "s")
