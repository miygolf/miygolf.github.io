#!/usr/bin/env python3
# faster-whisper large-v3, word times, every clip, Malay pass + auto pass -> edit/transcript.json / .txt
#   python3 tools/transcribe.py      (run from the project folder after tools/fetch.sh)
import json, wave
import numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
out, lines = {}, []
for i in (1, 2, 3, 4):
    w = wave.open(f"work/clip{i}.wav"); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    for lang in ("ms", None):
        segs, info = m.transcribe(x, language=lang, word_timestamps=True, vad_filter=False, beam_size=5,
                                  initial_prompt="Golf, swing, coach, korang, je, la.")
        segs = [{"start": s.start, "end": s.end, "text": s.text, "no_speech": s.no_speech_prob,
                 "words": [{"w": q.word, "s": q.start, "e": q.end, "p": q.probability} for q in s.words]} for s in segs]
        key = f"clip{i}_{lang or 'auto'}"; out[key] = segs
        lines.append(f"[{key}] lang={info.language} p={info.language_probability:.2f}")
        lines += [f"  {s['start']:5.2f}-{s['end']:5.2f} (no_speech {s['no_speech']:.2f}) {s['text']}" for s in segs] or ["  (nothing)"]
        print(lines[-1], flush=True)
json.dump(out, open("edit/transcript.json", "w"), ensure_ascii=False, indent=1)
open("edit/transcript.txt", "w").write("\n".join(lines) + "\n")
