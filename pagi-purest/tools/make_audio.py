"""Synthesise an original upbeat 120 BPM groove and a set of SFX for the trip vlog.
All audio is generated here, so it is royalty-free by construction.
Usage: python3 make_audio.py OUT_DIR [DURATION]"""
import numpy as np, sys
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000
OUT = sys.argv[1]
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 24.0
rng = np.random.default_rng(11)
BPM = 120; B = 60 / BPM  # 0.5 s per beat
ENDT = DUR - 3.5  # end card / final stab


def filt(x, fc, kind):
    return sosfilt(butter(2, fc, kind, fs=SR, output='sos'), x)


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def tt(sec):
    return np.arange(int(SR * sec)) / SR


def reverb(x, sec=1.2, decay=0.35, wet=0.25):
    ir = filt(rng.standard_normal(int(SR * sec)), 6000, 'low') * np.exp(-tt(sec) / decay)
    ir /= np.sqrt((ir ** 2).sum())
    return x + wet * fftconvolve(x, ir)[: len(x)]


def save(name, st, peak=0.9):
    st = np.asarray(st, dtype=np.float64)
    if st.ndim == 1:
        st = np.stack([st, st], 1)
    st = st / (np.abs(st).max() + 1e-9) * peak
    wavfile.write(f"{OUT}/{name}.wav", SR, st.astype(np.float32))


# ---------------- music ----------------
N = int(SR * (DUR + 2))
L = np.zeros(N); R = np.zeros(N)
duck = np.ones(N)


def add(sig, t0, g=1.0, pan=0.5):
    i = int(t0 * SR); j = min(N, i + len(sig))
    if i >= N or j <= i:
        return
    L[i:j] += sig[: j - i] * g * (1 - pan) * 2 ** 0.5
    R[i:j] += sig[: j - i] * g * pan * 2 ** 0.5


def kick():
    t = tt(0.4); f = 45 + 95 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 0.16) + 0.25 * filt(rng.standard_normal(len(t)), 3000, 'low') * np.exp(-t / 0.004)


def clap():
    t = tt(0.3); n = rng.standard_normal(len(t))
    env = sum(np.exp(-np.clip(t - d, 0, None) / 0.01) * (t >= d) for d in (0, 0.011, 0.022)) + 0.6 * np.exp(-t / 0.07)
    return filt(filt(n, 900, 'high'), 4200, 'low') * env


def hat(open_=False):
    t = tt(0.25 if open_ else 0.06)
    return filt(rng.standard_normal(len(t)), 7500, 'high') * np.exp(-t / (0.08 if open_ else 0.015))


def pluck(notes, length=0.45):
    t = tt(length); s = np.zeros_like(t)
    for m in notes:
        for d in (-7, 7):
            f = hz(m) * 2 ** (d / 1200)
            s += 2 * ((t * f) % 1) - 1  # saw
    cutoff_env = np.exp(-t / 0.09)
    # crude moving low-pass: blend a bright and a dark version
    bright = filt(s, 4200, 'low'); dark = filt(s, 900, 'low')
    return (bright * cutoff_env + dark * (1 - cutoff_env)) * np.exp(-t / 0.22) * np.minimum(1, t / 0.004)


def bass(m, length):
    t = tt(length); f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.35 * filt(2 * ((t * f) % 1) - 1, 700, 'low')
    return s * np.minimum(1, t / 0.005) * np.exp(-t / (length * 0.9))


def marimba(m):
    t = tt(0.6); f = hz(m)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / 0.02)) * np.exp(-t / 0.18)


# C major, bright: Fmaj7 | G6 | Em7 | Am7
PROG = [dict(root=41, ch=[64, 67, 69, 72]), dict(root=43, ch=[62, 67, 71, 76]),
        dict(root=40, ch=[62, 67, 71, 74]), dict(root=45, ch=[60, 64, 67, 72])]
STAB = [0, 0.75, 1.5, 2.5, 3.25]          # syncopated chord hits within a bar (beats)
ARP = [0, 2, 1, 3, 2, 1, 3, 0]

nbars = int(np.ceil(DUR / (4 * B)))
for bar in range(nbars):
    t0 = bar * 4 * B
    c = PROG[bar % 4]
    for beat in range(4):
        tb = t0 + beat * B
        in_break = 9.2 <= tb < 11.0
        end_zone = tb >= ENDT
        if not in_break and not end_zone:
            add(kick(), tb, 0.9)
            i = int(tb * SR); dl = int(0.22 * SR)
            duck[i:i + dl] = np.minimum(duck[i:i + dl], 0.35 + 0.65 * (np.arange(dl) / dl) ** 0.6)
        if beat in (1, 3) and not end_zone:
            add(clap(), tb, 0.35, 0.48)
        if not end_zone:
            add(hat(), tb + B / 2, 0.16, 0.62)
            add(hat(beat == 3), tb + B * 0.75 if beat % 2 else tb + B / 2 + 0.001, 0.07, 0.35)
    if t0 < ENDT:
        for s in STAB:
            if t0 + s * B < DUR:
                add(pluck(c['ch']), t0 + s * B, 0.075, 0.5)
        if not (9.2 <= t0 < 11.0):
            for k in range(8):
                add(bass(c['root'] + (12 if k % 4 == 3 else 0), B / 2 * 0.9), t0 + k * B / 2 + B / 2 * (k % 2 == 0) * 0, 0.22)
        if 11.0 <= t0 < ENDT:
            for k, idx in enumerate(ARP):
                add(marimba(c['ch'][idx] + 12), t0 + k * B / 2, 0.09, 0.3 + 0.4 * (k % 2))

