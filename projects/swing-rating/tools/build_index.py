#!/usr/bin/env python3
"""Writes index.html: A-roll, measurement drawings (from MediaPipe pose, edit/pose.json), grade slabs, labels and SFX, all from one place.

Film times: edit/timeline.json (tools/build_aroll.py). Ratings and numbers: edit/metrics.json (tools/metrics.py) + the RATING table below.
No speech in any clip (whisper only hallucinates outro phrases on range noise), so there are no captions; text is labels and numbers.
SFX start = picture beat - file peak. No music (house rule: final = SFX only).

Run from the project folder:  python3 tools/build_index.py
"""
import json, os, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
POSE = json.load(open(os.path.join(ROOT, "edit", "pose.json")))
MET = json.load(open(os.path.join(ROOT, "edit", "metrics.json")))
B = dict(TL["_beats"])
S = lambda n: TL[n]["start"]
E = lambda n: TL[n]["end"]
TOTAL = TL["_total"]
CROP = {int(k): v for k, v in TL["_crop"].items()}
KEYS = MET["keys"]; M = MET["metrics"]

# ---------------- rating (mine, from the measured numbers; 0-10) ----------------
RATING = {
    "rows": [
        # name, detail before, detail after, score before, score after
        ["SETUP", "postur 30°", "postur 28°", 7.0, 7.0],
        ["KEPALA", "lari sikit", "stay tengah", 6.5, 7.5],
        ["IMPACT", "hilang 18°", "hilang 7° je", 4.5, 7.5],
        ["FINISH", "balance", "balance", 8.0, 8.0],
    ],
}
RATING["before"] = round(sum(r[3] for r in RATING["rows"]) / 4, 1)
RATING["after"] = round(sum(r[4] for r in RATING["rows"]) / 4 + 1e-9, 1)


# ---------------- geometry (film px on the 1080x1920 frame) ----------------
def lm(clip, frame, i, n=1):
    pts = [POSE[clip][f][i] for f in range(frame - n, frame + n + 1)]
    return (sum(p[0] for p in pts) / len(pts) * 1080, sum(p[1] for p in pts) / len(pts) * 1920)

def midp(a, b): return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)

def spine(clip, frame):
    hip = midp(lm(clip, frame, 23), lm(clip, frame, 24)); sh = midp(lm(clip, frame, 11), lm(clip, frame, 12))
    ang = math.degrees(math.atan2(abs(sh[0] - hip[0]), hip[1] - sh[1]))
    return {"hip": [round(hip[0], 1), round(hip[1], 1)], "sh": [round(sh[0], 1), round(sh[1], 1)], "ang": round(ang)}

def head(clip, frame):
    pts = [lm(clip, frame, i) for i in (0, 7, 8)]          # nose + ears
    cx = sum(p[0] for p in pts) / 3
    ny = lm(clip, frame, 0)[1]
    hip = midp(lm(clip, frame, 23), lm(clip, frame, 24)); sh = midp(lm(clip, frame, 11), lm(clip, frame, 12))
    torso = math.dist(hip, sh)                              # head (with cap) ~ 0.6 torso tall, works bent over or upright
    return {"x": round(cx, 1), "nose_y": round(ny, 1), "top": round(ny - 0.42 * torso, 1), "bottom": round(ny + 0.22 * torso, 1),
            "half_w": round(0.3 * torso, 1), "torso": round(torso, 1)}

def shift(g, dx):
    g = json.loads(json.dumps(g))
    for k in ("hip", "sh"):
        g[k][0] = round(g[k][0] + dx, 1)
    return g

GEO = {
    "b_dtl": {"ghost": spine("clip3", KEYS["clip3"]["address"]), "now": spine("clip3", KEYS["clip3"]["impact"])},
    "a_dtl": {"ghost": spine("clip1", KEYS["clip1"]["address"]), "now": spine("clip1", KEYS["clip1"]["impact"])},
    "b_fo": {"addr": head("clip2", KEYS["clip2"]["address"]), "top": head("clip2", KEYS["clip2"]["top"])},
    "a_fo": {"addr": head("clip4", KEYS["clip4"]["address"]), "top": head("clip4", KEYS["clip4"]["top"])},
}
# split panels: left = clip3 window at x CROP[3], right = clip1 window at x CROP[1], each 540 wide
GEO["split"] = {
    "L": {"ghost": shift(GEO["b_dtl"]["ghost"], -CROP[3]), "now": shift(GEO["b_dtl"]["now"], -CROP[3])},
    "R": {"ghost": shift(GEO["a_dtl"]["ghost"], 540 - CROP[1]), "now": shift(GEO["a_dtl"]["now"], 540 - CROP[1])},
}
# head boxes for the safe-zone check (printed)
FACES = {
    "hook_frz L": head("clip3", KEYS["clip3"]["impact"]), "b_frz": head("clip3", KEYS["clip3"]["impact"]),
    "b_fo_top": head("clip2", KEYS["clip2"]["top"]), "b_card(finish)": head("clip2", 143),
    "a_frz": head("clip1", KEYS["clip1"]["impact"]), "a_fo_top": head("clip4", KEYS["clip4"]["top"]),
    "a_card(finish)": head("clip4", 170), "end_frz": head("clip1", 200),
}

