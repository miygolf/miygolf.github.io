#!/usr/bin/env python3
"""Writes index.html: the whole HyperFrames timeline (A-roll, stickers, captions, music bed, SFX) from one place.

Film times come from edit/timeline.json (build_aroll.py). Caption word times come from the transcript (faster-whisper),
mapped onto the film through the voice placements build_aroll.py recorded. SFX start = picture beat - file peak.

Run from the project folder:  python3 tools/build_index.py
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
B = dict(TL["_beats"])
VOICE = TL["_voice"]
S = lambda n: TL[n]["start"]
TOTAL = TL["_total"]


def film(t):
    """film time of source time t (all voice pieces play at 1x)"""
    for a, b, ft in VOICE:
        if a - 1e-3 <= t <= b + 1e-3:
            return ft + (t - a)
    best = None
    for a, b, ft in VOICE:
        for edge, fe in ((a, ft), (b, ft + b - a)):
            if abs(t - edge) < 0.4 and (best is None or abs(t - edge) < best[0]):
                best = (abs(t - edge), fe)
    if best: return best[1]
    raise ValueError(f"{t} is not in the film")


def src_to_film(seg, t):
    """film time of source time t inside a picture segment (speed-aware)"""
    sp = {"hook_slow": (10.45, 0.3), "demo": (8.55, 1.0), "roll_pan": (12.20, 1.75), "roll": (13.60, 1.0),
          "back_whip": (16.30, 1.5), "walk_tilt": (17.20, 2.2), "turf": (20.20, 1.0)}[seg]
    return S(seg) + (t - sp[0]) / sp[1]


# ---- beats ----
B["backswing"] = src_to_film("demo", 10.45)
B["step2"] = src_to_film("walk_tilt", 18.70)
B["drop"] = S("turf_freeze") + 0.66          # music drop + TAK ADA DIVOT, right after "Clean." ends

# ---- captions: word, source time (transcript word starts; whisper's first pass heard "Mesti tak boleh", re-checked on the
#      boosted piece four ways: "Mestilah boleh"), key word, line break after
CAP_DEF = [
    (False, [("BOLEH", 3.17, False), ("TAK", 3.42, False), ("KITA", 3.50, False), ("PAKAI", 3.66, False, "nl"), ("CHIP", 3.88, True),
             ("ATAUPUN", 4.78, False), ("WEDGE?", 6.84, True)]),
    (True, [("MESTILAH", 8.85, False), ("BOLEH.", 9.28, True)]),
    (True, [("CLEAN.", 21.02, True)]),
]


def build_caps():
    caps = []
    for big, ws in CAP_DEF:
        items = []
        lines = [[]]
        for w in ws:
            lines[-1].append(w)
            if len(w) > 3 and w[3] == "nl": lines.append([])
        for ln in lines:
            for i, w in enumerate(ln):
                cls = "solo" if len(ln) == 1 else ("bl" if i == 0 else ("br" if i == len(ln) - 1 else ""))
                items.append([w[0], round(film(w[1]), 3), w[2], cls])
        caps.append([items[0][1] - 0.03, items[-1][1] + 0.75, big, items])
    caps.sort(key=lambda c: c[0])
    for i in range(len(caps) - 1):
        caps[i][1] = min(caps[i][1], caps[i + 1][0] - 0.05)
    # the question stays up until the poll answers it
    caps[0][1] = max(caps[0][1], TL["_q_end"] + 0.05)
    caps[0][1] = min(caps[0][1], caps[1][0] - 0.05)
    for c in caps:
        c[0] = round(c[0], 3); c[1] = round(c[1], 3)
    return caps


CAPS = build_caps()
SPEEDS = [[0, "0.3×"], [S("demo"), "1×"], [S("roll_pan"), "1.75×"], [S("roll"), "1×"], [S("back_whip"), "1.5×"],
          [S("walk_tilt"), "2.2×"], [S("turf"), "1×"]]
BALL = [449, 1438]             # ball at the strike in the demo shot (film px)
SPARKS = [[214, 884, 0.10, 1.0], [800, 950, 0.22, 0.8], [270, 1290, 0.32, 0.7], [790, 1270, 0.16, 1.1], [600, 870, 0.38, 0.6]]
CROP_IMP = [1.9, 452, 1330]   # proof stills: [scale, focus x, focus y] in source px
CROP_TURF = [1.5, 480, 1390]
CTA_AT = 2.1

# ---- SFX: file -> (peak s, usable length s) (measured) ----
SFX = {
    "275.mp3": (0.20, 0.45), "1119.mp3": (0.14, 0.33), "2568.mp3": (0.0, 0.2), "2925.mp3": (0.18, 0.9), "2357.mp3": (0.04, 0.38),
    "2354.mp3": (0.05, 0.9), "2356.mp3": (0.13, 0.3), "1491.mp3": (0.29, 1.0), "1492.mp3": (1.07, 1.3), "1468.mp3": (0.30, 1.0),
    "1714.mp3": (1.09, 1.8), "1484.mp3": (0.59, 2.0), "2123.mp3": (0.14, 0.65), "786.mp3": (3.86, 3.95), "2290.mp3": (0.10, 1.6),
    "2586.mp3": (1.54, 3.0),
}
H1, H2, F, P = S("hook_freeze"), S("demo"), S("turf_freeze"), S("end_freeze")
C = P + CTA_AT
CUES = [
    (0.00, "2925.mp3", 0.40, "hook card on frame 0"),
    (0.10, "2357.mp3", 0.30, "speed chip"),
    (1.55, "1484.mp3", 0.22, "air sweep under the slow downswing"),
    (H1 + 0.01, "275.mp3", 1.00, "shutter: freeze on contact"),
    (H1 + 0.06, "1119.mp3", 0.45, "focus brackets snap"),
    (H2 - 0.02, "1491.mp3", 0.45, "hook card peels, bloom cut into the demo"),
    (H2 + 0.12, "2925.mp3", 0.35, "poll sticker pops"),
    (B["boleh"] + 0.09, "2568.mp3", 0.70, "tap on BOLEH (after the word)"),
    (B["boleh"] + 0.30, "1119.mp3", 0.40, "check mark"),
    (B["backswing"] - 0.1, "1468.mp3", 0.28, "poll peels away"),
    (B["impact"] + 0.03, "2123.mp3", 0.30, "strike layer on the real chip"),
    (S("roll_pan") + 0.02, "1492.mp3", 0.38, "bloom cut onto the pan"),
    (S("back_whip") + 0.02, "1714.mp3", 0.32, "bloom cut, swing back to the spot"),
    (B["step2"] + 0.05, "2357.mp3", 0.30, "step 02 pill"),
    (F, "786.mp3", 0.30, "riser in the music break, peaks on the freeze"),
    (F + 0.01, "275.mp3", 1.00, "shutter: freeze on the turf"),
    (F + 0.07, "1119.mp3", 0.45, "turf brackets snap"),
    (B["drop"], "2290.mp3", 0.42, "impact on TAK ADA DIVOT (music drop)"),
    (B["drop"] + 0.08, "2925.mp3", 0.40, "answer sticker"),
    (B["drop"] + 0.55, "2586.mp3", 0.75, "sparkles on the clean turf"),
    (P, "1492.mp3", 0.32, "proof cards fly in"),
    (P + 0.08, "2357.mp3", 0.30, "card 1"), (P + 0.33, "2354.mp3", 0.30, "card 2"),
    (P + 0.72, "2356.mp3", 0.40, "0 divot badge"),
    (C - 0.2, "1468.mp3", 0.30, "cards peel"),
    (C + 0.02, "2925.mp3", 0.40, "CTA sticker"),
    (C + 0.92, "2356.mp3", 0.40, "komen pill"),
]

# ---- music: Mixkit #1141 "Funkee Monkeee" (~99 BPM). Its break (77.35-81.6 s) sits under the roll and the walk back, and the
# drop (81.6 s) lands on TAK ADA DIVOT. Media time = film time + OFF.
M_DROP = 81.60
OFF = M_DROP - B["drop"]


def speech_windows():
    w = [[c[3][0][1] - 0.12, min(c[1] + 0.08, c[3][-1][1] + 0.45)] for c in CAPS]
    w.append([B["impact"] - 0.12, B["impact"] + 0.45])   # the real strike: bed down so the contact is heard
    w.sort(); out = []
    for a, b in w:
        if out and a - out[-1][1] < 0.4: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out


SPEECH = speech_windows()
BASE, DUCK, RAMP, LIFT = 0.45, 0.13, 0.15, 0.62


def music_points():
    pts = [(0.0, BASE)]
    for a, b in SPEECH:
        pts += [(max(a - RAMP, 0.0), BASE), (max(a, 0.01), DUCK), (b, DUCK), (b + RAMP, BASE)]
    D = B["drop"]
    pts += [(D - 0.02, BASE), (D + 0.03, LIFT), (D + 1.6, LIFT), (D + 2.0, BASE)]
    pts += [(TOTAL - 1.0, BASE), (TOTAL, 0.0)]
    pts.sort()
    def in_speech(t): return any(a <= t <= b for a, b in SPEECH)
    out = []
    for t, v in pts:
        if in_speech(t): v = DUCK
        if out and abs(out[-1][0] - t) < 1e-3: out[-1] = (t, v)
        else: out.append((t, v))
    return [{"t": round(t, 3), "v": round(v, 3)} for t, v in out]


def esc(o):
    return json.dumps(o, separators=(",", ":")).replace('"', "&quot;")


def audio_tags():
    L = []
    L.append(f'      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" '
             f'data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>')
    fx = {"version": 1, "nodes": [
        {"type": "highpass", "id": "hp", "label": "Clear the low end for the voice", "params": {"frequency": 110}},
        {"type": "peaking", "id": "carve", "label": "Pocket for the voice", "params": {"frequency": 2400, "gain": -6, "q": 0.8}}]}
    auto = {"version": 1, "lanes": [{"target": "volume", "points": music_points()}]}
    L.append('      <!-- music bed: Mixkit #1141, break under the roll + walk back, drop on TAK ADA DIVOT; ducked under every spoken line -->')
    L.append(f'      <audio data-hf-id="hf-bgm" id="bgm" class="clip" src="assets/music/mixkit-1141.mp3" data-start="0" '
             f'data-duration="{TOTAL:.3f}" data-media-start="{OFF:.3f}" data-track-index="11" data-volume="1" '
             f'data-timeline-role="music" data-audio-group="music" data-fx-chain="{esc(fx)}" data-automation="{esc(auto)}"></audio>')
    L.append("      <!-- sound design: Mixkit ids (assets/sfx/CREDITS.md). start = picture beat - file peak -->")
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
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": {k: round(v, 3) for k, v in B.items()}, "TOTAL": TOTAL,
              "CAPS": CAPS, "SPEEDS": SPEEDS, "BALL": BALL, "SPARKS": SPARKS, "CROP_IMP": CROP_IMP, "CROP_TURF": CROP_TURF, "CTA_AT": CTA_AT}
    html = tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False))
    open(os.path.join(ROOT, "index.html"), "w").write(html)
    print("index.html written:", len(CUES), "sfx cues,", len(CAPS), "caption lines, total", TOTAL, "| music offset", round(OFF, 3))
    for c in CAPS:
        print(f"  {c[0]:6.2f}-{c[1]:6.2f} " + " ".join(f"{w[0]}@{w[1]}" for w in c[3]))
    print("speech", SPEECH)


if __name__ == "__main__":
    main()
