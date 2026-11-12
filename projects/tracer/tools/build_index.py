#!/usr/bin/env python3
"""Writes index.html: A-roll, shot tracer, plan drawings, glass cards, captions and SFX, all from one place.

Film times: edit/timeline.json (build_aroll.py). Caption word times: faster-whisper on the assembled voice track (assets/voice.wav),
which is already on the film clock. SFX start = picture beat - file peak. No music (house rule: final = SFX only).

The tracer: ball positions measured by frame differencing for the first 0.4 s after impact (tools/track_ball.py, film px = 4K / 2);
after that the ball is a few pixels wide against the tree line and can't be followed, so the rest of the flight is a smooth draw
(starts right, peaks, curves left) to an estimated landing just past the pin at ~5.6 s ("over sikit"). Landing spot is approximate.

Run from the project folder:  python3 tools/build_index.py
"""
import json, os, html, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
B = dict(TL["_beats"])
S = lambda n: TL[n]["start"]
TOTAL = TL["_total"]

# ---------------- geometry (film px, uncropped 1080x1920; the camera is on a tripod) ----------------
BALL = (385, 1359)                  # ball at address (same spot in the talk section)
PIN = (470, 906)                    # estimated: left of the bunker, behind the branch line (approximate)
BUNKER = (548, 913)                 # pale sand face on the mound, where he aims
BRANCH = (432, 868)                 # edge of the overhanging canopy on the line to the pin
LAND = (478, 897)                   # estimated landing, just past the pin ("over sikit")

TRACKED = [  # (seconds after impact, x, y)   measured, tools/track_ball.py on the 4K frames (/2)
    (0.0, 385, 1359), (0.1135, 489, 990), (0.130, 494.5, 966), (0.1468, 499.5, 947.5), (0.1635, 503.5, 931.5),
    (0.180, 506.5, 918.5), (0.197, 509, 906.5), (0.2136, 511.5, 897), (0.230, 513.5, 889), (0.247, 515, 881),
    (0.264, 516, 874), (0.280, 517.5, 868), (0.297, 518.5, 862.5), (0.314, 519.5, 857.5), (0.330, 520.5, 853),
    (0.347, 521, 848.5), (0.364, 521.5, 844.5), (0.380, 522, 841), (0.397, 522.5, 837.5),
]
MODEL = [  # estimated continuation. The measured rise rate decays like 1/(t+0.076)^2 (fit on the tracked points), which leaves
           # ~70-100 px more climb before gravity wins: apex ~ y 772 near 1.8 s, then it draws left and drops to the landing
    (0.70, 532, 806), (1.00, 538, 790), (1.40, 543, 779), (1.80, 546, 773), (2.40, 547, 775), (3.10, 542, 788),
    (3.80, 532, 808), (4.50, 516, 834), (5.10, 497, 864), (5.60, LAND[0], LAND[1]),
]
KEYS = TRACKED + MODEL
FLIGHT = KEYS[-1][0]


def catmull(keys, t):
    ts = [k[0] for k in keys]
    if t <= ts[0]: return keys[0][1:]
    if t >= ts[-1]: return keys[-1][1:]
    i = max(j for j in range(len(ts) - 1) if ts[j] <= t)
    p0 = keys[max(i - 1, 0)]; p1 = keys[i]; p2 = keys[i + 1]; p3 = keys[min(i + 2, len(keys) - 1)]
    u = (t - p1[0]) / (p2[0] - p1[0])
    out = []
    for d in (1, 2):
        m1 = (p2[d] - p0[d]) / max(p2[0] - p0[0], 1e-6) * (p2[0] - p1[0])
        m2 = (p3[d] - p1[d]) / max(p3[0] - p1[0], 1e-6) * (p2[0] - p1[0])
        h00, h10, h01, h11 = 2*u**3 - 3*u**2 + 1, u**3 - 2*u**2 + u, -2*u**3 + 3*u**2, u**3 - u**2
        out.append(h00 * p1[d] + h10 * m1 + h01 * p2[d] + h11 * m2)
    return tuple(out)


