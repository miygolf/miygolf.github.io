#!/usr/bin/env python3
"""Writes index.html: the whole HyperFrames timeline (A-roll, spirit-level cards, ground marks, captions, SFX) from one place.

Film times come from edit/timeline.json (tools/build_aroll.py). Word times are faster-whisper large-v3 word starts (edit/transcript.txt,
pinned with cropped re-runs), mapped onto the film through the voice placements build_aroll.py recorded.
Ground marks ride the ball (edit/ball_track.json, tracked on the A-roll). SFX start = picture beat - file peak. No music.

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
TRACK = json.load(open(os.path.join(ROOT, "edit", "ball_track.json")))


def film(t, clip=1):
    for c, a, b, ft in VOICE:
        if c == clip and a - 1e-3 <= t <= b + 1e-3:
            return round(ft + (t - a), 3)
    raise ValueError(f"clip{clip} {t} is not in the film")


# ---- captions (source seconds). "/" = line break, * = key word ----
CAPS = [
    dict(words=[("So", 10.80), ("lie", 11.78), ("dia", 12.16), ("ni", 12.44), "/", ("*menurun", 12.66), ("macam", 13.26), ("ni.", 13.48)], end=13.74),
    dict(words=[("Nak", 17.58), ("buat", 18.12), ("apa?", 18.34), ("🤔", 18.34)], end=18.50),
    dict(words=[("The", 20.52), ("tendency", 20.64), ("normally,", 20.92), ("this", 21.24), ("kind", 21.62), ("of", 21.80), ("lie,", 21.90), "/",
                ("memang", 22.08), ("bola", 22.44), ("pergi", 22.58), ("*kiri.", 22.76)], end=23.12, small=True),
    dict(words=[("*Ball", 31.14), ("*position", 31.50), ("*tengah,", 31.92), "/", ("saya", 32.62), ("maintain.", 32.70)], end=33.00),
    dict(words=[("Apa-apa", 33.00), ("jenis", 33.76), ("lie", 34.34), ("pun", 34.58), "/", ("saya", 34.82), ("maintain", 34.94), ("*tengah.", 35.24)], end=35.74),
    dict(words=[("*Pegang", 36.20), ("*pendek.", 37.14)], end=37.54),
    dict(words=[("Then", 37.62), ("buat", 38.30), ("tu", 38.52), ("*practice", 38.64), ("*swing", 38.92), ("tu.", 39.54)], end=39.70),
    dict(words=[("Korang", 39.78), ("kena", 40.42), ("make", 40.56), ("sure", 40.74), "/", ("*low", 40.92), ("*point", 41.08), ("korang", 41.40), ("kat", 41.82), ("mana.", 41.94)], end=42.10),
    dict(words=[("Kena", 42.12), ("kat", 42.96), ("*sini", 43.10), ("ke,", 43.40), "/", ("kena", 43.68), ("kat", 44.10), ("*sini", 44.22), ("ke", 44.48), ("kan.", 44.76)], end=45.00),
    dict(words=[("Tapi", 45.80), ("cuba", 46.68), ("letak", 47.42), ("*weight", 47.76), ("tu", 47.96), "/", ("belah", 48.16), ("*kaki", 48.54), ("*kiri.", 48.84)], end=49.08),
    dict(words=[("So", 50.64), ("supaya", 51.24), ("kena", 51.84), ("bola", 52.08), ("*direct.", 52.30)], end=52.55),
]


def caps_html():
    out, data = [], []
    for i, c in enumerate(CAPS):
        parts, words = [], [w for w in c["words"] if w != "/"]
        t0 = film(words[0][1]) - 0.10
        t1 = film(c["end"]) + 0.12
        t1 = max(t1, t0 + 0.5 + 0.3 * len(words) + 0.1)
        seg_end = min(v["end"] for k, v in TL.items() if not k.startswith("_") and v["start"] <= t0 + 0.11 < v["end"])
        t1 = min(t1, seg_end - 0.04) if i + 1 < len(CAPS) and seg_end < film(next(w for w in CAPS[i + 1]["words"] if w != "/")[1]) else t1
        if i + 1 < len(CAPS):
            t1 = min(t1, film(next(w for w in CAPS[i + 1]["words"] if w != "/")[1]) - 0.12)
        else:
            t1 = min(t1, seg_end - 0.04)
        for w in c["words"]:
            if w == "/":
                parts.append("<br>"); continue
            txt, t = w
            hot = txt.startswith("*"); txt = txt.lstrip("*")
            if any(ord(ch) > 0x2600 for ch in txt):
                parts.append(f'<span class="emo">{txt}</span>')
            else:
                parts.append(f'<span class="{"w hot" if hot else "w"}" data-t="{film(t):.3f}">{html.escape(txt)}</span>')
        body = " ".join(parts).replace(" <br> ", "<br>")
        sty = ' style="font-size:42px;"' if c.get("small") else ""
        out.append(f'<div id="cap{i}" class="ov cap"{sty}>{body}</div>')
        data.append({"t0": round(t0, 3), "t1": round(t1, 3)})
    return "\n      ".join(out), data


CAPHTML, CAPDATA = caps_html()

# ---- ground marks: offsets from the ball (film px), measured at 12.0 and 26.5 ----
FOOT_L = (-112, -235)     # screen-left foot = the coach's right foot
FOOT_R = (138, -210)      # screen-right foot = the coach's LEFT foot (face-on, right-hander)
HANDS = (60, -530)
W = {k: round(v, 3) for k, v in B.items()}
W["sini1"] = film(43.10); W["sini2"] = film(44.22)


def smooth(pts, n=2):
    out = []
    for i in range(len(pts)):
        w = pts[max(0, i - n):i + n + 1]
        out.append([pts[i][0], round(sum(p[1] for p in w) / len(w)), round(sum(p[2] for p in w) / len(w))])
    return out


BALL = {k: smooth(v)[::2] for k, v in TRACK.items()}

# ---- SFX: file -> (peak s, usable length s) ----  Mixkit ids, see assets/sfx/CREDITS.md
SFX = {
    "1124.mp3": (0.11, 0.18), "2357.mp3": (0.24, 0.32), "3000.mp3": (0.05, 0.45), "2858.mp3": (0.23, 0.45),
    "2364.mp3": (0.01, 0.14), "2121.mp3": (0.14, 0.40), "2126.mp3": (0.17, 0.45), "1491.mp3": (0.30, 0.40),
    "1489.mp3": (0.71, 1.0), "166.mp3": (0.30, 0.60), "3005.mp3": (0.03, 0.17), "2568.mp3": (0.00, 0.10), "1120.mp3": (0.10, 0.14),
}
STEP_T = {"lie": S("lie") + 0.25, "tend": W["w_tendency"] - 0.1, "s1": W["w_tengah"] - 0.25, "s2": W["w_pendek"] - 0.5,
          "s3": W["w_practice"] - 0.2, "s4": W["w_weight"] - 0.25, "end": S("end_freeze") + 0.05}
CUES = [
    (0.03, "2858.mp3", 0.35, "level card locks on, frame 0"),
    (0.40, "3000.mp3", 0.35, "bubble settles to centre"),
    (B["hook_impact"], "2126.mp3", 0.28, "strike layer on the real one"),
    (S("hook_freeze") + 0.02, "1120.mp3", 0.5, "freeze tick"),
    (S("hook_b") + 0.05, "2364.mp3", 0.35, "4 STEP tag"),
    (S("lie") - 0.04, "166.mp3", 0.35, "tilt wipe into the lie"),
]
for k in ("lie", "tend", "s1", "s2", "s3", "s4"):
    t = STEP_T[k]
    CUES += [(t, "2858.mp3", 0.30, f"{k} card slides in tilted"), (t + 0.42, "3000.mp3", 0.30, f"{k} bubble levels")]
CUES += [
    (W["w_menurun"] + 0.1, "2357.mp3", 0.25, "slope vial tips"),
    (W["w_kiri"] + 0.05, "1489.mp3", 0.25, "curve draws left in the diagram"),
    (W["w_tengah"] + 0.15, "2568.mp3", 0.5, "stance bracket + centre tick"),
    (W["w_pendek"] + 0.1, "1124.mp3", 0.5, "grip ring"),
    (W["w_lowpoint"] + 0.1, "2357.mp3", 0.25, "low point ring"),
    (W["sini1"] + 0.05, "1124.mp3", 0.45, "here?"),
    (W["sini2"] + 0.05, "1124.mp3", 0.45, "or here?"),
    (W["w_kakikiri"] + 0.1, "2568.mp3", 0.5, "left-foot arrow"),
    (W["w_direct"] + 0.1, "2357.mp3", 0.25, "ball-first ring"),
    (S("shot") - 0.04, "166.mp3", 0.35, "tilt wipe into the shot"),
    (B["shot_impact"], "2121.mp3", 0.30, "strike layer"),
    (S("pan") + 0.1, "1491.mp3", 0.35, "camera follows the ball"),
    (STEP_T["end"], "2858.mp3", 0.35, "recap card"),
    (STEP_T["end"] + 0.45, "3000.mp3", 0.30, "recap bubble levels"),
    (STEP_T["end"] + 0.55, "1124.mp3", 0.4, "row 1"), (STEP_T["end"] + 0.72, "1124.mp3", 0.4, "row 2"),
    (STEP_T["end"] + 0.89, "1124.mp3", 0.4, "row 3"), (STEP_T["end"] + 1.06, "1124.mp3", 0.4, "row 4"),
    (STEP_T["end"] + 1.45, "2364.mp3", 0.35, "SAVE tag"),
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
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": B, "W": W, "TOTAL": TOTAL, "CAP": CAPDATA,
              "BALL": BALL, "STEP": {k: round(v, 3) for k, v in STEP_T.items()}}
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{CAPS}}", CAPHTML)
              .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    for k, v in {"FLX": FOOT_L[0], "FLY": FOOT_L[1], "FRX": FOOT_R[0], "FRY": FOOT_R[1], "HX": HANDS[0], "HY": HANDS[1]}.items():
        out = out.replace("{{" + k + "}}", str(v))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written:", len(CUES), "sfx cues, total", TOTAL)
    for c, d in zip(CAPS, CAPDATA):
        print(f"  {d['t0']:6.2f}-{d['t1']:6.2f}", " ".join(w[0] if w != "/" else "/" for w in c["words"]))


if __name__ == "__main__":
    main()
