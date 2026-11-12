#!/usr/bin/env python3
"""Cuts the source clip (iPhone on a tripod, 4K HEVC HLG 59.94 fps, upright 2160x3840) into one 1080x1920 30 fps A-roll (assets/aroll.mp4)
and builds the voice / natural-sound track (assets/voice.wav). No zoom anywhere: the camera never moves, so the shot tracer and the plan
drawings stay in the frame's own pixels (ball at (385,1359) on the film). Push-ins are done in the composition on a stage that scales
video and drawings together.

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]
Source: .src/clip1.mov (tools/fetch.sh).

Clip map (IMG_0030; the owner = grey shirt, black cap; talks quietly from off-frame left while the camera shows the hole):
  0.25-1.30   "154" (reading the distance)
  4.0-5.65 "Ok, disebabkan" · 6.45-8.85 "ke pin kita ada branch kat depan tu." · 9.3-11.25 "Ada sikit je pokok kat depan tu."
  12.85-14.6 "So, saya akan buat" · 1.6 s pause · 16.2-17.3 "draw sikit." · 18.15-19.4 "Supaya elak." · 19.85-21.35 "Kita aim kat bunker."
  22.05-23.4 "Bagi dia curve masuk."   (the club pokes in from the left now and then)
  24.5 walks in · 25-38.8 settles and waggles (cut) · takeaway 38.9 · top 39.5 · IMPACT 39.80 (transient 39.82) · finish 40.4, holds and watches
  45.74-49.32 "Oh, what a good shot." (quiet) · 49.4-51.5 walks up to the camera (face close, not used) · 50.8-52.2 "Tapi over sikit."
Clip 2 (IMG_0034, the result, filmed by a friend from the hole): 0.84 "Hole 2, Iqbal." · 3.3 "I think for birdie." · 17.8 "Fast, downhill putt,
  left to right." · 21.4 "Tengok apa jadi." · 22.6 "Back to back birdie." · birdie putt 24.28 · 27.9 "Need to slow down, need to slow down." ·
  rolls past the hole ~30.0 · 34.0 "Okay, not too bad." (camera moved) · second putt 72.02, drops 74.95 · 74.9 "Good save lah." · 76.7 "One down." (not used)
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
IMPACT = 39.80
GRADE = "null"     # no colour grade (owner's standing preference)

PLAN = [  # the talk, pauses cut (the picture is a static view of the hole, so the joins don't show)
    ("p1", 4.00, 5.65), ("p2", 6.45, 8.85), ("p3", 9.30, 11.25), ("p4", 12.85, 14.60),
    ("p5", 16.20, 17.30), ("p6", 18.15, 19.40), ("p7", 19.85, 21.35), ("p8", 22.05, 23.40),
]
EDL = [
    # HOOK: the swing into impact and the first second of flight (tracer starts), "154" over it
    dict(name="hook", clip=1, a=38.55, b=40.55, speed=1.0),
] + [dict(name=n, clip=1, a=a, b=b, speed=1.0) for n, a, b in PLAN] + [
    # THE SHOT: address -> swing -> the whole flight at 1x (tracer draws to the landing ~45.4)
    dict(name="swing", clip=1, a=38.30, b=45.50, speed=1.0),
    # "Oh, what a good shot." while he holds the finish and watches
    dict(name="react", clip=1, a=45.50, b=49.40, speed=1.0),
    # freeze before he walks up to the camera: "Tapi over sikit."
    dict(name="over_freeze", clip=1, a=49.40, kind="freeze", dur=2.0),
    # RESULT (clip2, IMG_0034, filmed by a friend on the green; tripod by the hole): the ball sits past the pin
    dict(name="r_intro1", clip=2, a=0.80, b=1.95, speed=1.0),      # "Hole 2, Iqbal."
    dict(name="r_intro2", clip=2, a=3.25, b=4.65, speed=1.0),      # "I think for birdie."
    dict(name="r_read", clip=2, a=17.70, b=20.45, speed=1.0),      # "Fast, downhill putt, left to right."
    dict(name="r_b2b", clip=2, a=21.40, b=23.65, speed=1.0),       # "Tengok apa jadi. Back to back birdie."
    dict(name="r_putt", clip=2, a=23.90, b=31.90, speed=1.0),      # birdie putt 24.28, "Need to slow down", rolls past the hole ~30.0
    dict(name="r_ok", clip=2, a=31.90, kind="freeze", dur=1.55),   # "Okay, not too bad." (34.0, while the camera moves) laid on a freeze
    dict(name="r_save", clip=2, a=71.20, b=75.95, speed=1.0),      # the putt back: stroke 72.02, drops 74.95, "Good save lah."
    dict(name="end_freeze", clip=2, a=75.95, kind="freeze", dur=3.6),]

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
    out = os.path.join(SEG, f"{i:02d}_{s['name']}.mp4")
    n = frames(seg_dur(s))
    enc = ["-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-g", "15", out]
    zf = ("," + zoom_filter(s["zoom"]) + ",setsar=1") if s.get("zoom") else ",scale=1080:1920:flags=lanczos,setsar=1"
    if s.get("kind") == "freeze":
        vf = f"{GRADE},trim=end_frame=1,setpts=PTS-STARTPTS,fps={FPS},tpad=stop_mode=clone:stop_duration={s['dur'] + 1}{zf}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-i", src(s["clip"]), "-vf", vf]
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
    total = tl["_total"]
    buf = np.zeros(int((total + 0.5) * SR), np.float32)
    placed = []
    def place(x, t, gain_db=0.0, src=None):
        i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * db(gain_db)
        if src: placed.append([src[0], round(src[1], 3), round(src[2], 3), round(t, 4)])
    T = lambda n: tl[n]["start"]
    # HOOK: swing sound in sync, "154" laid over the start
    place(piece(1, 38.55, 40.55, 0.04), T("hook"), -3)
    place(piece(1, 0.20, 1.32), T("hook") + 0.05, 0, (1, 0.20, 1.32))
    for n in [p[0] for p in PLAN] + ["swing", "react"]:
        s = next(x for x in EDL if x["name"] == n)
        place(piece(1, s["a"], s["b"], 0.03), T(n), 0, (1, s["a"], s["b"]))
    # "Oh, what a good shot" is said very quietly while he watches: lift it
    i0, i1 = int(film_time(tl, "react", 45.60) * SR), int(film_time(tl, "react", 49.38) * SR)
    r = np.ones(i1 - i0, np.float32) * db(4); f = int(0.05 * SR); r[:f] = np.linspace(1, db(4), f); r[-f:] = np.linspace(db(4), 1, f)
    buf[i0:i1] *= r
    # "Tapi over sikit." on the freeze, room tone under it
    tone = piece(1, 49.40, 50.70, 0.05); tone = np.tile(tone, 2)[:int(2.0 * SR)]
    place(tone, T("over_freeze"), -8)
    ov = (50.72, 52.22)
    place(piece(1, *ov), T("over_freeze") + 0.25, 0, (1, *ov))
    # RESULT: clip2 sync sound. The friend is close to the phone on some lines and far on others: per-piece gains even them out
    G2 = {"r_intro1": -6, "r_intro2": 2, "r_read": 3, "r_b2b": 5, "r_putt": 2, "r_save": 6}
    for n, g in G2.items():
        s2 = next(x for x in EDL if x["name"] == n)
        place(piece(2, s2["a"], s2["b"], 0.03), T(n), g, (2, s2["a"], s2["b"]))
    tone2 = piece(2, 31.0, 31.9, 0.05); tone2 = np.tile(tone2, 2)[:int(1.55 * SR)]
    place(tone2, T("r_ok"), 0)
    okp = (34.00, 35.38)
    place(piece(2, *okp), T("r_ok") + 0.05, 5, (2, *okp))        # "Okay, not too bad."
    tone3 = piece(2, 75.95, 76.60, 0.05); tone3 = np.tile(tone3, 6)[:int(3.6 * SR)]; tone3 *= np.linspace(1, 0, len(tone3))
    place(tone3, T("end_freeze"), -4)
    tl["_voice"] = placed
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    out = os.path.join(ROOT, "edit", "voice_raw.wav")
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    # he talks quietly from off-frame: denoise harder, lift the presence band, compress, then loudnorm
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af",
         "highpass=f=110,afftdn=nf=-42:nr=14,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3000:t=q:w=1.2:g=4,"
         "acompressor=threshold=-30dB:ratio=3.5:attack=5:release=180:makeup=6,loudnorm=I=-16:TP=-2:LRA=8",
         "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])


if __name__ == "__main__":
    tl = timeline()
    beats = {"hook_impact": film_time(tl, "hook", IMPACT), "takeaway": film_time(tl, "swing", 38.90),
             "impact": film_time(tl, "swing", IMPACT), "landing": film_time(tl, "swing", 45.40),
             "putt1": film_time(tl, "r_putt", 24.28), "putt1_hole": film_time(tl, "r_putt", 30.0),
             "putt2": film_time(tl, "r_save", 72.02), "drop": film_time(tl, "r_save", 74.95)}
    tl["_beats"] = {k: round(v, 3) for k, v in beats.items()}
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True); os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print({k: v for k, v in tl.items()})
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