# path sampled at 120 Hz; per film frame: drawn length + head position
pts, lens, L = [], [], 0.0
N = int(FLIGHT * 120)
for k in range(N + 1):
    t = k / 120
    if t <= 0.1135:   # impact -> first tracked point: straight, the ball covers it in 7 frames
        u = t / 0.1135; p = (BALL[0] + (489 - BALL[0]) * u, BALL[1] + (990 - BALL[1]) * u)
    else:
        p = catmull(KEYS, t)
    if pts: L += math.dist(pts[-1], p)
    pts.append(p); lens.append(L)
PATH = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def at(t):
    k = min(max(int(round(t * 120)), 0), N)
    return pts[k], lens[k]


def frames_from(t0, t1):
    """per 30 fps film frame between t0 (impact on film) and t1: [film_t, drawn_len, x, y]"""
    out = []; f = 0
    while True:
        ft = t0 + f / 30
        if ft > t1 + 1e-6: break
        tau = ft - t0
        (x, y), l = at(min(tau, FLIGHT))
        out.append([round(ft, 3), round(l, 1), round(x, 1), round(y, 1)])
        f += 1
    return out


# Ribbon for the tracer: points at 60 Hz with a width that falls off with distance (perspective), like broadcast tracers:
# ~14 px at the club, ~3 px from 0.5 s on (the ball is far away by then), never below 2.4 px.
RIB = []
for k in range(int(FLIGHT * 60) + 1):
    (x, y), _ = at(k / 60)
    RIB.append([round(x, 1), round(y, 1), round(max(2.4, 14.0 / (1 + 9.0 * k / 60)), 2)])


def ribframes(t0, t1):
    """per film frame: [film_t, last whole ribbon index, head x, head y]"""
    out = []; f = 0
    while True:
        ft = t0 + f / 30
        if ft > t1 + 1e-6: break
        tau = min(ft - t0, FLIGHT)
        (x, y), _ = at(tau)
        out.append([round(ft, 3), int(tau * 60), round(x, 1), round(y, 1)])
        f += 1
    return out


TR_HOOK = ribframes(B["hook_impact"], TL["hook"]["end"])
TR_MAIN = ribframes(B["impact"], B["impact"] + FLIGHT)

# plan drawings
DIRECT = f"M {BALL[0]} {BALL[1]} L {PIN[0]} {PIN[1]}"
XMARK = (457, 978)                                                      # where the straight line meets the canopy
DRAWPLAN = f"M {BALL[0]} {BALL[1]} C 515 1080 600 905 {PIN[0]} {PIN[1]}"   # out right toward the bunker, curving back in

# ---------------- captions: word times on the film (whisper on assets/voice.wav) ----------------
CAPS = [
    dict(words=[("Okey", 1.70), ("disebabkan", 2.26), ("ke", 3.12), ("*pin", 3.76)], end=4.10),
    dict(words=[("kita", 4.18), ("ada", 4.46), ("*branch", 4.82), ("kat", 5.38), ("depan", 5.60), ("tu.", 5.88)], end=6.05),
    dict(words=[("Ada", 6.16), ("sikit", 6.72), ("je", 7.04), ("*pokok", 7.16), ("kat", 7.44), ("depan", 7.56), ("tu.", 7.76)], end=7.98),
    dict(words=[("So", 8.00), ("saya", 8.36), ("akan", 8.72), ("buat", 9.08), ("*draw", 9.48), ("sikit", 10.34)], end=10.72),
    dict(words=[("supaya", 10.74), ("*elak.", 10.96)], end=11.60),
    dict(words=[("Kita", 12.18), ("*aim", 12.74), ("kat", 12.98), ("*bunker.", 13.14)], end=13.65),
    dict(words=[("Bagi", 13.70), ("dia", 14.26), ("*curve", 14.36), ("*masuk.", 14.62)], end=15.05),
    dict(words=[("Oh.", 22.44), ("What", 23.26), ("a", 23.58), ("*good", 25.52), ("*shot.", 25.68), ("🔥", 25.70)], end=26.30),
    dict(words=[("Tapi", 26.54), ("*over", 27.10), ("*sikit.", 27.34), ("😅", 27.40)], end=28.40),
]


