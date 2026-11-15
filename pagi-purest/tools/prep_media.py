"""Prepare footage: cover-crop photos to 9:16 and cut/stabilise/speed-ramp video segments."""
import subprocess, sys, os, json
from PIL import Image, ImageOps
RAW, OUT = sys.argv[1], sys.argv[2]
PHOTOS = ["IMG_0265", "IMG_0266", "IMG_0264", "IMG_0261", "IMG_0263", "IMG_0260", "IMG_0262"]
for p in PHOTOS:
    im = ImageOps.exif_transpose(Image.open(f"{RAW}/{p}.JPG")).convert("RGB")
    W, H = 1260, 2240  # 9:16 with headroom for punch zooms
    s = max(W / im.width, H / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (im.width - W) // 2, (im.height - H) // 2
    im.crop((l, t, l + W, t + H)).save(f"{OUT}/images/{p}.jpg", quality=90)
# id, src, in, out, speed, blend
SEGS = [("v_window", "VID_20261115_075253.mp4", 0.0, 2.2, 1.0, 1),
        ("v_corridor", "VID_20261115_075253.mp4", 2.2, 21.4, 4.8, 5),
        ("v_lift", "VID_20261115_075253.mp4", 21.4, 23.6, 1.0, 1),
        ("v_exterior", "IMG_0236.MOV", 0.0, 2.0, 0.8, 1)]
meta = {}
for sid, src, a, b, sp, blend in SEGS:
    out = f"{OUT}/clips/{sid}.mp4"; trf = f"{OUT}/clips/{sid}.trf"; base = "scale=1080:1920:flags=lanczos"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(a),"-t",str(b-a),"-i",f"{RAW}/{src}","-an","-vf",
                    f"{base},vidstabdetect=shakiness=7:result={trf}","-f","null","-"],check=True)
    mix = f",tmix=frames={blend}" if blend > 1 else ""
    vf = f"{base},vidstabtransform=input={trf}:smoothing=20:zoom=5,unsharp=5:5:0.5{mix},setpts=PTS/{sp},fps=30,format=yuv420p"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(a),"-t",str(b-a),"-i",f"{RAW}/{src}","-an","-vf",vf,
                    "-c:v","libx264","-preset","slow","-crf","17","-g","10","-movflags","+faststart",out],check=True)
    os.remove(trf)
    d = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",out]))
    meta[sid] = round(d, 3); print(sid, meta[sid], flush=True)
json.dump(meta, open(f"{OUT}/clips/segments.json", "w"), indent=1)
