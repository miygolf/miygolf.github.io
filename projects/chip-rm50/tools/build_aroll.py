#!/usr/bin/env python3
"""Cuts the source clip (iPhone, 4K HEVC 59.94 fps, upright 2160x3840) into one 1080x1920 30 fps A-roll (assets/aroll.mp4)
and builds the natural-sound track (assets/voice.wav). Same raw / chalkboard treatment as projects/bunker-raw (owner: "sama buat macam bunker shot style").

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]

Clip map (handheld behind/side of the coach, grey shirt; a friend in black with a bucket hat on the green later):
  0-3.0      ball on the turf, the coach walks in (face top-left from 3.0)
  1.64-3.12  "30 meter."   3.38-5.58 "Chip in, chip in."   5.86-6.84 "50 ringgit."   (large-v3 ms + en + crops agree)
  7.3-14.6   waiting at address (cut)
  impact 16.62 (picture; sound peak 16.646), divot flies, he watches 17-22
  20.40-20.94 "Masuk!" (ms) / "Go in!" (en)   16.6-17.5 and 21.3-24.5 unclear chatter (not captioned)
  23.6       camera pans to the friend on the green: hands out, "Tak dapat." 26.82-28.22 (ms; en "can't reach it")
  Faces (film px): coach x 300-560 / y 60-380 (head high in frame) -> chalk boards in the right column (x >= 560);
  friend x 300-380 / y 250-330.
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
IMPACT = 16.62
SND = 16.646

GRADE = "null"

EDL = [
    # HOOK: the strike 0.5x, freeze as the turf flies
    dict(name="hook_a", clip=1, a=16.25, b=16.90, speed=0.5),
    dict(name="hook_freeze", clip=1, a=16.90, kind="freeze", dur=1.1),
    # the bet: "30 meter. Chip in, chip in. 50 ringgit."
    dict(name="bet", clip=1, a=1.30, b=7.30, speed=1.0),
    # address + the shot, raw
    dict(name="shot", clip=1, a=14.60, b=17.60, speed=1.0),
    # watching it: "Masuk!"
    dict(name="watch", clip=1, a=18.70, b=21.80, speed=1.0),
    # the friend: hands out, "Tak dapat."
    dict(name="friend", clip=1, a=24.10, b=28.90, speed=1.0),
    dict(name="end_freeze", clip=1, a=28.90, kind="freeze", dur=4.4),
]


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
    return os.path.join(SRC, f"clip{clip}.mov")


def build_segment(i, s):
    if s.get("kind") == "rev": s = dict(s)
    out = os.path.join(SEG, f"{i:02d}_{s['name']}.mp4")
    n = frames(seg_dur(s))
    enc = ["-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-g", "15", out]
    zf = ("," + zoom_filter(s["zoom"]) + ",setsar=1") if s.get("zoom") else ",scale=1080:1920:flags=lanczos,setsar=1"
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


def build_audio(tl):
    """Raw: each segment carries its own sound; the hook gets the real strike on the slowed impact. No loops, no beds."""
    total = tl["_total"]
    buf = np.zeros(int((total + 0.5) * SR), np.float32)
    placed = []
    def place(x, t, gain_db=0.0, src=None):
        i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * db(gain_db)
        if src: placed.append([src[0], round(src[1], 3), round(src[2], 3), round(t, 4)])
    T = lambda n: tl[n]["start"]
    for n in ("bet", "shot", "watch", "friend"):
        s = next(x for x in EDL if x["name"] == n)
        place(piece(1, s["a"], s["b"], 0.03), T(n), 0, (1, s["a"], s["b"]))
    place(piece(1, 16.25, 16.62, 0.05), 0.0, -6)
    place(piece(1, SND - 0.03, SND + 0.40, 0.004), film_time(tl, "hook_a", IMPACT) + 1 / FPS - 0.03, 0)
    tl["_voice"] = placed
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    out = os.path.join(ROOT, "edit", "voice_raw.wav")
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af",
         "highpass=f=80,afftdn=nf=-42:nr=4,acompressor=threshold=-26dB:ratio=2.5:attack=8:release=200:makeup=2,"
         "loudnorm=I=-16:TP=-2:LRA=11", "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])


if __name__ == "__main__":
    tl = timeline()
    beats = {
        "hook_impact": film_time(tl, "hook_a", IMPACT),
        "shot_impact": film_time(tl, "shot", IMPACT),
        "w_30": film_time(tl, "bet", 1.64), "w_chip": film_time(tl, "bet", 3.38), "w_50": film_time(tl, "bet", 5.86),
        "w_masuk": film_time(tl, "watch", 20.40), "w_takdapat": film_time(tl, "friend", 26.82),
    }
    tl["_beats"] = {k: round(v, 3) for k, v in beats.items()}
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print(json.dumps(tl, indent=1))
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