def caps_html():
    out, data = [], []
    for i, c in enumerate(CAPS):
        t0 = c["words"][0][1] - 0.12
        t1 = c["end"]
        if i + 1 < len(CAPS): t1 = min(t1 + 0.25, CAPS[i + 1]["words"][0][1] - 0.12)
        parts = []
        for txt, t in c["words"]:
            hot = txt.startswith("*"); txt = txt.lstrip("*")
            if any(ord(ch) > 0x2600 for ch in txt):
                parts.append(f'<span class="emo">{txt}</span>')
            else:
                parts.append(f'<span class="{"w hot" if hot else "w"}" data-t="{t:.3f}">{html.escape(txt)}</span>')
        out.append(f'<div id="cap{i}" class="ov cap">{" ".join(parts)}</div>')
        data.append({"t0": round(t0, 3), "t1": round(t1, 3)})
    return "\n      ".join(out), data


CAPHTML, CAPDATA = caps_html()
W = {"branch": 4.82, "draw": 9.48, "aim": 12.74, "curve": 14.36, "good": 25.52, "over": 27.10, "one54": 0.05}
ZOOM = 1.6      # stage push-in during the flight (origin 510,880; must match the template)
END = 28.8      # end card (after "Tapi over sikit")

# ---------------- SFX ----------------  Mixkit ids, see assets/sfx/CREDITS.md
SFX = {
    "1119.mp3": (0.15, 0.23), "1484.mp3": (0.59, 2.16), "1489.mp3": (0.72, 1.41), "1491.mp3": (0.30, 0.40),
    "166.mp3": (0.34, 0.67), "2126.mp3": (0.17, 0.47), "2357.mp3": (0.24, 0.32), "2364.mp3": (0.05, 0.11),
    "2568.mp3": (0.01, 0.05), "2586.mp3": (1.60, 3.53), "2925.mp3": (0.06, 0.24), "3115.mp3": (0.11, 0.27), "772.mp3": (0.52, 0.67),
    "786.mp3": (3.86, 4.30),
}
CUES = [
    (0.02, "2925.mp3", 0.24, "title card on frame 0 (low: '154' starts at once)"),
    (B["hook_impact"], "2126.mp3", 0.38, "strike, layered on the real one"),
    (B["hook_impact"] + 0.05, "1484.mp3", 0.26, "tracer zip leaving the club"),
    (S("p1") - 0.10, "3115.mp3", 0.28, "glass sweep into the plan"),
    (W["branch"] + 0.05, "1119.mp3", 0.26, "ring snaps on the branch"),
    (W["branch"] + 0.40, "2364.mp3", 0.22, "X on the straight line"),
    (W["branch"] + 0.10, "2357.mp3", 0.20, "chip 1"),
    (W["draw"] + 0.05, "2357.mp3", 0.16, "chip 2"),
    (W["draw"] + 0.50, "1489.mp3", 0.20, "plan curve draws out"),
    (W["aim"] + 0.05, "2357.mp3", 0.16, "chip 3"),
    (W["aim"] + 0.12, "1119.mp3", 0.24, "aim rings on the bunker"),
    (W["curve"] + 0.62, "2357.mp3", 0.18, "chip 4 (after 'masuk')"),
    (W["curve"] + 0.70, "2568.mp3", 0.26, "pin flag pops (after the word)"),
    (S("swing") + 0.22, "166.mp3", 0.24, "glass sweep into the shot (after 'masuk')"),
    (B["takeaway"] + 0.20, "786.mp3", 0.14, "soft riser through the backswing, tops out on the strike"),
    (B["impact"], "2126.mp3", 0.40, "strike, layered on the real one"),
    (B["impact"] + 0.05, "1484.mp3", 0.30, "tracer zip"),
    (B["impact"] + 2.4, "1489.mp3", 0.12, "air under the apex (quiet)"),
    (B["landing"], "772.mp3", 0.26, "landing ripple"),
    (B["landing"] + 0.05, "2364.mp3", 0.22, "landing marker"),
    (W["good"] + 0.55, "2586.mp3", 0.10, "sparkle after 'good shot' (low)"),
    (W["over"] + 0.30, "1491.mp3", 0.22, "OVER arrow swipes past the pin"),
    (END + 0.10, "3115.mp3", 0.30, "end glass card"),
    (END + 0.45, "2364.mp3", 0.20, "row 1"), (END + 0.65, "2364.mp3", 0.20, "row 2"), (END + 0.85, "2364.mp3", 0.22, "row 3"),
    (END + 1.00, "2925.mp3", 0.28, "SAVE tag"),
]
VOICE = TL["_voice"]
SPEECH = [(ft, ft + b - a) for c, a, b, ft in VOICE]


