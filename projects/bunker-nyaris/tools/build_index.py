#!/usr/bin/env python3
"""Writes index.html: the whole HyperFrames timeline (A-roll, neon signs, captions, ball tracker, SFX) from one place.

Film times come from edit/timeline.json (tools/build_aroll.py). Word times are faster-whisper word starts (edit/transcript.txt,
pinned with cropped re-runs), mapped onto the film through the voice placements build_aroll.py recorded.
SFX start = picture beat - file peak. No music (owner's call).

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
BALL = json.load(open(os.path.join(ROOT, "edit", "ball_roll.json")))


def film(t, clip=1):
    for c, a, b, ft in VOICE:
        if c == clip and a - 1e-3 <= t <= b + 1e-3:
            return round(ft + (t - a), 3)
    raise ValueError(f"clip{clip} {t} is not in the film")


# ---- captions (source seconds). "/" = line break, * = key word (neon) ----
# Only lines the passes agree on. The opening question from behind the phone is not captioned (passes disagree).
CAPS = [
    dict(words=[("Bunker", 2.86), ("*sahaja.", 3.44)], end=3.84),
    dict(words=[("Almost", 9.56), ("similar,", 10.16), "/", ("about", 10.70), ("*20", 10.92), ("*feet.", 11.24)], end=11.90),
    dict(words=[("Kita", 11.92), ("main", 12.22), ("*stop", 12.38), ("*shot.", 12.60)], end=12.90),
    dict(words=[("What", 22.94), ("a", 23.42), ("*player!", 23.62), ("🔥", 23.62)], end=24.10),
]


def caps_html():
    out, data = [], []
    for i, c in enumerate(CAPS):
        parts, words = [], [w for w in c["words"] if w != "/"]
        t0 = film(words[0][1]) - 0.10
        t1 = film(min(c["end"], 24.38)) + 0.12
        t1 = max(t1, t0 + 0.5 + 0.3 * len(words) + 0.1)      # readable floor, may run past the spoken end
        seg_end = min(v["end"] for k, v in TL.items() if not k.startswith("_") and v["start"] <= t0 + 0.11 < v["end"])
        if seg_end < TL["plan"]["end"] - 1e-3 or seg_end > TL["plan"]["end"] + 1e-3:
            t1 = min(t1, seg_end - 0.06)                           # never across a cut (the plan line may run into the address)
        if i + 1 < len(CAPS):
            t1 = min(t1, film(next(w for w in CAPS[i + 1]["words"] if w != "/")[1]) - 0.12)
        for w in c["words"]:
            if w == "/":
                parts.append("<br>"); continue
            txt, t = w
            hot = txt.startswith("*"); txt = txt.lstrip("*")
            emo = any(ord(ch) > 0x2600 for ch in txt)
            if emo:
                parts.append(f'<span class="emo">{txt}</span>')
            else:
                parts.append(f'<span class="{"w hot" if hot else "w"}" data-t="{film(t):.3f}">{html.escape(txt)}</span>')
        body = " ".join(parts).replace(" <br> ", "<br>")
        out.append(f'<div id="cap{i}" class="ov cap">{body}</div>')
        data.append({"t0": round(t0, 3), "t1": round(t1, 3)})
    return "\n      ".join(out), data


CAPHTML, CAPDATA = caps_html()

# ---- positions (film px) ----
HOOK_CUP = (569, 1083)      # cup on the hook freeze (zoom 2.05 @ src (1180, 2480)); refined on the snapshot
ROLL_CUP = (590, 1280)      # cup when the ball passes it in the roll (film 10.11)
# ball tracker: smoothed (5-frame mean) positions from edit/ball_roll.json, every 3rd frame
sm = []
for i in range(len(BALL)):
    w = BALL[max(0, i - 2):i + 3]
    sm.append([BALL[i][0], round(sum(p[1] for p in w) / len(w)), round(sum(p[2] for p in w) / len(w))])
TRACK = sm[::3] + [sm[-1]]

# ---- SFX: file -> (peak s, usable length s) ----  Mixkit ids, see assets/sfx/CREDITS.md
SFX = {
    "2595.mp3": (0.12, 0.47), "2594.mp3": (0.02, 0.24), "2365.mp3": (0.02, 0.14), "2582.mp3": (0.01, 0.10),
    "2596.mp3": (0.83, 1.40), "786.mp3": (3.86, 1.45), "2125.mp3": (0.16, 0.30), "2498.mp3": (0.17, 0.50),
    "2364.mp3": (0.01, 0.14), "1491.mp3": (0.30, 0.40), "1464.mp3": (0.11, 0.24), "2586.mp3": (1.55, 1.70),
    "3201.mp3": (0.60, 0.60),
}
CUES = [
    (0.02, "2582.mp3", 0.45, "sign switches on, frame 0"),
    (0.06, "2595.mp3", 0.5, "neon tube flickers on"),
    (0.30, "2594.mp3", 0.35, "second word catches"),
    (B["hook_cup"], "2365.mp3", 0.6, "freeze: cup ring snaps on"),
    (B["hook_cup"] + 0.05, "3201.mp3", 0.35, "ring hum"),
    (B["hook_cup"] + 0.42, "2364.mp3", 0.35, "😱 pops"),
    (S("walk") - 0.02, "2596.mp3", 0.38, "neon scan wipe out of the hook"),
    (B["w_20"] + 0.18, "2365.mp3", 0.35, "≈ 20 FT sign"),
    (B["w_stop"] + 0.16, "2595.mp3", 0.4, "STOP SHOT sign flickers on (low: under the word)"),
    (B["w_stop"] + 0.60, "2594.mp3", 0.30, "STOP SHOT buzz, after the word"),
    (B["shot_impact"], "2125.mp3", 0.30, "strike layer on the real one"),
    (B["shot_impact"] + 0.03, "2498.mp3", 0.45, "sand splash"),
    (B["roll_cup"], "786.mp3", 0.30, "riser from the impact, peaks as the ball reaches the cup"),
    (S("whip") + 0.30, "1491.mp3", 0.45, "camera whip to the green"),
    (S("whip") + 0.32, "2596.mp3", 0.25, "neon scan rides the whip"),
    (S("roll") + 0.15, "2582.mp3", 0.30, "tracker ring locks on the ball"),
    (B["roll_cup"] + 0.02, "2365.mp3", 0.4, "cup ring pulse"),
    (B["roll_cup"] + 0.10, "2595.mp3", 0.4, "NYARIS! sign (low: the reaction starts)"),
    (S("replay") - 0.02, "2596.mp3", 0.32, "neon scan into the replay"),
    (B["replay_impact"], "2125.mp3", 0.28, "replay strike layer"),
    (B["replay_impact"] + 0.03, "2498.mp3", 0.42, "replay sand"),
    (S("end_freeze") + 0.02, "2582.mp3", 0.45, "end sign switch"),
    (S("end_freeze") + 0.06, "2595.mp3", 0.45, "end sign flickers on"),
    (S("end_freeze") + 0.55, "2365.mp3", 0.35, "sub line"),
    (S("end_freeze") + 1.00, "2364.mp3", 0.35, "CTA plate"),
]
SPEECH = [(ft, ft + b - a) for c, a, b, ft in VOICE if b - a < 5]


def audio_tags():
    L = [f'      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" '
         f'data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>',
         "      <!-- sound design: Mixkit ids (assets/sfx/CREDITS.md). start = picture beat - file peak. No music. -->"]
    busy = {}
    for i, (beat, f, vol, note) in enumerate(sorted(CUES)):
        peak, length = SFX[f]
        st = beat - peak; ms = 0.0
        if f == "786.mp3":           # riser: the last 1.45 s up to its peak
            ms = 3.86 - length; st = beat - length
        if st < 0: ms += -st; length += st; st = 0.0
        length = min(length, TOTAL - st)
        trk = next(k for k in range(12, 60) if busy.get(k, -1) <= st)
        busy[trk] = st + length
        mattr = f' data-media-start="{ms:.3f}"' if ms > 0 else ""
        L.append(f'      <audio data-hf-id="hf-s{i:02d}" id="sfx-{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{st:.3f}" '
                 f'data-duration="{length:.2f}"{mattr} data-track-index="{trk}" data-volume="{vol}" data-audio-group="sfx"></audio> <!-- {note} -->')
    return "\n".join(L)


def check_speech():
    for beat, f, vol, note in CUES:
        peak, length = SFX[f]
        st, en = beat - peak, beat - peak + length
        for a, b in SPEECH:
            if st < b and en > a and vol > 0.4 and f not in ("2125.mp3", "2498.mp3"):
                print(f"  ! loud cue over speech: {note} ({st:.2f}-{en:.2f}, vol {vol})")


def main():
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": B, "TOTAL": TOTAL, "CAP": CAPDATA,
              "HOOK_CUP": HOOK_CUP, "ROLL_CUP": ROLL_CUP, "TRACK": TRACK}
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{CAPS}}", CAPHTML)
              .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written:", len(CUES), "sfx cues, total", TOTAL)
    for c, d in zip(CAPS, CAPDATA):
        print(f"  {d['t0']:6.2f}-{d['t1']:6.2f}", " ".join(w[0] if w != "/" else "/" for w in c["words"]))
    check_speech()


if __name__ == "__main__":
    main()
