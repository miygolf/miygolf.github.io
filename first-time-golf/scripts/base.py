import subprocess, json
SRC="../src/in.mov"
# (name, src_start, src_end, speed, interpolate)
SEGS=[("a1",0.0,2.4,1.0,False),
      ("a2",2.4,3.3,1.0,False),
      ("a3",3.3,3.9,0.35,True),
      ("a4",3.9,4.7,1.0,False),
      ("b1",5.25,8.2,2.0,False),
      ("b2",8.2,8.6,1.0,False),
      ("b3",8.6,10.45,1.0,False),
      ("b4",10.45,10.9,0.35,True),
      ("b5",10.9,11.85,1.0,False)]
out=[]; t=0.0
for n,s,e,sp,interp in SEGS:
    vf=f"trim={s}:{e},setpts=PTS-STARTPTS"
    if interp:
        vf+=f",minterpolate=fps=90:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,setpts=PTS/{sp},fps=30"
    else:
        vf+=f",setpts=PTS/{sp},fps=30"
    subprocess.run(["ffmpeg","-v","error","-y","-i",SRC,"-vf",vf,"-an","-c:v","libx264","-crf","12","-preset","fast","-pix_fmt","yuv420p",f"{n}.mp4"],check=True)
    d=float(subprocess.run(["ffprobe","-v","error","-count_frames","-select_streams","v","-show_entries","stream=nb_read_frames","-of","csv=p=0",f"{n}.mp4"],capture_output=True,text=True).stdout)/30
    out.append(dict(name=n,src_start=s,src_end=e,speed=sp,out_start=round(t,4),dur=round(d,4))); t+=d
open("concat.txt","w").write("".join(f"file '{o['name']}.mp4'\n" for o in out))
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","concat.txt","-c","copy","base.mp4"],check=True)
json.dump(out,open("segs.json","w"),indent=1)
for o in out: print(o)
print("total",t)
