#!/usr/bin/env python3
"""Bola plug / fried egg (the follow-up to projects/bunker-skrip, for the people who comment "BUNKER"): cuts the owner's iPhone clips
(1920x1080 HEVC 59.94 fps, rotated -90 -> upright 1080x1920) into one 30 fps A-roll (assets/aroll.mp4) and the sound track (assets/voice.wav)
from the clips' own audio. Owner: "kau ambil footage tu (egg fry), kau blend in dengan apa yang ada sekarang ... kalau orang komen bunker,
aku nak upload video tu".

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]

Clip map (crop transcripts, large-v3, on the sound; energy segments; picture on contact sheets):
  IMG_0418  17.12-18.20 "Macam mana nak pukul bola plug?" (the question that ends the bunker video: the hook, talking head, face low in frame)
  egg_fry   4.6-6.4 close-up: the plugged yellow ball, club hovering (no usable speech: he is directing the phone)
            9.86-10.52 "Ini normal."  11.44-12.76 "Kalau korang buat macam ni, bola tak keluar."  13.84-14.10 "Contoh,"
            15.09 impact, open face: the sand explodes, the ball stays   16.58-17.24 "so bola kat situ je."
            20.76-21.10 "Tip dia."  25.56-27.04 "Instead of club face terbuka,"  28.52-29.58 "korang tutupkan dia macam ni,"
            30.78-31.36 "biar je macam ni,"  32.08-32.44 "ni pukul."  34.05 impact, closed face, the ball comes out
            35.6-39.8 the phone pans to the green   41.00-42.34 "Okey, itu dia. Siap." (face close, walking towards the phone)
  Not used: egg_fry 0-8.5 (behind the scenes: "nak slow-mo ke tak payah? ... fokus kat kayu").
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
C = {"egg": "egg_fry.MOV", "s18": "IMG_0418.MOV"}

# own = the segment's own sound plays; vo = extra (clip, a, b, offset-in-segment); mute = picture only
EDL = [
    dict(name="q", clip="s18", a=17.05, b=18.30, own=True),                     # hook: "Macam mana nak pukul bola plug?"
    dict(name="plug", clip="egg", a=4.60, b=6.40, own=False),                   # the plugged ball, close
    dict(name="normal", clip="egg", a=9.80, b=10.62, own=True),                 # "Ini normal."
    dict(name="normal2", clip="egg", a=11.38, b=12.90, own=True),               # "Kalau korang buat macam ni, bola tak keluar."
    dict(name="fail", clip="egg", a=13.76, b=17.40, own=True),                  # "Contoh," open-face strike 15.09, "so bola kat situ je."
    dict(name="tip", clip="egg", a=20.68, b=21.24, own=True),                   # "Tip dia."
    dict(name="face", clip="egg", a=25.46, b=27.14, own=True),                  # "Instead of club face terbuka,"
    dict(name="face2", clip="egg", a=28.44, b=29.70, own=True),                 # "korang tutupkan dia macam ni,"
    dict(name="biar", clip="egg", a=30.70, b=32.58, own=True),                  # "biar je macam ni, ni pukul."
    dict(name="hit", clip="egg", a=32.58, b=35.00, own=True),                   # closed-face strike 34.05
    dict(name="slow", clip="egg", a=33.70, b=34.55, speed=0.5, own=False, vo=[("egg", 33.99, 34.40, None)]),   # replay 0.5x, real strike on it
    dict(name="pan", clip="egg", a=35.00, b=39.80, own=True),                   # the ball out, the phone pans to the green
    dict(name="end", clip="egg", a=40.92, b=42.70, own=True),                   # "Okey, itu dia. Siap."
    dict(name="hold", clip="egg", a=42.66, kind="freeze", dur=1.3),
]
IMPACTS = {"fail": 15.09, "hit": 34.05, "slow": 34.05}
STRIKE = 34.05          # egg_fry closed-face strike transient, laid on the slowed replay


def seg_dur(s):
    return s["dur"] if s.get("kind") == "freeze" else (s["b"] - s["a"]) / s.get("speed", 1.0)


def frames(d):
    return int(round(d * FPS))


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)); print(r.stderr[-3000:]); sys.exit(1)


def src(c):
    return os.path.join(SRC, C[c])


def build_segment(i, s):
    out = os.path.join(SEG, f"{i:02d}_{s['name']}.mp4")
    n = frames(seg_dur(s))
    enc = ["-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-g", "15", out]
    sc = "scale=1080:1920:flags=lanczos,setsar=1"
    if s.get("kind") == "freeze":
        vf = f"trim=end_frame=1,setpts=PTS-STARTPTS,fps={FPS},tpad=stop_mode=clone:stop_duration={s['dur'] + 1},{sc}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-i", src(s["clip"]), "-vf", vf]
    else:
        sp = s.get("speed", 1.0)       # 0.5x of 59.94 fps = every source frame once at 30 fps (no interpolation)
        vf = f"setpts=PTS/{sp},fps={FPS},{sc}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{s['b'] - s['a'] + 0.3:.3f}", "-i", src(s["clip"]), "-vf", vf]
    run(cmd + enc)
    return out, n


def build_video():
    from concurrent.futures import ThreadPoolExecutor
    os.makedirs(SEG, exist_ok=True)
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(lambda p: build_segment(*p), list(enumerate(EDL))))
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
    return tl[name]["start"] + (src_t - s["a"]) / s.get("speed", 1.0)


_cache = {}
def load(c):
    if c not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src(c), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                             capture_output=True).stdout
        _cache[c] = np.frombuffer(raw, np.float32).copy()
    return _cache[c]


def piece(c, a, b, fade=0.02):
    x = load(c)[int(a * SR):int(b * SR)].copy()
    f = int(fade * SR)
    if f and len(x) > 2 * f:
        x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    return x


def build_audio(tl):
    total = tl["_total"]
    buf = np.zeros(int((total + 0.5) * SR), np.float32)
    placed = []
    def place(x, t, src=None):
        i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x
        if src: placed.append([src[0], round(src[1], 3), round(src[2], 3), round(t, 4)])
    for s in EDL:
        T = tl[s["name"]]["start"]
        if s.get("own"):
            place(piece(s["clip"], s["a"], s["b"]), T, (s["clip"], s["a"], s["b"]))
        for c, a, b, off in s.get("vo", []):
            if off is None:   # real strike on the slowed impact (picture first, sound peak one frame later)
                off = (IMPACTS[s["name"]] - s["a"]) / s.get("speed", 1.0) + 1 / FPS - (STRIKE - a)
            place(piece(c, a, b, 0.01), T + off, (c, a, b))
    tl["_voice"] = placed
    out = os.path.join(ROOT, "edit", "voice_raw.wav")
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(buf, -1, 1) * 32767).astype(np.int16).tobytes())
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af",
         "highpass=f=80,afftdn=nf=-40:nr=6,acompressor=threshold=-24dB:ratio=2.5:attack=8:release=200:makeup=2,"
         "loudnorm=I=-16:TP=-2:LRA=11", "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])


if __name__ == "__main__":
    tl = timeline()
    tl["_impacts"] = {k: round(film_time(tl, k, v), 3) for k, v in IMPACTS.items()}
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True); os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in tl.items() if k != "_voice"}, indent=0))
