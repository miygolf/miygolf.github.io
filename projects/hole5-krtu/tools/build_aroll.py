#!/usr/bin/env python3
"""Cuts the four source clips (iPhone, 4K HEVC 59.94 fps, upright 2160x3840) into one 1080x1920 30 fps A-roll (assets/aroll.mp4),
builds the voice / natural-sound track (assets/voice.wav) and edit/timeline.json for tools/build_index.py.

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]
Sources: .src/clip1..4.mov (tools/fetch.sh).

Clip map (transcripts: edit/transcript.txt + .work/tx2.log, Malay + English passes compared):
  clip1 (12 s)  hole-5 sign: "Par tiga, hole five." "Berapa distance?" "180."
  clip2 (68 s)  tee box: "Okay, come play with us. Lubang lima, par tiga, KRTU, 180 meter."
                TEAL player tee shot (impact 16.45), "Good line." 18.8, "Pendek sikit." 24.6 / "Sampai? ... Pendek sikit." 26.3-28.4
                GREY player: "... 180, pin belakang." 34.3-37.1, "Aku try pakai iron five eh." 43.2, impact 52.17, "Good swing." 53.1, "Center." 59.6
  clip3 (29 s)  TEAL from the fringe: "Putt for birdie." 4.3, "Nampak dia, slope banyak, right to left." 6.6-10.1,
                "Sejujurnya, make sure bola sampai." 11.5, practice strokes, putt 22.81, ball stops close to the pin (seen 26-28.6)
  clip4 (20 s)  GREY birdie putt: stroke 13.51, ball rolls up and stops just short-right of the hole (~17.3), "Sikit." 17.8
Audio and picture are in sync on these takes (impact frame = audio transient within a frame), so no offset.
Cut: walking, waiting, practice swings/strokes, repeated lines ("hole five" said three times, "pendek sikit" twice), the
close walk-by at the end of clip2, lines the two transcription passes could not agree on.
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
UP = 2  # sources are 2160x3840: zoom keys are written in 1080x1920 units and scaled by 2

GRADE = "null"  # no colour grade (house style)

# zoom keys: (t_in_segment, zoom, cx, cy) in 1080x1920 units; smoothstep between keys
G1 = (330, 1000)   # teal at the tee (head ~ 360,760 unzoomed)
G2 = (390, 1000)   # grey at the tee
EDL = [
    # HOOK: grey's birdie putt rolls up to the hole and stops, freeze ("Sikit.")
    dict(name="hook_roll", clip=4, a=15.95, b=17.35, speed=1.0, zoom=[(0, 1.15, 640, 900), (1.4, 1.35, 660, 960)]),
    dict(name="hook_freeze", clip=4, a=17.35, kind="freeze", dur=1.60, zoom=[(0, 1.35, 660, 960), (1.6, 1.55, 672, 995)]),
    # INTRO: "Okay, come play with us. Lubang lima, par tiga, KRTU, 180 meter." over the tee box, the sign cut in on "lubang lima"
    dict(name="intro", clip=2, a=0.00, b=2.30, speed=1.0),
    dict(name="sign", clip=1, a=0.30, b=3.30, speed=1.0, zoom=[(0, 1.0, 540, 960), (3.0, 1.1, 560, 900)]),
    # TEE 1 (teal): address, swing, ball away, "Good line."
    dict(name="tee1", clip=2, a=13.00, b=20.00, speed=1.0,
         zoom=[(0, 1.6, *G1), (3.3, 1.75, *G1), (4.4, 1.75, *G1), (7.0, 1.25, 420, 900)]),
    dict(name="tee1_slo", clip=2, a=16.20, b=16.75, speed=0.4, zoom=[(0, 2.3, 350, 1020), (1.375, 2.45, 350, 1040)]),
    dict(name="tee1_res", clip=2, a=24.40, b=25.75, speed=1.0, zoom=[(0, 1.5, 360, 960), (1.35, 1.55, 360, 960)]),
    # TEE 2 (grey): "180, pin belakang." / "Aku try pakai iron five eh." / swing / "Good swing." / slow replay / "Center."
    dict(name="tee2_pin", clip=2, a=34.20, b=37.15, speed=1.0, zoom=[(0, 1.6, *G2), (2.95, 1.65, *G2)]),
    dict(name="tee2_iron", clip=2, a=43.05, b=45.20, speed=1.0, zoom=[(0, 1.75, *G2), (2.15, 1.8, *G2)]),
    dict(name="tee2", clip=2, a=50.60, b=54.10, speed=1.0, zoom=[(0, 1.8, *G2), (1.6, 1.8, *G2), (3.5, 1.3, 460, 900)]),
    dict(name="tee2_slo", clip=2, a=51.95, b=52.50, speed=0.4, zoom=[(0, 2.4, 400, 1030), (1.375, 2.55, 400, 1050)]),
    dict(name="tee2_res", clip=2, a=58.40, b=61.00, speed=1.0, zoom=[(0, 1.3, 500, 1000), (2.6, 1.35, 500, 1000)]),
    # GREEN 1 (teal, from the fringe): the read (pauses removed, punch-ins hide the jumps), the putt, ball stops by the pin
    dict(name="g1_a", clip=3, a=4.15, b=5.40, speed=1.0, zoom=[(0, 1.0, 540, 960), (1.25, 1.03, 540, 960)]),
    dict(name="g1_b", clip=3, a=6.50, b=8.70, speed=1.0, zoom=[(0, 1.18, 520, 1000), (2.2, 1.2, 520, 1000)]),
    dict(name="g1_c", clip=3, a=9.15, b=10.40, speed=1.0, zoom=[(0, 1.0, 540, 960), (1.25, 1.0, 540, 960)]),
    dict(name="g1_d", clip=3, a=11.35, b=13.50, speed=1.0, zoom=[(0, 1.0, 540, 960), (2.15, 1.0, 540, 960)]),
    dict(name="g1_e", clip=3, a=15.80, b=16.85, speed=1.0, zoom=[(0, 1.0, 540, 960), (1.05, 1.03, 540, 960)]),
    dict(name="g1_putt", clip=3, a=21.95, b=25.10, speed=1.0, zoom=[(0, 1.1, 520, 1000), (1.2, 1.1, 520, 1000), (3.15, 1.0, 540, 960)]),
    dict(name="g1_ball", clip=3, a=25.80, b=28.55, speed=1.0, zoom=[(0, 1.3, 520, 860), (2.75, 1.7, 470, 840)]),
    # GREEN 2 (grey): address + stroke, pan, the roll in slow motion (every 60 fps frame), freeze on the stop, outro on the freeze
    dict(name="g2_setup", clip=4, a=8.60, b=13.70, speed=1.0, zoom=[(0, 1.2, 330, 1000), (5.1, 1.3, 330, 1000)]),
    dict(name="g2_pan", clip=4, a=13.70, b=15.95, speed=1.5, zoom=[(0, 1.0, 540, 960), (1.5, 1.1, 620, 900)]),
    dict(name="g2_roll", clip=4, a=15.95, b=17.35, speed=0.5, zoom=[(0, 1.1, 620, 900), (2.8, 1.45, 660, 970)]),
    dict(name="g2_freeze", clip=4, a=17.35, kind="freeze", dur=1.60, zoom=[(0, 1.45, 660, 970), (1.6, 1.55, 665, 985)]),
    dict(name="outro", clip=4, a=17.35, kind="freeze", dur=6.00, zoom=[(0, 1.55, 665, 985), (6.0, 1.67, 668, 997)]),
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
    return (f"zoompan=z='{z}':x='clip({cx}-iw/zoom/2,0,iw-iw/zoom)':y='clip({cy}-ih/zoom/2,0,ih-ih/zoom)'"
            f":d=1:s=1080x1920:fps={FPS}")


def seg_dur(s):
    return s["dur"] if s.get("kind") == "freeze" else (s["b"] - s["a"]) / s["speed"]


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
    enc = ["-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", "-g", "15", out]
    zf = ("," + zoom_filter(s["zoom"]) + ",setsar=1") if s.get("zoom") else ",scale=1080:1920:flags=lanczos,setsar=1"
    if s.get("kind") == "freeze":
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
    placed = []   # [clip, src_a, src_b, film_t]
    def place(x, t, gain_db=0.0, src_=None):
        i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * db(gain_db)
        if src_: placed.append([src_[0], round(src_[1], 3), round(src_[2], 3), round(t, 4)])
    T = lambda n: tl[n]["start"]
    def sync(n, g=0.0, a=None, b=None):
        s = next(x for x in EDL if x["name"] == n)
        a = s["a"] if a is None else a; b = s["b"] if b is None else b
        place(piece(s["clip"], a, b, 0.04), T(n) + (a - s["a"]) / s["speed"], g, (s["clip"], a, b))
    # hook: the roll is quiet; "Sikit." lands on the freeze
    place(piece(4, 17.70, 18.45), T("hook_freeze") + 0.02, +6, (4, 17.70, 18.45))
    # intro: "Okay, come play with us." then over the sign "Lubang lima, par tiga, KRTU, 180 meter."
    sync("intro", +1, 0.0, 1.95)
    place(piece(2, 2.25, 7.00), T("sign") + 0.05, +1, (2, 2.25, 7.00))
    # tee 1: natural sound in sync (strike 16.45, "Good line." 18.8); slow replay dry; "Sampai? ... Pendek sikit."
    sync("tee1", 0)
    sync("tee1_res", +2)
    # tee 2
    sync("tee2_pin", +2); sync("tee2_iron", +2); sync("tee2", 0); sync("tee2_res", +9)
    # green 1: the read, the putt, ambience
    for n in ["g1_a", "g1_b", "g1_c", "g1_d", "g1_e"]:
        sync(n, +2)
    sync("g1_putt", +1)
    # green 2: address + stroke in sync; the slow roll dry; "Sikit." on the freeze
    sync("g2_setup", +2)
    place(piece(4, 17.70, 18.45), T("g2_freeze") + 0.20, +6, (4, 17.70, 18.45))
    tl["_voice"] = placed
    out = os.path.join(ROOT, "edit", "voice_raw.wav")
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af",
         "highpass=f=90,afftdn=nf=-28:nr=12,equalizer=f=3000:t=q:w=1.2:g=2,acompressor=threshold=-26dB:ratio=3.5:attack=6:release=160:makeup=5,"
         "loudnorm=I=-16:TP=-2:LRA=8",
         "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])


if __name__ == "__main__":
    tl = timeline()
    tl["_beats"] = {
        "hook_stop": round(tl["hook_freeze"]["start"], 3),
        "tee1_impact": round(film_time(tl, "tee1", 16.45), 3),
        "tee1_slo_impact": round(film_time(tl, "tee1_slo", 16.45), 3),
        "tee2_impact": round(film_time(tl, "tee2", 52.17), 3),
        "tee2_slo_impact": round(film_time(tl, "tee2_slo", 52.17), 3),
        "g1_stroke": round(film_time(tl, "g1_putt", 22.81), 3),
        "g2_stroke": round(film_time(tl, "g2_setup", 13.51), 3),
        "g2_stop": round(tl["g2_freeze"]["start"], 3),
    }
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True)
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in tl.items() if k != "_voice"}, indent=1))
