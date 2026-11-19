#!/usr/bin/env python3
"""Before & after adjustment (Drive folder 1vAvvjHm1jcRnv-GNmpjir7cBmisdTn-b, 18 Nov 2026, range bay 32, night).
Cuts the takes and the coach's analysis screen recording into one 1080x1920 30 fps A-roll; builds the sound (takes' strikes + coach's voice-over).

Sources (.src/, tools/fetch.sh):
  IMG_0328 21:21 BEFORE down-the-line, 12.5 s: address ~9.0, top ~10.65, IMPACT 11.02 (sound 11.04)
  IMG_0330 21:22 BEFORE face-on, 5.4 s: IMPACT ~4.15 (sound 4.16)
  IMG_0331 21:39 AFTER down-the-line, 8.4 s: IMPACT 7.10 (sound 7.12)
  IMG_0333 21:39 AFTER face-on, 5.5 s: IMPACT ~4.28
  clip_m4v.m4v   the coach's analysis (screen recording, 105.6 s, voice-over): top panel = before, bottom = after, red plane line drawn by him.
     large-v3 (ms + en + crops): 6.6-10 "backswing angkat cantik je, on plane" · 31.0-35.8 "bila down swing tu, tangan tu di atas swing plane"
     · 80.3-85.4 "tengok, terangkat badan-badan, sebab bodi tak clear" · 53.4-58.4 "dia turun, dia dalam plane, so kita jadi shallow lah"
     · 62.6-63.8 "lepas tu lutut masuk" · 68.4-71.4 "kita tak adalah kes early extension tu" · 92.4-95.2 "after ni finishing cantik je"
     · 100.5-104.0 "banyak kan buat drill tu lah, yang saya tunjuk tadi tu kan" (over the face-on reps = the drill, owner's note)
     The coach says the student's name at 0.6-2.2, ~24.3 ("macam <name>"), ~64.3 and ~67.9: every cut avoids it (privacy).
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
GRADE = "null"
M = "clip_m4v.m4v"
IMP = {"IMG_0328": 11.02, "IMG_0331": 7.10, "IMG_0330": 4.15, "IMG_0333": 4.28}
SND = {"IMG_0328": 11.04, "IMG_0331": 7.12, "IMG_0330": 4.16, "IMG_0333": 4.30}
ZH = [(0, 1.0, 1080, 1920), (1, 1.04, 1080, 1960)]           # hook: full frame so the head sits below the title slate

EDL = [
    dict(name="hook_a", sec="hook", clip="IMG_0331", a=6.62, b=7.12, speed=0.5, zoom=ZH, voice=False),
    dict(name="hook_freeze", sec="hook", clip="IMG_0331", a=7.12, kind="freeze", dur=1.1, zoom=[(0, 1.04, 1080, 1960), (1.1, 1.07, 1080, 1980)], voice=False),
    # BEFORE take at 1x, real strike
    dict(name="b_swing", sec="before", clip="IMG_0328", a=9.60, b=12.40, speed=1.0),
    # coach's analysis: backswing fine on both
    dict(name="m_bs", sec="analysis_b", clip=M, a=7.30, b=10.20, speed=1.0, fit=True),
    # cause 1, cause 2 (the coach's words over his own lines)
    dict(name="m_c1", sec="analysis_b", clip=M, a=31.35, b=36.10, speed=1.0, fit=True),
    dict(name="m_c2", sec="analysis_b", clip=M, a=80.20, b=85.70, speed=1.0, fit=True),
    # AFTER take at 1x
    dict(name="a_swing", sec="after", clip="IMG_0331", a=5.80, b=8.30, speed=1.0),
    # fixes
    dict(name="m_f1", sec="analysis_a", clip=M, a=53.25, b=58.65, speed=1.0, fit=True),
    dict(name="m_f2a", sec="analysis_a", clip=M, a=62.45, b=63.80, speed=1.0, fit=True, fade=0.012),   # "masuk" ends 63.79 (glottal k); 63.80 = the "m" of "macam <student name>"
    dict(name="m_f2b", sec="analysis_a", clip=M, a=68.36, b=71.55, speed=1.0, fit=True),   # starts after "macam ni" (68.2)
    dict(name="m_f3", sec="analysis_a", clip=M, a=92.30, b=95.40, speed=1.0, fit=True),
    # HOMEWORK (owner: "front side to drill aka homework kena buat"): the face-on reps are the drill; the coach's line over them
    dict(name="fo_b", sec="drill", clip="IMG_0330", a=3.20, b=5.00, speed=1.0, voice=False),
    dict(name="fo_a", sec="drill", clip="IMG_0333", a=3.30, b=5.10, speed=1.0, voice=False),
    # the student's WhatsApp reply (name and photo blurred) over the after finish
    dict(name="testi", sec="testi", clip="IMG_0331", a=7.95, kind="freeze", dur=4.3, voice=False),
    # end: CTA
    dict(name="end_freeze", sec="end", clip="IMG_0331", a=7.95, kind="freeze", dur=3.0, voice=False),
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
    return os.path.join(SRC, clip if "." in clip else f"{clip}.MOV")


def build_segment(i, s):
    if s.get("kind") == "rev": s = dict(s)
    out = os.path.join(SEG, f"{i:02d}_{s['name']}.mp4")
    n = frames(seg_dur(s))
    enc = ["-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-g", "15", out]
    zf = ("," + zoom_filter(s["zoom"]) + ",setsar=1") if s.get("zoom") else ",scale=1080:1920:flags=lanczos,setsar=1"
    if s.get("fit"):   # the coach's analysis screen recording (920x1912, two stacked panels at x 150-770): fit the height, slate-black sides
        zf = ",crop=620:1912:150:0,scale=-2:1920:flags=lanczos,pad=1080:1920:(ow-iw)/2:0:color=0x141414,setsar=1"
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
    gm = seg_gain(M, 6.0, 100.0)                       # one gain for the whole voice-over (it is one recording)
    for s in EDL:
        if s.get("kind") == "freeze" or not s.get("voice", True):
            continue
        g = gm if s["clip"] == M else seg_gain(s["clip"], s["a"], s["b"])
        place(piece(s["clip"], s["a"], s["b"], s.get("fade", 0.03)), T(s["name"]), g, (s["clip"], s["a"], s["b"]))
    # hook: room tone + the real strike on the slowed impact (peak one frame after the picture)
    g31 = seg_gain("IMG_0331", 5.8, 8.3)
    place(piece("IMG_0331", 1.0, 2.6, 0.1), 0.0, g31 - 6)
    place(piece("IMG_0331", SND["IMG_0331"] - 0.03, SND["IMG_0331"] + 0.4, 0.004), film_time(tl, "hook_a", IMP["IMG_0331"]) + 1 / FPS - 0.03, g31)
    # drill: the coach's homework line over the face-on reps (their own strikes kept low under it)
    dw = (100.40, 104.25)
    place(piece(M, *dw, 0.03), T("fo_b") + 0.15, gm, (M, *dw))
    for n, c in (("fo_b", "IMG_0330"), ("fo_a", "IMG_0333")):
        s_ = next(x for x in EDL if x["name"] == n)
        place(piece(c, s_["a"], s_["b"], 0.05), T(n), seg_gain(c, s_["a"], s_["b"]) - 9)
    place(piece("IMG_0331", 1.0, 4.4, 0.1), T("testi"), g31 - 10)
    place(piece("IMG_0331", 1.0, 4.0, 0.1), T("end_freeze"), g31 - 10)
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
    tl["_sections"] = []
    last = None
    for s in EDL:
        if s["sec"] != last:
            tl["_sections"].append([s["sec"], tl[s["name"]]["start"]]); last = s["sec"]
    tl["_beats"] = {"hook_impact": round(film_time(tl, "hook_a", IMP["IMG_0331"]), 3),
                    "b_impact": round(film_time(tl, "b_swing", IMP["IMG_0328"]), 3),
                    "a_impact": round(film_time(tl, "a_swing", IMP["IMG_0331"]), 3),
                    "fob_impact": round(film_time(tl, "fo_b", IMP["IMG_0330"]), 3),
                    "foa_impact": round(film_time(tl, "fo_a", IMP["IMG_0333"]), 3)}
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True); os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print("total", tl["_total"]); print(tl["_sections"]); print(tl["_beats"])
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
