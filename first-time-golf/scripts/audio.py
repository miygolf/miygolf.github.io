import subprocess, json, numpy as np, wave
SR=48000
segs=json.load(open("segs.json"))
BASE=segs[-1]["out_start"]+segs[-1]["dur"]; TOTAL=BASE+2.7
IA, IB, CUT, H0, H1 = 3.87, 9.98, 5.8, 7.6667, 9.5333
raw=subprocess.run(["ffmpeg","-v","error","-i","../src/in.mov","-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout
src=np.frombuffer(raw,np.float32).reshape(-1,2).copy()
N=int(TOTAL*SR)+SR; out=np.zeros((N,2),np.float32)
def S(t): return int(round(t*SR))
def add(x,t,g=1.0):
    i=S(t); x=np.atleast_2d(x.T).T if x.ndim==1 else x
    if x.ndim==1 or x.shape[1]==1: x=np.repeat(x.reshape(-1,1),2,1)
    n=min(len(x),N-i); out[i:i+n]+=g*x[:n]
def fade(x,fi=0.01,fo=0.01):
    x=x.copy(); a=int(fi*SR); b=int(fo*SR)
    if a: x[:a]*=np.linspace(0,1,a)[:,None]
    if b: x[-b:]*=np.linspace(1,0,b)[:,None]
    return x
def clip(a,b): return src[S(a):S(b)]
quiet=np.concatenate([clip(5.5,6.4),clip(6.7,9.0)])   # ambient without hits
# ambient bed following the edit
for s in segs:
    a,b,sp,o,d=s["src_start"],s["src_end"],s["speed"],s["out_start"],s["dur"]
    if sp==1.0:
        x=clip(a,b)
        if s["name"]=="a1": x=x.copy(); x[S(1.05):S(1.4)]*=0.25   # tame stray noise
    elif sp>1:
        x=clip(a,b)[::int(sp)]
    else:
        x=quiet[:S(d)]
    add(fade(x,0.02,0.02),o,0.9)
add(fade(quiet[:S(TOTAL-BASE)],0.02,1.2),BASE,0.6)
# real impact clicks, placed at the slow-mo impact moments
add(fade(clip(3.44,3.80),0.003,0.12),IA-0.06,3.2)
add(fade(clip(10.56,10.95),0.003,0.12),IB-0.04,1.3)
# synthesized SFX
t=lambda d: np.arange(int(d*SR))/SR
def boom(d=0.6,f0=95,f1=38):
    tt=t(d); ph=2*np.pi*np.cumsum(np.linspace(f0,f1,len(tt)))/SR
    return np.sin(ph)*np.exp(-tt*7)
def whoosh(d=0.55):
    rng=np.random.default_rng(1); n=rng.standard_normal(int(d*SR))
    # sweep a one-pole lowpass upward
    tt=t(d); fc=300+5500*(tt/d)**2; y=np.zeros_like(n); s=0
    for i in range(len(n)):
        a=1-np.exp(-2*np.pi*fc[i]/SR); s+=a*(n[i]-s); y[i]=s
    env=(tt/d)**2.2*np.exp(-np.maximum(0,tt-d*0.9)*40)
    return y*env*0.9
def blip(f=880,d=0.07):
    tt=t(d); return np.sin(2*np.pi*f*tt)*np.exp(-tt*45)
def tick(): return blip(2200,0.025)*0.5
W=whoosh()
add(W,IA-len(W)/SR,0.55); add(boom(),IA,0.7)
add(W,IB-len(W)/SR,0.7); add(boom(0.8,110,34),IB,0.9)
add(W[::-1]*0.8,CUT-0.25,0.5); add(boom(0.35,140,60),CUT,0.35)   # transition whoosh
for tp,f in [(0.12,660),(0.55,990),(2.85,780),(CUT,780),(5.02,880),(10.9,1040),(BASE+0.25,660),(BASE+0.9,990)]:
    add(blip(f),tp,0.25)
# loading ticks speeding up, then a 'done' chime
k=0; tp=H0+0.1
while tp<H1-0.05:
    add(tick(),tp,0.35); k+=1; tp+=max(0.09,0.32-0.025*k)
ch=np.concatenate([blip(1320,0.09),blip(1760,0.18)])
add(ch,H1-0.05,0.3)
out=out[:S(TOTAL)]
fo=S(0.3); out[-fo:]*=np.linspace(1,0,fo)[:,None]
out=np.clip(out,-1,1)
with wave.open("audio.wav","wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out*32767).astype(np.int16).tobytes())
print("audio",len(out)/SR)
