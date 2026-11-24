#!/usr/bin/env python3
"""Word times on the FILM (assets/voice.wav), from large-v3 re-runs on each segment with 0.5 s padding (crop times are on the sound;
full-pass times on these phone recordings ran 0.3-0.5 s early). faster-whisper reports times without the leading pad, so no pad offset is subtracted. Writes edit/film_words.json: {segment: [[t0, t1, word], ...]}.
Run after build_aroll.py:  python3 tools/film_words.py"""
import json, os, subprocess
import numpy as np
from faster_whisper import WhisperModel
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tl = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
y = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, "assets", "voice.wav"), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                                 capture_output=True).stdout, np.float32)
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
pad = np.zeros(8000, np.float32); out = {}
for k, v in tl.items():
    if k.startswith("_"): continue
    seg = y[int(v["start"] * 16000):int(v["end"] * 16000)]
    segs, _ = m.transcribe(np.concatenate([pad, seg, pad]), language="ms", word_timestamps=True,
                           initial_prompt="bunker, pasir, line, grip, logo, open, weight, blast, skull, penalty, plug.")
    out[k] = [[round(v["start"] + w.start, 3), round(v["start"] + w.end, 3), w.word.strip()] for s in segs for w in s.words]
    print(k, " ".join(f"{a:.2f}:{w}" for a, b, w in out[k]))
json.dump(out, open(os.path.join(ROOT, "edit", "film_words.json"), "w"), ensure_ascii=False, indent=0)
