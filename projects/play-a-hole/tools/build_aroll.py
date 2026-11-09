#!/usr/bin/env python3
"""Cuts the four source clips into one upright 1080x1920 30 fps A-roll (assets/aroll.mp4) and builds the
dialogue / natural-sound track (assets/voice.wav). The EDL below is the single source of truth: film times
of every beat are written to edit/timeline.json for the graphics and sound design in index.html.

Run from the project folder:  python3 tools/build_aroll.py
Needs ffmpeg and numpy. Sources live in .src/clip1..4.mp4 (see tools/fetch.sh).
"""
import json, os, subprocess, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000

# per-clip grade: clip1 (wide action cam) is already punchy, the iPhone clips are hazy
GRADE = {
    1: "eq=saturation=0.9:contrast=1.03",
    2: "eq=contrast=1.1:saturation=1.2:gamma=0.96,curves=all='0/0 0.25/0.22 0.75/0.76 1/0.97'",
    3: "eq=contrast=1.1:saturation=1.2:gamma=0.96,curves=all='0/0 0.25/0.22 0.75/0.76 1/0.97'",
    4: "eq=contrast=1.12:saturation=1.22:gamma=0.95,curves=all='0/0 0.25/0.21 0.75/0.75 1/0.96'",
}

# video EDL, in film order: (name, clip, src_in, src_out, speed) ; kind "freeze" holds src_in for `dur`; "reverse" plays backwards
EDL = [
    dict(name="hook_putt",   clip=4, a=10.25, b=13.00, speed=1.0,
         zoom=[(0.0, 1.0, 1080, 1920), (0.55, 1.0, 1080, 1920), (2.73, 1.8, 1308, 1690)]),
    dict(name="hook_freeze", clip=4, a=13.00, kind="freeze", dur=0.90, zoom=[(0, 1.8, 1308, 1690)]),
    dict(name="hook_rewind", clip=4, a=10.25, b=13.00, kind="reverse", dur=0.45),
    dict(name="tee",         clip=1, a=8.90,  b=12.60, speed=1.0),
    dict(name="app_1x",      clip=2, a=19.70, b=22.25, speed=1.0),
    dict(name="app_slow",    clip=2, a=22.25, b=22.80, speed=0.35),
    dict(name="app_finish",  clip=2, a=22.80, b=25.00, speed=1.0),
    dict(name="green",       clip=3, a=7.00,  b=14.70, speed=1.0),
    dict(name="putt_1x",     clip=4, a=8.60,  b=12.40, speed=1.0,
         zoom=[(0.0, 1.0, 1080, 1920), (2.2, 1.0, 1080, 1920), (3.8, 1.7, 1300, 1700)]),
    dict(name="putt_slow",   clip=4, a=12.40, b=13.35, speed=0.5,
         zoom=[(0.0, 1.7, 1300, 1700), (1.9, 2.2, 1308, 1675)]),
    dict(name="putt_react",  clip=4, a=13.35, b=15.10, speed=1.0,
         zoom=[(0.0, 2.2, 1308, 1675), (0.35, 2.2, 1308, 1675), (1.2, 1.0, 1080, 1920)]),
    dict(name="after",       clip=4, a=17.40, b=24.90, speed=1.0),
    dict(name="end_freeze",  clip=4, a=24.90, kind="freeze", dur=5.30),
]

def _lerp_expr(keys, idx):
    """piecewise smoothstep expression over keyframes [(t, value), ...]; T = output time in the segment"""
    expr = f"{keys[-1][1]}"
    for (t0, v0), (t1, v1) in reversed(list(zip(keys[:-1], keys[1:]))):
        u = f"clip((T-{t0})/{max(t1 - t0, 1e-3)},0,1)"
        seg = f"({v0}+({v1}-{v0})*{u}*{u}*(3-2*{u}))"
        expr = f"if(lt(T,{t1}),{seg},{expr})"
    expr = f"if(lt(T,{keys[0][0]}),{keys[0][1]},{expr})"
    return expr.replace("T", f"(on/{FPS})")

def zoom_filter(zk, sw=2160, sh=3840):
    """zk = [(t, zoom, cx, cy)] in source (upright 4K) pixels -> zoompan to 1080x1920, full source detail"""
    z = _lerp_expr([(k[0], k[1]) for k in zk], 0)
    cx = _lerp_expr([(k[0], k[2]) for k in zk], 0)
    cy = _lerp_expr([(k[0], k[3]) for k in zk], 0)
    return (f"zoompan=z='{z}':x='clip({cx}-iw/zoom/2,0,iw-iw/zoom)':y='clip({cy}-ih/zoom/2,0,ih-ih/zoom)'"
            f":d=1:s=1080x1920:fps={FPS}")

def seg_dur(s):
    if s.get("kind") in ("freeze", "reverse"):
        return s["dur"]
    return (s["b"] - s["a"]) / s["speed"]

def frames(d):
    return int(round(d * FPS))

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)); print(r.stderr[-3000:]); sys.exit(1)

