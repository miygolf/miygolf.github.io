#!/usr/bin/env python3
"""Writes index.html for the Templer Park round compilation: yardage-book chapter tabs, round tracker, captions, a few SFX.
Film times from edit/timeline.json (tools/build_aroll.py). Caption word times are faster-whisper word starts from the per-video projects
(large-v3 pinned) and this folder's transcripts, mapped onto the film through the voice placements. No music.
Run from the project folder:  python3 tools/build_index.py
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
VOICE = TL["_voice"]; TOTAL = TL["_total"]; B = TL["_beats"]
S = lambda n: TL[n]["start"]; E = lambda n: TL[n]["end"]


def film(t, clip):
    for c, a, b, ft in VOICE:
        if c == clip and a - 1e-3 <= t <= b + 1e-3:
            return round(ft + (t - a), 3)
    raise ValueError(f"{clip} {t} not in film")


# chapter key -> (number, title, sub, record time, side)
CH = {
    "chip": ("01", "Chipping 101", "bola tengah · weight kiri · face normal", "07:40", "L"),
    "duff": ("02", "Coach pun duff", "part of the game 😅", "08:27", "R"),
    "pin": ("03", "Hantar pin", "dalam hole terus", "08:54", "L"),
    "bunker": ("04", "Bunker", "±20 ft · stock shot", "09:00", "L"),
    "downhill": ("05", "Downhill lie", "bola suka lari kiri", "10:01", "L"),
    "tee": ("06", "Tee shot", "dalam kabus", "10:12", "L"),
    "m80": ("07", "80 meter", "approach", "10:19", "L"),
    "rm50": ("08", "Chip in = RM50?", "30 meter", "11:05", "R"),
    "divot": ("09", "Divot cam", "dari bawah", "11:30", "L"),
    "h18": ("10", "Hole 18", "iconic hole, Templer Park", "11:36", "L"),
}
CHAP = [(k, t) for k, t in TL["_chapters"] if k in CH]

# captions: (clip, [(word, t) | "/"], end, top?)   * = key word
CAPS = [
    ("IMG_0176", [("Okay,", 4.82), ("*ball", 5.36), ("*position", 5.56), "/", ("saya", 5.86), ("akan", 6.14), ("letak", 6.34), ("kat", 6.62), ("*tengah.", 6.72)], 7.00),
    ("IMG_0176", [("Slightly", 7.98), ("*depan", 8.46), ("*sikit,", 8.86), ("tak", 9.08), ("apa.", 9.20)], 9.34),
    ("IMG_0176", [("*Weight", 9.92), ("pula", 10.40), ("*kiri.", 10.60)], 10.92),
    ("IMG_0176", [("Club", 15.32), ("face", 15.36), ("*normal", 15.44), ("je,", 16.00), "/", ("tak", 16.30), ("perlu", 16.58), ("*buka", 17.10), ("pun.", 17.44)], 17.62),
    ("IMG_0192", [("Jangan", 5.98), ("gerak,", 6.38), ("kita", 6.72), ("nak", 6.82), "/", ("*hantar", 6.98), ("*pin", 7.18), ("dalam", 7.84), ("*hole.", 8.06)], 8.50),
    ("IMG_0193", [("Favourite", 0.80), ("*bunker", 1.04), ("nampaknya…", 1.30), "/", ("hari", 2.20), ("ni?", 2.36)], 2.70),
    ("IMG_0193", [("Bunker", 2.86), ("*sahaja.", 3.44)], 3.84),
    ("IMG_0193", [("Almost", 9.56), ("similar,", 10.16), "/", ("about", 10.70), ("*20", 10.92), ("*feet.", 11.24)], 11.90),
    ("IMG_0193", [("Kita", 11.92), ("main", 12.22), ("*stock", 12.38), ("*shot.", 12.60)], 12.90),
    ("IMG_0193", [("What", 22.94), ("a", 23.42), ("*player!", 23.62), ("🔥", 23.62)], 24.10, "top"),
    ("IMG_0203", [("So", 10.80), ("lie", 11.78), ("dia", 12.16), ("ni", 12.44), "/", ("*menurun", 12.66), ("macam", 13.26), ("ni.", 13.48)], 13.74),
    ("IMG_0203", [("The", 20.52), ("tendency", 20.64), ("normally,", 20.92), ("this", 21.24), ("kind", 21.62), ("of", 21.80), ("lie,", 21.90), "/",
                  ("memang", 22.08), ("bola", 22.44), ("pergi", 22.58), ("*kiri.", 22.76)], 23.12),
    ("IMG_0203", [("*Ball", 31.14), ("*position", 31.50), ("*tengah,", 31.92), "/", ("saya", 32.62), ("maintain.", 32.70)], 33.00),
    ("IMG_0203", [("Apa-apa", 33.00), ("jenis", 33.76), ("lie", 34.34), ("pun", 34.58), "/", ("saya", 34.82), ("maintain", 34.94), ("*tengah.", 35.24)], 35.74),
    ("IMG_0203", [("*Pegang", 36.20), ("*pendek.", 37.14)], 37.54),
    ("IMG_0203", [("Tapi", 45.80), ("cuba", 46.68), ("letak", 47.42), ("*weight", 47.76), ("tu", 47.96), "/", ("belah", 48.16), ("*kaki", 48.54), ("*kiri.", 48.84)], 49.08),
    ("IMG_0206", [("KD", 0.00), ("cakap", 0.88), ("*80", 1.32), ("*meter.", 1.64)], 2.30),
    ("IMG_0211", [("*30", 1.64), ("*meter.", 3.12)], 3.30),
    ("IMG_0211", [("Chip", 3.38), ("in,", 4.68), ("*chip", 4.86), ("*in.", 5.58)], 5.80),
    ("IMG_0211", [("*50", 5.86), ("*ringgit.", 6.30)], 7.20),
    ("IMG_0211", [("Tak", 26.82), ("*dapat.", 28.22)], 28.60),
    ("IMG_0216", [("*Iconic", 4.90), ("*hole,", 5.26), "/", ("Templer", 5.58), ("Park,", 6.38), ("*18.", 6.64)], 7.20),
]


def seg_end_at(t):
    return min(v["end"] for k, v in TL.items() if not k.startswith("_") and v["start"] <= t + 1e-3 < v["end"])


def caps_html():
    out, data = [], []
    for i, c in enumerate(CAPS):
        clip, ws, end = c[0], c[1], c[2]
        words = [w for w in ws if w != "/"]
        t0 = film(words[0][1], clip) - 0.10
        t1 = max(film(end, clip) + 0.12, t0 + 0.5 + 0.3 * len(words) + 0.1)
        t1 = min(t1, seg_end_at(t0 + 0.11) - 0.04)
        if i + 1 < len(CAPS):
            nx = CAPS[i + 1]; t1 = min(t1, film(next(w for w in nx[1] if w != "/")[1], nx[0]) - 0.10)
        parts = []
        for w in ws:
            if w == "/": parts.append("<br>"); continue
            txt, t = w; hot = txt.startswith("*"); txt = txt.lstrip("*")
            if any(ord(ch) > 0x2600 for ch in txt): parts.append(f'<span class="emo">{txt}</span>'); continue
            parts.append(f'<span class="{"w hot" if hot else "w"}" data-t="{film(min(t, end), clip):.3f}">{html.escape(txt)}</span>')
        body = " ".join(parts).replace(" <br> ", "<br>")
        cls = "ov cap top" if len(c) > 3 else "ov cap"
        out.append(f'<div id="cap{i}" class="{cls}">{body}</div>')
        data.append({"t0": round(t0, 3), "t1": round(t1, 3)})
    return "\n      ".join(out), data


def tabs_html():
    out = []
    for k, t in CHAP:
        n, title, sub, rec, side = CH[k]
        pos = "left:60px;" if side == "L" else "right:150px;"
        out.append(f'<div id="tab-{k}" class="ov tab" style="{pos}"><div class="no">{n}</div><div class="tx"><div class="tt">{html.escape(title)}</div>'
                   f'<div class="sb">{sub}</div></div><div class="tm mono">{rec}</div></div>')
    return "\n      ".join(out)


SFX = {"2380.mp3": (0.29, 0.55), "2367.mp3": (0.06, 0.65)}
CUES = [(S("title") + 0.15, "2367.mp3", 0.28, "title written")] + [(t + 0.05, "2380.mp3", 0.26, f"tab {k}") for k, t in CHAP] + \
       [(S("end_freeze") + 0.1, "2367.mp3", 0.26, "end card written")]


def audio_tags():
    L = [f'      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>']
    busy = {}
    for i, (beat, f, vol, note) in enumerate(sorted(CUES)):
        peak, length = SFX[f]; st = max(0.0, beat - peak); length = min(length, TOTAL - st)
        trk = next(k for k in range(12, 60) if busy.get(k, -1) <= st); busy[trk] = st + length
        L.append(f'      <audio data-hf-id="hf-s{i:02d}" id="sfx-{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{st:.3f}" data-duration="{length:.2f}" '
                 f'data-track-index="{trk}" data-volume="{vol}" data-audio-group="sfx"></audio> <!-- {note} -->')
    return "\n".join(L)


def main():
    caps, capdata = caps_html()
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": B, "TOTAL": TOTAL, "CAP": capdata,
              "CHAP": [[k, round(t, 3), round((CHAP[i + 1][1] if i + 1 < len(CHAP) else S("end_freeze")), 3)] for i, (k, t) in enumerate(CHAP)]}
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{CAPS}}", caps).replace("{{TABS}}", tabs_html())
              .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written, total", TOTAL)
    for c, d in zip(CAPS, capdata):
        print(f"  {d['t0']:6.2f}-{d['t1']:6.2f}", " ".join(w[0] if w != "/" else "/" for w in c[1]))


if __name__ == "__main__":
    main()