def check_speech():
    for beat, f, vol, note in CUES:
        peak, length = SFX[f]; st, en = beat - peak, beat - peak + length
        for a, b in SPEECH:
            if st < b and en > a and vol > 0.3:
                print(f"  ! loud cue over speech: {note} ({st:.2f}-{en:.2f}, vol {vol})")


def audio_tags():
    L = [f'      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" '
         f'data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>',
         "      <!-- sound design: Mixkit ids (assets/sfx/CREDITS.md). start = picture beat - file peak. No music. -->"]
    busy = {}
    for i, (beat, f, vol, note) in enumerate(sorted(CUES)):
        peak, length = SFX[f]
        st = beat - peak; ms = 0.0
        if st < 0: ms = -st; length += st; st = 0.0
        length = min(length, TOTAL - st)
        trk = next(k for k in range(12, 60) if busy.get(k, -1) <= st)
        busy[trk] = st + length
        mattr = f' data-media-start="{ms:.3f}"' if ms > 0 else ""
        L.append(f'      <audio data-hf-id="hf-s{i:02d}" id="sfx-{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{st:.3f}" '
                 f'data-duration="{length:.2f}"{mattr} data-track-index="{trk}" data-volume="{vol}" data-audio-group="sfx"></audio> <!-- {note} -->')
    return "\n".join(L)


def main():
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": B, "TOTAL": TOTAL, "CAP": CAPDATA, "W": W, "END": END,
              "TRH": TR_HOOK, "TRM": TR_MAIN, "RIB": RIB, "LAND": LAND, "PIN": PIN}
    rep = {"{{TOTAL}}": str(TOTAL), "{{AUDIO}}": audio_tags(), "{{CAPS}}": CAPHTML, "{{PATH}}": PATH, "{{DIRECT}}": DIRECT,
           "{{DRAWPLAN}}": DRAWPLAN, "{{XX}}": str(XMARK[0]), "{{XY}}": str(XMARK[1]), "{{BX}}": str(BRANCH[0]), "{{BY}}": str(BRANCH[1]),
           "{{KX}}": str(BUNKER[0]), "{{KY}}": str(BUNKER[1]), "{{PX}}": str(PIN[0]), "{{PY}}": str(PIN[1]),
           "{{LX}}": str(LAND[0]), "{{LY}}": str(LAND[1]),
           "{{LEADX}}": f"{510 + (LAND[0] - 510) * ZOOM:.0f}", "{{LEADY}}": f"{880 + (LAND[1] - 880) * ZOOM - 12:.0f}", "{{CONSTS}}": json.dumps(consts, ensure_ascii=False)}
    out = tpl
    for k, v in rep.items(): out = out.replace(k, v)
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written:", len(CUES), "sfx cues, total", TOTAL, "tracer length", round(L), "px")
    check_speech()


if __name__ == "__main__":
    main()
