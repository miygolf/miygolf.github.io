#!/usr/bin/env python3
"""Writes index.html: the whole HyperFrames timeline (A-roll, graphics, captions, music bed, SFX) from one place.

Film times come from edit/timeline.json (written by build_aroll.py). SFX are placed so the file's peak lands on
the picture beat (start = beat - peak), peaks measured from the Mixkit files.

Run from the project folder:  python3 tools/build_index.py
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
B = TL["_beats"]
S = lambda n: TL[n]["start"]
TOTAL = TL["_total"]

# --- Mixkit SFX: id -> (file peak s, usable length s) ---
SFX = {
    2185: (0.01, 0.5), 2073: (0.0, 0.29), 212: (0.2, 0.6), 2887: (0.25, 0.4), 1092: (1.43, 1.9), 237: (0.14, 0.18),
    217: (0.25, 1.0), 2837: (0.06, 1.0), 2126: (0.16, 0.55), 3200: (0.26, 0.9), 1489: (0.71, 1.7), 2120: (0.15, 0.6),
    2342: (0.66, 2.0), 2069: (0.04, 0.6), 206: (0.19, 0.6), 3217: (0.19, 0.45), 2059: (0.0, 3.2), 518: (0.6, 6.0),
    2058: (0.14, 1.2), 205: (0.46, 1.1), 1490: (0.71, 0.8), 216: (0.04, 0.12),
}

CUTS = [S("tee"), S("app_1x"), S("green"), S("putt_1x"), S("after")]

# (beat time, id, volume, note)  -> start = beat - peak
CUES = [
    (0.02, 2185, 0.45, "title blocks snap on"),
    (B["hook_stroke"] + 0.02, 2073, 0.5, "putter tap"),
    (S("hook_freeze"), 212, 0.9, "PAUSE"),
    (S("hook_freeze") + 0.14, 2887, 0.55, "MASUK KE TAK? pops"),
    (S("hook_rewind") + 0.35, 1092, 0.55, "tape rewind back to the tee"),
    (S("tee"), 2185, 0.4, "pixel wipe lands"),
    (S("tee") + 0.12, 217, 0.4, "HOLE 1 / PAR 4 card"),
    (B["tee_top"] - 0.55, 2837, 0.35, "power meter charges"),
    (B["tee_impact"], 2126, 0.55, "tee strike (layered on the real one)"),
    (B["tee_impact"] + 0.06, 3200, 0.3, "TEE OFF! pops"),
    (S("app_1x"), 1489, 0.4, "pixel wipe whoosh"),
    (B["app_takeaway"] + 0.2, 2837, 0.32, "power meter charges"),
    (B["app_impact"], 2120, 0.5, "approach strike (layered)"),
    (B["app_impact"] + 0.75, 2342, 0.25, "pixel tracer sparkle"),
    (S("app_finish") + 0.85, 2069, 0.45, "ON THE GREEN coin"),
    (S("green"), 1489, 0.35, "pixel wipe whoosh"),
    (S("green") + 2.2, 237, 0.5, "117 YDS row"),
    (S("green") + 5.0, 237, 0.5, "KE PIN row"),
    (S("green") + 6.7, 2887, 0.4, "10-12 KAKI settles"),
    (S("putt_1x"), 1490, 0.4, "pixel wipe whoosh"),
    (S("putt_1x") + 0.1, 206, 0.4, "SHOT 3 banner"),
    (B["putt_stroke"], 2073, 0.45, "putter tap"),
    (S("putt_slow") + 0.05, 2837, 0.22, "target brackets lock"),
    (B["putt_drop"], 3217, 0.6, "ball drops in the cup"),
    (B["putt_drop"] + 0.02, 2059, 0.45, "BIRDIE! fanfare"),
    (B["putt_drop"] + 0.75, 518, 0.22, "small crowd cheer"),
    (B["putt_drop"] + 0.4, 2069, 0.4, "-1 coin"),
    (S("after"), 1489, 0.3, "pixel wipe whoosh"),
    (S("end_freeze"), 2185, 0.45, "freeze + results panel"),
    (S("end_freeze") + 0.35, 216, 0.5, "row 1"), (S("end_freeze") + 0.6, 216, 0.5, "row 2"),
    (S("end_freeze") + 0.85, 216, 0.5, "row 3"), (S("end_freeze") + 1.1, 2058, 0.45, "SCORE row"),
    (S("end_freeze") + 2.8, 205, 0.45, "CTA"),
]

# --- music bed ducking (speech windows in film time) ---
SPEECH = [(0.25, 2.05), (S("app_1x") + 0.28, S("app_1x") + 1.15), (S("green"), S("putt_1x") - 0.05), (B["putt_drop"] + 0.45, S("after") - 0.15),
          (S("after") + 0.05, S("after") + 5.85)]
BASE, DUCK, RAMP = 0.32, 0.085, 0.18

def music_points():
    pts = [(0.0, DUCK)]
    for a, b in SPEECH:
        pts += [(max(a - RAMP, 0.0), DUCK if a < 0.3 else BASE), (a, DUCK), (b, DUCK), (b + RAMP, BASE)]
    # the drop on the birdie: let it hit, then duck under the reaction
    pts += [(B["putt_drop"] - 0.05, BASE), (B["putt_drop"] + 0.02, 0.42), (B["putt_drop"] + 0.4, 0.42)]
    pts += [(TOTAL - 0.9, BASE), (TOTAL, 0.0)]
    pts.sort()
    # keep the later of duplicate times, merge
    out = []
    for t, v in pts:
        if out and abs(out[-1][0] - t) < 1e-3:
            out[-1] = (t, v)
        else:
            out.append((t, v))
    # windows can overlap the drop points: re-apply ducks inside speech windows
    def in_speech(t):
        return any(a <= t <= b for a, b in SPEECH)
    out = [(t, DUCK if in_speech(t) else v) for t, v in out]
    return [{"t": round(t, 3), "v": round(v, 3)} for t, v in out]

def esc(o):
    return json.dumps(o, separators=(",", ":")).replace('"', "&quot;")

def audio_tags():
    lines = []
    lines.append(f'      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" '
                 f'data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>')
    fx = {"version": 1, "nodes": [
        {"type": "highpass", "id": "hp", "label": "Clear the low end for the voice", "params": {"frequency": 110}},
        {"type": "peaking", "id": "carve", "label": "Pocket for the voice", "params": {"frequency": 2400, "gain": -6, "q": 0.8}}]}
    auto = {"version": 1, "lanes": [{"target": "volume", "points": music_points()}]}
    lines.append(f'      <!-- music bed: Mixkit "A Game" (#777), from 55.767 s so the drop at 82.5 s lands on the birdie -->')
    lines.append(f'      <audio data-hf-id="hf-bgm" id="bgm" class="clip" src="assets/music/a-game-777.mp3" data-start="0" data-duration="{TOTAL}" '
                 f'data-media-start="{82.5 - B["putt_drop"]:.3f}" data-track-index="11" data-volume="1" data-timeline-role="music" data-audio-group="music" '
                 f'data-fx-chain="{esc(fx)}" data-automation="{esc(auto)}"></audio>')
    lines.append("      <!-- sound design (Mixkit, file name = Mixkit id): start = picture beat - file peak -->")
    for i, (beat, sid, vol, note) in enumerate(sorted(CUES)):
        peak, length = SFX[sid]
        st = max(0.0, beat - peak)
        length = min(length, TOTAL - st)
        lines.append(f'      <audio data-hf-id="hf-s{i:02d}" id="sfx-{i:02d}" class="clip" src="assets/sfx/{sid}.mp3" data-start="{st:.3f}" '
                     f'data-duration="{length:.2f}" data-track-index="{12 + i % 4}" data-volume="{vol}" data-audio-group="sfx"></audio> <!-- {note} -->')
    return "\n".join(lines)

def main():
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": B, "TOTAL": TOTAL, "CUTS": CUTS}
    html = (tpl.replace("{{TOTAL}}", str(TOTAL))
               .replace("{{AUDIO}}", audio_tags())
               .replace("{{CONSTS}}", json.dumps(consts)))
    open(os.path.join(ROOT, "index.html"), "w").write(html)
    print("index.html written,", len(CUES), "sfx cues, total", TOTAL)

if __name__ == "__main__":
    main()
