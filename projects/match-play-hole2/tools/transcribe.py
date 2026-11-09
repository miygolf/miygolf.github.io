#!/usr/bin/env python3
"""Transcribes the six source clips with faster-whisper (large-v3, Malay + English code-switching), word timestamps.
Writes edit/transcript.json and a readable edit/transcript.txt.

Run from the project folder:  python3 tools/transcribe.py   (needs .work/a1..6.wav, 16 kHz mono)
"""
import json, os, sys, wave
import numpy as np
from faster_whisper import WhisperModel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model = WhisperModel(os.environ.get("WHISPER_MODEL", "large-v3"), device="cpu", compute_type="int8", cpu_threads=4)
out, txt = {}, []
clips = [int(c) for c in sys.argv[1:]] or [1, 2, 3, 4, 5, 6]
for i in clips:
    wav = os.path.join(ROOT, ".work", f"a{i}.wav")
    with wave.open(wav) as w:
        audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768.0
    segs, info = model.transcribe(audio, language="ms", word_timestamps=True, vad_filter=True,
                                  vad_parameters=dict(min_silence_duration_ms=300), beam_size=5,
                                  initial_prompt="Match play golf, hole 2, KRTU Subang. Iqbal, Farhan. Birdie, par, bogey, putt, driver, fairway, green.")
    rows = []
    for s in segs:
        rows.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                     "words": [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2), "p": round(w.probability, 2)} for w in (s.words or [])]})
        txt.append(f"clip{i} [{s.start:7.2f}-{s.end:7.2f}] {s.text.strip()}")
        print(txt[-1], flush=True)
    out[f"clip{i}"] = rows
os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True)
name = "transcript" if len(clips) == 6 else "transcript_" + "".join(map(str, clips))
json.dump(out, open(os.path.join(ROOT, "edit", f"{name}.json"), "w"), indent=1, ensure_ascii=False)
open(os.path.join(ROOT, "edit", f"{name}.txt"), "w").write("\n".join(txt) + "\n")
