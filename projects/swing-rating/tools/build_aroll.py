#!/usr/bin/env python3
"""Cuts the four source clips (iPhone, 4K HEVC HLG 59.94 fps, upright 2160x3840, tripod, no speech) into one 1080x1920 30 fps A-roll
(assets/aroll.mp4) and the natural-sound track (assets/voice.wav). No colour grade (owner's standing preference: iPhone's own colour).

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]
Sources (tools/fetch.sh): order by recording time = before -> after
  clip3  09:50:20  BEFORE, down the line (open range)   address 134, takeaway 137, top 168, IMPACT 183, finish ~230 (frame @59.94)
  clip2  09:50:41  BEFORE, face on (bay 7)              address 8,   takeaway 10,  top 54,  IMPACT 69,  finish ~110
  clip4  10:00:14  AFTER,  face on (bay 7)              address 33,  takeaway 36,  top 84,  IMPACT 105, finish ~150
  clip1  10:25:28  AFTER,  down the line (open range)   address 48,  takeaway 51,  top 84,  IMPACT 100, finish ~170
Strike transients in the audio land ~0.025 s after the impact frame (3.08 / 1.17 / 1.78 / 1.69 s): audio is read AOFF later.
clip3 opens with ~2.2 s of standing over the ball (cut).
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
AOFF = 0.025
F = lambda n: n / 59.94                     # source frame -> seconds
IMP = {3: F(183), 1: F(100), 2: F(69), 4: F(105)}
TOP = {3: F(168), 1: F(84), 2: F(54), 4: F(84)}
CROP = {3: 150, 1: 90}                       # split-screen: x of the 540-wide window on the 1080 frame (DTL clips)

EDL = [
    # HOOK: both down-the-line swings side by side, synced into impact at 0.5x, freeze on impact (lines + "?" in the composition)
    dict(name="hook", kind="split", L=(3, IMP[3] - 0.46, IMP[3]), R=(1, IMP[1] - 0.46, IMP[1]), speed=0.5),
    dict(name="hook_frz", kind="splitfreeze", L=(3, IMP[3]), R=(1, IMP[1]), dur=2.6),
    # BEFORE
    dict(name="b_dtl", clip=3, a=2.05, b=3.95, speed=1.0),
    dict(name="b_slow", clip=3, a=2.70, b=IMP[3], speed=0.5),
    dict(name="b_frz", clip=3, a=IMP[3], kind="freeze", dur=3.3),
    dict(name="b_fo1", clip=2, a=0.00, b=TOP[2], speed=1.0),
    dict(name="b_fo_top", clip=2, a=TOP[2], kind="freeze", dur=2.7),
    dict(name="b_fo2", clip=2, a=TOP[2], b=2.40, speed=1.0),
    dict(name="b_card", clip=2, a=2.40, kind="freeze", dur=2.8),
    # AFTER
    dict(name="a_dtl", clip=1, a=0.66, b=2.90, speed=1.0),
    dict(name="a_slow", clip=1, a=1.33, b=IMP[1], speed=0.5),
    dict(name="a_frz", clip=1, a=IMP[1], kind="freeze", dur=3.3),
    dict(name="a_fo1", clip=4, a=0.45, b=TOP[4], speed=1.0),
    dict(name="a_fo_top", clip=4, a=TOP[4], kind="freeze", dur=2.6),
    dict(name="a_fo2", clip=4, a=TOP[4], b=2.85, speed=1.0),
    dict(name="a_card", clip=4, a=2.85, kind="freeze", dur=3.4),
    # PROOF: side by side at full speed, synced on impact, then the impact freeze with the numbers
    dict(name="proof", kind="split", L=(3, IMP[3] - 0.85, IMP[3] + 0.80), R=(1, IMP[1] - 0.85, IMP[1] + 0.80), speed=1.0),
    dict(name="proof_frz", kind="splitfreeze", L=(3, IMP[3] + 0.80), R=(1, IMP[1] + 0.80), dur=0.01),  # placeholder, dropped below
    # END: the after swing at full speed (back to camera at the finish), freeze for the scorecard + CTA
    dict(name="end_play", clip=1, a=0.66, b=3.36, speed=1.0),
    dict(name="end_frz", clip=1, a=3.36, kind="freeze", dur=4.4),
]
# proof freeze = impact freeze (numbers revealed), not the finish
EDL[[e["name"] for e in EDL].index("proof_frz")] = dict(name="proof_frz", kind="splitfreeze", L=(3, IMP[3]), R=(1, IMP[1]), dur=2.6)


def seg_dur(s):
    if s.get("kind") in ("freeze", "splitfreeze"):
        return s["dur"]
    if s.get("kind") == "split":
        return (s["L"][2] - s["L"][1]) / s["speed"]
    return (s["b"] - s["a"]) / s["speed"]


def frames(d):
    return int(round(d * FPS))


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)); print(r.stderr[-3000:]); sys.exit(1)


def src(clip):
    return os.path.join(SRC, f"clip{clip}.mov")


ENC = ["-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-g", "15"]


def build_segment(i, s):
    out = os.path.join(SEG, f"{i:02d}_{s['name']}.mp4")
    n = frames(seg_dur(s))
    k = s.get("kind")
    if k in ("split", "splitfreeze"):
        ins, fc = [], []
        for j, side in enumerate(("L", "R")):
            c, a = s[side][0], s[side][1]
            if k == "split":
                ins += ["-ss", f"{a:.4f}", "-t", f"{s[side][2] - a + 0.3:.4f}", "-i", src(c)]
                fc.append(f"[{j}:v]setpts=PTS/{s['speed']},fps={FPS},scale=1080:1920:flags=lanczos,crop=540:1920:{CROP[c]}:0,setsar=1[v{j}]")
            else:
                ins += ["-ss", f"{a:.4f}", "-i", src(c)]
                fc.append(f"[{j}:v]trim=end_frame=1,setpts=PTS-STARTPTS,fps={FPS},tpad=stop_mode=clone:stop_duration={s['dur'] + 1},"
                          f"scale=1080:1920:flags=lanczos,crop=540:1920:{CROP[c]}:0,setsar=1[v{j}]")
        fc.append("[v0][v1]hstack=inputs=2[v]")
        run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-frames:v", str(n), *ENC, out])
        return out, n
    sc = "scale=1080:1920:flags=lanczos,setsar=1"
    if k == "freeze":
        vf = f"trim=end_frame=1,setpts=PTS-STARTPTS,fps={FPS},tpad=stop_mode=clone:stop_duration={s['dur'] + 1},{sc}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.4f}", "-i", src(s["clip"]), "-vf", vf]
    else:
        # 0.5x of 59.94 fps = every source frame once at 30 fps (no interpolation)
        vf = f"setpts=PTS/{s['speed']},fps={FPS},{sc}"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.4f}", "-t", f"{s['b'] - s['a'] + 0.3:.4f}", "-i", src(s["clip"]), "-vf", vf]
    run(cmd + ["-frames:v", str(n)] + ENC + [out])
    return out, n


def build_video():
    from concurrent.futures import ThreadPoolExecutor
    os.makedirs(SEG, exist_ok=True)
    with ThreadPoolExecutor(4) as ex:
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
    a = s["L"][1] if s.get("kind") == "split" else s["a"]
    return tl[name]["start"] + (src_t - a) / s["speed"]


# ---------------- audio ----------------
_cache = {}
def load(clip):
    if clip not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src(clip), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                             capture_output=True).stdout
        _cache[clip] = np.frombuffer(raw, np.float32).copy()
    return _cache[clip]


def piece(clip, a, b, fade=0.03):
    x = load(clip)[max(0, int((a + AOFF) * SR)):int((b + AOFF) * SR)].copy()
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
        i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * db(gain_db)
    T = lambda n: tl[n]["start"]
    E = {s["name"]: s for s in EDL}
    tone = np.concatenate([piece(3, 0.30, 1.90, 0.08)] * 3)          # range ambience while he stands over the ball (no speech)
    def room(t0, t1, g=-4):
        n = int((t1 - t0) * SR); x = tone[:n].copy(); f = int(0.06 * SR); x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
        place(x, t0, g)
    def strike(clip, t, g=0.0):                                         # the real strike, re-used where the picture is slowed or frozen
        place(piece(clip, IMP[clip] - 0.06, IMP[clip] + 0.55, 0.01), t - 0.06, g)
    for n, s in E.items():
        k = s.get("kind")
        if k in ("freeze", "splitfreeze"):
            room(T(n), tl[n]["end"])
        elif k == "split":
            if s["speed"] == 1.0:
                place(piece(1, s["R"][1], s["R"][2]), T(n), -1)
                place(piece(3, s["L"][1], s["L"][2]), T(n), -5)
            else:
                room(T(n), tl[n]["end"])
        elif s["speed"] == 1.0:
            place(piece(s["clip"], s["a"], s["b"]), T(n), 0)
        else:
            room(T(n), tl[n]["end"])
    # strikes at the slowed impacts (the freeze starts on the impact frame)
    strike(1, tl["hook_frz"]["start"], -1); strike(3, tl["hook_frz"]["start"], -6)
    strike(3, tl["b_frz"]["start"], -2)
    strike(1, tl["a_frz"]["start"], -2)
    out = os.path.join(ROOT, "edit", "voice_raw.wav")
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    # no voice in these clips: just tame the wind rumble and level the range sound; strikes keep their transient
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af",
         "highpass=f=90,afftdn=nf=-40:nr=8,alimiter=limit=0.89:attack=1:release=60,loudnorm=I=-18:TP=-2:LRA=11",
         "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])


if __name__ == "__main__":
    tl = timeline()
    beats = {
        "hook_impact": tl["hook_frz"]["start"],
        "b_impact": film_time(tl, "b_dtl", IMP[3]), "b_slow_impact": tl["b_frz"]["start"],
        "b_fo_impact": film_time(tl, "b_fo2", IMP[2]),
        "a_impact": film_time(tl, "a_dtl", IMP[1]), "a_slow_impact": tl["a_frz"]["start"],
        "a_fo_impact": film_time(tl, "a_fo2", IMP[4]),
        "proof_impact": film_time(tl, "proof", IMP[3]),
        "end_impact": film_time(tl, "end_play", IMP[1]),
        "b_takeaway": film_time(tl, "b_dtl", F(137)), "a_takeaway": film_time(tl, "a_dtl", F(51)),
    }
    tl["_beats"] = {k: round(v, 3) for k, v in beats.items()}
    tl["_edl"] = [{k: v for k, v in s.items()} for s in EDL]
    tl["_crop"] = CROP
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True); os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print({k: v for k, v in tl.items() if k != "_edl"})
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
