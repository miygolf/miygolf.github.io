#!/usr/bin/env python3
"""Writes index.html: the whole HyperFrames timeline (A-roll, leaflet panels, chips, flight line, captions, SFX) from one place.

Film times come from edit/timeline.json (build_aroll.py). Word times are faster-whisper word starts (edit/transcript.json,
pinned with cropped re-runs, tools/pin_words.py), mapped onto the film through the voice placements build_aroll.py recorded.
SFX start = picture beat - file peak. No music (owner's call for this video, and the house rule for finals).

Run from the project folder:  python3 tools/build_index.py
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
B = dict(TL["_beats"])
VOICE = TL["_voice"]
S = lambda n: TL[n]["start"]
E = lambda n: TL[n]["end"]
TOTAL = TL["_total"]


def film(t, clip=1):
    for c, a, b, ft in VOICE:
        if c == clip and a - 1e-3 <= t <= b + 1e-3:
            return round(ft + (t - a), 3)
    raise ValueError(f"clip{clip} {t} is not in the film")


# ---- captions: the spoken words (source seconds). "/" = line break inside the strip, * = key word (cyan underline) ----
# Only lines both whisper passes agree on. The narrator's reaction over the replay is not captioned (passes disagree).
CAPS = [
    dict(words=[("Coach", 0.00), ("Farhan,", 0.16), ("ni", 0.64), ("nak", 2.38), "/", ("buat", 2.54), ("*macam", 2.66), ("*mana", 2.78), ("ni?", 2.94), ("🤔", 2.94)], end=3.10),
    dict(words=[("Ada", 3.46), ("*tip", 3.90), ("tak?", 4.24)], end=4.42),
    dict(words=[("Kita", 4.78), ("ada", 5.22), ("*plenty", 5.40), "/", ("*of", 5.62), ("*green", 6.00), ("to", 6.30), ("play.", 6.52)], end=7.10),
    dict(words=[("Silap", 11.54), ("bawa", 11.80), ("kayu,", 11.94), ("bawa", 12.22), ("*60", 12.28), ("😅", 12.30)], end=12.56, lead=11.34),
    dict(words=[("So", 12.74), ("kita", 12.90), ("try", 12.98), ("to", 13.26), ("do", 13.46), "/", ("*normal", 14.26), ("*pitch,", 14.58)], end=14.98),
    dict(words=[("But", 15.46), ("then", 15.90), ("you", 16.10), ("kena", 16.22), ("make", 16.38), ("sure", 16.52), "/", ("you", 16.74), ("*accelerate", 16.94)], end=17.88),
    dict(words=[("Kita", 26.18), ("*visualize", 26.36), ("mana", 26.80), ("you", 27.06)], end=27.26, left=True),
    dict(words=[("nak", 27.26), ("hantar", 27.34), ("bola", 28.46), ("tu.", 28.60)], end=28.88, left=True),
    dict(words=[("Normal", 30.80), ("pitch.", 30.96)], end=31.40),
    dict(words=[("Let's", 39.78), ("go!", 40.42), ("⛳", 40.45)], end=40.80),
]


def caps_html():
    out, data = [], []
    for i, c in enumerate(CAPS):
        parts, words = [], [w for w in c["words"] if w != "/"]
        t0 = film(c["lead"]) if "lead" in c else film(words[0][1]) - 0.10
        t1 = film(c["end"]) + 0.12
        if i + 1 < len(CAPS):
            t1 = min(t1, film(next(w for w in CAPS[i + 1]["words"] if w != "/")[1]) - 0.12)
        for w in c["words"]:
            if w == "/":
                parts.append("<br>"); continue
            txt, t = w
            hot = txt.startswith("*"); txt = txt.lstrip("*")
            emo = any(ord(ch) > 0x2600 for ch in txt)
            cls = "emo" if emo else ("w hot" if hot else "w")
            ft = film(min(t, c["end"]))
            if emo:
                parts.append(f'<span class="{cls}">{txt}</span>')
            else:
                parts.append(f'<span class="{cls}" data-t="{ft:.3f}">{html.escape(txt)}</span>')
        body = " ".join(parts).replace(" <br> ", "<br>")
        style = ' style="left:60px; transform:none;"' if c.get("left") else ""
        out.append(f'<div id="cap{i}" class="ov cap"{style}>{body}</div>')
        data.append({"t0": round(t0, 3), "t1": round(t1, 3)})
    return "\n      ".join(out), data


CAPHTML, CAPDATA = caps_html()

W = {
    "normal": film(14.26), "accel": film(16.94), "visual": film(26.36), "sixty": film(12.32),
}
TICK = [S("shot") + 0.75, S("shot") + 1.15, S("shot") + 1.55]
END = S("letsgo") + 0.25      # end leaflet opens as he turns to the camera

# flight line for step 3: from the ball (film ~(618,1415)) out to the right over the lip (green side), clear of the legs and the caption
FLY = "M 622 1398 Q 752 1010 900 1050"
LX, LY = 900, 1050

# speech windows on the film (for keeping SFX off the voice)
SPEECH = [(ft, ft + b - a) for c, a, b, ft in VOICE]

# ---- SFX: file -> (peak s, usable length s) ----  Mixkit ids, see assets/sfx/CREDITS.md
SFX = {
    "1530.mp3": (0.36, 0.50), "2380.mp3": (0.42, 0.80), "2384.mp3": (0.10, 0.34), "2364.mp3": (0.01, 0.14),
    "2121.mp3": (0.17, 0.40), "772.mp3": (0.41, 0.75), "166.mp3": (0.30, 0.68),
    "3115.mp3": (0.12, 0.30), "1489.mp3": (0.71, 1.40), "1364.mp3": (0.04, 0.20), "2357.mp3": (0.13, 0.32),
    "3005.mp3": (0.03, 0.17), "1146.mp3": (1.79, 2.10),
}
F = lambda st: st          # readability
CUES = [
    (0.02, "1530.mp3", 0.26, "title panel on frame 0 (low: the question starts at once)"),
    (B["hook_impact"], "2121.mp3", 0.30, "strike, layered on the real one (0.5x)"),
    (B["hook_impact"] + 0.02, "772.mp3", 0.24, "freeze weight under the flash"),
    (S("hook_freeze") + 0.32, "2364.mp3", 0.30, "3 STEP JE tag snaps on"),
    (S("sit") - 0.12, "166.mp3", 0.30, "accordion-fold wipe in"),
    (S("sit") + 0.02, "2380.mp3", 0.30, "panels fold away"),
    (S("sit") + 0.30, "1530.mp3", 0.24, "SITUASI panel unfolds"),
    (B["green_point"] - 0.05, "2357.mp3", 0.22, "GREEN chip"),
    (W["sixty"] + 0.22, "3005.mp3", 0.20, "KAYU 60 chip (after the word)"),
    (W["normal"] + 0.14, "2380.mp3", 0.28, "step 1 panel unfolds"),
    (W["normal"] + 0.18, "2364.mp3", 0.22, "step 1 disc"),
    (W["accel"] + 0.14, "2380.mp3", 0.14, "step 2 panel unfolds (quiet: 'accelerate' is soft)"),
    (W["accel"] + 0.72, "1364.mp3", 0.22, "warning triangle lands, after the word"),
    (W["visual"] + 0.14, "2380.mp3", 0.28, "step 3 panel unfolds"),
    (W["visual"] + 0.70, "1489.mp3", 0.20, "flight line draws out"),
    (W["visual"] + 0.80, "2357.mp3", 0.22, "landing ring"),
    (TICK[0], "2364.mp3", 0.22, "checklist tick 1"),
    (TICK[1], "2364.mp3", 0.22, "checklist tick 2"),
    (TICK[2], "2364.mp3", 0.24, "checklist tick 3"),
    (B["shot_impact"], "1146.mp3", 0.16, "soft build through the backswing, peaks on the strike"),
    (B["shot_impact"], "2121.mp3", 0.40, "strike, layered on the real one"),
    (S("replay") - 0.12, "3115.mp3", 0.42, "fold wipe into the replay"),
    (S("replay") + 0.04, "2384.mp3", 0.34, "panels fold away"),
    (B["replay_impact"], "2121.mp3", 0.34, "replay strike layer"),
    (B["replay_impact"] + 0.20, "1364.mp3", 0.30, "ACCELERATE stamp lands"),
    (END + 0.36, "1530.mp3", 0.28, "end leaflet unfolds"),
    (END + 0.36, "2364.mp3", 0.20, "row 1"), (END + 0.56, "2364.mp3", 0.20, "row 2"), (END + 0.76, "2364.mp3", 0.22, "row 3"),
    (END + 1.16, "3005.mp3", 0.26, "SAVE tag"),
]


def check_speech():
    for beat, f, vol, note in CUES:
        peak, length = SFX[f]
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
        peak, length = SFX[f]
        st = beat - peak; ms = 0.0
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
              "TOTAL": TOTAL, "CAP": CAPDATA, "W": W, "TICK": [round(x, 3) for x in TICK], "END": round(END, 3)}
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{CAPS}}", CAPHTML)
              .replace("{{FLY}}", FLY).replace("{{LX}}", str(LX)).replace("{{LY}}", str(LY))
              .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written:", len(CUES), "sfx cues, total", TOTAL)
    print("W", W, "END", END)
    for c, d in zip(CAPS, CAPDATA):
        print(f"  {d['t0']:6.2f}-{d['t1']:6.2f}", " ".join(w[0] if w != "/" else "/" for w in c["words"]))
    check_speech()


if __name__ == "__main__":
    main()
