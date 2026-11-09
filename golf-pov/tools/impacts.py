import wave, numpy as np, sys
wf=wave.open(sys.argv[1]); sr=wf.getframerate(); n=wf.getnframes(); ch=wf.getnchannels()
a=np.frombuffer(wf.readframes(n),dtype=np.int16).astype(np.float32).reshape(-1,ch).mean(1)/32768
# high-pass via diff to emphasize clicks
d=np.abs(np.diff(a))
hop=int(sr*0.01); m=d[:len(d)//hop*hop].reshape(-1,hop).max(1)
rms=np.sqrt((a[:len(a)//hop*hop].reshape(-1,hop)**2).mean(1))
med=np.convolve(m,np.ones(200)/200,'same')+1e-6
ratio=m/med
idx=np.where((ratio>8)&(m>0.08))[0]
ev=[];last=-100
for i in idx:
    if i-last>150: ev.append(i); last=i
    elif m[i]>m[ev[-1]]: ev[-1]=i
for i in ev: print(f"{i/100:8.2f}s peak={m[i]:.3f} ratio={ratio[i]:.1f}")
