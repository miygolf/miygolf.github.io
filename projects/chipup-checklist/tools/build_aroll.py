#!/usr/bin/env python3
"""Cuts the source clip (iPhone, 4K HEVC 59.94 fps, upright 2160x3840) into one 1080x1920 30 fps A-roll (assets/aroll.mp4)
and builds the natural-sound track (assets/voice.wav). Educational, raw, low-SFX like bunker-raw / chip-rm50, in a new
"notebook checklist" format (owner: "sama educational style macam sebelum ni tapi ubah format skit").

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]

Clip map (face-on, the coach by a greenside bunker; the person filming turns the phone on himself at the end):
  0-2.0     "Right, ... Coach [name?], sorry" (cut)
  2.16-3.40 "Kita nak chip [up ke / up here / uphill / 'cip api']" - unclear across large-v3 / medium crops: captioned "Kita nak chip…", title CHIPPING
  4.82-6.98 "Okay, ball position saya akan letak kat tengah."
  7.98-9.34 "Slightly depan sikit, tak apa."
  9.92-10.92 "Weight pula kiri."
  12.38-13.40 "Okay, club face dia"   15.44-17.62 "normal je, tak perlu buka pun." (large-v3 crop ms "buka", en "no need to open it")
  18.84 "Right" ; IMPACT 19.22 (sound peak 19.24) ; camera pans to the green 20.6-24.5 ("Baik" / "That's it" ~23.4: passes disagree, not captioned)
  25.4-26.96 selfie of the person filming, two fingers up
  Faces (film px): coach x 420-680 / y 330-800 (centre) -> notebook card in the left column (x 60-420); selfie face x 600-900 / y 300-800.
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
IMPACT = 19.22
SND = 19.24

GRADE = "null"

EDL = [
    # HOOK: the chip at 0.5x, freeze just after the strike
    dict(name="hook_a", clip=1, a=18.85, b=19.45, speed=0.5),
    dict(name="hook_freeze", clip=1, a=19.45, kind="freeze", dur=1.0),
    dict(name="intro", clip=1, a=2.15, b=3.70, speed=1.0),
    dict(name="p1", clip=1, a=4.72, b=7.10, speed=1.0),
    dict(name="p2", clip=1, a=7.85, b=9.42, speed=1.0),
    dict(name="p3", clip=1, a=9.75, b=11.05, speed=1.0),
    dict(name="p4a", clip=1, a=12.28, b=13.62, speed=1.0),
    dict(name="p4b", clip=1, a=15.32, b=17.75, speed=1.0),
    dict(name="shot", clip=1, a=17.75, b=20.60, speed=1.0),
    dict(name="pan", clip=1, a=21.00, b=23.30, speed=1.0),
    dict(name="selfie", clip=1, a=26.05, b=26.75, speed=1.0),
    dict(name="end_freeze", clip=1, a=26.75, kind="freeze", dur=3.2),   # two fingers up, sharp
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
    for n in ("intro", "p1", "p2", "p3", "p4a", "p4b", "shot", "pan", "selfie"):
        s = next(x for x in EDL if x["name"] == n)
        place(piece(1, s["a"], s["b"], 0.03), T(n), 0, (1, s["a"], s["b"]))
    place(piece(1, 18.85, 19.20, 0.05), 0.0, -6)
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
        "w_chipup": film_time(tl, "intro", 3.00),
        "w_tengah": film_time(tl, "p1", 6.72), "w_depan": film_time(tl, "p2", 8.46), "w_kiri": film_time(tl, "p3", 10.60),
        "w_face": film_time(tl, "p4a", 12.94), "w_buka": film_time(tl, "p4b", 17.10),
    }
    tl["_beats"] = {k: round(v, 3) for k, v in beats.items()}
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print(json.dumps(tl, indent=1))
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
