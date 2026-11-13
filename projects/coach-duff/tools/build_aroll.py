#!/usr/bin/env python3
"""Cuts the two source clips (iPhone, 4K HEVC 59.94 fps, upright 2160x3840) into one 1080x1920 30 fps A-roll (assets/aroll.mp4)
and builds the natural-sound track (assets/voice.wav). The EDL below is the single source of truth: film times of every segment
and beat go to edit/timeline.json, which tools/build_index.py turns into graphics and SFX.

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]
Needs ffmpeg and numpy. Sources live in .src/ (see tools/fetch.sh).

No speech in either clip (faster-whisper small, ms + auto: only the usual end-of-silence hallucinations; edit/transcript.txt).
Cut on picture beats instead.

Clip map
  clip1 (IMG_0187, handheld, 4.6 s): ball's lie close-up 0-2.2 (camera backing away), tilt up 2.2-2.6, flag on the green 2.6-3.4
        (flag ~ (520, 280) film px at 2.8), drifts down to the tripod spot 3.4-4.6
  clip2 (IMG_0188, tripod behind the ball, 31.3 s): empty fairway 0-3.4, coach walks in 3.4-5.0, at address 5.5,
        waggles / one rehearsal ~15.7 / settles until the take-away 21.6, top ~21.85, IMPACT 22.15 (picture; sound peak 22.166),
        a big chunk of turf flies 22.2-22.45, the ball leaves the frame (where it lands is not visible), he freezes and stares 22.5-24.3,
        turns and walks to the phone 24.3-27.6 laughing (face clear 25.9-27.3, top-left of the frame), shirt fills the frame 27.6+.
  Face boxes (film px, 1080x1920): address 220-340 x 380-520 y; laugh 26.0 20-220 x 200-400 y, 26.6 80-320 x 120-360 y, 27.2 0-320 x 0-360 y.
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
IMPACT = 22.15          # picture
SND = 22.166            # the strike's sound peak in the take

GRADE = "null"          # no colour grade: iPhone colour as shot (owner's standing preference)

# EDL in film order.  kind: None (play), "freeze" (hold src a for dur), "rev" (play b -> a backwards at speed)
# zoom = [(t_in_segment, zoom, cx, cy)] in source pixels (2160x3840), smoothstep between keys
EDL = [
    # HOOK: the strike at 0.5x (every 60 fps frame), tight on hands, club and ball so the face is above the frame; freeze on the turf in the air
    dict(name="hook_a", clip=2, a=21.62, b=22.30, speed=0.5, zoom=[(0, 1.5, 1000, 2560), (1.36, 1.6, 1030, 2600)]),
    dict(name="hook_freeze", clip=2, a=22.30, kind="freeze", dur=1.25, zoom=[(0, 1.6, 1030, 2600), (1.25, 1.68, 1040, 2620)]),
    # REWIND to the start (trail-cam tape rewinds over the whole setup)
    dict(name="rew", clip=2, a=3.40, b=22.30, speed=21.0, kind="rev"),
    # HABITAT: the lie, then the flag
    dict(name="lie", clip=1, a=0.20, b=2.50, speed=1.6),
    dict(name="lie_flag", clip=1, a=2.50, b=3.45, speed=1.0),
    # SPECIMEN walks in and takes his address
    dict(name="walk", clip=2, a=3.40, b=5.90, speed=1.4),
    # setup fast-forwarded (15.4 s of waggles in 2.2 s)
    dict(name="ff", clip=2, a=5.90, b=21.30, speed=7.0),
    # THE SHOT at 1x, and the frozen stare after it
    dict(name="shot", clip=2, a=21.30, b=23.50, speed=1.0, zoom=[(0, 1.0, 1080, 1920), (2.2, 1.06, 900, 2100)]),
    # REPLAY at 0.5x, tight on the turf
    dict(name="replay", clip=2, a=21.95, b=22.55, speed=0.5, zoom=[(0, 1.8, 1120, 2780), (1.2, 2.0, 1160, 2800)]),
    # REACTION: walks to the phone laughing (face top-left)
    dict(name="laugh", clip=2, a=25.30, b=26.95, speed=1.0),
    dict(name="end_freeze", clip=2, a=26.95, kind="freeze", dur=3.4, zoom=[(0, 1.0, 1080, 1920), (3.4, 1.04, 900, 1800)]),
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
    """Natural sound only (no speech in the takes). The phone heard the course as near-silence (~-46 dBFS) plus the strike.
    Sync segments carry their own sound; the strike is lifted so it reads; the bird bed and SFX live in index.html."""
    total = tl["_total"]
    buf = np.zeros(int((total + 0.5) * SR), np.float32)
    def place(x, t, gain_db=0.0):
        i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * db(gain_db)
    T = lambda n: tl[n]["start"]
    BED = 10      # lift the take's room tone a little
    for n in ("shot", "laugh"):
        s = next(x for x in EDL if x["name"] == n)
        place(piece(2, s["a"], s["b"], 0.04), T(n), BED)
    # the strike: lifted, peak one frame after the picture (house rule); hook and replay get it too
    hit = lambda: piece(2, SND - 0.03, SND + 0.35, 0.004)
    for name, src_t in (("hook_a", IMPACT), ("shot", IMPACT), ("replay", IMPACT)):
        ft = film_time(tl, name, src_t) + 1 / FPS
        place(hit(), ft - 0.03, 22 if name != "shot" else 12)
    tail = piece(2, 26.95, 27.60, 0.05)
    tail = np.tile(tail, 6)[:int(3.4 * SR)]; tail *= np.linspace(1, 0, len(tail))
    place(tail, T("end_freeze"), BED)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    out = os.path.join(ROOT, "edit", "voice_raw.wav")
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af", "highpass=f=70,afftdn=nf=-30:nr=12",
         "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])


if __name__ == "__main__":
    tl = timeline()
    beats = {
        "hook_impact": film_time(tl, "hook_a", IMPACT),
        "hook_turf": tl["hook_freeze"]["start"],
        "lie_flag": film_time(tl, "lie_flag", 2.80),
        "walk_address": film_time(tl, "walk", 5.30),
        "ff_rehearsal": film_time(tl, "ff", 15.70),
        "shot_takeaway": film_time(tl, "shot", 21.60),
        "shot_impact": film_time(tl, "shot", IMPACT),
        "shot_stare": film_time(tl, "shot", 22.60),
        "replay_impact": film_time(tl, "replay", IMPACT),
        "laugh_face": film_time(tl, "laugh", 25.90),
    }
    tl["_beats"] = {k: round(v, 3) for k, v in beats.items()}
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print(json.dumps(tl, indent=1))
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
