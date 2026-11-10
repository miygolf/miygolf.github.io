#!/usr/bin/env python3
"""Transcribes .work/a1.wav (16 kHz mono) with faster-whisper large-v3 (Malay, word timestamps) -> edit/transcript.json/.txt"""
import json, os, wave
import numpy as np
from faster_whisper import WhisperModel
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model = WhisperModel(os.environ.get("WHISPER_MODEL", "large-v3"), device="cpu", compute_type="int8", cpu_threads=4)
with wave.open(os.path.join(ROOT, ".work", "a1.wav")) as w:
    audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768.0
segs, info = model.transcribe(audio, language=os.environ.get("LANG_CODE", "ms"), word_timestamps=True, vad_filter=False, beam_size=5,
                              initial_prompt="Golf, chip atas green, divot, impact, wedge, bola, rumput.")
rows, txt = [], []
for s in segs:
    rows.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                 "words": [{"w": x.word.strip(), "s": round(x.start, 2), "e": round(x.end, 2), "p": round(x.probability, 2)} for x in (s.words or [])]})
    txt.append(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}")
    for x in s.words or []: txt.append(f"     {x.start:6.2f}-{x.end:6.2f} {x.word.strip()} ({x.probability:.2f})")
print("\n".join(txt))
json.dump(rows, open(os.path.join(ROOT, "edit", "transcript.json"), "w"), indent=1, ensure_ascii=False)
open(os.path.join(ROOT, "edit", "transcript.txt"), "w").write("\n".join(txt) + "\n")
