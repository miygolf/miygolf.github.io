#!/usr/bin/env python3
"""Writes index.html: the whole HyperFrames timeline (A-roll, graphics, captions, music bed, SFX) from one place.

Film times come from edit/timeline.json (build_aroll.py). Caption word times come from edit/transcript.json (faster-whisper),
mapped onto the film through the voice placements build_aroll.py recorded. SFX start = picture beat - file peak.

Run from the project folder:  python3 tools/build_index.py
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
TR = json.load(open(os.path.join(ROOT, "edit", "transcript.json")))
B = dict(TL["_beats"])
VOICE = TL["_voice"]
S = lambda n: TL[n]["start"]
E = lambda n: TL[n]["end"]
TOTAL = TL["_total"]

def film(clip, t):
    """film time of source time t in clip (through the voice placements, all real-time)"""
    for c, a, b, ft in VOICE:
        if c == clip and a - 1e-3 <= t <= b + 1e-3:
            return ft + (t - a)
    # a word edge just outside a placed piece: clamp to the nearest piece edge (within 0.4 s)
    best = None
    for c, a, b, ft in VOICE:
        if c != clip: continue
        for edge, fe in ((a, ft), (b, ft + b - a)):
            if abs(t - edge) < 0.4 and (best is None or abs(t - edge) < best[0]):
                best = (abs(t - edge), fe)
    if best: return best[1]
    raise ValueError(f"clip{clip} {t} is not in the film")

def words(clip, a, b):
    out = []
    for seg in TR[f"clip{clip}"]:
        for w in seg["words"]:
            if a <= w["s"] < b:
                out.append(w)
    return out

FIX = {"part.": "putt.", "part": "putt", "part,": "putt,"}

# ---- beats from the words ----
B["plan_draw"] = film(2, 14.32)
B["plan_aim"] = film(2, 20.47)
B["plan_curve"] = film(2, 22.79)
B["why_scoop"] = film(4, 29.60)
B["why_weight"] = film(4, 31.72)
B["bogey"] = film(5, 36.14)

# ---- captions: (clip, src_from, src_to, who, key words, big)  or  ("manual", film_t, end, who, [(word, film_t, key)])
CAP_DEF = [
    (4, 18.20, 18.95, "fa", {"ASTAGFIRULLAH."}, True),
    (2, 12.50, 14.70, "iq", {"DRAW"}, False),
    (2, 19.90, 21.20, "iq", {"BUNKER."}, False),
    (2, 22.10, 23.40, "iq", {"CURVE"}, False),
    (2, 48.10, 49.30, "iq", {"GOOD"}, False),
    (2, 50.90, 52.10, "iq", {"OVER"}, False),
    (3, 14.90, 16.20, "fa", {"150."}, False),
    (3, 19.00, 21.30, "fa", {"P,"}, False),
    (4, 29.10, 30.05, "fa", {"SCOOP."}, False),
    (4, 31.10, 32.95, "fa", {"WEIGHT"}, False),
    (5, 0.70, 1.90, "fa", {"DISASTER,"}, False),
    (5, 29.00, 30.50, "fa", {"POINT"}, False),
    (6, 3.50, 4.70, "iq", {"BIRDIE."}, False),
    (6, 17.40, 19.00, "iq", {"DOWNHILL"}, False),
    (6, 19.50, 20.50, "iq", {"LEFT", "RIGHT."}, False),
    (6, 22.58, 23.48, "iq", {"BIRDIE."}, False),
    ("manual", 6, [("NEED", 28.46), ("TO", 28.50), ("SLOW", 28.56), ("DOWN!", 28.82)], "iq", {"SLOW"}),
    (6, 34.10, 35.35, "iq", {"BAD."}, False),
    ("manual", 6, [("GOOD", 75.36), ("SAVE!", 75.52)], "iq", {"SAVE!"}),
    (6, 80.40, 81.10, "iq", {"NEXT"}, True),
]

def build_caps():
    caps = []
    for d in CAP_DEF:
        if d[0] == "manual":
            _, clip, ws, who, keys = d
            items = [[w, round(film(clip, t), 3), w in keys] for w, t in ws]
            last_end = film(clip, ws[-1][1]) + 0.4
            big = False
        else:
            clip, a, b, who, keys, big = d
            ws = words(clip, a, b)
            items = []
            for w in ws:
                txt = FIX.get(w["w"], w["w"]).upper()
                t = film(clip, max(w["s"], a))
                items.append([txt, round(t, 3), txt in keys])
            last_end = film(clip, min(ws[-1]["e"], b)) if ws else 0
        caps.append([items[0][1] - 0.02, last_end + 0.25, who, big, items])
    # a line ends when the next one starts
    caps.sort(key=lambda c: c[0])
    for i in range(len(caps) - 1):
        caps[i][1] = round(min(caps[i][1], caps[i + 1][0] - 0.03), 3)
    for c in caps:
        c[0] = round(c[0], 3); c[1] = round(c[1], 3)
    return caps

CAPS = build_caps()

CUTS = [[S("tee_far"), "fa"], [S("tee_iqb"), "iq"], [S("iqb_plan"), "iq"], [S("far_plan"), "fa"], [S("chip_replay"), "fa"],
        [S("far_disaster"), "fa"], [S("iqb_read"), "iq"], [S("par_setup"), "iq"]]
TURNS = [[S("tee_far"), "fa"], [S("tee_iqb"), "iq"], [S("iqb_plan"), "iq"], [S("far_plan"), "fa"], [S("chip_replay"), "fa"],
         [S("far_putt"), "fa"], [S("iqb_read"), "iq"]]
HUD_HIDE = [[S("far_disaster"), E("far_disaster")]]
RINGS = [[B["far_tee_impact"], 720, 1320, "fa"], [B["iqb_tee_impact"], 510, 1385, "iq"], [B["iqb_app_impact"], 320, 1420, "iq"],
         [B["far_app_impact"], 345, 1470, "fa"], [B["chip_impact"], 384, 1250, "fa"]]
PLATES = [
    [S("tee_far") + 0.15, E("tee_far") - 0.12, "fa", "TEE SHOT", ""],
    [S("tee_iqb") + 0.15, E("tee_iqb") - 0.12, "iq", "TEE SHOT", ""],
    [S("iqb_plan") + 0.12, E("iqb_swing") - 0.12, "iq", "APPROACH", "PLAN: DRAW SIKIT"],
    [S("far_plan") + 0.12, E("far_swing") - 0.12, "fa", "APPROACH", "150 M · PAKAI P"],
    [S("chip_replay") + 0.06, E("chip_replay") - 0.05, "fa", "CHIP", "20 M KE PIN"],
    [S("far_putt") + 0.12, E("far_putt") - 0.12, "fa", "PUTT", ""],
    [S("iqb_read") + 0.12, S("iqb_roll") + 1.2, "iq", "BIRDIE PUTT", "DOWNHILL · LEFT → RIGHT"],
    [S("par_setup") + 0.12, B["par_stroke"] - 0.05, "iq", "PAR PUTT", ""],
]

# ---- SFX: file -> (peak s, usable length s) ----
SFX = {
    "3115.mp3": (0.11, 0.5), "166.mp3": (0.29, 0.7), "175.mp3": (0.46, 0.6), "1464.mp3": (0.11, 0.4), "1489.mp3": (0.71, 1.4),
    "1490.mp3": (0.71, 0.9), "2120.mp3": (0.15, 0.6), "2126.mp3": (0.18, 0.6), "2364.mp3": (0.0, 0.3), "3005.mp3": (0.03, 0.2),
    "518.mp3": (5.53, 10.5), "772.mp3": (0.41, 1.0), "bell-1.wav": (0.0, 3.0), "bell-3.wav": (0.0, 3.4),
    "hf-impact-bass-1.mp3": (0.07, 2.0), "hf-impact-bass-2.mp3": (0.36, 2.5), "hf-riser.mp3": (3.98, 4.2),
    "hf-whoosh-cinematic.mp3": (2.50, 4.0), "hf-whoosh-short.mp3": (0.16, 0.3),
}
V = S("vs")
D = B["par_drop"]
SW = ["3115.mp3", "166.mp3", "175.mp3"]
CUES = [
    (0.11, "3115.mp3", 0.45, "hook title slams in"),
    (0.17, "2364.mp3", 0.35, "HOLE 2 lands"),
    (V, "hf-riser.mp3", 0.30, "riser under the hook into the VS card"),
    (S("hook_freeze"), "772.mp3", 0.55, "freeze punch + SIAPA MENANG?"),
    (V + 0.02, "1489.mp3", 0.45, "VS panels slide in"),
    (V + 0.05, "bell-3.wav", 0.45, "ring bell: ding ding ding"),
    (V + 0.44, "hf-impact-bass-1.mp3", 0.6, "VS badge slams"),
    (V + 0.50, "2364.mp3", 0.45, "IQBAL name"), (V + 0.64, "2364.mp3", 0.45, "FARHAN name"),
    (B["far_tee_impact"], "2126.mp3", 0.40, "Farhan tee strike (layered on the real one)"),
    (B["iqb_tee_impact"], "2126.mp3", 0.40, "Iqbal tee strike (layered)"),
    (B["plan_draw"], "1489.mp3", 0.22, "draw curve draws itself"),
    (B["plan_aim"], "2364.mp3", 0.4, "AIM: BUNKER target"),
    (B["plan_curve"], "2364.mp3", 0.4, "PIN marker"),
    (B["iqb_app_impact"], "2120.mp3", 0.42, "Iqbal approach strike (layered)"),
    (B["far_app_impact"], "2120.mp3", 0.42, "Farhan approach strike (layered)"),
    (S("chip_replay") + 0.05, "hf-whoosh-short.mp3", 0.45, "REPLAY tag"),
    (B["chip_impact"] + 0.12, "hf-impact-bass-2.mp3", 0.55, "FAT! stamp"),
    (B["why_scoop"], "2364.mp3", 0.45, "why row 1"), (B["why_weight"], "2364.mp3", 0.45, "why row 2"),
    (B["bogey"], "hf-impact-bass-1.mp3", 0.6, "BOGEY stamp"),
    (S("iqb_read") + 0.3, "hf-whoosh-cinematic.mp3", 0.22, "4K push-in on the far address"),
    (S("par_setup") + 0.45, "772.mp3", 0.35, "MASUK = MENANG HOLE"),
    (D, "hf-riser.mp3", 0.32, "riser through the music break into the drop"),
    (D, "hf-impact-bass-1.mp3", 0.8, "KO: ball drops"),
    (D + 0.02, "bell-3.wav", 0.75, "ring bell on the win"),
    (D + 0.08, "772.mp3", 0.6, "IQBAL slams"),
    (D + 0.30, "518.mp3", 0.30, "cheer and applause"),
    (D + 0.7, "2364.mp3", 0.45, "HUD: W for Iqbal"),
    (S("end_freeze") + 0.05, "1490.mp3", 0.4, "result card"),
    (S("end_freeze") + 0.3, "2364.mp3", 0.45, "row Iqbal"), (S("end_freeze") + 0.5, "2364.mp3", 0.45, "row Farhan"),
    (S("end_freeze") + 1.1, "3005.mp3", 0.5, "CTA"),
]
for i, (t, who) in enumerate(CUTS):
    CUES.append((t, SW[i % 3], 0.38, f"slash wipe ({who})"))
for t0, t1, who, what, sub in PLATES:
    CUES.append((t0, "1464.mp3", 0.3, f"plate {what}"))

# ---- music: Mixkit track #400 (~144 BPM). First drop (13.243 s) on the VS slam, the break (64.75-66.2 s) under the par putt,
# the second drop (66.208 s) on the ball dropping.
M_DROP2 = 66.208
M_OFFSET = M_DROP2 - D              # media time = film time + offset
MUSIC_START = V - 0.05

def speech_windows():
    w = []
    for t0, t1, who, big, items in CAPS:
        w.append([items[0][1] - 0.12, t1 + 0.1])
    w.sort(); out = []
    for a, b in w:
        if out and a - out[-1][1] < 0.5: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out

SPEECH = speech_windows()
BASE, DUCK, RAMP = 0.30, 0.08, 0.18

def music_points():
    pts = [(0.0, 0.0), (MUSIC_START, 0.0), (MUSIC_START + 0.06, BASE)]
    for a, b in SPEECH:
        if b < MUSIC_START: continue
        pts += [(max(a - RAMP, MUSIC_START + 0.07), BASE), (max(a, MUSIC_START + 0.08), DUCK), (b, DUCK), (b + RAMP, BASE)]
    pts += [(V + 0.02, 0.34), (V + 0.9, 0.34), (V + 1.1, BASE)]                # let the first drop hit under the VS card
    pts += [(D - 0.05, BASE), (D + 0.02, 0.44), (D + 1.1, 0.44), (D + 1.3, BASE)]   # and the second on the win
    pts += [(TOTAL - 1.2, BASE), (TOTAL, 0.0)]
    pts.sort()
    def in_speech(t):
        return any(a <= t <= b for a, b in SPEECH)
    out = []
    for t, v in pts:
        if t > MUSIC_START + 0.07 and in_speech(t): v = DUCK
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
        {"type": "highpass", "id": "hp", "label": "Clear the low end for the voice", "params": {"frequency": 100}},
        {"type": "peaking", "id": "carve", "label": "Pocket for the voice", "params": {"frequency": 2400, "gain": -6, "q": 0.8}}]}
    auto = {"version": 1, "lanes": [{"target": "volume", "points": music_points()}]}
    L.append(f'      <!-- music bed: Mixkit track #400, entered so its first drop lands on the VS slam and the second on the par putt dropping -->')
    L.append(f'      <audio data-hf-id="hf-bgm" id="bgm" class="clip" src="assets/music/mixkit-400.mp3" data-start="{MUSIC_START:.3f}" '
             f'data-duration="{TOTAL - MUSIC_START:.3f}" data-media-start="{MUSIC_START + M_OFFSET:.3f}" data-track-index="11" data-volume="1" '
             f'data-timeline-role="music" data-audio-group="music" data-fx-chain="{esc(fx)}" data-automation="{esc(auto)}"></audio>')
    L.append("      <!-- sound design: Mixkit ids, HyperFrames bundle (hf-*), synthesised ring bell. start = picture beat - file peak -->")
    busy = {}   # track -> end time: give overlapping sounds their own track
    for i, (beat, f, vol, note) in enumerate(sorted(CUES)):
        peak, length = SFX[f]
        st = beat - peak; ms = 0.0
        if st < 0: ms = -st; st = 0.0
        length = min(length - ms, TOTAL - st)
        trk = next(k for k in range(12, 60) if busy.get(k, -1) <= st)
        busy[trk] = st + length
        mattr = f' data-media-start="{ms:.3f}"' if ms > 0 else ""
        L.append(f'      <audio data-hf-id="hf-s{i:02d}" id="sfx-{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{st:.3f}" '
                 f'data-duration="{length:.2f}"{mattr} data-track-index="{trk}" data-volume="{vol}" data-audio-group="sfx"></audio> <!-- {note} -->')
    return "\n".join(L)

def main():
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": {k: round(v, 3) for k, v in B.items()}, "TOTAL": TOTAL,
              "CUTS": CUTS, "TURNS": TURNS, "HUD_HIDE": HUD_HIDE, "RINGS": RINGS, "PLATES": PLATES, "CAPS": CAPS}
    html = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(html)
    print("index.html written:", len(CUES), "sfx cues,", len(CAPS), "caption lines, total", TOTAL)
    for c in CAPS:
        print(f"  {c[0]:6.2f}-{c[1]:6.2f} {c[2]} " + " ".join(w[0] for w in c[4]))

if __name__ == "__main__":
    main()
