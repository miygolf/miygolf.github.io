#!/usr/bin/env python3
"""Cuts the source clip (iPhone, 4K HEVC HLG 59.94 fps, upright 2160x3840) into one 1080x1920 30 fps A-roll (assets/aroll.mp4)
and builds the dialogue / natural-sound track (assets/voice.wav).
The EDL below is the single source of truth: film times of every segment and beat go to edit/timeline.json,
which tools/build_index.py turns into graphics, captions and SFX.

Run from the project folder:  python3 tools/build_aroll.py [--audio-only]
Needs ffmpeg and numpy. Source lives in .src/clip1.mov (see tools/fetch.sh).

Clip map (IMG_0023; Coach Farhan = mint shirt, white cap, standing in the bunker, ball in the sand near the right-hand lip;
the narrator films and asks the questions):
  0.00-4.38  narrator: "Coach Farhan, ni ... nak buat macam mana ni? Ada tip tak?" (1.7 s pause after "ni")
  4.78-7.62  coach: "Kita ada plenty of green to play." (points the club at the green ~6.2)
  8.38-9.68  "So nak buka pun," camera pans to the green and back 8.5-11.4 (cut)
  10.86-12.52 "okay dah, silap bawa kayu, bawa 60."  (camera settled on the coach from 11.5)
  12.74-14.96 "So kita try to do normal pitch,"   15.46-17.9 "but then you kena make sure you accelerate" (word ends ~17.88, pinned with right context)
  17.92-22.02 "because bunker ni memang most of the time you akan hit shot." (unclear ending, cut)   22.34 "So kita try." (cut)
  25.38-28.82 "Satu atau dua, kita visualize mana you nak hantar bola tu." ("hantar" drawn out 27.3-28.2)
  30.00-31.36 "Kita do normal, normal pitch." (cropped re-run: "normal pitch" 30.80-31.36)  address 31-33.6, backswing 33.6, IMPACT 34.24 (sound and picture agree), finish 34.6-35.3
  35.5-38.4  camera pans to the green (ball not visible) ; reaction 36.7-37.4 (first pass "Keluat lah", others disagree: not captioned) ; back on the coach 38.5 ; "Let's go." 39.78-40.52
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".src")
SEG = os.path.join(ROOT, "edit", "segs")
FPS = 30
SR = 48000
IMPACT = 34.24

# No colour grade: the footage keeps the iPhone's own colour (owner's standing preference since match play hole 2).
GRADE = "null"

# EDL in film order.  kind: None (play), "freeze" (hold src a for dur)
# zoom = [(t_in_segment, zoom, cx, cy)] in source pixels (2160x3840), smoothstep between keys
EDL = [
    # HOOK: the real shot from the top, 0.5x through impact (every 60 fps frame), freeze on the ball leaving in a puff of sand.
    # The narrator's question runs over it. Framed so the head stays below the title band (head y ~ 570-610 on the film).
    dict(name="hook_a", clip=1, a=33.00, b=33.95, speed=1.0, zoom=[(0, 1.45, 1110, 1975), (0.95, 1.52, 1120, 1975)]),
    dict(name="hook_slow", clip=1, a=33.95, b=34.27, speed=0.5, zoom=[(0, 1.52, 1120, 1975), (0.64, 1.62, 1140, 1985)]),
    dict(name="hook_freeze", clip=1, a=34.27, kind="freeze", dur=1.55, zoom=[(0, 1.62, 1140, 1985), (1.55, 1.68, 1150, 1985)]),
    # THE SITUATION: "Kita ada plenty of green to play."
    dict(name="sit", clip=1, a=4.70, b=7.70, speed=1.0, zoom=[(0, 1.0, 1080, 1920), (3.0, 1.05, 1080, 1800)]),
    # "silap bawa kayu, bawa 60."
    dict(name="club", clip=1, a=11.30, b=12.58, speed=1.0, zoom=[(0, 1.0, 1080, 1920), (1.28, 1.03, 1080, 1920)]),
    # STEP 1 "So kita try to do normal pitch," / STEP 2 "but then you kena make sure you accelerate" (jump cut hidden by a punch-in)
    dict(name="pitch1", clip=1, a=12.70, b=14.98, speed=1.0, zoom=[(0, 1.08, 1000, 2000), (2.28, 1.10, 1000, 2000)]),
    dict(name="pitch2", clip=1, a=15.40, b=17.90, speed=1.0, zoom=[(0, 1.22, 1000, 2000), (2.5, 1.25, 1000, 2000)]),
    # STEP 3 "kita visualize mana you nak hantar bola tu."
    # (whisper hears a pause inside "hantar" but the speech energy says the word is drawn out: kept whole)
    dict(name="vis", clip=1, a=26.12, b=28.90, speed=1.0, zoom=[(0, 1.08, 1000, 2050), (2.78, 1.11, 1000, 2050)]),
    # THE SHOT: "normal pitch." (30.80-31.36, pinned with a cropped re-run) -> address -> swing at 1x -> finish
    dict(name="shot", clip=1, a=30.72, b=35.30, speed=1.0, zoom=[(0, 1.15, 1060, 2100), (4.58, 1.18, 1060, 2100)]),
    # REPLAY at 0.5x, tight on the strike (the narrator's reaction over it)
    dict(name="replay", clip=1, a=33.95, b=34.75, speed=0.5, zoom=[(0, 1.75, 1200, 2300), (1.6, 1.95, 1260, 2330)]),
    # "Let's go." -> end card over the coach standing in the bunker
    dict(name="letsgo", clip=1, a=39.30, b=42.25, speed=1.0, zoom=[(0, 1.0, 1080, 1900), (2.95, 1.06, 1060, 1900)]),
    dict(name="end_freeze", clip=1, a=42.25, kind="freeze", dur=1.30, zoom=[(0, 1.06, 1060, 1900), (1.3, 1.08, 1060, 1900)]),
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
    placed = []   # (clip, src_a, src_b, film_t): lets build_index map transcript word times onto the film
    def place(x, t, gain_db=0.0, src=None):
        i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * db(gain_db)
        if src: placed.append([src[0], round(src[1], 3), round(src[2], 3), round(t, 4)])
    T = lambda n: tl[n]["start"]
    AMB = -8      # course ambience under the voice-over in the hook / replay
    # HOOK: the narrator's question (pause after "ni" cut), real strike on the slowed impact, quiet ambience under it
    place(piece(1, 32.95, 34.20, 0.08), T("hook_a"), AMB)
    q1 = (0.00, 0.86); q2 = (2.36, 3.12); q3 = (3.44, 4.42)
    t1 = 0.04; t2 = t1 + (q1[1] - q1[0]) + 0.10; t3 = t2 + (q2[1] - q2[0]) + 0.16
    place(piece(1, *q1), t1, 0, (1, *q1))          # "Coach Farhan, ni"
    place(piece(1, *q2), t2, 0, (1, *q2))          # "nak buat macam mana ni?"
    place(piece(1, *q3), t3, 0, (1, *q3))          # "Ada tip tak?"
    hook_imp = film_time(tl, "hook_slow", IMPACT)
    place(piece(1, IMPACT - 0.02, IMPACT + 0.30, 0.005), hook_imp - 0.02, -2)
    tl["_hook_vo_end"] = round(t3 + q3[1] - q3[0], 3)
    # the talking segments play in sync with their own sound
    for n in ("sit", "club", "pitch1", "pitch2", "vis", "shot", "letsgo"):
        s = next(x for x in EDL if x["name"] == n)
        place(piece(1, s["a"], s["b"], 0.025), T(n), 0, (1, s["a"], s["b"]))
    # "accelerate" is said softly as he turns away: lift it so the key word of the tip reads
    i0, i1 = int(film_time(tl, "pitch2", 16.88) * SR), int(film_time(tl, "pitch2", 17.88) * SR)
    ramp = np.ones(i1 - i0, np.float32) * db(5); f = int(0.04 * SR); ramp[:f] = np.linspace(1, db(5), f); ramp[-f:] = np.linspace(db(5), 1, f)
    buf[i0:i1] *= ramp
    # REPLAY: real strike on the slowed impact, the narrator's reaction (from the pan to the green) over it
    rep_imp = film_time(tl, "replay", IMPACT)
    place(piece(1, 33.95, 34.20, 0.05), T("replay"), AMB - 4)
    place(piece(1, IMPACT - 0.02, IMPACT + 0.40, 0.005), rep_imp - 0.02, -3)
    kl = (36.58, 37.42)   # reaction from behind the phone; words unclear across passes ("Keluar lah" / "Get out, bro" / ...): not captioned
    place(piece(1, *kl), rep_imp + 0.32, 0, (1, *kl))
    tail = piece(1, 42.00, 42.34, 0.05); tail = np.tile(tail, 5)[:int(1.3 * SR)] * np.linspace(1, 0, int(1.3 * SR))[:len(np.tile(tail, 5)[:int(1.3 * SR)])]
    place(tail, T("end_freeze"), -6)    # room tone under the last freeze
    tl["_voice"] = placed
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    out = os.path.join(ROOT, "edit", "voice_raw.wav")
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    run(["ffmpeg", "-v", "error", "-y", "-i", out, "-af",
         "highpass=f=100,afftdn=nf=-40:nr=10,equalizer=f=2800:t=q:w=1.2:g=3,acompressor=threshold=-24dB:ratio=3:attack=5:release=150:makeup=3,"
         "loudnorm=I=-16:TP=-2:LRA=9",
         "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")])


if __name__ == "__main__":
    tl = timeline()
    beats = {
        "hook_impact": film_time(tl, "hook_slow", IMPACT),
        "shot_backswing": film_time(tl, "shot", 33.62),
        "shot_impact": film_time(tl, "shot", IMPACT),
        "replay_impact": film_time(tl, "replay", IMPACT),
        "green_point": film_time(tl, "sit", 6.10),
    }
    tl["_beats"] = {k: round(v, 3) for k, v in beats.items()}
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    json.dump(tl, open(os.path.join(ROOT, "edit", "timeline.json"), "w"), indent=1)
    print(json.dumps(tl, indent=1))
    if "--audio-only" not in sys.argv:
        build_video()
    build_audio(tl)
