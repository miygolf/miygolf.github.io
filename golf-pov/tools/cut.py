import sys, subprocess, os
sys.path.insert(0,'/home/user/work/edl'); from edl import EDL; from crops import CROPS
OUT='/home/user/video-claude/golf-pov/assets/clips'; os.makedirs(OUT,exist_ok=True)
SRC='/home/user/work/src/raw.mp4'; VOICE='/home/user/work/src/voice_proc.wav'
W=1080*1080//1920  # 607
W=608
def xexpr(kf, speed):
    # t in output filter is source-relative time (crop before setpts)
    kf=[(t,cx) for t,cx in kf]
    if len(kf)==1: return str(max(0,min(1920-W,kf[0][1]-W//2)))
    e=str(kf[-1][1])
    for (t0,c0),(t1,c1) in reversed(list(zip(kf,kf[1:]))):
        # smoothstep between keyframes
        u=f"(t-{t0})/{t1-t0}"; s=f"({u})*({u})*(3-2*({u}))"
        e=f"if(lt(t,{t1}),{c0}+({c1-c0})*{s},{e})"
    e=f"if(lt(t,{kf[0][0]}),{kf[0][1]},{e})"
    return f"max(0,min({1920-W},({e})-{W//2}))"
def cut(item):
    cid,a,b,o=item; sp=o.get('speed',1.0); dur=b-a
    vf=f"crop={W}:1080:'{xexpr(CROPS[cid],sp)}':0,scale=1080:1920:flags=lanczos,unsharp=5:5:0.4,setsar=1"
    if sp!=1.0: vf+=f",setpts=PTS/{sp}"
    vf+=",fps=30,format=yuv420p"
    cmd=['ffmpeg','-v','error','-y','-ss',f'{a:.3f}','-t',f'{dur:.3f}','-i',SRC]
    if not o.get('mute'):
        cmd+=['-ss',f'{a:.3f}','-t',f'{dur:.3f}','-i',VOICE,'-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','192k','-af','afade=t=in:d=0.02,areverse,afade=t=in:d=0.03,areverse']
    else:
        cmd+=['-map','0:v:0','-an']
    cmd+=['-vf',vf,'-c:v','libx264','-preset','medium','-crf','20','-g','15','-movflags','+faststart',f'{OUT}/{cid}.mp4']
    subprocess.run(cmd,check=True); return cid
from concurrent.futures import ThreadPoolExecutor
only=set(sys.argv[1:])
with ThreadPoolExecutor(2) as ex:
    for c in ex.map(cut,[i for i in EDL if not only or i[0] in only]): print('done',c,flush=True)
