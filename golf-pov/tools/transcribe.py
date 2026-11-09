import sys, json, time
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]
import wave, numpy as np
wf=wave.open(src); audio=np.frombuffer(wf.readframes(wf.getnframes()),dtype=np.int16).astype(np.float32)/32768.0
t=time.time()
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=4)
segs, info = m.transcribe(audio, language="ms", word_timestamps=True, vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=400), beam_size=5,
    initial_prompt="Video golf dalam Bahasa Melayu bercampur English. Golf course, driver, iron, putter, swing, fairway, green, birdie, par, bogey, hole.")
res=[]
for s in segs:
    res.append(dict(start=s.start,end=s.end,text=s.text,words=[dict(w=w.word,s=w.start,e=w.end,p=w.probability) for w in s.words]))
    print(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text}", flush=True)
json.dump(dict(lang=info.language,segments=res), open(out,"w"), ensure_ascii=False, indent=1)
print("DONE", time.time()-t, flush=True)
