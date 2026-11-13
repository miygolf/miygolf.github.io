#!/usr/bin/env python3
"""Cuts the source clip (iPhone, 4K HEVC HLG 59.94 fps, upright 2160x3840) into one 1080x1920 30 fps A-roll (assets/aroll.mp4)
and builds the dialogue / natural-sound track (assets/voice.wav). The EDL below is the single source of truth: film times of every segment
and beat go to edit/timeline.json, which tools/build_index.py turns into graphics, captions and SFX.

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]

Clip map (downhill lie, handheld face-on; the coach = grey shirt, black cap; the person filming asks):
  0-10     camera finds the lie ("... downhill, uneven lie" 1.4-3.5, first word unclear) - cut
  10.80-13.74 "So lie dia ni menurun macam ni."  (camera walks in on the ball at his feet)
  14.3-17.0 unclear ("dah lah ... lie, kasi dekat bawah") - cut ;  17.58-18.46 "Nak buat apa?"
  19.60-23.12 coach: "Okay, the tendency normally, this kind of lie, memang bola pergi kiri."
  24.0-26.5 "Kiri satu hal, [draft / jauh / daft] satu hal." - second word unclear, cut
  30.95-35.74 "ball position tengah, saya maintain. Apa-apa jenis lie pun saya maintain tengah."  ("Operation/Cooperation tengah" in ms passes,
             "maintain the position in the middle" in en: ball position)
  36.20-37.54 "Pegang pendek."   37.62-39.6 "Then buat tu practice swing tu."
  39.78-44.76 "Korang kena make sure low point korang tu kat mana. Kena kat sini ke, kena kat sini ke kan."
  45.80-48.84 "Tapi cuba letak weight tu belah kaki kiri."  50.64-52.40 "So supaya kena bola direct." (large-v3 x3 "direct", medium "darat")
  55.2-60.1 "... kanan sikit ... kiri" - first word unclear ("aim"? "tekan"? "letak tim"), NOT used until the owner confirms
  address ~61.5, take-away 62.2, top 62.6, IMPACT 63.00 (picture; sound peak 63.03), finish 63.6, camera pans down the fairway 64-70
  Faces (film px): standing / address x 470-620 / y 480-640; finish x 450-560 / y 440-560.  Target = screen right (face-on, right-hander).
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
IMPACT = 63.00
SND = 63.03

GRADE = "null"

EDL = [
    # HOOK: the strike at 0.5x into the finish, freeze
    dict(name="hook_a", clip=1, a=62.55, b=63.05, speed=0.5),
    dict(name="hook_b", clip=1, a=63.05, b=63.65, speed=1.0),
    dict(name="hook_freeze", clip=1, a=63.65, kind="freeze", dur=1.1),
    # THE LIE
    dict(name="lie", clip=1, a=10.70, b=13.80, speed=1.0),
    dict(name="ask", clip=1, a=17.45, b=18.55, speed=1.0),
    # TENDENCY
    dict(name="tend", clip=1, a=19.55, b=23.20, speed=1.0),
    # STEP 1 ball position
    dict(name="s1", clip=1, a=30.95, b=35.80, speed=1.0),
    # STEP 2 grip down
    dict(name="s2", clip=1, a=36.05, b=37.56, speed=1.0),
    # STEP 3 practice swing, low point
    dict(name="s3", clip=1, a=37.58, b=45.05, speed=1.0),
    # STEP 4 weight left
    dict(name="s4a", clip=1, a=45.70, b=49.10, speed=1.0),
    dict(name="s4b", clip=1, a=50.55, b=52.60, speed=1.0),
    # THE SHOT 1x
    dict(name="shot", clip=1, a=61.40, b=64.30, speed=1.0),
    # follows the ball down the fairway
    dict(name="pan", clip=1, a=64.30, b=68.30, speed=2.0),
    # END card over the fairway
    dict(name="end_freeze", clip=1, a=69.80, kind="freeze", dur=3.6),
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
    total = tl["_total"]
    buf = np.zeros(int((total + 0.5) * SR), np.float32)
    placed = []
    def place(x, t, gain_db=0.0, src=None):
        i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * db(gain_db)
        if src: placed.append([src[0], round(src[1], 3), round(src[2], 3), round(t, 4)])
    T = lambda n: tl[n]["start"]
    for n in ("hook_b", "lie", "ask", "tend", "s1", "s2", "s3", "s4a", "s4b", "shot"):
        s = next(x for x in EDL if x["name"] == n)
        place(piece(1, s["a"], s["b"], 0.03), T(n), 0, (1, s["a"], s["b"]))
    hit = lambda: piece(1, SND - 0.03, SND + 0.30, 0.004)
    place(hit(), film_time(tl, "hook_a", IMPACT) + 1 / FPS - 0.03, 0)
    place(hit(), film_time(tl, "shot", IMPACT) + 1 / FPS - 0.03, 3)
    # room tone with no voice in it (the clip's last seconds carry "okay ... breathe" from behind the phone: owner asked to mute it)
    amb = piece(1, 27.10, 29.30, 0.1)
    place(amb[: int(1.0 * SR)], 0.0, -8)
    place(amb, T("hook_freeze"), -8)
    place(amb, T("pan"), -4)
    place(amb, T("end_freeze"), -6); place(amb, T("end_freeze") + 1.7, -8)
    tl["_voice"] = placed
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    out = os.path.join(ROOT, "edit", "voice_raw.wav")
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af",
         "highpass=f=90,afftdn=nf=-40:nr=5,equalizer=f=2800:t=q:w=1.2:g=2,acompressor=threshold=-24dB:ratio=3:attack=5:release=150:makeup=3,"
         "loudnorm=I=-16:TP=-2:LRA=9", "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])


if __name__ == "__main__":
    tl = timeline()
    beats = {
        "hook_impact": film_time(tl, "hook_a", IMPACT),
        "shot_impact": film_time(tl, "shot", IMPACT),
        "shot_takeaway": film_time(tl, "shot", 62.20),
        "w_menurun": film_time(tl, "lie", 12.66),
        "w_ask": film_time(tl, "ask", 17.58),
        "w_tendency": film_time(tl, "tend", 20.64),
        "w_kiri": film_time(tl, "tend", 22.76),
        "w_tengah": film_time(tl, "s1", 31.92),
        "w_pendek": film_time(tl, "s2", 37.14),
        "w_practice": film_time(tl, "s3", 38.64),
        "w_lowpoint": film_time(tl, "s3", 40.92),
        "w_weight": film_time(tl, "s4a", 47.76),
        "w_kakikiri": film_time(tl, "s4a", 48.54),
        "w_direct": film_time(tl, "s4b", 52.30),
    }
    tl["_beats"] = {k: round(v, 3) for k, v in beats.items()}
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print(json.dumps(tl, indent=1))
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
