#!/usr/bin/env python3
# faster-whisper large-v3 (Malay) with word times -> edit/transcript.json. Run tools/fetch.sh first. Cropped re-runs used to pin words: see EDIT_NOTES.md.
import sys, json
from faster_whisper import WhisperModel
import numpy as np, wave
def load(i):
    w = wave.open(f"work/clip{i}.wav"); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)/32768
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
out = {}
for i in (1,2,3):
    segs, info = m.transcribe(load(i), language="ms", word_timestamps=True, vad_filter=False, beam_size=5,
        initial_prompt="Golf, swing, driver, iron, coach, korang, je, la.")
    res = []
    for s in segs:
        res.append({"start": s.start, "end": s.end, "text": s.text, "words": [{"w": w.word, "s": w.start, "e": w.end} for w in s.words]})
        print(i, f"{s.start:6.2f}-{s.end:6.2f}", s.text, flush=True)
    out[i] = res
json.dump(out, open("edit/transcript.json","w"), ensure_ascii=False, indent=1)
