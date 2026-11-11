#!/usr/bin/env python3
# faster-whisper large-v3 with word times -> edit/transcript.json (+ .txt). Run after extracting work/clip1.wav (16 kHz mono).
#   python3 tools/transcribe.py [lang]   (default ms; pass "auto" for language detection)
import sys, json, wave
import numpy as np
from faster_whisper import WhisperModel
lang = sys.argv[1] if len(sys.argv) > 1 else "ms"
w = wave.open("work/clip1.wav"); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, info = m.transcribe(x, language=None if lang == "auto" else lang, word_timestamps=True, vad_filter=False, beam_size=5,
                          initial_prompt="Golf, tip, shot, swing, club, wedge, iron, bunker, rough, korang, je, la.")
res, lines = [], []
for s in segs:
    res.append({"start": s.start, "end": s.end, "text": s.text, "words": [{"w": q.word, "s": q.start, "e": q.end} for q in s.words]})
    lines.append(f"{s.start:6.2f}-{s.end:6.2f} {s.text}"); print(lines[-1], flush=True)
print("lang", info.language, info.language_probability)
suf = "" if lang == "ms" else "_" + lang
json.dump(res, open(f"edit/transcript{suf}.json", "w"), ensure_ascii=False, indent=1)
open(f"edit/transcript{suf}.txt", "w").write("\n".join(lines) + "\n")
