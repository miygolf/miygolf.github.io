import sys, json
from faster_whisper import WhisperModel
m = WhisperModel(__import__("os").environ.get("WM","small"), device="cpu", compute_type="int8")
from faster_whisper.audio import decode_audio
import numpy as np, wave
def load(p):
    w=wave.open(p); return np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
for f in sys.argv[1:]:
    for lang in ["ms", None]:
        segs, info = m.transcribe(load(f), language=lang, word_timestamps=True, vad_filter=False, beam_size=5)
        print(f"== {f} lang={lang or info.language}")
        for s in segs:
            print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}")
            print("   ", " ".join(f"{w.word.strip()}@{w.start:.2f}-{w.end:.2f}" for w in s.words))
