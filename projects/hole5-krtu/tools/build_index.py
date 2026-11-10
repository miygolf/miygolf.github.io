#!/usr/bin/env python3
"""Writes index.html: the whole HyperFrames timeline (A-roll, departure board, boarding passes, stamps, captions, music, SFX).

Film times come from edit/timeline.json (build_aroll.py). Caption word times are transcript word starts (two faster-whisper passes,
Malay + English) mapped onto the film through the voice placements build_aroll.py recorded. SFX start = picture beat - file peak.

Run from the project folder:  python3 tools/build_index.py
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
B = dict(TL["_beats"])
VOICE = TL["_voice"]
S = lambda n: TL[n]["start"]
E = lambda n: TL[n]["end"]
TOTAL = TL["_total"]


def film(clip, t):
    for c, a, b, ft in VOICE:
        if c == clip and a - 1e-3 <= t <= b + 1e-3:
            return ft + (t - a)
    raise ValueError(f"clip{clip} {t} is not in the film")


# ---- captions: (big, [(word, clip, src_t, key, line_break_after)]) — only lines both passes agree on
C2, C3, C4 = 2, 3, 4
CAP_DEF = [
    (True,  [("SIKIT.", C4, 17.82, True, 0)]),
    (False, [("OKAY,", C2, 0.02, 0, 0), ("COME", C2, 0.18, 0, 0), ("PLAY", C2, 0.82, 1, 0), ("WITH", C2, 1.10, 0, 0), ("US.", C2, 1.34, 0, 0)]),
    (False, [("LUBANG", C2, 2.32, 0, 0), ("LIMA,", C2, 3.02, 1, 0), ("PAR", C2, 3.44, 0, 0), ("TIGA,", C2, 3.64, 1, 1),
             ("KRTU,", C2, 4.20, 0, 0), ("180", C2, 5.46, 1, 0), ("METER.", C2, 6.26, 0, 0)]),
    (False, [("GOOD", C2, 18.82, 0, 0), ("LINE.", C2, 19.52, 1, 0)]),
    (False, [("PENDEK", C2, 24.58, 1, 0), ("SIKIT.", C2, 25.28, 0, 0)]),
    (False, [("180,", C2, 34.34, 1, 0), ("PIN", C2, 34.78, 0, 0), ("BELAKANG.", C2, 36.40, 1, 0)]),
    (False, [("AKU", C2, 43.25, 0, 0), ("TRY", C2, 43.60, 0, 0), ("PAKAI", C2, 43.86, 0, 0), ("IRON", C2, 44.10, 1, 0), ("5.", C2, 44.44, 1, 0)]),
    (False, [("GOOD", C2, 53.12, 0, 0), ("SWING.", C2, 53.42, 1, 0)]),
    (False, [("CENTER.", C2, 59.62, 1, 0)]),
    (False, [("PUTT", C3, 4.26, 0, 0), ("FOR", C3, 4.78, 0, 0), ("BIRDIE.", C3, 4.94, 1, 0)]),
    (False, [("NAMPAK", C3, 6.62, 0, 0), ("DIA,", C3, 7.14, 0, 0), ("SLOPE", C3, 7.32, 1, 0), ("BANYAK.", C3, 8.06, 0, 0)]),
    (False, [("RIGHT", C3, 9.24, 1, 0), ("TO", C3, 9.76, 0, 0), ("LEFT.", C3, 9.90, 1, 0)]),
    (False, [("SEJUJURNYA,", C3, 11.52, 0, 1), ("MAKE", C3, 12.00, 0, 0), ("SURE", C3, 12.15, 0, 0), ("BOLA", C3, 12.34, 0, 0), ("SAMPAI.", C3, 12.56, 1, 0)]),
    (False, [("LEBIH", C3, 15.90, 0, 0), ("SAMPAI", C3, 16.10, 1, 0), ("JE.", C3, 16.44, 0, 0)]),
]


def build_caps():
    caps = []
    for big, ws in CAP_DEF:
        items = []
        for w, clip, t, key, br in ws:
            if clip == C4:   # "Sikit." is placed twice; the hook one is the first placement
                ft = next(p[3] for p in VOICE if p[0] == 4) + (t - 17.70)
            else:
                ft = film(clip, t)
            items.append([w, round(ft, 3), bool(key), bool(br)])
        caps.append([items[0][1] - 0.03, items[-1][1] + 0.7, big, items])
    g2 = [p for p in VOICE if p[0] == 4][-1][3] + (17.82 - 17.70)
    caps.append([g2 - 0.03, g2 + 0.9, True, [["SIKIT.", round(g2, 3), True, False]]])
    caps.sort(key=lambda c: c[0])
    for i in range(len(caps) - 1):
        caps[i][1] = min(caps[i][1], caps[i + 1][0] - 0.05)
    for c in caps:
        c[0] = round(c[0], 3); c[1] = round(c[1], 3)
    return caps


CAPS = build_caps()

# ---- section wipes (flap slats) with the board word that flashes in the middle
WIPES = [[S("intro"), "REWIND"], [S("g1_a"), "GREEN"], [S("outro") - 0.0, ""]]
WIPES = [w for w in WIPES if w[1]]
HUD = [[S("tee1") + 0.1, S("tee1_slo") - 0.05], [S("tee1_res"), E("tee2_res") - 0.1], [S("g1_c") + 0.3, E("g1_ball") - 0.1], [S("g2_setup") + 0.1, S("outro")]]

# ---- boarding passes: [t0, t1, num, title, f1 label, f1 value, f2 label, f2 value, top px]
PASSES = [
    [S("tee1") + 0.15, B["tee1_impact"] - 0.5, "01", "TEE SHOT", "JARAK", "180 M", "PIN", "BELAKANG", 305],
    [S("tee2_pin") + 0.15, S("tee2") + 1.2, "02", "TEE SHOT", "JARAK", "180 M", "KAYU", "IRON 5", 305],
    [S("g1_a") + 0.25, S("g1_c") + 0.2, "03", "BIRDIE PUTT", "BREAK", "R → L", "GATE", "GREEN 5", 190, 490],
    [S("g2_setup") + 0.2, B["g2_stroke"] - 0.6, "04", "BIRDIE PUTT", "GATE", "GREEN 5", "STATUS", "FINAL CALL", 305],
]
# ---- stamps: [t0, t1, sub, text, x, y, rotation, class]
STAMPS = [
    [B["hook_stop"] + 0.22, S("intro") - 0.12, "BIRDIE PUTT", "SIKIT JE!", 300, 560, -8, "big"],
    [film(2, 19.52) + 0.05, film(2, 19.52) + 1.75, "SHOT 01", "GOOD LINE", 70, 760, -7, ""],
    [film(2, 24.58) + 0.05, E("tee1_res") + 0.45, "SHOT 01", "PENDEK SIKIT", 70, 1000, 6, ""],
    [film(2, 53.42) + 0.08, film(2, 53.42) + 1.75, "SHOT 02", "GOOD SWING", 70, 900, -6, ""],
    [film(2, 59.62) + 0.1, E("tee2_res") + 0.02, "SHOT 02", "CENTER GREEN", 80, 820, 5, "y"],
    [S("g1_ball") + 0.6, E("g1_ball") - 0.05, "SHOT 03", "DEKAT PIN", 300, 1120, -6, ""],
    [B["g2_stop"] + 0.3, S("outro") + 0.9, "SHOT 04", "SIKIT LAGI!", 230, 560, -7, "big y"],
]
# ---- the break line on green 1 (from the ball, drifting right then breaking left), and its time window
BRK = "M 525 1300 C 760 1160, 880 920, 705 800"
BRK_T = [film(3, 9.24) - 0.1, E("g1_d") - 0.1]

# ---- SFX: file -> (peak s, usable length s) (measured)
SFX = {
    "1379.mp3": (0.36, 1.2), "1378.mp3": (3.41, 1.4), "1371.mp3": (0.35, 0.9), "1570.mp3": (0.53, 3.0), "1364.mp3": (0.03, 0.8),
    "1367.mp3": (0.34, 0.7), "2380.mp3": (0.29, 0.9), "2384.mp3": (0.13, 0.35), "1530.mp3": (0.35, 1.0), "1490.mp3": (0.72, 1.5),
    "166.mp3": (0.33, 0.75), "3115.mp3": (0.11, 0.55), "175.mp3": (0.49, 0.6), "2127.mp3": (0.15, 0.7), "2121.mp3": (0.15, 0.6),
    "1095.mp3": (0.31, 0.6), "1146.mp3": (1.71, 2.6),
}
CUES = [
    (0.10, "1379.mp3", 0.35, "board riffles on frame 0"),
    (B["hook_stop"] + 0.22, "1364.mp3", 0.5, "stamp SIKIT JE! (after the word)"),
    (B["hook_stop"] + 0.18, "1371.mp3", 0.30, "status flaps flip"),
    (S("intro") - 0.25, "1095.mp3", 0.45, "rewind: slat wipe to the tee"),
    (S("intro") + 0.20, "1570.mp3", 0.16, "airport chime: COME PLAY WITH US board"),
    (S("intro") + 0.30, "1379.mp3", 0.30, "intro board riffles"),
    (S("sign") - 0.05, "175.mp3", 0.45, "cut to the sign"),
    (S("tee1") + 0.15, "1530.mp3", 0.45, "boarding pass 01 slides in"),
    (B["tee1_impact"] - 0.5, "2384.mp3", 0.6, "pass 01 stub tears"),
    (B["tee1_impact"] + 0.01, "2127.mp3", 0.28, "strike layer, teal tee shot"),
    (film(2, 19.52) + 0.06, "1364.mp3", 0.5, "stamp GOOD LINE"),
    (S("tee1_slo") + 0.02, "166.mp3", 0.40, "slow replay in"),
    (B["tee1_slo_impact"] + 0.01, "2127.mp3", 0.30, "strike on the slow replay"),
    (film(2, 24.58) + 0.06, "1367.mp3", 0.5, "stamp PENDEK SIKIT"),
    (S("tee2_pin") + 0.15, "2380.mp3", 0.9, "boarding pass 02"),
    (S("tee2") + 1.2, "2384.mp3", 0.6, "pass 02 stub tears"),
    (B["tee2_impact"] + 0.01, "2121.mp3", 0.30, "strike layer, grey tee shot"),
    (film(2, 53.42) + 0.09, "1364.mp3", 0.5, "stamp GOOD SWING"),
    (S("tee2_slo") + 0.02, "3115.mp3", 0.55, "slow replay in"),
    (B["tee2_slo_impact"] + 0.01, "2121.mp3", 0.30, "strike on the slow replay"),
    (film(2, 59.62) + 0.11, "1367.mp3", 0.5, "stamp CENTER GREEN"),
    (S("g1_a") - 0.25, "1490.mp3", 0.40, "slat wipe to the green"),
    (S("g1_a") - 0.05, "1378.mp3", 0.35, "GREEN flaps"),
    (S("g1_a") + 0.25, "1530.mp3", 0.45, "boarding pass 03"),
    (BRK_T[0] + 0.1, "175.mp3", 0.40, "break line draws"),
    (S("g1_ball") + 0.61, "1364.mp3", 0.5, "stamp DEKAT PIN"),
    (S("g2_setup") + 0.2, "2380.mp3", 0.9, "boarding pass 04"),
    (B["g2_stroke"] - 0.6, "2384.mp3", 0.6, "pass 04 stub tears"),
    (S("g2_pan") + 0.05, "166.mp3", 0.35, "pan to the hole"),
    (B["g2_stop"], "1146.mp3", 0.30, "build under the slow roll, peaks on the stop"),
    (B["g2_stop"] + 0.31, "1364.mp3", 0.5, "stamp SIKIT LAGI!"),
    (S("outro") + 0.25, "1379.mp3", 0.35, "arrivals board riffles"),
    (S("outro") + 1.4, "1530.mp3", 0.40, "CTA ticket"),
]

# ---- music: Mixkit #989 "Gimme that Groove!" (~76 BPM). Its quiet stretch (62-69.5 s) sits under green 2's setup and slow roll;
# the groove comes back (69.5 s) on the ball stopping. Media time = film time + OFF.
M_BACK = 69.5
OFF = M_BACK - B["g2_stop"]


def speech_windows():
    w = [[c[3][0][1] - 0.12, min(c[1] + 0.08, c[3][-1][1] + 0.55)] for c in CAPS]
    w.sort(); out = []
    for a, b in w:
        if out and a - out[-1][1] < 0.4: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out


SPEECH = speech_windows()
BASE, DUCK, RAMP, LIFT = 0.66, 0.10, 0.15, 0.85


def music_points():
    pts = [(0.0, 0.0), (0.05, BASE)]
    for a, b in SPEECH:
        pts += [(max(a - RAMP, 0.06), BASE), (max(a, 0.07), DUCK), (b, DUCK), (b + RAMP, BASE)]
    for t in [B["tee1_impact"], B["tee2_impact"], B["g1_stroke"], B["g2_stroke"]]:   # the real strikes stay audible
        pts += [(t - 0.2, BASE), (t - 0.1, DUCK), (t + 0.35, DUCK), (t + 0.5, BASE)]
    D = B["g2_stop"]
    pts += [(D - 0.02, BASE), (D + 0.03, LIFT), (D + 1.4, LIFT), (D + 1.8, BASE)]
    pts += [(TOTAL - 1.2, BASE), (TOTAL, 0.0)]
    pts.sort()
    def in_speech(t): return any(a <= t <= b for a, b in SPEECH)
    out = []
    for t, v in pts:
        if t > 0.06 and in_speech(t): v = DUCK
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
    L.append('      <!-- music bed: Mixkit #989, its quiet stretch under green 2, the groove back on the ball stopping; ducked under speech and strikes -->')
    L.append(f'      <audio data-hf-id="hf-bgm" id="bgm" class="clip" src="assets/music/mixkit-989.mp3" data-start="0" '
             f'data-duration="{TOTAL:.3f}" data-media-start="{OFF:.3f}" data-track-index="11" data-volume="1" '
             f'data-timeline-role="music" data-audio-group="music" data-fx-chain="{esc(fx)}" data-automation="{esc(auto)}"></audio>')
    L.append("      <!-- sound design: Mixkit ids (assets/sfx/CREDITS.md). start = picture beat - file peak -->")
    busy = {}
    for i, (beat, f, vol, note) in enumerate(sorted(CUES)):
        peak, length = SFX[f]
        st = beat - peak; ms = max(0.0, peak - length) if f in ("1378.mp3",) else 0.0
        if f == "1378.mp3":   # long typewriter run: use the 1.4 s around its peak
            ms = peak - 1.0; st = beat - 1.0
        if st < 0: ms += -st; length += st; st = 0.0
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
              "CAPS": CAPS, "WIPES": WIPES, "HUD": HUD, "PASSES": PASSES, "STAMPS": STAMPS, "BRK_T": BRK_T}
    html = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{BRK}}", BRK)
            .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(html)
    print("index.html written:", len(CUES), "sfx cues,", len(CAPS), "caption lines, total", TOTAL, "| music offset", round(OFF, 3))
    for c in CAPS:
        print(f"  {c[0]:6.2f}-{c[1]:6.2f} " + " ".join(f"{w[0]}" for w in c[3]))


if __name__ == "__main__":
    main()
