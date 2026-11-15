"""Cut, stabilise and slow selected segments from the raw 4K footage into 1080x1920 clips."""
import json, subprocess, sys, os
RAW, OUT = sys.argv[1], sys.argv[2]
FPS = 30
# id, source, in, out, speed
SEGS = [
  ("s01_reveal",   "IMG_0259", 4.6, 7.4, 1.0),
  ("s03_corridor", "IMG_0238", 3.8, 7.0, 0.7),
  ("s04_bed",      "IMG_0258", 0.2, 3.2, 0.7),
  ("s05_room",     "IMG_0258", 5.8, 8.6, 0.7),
  ("s06_marble",   "IMG_0242", 2.0, 4.6, 0.7),
  ("s07_shower",   "IMG_0259", 10.1, 12.3, 1.0),
  ("s08_vanity",   "IMG_0259", 18.6, 20.7, 1.0),
  ("s09_amenity",  "IMG_0243", 0.2, 2.8, 1.0),
  ("s10_coffee",   "IMG_0241", 8.6, 11.4, 1.0),
  ("s11_card",     "IMG_0244", 0.6, 3.4, 0.75),
  ("s12_wide",     "IMG_0258", 16.4, 19.8, 0.7),
]
meta = {}
for sid, src, a, b, sp in SEGS:
    inp = os.path.join(RAW, src + ".MOV"); out = os.path.join(OUT, sid + ".mp4")
    trf = os.path.join(OUT, sid + ".trf")
    base = f"scale=1080:1920:flags=lanczos"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(a),"-t",str(b-a),"-i",inp,"-an","-vf",
        f"{base},vidstabdetect=shakiness=6:accuracy=12:result={trf}","-f","null","-"],check=True)
    vf = (f"{base},vidstabtransform=input={trf}:smoothing=24:zoom=4:optzoom=0:interpol=bicubic,unsharp=5:5:0.4,"
          f"setpts=PTS/{sp},fps={FPS},format=yuv420p")
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(a),"-t",str(b-a),"-i",inp,"-an","-vf",vf,
        "-c:v","libx264","-preset","slow","-crf","16","-g","15","-movflags","+faststart",out],check=True)
    os.remove(trf)
    d = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",out]))
    meta[sid] = {"src": src, "in": a, "out": b, "speed": sp, "duration": round(d, 3)}
    print(sid, meta[sid], flush=True)
json.dump(meta, open(os.path.join(OUT, "segments.json"), "w"), indent=1)
