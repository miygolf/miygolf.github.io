#!/usr/bin/env python3
"""Builds the voice-over track for MIY GOLF Ep1 "Break 100" from the owner's recording (.src/vo.wav, 69.9 s).

Re-ordered for the hook, repeats removed, pauses tightened:
  - opens on "30 minit je. 3 drill. Tak payah swing cantik." (strongest line), THEN "Episod 1, Break 100."
  - the second "Kalau kau ada 30 minit je," (repeat of the hook) is dropped: the line starts at "dekat range minggu ni"
  - every silence inside a piece longer than 0.30 s is collapsed to 0.14 s; 0.22 s between pieces
Word times: faster-whisper large-v3 (ms, domain prompt) + crop re-runs, edit/vo_words.json.
Writes assets/voice.wav (denoised, compressed, -16 LUFS) and edit/voice_map.json (piece -> film time, word map for captions).
Run from the project folder: python3 tools/build_voice.py
"""
import json, os, subprocess, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
GAP = 0.22

# (key, src_start, src_end, text) - src times in the recording
PIECES = [
    ("hook1", 2.18, 3.32, "30 minit je."),
    ("hook2", 3.80, 6.32, "3 drill. Tak payah swing cantik."),
    ("ep", 0.00, 1.95, "Episod 1, Break 100."),
    ("intro", 9.14, 11.64, "Dekat range minggu ni, kau buat 3 benda ni."),
    ("d1a", 11.88, 15.50, "Satu, pilih 2 sasaran untuk fairway."),
    ("d1b", 15.80, 17.88, "Pukul 10 bola dengan driver."),
    ("d1c", 18.56, 20.72, "Kira berapa banyak yang masuk."),
    ("d1d", 20.88, 24.96, "Kalau bawah 6, kau cuba dengan hybrid atau 3 wood."),
    ("d1e", 25.42, 30.78, "Mana lagi banyak masuk, to consider kayu untuk kau tee off."),
    ("d2a", 30.80, 38.12, "Yang kedua, ambil 7 iron, pukul bola rendah atau punch, 20 ke 30 meter."),
    ("d2b", 38.08, 40.54, "Ini pukulan masa kau belakang pokok."),
    ("d2c", 41.48, 47.82, "Aku jarang nampak orang buat latihan ni dekat range, sebab tu lubang tu masuk lapan."),
    ("d3a", 48.30, 50.52, "Yang ketiga, lag jauh."),
    ("d3b", 50.50, 57.66, "Objektif cuma untuk berhenti dalam panjang putter dari lubang, bukan masuk."),
    ("cta", 58.68, 67.98, "Pergi range minggu ni, buat drill tee off tu, lepas tu bagitahu aku berapa yang masuk dari 10."),
]


def load():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, ".src", "vo.wav"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def tighten(x, a0):
    """Collapse silent runs (>0.30 s under -50 dBFS, 20 ms frames) to 0.14 s. Returns audio + a src->local time map [(src, local)]."""
    h = int(0.02 * SR)
    n = len(x) // h
    rms = np.array([np.sqrt(np.mean(x[i * h:(i + 1) * h] ** 2)) + 1e-9 for i in range(n)])
    quiet = 20 * np.log10(rms) < -50
    keep = np.ones(n, bool)
    i = 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            if (j - i) * 0.02 > 0.30 and i > 0 and j < n:
                k = int(0.14 / 0.02)
                keep[i + k // 2:j - (k - k // 2)] = False
            i = j
        else:
            i += 1
    out, tmap, local = [], [], 0.0
    for i in range(n):
        if keep[i]:
            seg = x[i * h:(i + 1) * h].copy()
            if out and not keep[i - 1]:              # tiny crossfade at a removed gap
                f = min(len(seg), int(0.004 * SR)); seg[:f] *= np.linspace(0, 1, f)
            out.append(seg); tmap.append((a0 + i * 0.02, local)); local += 0.02
    return np.concatenate(out), tmap


def main():
    x = load()
    buf, pieces, t = [], [], 0.25
    buf.append(np.zeros(int(0.25 * SR), np.float32))
    for key, a, b, text in PIECES:
        seg, tmap = tighten(x[int(a * SR):int(b * SR)], a)
        f = int(0.012 * SR); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        pieces.append({"key": key, "src": [a, b], "start": round(t, 3), "end": round(t + len(seg) / SR, 3), "text": text,
                       "map": [[round(s, 2), round(t + l, 3)] for s, l in tmap[::5]]})
        buf.append(seg); t += len(seg) / SR
        buf.append(np.zeros(int(GAP * SR), np.float32)); t += GAP
    y = np.concatenate(buf)
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True)
    raw = os.path.join(ROOT, "edit", "voice_raw.wav")
    with wave.open(raw, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
                    "highpass=f=80,afftdn=nf=-45:nr=8,equalizer=f=3000:t=q:w=1.2:g=2,acompressor=threshold=-22dB:ratio=3:attack=5:release=120:makeup=3,"
                    "loudnorm=I=-16:TP=-2:LRA=8", "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")], check=True)
    total = round(t + 0.1, 3)
    json.dump({"total_voice": total, "pieces": pieces}, open(os.path.join(ROOT, "edit", "voice_map.json"), "w"), indent=1)
    print("voice", total, "s")
    for p in pieces: print(f"  {p['start']:6.2f}-{p['end']:6.2f} {p['key']:6} {p['text']}")


if __name__ == "__main__":
    main()
