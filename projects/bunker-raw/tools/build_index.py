#!/usr/bin/env python3
"""Writes index.html: the whole HyperFrames timeline (A-roll, chalk notes, captions, a few SFX) from one place.

Film times come from edit/timeline.json (tools/build_aroll.py). Word times are faster-whisper word starts (edit/transcript.txt,
pinned with cropped re-runs), mapped onto the film through the voice placements build_aroll.py recorded.
Raw cut: hard cuts, real sound, only five soft chalk SFX (owner: \"kurangkan sfx, biarkan raw\"). No music.

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


# ---- captions (source seconds). "/" = line break, * = key word (neon) ----
# Only lines the passes agree on. The opening question from behind the phone is not captioned (passes disagree).
CAPS = [
    dict(words=[("Favourite", 0.80), ("*bunker", 1.04), ("nampaknya…", 1.30), "/", ("hari", 2.20), ("ni?", 2.36)], end=2.70),
    dict(words=[("Bunker", 2.86), ("*sahaja.", 3.44)], end=3.84),
    dict(words=[("Saya", 4.96), ("boleh", 5.56), ("tunjuk", 5.76), ("banyak", 6.06), ("sikit", 6.36), "/", ("*educational", 6.64), ("*video.", 7.12)], end=7.40),
    dict(words=[("Almost", 9.56), ("similar,", 10.16), "/", ("about", 10.70), ("*20", 10.92), ("*feet.", 11.24)], end=11.90),
    dict(words=[("Kita", 11.92), ("main", 12.22), ("*stop", 12.38), ("*shot.", 12.60)], end=12.90),
    dict(words=[("What", 22.94), ("a", 23.42), ("*player!", 23.62), ("🔥", 23.62)], end=24.10),
]


def caps_html():
    out, data = [], []
    for i, c in enumerate(CAPS):
        parts, words = [], [w for w in c["words"] if w != "/"]
        t0 = film(words[0][1]) - 0.10
        t1 = film(min(c["end"], 25.10)) + 0.12
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
import importlib.util as _u
_sp = _u.spec_from_file_location("ar", os.path.join(ROOT, "tools", "build_aroll.py")); _ar = _u.module_from_spec(_sp); _sp.loader.exec_module(_ar)
_z, _cx, _cy = _ar.HOOK_F[0][1:]
CUP_SRC = (1208, 2600)
HOOK_CUP = (round((CUP_SRC[0] - (_cx - 1080 / _z)) * _z / 2), round((CUP_SRC[1] - (_cy - 1920 / _z)) * _z / 2))
ROLL_CUP = (590, 1280)      # cup as the ball passes it in the roll (film px, roll is unzoomed)
# the handheld camera drifts after the pass: the circle follows the cup = tracked yellow flag + (27, 507) to the pole base
_FL = json.load(open(os.path.join(ROOT, "edit", "flag_roll.json")))
CUPK = [[t, x + 27, y + 507] for t, x, y, n in _FL][::2]

# ---- SFX: only five, soft ----  Mixkit ids, see assets/sfx/CREDITS.md
SFX = {"2366-write.mp3": (0.10, 0.85), "2372.mp3": (0.03, 0.30), "3085.mp3": (0.39, 0.90)}
CUES = [
    (0.15, "2366-write.mp3", 0.28, "stop shot line chalked under BUNKER 101"),
    (B["hook_cup"] + 0.06, "2372.mp3", 0.30, "chalk circle round the cup"),
    (S("q") - 0.30, "3085.mp3", 0.22, "board wiped clean into the story"),
    (B["w_stop"] + 0.40, "2372.mp3", 0.22, "STOP SHOT underlined, after the word"),
    (S("end_freeze") + 0.10, "2366-write.mp3", 0.28, "HOMEWORK chalked"),
]
SPEECH = [(ft, ft + b - a) for c, a, b, ft in VOICE]


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
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": B, "TOTAL": TOTAL, "CAP": CAPDATA,
              "HOOK_CUP": HOOK_CUP, "ROLL_CUP": ROLL_CUP, "CUPK": CUPK}
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{CAPS}}", CAPHTML)
              .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written:", len(CUES), "sfx cues, total", TOTAL)
    for c, d in zip(CAPS, CAPDATA):
        print(f"  {d['t0']:6.2f}-{d['t1']:6.2f}", " ".join(w[0] if w != "/" else "/" for w in c["words"]))


if __name__ == "__main__":
    main()
