#!/usr/bin/env python3
"""Cuts the one source clip (iPhone, 1080x1920 HEVC 30 fps, 21.8 s) into the 1080x1920 30 fps A-roll (assets/aroll.mp4),
builds the voice / natural-sound track (assets/voice.wav) and the two proof stills (assets/img/).
The EDL is the single source of truth: film times of every segment and beat go to edit/timeline.json,
which tools/build_index.py turns into graphics, captions, music and SFX.

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]
Source: .src/clip1.mov (tools/fetch.sh).

What the clip holds (transcript: edit/transcript.txt, checked again on boosted pieces):
  0.4-1.8  "So, kita on the green."            (not used: the hook says it in text)
  3.2-7.5  "Boleh tak kita pakai chip ataupun wedge?"   (long pauses inside, removed)
  8.8-9.5  "Mestilah boleh."                    (quiet, boosted)
  10.45 backswing starts, 11.10 impact (club at the ball, audio peak on the same frame)
  12.2-16 camera pans to the green, ball rolls up by the pin
  16.3-20.2 camera swings back, golfer points at the spot, camera walks up and tilts down
  20.2-21.0 wedge sole resting on the spot: turf intact, no divot
  20.98-21.4 "Clean."
Cut: the waggles / practice swings (0-8.5), the pauses inside the question, the wobble 15.9-16.3, the slow walk (sped 2.2x).
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src", "clip1.mov")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
UP = 2  # zoompan runs on a 2x lanczos upscale (2160x3840) so slow push-ins don't step

# no colour grade (house style: iPhone's own colour)
GRADE = "null"

# zoom keys: (t_in_segment, zoom, cx, cy) in SOURCE pixels (1080x1920), smoothstep between keys
EDL = [
    # HOOK: the backswing + downswing at 0.3x, push-in onto the club and ball, freeze on contact
    dict(name="hook_slow", a=10.45, b=11.10, speed=0.3, zoom=[(0, 1.5, 700, 1050), (2.167, 2.1, 484, 1400)]),
    dict(name="hook_freeze", a=11.10, kind="freeze", dur=0.80, zoom=[(0, 2.1, 484, 1400), (0.8, 2.2, 480, 1404)]),
    # DEMO at 1x: address ("Mestilah boleh."), the chip, real strike
    dict(name="demo", a=8.55, b=12.20, speed=1.0, zoom=[(0, 1.12, 540, 1000), (3.65, 1.2, 530, 1020)]),
    # the ball on the green
    dict(name="roll_pan", a=12.20, b=13.60, speed=1.75),
    dict(name="roll", a=13.60, b=15.90, speed=1.0, zoom=[(0, 1.0, 540, 960), (2.3, 1.06, 560, 1000)]),
    # back to the spot: swing back, walk up, tilt down
    dict(name="back_whip", a=16.30, b=17.20, speed=1.5),
    dict(name="walk_tilt", a=17.20, b=20.20, speed=2.2),
    dict(name="turf", a=20.20, b=20.95, speed=1.0, zoom=[(0, 1.0, 540, 960), (0.75, 1.1, 500, 1150)]),
    # the answer: freeze on the intact turf, then proof + CTA on the same frame
    dict(name="turf_freeze", a=20.95, kind="freeze", dur=2.50, zoom=[(0, 1.1, 500, 1150), (2.5, 1.22, 492, 1220)]),
    dict(name="end_freeze", a=20.95, kind="freeze", dur=5.40, zoom=[(0, 1.22, 492, 1220), (5.4, 1.32, 488, 1244)]),
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
    cx = _lerp_expr([(k[0], k[2] * UP) for k in zk])
    cy = _lerp_expr([(k[0], k[3] * UP) for k in zk])
    return (f"scale={1080 * UP}:{1920 * UP}:flags=lanczos,"
            f"zoompan=z='{z}':x='clip({cx}-iw/zoom/2,0,iw-iw/zoom)':y='clip({cy}-ih/zoom/2,0,ih-ih/zoom)'"
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


def build_segment(i, s):
    out = os.path.join(SEG, f"{i:02d}_{s['name']}.mp4")
    n = frames(seg_dur(s))
    enc = ["-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", "-g", "15", out]
    zf = ("," + zoom_filter(s["zoom"]) + ",setsar=1") if s.get("zoom") else ",setsar=1"
    if s.get("kind") == "freeze":
        vf = f"{GRADE},trim=end_frame=1,setpts=PTS-STARTPTS,fps={FPS},tpad=stop_mode=clone:stop_duration={s['dur'] + 1}{zf}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-i", SRC, "-vf", vf]
    else:
        # slow segments: plain frame repeats (no interpolation: the club would warp)
        vf = f"{GRADE},setpts=PTS/{s['speed']},fps={FPS}{zf}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{s['b'] - s['a'] + 0.3:.3f}", "-i", SRC, "-vf", vf]
    run(cmd + enc)
    return out, n


def build_video():
    from concurrent.futures import ThreadPoolExecutor
    os.makedirs(SEG, exist_ok=True)
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(lambda p: build_segment(*p), list(enumerate(EDL))))
    for (p, n), s in zip(res, EDL):
        print(f"  seg {os.path.basename(p):<22} {n} frames")
    with open(os.path.join(SEG, "list.txt"), "w") as f:
        for p, _ in res:
            f.write(f"file '{p}'\n")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(SEG, "list.txt"), "-c", "copy",
         os.path.join(ROOT, "assets", "aroll.mp4")])


def build_stills():
    """proof stills: contact (11.10 s) and the intact turf under the resting wedge (20.95 s)."""
    d = os.path.join(ROOT, "assets", "img"); os.makedirs(d, exist_ok=True)
    for name, t in [("proof-impact", 11.10), ("proof-turf", 20.95)]:
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", SRC, "-frames:v", "1",
             "-vf", f"{GRADE},scale=1080:1920:flags=lanczos", "-q:v", "2", os.path.join(d, f"{name}.jpg")])


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
def load():
    if "a" not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                             capture_output=True).stdout
        _cache["a"] = np.frombuffer(raw, np.float32).copy()
    return _cache["a"]


def piece(a, b, fade=0.03):
    x = load()[int(a * SR):int(b * SR)].copy()
    f = int(fade * SR)
    if f and len(x) > 2 * f:
        x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    return x


def db(g):
    return 10 ** (g / 20)


def build_audio(tl):
    total = tl["_total"]
    buf = np.zeros(int((total + 0.5) * SR), np.float32)
    placed = []   # (src_a, src_b, film_t): build_index maps transcript word times onto the film with these
    def place(x, t, gain_db=0.0, src=None):
        i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * db(gain_db)
        if src: placed.append([round(src[0], 3), round(src[1], 3), round(t, 4)])
    def chain(parts, t, gain_db=0.0, gap=0.05):
        for a, b in parts:
            x = piece(a, b); place(x, t, gain_db, (a, b)); t += len(x) / SR + gap
        return t
    T = lambda n: tl[n]["start"]
    # hook: the question, pauses removed, over the slow-mo (no natural sound under the slow-mo)
    end_q = chain([(3.15, 4.50), (4.75, 5.60), (6.78, 7.50)], 0.04, 0.0)
    tl["_q_end"] = round(end_q, 3)
    # demo: "Mestilah boleh." (quiet -> boosted), then the address and the real strike in sync
    d0 = T("demo")
    place(piece(8.55, 9.68, 0.02), d0, +10, (8.55, 9.68))
    place(piece(9.68, 12.20, 0.04), d0 + (9.68 - 8.55), +1, (9.68, 12.20))
    # ambience under the roll and the walk (quiet)
    place(piece(13.60, 15.90, 0.1), T("roll"), -8)
    # "Clean." over the freeze on the intact turf
    place(piece(20.98, 21.42, 0.02), T("turf_freeze") + 0.15, +9, (20.98, 21.42))
    tl["_voice"] = placed
    out = os.path.join(ROOT, "edit", "voice_raw.wav")
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af",
         "highpass=f=90,afftdn=nf=-30:nr=10,equalizer=f=3000:t=q:w=1.2:g=2,acompressor=threshold=-24dB:ratio=3:attack=8:release=180:makeup=4,"
         "loudnorm=I=-16:TP=-2:LRA=9",
         "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])


if __name__ == "__main__":
    tl = timeline()
    tl["_beats"] = {
        "hook_impact": round(tl["hook_freeze"]["start"], 3),
        "mestilah": round(film_time(tl, "demo", 8.80), 3),
        "boleh": round(film_time(tl, "demo", 9.28), 3),
        "impact": round(film_time(tl, "demo", 11.10), 3),
        "clean": round(tl["turf_freeze"]["start"] + 0.15, 3),
    }
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True)
    if "--audio-only" not in sys.argv:
        build_stills()
        build_video()
    build_audio(tl)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in tl.items() if k != "_voice"}, indent=1))
