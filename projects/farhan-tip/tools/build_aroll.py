#!/usr/bin/env python3
"""Coach Farhan tips: cuts one source clip (iPhone 1920x1080 HEVC 59.94 fps, rotated -90 -> upright 1080x1920, KL Golf & Country Club range)
into a 30 fps A-roll (assets/aroll.mp4) + sound (assets/voice.wav). The pieces (source ranges, chosen on crop transcripts) come from
content.py in the project folder (PIECES, SRC). Inside each piece, pauses longer than 0.5 s are shortened to ~0.3 s (jump cut, the speech
and every phrase ending kept: 0.16 s kept after the last sound, 0.12 s before the next). Writes edit/timeline.json with the src->film map.
Run from the project folder:  python3 ../farhan-tip/tools/build_aroll.py   (or tools/build_aroll.py)
"""
import json, os, subprocess, sys, wave, importlib.util
import numpy as np

PROJ = os.getcwd()
spec = importlib.util.spec_from_file_location("content", os.path.join(PROJ, "content.py")); C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
SRCS = sorted({p.get("src", C.SRC) for p in C.PIECES})      # pieces may come from several clips (piece key "src")
SEG = os.path.join(PROJ, "edit", "segs")
FPS, SR = 30, 48000


def path(src): return os.path.join(PROJ, ".src", src)


def load(src):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path(src), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


H = int(0.02 * SR)
AUD = {}
for _s in SRCS:
    _x = load(_s); _db = np.array([20 * np.log10(np.sqrt(np.mean(_x[i * H:(i + 1) * H] ** 2)) + 1e-9) for i in range(len(_x) // H)])
    AUD[_s] = (_x, _db, np.percentile(_db, 10) + 8)


def subsegments(src, a, b):
    X, DB, THR = AUD[src]
    """split [a,b] at pauses > 0.5 s (under floor + 8 dB): keep 0.16 s after the sound, 0.12 s before the next"""
    out, cur = [], a
    i, j0 = int(a / 0.02), int(b / 0.02)
    while i < j0:
        if DB[i] < THR:
            j = i
            while j < j0 and DB[j] < THR: j += 1
            if (j - i) * 0.02 > 0.5 and i * 0.02 > a + 0.1 and j < j0:
                out.append((cur, round(i * 0.02 + 0.16, 2))); cur = round(j * 0.02 - 0.12, 2)
            i = j
        else:
            i += 1
    out.append((cur, b))
    return out


SEGS = []
for p in C.PIECES:
    src = p.get("src", C.SRC)
    for k, (a, b) in enumerate(subsegments(src, p["a"], p["b"])):
        SEGS.append(dict(name=f"{p['name']}{k}", piece=p["name"], src=src, a=a, b=b))
if getattr(C, "HOLD", 0):
    SEGS.append(dict(name="hold", piece="hold", src=SEGS[-1]["src"], a=SEGS[-1]["b"] - 0.04, kind="freeze", dur=C.HOLD))


def frames(d): return int(round(d * FPS))
def dur(s): return s["dur"] if s.get("kind") == "freeze" else s["b"] - s["a"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(" ".join(cmd)); print(r.stderr[-3000:]); sys.exit(1)


SC = "scale=1080:1920:flags=lanczos,setsar=1"


def build_segment(i, s):
    out = os.path.join(SEG, f"{i:02d}_{s['name']}.mp4"); n = frames(dur(s))
    enc = ["-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-g", "15", out]
    if s.get("kind") == "freeze":
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-i", path(s["src"]), "-vf", f"trim=end_frame=1,setpts=PTS-STARTPTS,fps={FPS},tpad=stop_mode=clone:stop_duration={s['dur'] + 1},{SC}"]
    else:
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{s['b'] - s['a'] + 0.3:.3f}", "-i", path(s["src"]), "-vf", f"fps={FPS},{SC}"]
    run(cmd + enc); return out


def main():
    os.makedirs(SEG, exist_ok=True); os.makedirs(os.path.join(PROJ, "assets"), exist_ok=True)
    t = 0.0; tl = {"segs": []}
    for s in SEGS:
        d = frames(dur(s)) / FPS
        tl["segs"].append(dict(s, start=round(t, 4), end=round(t + d, 4))); t += d
    tl["total"] = round(t, 4)
    if "--audio-only" not in sys.argv:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(3) as ex: res = list(ex.map(lambda p: build_segment(*p), list(enumerate(SEGS))))
        open(os.path.join(SEG, "list.txt"), "w").write("".join(f"file '{p}'\n" for p in res))
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(SEG, "list.txt"), "-c", "copy", os.path.join(PROJ, "assets", "aroll.mp4")])
    buf = np.zeros(int((t + 0.5) * SR), np.float32)
    for s in tl["segs"]:
        if s.get("kind") == "freeze": continue
        x = AUD[s["src"]][0][int(s["a"] * SR):int(s["b"] * SR)].copy(); f = int(0.012 * SR)
        x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
        i = int(s["start"] * SR); buf[i:i + len(x)] += x[:len(buf) - i]
    raw = os.path.join(PROJ, "edit", "voice_raw.wav")
    with wave.open(raw, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(buf, -1, 1) * 32767).astype(np.int16).tobytes())
    run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "highpass=f=80,afftdn=nf=-40:nr=6,acompressor=threshold=-24dB:ratio=2.5:attack=8:release=200:makeup=2,loudnorm=I=-16:TP=-2:LRA=11",
         "-ar", str(SR), "-ac", "2", os.path.join(PROJ, "assets", "voice.wav")])
    json.dump(tl, open(os.path.join(PROJ, "edit", "timeline.json"), "w"), indent=1)
    for s in tl["segs"]: print(f"  {s['start']:6.2f}-{s['end']:6.2f}  {s['name']:10} {s['src']} {s['a']:.2f}-{s.get('b', s['a']):.2f}")
    print("total", tl["total"])


if __name__ == "__main__":
    main()
