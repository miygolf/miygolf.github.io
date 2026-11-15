"""Mix the SFX cue sheet from index.html into one track (no music) and mux it onto a rendered video.
Usage: python3 tools/mix_sfx_only.py IN_VIDEO OUT_VIDEO"""
import re, subprocess, sys
h = open("index.html").read()
tags = re.findall(r'<audio[^>]*id="(sfx\d+)" src="([^"]+)" data-start="([\d.]+)" data-duration="([\d.]+)" data-volume="([\d.]+)"', h)
dur = float(re.search(r'data-composition-id="main" data-start="0" data-duration="([\d.]+)"', h).group(1))
args = ["ffmpeg", "-v", "error", "-y", "-i", sys.argv[1], "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo"]
fl = []
for k, (_, src, st, du, vol) in enumerate(tags, 2):
    args += ["-i", src]; ms = int(round(float(st) * 1000))
    fl.append(f"[{k}:a]atrim=0:{du},aformat=sample_rates=48000:channel_layouts=stereo,volume={vol},adelay={ms}|{ms}[a{k}]")
fl.append("[1:a]" + "".join(f"[a{k}]" for k in range(2, len(tags) + 2)) +
          f"amix=inputs={len(tags) + 1}:normalize=0:duration=first,volume=1.0,alimiter=limit=0.6[out]")
args += ["-filter_complex", ";".join(fl), "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
         "-movflags", "+faststart", sys.argv[2]]
subprocess.run(args, check=True); print(len(tags), "sfx mixed")
