#!/usr/bin/env python3
# Cropped re-runs to pin word times: python3 tools/pin_words.py a1-b1 a2-b2 ...  (source seconds, work/clip1.wav)
import sys, wave, numpy as np
from faster_whisper import WhisperModel
w = wave.open("work/clip1.wav"); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
for r in sys.argv[1:]:
    a, b = map(float, r.split("-"))
    seg = x[int(a * 16000):int(b * 16000)] * 4.0
    for lang in ("ms", "en"):
        segs, _ = m.transcribe(np.clip(seg, -1, 1), language=lang, word_timestamps=True, vad_filter=False, beam_size=5)
        print(r, lang, " | ".join(" ".join(f"{q.word.strip()}@{a + q.start:.2f}-{a + q.end:.2f}" for q in s.words) for s in segs), flush=True)
