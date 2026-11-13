#!/usr/bin/env python3
"""Writes index.html: the whole HyperFrames timeline (A-roll, chalk notes, captions, a few SFX) from one place.

Film times come from edit/timeline.json (tools/build_aroll.py). Word times are faster-whisper word starts (edit/transcript.txt,
pinned with cropped re-runs), mapped onto the film through the voice placements build_aroll.py recorded.
Raw cut: hard cuts, real sound, only four soft chalk SFX (owner: \"kurangkan sfx, biarkan raw\"). No music.

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
    dict(words=[("*30", 1.64), ("*meter.", 3.12)], end=3.30),
    dict(words=[("Chip", 3.38), ("in,", 4.68), ("*chip", 4.86), ("*in.", 5.58)], end=5.80),
    dict(words=[("*50", 5.86), ("*ringgit.", 6.12)], end=7.20),
    dict(words=[("*Masuk!", 20.40)], end=20.95),
    dict(words=[("Tak", 26.82), ("*dapat.", 28.22)], end=28.55),
]


def caps_html():
    out, data = [], []
    for i, c in enumerate(CAPS):
        parts, words = [], [w for w in c["words"] if w != "/"]
        t0 = film(words[0][1]) - 0.10
        t1 = film(c["end"]) + 0.12
        t1 = max(t1, t0 + 0.5 + 0.3 * len(words) + 0.1)      # readable floor, may run past the spoken end
        seg_end = min(v["end"] for k, v in TL.items() if not k.startswith("_") and v["start"] <= t0 + 0.11 < v["end"])
        t1 = min(t1, seg_end - 0.06)                               # never across a cut
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

# ---- SFX: only four, soft ----  Mixkit ids, see assets/sfx/CREDITS.md
SFX = {"2366-write.mp3": (0.10, 0.85), "2372.mp3": (0.03, 0.30), "3085.mp3": (0.39, 0.90)}
CUES = [
    (0.15, "2366-write.mp3", 0.28, "RM50 line chalked under CHIP 101"),
    (S("bet") - 0.30, "3085.mp3", 0.22, "board wiped clean into the story"),
    (B["w_50"] + 0.10, "2372.mp3", 0.22, "RM50 chalked"),
    (S("end_freeze") + 0.10, "2366-write.mp3", 0.28, "HOMEWORK chalked"),
]


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
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": B, "TOTAL": TOTAL, "CAP": CAPDATA}
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{CAPS}}", CAPHTML)
              .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written:", len(CUES), "sfx cues, total", TOTAL)
    for c, d in zip(CAPS, CAPDATA):
        print(f"  {d['t0']:6.2f}-{d['t1']:6.2f}", " ".join(w[0] if w != "/" else "/" for w in c["words"]))


if __name__ == "__main__":
    main()
