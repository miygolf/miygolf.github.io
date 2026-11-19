#!/usr/bin/env python3
"""Kinrara Golf recap, 19 Nov 2026 (Drive folder 1JaOAR5R1cVyvUQVPdNlqJBex6J4nSiA_). One 1080x1920 30 fps A-roll in shooting order.
Players (owner's names): Coach Reza = black shirt; Kimi = blue shirt, navy bucket hat; owner ("me", label SAYA) = blue patterned shirt, black cap;
Taza = dark shirt, white bucket hat, knee brace.
  IMG_0338 14:25 owner's approach (DTL), impact 8.08          IMG_0344 14:33 owner's putt: rolls in ~2.85, picks it out of the cup
  c1_1..4  14:55 tee (palm tree): Reza, owner, Taza, Kimi     c2_1..4  15:04 next tee: Taza, Reza, Kimi, owner
No speech in any clip (large-v3: only end-of-silence hallucinations) -> cut on picture beats.
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
GRADE = "null"
ZC = [(0, 1.45, 920, 2900), (0.75, 1.55, 860, 2960)]          # hook: on the putter, ball and cup (cup ~ (720, 3160) source px)

# who: player key shown on the badge
EDL = [
    dict(name="hook_a", sec="hook", clip="IMG_0344", a=1.95, b=2.90, speed=0.5, zoom=ZC, voice=False),
    dict(name="hook_freeze", sec="hook", clip="IMG_0344", a=2.90, kind="freeze", dur=1.0, zoom=[(0, 1.55, 860, 2960), (1, 1.6, 850, 2970)], voice=False),
    dict(name="appr", sec="appr", clip="IMG_0338", a=6.70, b=9.80, speed=1.0, who="me"),
    dict(name="putt", sec="putt", clip="IMG_0344", a=0.30, b=4.70, speed=1.0, who="me"),
    dict(name="t1_reza", sec="tee1", clip="c1_1.mp4", a=0.00, b=3.00, speed=1.0, who="reza"),
    dict(name="t1_me", sec="tee1", clip="c1_2.mp4", a=5.30, b=7.70, speed=1.0, who="me"),
    dict(name="t1_taza", sec="tee1", clip="c1_3.mp4", a=0.40, b=3.70, speed=1.0, who="taza"),
    dict(name="t1_kimi", sec="tee1", clip="c1_4.mp4", a=0.00, b=3.06, speed=1.0, who="kimi"),
    dict(name="t2_taza", sec="tee2", clip="c2_1.mp4", a=3.40, b=5.70, speed=1.0, who="taza"),
    dict(name="t2_reza", sec="tee2", clip="c2_2.mp4", a=0.00, b=2.13, speed=1.0, who="reza"),
    dict(name="t2_kimi", sec="tee2", clip="c2_3.mp4", a=0.00, b=2.43, speed=1.0, who="kimi"),
    dict(name="t2_me", sec="tee2", clip="c2_4.mp4", a=0.00, b=1.66, speed=1.0, who="me"),
    dict(name="end_freeze", sec="end", clip="IMG_0344", a=4.70, kind="freeze", dur=3.2, voice=False),
]
IMPACTS = {"appr": 8.08, "t1_reza": 1.14, "t1_me": 7.21, "t1_taza": 2.04, "t1_kimi": 1.42, "t2_taza": 4.69, "t2_reza": 1.15, "t2_kimi": 1.43, "t2_me": 1.14}
DROP = 2.85     # putt drops (IMG_0344)

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
    for s in EDL:
        if s.get("kind") == "freeze" or not s.get("voice", True):
            continue
        place(piece(s["clip"], s["a"], s["b"], 0.03), T(s["name"]), seg_gain(s["clip"], s["a"], s["b"]), (s["clip"], s["a"], s["b"]))
    g = seg_gain("IMG_0344", 0.3, 4.7)
    place(piece("IMG_0344", 0.3, 1.8, 0.1), 0.0, g - 4)                       # green quiet under the slow drop (no loop)
    place(piece("IMG_0344", 4.70, 5.95, 0.1), T("end_freeze"), g - 4)
    place(piece("IMG_0338", 0.3, 2.3, 0.1), T("end_freeze") + 1.2, seg_gain("IMG_0338", 6.7, 9.8) - 10)
    tl["_voice"] = placed
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    out = os.path.join(ROOT, "edit", "voice_raw.wav")
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af", "highpass=f=70,afftdn=nf=-42:nr=4,loudnorm=I=-16:TP=-2:LRA=11",
         "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])


if __name__ == "__main__":
    tl = timeline()
    tl["_who"] = [[s["name"], s["who"]] for s in EDL if s.get("who")]
    tl["_sections"] = []
    last = None
    for s in EDL:
        if s["sec"] != last:
            tl["_sections"].append([s["sec"], tl[s["name"]]["start"]]); last = s["sec"]
    b = {k + "_impact": round(film_time(tl, k, v), 3) for k, v in IMPACTS.items()}
    b["hook_drop"] = round(film_time(tl, "hook_a", DROP), 3); b["putt_drop"] = round(film_time(tl, "putt", DROP), 3)
    tl["_beats"] = b
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True); os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print("total", tl["_total"]); print(tl["_sections"])
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
