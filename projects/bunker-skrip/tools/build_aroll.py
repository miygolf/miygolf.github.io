#!/usr/bin/env python3
"""Bunker Shot (owner's script, ±40 s): cuts the owner's iPhone clips (1920x1080 HEVC 59.94 fps, rotated -90 -> upright 1080x1920) into one
30 fps A-roll (assets/aroll.mp4) and builds the sound track (assets/voice.wav) from the clips' own audio, placed explicitly.

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]

Clip map (large-v3 word times; on this phone they run ~0.3-0.5 s early, so every cut below was re-measured on the audio energy
and re-transcribed as a crop; picture checked on contact sheets):
  demo_top_n_skull  7.67 top, 8.43 impact (sand flies, ball stays in), 9.20-9.80 "Alamak."   32.3 top, 32.98 impact = skull
  IMG_0417          46.36-49.92 "Okey, rahsia dia, korang jangan pukul bola, korang pukul pasir." (close to the phone, face top of frame)
                    57.58-59.76 "korang kangkang besar-besar."   75.16-77.10 "cut sikit, so bagi dia open." ("grip ke logo" before it is cut, owner v3)
                    77.28-80.08 "Weight belah kiri, and then blast."   86.64-87.88 "korang buat satu line." (drawing the line, side-on)
                    91.06-92.20 "Tak payah pukul bola dulu."   97.86-98.74 "Contoh macam ni." swing, 100.09 impact on the line, 100.86-101.64 "Pukul line tu."
                    116.56-117.46 "Letak depan line." (rakes a ball in front of the line, 116.4-119.5 shown in full); 126.2-128.65 address + shot, impact 127.87   43.14-45.40 "Ataupun, top, skull." (voice over the skull)
  IMG_0419          12.0-16.9 club face held up to the phone (open face);  31.86 impact (its strike sound is used on IMG_0413)
  IMG_0413          2.67 top, 3.07 impact (sand splash, no sound on this clip), 3.33-5.9 pan to the green, 5.9-8.2 holds on the green:
                    the balls by the yellow flag (frame ~x 430-470 / y 1020, flag base x 572 / y 1080); earlier practice balls lie there too
  IMG_0418          1.64-6.42 "one more thing dalam pasir, korang jangan sentuh, club tu jangan sentuh pasir"  (cut before "sebab ni consider
                    penalty area": a bunker is not a penalty area; the rule is a 2-stroke penalty, shown on screen as in the owner's script)
                    13.24-16.50 "komen bunker kalau korang nak bola plug."
  Not used: IMG_0414/0415 (same shot as 0413), egg_fry (the next video), IMG_0417 0-45 (set-up chatter, camera too close).
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
C = {"demo": "demo_top_n_skull.MOV", "s17": "IMG_0417.MOV", "s18": "IMG_0418.MOV", "s19": "IMG_0419.MOV", "s13": "IMG_0413.MOV"}

# own = the segment's own sound plays; vo = extra (clip, a, b, offset-in-segment); mute = picture only
EDL = [
    dict(name="hook", clip="demo", a=7.45, b=10.10, own=True),                                  # fail: impact 8.43, "Alamak."
    dict(name="skull", clip="demo", a=31.70, b=34.20, own=False,
         vo=[("demo", 32.86, 33.40, 1.16), ("s17", 43.20, 45.62, 0.0)]),                      # skull strike + "Ataupun, top, skull."
    dict(name="rahsia", clip="s17", a=47.04, b=50.15, own=True),
    dict(name="face", clip="s19", a=12.40, b=14.80, own=False, vo=[("s17", 75.10, 77.36, 0.05)]),   # owner v3: "grip ke logo" (73.64-74.32) removed
    dict(name="stance", clip="s17", a=58.70, b=60.18, own=True),
    dict(name="weight", clip="s17", a=77.30, b=80.47, own=True),
    dict(name="line", clip="s17", a=86.88, b=88.10, own=True),
    dict(name="nobola", clip="s17", a=91.40, b=92.45, own=True),
    dict(name="contoh", clip="s17", a=97.98, b=101.85, own=True),
    dict(name="letak", clip="s17", a=116.40, b=119.45, own=True),            # owner v3: the ball set in front of the line, in full
    dict(name="letakshot", clip="s17", a=126.20, b=128.65, own=True),       # ... and the shot from there (impact 127.87, "Eh!")
    dict(name="shot", clip="s13", a=1.75, b=5.70, own=False, vo=[("s19", 31.80, 32.30, None)]),  # owner v2: IMG_0413 here (impact 3.07, pan to the green); it has no sound -> IMG_0419's real strike on the impact
    dict(name="slow", clip="s13", a=2.55, b=3.55, speed=0.5, own=False, vo=[("s19", 31.80, 32.30, None)]),  # strike placed on the impact
    dict(name="slow2", clip="s13", a=3.55, b=8.20, own=False),    # owner v4: follow the pan until the phone settles on the green (5.9) and hold
    dict(name="penalty", clip="s18", a=1.55, b=6.65, own=True),
    dict(name="cta", clip="s18", a=13.58, b=16.78, own=True),
    dict(name="end", clip="s18", a=16.74, kind="freeze", dur=1.6),
]
IMPACTS = {"hook": 8.43, "skull": 32.98, "contoh": 100.09, "letakshot": 127.87, "shot": 3.07, "slow": 3.07}
STRIKE = 31.86          # IMG_0419 impact transient: the real bunker strike laid on IMG_0413's silent impacts


def seg_dur(s):
    return s["dur"] if s.get("kind") == "freeze" else (s["b"] - s["a"]) / s.get("speed", 1.0)


def frames(d):
    return int(round(d * FPS))


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)); print(r.stderr[-3000:]); sys.exit(1)


def src(c):
    return os.path.join(SRC, C[c])


def build_segment(i, s):
    out = os.path.join(SEG, f"{i:02d}_{s['name']}.mp4")
    n = frames(seg_dur(s))
    enc = ["-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-g", "15", out]
    sc = "scale=1080:1920:flags=lanczos,setsar=1"
    if s.get("kind") == "freeze":
        vf = f"trim=end_frame=1,setpts=PTS-STARTPTS,fps={FPS},tpad=stop_mode=clone:stop_duration={s['dur'] + 1},{sc}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-i", src(s["clip"]), "-vf", vf]
    else:
        sp = s.get("speed", 1.0)       # 0.5x of 59.94 fps = every source frame once at 30 fps (no interpolation)
        vf = f"setpts=PTS/{sp},fps={FPS},{sc}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{s['b'] - s['a'] + 0.3:.3f}", "-i", src(s["clip"]), "-vf", vf]
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


def film_time(tl, name, src_t):
    s = next(x for x in EDL if x["name"] == name)
    return tl[name]["start"] + (src_t - s["a"]) / s.get("speed", 1.0)


_cache = {}
def load(c):
    if c not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src(c), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                             capture_output=True).stdout
        _cache[c] = np.frombuffer(raw, np.float32).copy()
    return _cache[c]


def piece(c, a, b, fade=0.02):
    x = load(c)[int(a * SR):int(b * SR)].copy()
    f = int(fade * SR)
    if f and len(x) > 2 * f:
        x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    return x


def build_audio(tl):
    total = tl["_total"]
    buf = np.zeros(int((total + 0.5) * SR), np.float32)
    placed = []
    def place(x, t, src=None):
        i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x
        if src: placed.append([src[0], round(src[1], 3), round(src[2], 3), round(t, 4)])
    for s in EDL:
        T = tl[s["name"]]["start"]
        if s.get("own"):
            place(piece(s["clip"], s["a"], s["b"]), T, (s["clip"], s["a"], s["b"]))
        for c, a, b, off in s.get("vo", []):
            if off is None:   # real strike on the slowed impact (picture first, sound peak one frame later)
                off = (IMPACTS[s["name"]] - s["a"]) / s.get("speed", 1.0) + 1 / FPS - (STRIKE - a)
            place(piece(c, a, b, 0.01), T + off, (c, a, b))
    tl["_voice"] = placed
    out = os.path.join(ROOT, "edit", "voice_raw.wav")
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(buf, -1, 1) * 32767).astype(np.int16).tobytes())
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af",
         "highpass=f=80,afftdn=nf=-40:nr=6,acompressor=threshold=-24dB:ratio=2.5:attack=8:release=200:makeup=2,"
         "loudnorm=I=-16:TP=-2:LRA=11", "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])


if __name__ == "__main__":
    tl = timeline()
    tl["_impacts"] = {k: round(film_time(tl, k, v), 3) for k, v in IMPACTS.items()}
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True); os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in tl.items() if k != "_voice"}, indent=0))
