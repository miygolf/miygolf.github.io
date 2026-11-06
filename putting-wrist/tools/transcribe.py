import sys, json
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[3] if len(sys.argv)>3 else "large-v3", device="cpu", compute_type="int8", cpu_threads=4)
import wave, numpy as np
_w=wave.open(sys.argv[1]); audio=np.frombuffer(_w.readframes(_w.getnframes()),dtype=np.int16).astype(np.float32)/32768.0
segs, info = m.transcribe(audio, language="ms", word_timestamps=True, vad_filter=False, beam_size=5,
    initial_prompt="Video golf tentang putting untuk golfer baru. Putter, bola, green, alignment stick, stroke, grip, line, pace.")
out=[]
for s in segs:
    d={"start":s.start,"end":s.end,"text":s.text.strip(),"words":[{"w":w.word,"s":w.start,"e":w.end,"p":w.probability} for w in s.words]}
    out.append(d); print(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text.strip()}", flush=True)
json.dump(out, open(sys.argv[2],"w"), ensure_ascii=False, indent=1)
