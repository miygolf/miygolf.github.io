#!/usr/bin/env python3
"""Compilation: one round at Templer Park, 13 Nov 2026 (07:40-11:36), from the owner's Drive folder 1kptuZSNf8-Zq_3cTnAplmOHGZtOv1p4J.
Cuts every round clip into one 1080x1920 30 fps A-roll (assets/aroll.mp4) in shooting order, with each segment's own sound (assets/voice.wav).
The EDL is the single source of truth; tools/build_index.py turns edit/timeline.json into chapter tabs, captions and SFX.

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]   (sources: tools/fetch.sh)

Clips used (record time +08:00):
  IMG_0176 07:40 chipping tips (coach face-on)            IMG_0188 08:27 coach duffs a pitch, laughs
  IMG_0192 08:54 "Jangan gerak, kita nak hantar pin..."   IMG_0193 09:00 bunker stock shot, rolls past the cup
  IMG_0203 10:01 downhill lie lesson                       IMG_0205 10:12 tee shots in the mist
  IMG_0206 10:19 "KD cakap 80 meter"                        IMG_0211 11:05 chip-in bet RM50, "tak dapat"
  IMG_0214 11:30 ground-level divot cam (landscape: cropped 9:16)
  IMG_0215 11:32 scenery pan (title + hook bed)            IMG_0216 11:36 "Iconic hole, Templer Park, 18", tee shot
Not used: IMG_0213 (putting, too far to read), IMG_0187 (lie close-up, nothing new), IMG_0041 (9 Nov, another course),
          IMG_5564 / IMG_6392 / IMG_6411 (other golfers at ranges, Oct / early Nov).
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
GRADE = "null"
W13 = [(0, 1.3, 1180, 2400), (1, 1.3, 1180, 2400)]

# ch = chapter key (build_index shows a tab when it changes); voice=False: no own sound (bed placed in build_audio)
EDL = [
    dict(name="hook_a", ch="hook", clip="IMG_0193", a=22.50, b=22.86, speed=0.5, zoom=[(0, 1.25, 1150, 2350), (0.72, 1.3, 1180, 2400)], voice=False),
    dict(name="hook_freeze", ch="hook", clip="IMG_0193", a=22.86, kind="freeze", dur=1.6, zoom=[(0, 1.3, 1180, 2400), (1.6, 1.36, 1185, 2420)], voice=False),
    dict(name="title", ch="title", clip="IMG_0215", a=0.0, b=3.2, speed=1.0, gain_adj=-8),
    # 1 chipping 07:40
    dict(name="c1a", ch="chip", clip="IMG_0176", a=4.72, b=7.10, speed=1.0),
    dict(name="c1b", ch="chip", clip="IMG_0176", a=7.85, b=9.42, speed=1.0),
    dict(name="c1c", ch="chip", clip="IMG_0176", a=9.75, b=11.05, speed=1.0),
    dict(name="c1d", ch="chip", clip="IMG_0176", a=15.32, b=17.75, speed=1.0),
    dict(name="c1s", ch="chip", clip="IMG_0176", a=18.70, b=20.40, speed=1.0),
    # 2 coach duff 08:27
    dict(name="d_ff", ch="duff", clip="IMG_0188", a=5.90, b=21.30, speed=7.0, voice=False),
    dict(name="d_shot", ch="duff", clip="IMG_0188", a=21.30, b=23.50, speed=1.0),
    dict(name="d_laugh", ch="duff", clip="IMG_0188", a=25.30, b=26.95, speed=1.0),
    # 3 hantar pin 08:54
    dict(name="p_q", ch="pin", clip="IMG_0192", a=5.80, b=8.70, speed=1.0),
    dict(name="p_shot", ch="pin", clip="IMG_0192", a=20.20, b=22.80, speed=1.0),
    # 4 bunker 09:00
    dict(name="b_q", ch="bunker", clip="IMG_0193", a=0.00, b=3.95, speed=1.0),
    dict(name="b_plan", ch="bunker", clip="IMG_0193", a=9.42, b=12.96, speed=1.0),
    dict(name="b_shot", ch="bunker", clip="IMG_0193", a=19.50, b=21.05, speed=1.0),
    dict(name="b_whip", ch="bunker", clip="IMG_0193", a=21.05, b=22.45, speed=2.0, voice=False),
    dict(name="b_roll", ch="bunker", clip="IMG_0193", a=22.45, b=24.40, speed=1.0),
    # 5 downhill 10:01
    dict(name="h_lie", ch="downhill", clip="IMG_0203", a=10.70, b=13.80, speed=1.0),
    dict(name="h_tend", ch="downhill", clip="IMG_0203", a=19.55, b=23.20, speed=1.0),
    dict(name="h_pos", ch="downhill", clip="IMG_0203", a=30.95, b=35.80, speed=1.0),
    dict(name="h_grip", ch="downhill", clip="IMG_0203", a=36.05, b=37.56, speed=1.0),
    dict(name="h_w", ch="downhill", clip="IMG_0203", a=45.70, b=49.10, speed=1.0),
    dict(name="h_shot", ch="downhill", clip="IMG_0203", a=61.40, b=64.30, speed=1.0),
    # 6 tee shots in the mist 10:12
    dict(name="t1", ch="tee", clip="IMG_0205", a=14.00, b=17.40, speed=1.0),
    dict(name="t2", ch="tee", clip="IMG_0205", a=41.80, b=45.30, speed=1.0),
    # 7 80 meter 10:19
    dict(name="k_q", ch="m80", clip="IMG_0206", a=0.00, b=2.50, speed=1.0),
    dict(name="k_shot", ch="m80", clip="IMG_0206", a=29.60, b=32.40, speed=1.0),
    # 8 RM50 11:05
    dict(name="r_bet", ch="rm50", clip="IMG_0211", a=1.30, b=7.30, speed=1.0),
    dict(name="r_shot", ch="rm50", clip="IMG_0211", a=15.80, b=17.50, speed=1.0),
    dict(name="r_friend", ch="rm50", clip="IMG_0211", a=26.40, b=28.70, speed=1.0),
    # 9 divot cam 11:30 (landscape source, centre-crop 9:16 on the feet and the turf)
    dict(name="g_a", ch="divot", clip="IMG_0214", a=20.40, b=21.15, speed=1.0, crop=(1500, 1215)),
    dict(name="g_slow", ch="divot", clip="IMG_0214", a=21.15, b=21.85, speed=0.5, crop=(1500, 1215), voice=False),
    dict(name="g_b", ch="divot", clip="IMG_0214", a=21.85, b=23.20, speed=1.0, crop=(1500, 1215)),
    # 10 hole 18 11:36
    dict(name="i_q", ch="h18", clip="IMG_0216", a=4.50, b=7.40, speed=1.0),
    dict(name="i_shot", ch="h18", clip="IMG_0216", a=10.60, b=14.40, speed=1.0),
    dict(name="end_freeze", ch="end", clip="IMG_0216", a=14.40, kind="freeze", dur=3.6, voice=False),
]
IMPACTS = {"b_shot": 20.74, "d_shot": 22.15, "c1s": 19.22, "h_shot": 63.00, "r_shot": 16.62, "i_shot": 11.92, "t2": 43.41, "t1": 15.82,
           "k_shot": 30.56, "g_a": 21.19}

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
    return os.path.join(SRC, f"{clip}.MOV")


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
    """Level each segment so its loud 100 ms frames (90th pct) sit near -24 dBFS, capped at +-10 dB."""
    x = load(clip)[int(a * SR):int(b * SR)]
    if len(x) < SR // 10: return 0.0
    h = SR // 10
    r = np.array([np.sqrt(np.mean(x[i:i + h] ** 2)) + 1e-9 for i in range(0, len(x) - h, h)])
    lvl = 20 * np.log10(np.percentile(r, 90))
    return float(np.clip(-24 - lvl, -10, 10))


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
        g = seg_gain(s["clip"], s["a"], s["b"]) + s.get("gain_adj", 0)
        place(piece(s["clip"], s["a"], s["b"], 0.03), T(s["name"]), g, (s["clip"], s["a"], s["b"]))
    # beds for the silent-speed segments: real sound at 1x, never looped
    place(piece("IMG_0215", 3.2, 5.6, 0.1), 0.0, seg_gain("IMG_0215", 0, 7) - 8)                # hook
    place(piece("IMG_0188", 5.9, 8.2, 0.1), T("d_ff"), seg_gain("IMG_0188", 5.9, 8.2) - 8)     # fast-forward
    place(piece("IMG_0193", 21.05, 21.80, 0.05), T("b_whip"), seg_gain("IMG_0193", 21.05, 21.8))
    g14 = seg_gain("IMG_0214", 18.0, 23.2)
    place(piece("IMG_0214", 18.6, 20.0, 0.1), T("g_slow"), g14 - 6)
    snd = 21.19
    place(piece("IMG_0214", snd - 0.03, snd + 0.35, 0.004), film_time(tl, "g_slow", 21.19) - 0.03 + 1 / FPS, g14)
    place(piece("IMG_0216", 15.2, 18.8, 0.1), T("end_freeze"), seg_gain("IMG_0216", 15.2, 18.8) - 8)
    # the coach's quiet "stock shot" line, as in bunker-raw
    i0, i1 = int(film_time(tl, "b_plan", 11.90) * SR), int(film_time(tl, "b_plan", 12.92) * SR)
    ramp = np.ones(i1 - i0, np.float32) * db(9); f = int(0.04 * SR); ramp[:f] = np.linspace(1, db(9), f); ramp[-f:] = np.linspace(db(9), 1, f)
    buf[i0:i1] *= ramp
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
    tl["_chapters"] = []
    last = None
    for s in EDL:
        if s["ch"] != last:
            tl["_chapters"].append([s["ch"], tl[s["name"]]["start"]]); last = s["ch"]
    tl["_beats"] = {k + "_impact": round(film_time(tl, k, v), 3) for k, v in IMPACTS.items()}
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print("total", tl["_total"]); print(tl["_chapters"])
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