# ---------------- beats for the overlays (film s) ----------------
W = {
    "hook_lines": S("hook_frz") + 0.25,
    "b_lines": S("b_frz") + 0.15, "a_lines": S("a_frz") + 0.15,
    "b_head": S("b_fo_top") + 0.15, "a_head": S("a_fo_top") + 0.15,
    "proof_lines": S("proof_frz") + 0.15,
}

# ---------------- SFX ----------------  Mixkit ids, see assets/sfx/CREDITS.md;  (peak, length) measured from the files
SFX = {
    "166.mp3": (0.30, 0.78), "772.mp3": (0.41, 1.22), "871.mp3": (0.45, 1.30), "1119.mp3": (0.15, 0.33), "1133.mp3": (0.20, 0.35),
    "1430.mp3": (0.14, 0.63), "1489.mp3": (0.72, 1.41), "1491.mp3": (0.30, 0.60), "1994.mp3": (0.02, 0.69), "2001.mp3": (0.02, 0.30),
    "2002.mp3": (0.20, 0.40), "2126.mp3": (0.18, 0.64), "2350.mp3": (0.46, 1.70), "2357.mp3": (0.13, 0.38), "2364.mp3": (0.01, 0.12),
    "2586.mp3": (1.64, 3.0), "2925.mp3": (0.19, 0.30), "3115.mp3": (0.12, 0.57),
}

def foil_cues(t, rare=False):   # foil sweep transition centred on t
    c = [(t - 0.02, "3115.mp3", 0.30, "foil sweep")]
    if rare: c.append((t + 0.05, "2350.mp3", 0.12, "foil sparkle (after section)"))
    return c