def build_video():
    os.makedirs(SEG, exist_ok=True)
    lst = []
    for i, s in enumerate(EDL):
        out = os.path.join(SEG, f"{i:02d}_{s['name']}.mp4")
        src = os.path.join(SRC, f"clip{s['clip']}.mp4")
        n = frames(seg_dur(s))
        base = f"scale=1080:1920:flags=lanczos,setsar=1,{GRADE[s['clip']]}"
        if s.get("zoom"):
            base = f"{GRADE[s['clip']]}"
        kind = s.get("kind")
        if kind == "freeze":
            vf = f"{base},trim=end_frame=1,setpts=PTS-STARTPTS,fps={FPS},tpad=stop_mode=clone:stop_duration={s['dur'] + 1}"
            if s.get("zoom"): vf += "," + zoom_filter(s["zoom"]) + ",setsar=1"
            cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-i", src, "-vf", vf]
        elif kind == "reverse":
            sp = (s["b"] - s["a"]) / s["dur"]
            vf = f"{base},reverse,setpts=PTS/{sp:.5f},fps={FPS}"
            cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{s['b'] - s['a']:.3f}", "-i", src, "-vf", vf]
        else:
            vf = f"{base},setpts=PTS/{s['speed']},fps={FPS}"
            if s.get("zoom"): vf += "," + zoom_filter(s["zoom"]) + ",setsar=1"
            cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{s['b'] - s['a'] + 0.2:.3f}", "-i", src, "-vf", vf]
        cmd += ["-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", "-g", "15", out]
        run(cmd)
        lst.append(out)
        print(f"  seg {i:02d} {s['name']:<12} {n} frames")
    with open(os.path.join(SEG, "list.txt"), "w") as f:
        for p in lst:
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
    """film time of a source timestamp inside a 1x/slow segment"""
    s = next(x for x in EDL if x["name"] == name)
    return tl[name]["start"] + (src_t - s["a"]) / s["speed"]

# ---------------- audio ----------------
_cache = {}
def load(clip):
    if clip not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(SRC, f"clip{clip}.mp4"), "-vn", "-ac", "1", "-ar", str(SR),
                              "-f", "f32le", "-"], capture_output=True).stdout
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
    def place(x, t, gain_db=0.0):
        i = int(t * SR); buf[i:i + len(x)] += x[:max(0, len(buf) - i)] * db(gain_db)

    T = lambda n: tl[n]["start"]
    # hook: the coach's own question (clip3) over the putt, take sound under it
    place(piece(4, 10.25, 13.00, 0.08), T("hook_putt"), -8)
    place(piece(3, 14.75, 16.50), T("hook_putt") + 0.25, +4)
    # tee shot: take sound (strike ~0.08 s late on this camera -> nudge it early)
    place(piece(1, 8.98, 12.60, 0.06), T("tee"), -1)
    # approach: "117" line (said while walking up), take sound, real strike on the slow-mo contact, finish
    place(piece(2, 19.70, 22.30, 0.06), T("app_1x"), -3)
    place(piece(2, 3.72, 4.52), T("app_1x") + 0.30, +3)
    imp = film_time(tl, "app_slow", 22.49)
    place(piece(2, 22.40, 22.98, 0.01), imp - 0.09, 0)
    place(piece(2, 22.98, 24.45, 0.1), film_time(tl, "app_finish", 22.98) , -4)
    # green: the coach's read, pauses removed (POV shot, so the voice runs over continuous picture)
    t = T("green")
    for a, b in [(1.35, 4.95), (6.30, 7.10), (9.05, 10.05), (11.45, 13.75)]:
        x = piece(3, a, b, 0.03); place(x, t, +4); t += len(x) / SR
    # putt: take sound; slow-mo part stays dry (music + SFX); reaction from the real roll
    place(piece(4, 8.60, 12.40, 0.06), T("putt_1x"), -4)
    place(piece(4, 13.25, 15.10, 0.03), T("putt_react") - 0.10, -2)
    # after: "Such a good player" / "any tips for green reading, Coach Iqbal?" / "Green reading"
    place(piece(4, 17.40, 24.90, 0.06), T("after"), -1)
    out = os.path.join(ROOT, "edit", "voice_raw.wav")
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    import wave
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    # clean-up chain: rumble cut, gentle denoise, de-harsh, level the speech, then loudness ~ -16 LUFS
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af",
         "highpass=f=90,afftdn=nf=-30:nr=10,equalizer=f=3000:t=q:w=1.2:g=2,acompressor=threshold=-24dB:ratio=3:attack=8:release=180:makeup=4,"
         "loudnorm=I=-16:TP=-2:LRA=9",
         "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])

if __name__ == "__main__":
    tl = timeline()
    beats = {
        "hook_stroke": film_time(tl, "hook_putt", 10.45),
        "tee_top": film_time(tl, "tee", 10.03),
        "tee_impact": film_time(tl, "tee", 10.25),
        "app_takeaway": film_time(tl, "app_1x", 21.60),
        "app_top": film_time(tl, "app_slow", 22.30),
        "app_impact": film_time(tl, "app_slow", 22.49),
        "putt_stroke": film_time(tl, "putt_1x", 10.45),
        "putt_drop": film_time(tl, "putt_slow", 13.05),
        "q_start": film_time(tl, "after", 18.78),
        "q_end": film_time(tl, "after", 21.84),
    }
    tl["_beats"] = {k: round(v, 3) for k, v in beats.items()}
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print(json.dumps(tl, indent=1))
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
