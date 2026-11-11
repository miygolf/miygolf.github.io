#!/usr/bin/env python3
"""Writes index.html: the whole HyperFrames timeline (A-roll, chat bubbles, pills, stickers, SFX) from one place.

Film times come from edit/timeline.json (build_aroll.py). Word times are the faster-whisper word starts (edit/transcript.json,
checked against the speech energy), mapped onto the film through the voice placements build_aroll.py recorded.
SFX start = picture beat - file peak. No music (house rule: final = SFX only).

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
            return round(ft + (t - a), 3)
    raise ValueError(f"clip{clip} {t} is not in the film")

# ---- the narrator's words (source seconds). Lines as they wrap in the bubble. ----
CAP = {
    "m1": [[("Tengok", 3.06), ("dia", 3.26), ("boleh", 3.42)],
           [("convert", 3.64), ("birdie", 3.88), ("ke…", 4.44)]],
    "m2": [[("…bogey", 6.10), ("😂", 6.40)],
           [("kita", 6.62), ("tengok.", 6.88)]],
    "nasib": [[("Tu", 11.02), ("nasib", 11.32), ("😂", 11.70)]],
}
CAPF = {k: [[[w, film(1 if k != "nasib" else 3, t)] for w, t in line] for line in v] for k, v in CAP.items()}
CAPF["m1"][0][0][1] = 0.0      # first word lit on frame 0

B["freeze"] = S("hook_freeze")
B["ask"] = S("hook_freeze") + 0.40

# speech windows on the film (for keeping SFX off the voice)
SPEECH = [(ft, ft + b - a) for c, a, b, ft in VOICE]

# ---- SFX: file -> (peak s, usable length s) ----  Mixkit ids, see assets/sfx/CREDITS.md
SFX = {
    "2357.mp3": (0.24, 0.38), "3005.mp3": (0.03, 0.18), "2364.mp3": (0.01, 0.5), "1464.mp3": (0.11, 0.6),
    "166.mp3": (0.30, 0.7), "2126.mp3": (0.17, 0.64), "2121.mp3": (0.14, 0.66), "2127.mp3": (0.15, 0.72),
    "1146.mp3": (1.79, 2.05), "518.mp3": (5.54, 10.6),
}
ALIAS = {"cheer": ("518.mp3", 0.0, 3.2, 4.6)}   # applause from its loud part, 3.2 s, fades with the film
CUES = [
    (0.00, "2357.mp3", 0.22, "first bubble (on frame 0)"),
    (CAPF["m2"][0][0][1] - 0.06, "2357.mp3", 0.22, "second bubble (in the gap before 'bogey')"),
    (B["freeze"], "1464.mp3", 0.22, "freeze, soft accent (under 'kita tengok', low)"),
    (B["freeze"] + 0.30, "2357.mp3", 0.30, "typing bubble"),
    (B["ask"], "3005.mp3", 0.55, "MASUK KE TAK? sticker"),
    (B["ask"] + 0.02, "2364.mp3", 0.35, "sticker lands"),
    (S("tee_intro"), "166.mp3", 0.30, "cut from the hook back to the tee"),
    (S("tee_intro") + 0.12, "2357.mp3", 0.16, "TEE SHOT pill (quiet: 'Farhan' is spoken here)"),
    (B["tee_impact"], "2126.mp3", 0.38, "tee strike, layered on the real one"),
    (S("chip") + 0.12, "2357.mp3", 0.22, "CHIP pill"),
    (B["chip_contact"], "2127.mp3", 0.30, "chip contact, layered"),
    (S("putt") + 0.12, "2357.mp3", 0.22, "PUTT pill"),
    (B["putt_drop"], "1146.mp3", 0.20, "soft build under the roll, peaks on the drop"),
    (B["putt_drop"] + 0.03, "3005.mp3", 0.6, "MASUK!! sticker"),
    (B["putt_drop"] + 0.05, "2364.mp3", 0.45, "sticker lands"),
    (S("end_freeze") + 0.15, "1464.mp3", 0.30, "end card: recap pill"),
    (S("end_freeze") + 0.75, "2357.mp3", 0.30, "CTA bubble"),
    (S("end_freeze") + 0.10, "cheer", 0.16, "light applause under the end card (no speech here)"),
]

def check_speech():
    for beat, f, vol, note in CUES:
        if f in ALIAS: f, peak, length = ALIAS[f][:3]
        else: peak, length = SFX[f]
        st, en = beat - peak, beat - peak + length
        for a, b in SPEECH:
            if st < b and en > a and vol > 0.3:
                print(f"  ! loud cue over speech: {note} ({st:.2f}-{en:.2f}, vol {vol})")

def audio_tags():
    L = [f'      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" '
         f'data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>',
         "      <!-- sound design: Mixkit ids (assets/sfx/CREDITS.md). start = picture beat - file peak. No music. -->"]
    busy = {}
    for i, (beat, f, vol, note) in enumerate(sorted(CUES)):
        m0 = 0.0
        if f in ALIAS:
            al = ALIAS[f]; f, peak, length = al[:3]; m0 = al[3] if len(al) > 3 else 0.0
        else:
            peak, length = SFX[f]
        st = beat - peak; ms = m0
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
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": {k: round(v, 3) for k, v in B.items()},
              "TOTAL": TOTAL, "CAP": CAPF}
    html = tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False))
    open(os.path.join(ROOT, "index.html"), "w").write(html)
    print("index.html written:", len(CUES), "sfx cues, total", TOTAL)
    for k, v in CAPF.items():
        print(" ", k, " / ".join(" ".join(f"{w}@{t}" for w, t in line) for line in v))
    check_speech()

if __name__ == "__main__":
    main()