CUES = [
    (0.03, "2925.mp3", 0.26, "title plate on frame 0"),
    (0.30, "2002.mp3", 0.30, "SEBELUM tag"), (0.45, "2002.mp3", 0.30, "SELEPAS tag"),
    (B["hook_impact"], "772.mp3", 0.30, "freeze on both impacts"),
    (B["hook_impact"] + 0.02, "1133.mp3", 0.30, "card edge snaps round the freeze"),
    (W["hook_lines"] + 0.25, "1489.mp3", 0.12, "spine lines draw"),
    (W["hook_lines"] + 0.55, "1119.mp3", 0.24, "lines land"),
    (W["hook_lines"] + 0.75, "2357.mp3", 0.22, "'?' question"),
    *foil_cues(S("b_dtl")),
    (S("b_dtl") + 0.15, "2002.mp3", 0.30, "01 SEBELUM plate"),
    (B["b_impact"], "2126.mp3", 0.16, "quiet layer on the real strike"),
    (S("b_slow") + 0.05, "166.mp3", 0.16, "into the 0.5x replay"),
    (B["b_slow_impact"], "2126.mp3", 0.22, "slowed strike"),
    (B["b_slow_impact"] + 0.02, "1133.mp3", 0.28, "freeze, card edge"),
    (W["b_lines"] + 0.25, "1489.mp3", 0.12, "address line (ghost) draws"),
    (W["b_lines"] + 0.75, "1119.mp3", 0.26, "impact line snaps"),
    (W["b_lines"] + 0.85, "1994.mp3", 0.30, "-18° callout lands"),
    (W["b_lines"] + 1.2, "2357.mp3", 0.20, "hip arrow"),
    (S("b_fo1") + 0.02, "166.mp3", 0.18, "cut to face-on"),
    (W["b_head"] - 0.13, "1133.mp3", 0.26, "freeze at the top"),
    (W["b_head"] + 0.10, "2357.mp3", 0.18, "address head marker"),
    (W["b_head"] + 0.45, "1491.mp3", 0.20, "head arrow swipes"),
    (W["b_head"] + 0.6, "1994.mp3", 0.28, "KEPALA LARI callout"),
    (B["b_fo_impact"], "2126.mp3", 0.16, "quiet layer on the strike"),
    (S("b_card") + 0.02, "166.mp3", 0.22, "frame shrinks into the slab"),
    (S("b_card") + 0.40, "1994.mp3", 0.34, "slab label lands"),
    (S("b_card") + 0.85, "2364.mp3", 0.22, "stat 1"), (S("b_card") + 1.05, "2364.mp3", 0.22, "stat 2"),
    (S("b_card") + 1.25, "2364.mp3", 0.22, "stat 3"), (S("b_card") + 1.45, "2364.mp3", 0.22, "stat 4"),
    (S("b_card") + 1.85, "772.mp3", 0.22, "grade 6.5 slams"),
    *foil_cues(S("a_dtl"), rare=True),
    (S("a_dtl") + 0.15, "2002.mp3", 0.30, "02 SELEPAS plate"),
    (B["a_impact"], "2126.mp3", 0.16, "quiet layer on the real strike"),
    (S("a_slow") + 0.05, "166.mp3", 0.16, "into the 0.5x replay"),
    (B["a_slow_impact"], "2126.mp3", 0.22, "slowed strike"),
    (B["a_slow_impact"] + 0.02, "1133.mp3", 0.28, "freeze, card edge"),
    (W["a_lines"] + 0.25, "1489.mp3", 0.12, "address line (ghost) draws"),
    (W["a_lines"] + 0.75, "1119.mp3", 0.26, "impact line snaps"),
    (W["a_lines"] + 0.85, "1994.mp3", 0.30, "-7° callout lands"),
    (S("a_fo1") + 0.02, "166.mp3", 0.18, "cut to face-on"),
    (W["a_head"] - 0.13, "1133.mp3", 0.26, "freeze at the top"),
    (W["a_head"] + 0.10, "2357.mp3", 0.18, "address head marker"),
    (W["a_head"] + 0.6, "1994.mp3", 0.28, "KEPALA STAY callout"),
    (B["a_fo_impact"], "2126.mp3", 0.16, "quiet layer on the strike"),
    (S("a_card") + 0.02, "166.mp3", 0.22, "frame shrinks into the slab"),
    (S("a_card") + 0.40, "1994.mp3", 0.34, "slab label lands"),
    (S("a_card") + 0.85, "2364.mp3", 0.22, "stat 1"), (S("a_card") + 1.05, "2364.mp3", 0.22, "stat 2"),
    (S("a_card") + 1.25, "2364.mp3", 0.22, "stat 3"), (S("a_card") + 1.45, "2364.mp3", 0.22, "stat 4"),
    (S("a_card") + 1.85, "772.mp3", 0.24, "grade 7.6 slams"),
    (S("a_card") + 1.95, "871.mp3", 0.24, "UPGRADE foil burst"),
    (S("a_card") + 2.0, "2586.mp3", 0.12, "sparkles round the slab"),
    *foil_cues(S("proof")),
    (S("proof") + 0.15, "2002.mp3", 0.28, "SIDE BY SIDE plate"),
    (B["proof_impact"], "2126.mp3", 0.14, "quiet layer on the strikes"),
    (S("proof_frz") + 0.02, "1133.mp3", 0.28, "freeze on impact, card edge"),
    (W["proof_lines"] + 0.35, "1119.mp3", 0.22, "lines left"), (W["proof_lines"] + 0.55, "1119.mp3", 0.22, "lines right"),
    (W["proof_lines"] + 0.90, "2364.mp3", 0.24, "-18°"), (W["proof_lines"] + 1.10, "2364.mp3", 0.24, "-7°"),
    *foil_cues(S("end_play"), rare=True),
    (S("end_play") + 0.30, "2002.mp3", 0.28, "APA BERUBAH plate"),
    (S("end_play") + 0.60, "2364.mp3", 0.22, "row 1"), (S("end_play") + 0.85, "2364.mp3", 0.22, "row 2"),
    (S("end_play") + 1.10, "2364.mp3", 0.22, "row 3"),
    (B["end_impact"], "2126.mp3", 0.14, "quiet layer on the strike"),
    (S("end_frz") + 0.10, "1994.mp3", 0.32, "end scorecard"),
    (S("end_frz") + 0.55, "2364.mp3", 0.22, "6.5"), (S("end_frz") + 0.85, "772.mp3", 0.20, "7.6"),
    (S("end_frz") + 1.20, "2357.mp3", 0.20, "NEXT chip"),
    (S("end_frz") + 1.60, "2925.mp3", 0.28, "CTA"),
]


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


def stat_rows(phase):
    j = 3 if phase == "b" else 4; d = 1 if phase == "b" else 2
    out = []
    for r in RATING["rows"]:
        out.append(f'<div class="srow"><div class="sn"><b>{r[0]}</b><small>{r[d]}</small></div><div class="sv">{r[j]:.1f}</div>'
                   f'<div class="sbar"><i style="width:{r[j] * 10:.0f}%"></i></div></div>')
    return "\n            ".join(out)


def main():
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": B, "TOTAL": TOTAL, "W": W, "GEO": GEO,
              "R": {"before": RATING["before"], "after": RATING["after"]}}
    rep = {"{{TOTAL}}": str(TOTAL), "{{AUDIO}}": audio_tags(), "{{CONSTS}}": json.dumps(consts, ensure_ascii=False),
           "{{STATS_B}}": stat_rows("b"), "{{STATS_A}}": stat_rows("a"),
           "{{GB}}": f'{RATING["before"]:.1f}', "{{GA}}": f'{RATING["after"]:.1f}', "{{UP}}": f'{RATING["after"] - RATING["before"]:+.1f}'}
    out = tpl
    for k, v in rep.items(): out = out.replace(k, v)
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written:", len(CUES), "sfx cues, total", TOTAL, "| grade", RATING["before"], "->", RATING["after"])
    for k, v in GEO.items(): print("  geo", k, v)
    for k, v in FACES.items(): print(f"  face {k:<16} x {v['x'] - v['half_w']:.0f}-{v['x'] + v['half_w']:.0f}  y {v['top']:.0f}-{v['bottom']:.0f}")


if __name__ == "__main__":
    main()
