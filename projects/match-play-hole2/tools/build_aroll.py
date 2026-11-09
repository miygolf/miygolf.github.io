#!/usr/bin/env python3
"""Cuts the six source clips (iPhone 15, 4K HEVC 60 fps, upright) into one 1080x1920 30 fps A-roll (assets/aroll.mp4),
builds the dialogue / natural-sound track (assets/voice.wav) and the two VS-card stills (assets/img/).
The EDL below is the single source of truth: film times of every segment and beat go to edit/timeline.json,
which tools/build_index.py turns into graphics, captions, music and SFX.

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]
Needs ffmpeg and numpy. Sources live in .src/clip1..6.mov (see tools/fetch.sh).

Players: IQBAL = grey shirt, black trousers, black cap (red corner). FARHAN = teal shirt, white cap (blue corner).
Clip map: 1 tee shots (Farhan 4.75 s, Iqbal 39.27 s; the third player is cut), 2 Iqbal approach (39.82 s),
3 Farhan approach (31.48 s), 4 Farhan chip (17.58 s) + his explanation, 5 Farhan putt -> "Bogey",
6 Iqbal long birdie putt (stroke ~27.2 s) + par putt (drops ~75.3 s) + "Next hole".
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
SW, SH = 2160, 3840  # upright source

# one grade for every clip (v2, owner: "terang sangat"): darker mids, highlights pulled down to tame the bright sky,
# deeper shadows, a little cool in the shadows and warm in the highlights so skin stays natural
GRADE = ("eq=contrast=1.10:saturation=1.06:gamma=0.86,curves=all='0/0 0.25/0.17 0.5/0.40 0.75/0.66 1/0.88',"
         "colorbalance=bs=0.05:gs=0.01:rh=0.04:bh=-0.04")

# EDL in film order.  kind: None (play), "freeze" (hold src a for dur), "black" (dur)
# zoom = [(t_in_segment, zoom, cx, cy)] in source pixels (2160x3840), smoothstep between keys
EDL = [
    # HOOK: Farhan's chip comes out fat -> "Astagfirullah", freeze on the look-up
    dict(name="hook_chip", clip=4, a=16.20, b=18.95, speed=1.0,
         zoom=[(0, 1.12, 1000, 2000), (2.75, 1.32, 980, 1750)]),
    dict(name="hook_freeze", clip=4, a=18.95, kind="freeze", dur=0.75, zoom=[(0, 1.32, 980, 1750), (0.75, 1.40, 980, 1700)]),
    # VS card (stills drawn in HTML over black)
    dict(name="vs", kind="black", dur=2.70),
    # TEE SHOTS
    dict(name="tee_far", clip=1, a=3.55, b=6.25, speed=1.0),
    dict(name="tee_iqb", clip=1, a=37.85, b=40.75, speed=1.0),
    # IQBAL SHOT 2: the plan over his POV (static), the swing, the verdict
    dict(name="iqb_plan", clip=2, a=9.60, b=18.30, speed=1.0, zoom=[(0, 1.0, 1080, 1920), (8.7, 1.1, 1000, 1850)]),
    dict(name="iqb_swing", clip=2, a=38.30, b=41.50, speed=1.0, zoom=[(0, 1.55, 560, 2250), (3.2, 1.62, 560, 2230)]),
    dict(name="iqb_react", clip=2, a=49.30, b=51.45, speed=1.0),
    # FARHAN SHOT 2
    dict(name="far_plan", clip=3, a=17.90, b=23.40, speed=1.0),
    dict(name="far_swing", clip=3, a=29.95, b=33.40, speed=1.0, zoom=[(0, 1.18, 760, 2050), (3.45, 1.24, 760, 2000)]),
    # FARHAN CHIP: slow replay of contact, then his own diagnosis (jump cut hidden by a punch-in)
    dict(name="chip_replay", clip=4, a=16.95, b=17.95, speed=0.5, zoom=[(0, 1.3, 980, 1950), (2.0, 1.55, 900, 2000)]),
    dict(name="chip_kenapa", clip=4, a=21.75, b=22.85, speed=1.0),
    dict(name="chip_why_a", clip=4, a=28.85, b=30.05, speed=1.0),
    dict(name="chip_why_b", clip=4, a=31.10, b=32.95, speed=1.0, zoom=[(0, 1.15, 1000, 1700), (1.85, 1.18, 1000, 1700)]),
    # FARHAN PUTT -> bogey
    dict(name="far_disaster", clip=5, a=0.62, b=1.90, speed=1.0),
    dict(name="far_putt", clip=5, a=29.00, b=33.70, speed=1.0, zoom=[(0, 1.0, 1080, 1920), (4.7, 1.1, 1000, 2000)]),
    dict(name="far_bogey", clip=5, a=35.85, b=36.99, speed=1.0),
    # IQBAL BIRDIE PUTT: 4K push-in on the far address, pull back with the ball rolling to the cup
    dict(name="iqb_read", clip=6, a=20.45, b=27.25, speed=1.0,
         zoom=[(0, 2.7, 1226, 1600), (6.65, 3.2, 1226, 1600)]),
    dict(name="iqb_roll", clip=6, a=27.25, b=31.70, speed=1.0,
         zoom=[(0, 3.2, 1226, 1600), (0.5, 3.2, 1226, 1600), (3.4, 1.15, 1150, 2000), (4.45, 1.1, 1130, 2050)]),
    dict(name="iqb_ok", clip=6, a=34.00, b=35.35, speed=1.0),
    # IQBAL PAR PUTT: real time to the stroke, slow on the roll, real time from the drop
    dict(name="par_setup", clip=6, a=72.467, b=74.45, speed=1.0, zoom=[(0, 1.2, 760, 2150), (2.1, 1.3, 900, 2200)]),
    dict(name="par_roll", clip=6, a=74.45, b=75.30, speed=0.4, zoom=[(0, 1.3, 900, 2200), (2.1, 1.45, 1100, 2250)]),
    dict(name="par_drop", clip=6, a=75.30, b=76.60, speed=1.0, zoom=[(0, 1.45, 1100, 2250), (1.3, 1.2, 1000, 2150)]),
    # WINNER walks up: "Next hole." -> end freeze
    dict(name="next", clip=6, a=79.20, b=81.10, speed=1.0),
    dict(name="end_freeze", clip=6, a=81.10, kind="freeze", dur=7.50, zoom=[(0, 1.0, 1080, 1920), (7.5, 1.08, 1060, 1500)]),
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
    if s.get("kind") in ("freeze", "black"):
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
    kind = s.get("kind")
    enc = ["-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", "-g", "15", out]
    if kind == "black":
        run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x0b0b10:s=1080x1920:r={FPS}"] + enc)
        return out, n
    zf = ("," + zoom_filter(s["zoom"]) + ",setsar=1") if s.get("zoom") else ",scale=1080:1920:flags=lanczos,setsar=1"
    if kind == "freeze":
        vf = f"{GRADE},trim=end_frame=1,setpts=PTS-STARTPTS,fps={FPS},tpad=stop_mode=clone:stop_duration={s['dur'] + 1}{zf}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-i", src(s["clip"]), "-vf", vf]
    else:
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

def build_stills():
    """VS-card stills: Iqbal walking up (clip6 81.05 s), Farhan pointing on the tee (clip1 13.5 s)."""
    d = os.path.join(ROOT, "assets", "img"); os.makedirs(d, exist_ok=True)
    for name, clip, t in [("vs-iqbal", 6, 81.05), ("vs-farhan", 1, 13.50)]:
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", src(clip), "-frames:v", "1",
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
def load(clip):
    if clip not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src(clip), "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
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
    placed = []   # (clip, src_a, src_b, film_t): lets build_index map transcript word times onto the film
    def place(x, t, gain_db=0.0, src=None):
        i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * db(gain_db)
        if src: placed.append([src[0], round(src[1], 3), round(src[2], 3), round(t, 4)])
    def chain(clip, parts, t, gain_db=0.0, gap=0.07):
        """lay speech pieces end to end (pauses removed), return end time"""
        for a, b in parts:
            x = piece(clip, a, b); place(x, t, gain_db, (clip, a, b)); t += len(x) / SR + gap
        return t
    T = lambda n: tl[n]["start"]
    def sync(n, clip, g=0.0):
        s = next(x for x in EDL if x["name"] == n)
        place(piece(clip, s["a"], s["b"], 0.04), T(n), g, (clip, s["a"], s["b"]))
    # hook: chip, thud, "Astagfirullah" (natural)
    sync("hook_chip", 4, +2)
    # tee shots (natural, strikes in sync)
    sync("tee_far", 1, -1); sync("tee_iqb", 1, -1)
    # Iqbal's plan, pauses removed: "So, saya akan buat draw ... Kita aim kat bunker. Bagi dia curve masuk."
    # "1-5-4. ... kita ada branch kat depan tu. So, saya akan buat draw ... Supaya elak. Kita aim kat bunker. Bagi dia curve masuk."
    chain(2, [(0.20, 1.22), (7.00, 8.85), (12.58, 14.62), (18.24, 19.20), (19.90, 21.10), (22.10, 23.32)], T("iqb_plan") + 0.06, +3, gap=0.06)
    sync("iqb_swing", 2, 0)
    # verdict over the walk-up: "Buat a good shot. ... Tapi over sikit."
    chain(2, [(48.18, 49.20), (50.95, 52.10)], T("iqb_react") - 0.35, +3, gap=0.05)
    # Farhan's plan: "...middle, 150. ... pakai P, dengan bola kat belakang."
    chain(3, [(14.36, 16.20), (19.02, 21.25), (21.78, 23.15)], T("far_plan") - 0.05, +3, gap=0.06)
    sync("far_swing", 3, -1)
    # chip replay stays dry (music + sfx); diagnosis natural
    sync("chip_kenapa", 4, +3)       # "Kenapa jadi begitu?"
    sync("chip_why_a", 4, +3); sync("chip_why_b", 4, +3)
    sync("far_disaster", 5, +3)
    sync("far_putt", 5, +2)
    sync("far_bogey", 5, +3)
    # Iqbal's read over the push-in: "I think for birdie." "Fast, downhill putt. Left to right." "Back to back birdie."
    chain(6, [(0.84, 2.15), (3.50, 4.70), (17.40, 20.50), (22.58, 23.48)], T("iqb_read") + 0.05, +2)
    sync("iqb_roll", 6, +1)          # "Need to slow down, need to slow down" while it rolls
    sync("iqb_ok", 6, +2)            # "Okay, not too bad."
    sync("par_setup", 6, 0)
    place(piece(6, 75.30, 76.60, 0.03), T("par_drop"), +5, (6, 75.30, 76.60))   # "...save lah" right on the drop
    sync("next", 6, +6)              # "Next hole." (said walking up, quieter)
    tl["_voice"] = placed
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
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
    beats = {
        "hook_impact": film_time(tl, "hook_chip", 17.58),
        "hook_astag": film_time(tl, "hook_chip", 18.28),
        "far_tee_impact": film_time(tl, "tee_far", 4.75),
        "iqb_tee_impact": film_time(tl, "tee_iqb", 39.27),
        "iqb_app_impact": film_time(tl, "iqb_swing", 39.82),
        "far_app_impact": film_time(tl, "far_swing", 31.48),
        "chip_impact": film_time(tl, "chip_replay", 17.58),
        "far_putt_stroke": film_time(tl, "far_putt", 31.86),
        "iqb_stroke": film_time(tl, "iqb_roll", 27.25),
        "par_stroke": film_time(tl, "par_setup", 74.35),
        "par_drop": film_time(tl, "par_drop", 75.30),
    }
    tl["_beats"] = {k: round(v, 3) for k, v in beats.items()}
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print(json.dumps(tl, indent=1))
    if "--audio-only" not in sys.argv:
        build_stills()
        build_video()
    build_audio(tl)
