#!/usr/bin/env python3
"""Early Extension (owner's script, ±40 s): cuts IMG_0448 (iPhone 1920x1080 HEVC 59.94 fps, rotated -90 -> upright 1080x1920, face-on
from the toe side, driving range, 3:04) into one 30 fps A-roll (assets/aroll.mp4) + the sound track (assets/voice.wav) from its own audio.

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]

Clip map (crop transcripts, large-v3, on the sound; energy; picture on contact sheets). The recording is noise-gated (silence = -180 dB).
  6.25-8.45   "Apa itu early extension?"
  14.75 addr, 15.40 top, 15.783 impact (picture; sound peak 15.80)   = swing 1, BEFORE the drills
  29.5-31.55 "First of all, dia angkat"  33.65-36.10 "backswing, dia naik badan."  37.3-40.1 "So, bila dia turun, dia turun je macam tu."
              (slow demonstration of the fault, no ball)
  89.55-92.65 "Buat slow-slow, backswing slow je."   (drill 1: foot back, slow backswing)
  102.62-104.55 "Ambil golf bag ataupun kerusi."   117-119.9 address with the chair behind him
  119.9-130.8 "Okay, kerusi ni sebagai kita nak dapatkan rasa je. Angkat backswing. Downswing tu bagi rasa, tolak je kerusi tu. Then follow through."
  132.9 addr, 134.007 impact = full swing with the chair
  174.6 addr, 175.668 impact = last swing (gripped down), AFTER the drills
  180.4-181.5 "Okay, itu dia."  (walks up to the phone)
Measured (upright frame, rows y 970-1030, leftmost trouser pixel = back of the hips): swing 1 address x ~24 -> impact ~110 (hips move ~85 px
towards the ball = early extension); last swing address ~40 -> impact ~65 (~25 px). Left frame edge is background, not trousers (not clipped).
No talking-head takes of script shots 2 and 6 and no wall in the footage: those lines are on screen; the drill shown is the chair (same feel).
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src", "IMG_0448.MOV")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
I1, I2, I3 = 15.783, 134.007, 175.668          # impacts (picture)
SND = {I1: 15.80, I2: 134.03, I3: 175.68}       # matching sound peaks

# split screen (before | after): each side = src crop x 0-860 / y 380-1730, scaled 0.628 -> 540x848, placed at film y 330
SPLIT = dict(cx=0, cy=380, cw=860, ch=1350, w=540, h=848, y=330)
PRE, POST = 0.43, 0.32

EDL = [
    dict(name="hook", a=14.75, b=15.40, own=True),
    dict(name="hookslow", a=15.40, b=I1, speed=0.5),
    dict(name="hookfreeze", a=I1, kind="freeze", dur=2.4, vo=[(6.25, 8.45, 0.1)]),         # "Apa itu early extension?"
    dict(name="hookpost", a=I1, b=16.25, speed=0.5),
    dict(name="demoA", a=29.50, b=31.55, own=True),
    dict(name="demoB", a=33.65, b=36.10, own=True),
    dict(name="demoC", a=37.30, b=40.10, own=True),
    dict(name="kerusi0", a=117.00, b=118.95, vo=[(102.62, 104.55, 0.0)]),                   # "Ambil golf bag ataupun kerusi."
    dict(name="kerusi", a=119.90, b=130.80, own=True),
    dict(name="slow", a=89.55, b=92.65, own=True),
    dict(name="chairhit", a=132.90, b=134.75, own=True),
    dict(name="splitpre", kind="split", a=I1 - PRE, a2=I3 - PRE, src_dur=PRE, speed=0.5),
    dict(name="splitfreeze", kind="splitfreeze", a=I1, a2=I3, dur=2.6),
    dict(name="splitpost", kind="split", a=I1, a2=I3, src_dur=POST, speed=0.5),
    dict(name="end", a=179.90, b=181.90, own=True),
    dict(name="hold", a=181.86, kind="freeze", dur=1.5),
]


def seg_dur(s):
    if s.get("kind") in ("freeze", "splitfreeze"): return s["dur"]
    if s.get("kind") == "split": return s["src_dur"] / s["speed"]
    return (s["b"] - s["a"]) / s.get("speed", 1.0)


def frames(d):
    return int(round(d * FPS))


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)); print(r.stderr[-3000:]); sys.exit(1)


SC = "scale=1080:1920:flags=lanczos,setsar=1"


def side(label, sp, freeze_dur=None):
    S = SPLIT
    base = f"[{label}:v]scale=1080:1920,crop={S['cw']}:{S['ch']}:{S['cx']}:{S['cy']},scale={S['w']}:{S['h']}:flags=lanczos"
    if freeze_dur is not None:
        return base + f",trim=end_frame=1,setpts=PTS-STARTPTS,fps={FPS},tpad=stop_mode=clone:stop_duration={freeze_dur + 1}[v{label}]"
    return base + f",setpts=PTS/{sp},fps={FPS}[v{label}]"


def build_segment(i, s):
    out = os.path.join(SEG, f"{i:02d}_{s['name']}.mp4")
    n = frames(seg_dur(s))
    enc = ["-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-g", "15", out]
    k = s.get("kind")
    if k in ("split", "splitfreeze"):
        fz = s["dur"] if k == "splitfreeze" else None
        sp = s.get("speed", 1.0)
        t = s.get("src_dur", 0.1) + 0.3
        fc = (side(0, sp, fz) + ";" + side(1, sp, fz) + f";[v0][v1]hstack=2,pad=1080:1920:0:{SPLIT['y']}:color=0x13202b,setsar=1[v]")
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{t:.3f}", "-i", SRC, "-ss", f"{s['a2']:.3f}", "-t", f"{t:.3f}", "-i", SRC,
               "-filter_complex", fc, "-map", "[v]"]
    elif k == "freeze":
        vf = f"trim=end_frame=1,setpts=PTS-STARTPTS,fps={FPS},tpad=stop_mode=clone:stop_duration={s['dur'] + 1},{SC}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-i", SRC, "-vf", vf]
    else:
        sp = s.get("speed", 1.0)       # 0.5x of 59.94 fps = every source frame once at 30 fps (no interpolation)
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{s['b'] - s['a'] + 0.3:.3f}", "-i", SRC, "-vf", f"setpts=PTS/{sp},fps={FPS},{SC}"]
    run(cmd + enc)
    return out, n


def build_video():
    from concurrent.futures import ThreadPoolExecutor
    os.makedirs(SEG, exist_ok=True)
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(lambda p: build_segment(*p), list(enumerate(EDL))))
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


_cache = {}
def load():
    if "x" not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-map", "0:a:0", "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
        _cache["x"] = np.frombuffer(raw, np.float32).copy()
    return _cache["x"]


def piece(a, b, fade=0.02):
    x = load()[int(a * SR):int(b * SR)].copy()
    f = int(fade * SR)
    if f and len(x) > 2 * f:
        x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    return x


def build_audio(tl):
    total = tl["_total"]
    buf = np.zeros(int((total + 0.5) * SR), np.float32)
    placed = []
    def place(x, t, src=None, gain=1.0):
        i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * gain
        if src: placed.append([round(src[0], 3), round(src[1], 3), round(t, 4)])
    for s in EDL:
        T = tl[s["name"]]["start"]
        if s.get("own"):
            place(piece(s["a"], s["b"]), T, (s["a"], s["b"]))
        for a, b, off in s.get("vo", []):
            place(piece(a, b), T + off, (a, b))
    # real strikes on the slowed impacts (picture first, sound peak one frame later)
    strike = lambda imp: piece(SND[imp] - 0.03, SND[imp] + 0.45, 0.004)
    place(strike(I1), tl["hookfreeze"]["start"] + 1 / FPS - 0.03, gain=0.9)
    place(strike(I1), tl["splitfreeze"]["start"] + 1 / FPS - 0.03, gain=0.8)
    place(strike(I3), tl["splitfreeze"]["start"] + 1 / FPS - 0.03 + 0.04, gain=0.8)
    tl["_voice"] = placed
    out = os.path.join(ROOT, "edit", "voice_raw.wav")
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(buf, -1, 1) * 32767).astype(np.int16).tobytes())
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af",
         "highpass=f=80,acompressor=threshold=-24dB:ratio=2.5:attack=8:release=200:makeup=2,loudnorm=I=-16:TP=-2:LRA=11",
         "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])


if __name__ == "__main__":
    tl = timeline()
    tl["_impacts"] = {"hook": tl["hookfreeze"]["start"], "chair": round(tl["chairhit"]["start"] + (I2 - 132.90), 3), "split": tl["splitfreeze"]["start"]}
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True); os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print({k: (v["start"], v["end"]) for k, v in tl.items() if not k.startswith("_")}, tl["_total"], tl["_impacts"])
