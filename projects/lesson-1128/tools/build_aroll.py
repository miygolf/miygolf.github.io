#!/usr/bin/env python3
"""Lesson recap 28.11 (owner: "recap today lesson"): five swings from today's lessons (iPhone 1920x1080 HEVC 59.94 fps, rotated -90 ->
upright 1080x1920, recorded 12:09-17:38) cut into one 30 fps A-roll (assets/aroll.mp4) + the real sound (assets/voice.wav). No names.

Per swing: 1x from just before the takeaway to the finish (own sound), then a 0.5x replay through impact (every 60 fps frame, real strike laid
one frame after the picture). Hook = the cleanest strike (IMG_0494) into impact at 0.5x, freeze.
Impacts (picture) = strike onset - 0.045 s (the onsets sit ~0.05 s after the club reaches the ball on the frame strips).
Run from the project folder:  python3 tools/build_aroll.py [--audio-only]
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEG = os.path.join(ROOT, "edit", "segs")
FPS, SR = 30, 48000
ONSET = {"IMG_0474": 1.486, "IMG_0480": 0.763, "IMG_0485": 3.990, "IMG_0494": 2.259, "IMG_0505": 3.387}
IMP = {k: round(v - 0.045, 3) for k, v in ONSET.items()}
SWINGS = [("IMG_0474", 0.00, 2.90), ("IMG_0480", 0.00, 2.00), ("IMG_0485", 2.60, 5.60), ("IMG_0494", 0.75, 3.30), ("IMG_0505", 2.30, 4.95)]

EDL = [dict(name="hook", clip="IMG_0494", a=IMP["IMG_0494"] - 0.45, b=IMP["IMG_0494"], speed=0.5, strike=True),
       dict(name="hookfreeze", clip="IMG_0494", a=IMP["IMG_0494"], kind="freeze", dur=1.4)]
for i, (c, a, b) in enumerate(SWINGS, 1):
    EDL.append(dict(name=f"s{i}", clip=c, a=a, b=b, own=True))
    EDL.append(dict(name=f"r{i}", clip=c, a=IMP[c] - 0.28, b=IMP[c] + 0.22, speed=0.5, strike=True))
EDL.append(dict(name="end", clip="IMG_0505", a=4.30, kind="freeze", dur=2.8))     # end card on swing 5's finish (the take ends with a finger over the lens)


def src(c): return os.path.join(ROOT, ".src", c + ".MOV")
def dur(s): return s["dur"] if s.get("kind") == "freeze" else (s["b"] - s["a"]) / s.get("speed", 1.0)
def frames(d): return int(round(d * FPS))


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(" ".join(cmd)); print(r.stderr[-3000:]); sys.exit(1)


SC = "scale=1080:1920:flags=lanczos,setsar=1"


def build_segment(i, s):
    out = os.path.join(SEG, f"{i:02d}_{s['name']}.mp4"); n = frames(dur(s))
    enc = ["-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-g", "15", out]
    if s.get("kind") == "freeze":
        vf = f"trim=end_frame=1,setpts=PTS-STARTPTS,fps={FPS},tpad=stop_mode=clone:stop_duration={s['dur'] + 1},{SC}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-i", src(s["clip"]), "-vf", vf]
    else:
        sp = s.get("speed", 1.0)
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{s['b'] - s['a'] + 0.3:.3f}", "-i", src(s["clip"]),
               "-vf", f"setpts=PTS/{sp},fps={FPS},{SC}"]
    run(cmd + enc); return out


_cache = {}
def load(c):
    if c not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src(c), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
        _cache[c] = np.frombuffer(raw, np.float32).copy()
    return _cache[c]


def piece(c, a, b, fade=0.015):
    x = load(c)[max(0, int(a * SR)):int(b * SR)].copy(); f = int(fade * SR)
    if f and len(x) > 2 * f: x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    return x


def main():
    os.makedirs(SEG, exist_ok=True); os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    t = 0.0; tl = {}
    for s in EDL:
        d = frames(dur(s)) / FPS; tl[s["name"]] = {"start": round(t, 4), "end": round(t + d, 4)}; t += d
    tl["_total"] = round(t, 4)
    # film time of each impact (1x swings and slowed replays)
    imp = {}
    for s in EDL:
        if s.get("kind") == "freeze": continue
        ip = IMP[s["clip"]]
        if s["a"] <= ip <= s["b"] + 1e-3: imp[s["name"]] = round(tl[s["name"]]["start"] + (ip - s["a"]) / s.get("speed", 1.0), 3)
    imp["hook"] = tl["hookfreeze"]["start"]
    tl["_impacts"] = imp
    if "--audio-only" not in sys.argv:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(3) as ex: res = list(ex.map(lambda p: build_segment(*p), list(enumerate(EDL))))
        open(os.path.join(SEG, "list.txt"), "w").write("".join(f"file '{p}'\n" for p in res))
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(SEG, "list.txt"), "-c", "copy", os.path.join(ROOT, "assets", "aroll.mp4")])
    buf = np.zeros(int((t + 0.6) * SR), np.float32)
    def place(x, at, g=1.0):
        i = int(at * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * g
    for s in EDL:
        T = tl[s["name"]]["start"]
        if s.get("own"): place(piece(s["clip"], s["a"], s["b"]), T)
        if s.get("strike"):     # the real strike on the slowed impact: picture first, sound onset one frame later
            c = s["clip"]; at = imp["hook"] if s["name"] == "hook" else imp[s["name"]]
            place(piece(c, ONSET[c] - 0.02, ONSET[c] + 0.45, 0.004), at + 1 / FPS - 0.02, 0.9)
    raw = os.path.join(ROOT, "edit", "voice_raw.wav")
    with wave.open(raw, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(buf, -1, 1) * 32767).astype(np.int16).tobytes())
    run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "highpass=f=60,acompressor=threshold=-22dB:ratio=2:attack=5:release=150:makeup=2,loudnorm=I=-16:TP=-2:LRA=11",
         "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print({k: (v["start"], v["end"]) for k, v in tl.items() if not k.startswith("_")}); print(tl["_total"], tl["_impacts"])


if __name__ == "__main__":
    main()