# riser into the buffet (9.5 -> 11.0)
rs = tt(1.5); nz = rng.standard_normal(len(rs)); prog = rs / 1.5
riser = filt(nz, 600, 'high') * (1 - prog) * 0.3 + filt(nz, 3000, 'high') * prog
add(riser * prog ** 2, 9.5, 0.22)
# final chord stab + tail at ENDT
fin = sum(pluck([m], 2.4) for m in [53, 60, 64, 67, 72, 76])
add(fin, ENDT, 0.12); add(kick(), ENDT, 1.0); add(bass(41, 1.6), ENDT, 0.3)
for k, m in enumerate([72, 76, 79, 84]):
    add(marimba(m), ENDT + 0.25 * k, 0.1, 0.3 + 0.13 * k)

L = L * duck; R = R * duck  # sidechain pump (kick sits under it, acceptable)
st = np.stack([reverb(L, wet=0.18), reverb(R, wet=0.18)], 1)
st = filt(st.T, 30, 'high').T
n = int(SR * DUR); st = st[:n]
fade = np.clip((DUR - tt(DUR)) / 1.2, 0, 1)
st *= fade[:, None]
save("music_raw", st, 0.89)

# ---------------- SFX ----------------
def whoosh(sec=0.42):
    t = tt(sec); p = t / sec; nz = rng.standard_normal((len(t), 2))
    env = np.sin(np.pi * p) ** 1.6
    out = []
    for i in range(2):
        lo = filt(filt(nz[:, i], 300, 'high'), 1500, 'low'); hi = filt(filt(nz[:, i], 1500, 'high'), 7000, 'low')
        out.append((lo * (1 - p) + hi * p) * env)
    o = np.stack(out, 1); o[:, 0] *= 1 - 0.6 * p; o[:, 1] *= 0.4 + 0.6 * p
    return o


def pop():
    t = tt(0.12); f = 320 + 700 * np.exp(-t / 0.018)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.035) + 0.15 * filt(rng.standard_normal(len(t)), 2000, 'high') * np.exp(-t / 0.003)


def shutter():
    t = tt(0.16); s = np.zeros_like(t)
    for d, g in ((0, 1.0), (0.055, 0.7)):
        m = t >= d; tc = t[m] - d
        s[m] += g * filt(rng.standard_normal(m.sum()), 1800, 'high') * np.exp(-tc / 0.006)
        s[m] += g * 0.4 * np.sin(2 * np.pi * 180 * tc) * np.exp(-tc / 0.012)
    return reverb(s, 0.3, 0.05, 0.15)


def bell(f0, sec=1.2, idx=2.2, ratio=3.5):
    t = tt(sec); mod = idx * np.exp(-t / 0.15) * np.sin(2 * np.pi * f0 * ratio * t)
    return np.sin(2 * np.pi * f0 * t + mod) * np.exp(-t / (sec / 3.2)) * np.minimum(1, t / 0.002)


def ping():
    b2 = bell(2352, 0.6); return reverb(bell(1568, 1.0) + 0.4 * np.pad(b2, (0, int(SR * 1.0) - len(b2))), 0.8, 0.2, 0.3)


def ding():
    t = tt(1.6); s = np.zeros_like(t)
    a = bell(988, 1.2, 1.2, 2.0); b = bell(784, 1.2, 1.2, 2.0)
    s[: len(a)] += a; i = int(0.38 * SR); s[i:i + len(b)] += b[: len(s) - i]
    return reverb(s, 1.0, 0.25, 0.3)


def stamp():
    t = tt(0.35); f = 55 + 80 * np.exp(-t / 0.02)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.07)
            + 0.5 * filt(rng.standard_normal(len(t)), 1200, 'low') * np.exp(-t / 0.02))


def impact():
    t = tt(1.4); f = 38 + 120 * np.exp(-t / 0.05)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35)
    s += 0.5 * filt(rng.standard_normal(len(t)), 2500, 'low') * np.exp(-t / 0.05)
    return reverb(s, 1.4, 0.4, 0.35)


def tick():
    t = tt(0.05)
    return filt(rng.standard_normal(len(t)), 3000, 'high') * np.exp(-t / 0.004) + 0.5 * np.sin(2 * np.pi * 2400 * t) * np.exp(-t / 0.008)


save("sfx_whoosh_raw", whoosh(), 0.8)
save("sfx_pop_raw", pop(), 0.8)
save("sfx_shutter_raw", shutter(), 0.8)
save("sfx_ping_raw", ping(), 0.8)
save("sfx_ding_raw", ding(), 0.8)
save("sfx_stamp_raw", stamp(), 0.85)
save("sfx_impact_raw", impact(), 0.9)
save("sfx_tick_raw", tick(), 0.6)
print("ok")
