#!/usr/bin/env python3
"""Lesson montage (Drive folder "Golf Lesson" 1r-oIAmpoBExYVC6MEixDWunlK6T5W5DA): three students, one full swing each, no speech, no names (owner).
  IMG_0352 19.11 19:29 black shirt (indoor bay), IMPACT 1.80 (sound 1.80)
  IMG_0355 19.11 21:32 blue shirt (night range), IMPACT 1.55 (sound 1.54)
  IMG_0368 20.11 09:33 grey shirt (covered range, morning), IMPACT 1.71 (sound 1.72)
Per student: full swing at 1x with its strike, 0.5x replay through impact, freeze on the finish (polaroid). Faces: heads at film y ~560-680.
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
GRADE = "null"
IMP = {"IMG_0352": 1.80, "IMG_0355": 1.55, "IMG_0368": 1.71}
SND = {"IMG_0352": 1.80, "IMG_0355": 1.54, "IMG_0368": 1.72}
ZI = {"IMG_0352": [(0, 1.25, 1100, 2250), (1, 1.3, 1100, 2250)], "IMG_0355": [(0, 1.25, 1000, 2150), (1, 1.3, 1000, 2150)],
      "IMG_0368": [(0, 1.25, 1500, 2350), (1, 1.3, 1500, 2350)]}

EDL = [
    dict(name="hook_a", sec="hook", clip="IMG_0355", a=1.35, b=1.62, speed=0.5, voice=False),
    dict(name="hook_freeze", sec="hook", clip="IMG_0355", a=1.62, kind="freeze", dur=1.0, voice=False),
]
FIN = {"IMG_0352": 2.70, "IMG_0355": 2.55, "IMG_0368": 2.65}
for i, c in enumerate(["IMG_0352", "IMG_0355", "IMG_0368"], 1):
    t = IMP[c]
    EDL += [dict(name=f"s{i}_full", sec=f"s{i}", clip=c, a=round(t - 1.25, 3), b=FIN[c], speed=1.0),
            dict(name=f"s{i}_slow", sec=f"s{i}", clip=c, a=round(t - 0.28, 3), b=round(t + 0.12, 3), speed=0.5, zoom=ZI[c], voice=False),
            dict(name=f"s{i}_fin", sec=f"s{i}", clip=c, a=FIN[c], kind="freeze", dur=1.5, voice=False)]
EDL.append(dict(name="end_freeze", sec="end", clip="IMG_0368", a=FIN["IMG_0368"], kind="freeze", dur=3.0, voice=False))

def _lerp_expr(keys):
    expr = f"{keys[-1][1]}"
    for (t0, v0), (t1, v1) in reversed(list(zip(keys[:-1], keys[1:]))):
        u = f"clip((T-{t0})/{max(t1 - t0, 1e-3)},0,1)"
        expr = f"if(lt(T,{t1}),({v0}+({v1}-{v0})*{u}*{u}*(3-2*{u})),{expr})"
    expr = f"if(lt(T,{keys[0][0]}),{keys[0][1]},{expr})"
    return expr.replace("T", f"(on/{FPS})")


def zoom_filter(zk):
    z = _lerp_expr([(k[0], k[1]) for k in zk])
    cx = _lerp_expr([(k[0], k[2]) for k in zk])
    cy = _lerp_expr([(k[0], k[3]) for k in zk])
    return (f"zoompan=z='{z}':x='clip({cx}-iw/zoom/2,0,iw-iw/zoom)':y='clip({cy}-ih/zoom/2,0,ih-ih/zoom)'"
            f":d=1:s=1080x1920:fps={FPS}")


def seg_dur(s):
    if s.get("kind") == "rev":
        return (s["b"] - s["a"]) / s["speed"]
    if s.get("kind") == "freeze":
        return s["dur"]
    return (s["b"] - s["a"]) / s["speed"]


def frames(d):
    return int(round(d * FPS))


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)); print(r.stderr[-3000:]); sys.exit(1)


def src(clip):
    return os.path.join(SRC, clip if "." in clip else f"{clip}.MOV")


def build_segment(i, s):
    if s.get("kind") == "rev": s = dict(s)
    out = os.path.join(SEG, f"{i:02d}_{s['name']}.mp4")
    n = frames(seg_dur(s))
    enc = ["-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-g", "15", out]
    zf = ("," + zoom_filter(s["zoom"]) + ",setsar=1") if s.get("zoom") else ",scale=1080:1920:flags=lanczos,setsar=1"
    if s.get("crop"):
        x, w = s["crop"]
        zf = f",crop={w}:ih:{x}:0,scale=1080:1920:flags=lanczos,setsar=1"
    if s.get("kind") == "freeze":
        vf = f"{GRADE},trim=end_frame=1,setpts=PTS-STARTPTS,fps={FPS},tpad=stop_mode=clone:stop_duration={s['dur'] + 1}{zf}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-i", src(s["clip"]), "-vf", vf]
    elif s.get("kind") == "rev":
        vf = f"{GRADE},setpts=PTS/{s['speed']},fps={FPS}{zf},reverse"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{s['b'] - s['a']:.3f}", "-i", src(s["clip"]), "-vf", vf]
    else:
        # 0.5x of 59.94 fps = every source frame once at 30 fps (no interpolation)
        vf = f"{GRADE},setpts=PTS/{s['speed']},fps={FPS}{zf}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{s['b'] - s['a'] + 0.3:.3f}", "-i", src(s["clip"]), "-vf", vf]
    run(cmd + enc)
    return out, n


def build_video():
    from concurrent.futures import ThreadPoolExecutor
    os.makedirs(SEG, exist_ok=True)
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(lambda p: build_segment(*p), list(enumerate(EDL))))
    for (p, n), s in zip(res, EDL):
        print(f"  seg {os.path.basename(p):<22} {n} frames")
    with open(os.path.join(SEG, "list.txt"), "w") as f:
        for p, _ in res:
            f.write(f"file '{p}'\n")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(SEG, "list.txt"), "-c", "copy",
         os.path.join(ROOT, "assets", "aroll.mp4")])


def timeline():
    t = 0.0; out = {}
    for s in EDL:
        d = frames(seg_dur(s)) / FPS
        out[s["name"]] = {"start": round(t, 4), "end": round(t + d, 4)}
        t += d
    out["_total"] = round(t, 4)
    return out


def film_time(tl, name, src_t):
    s = next(x for x in EDL if x["name"] == name)
    return tl[name]["start"] + (src_t - s["a"]) / s["speed"]


# ---------------- audio ----------------
_cache = {}
def load(clip):
    if clip not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src(clip), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                             capture_output=True).stdout
        _cache[clip] = np.frombuffer(raw, np.float32).copy()
    return _cache[clip]


def piece(clip, a, b, fade=0.03):
    x = load(clip)[int(a * SR):int(b * SR)].copy()
    f = int(fade * SR)
    if f and len(x) > 2 * f:
        x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    return x


def db(g):
    return 10 ** (g / 20)


def seg_gain(clip, a, b):
    x = load(clip)[int(a * SR):int(b * SR)]
    h = SR // 10
    r = np.array([np.sqrt(np.mean(x[i:i + h] ** 2)) + 1e-9 for i in range(0, len(x) - h, h)])
    return float(np.clip(-24 - 20 * np.log10(np.percentile(r, 90)), -10, 12))


def build_audio(tl):
    total = tl["_total"]
    buf = np.zeros(int((total + 0.5) * SR), np.float32)
    placed = []
    def place(x, t, gain_db=0.0, src=None):
        i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * db(gain_db)
        if src: placed.append([src[0], round(src[1], 3), round(src[2], 3), round(t, 4)])
    T = lambda n: tl[n]["start"]
    hit = lambda c: piece(c, SND[c] - 0.03, SND[c] + 0.35, 0.004)
    for s in EDL:
        if s.get("kind") == "freeze" or not s.get("voice", True):
            continue
        place(piece(s["clip"], s["a"], s["b"], 0.03), T(s["name"]), seg_gain(s["clip"], s["a"], s["b"]), (s["clip"], s["a"], s["b"]))
    for n in [s["name"] for s in EDL if s["name"].endswith("_slow") or s["name"] == "hook_a"]:
        c = next(x["clip"] for x in EDL if x["name"] == n)
        place(hit(c), film_time(tl, n, IMP[c]) + 1 / FPS - 0.03, seg_gain(c, IMP[c] - 1.2, IMP[c] + 0.9) - 2)
    tl["_voice"] = placed
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    out = os.path.join(ROOT, "edit", "voice_raw.wav")
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    # clean like the Kinrara casual cut: no speech, so cut the range noise and gate between strikes
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af",
         "highpass=f=180,lowpass=f=9000,afftdn=nr=30:nf=-28:tn=1,afftdn=nr=20:nf=-35,"
         "agate=threshold=0.06:ratio=8:attack=1:release=180:range=0.03,loudnorm=I=-18:TP=-2:LRA=15",
         "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])


if __name__ == "__main__":
    tl = timeline()
    b = {"hook_impact": round(film_time(tl, "hook_a", IMP["IMG_0355"]), 3)}
    for i, c in enumerate(["IMG_0352", "IMG_0355", "IMG_0368"], 1):
        b[f"s{i}_impact"] = round(film_time(tl, f"s{i}_full", IMP[c]), 3)
        b[f"s{i}_slowimp"] = round(film_time(tl, f"s{i}_slow", IMP[c]), 3)
    tl["_beats"] = b
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True); os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print("total", tl["_total"]); print(b)
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
