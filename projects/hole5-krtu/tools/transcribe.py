#!/usr/bin/env python3
"""Transcribes .work/a1..4.wav (16 kHz mono) with faster-whisper large-v3 (Malay, word timestamps) -> edit/transcript.json/.txt"""
import json, os, sys, wave
import numpy as np
from faster_whisper import WhisperModel
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model = WhisperModel(os.environ.get("WHISPER_MODEL", "large-v3"), device="cpu", compute_type="int8", cpu_threads=4)
out, txt = {}, []
for i in [1, 2, 3, 4]:
    with wave.open(os.path.join(ROOT, ".work", f"a{i}.wav")) as w:
        audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768.0
    segs, info = model.transcribe(audio, language="ms", word_timestamps=True, vad_filter=True,
                                  vad_parameters=dict(min_silence_duration_ms=300), beam_size=5,
                                  initial_prompt="Golf, swing, driver, iron, wedge, chip, putt, green, fairway, impact, divot.")
    rows = []
    for s in segs:
        rows.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                     "words": [{"w": x.word.strip(), "s": round(x.start, 2), "e": round(x.end, 2), "p": round(x.probability, 2)} for x in (s.words or [])]})
        txt.append(f"clip{i} [{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}")
        print(txt[-1], flush=True)
    out[f"clip{i}"] = rows
json.dump(out, open(os.path.join(ROOT, "edit", "transcript.json"), "w"), indent=1, ensure_ascii=False)
open(os.path.join(ROOT, "edit", "transcript.txt"), "w").write("\n".join(txt) + "\n")
