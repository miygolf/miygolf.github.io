import json, subprocess, sys, os
cuts=json.load(open(sys.argv[1])); src=sys.argv[2]; out_v=sys.argv[3]; out_a=sys.argv[4]; voice=sys.argv[5]
tmp='edit/segs'; os.makedirs(tmp,exist_ok=True)
F=0.012; lst=open(f'{tmp}/list.txt','w'); af=[]
for i,(s,e) in enumerate(cuts):
    d=e-s
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(s),'-i',src,'-t',f'{d:.3f}','-vf','fps=30,scale=1080:1920:flags=lanczos,setsar=1',
        '-an','-c:v','libx264','-preset','medium','-crf','15','-g','30','-pix_fmt','yuv420p',f'{tmp}/s{i:02d}.mp4'],check=True)
    lst.write(f"file 's{i:02d}.mp4'\n")
    af.append(f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,afade=t=in:d={F},afade=t=out:st={d-F:.3f}:d={F}[a{i}]")
lst.close()
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{tmp}/list.txt','-c','copy','-movflags','+faststart',out_v],check=True)
n=len(cuts)
fc=';'.join(af)+';'+''.join(f'[a{i}]' for i in range(n))+f'concat=n={n}:v=0:a=1[a]'
subprocess.run(['ffmpeg','-v','error','-y','-i',voice,'-filter_complex',fc,'-map','[a]','-c:a','pcm_s24le','-ar','48000',out_a],check=True)
t=0
for s,e in cuts: print(f"{s:6.2f}-{e:6.2f} -> out {t:6.2f}-{t+e-s:6.2f}"); t+=e-s
print('total',round(t,3))
