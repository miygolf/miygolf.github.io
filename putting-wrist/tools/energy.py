import wave, numpy as np, sys
w=wave.open(sys.argv[1]); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
sr=16000; hop=int(sr*0.05)
for rng in sys.argv[2:]:
    s,e=map(float,rng.split('-'))
    out=[]
    for t in np.arange(s,e,0.05):
        seg=a[int(t*sr):int(t*sr)+hop]; db=20*np.log10(np.sqrt((seg**2).mean())+1e-9)
        out.append(f"{t:.2f}:{int(db)}")
    print(rng, ' '.join(out)); print()
