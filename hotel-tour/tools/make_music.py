"""Synthesise an original, calm instrumental bed (felt piano + warm pad) and a soft air-swell SFX.
Everything is generated here, so the music is royalty-free by construction."""
import numpy as np, sys
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR = 48000; OUT = sys.argv[1]; DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 40.0
rng = np.random.default_rng(7)
BPM = 66; BEAT = 60 / BPM; BAR = 4 * BEAT
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def lp(x, fc, o=2): return sosfilt(butter(o, fc, 'low', fs=SR, output='sos'), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x)
N = int(SR * (DUR + 4)); L = np.zeros(N); R = np.zeros(N)
# D major: Dmaj9 | Bm9 | Gmaj9 | A6sus(add9)
CHORDS = [
  dict(root=38, pad=[50, 54, 57, 61, 64], arp=[62, 66, 69, 73, 76, 73, 69, 66]),
  dict(root=35, pad=[47, 50, 54, 57, 61], arp=[59, 62, 66, 69, 73, 69, 66, 62]),
  dict(root=31, pad=[47, 50, 54, 55, 57], arp=[59, 62, 66, 67, 71, 67, 66, 62]),
  dict(root=33, pad=[45, 50, 52, 54, 57], arp=[57, 62, 64, 66, 69, 66, 64, 62]),
]
def add(buf, sig, t0, gain=1.0):
    i = int(t0 * SR); j = min(N, i + len(sig)); buf[i:j] += sig[: j - i] * gain
def pad_voice(m, dur):
    t = np.arange(int(SR * (dur + 2.5))) / SR; f = hz(m); s = np.zeros_like(t)
    for det in (-5, 0, 5):
        ff = f * 2 ** (det / 1200)
        for n in range(1, 7): s += np.sin(2 * np.pi * ff * n * t + rng.uniform(0, 6.28)) / n ** 1.8
    env = np.minimum(1, t / 1.6) * np.where(t < dur, 1, np.exp(-(t - dur) / 0.9))
    trem = 1 + 0.06 * np.sin(2 * np.pi * 0.23 * t + rng.uniform(0, 6))
    return lp(s * env * trem, 1600)
def piano(m, vel, length=4.0):
    t = np.arange(int(SR * length)) / SR; f = hz(m); s = np.zeros_like(t); B = 0.0004
    for n in range(1, 9):
        fn = f * n * np.sqrt(1 + B * n * n)
        s += np.sin(2 * np.pi * fn * t) * (vel ** (0.5 + n * 0.15)) / n ** 1.3 * np.exp(-t * (0.9 + n * 0.55))
    s *= np.minimum(1, t / 0.006)
    hammer = lp(rng.standard_normal(len(t)) * np.exp(-t / 0.004), 2500) * 0.05
    return lp(s + hammer, 2600 + 2000 * vel) * vel
bar = 0; t = 0.0
while t < DUR:
    c = CHORDS[bar % 4]
    for m in c['pad']:
        v = pad_voice(m, BAR + 0.4); pan = (m % 7) / 7
        add(L, v, t, 0.055 * (1 - 0.4 * pan)); add(R, v, t, 0.055 * (0.6 + 0.4 * pan))
    sub = np.arange(int(SR * (BAR + 1.5))) / SR
    sv = np.sin(2 * np.pi * hz(c['root']) * sub) * np.minimum(1, sub / 0.8) * np.where(sub < BAR, 1, np.exp(-(sub - BAR) / 0.4))
    add(L, sv, t, 0.10); add(R, sv, t, 0.10)
    if t >= 2.2:  # piano enters with the title card
        for k, m in enumerate(c['arp']):
            tt = t + k * BEAT / 2 + rng.normal(0, 0.012)
            vel = 0.42 + 0.18 * (k % 4 == 0) + rng.uniform(-0.06, 0.06)
            if bar % 2 == 1 and k in (3, 7): continue  # breathe
            p = piano(m, vel); pan = 0.5 + 0.35 * np.sin(m)
            add(L, p, tt, 0.16 * (1.2 - pan)); add(R, p, tt, 0.16 * (0.2 + pan))
        if bar % 2 == 0:  # occasional high melody tone
            mel = piano(c['arp'][4] + 12, 0.33, 5.0); add(L, mel, t + BEAT * 2.5, 0.10); add(R, mel, t + BEAT * 2.5, 0.12)
    bar += 1; t += BAR
# final chord resolve
for m in [50, 54, 57, 61, 64, 69]:
    p = piano(m, 0.38, 6.0); add(L, p, DUR - 3.4, 0.13); add(R, p, DUR - 3.4, 0.13)
# reverb: stereo decaying-noise IR
irn = int(SR * 3.2); ti = np.arange(irn) / SR
irL = lp(rng.standard_normal(irn), 5000) * np.exp(-ti / 0.85); irR = lp(rng.standard_normal(irn), 5000) * np.exp(-ti / 0.85)
pre = int(0.025 * SR); irL = np.concatenate([np.zeros(pre), irL]); irR = np.concatenate([np.zeros(pre), irR])
irL /= np.sqrt((irL ** 2).sum()); irR /= np.sqrt((irR ** 2).sum())
wL = fftconvolve(L, irL)[:N]; wR = fftconvolve(R, irR)[:N]
L = hp(0.72 * L + 0.42 * wL, 35); R = hp(0.72 * R + 0.42 * wR, 35)
n = int(SR * DUR); L, R = L[:n], R[:n]
tt = np.arange(n) / SR; fade = np.clip((DUR - tt) / 3.0, 0, 1) ** 1.5 * np.clip(tt / 0.8, 0, 1)
st = np.stack([L * fade, R * fade], 1); st /= np.abs(st).max() / 0.85
wavfile.write(OUT + '/music_raw.wav', SR, st.astype(np.float32))
# soft air swell SFX (2.2 s): band-passed noise that rises and settles
m = int(SR * 2.2); ts = np.arange(m) / SR
nz = rng.standard_normal((m, 2)); env = np.sin(np.pi * np.clip(ts / 2.2, 0, 1)) ** 2.5
bright = np.sin(np.pi * ts / 2.2)
sw = np.stack([lp(hp(nz[:, i], 500), 1800) * (1 - bright) + lp(hp(nz[:, i], 700), 4800) * bright for i in range(2)], 1) * env[:, None]
sw /= np.abs(sw).max() / 0.7
wavfile.write(OUT + '/sfx_air_raw.wav', SR, sw.astype(np.float32))
print('ok')
