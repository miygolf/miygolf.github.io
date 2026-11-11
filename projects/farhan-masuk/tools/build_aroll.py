#!/usr/bin/env python3
"""Cuts the three source clips (iPhone, 4K HEVC HLG 60 fps, upright) into one 1080x1920 30 fps A-roll (assets/aroll.mp4)
and builds the dialogue / natural-sound track (assets/voice.wav).
The EDL below is the single source of truth: film times of every segment and beat go to edit/timeline.json,
which tools/build_index.py turns into graphics, captions and SFX.

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]
Needs ffmpeg and numpy. Sources live in .src/clip1..3.mov (see tools/fetch.sh).

Clip map (Farhan = teal shirt, white cap; the narrator is the person filming):
  1 IMG_0058  tee shot with driver. Narrator 0.0-7.2: "(Si/Encik) Farhan ... Tengok dia boleh convert birdie ke ... bogey, kita tengok."
              waggles 3-11.5, takeaway 11.7, impact 12.43, finish 13.9
  2 IMG_0062  chip from the fringe by the bunker: reads/points 0-3, camera pans to the pin and back 3.5-6.3, address 6.5-12.9,
              contact 13.05, camera follows the ball to the pin 13.4-18.5. No speech (whisper's "Terima kasih kerana menonton" is a hallucination)
  3 IMG_0063  short putt: address 0-8.8, stroke 8.85, ball drops in the cup 10.25. Narrator "Tu nasib" 11.0-11.95,
              repeats "nasib tu, yang mana nasib" 12.4-13.2 (cut), Farhan picks the ball out of the cup 13.6-14.5, stands up facing the camera 15.0
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000

# No colour grade: the footage keeps the iPhone's own colour (owner's standing preference since match play hole 2).
GRADE = "null"

# EDL in film order.  kind: None (play), "freeze" (hold src a for dur)
# zoom = [(t_in_segment, zoom, cx, cy)] in source pixels (2160x3840), smoothstep between keys
EDL = [
    # HOOK: the putt rolling at the cup (real time, wide), cut in tight on the cup for 0.5x over the last 40 cm, freeze before it drops.
    # (a cut, not a push-in: a push would drag Farhan's head up through the bubbles)
    # The narrator's line from the tee ("Tengok dia boleh convert birdie ke... bogey, kita tengok.") runs over it.
    dict(name="hook_roll", clip=3, a=7.60, b=9.75, speed=1.0,
         zoom=[(0, 1.30, 1120, 1640), (2.15, 1.33, 1120, 1660)]),
    dict(name="hook_slow", clip=3, a=9.75, b=10.15, speed=0.5,
         zoom=[(0, 1.95, 1110, 2470), (0.8, 2.00, 1110, 2500)]),
    dict(name="hook_freeze", clip=3, a=10.15, kind="freeze", dur=1.85,
         zoom=[(0, 2.00, 1110, 2500), (1.85, 2.12, 1110, 2500)]),
    # TEE: "Farhan" walking onto the tee, then straight to the address (waggles cut), swing to the finish
    dict(name="tee_intro", clip=1, a=0.00, b=0.85, speed=1.0, zoom=[(0, 1.45, 900, 1950), (0.85, 1.48, 900, 1950)]),
    dict(name="tee_swing", clip=1, a=11.30, b=14.25, speed=1.0, zoom=[(0, 1.55, 860, 1960), (2.95, 1.62, 860, 1960)]),
    # CHIP: address -> contact -> the camera follows the ball up to the pin
    dict(name="chip", clip=2, a=11.95, b=15.75, speed=1.0, zoom=[(0, 1.12, 1080, 1920), (3.8, 1.12, 1080, 1920)]),
    # PUTT: full, ball drops at 10.25, "Tu nasib" (the repeat that follows is cut)
    dict(name="putt", clip=3, a=7.20, b=11.98, speed=1.0, zoom=[(0, 1.12, 1100, 1800), (4.78, 1.18, 1100, 1850)]),
    # Farhan picks the ball out of the cup, freeze on him standing up with it -> end card
    dict(name="pick", clip=3, a=13.62, b=15.00, speed=1.0, zoom=[(0, 1.10, 1080, 1800), (1.38, 1.12, 1080, 1800)]),
    dict(name="end_freeze", clip=3, a=15.00, kind="freeze", dur=3.30, zoom=[(0, 1.12, 1080, 1800), (3.3, 1.18, 1080, 1760)]),
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
    out = os.path.join(SEG, f"{i:02d}_{s['name']}.mp4")
    n = frames(seg_dur(s))
    enc = ["-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-g", "15", out]
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
    placed = []   # (clip, src_a, src_b, film_t): lets build_index map transcript word times onto the film
    def place(x, t, gain_db=0.0, src=None):
        i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * db(gain_db)
        if src: placed.append([src[0], round(src[1], 3), round(src[2], 3), round(t, 4)])
    T = lambda n: tl[n]["start"]
    E = lambda n: tl[n]["end"]
    SPEECH = +9     # the narrator is behind the phone and quiet: lift every spoken piece well above the course ambience
    AMB = -4
    # HOOK: course ambience of the putt (quiet), the narrator's line on top, the long pause after "ke" cut to 0.22 s
    place(piece(3, 7.60, 10.15, 0.05), T("hook_roll"), AMB - 4)
    place(piece(1, 3.02, 4.74), T("hook_roll") + 0.05, SPEECH, (1, 3.02, 4.74))          # "Tengok dia boleh convert birdie ke"
    place(piece(1, 6.06, 7.26), T("hook_roll") + 0.05 + 1.72 + 0.22, SPEECH, (1, 6.06, 7.26))   # "bogey, kita tengok."
    # TEE: "Farhan" (natural), swing with the real strike (the phone records sound late: lead it by ~0.07 s, measured on the transient)
    place(piece(1, 0.00, 0.85), T("tee_intro"), SPEECH - 2, (1, 0.00, 0.85))
    place(piece(1, 11.37, 14.25), T("tee_swing"), AMB + 2)
    # CHIP: natural sound
    place(piece(2, 11.95, 15.75), T("chip"), AMB + 2)
    # PUTT: natural up to the drop, then "Tu nasib" lifted
    place(piece(3, 7.20, 10.95), T("putt"), AMB + 3)
    place(piece(3, 10.95, 11.98), film_time(tl, "putt", 10.95), SPEECH, (3, 10.95, 11.98))
    # PICK: natural, and a tail of room tone under the freeze
    place(piece(3, 13.62, 15.00), T("pick"), AMB)
    tail = piece(3, 15.00, 15.84, 0.05); tail *= np.linspace(1, 0, len(tail)); place(tail, T("end_freeze"), AMB - 6)
    tl["_voice"] = placed
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    out = os.path.join(ROOT, "edit", "voice_raw.wav")
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af",
         "highpass=f=110,afftdn=nf=-40:nr=12,equalizer=f=2800:t=q:w=1.2:g=3,acompressor=threshold=-26dB:ratio=3:attack=6:release=160:makeup=3,"
         "loudnorm=I=-16:TP=-2:LRA=9",
         "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])

if __name__ == "__main__":
    tl = timeline()
    beats = {
        "hook_stroke": film_time(tl, "hook_roll", 8.85),
        "tee_impact": film_time(tl, "tee_swing", 12.43),
        "chip_contact": film_time(tl, "chip", 13.05),
        "putt_stroke": film_time(tl, "putt", 8.85),
        "putt_drop": film_time(tl, "putt", 10.25),
        "tu_nasib": film_time(tl, "putt", 11.02),
    }
    tl["_beats"] = {k: round(v, 3) for k, v in beats.items()}
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in tl.items()}, indent=1))
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
