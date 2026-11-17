"""Original romantic waltz (nylon guitar + music box + pad, 90 BPM in 3/4) and soft paper SFX.
Generated here, so royalty-free by construction.  Usage: python3 make_audio.py OUT_DIR [DUR]"""
import numpy as np, sys
from scipy.signal import butter, sosfilt, lfilter, fftconvolve
from scipy.io import wavfile

SR = 48000
OUT = sys.argv[1]
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 48.0
rng = np.random.default_rng(9)
BEAT = 60 / 90; BAR = 3 * BEAT  # 2.0 s


def filt(x, fc, kind, o=2):
    return sosfilt(butter(o, fc, kind, fs=SR, output='sos'), x)


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def tt(s):
    return np.arange(int(SR * s)) / SR


N = int(SR * (DUR + 4)); L = np.zeros(N); R = np.zeros(N)


def add(sig, t0, g, pan=0.5):
    i = int(t0 * SR); j = min(N, i + len(sig))
    if 0 <= i < N:
        L[i:j] += sig[: j - i] * g * (1 - pan) * 1.4
        R[i:j] += sig[: j - i] * g * pan * 1.4


def guitar(m, dur=2.5, bright=0.5):
    """Karplus-Strong plucked string via a long-delay IIR."""
    f = hz(m); D = int(round(SR / f)); n = int(SR * dur)
    x = np.zeros(n); burst = filt(rng.uniform(-1, 1, D), 1500 + 3500 * bright, 'low')
    x[:D] = burst
    a = np.zeros(D + 2); a[0] = 1; a[D] = -0.4985; a[D + 1] = -0.4985
    y = lfilter([1.0], a, x)
    y = filt(y, 70, 'high')
    return y * np.minimum(1, tt(dur) / 0.003)


def musicbox(m, dur=2.2):
    t = tt(dur); f = hz(m)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.9) + 0.35 * np.sin(2 * np.pi * f * 3.0 * t) * np.exp(-t / 0.25) \
        + 0.12 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.08)
    return s * np.minimum(1, t / 0.002)


def pad(notes, dur):
    t = tt(dur + 1.5); s = np.zeros_like(t)
    for m in notes:
        for d in (-6, 6):
            f = hz(m) * 2 ** (d / 1200)
            s += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) + 0.3 * np.sin(4 * np.pi * f * t)
    env = np.minimum(1, t / 0.8) * np.where(t < dur, 1, np.exp(-(t - dur) / 0.5))
    return filt(s * env, 1800, 'low')


def bass(m, dur):
    t = tt(dur); f = hz(m)
    return (np.sin(2 * np.pi * f * t) + 0.2 * np.sin(4 * np.pi * f * t)) * np.exp(-t / 0.9) * np.minimum(1, t / 0.01)


# G | Bm | Em | C | Am | D | G | D   (8-bar loop)
PROG = [(43, [55, 59, 62]), (47, [54, 59, 62]), (40, [55, 59, 64]), (36, [55, 60, 64]),
        (45, [57, 60, 64]), (38, [54, 57, 62]), (43, [55, 59, 62]), (38, [54, 57, 62])]
# melody per bar: list of (beat offset, midi, length)
MEL = [[(0, 74, 2), (2, 71, 1)], [(0, 74, 1.5), (1.5, 76, .5), (2, 78, 1)], [(0, 79, 2), (2, 76, 1)], [(0, 76, 3)],
       [(0, 72, 1), (1, 76, 1), (2, 79, 1)], [(0, 78, 2), (2, 74, 1)], [(0, 71, 1), (1, 74, 1), (2, 79, 1)], [(0, 78, 3)]]

nbars = int(np.ceil(DUR / BAR))
OUTRO = nbars - 3
for b in range(nbars):
    t0 = b * BAR
    root, ch = PROG[b % 8]
    if b >= OUTRO:
        root, ch = PROG[0]
    # waltz guitar: bass on 1, chord pluck on 2 and 3 (arpeggiated slightly)
    add(guitar(root + 12, 2.2, 0.35), t0, 0.5, 0.45)
    if b < OUTRO + 1:
        for beat in (1, 2):
            for k, m in enumerate(ch):
                add(guitar(m, 1.6, 0.5), t0 + beat * BEAT + k * 0.018, 0.22, 0.55 + 0.05 * k)
    if b >= 1:
        add(pad([m - 12 for m in ch] + [ch[0]], BAR), t0, 0.035)
        add(bass(root, BAR * 0.95), t0, 0.16)
    if 2 <= b < OUTRO:
        for off, m, ln in MEL[b % 8]:
            add(musicbox(m + (12 if b >= 10 and b < 18 else 0), 2.2), t0 + off * BEAT, 0.13, 0.35)
# final resolve: rolled G chord + music box sparkle
tf = OUTRO * BAR
for k, m in enumerate([43, 50, 55, 59, 62, 67, 71]):
    add(guitar(m, 4.0, 0.45), tf + k * 0.06, 0.28, 0.4 + 0.05 * k)
for k, m in enumerate([79, 83, 86, 91]):
    add(musicbox(m, 2.6), tf + 0.6 + k * 0.33, 0.1, 0.3 + 0.12 * k)

# room reverb
irn = int(SR * 2.4); ti = np.arange(irn) / SR
irs = [filt(rng.standard_normal(irn), 5500, 'low') * np.exp(-ti / 0.7) for _ in range(2)]
irs = [np.concatenate([np.zeros(int(0.02 * SR)), ir / np.sqrt((ir ** 2).sum())]) for ir in irs]
L2 = 0.8 * L + 0.35 * fftconvolve(L, irs[0])[:N]; R2 = 0.8 * R + 0.35 * fftconvolve(R, irs[1])[:N]
n = int(SR * DUR); st = np.stack([L2[:n], R2[:n]], 1)
t = tt(DUR); st *= (np.clip((DUR - t) / 2.0, 0, 1) ** 1.3)[:, None]
st /= np.abs(st).max() / 0.88
wavfile.write(f"{OUT}/music_raw.wav", SR, st.astype(np.float32))

# soft paper swish (card landing) and a tiny chime (heart)
t = tt(0.5); p = t / 0.5; nz = rng.standard_normal((len(t), 2))
env = np.sin(np.pi * np.clip(p * 1.3, 0, 1)) ** 2 * np.exp(-p * 1.5)
sw = np.stack([filt(filt(nz[:, i], 900, 'high'), 5200, 'low') * env for i in range(2)], 1)
sw /= np.abs(sw).max() / 0.6
wavfile.write(f"{OUT}/sfx_paper_raw.wav", SR, sw.astype(np.float32))
ch = sum(musicbox(m, 2.0) * (0.8 ** k) for k, m in enumerate([84, 88, 91, 96]))
ch = np.stack([ch, ch], 1); ch /= np.abs(ch).max() / 0.6
wavfile.write(f"{OUT}/sfx_chime_raw.wav", SR, ch.astype(np.float32))
print("ok")
