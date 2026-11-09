#!/usr/bin/env python3
"""Synthesises the ring bell (round bell, "ding ding ding") used for the match-play theme: assets/sfx/bell-3.wav and bell-1.wav.
Additive model of a struck brass bell: inharmonic partials with their own decays + beating pairs + a short hammer transient,
through a small room. Made here because the CC0 bell recordings could not be reached from the edit machine.

Run from the project folder:  python3 tools/make_bell.py
"""
import os, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
rng = np.random.default_rng(3)

# (ratio to fundamental, amplitude, decay seconds)
PARTIALS = [(1.0, 1.0, 2.6), (1.003, 0.55, 2.4), (2.41, 0.62, 1.6), (2.417, 0.3, 1.5), (3.98, 0.45, 1.0),
            (5.43, 0.32, 0.7), (6.9, 0.2, 0.45), (8.95, 0.12, 0.3), (0.5, 0.18, 1.8)]
F0 = 1180.0

def strike(dur=2.8, vel=1.0):
    t = np.arange(int(dur * SR)) / SR
    x = np.zeros_like(t)
    for r, a, d in PARTIALS:
        ph = rng.uniform(0, 2 * np.pi)
        x += a * np.exp(-t / d) * np.sin(2 * np.pi * F0 * r * t + ph)
    # hammer: 6 ms band-passed click
    n = int(0.006 * SR)
    click = rng.standard_normal(n) * np.hanning(n)
    click = np.convolve(click, np.ones(4) / 4, "same")
    x[:n] += 2.2 * click
    # soft attack (1.5 ms) so it doesn't pop
    a = int(0.0015 * SR); x[:a] *= np.linspace(0, 1, a)
    return x * vel

def room(x, mix=0.18):
    # cheap early-reflection + diffuse tail
    out = x.copy()
    for d, g in [(0.013, 0.5), (0.021, 0.4), (0.034, 0.3), (0.047, 0.25), (0.069, 0.18)]:
        i = int(d * SR); out[i:] += g * mix * x[:-i]
    n = int(1.2 * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR / 0.35)
    tail = np.convolve(x, ir)[:len(x)]
    tail /= np.max(np.abs(tail)) + 1e-9
    return out + mix * 0.6 * tail * np.max(np.abs(x))

def write(name, x):
    x = x / np.max(np.abs(x)) * 0.89
    pcm = (x * 32767).astype(np.int16)
    st = np.stack([pcm, pcm], 1)
    with wave.open(os.path.join(ROOT, "assets", "sfx", name), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())

total = np.zeros(int(3.6 * SR))
for k, (t0, v) in enumerate([(0.0, 1.0), (0.24, 0.92), (0.48, 0.96)]):
    s = strike(vel=v); i = int(t0 * SR)
    total[i:i + len(s)] += s[:len(total) - i]
write("bell-3.wav", room(total))
write("bell-1.wav", room(np.concatenate([strike(), np.zeros(int(0.4 * SR))])))
print("bell-3.wav, bell-1.wav written")
