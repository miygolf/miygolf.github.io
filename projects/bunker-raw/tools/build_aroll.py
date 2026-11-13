#!/usr/bin/env python3
"""Cuts the source clip (iPhone, 4K HEVC HLG 59.94 fps, upright 2160x3840) into one 1080x1920 30 fps A-roll (assets/aroll.mp4)
and builds the dialogue / natural-sound track (assets/voice.wav). The EDL below is the single source of truth: film times of every segment
and beat go to edit/timeline.json, which tools/build_index.py turns into graphics, captions and SFX.

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]
Needs ffmpeg and numpy. Source lives in .src/clip1.mov (see tools/fetch.sh).

Raw / educational-with-a-laugh cut of the same clip as projects/bunker-nyaris (owner: less SFX, raw, hear the green).
Clip map (IMG_0193, handheld; the coach = grey shirt, black cap, in a greenside bunker; the person filming asks / reacts):
  0.00-2.38  question: "Favourite bunker nampaknya [name unclear] hari ni?" (large-v3 ms+en agree on "favourite bunker", "hari ni"; the name is not captioned)
  2.86-3.84  "Bunker sahaja."  (coach walking toward the camera, face ~ x 480-680 / y 560-720 film)
  4.38-7.30  "Saya boleh tunjuk banyak sikit educational video."
  9.56-11.92 "Almost similar, about 20 feet."  ("20": medium + large-v3 crops)
  11.92-12.82 "Kita main stock shot."  (face far, ~ x 340-510 / y 890-930 film)
  13-19      setup, camera walks in; "stop shot" repeated 14.76-15.96 (cut)
  address ~19.2, IMPACT 20.74 (picture; sound peak 20.749), sand spray 20.75-21.0
  21.0-22.4  camera whips to the green past two players
  22.45-22.86 the ball rolls in from the left and passes right at the cup (22.83-22.90), keeps rolling right, still creeping at the end 25.2
  22.94-23.90 "What a player!" (behind the phone)
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
IMPACT = 20.74          # picture
SND = 20.749            # strike sound peak in the take
CUP = 22.86             # ball at the cup

GRADE = "null"          # no colour grade: iPhone colour as shot

# Wide framing (owner prefers seeing the course). Raw: every segment plays at 1x with its own sound except the hook.
HOOK_A = [(0, 1.25, 1150, 2350), (0.72, 1.3, 1180, 2400)]
HOOK_F = [(0, 1.3, 1180, 2400), (1.8, 1.34, 1184, 2414)]

EDL = [
    # HOOK: the ball at the cup, 0.5x, freeze as it passes the hole
    dict(name="hook_a", clip=1, a=22.50, b=CUP, speed=0.5, zoom=HOOK_A),
    dict(name="hook_freeze", clip=1, a=CUP, kind="freeze", dur=1.8, zoom=HOOK_F),
    # "Favourite bunker nampaknya ... hari ni?"  "Bunker sahaja."
    dict(name="q", clip=1, a=0.00, b=3.95, speed=1.0),
    # "Saya boleh tunjuk banyak sikit educational video."
    dict(name="edu", clip=1, a=4.30, b=7.45, speed=1.0),
    # "Almost similar, about 20 feet. Kita main stop shot."
    dict(name="plan", clip=1, a=9.30, b=12.96, speed=1.0),
    # address + swing, raw
    dict(name="shot", clip=1, a=19.20, b=21.05, speed=1.0),
    # the camera whips to the green, raw 1x
    dict(name="whip", clip=1, a=21.05, b=22.45, speed=1.0),
    # the roll past the cup, "What a player!"
    dict(name="roll", clip=1, a=22.45, b=25.15, speed=1.0),
    dict(name="end_freeze", clip=1, a=25.15, kind="freeze", dur=4.4),
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
    """Raw: each segment carries its own sound (no SFX layered on the strike). The quiet "stop shot" line is lifted."""
    total = tl["_total"]
    buf = np.zeros(int((total + 0.5) * SR), np.float32)
    placed = []
    def place(x, t, gain_db=0.0, src=None):
        i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * db(gain_db)
        if src: placed.append([src[0], round(src[1], 3), round(src[2], 3), round(t, 4)])
    T = lambda n: tl[n]["start"]
    for n in ("q", "edu", "plan", "shot", "whip", "roll"):
        s = next(x for x in EDL if x["name"] == n)
        place(piece(1, s["a"], s["b"], 0.03), T(n), 0, (1, s["a"], s["b"]))
    i0, i1 = int(film_time(tl, "plan", 11.90) * SR), int(film_time(tl, "plan", 12.92) * SR)
    ramp = np.ones(i1 - i0, np.float32) * db(9); f = int(0.04 * SR); ramp[:f] = np.linspace(1, db(9), f); ramp[-f:] = np.linspace(db(9), 1, f)
    buf[i0:i1] *= ramp
    # hook and end freeze: no sound bed. (v1 looped a 0.9 s green-ambience piece here; the owner heard it as a stuck sound: removed)
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
        "hook_cup": tl["hook_freeze"]["start"],
        "shot_impact": film_time(tl, "shot", IMPACT),
        "roll_cup": film_time(tl, "roll", CUP),
        "w_fav": film_time(tl, "q", 0.10), "w_bunker": film_time(tl, "q", 2.86),
        "w_edu": film_time(tl, "edu", 6.64), "w_20": film_time(tl, "plan", 10.92), "w_stop": film_time(tl, "plan", 12.38),
        "w_player": film_time(tl, "roll", 23.60),
    }
    tl["_beats"] = {k: round(v, 3) for k, v in beats.items()}
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print(json.dumps(tl, indent=1))
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
