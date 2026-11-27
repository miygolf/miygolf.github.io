#!/usr/bin/env python3
"""Writes index.html for "Bola plug" (the follow-up to the bunker video, same "Label Maker" look so the two read as one series):
A-roll, embossed tapes, spoken captions, a few SFX. Film times: edit/timeline.json (tools/build_aroll.py). Word anchors: edit/film_words.json.
Final = real sound + SFX, no music (house rule). Run from the project folder:  python3 tools/build_index.py
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
FW = json.load(open(os.path.join(ROOT, "edit", "film_words.json")))
TOTAL = TL["_total"]; IMP = TL["_impacts"]
S = lambda n: TL[n]["start"]; E = lambda n: TL[n]["end"]
def W(seg, word, nth=0, default=None):
    """film time of the nth word in a segment that contains `word` (crop transcript), else default"""
    hits = [a for a, b, w in FW.get(seg, []) if word.lower() in w.lower()]
    return hits[nth] if len(hits) > nth else (default if default is not None else S(seg))


# sections: tapes stack inside a section and peel off when the next section's first tape prints
SEC = {k: (S(k), E(k)) for k in ("q", "plug", "normal", "fail", "tip", "face", "biar", "hit", "slow", "pan", "end")}
BASE = {"q": 230, "end": 230}          # talking heads: the face is low (q) / close (end) -> tapes at the top
# owner v3 ("align wording a bit higher so viewer can see the club"): every tape starts at y 200 and captions sit at y 640,
# so the club head and the ball (y ~1000-1250 in the sand close-ups) stay clear
# (section, text, colour k/y/r/w, film time, tilt deg, big?) - the coach's own words; "fried egg" is the owner's word from the bunker script
T = [
    ("q", "Korang komen \"bunker\"", "k", 0.0, -1.5, False),
    ("q", "Bola plug? <span class='emo' style='font-size:66px'>🍳</span>", "r", 0.0, 1.5, True),
    ("plug", "Bola plug = fried egg", "y", S("plug") + 0.1, -1.2, True),
    ("normal", "Face terbuka (normal)", "w", S("normal") + 0.05, -1.0, False),
    ("normal", "Bola tak keluar ✗", "r", S("normal2") + 0.4, 1.2, False),
    ("fail", "Contoh: face terbuka", "k", S("fail") + 0.05, -1.0, False),
    ("fail", "Bola kat situ je ✗", "r", IMP["fail"] + 0.5, 1.5, True),
    ("face", "Tip dia:", "k", S("tip") + 0.02, -1.5, True),            # "Tip dia." is a 0.6 s line: its tape stays with the tip
    ("face", "Face terbuka ✗", "w", S("face") + 0.1, -1.0, False),
    ("face", "Tutup face club ✓", "y", S("face2") + 0.05, 1.2, True),
    ("biar", "Biar je macam ni", "w", S("biar") + 0.75, 1.0, False),
    ("biar", "Then pukul", "k", W("biar", "pukul", 0, E("biar") - 0.5) - 0.2, -1.0, False),
    ("hit", "Bola keluar ✓", "y", IMP["hit"] + 0.25, -1.5, True),
    ("slow", "Replay: face tertutup", "k", S("slow") + 0.6, -1.2, False),
    ("pan", "Atas green ✓", "y", S("pan") + 1.6, 1.2, True),
    ("end", "Save. Cuba kat bunker ↓", "y", W("end", "siap", 0, S("end") + 1.4) - 0.2, -1.5, False),
    ("end", "Face terbuka ✗ · tutup ✓", "k", W("end", "siap", 0, S("end") + 1.4) + 0.25, 1.2, False),
]
# spoken captions (cleaned), (text, t0, t1, [top])
CAP = [
    ("Macam mana nak pukul bola plug?", 0.0, E("q") - 0.03, 640),
    ("Ini normal. Kalau korang buat macam ni, bola tak keluar.", S("normal") + 0.03, E("normal2") - 0.03),
    ("Contoh…", S("fail") + 0.05, IMP["fail"] - 0.2),
    ("So bola kat situ je.", IMP["fail"] + 0.6, E("fail") - 0.03),
    ("Tip dia.", S("tip") + 0.02, E("tip") - 0.02),
    ("Instead of club face terbuka, korang tutupkan dia macam ni.", S("face") + 0.03, E("face2") - 0.03),
    ("Biar je macam ni, ni pukul.", S("biar") + 0.03, E("biar") - 0.03),
    ("Okey, itu dia. Siap.", S("end") + 0.3, TOTAL, 640),
]


def tapes():
    out, data, stack = [], [], {}
    order = list(dict.fromkeys(x[0] for x in T))
    first = {sec: min(x[3] for x in T if x[0] == sec) for sec in order}
    for i, (sec, txt, col, t0, r, big) in enumerate(T):
        # a section's tapes stay until the next section's first tape prints (readable even when the speech is quick)
        nxt = order.index(sec) + 1
        b = first[order[nxt]] - 0.05 if nxt < len(order) else TOTAL
        if sec in ("q", "pan"): b = min(b, E(sec) - 0.02)          # never carried across a cut onto / off a talking head
        k = stack.get(sec, 0); stack[sec] = k + 1
        y = BASE.get(sec, 200) + sum(126 if T[j][5] else 106 for j in range(len(T)) if T[j][0] == sec and j < i)
        plain = html.unescape(txt.split("</span>")[-1]) if "<span" in txt else txt
        nch = max(len(plain), 4)
        style = f"top:{y}px;" + (f" opacity:1; transform: rotate({r}deg);" if t0 < 0.2 else "")
        out.append(f'<div id="tp{i}" class="ov tape {col}{" big" if big else ""}" style="{style}">{txt}</div>')
        pulse = [round(TOTAL - 1.0, 3)] if sec == "end" else []
        data.append({"id": f"tp{i}", "t0": round(t0, 3), "t1": round(b, 3), "r": r, "print": round(min(0.05 * nch, 0.55), 2), "steps": min(nch, 14), "pulse": pulse})
    return "\n      ".join(out), data


def caps():
    out, data = [], []
    for i, (txt, t0, t1, *top) in enumerate(CAP):
        floor = 0.5 + 0.3 * len(txt.split()) + 0.1                    # readable floor, may run past the cut, never into the next line
        nxt = CAP[i + 1][1] - 0.05 if i + 1 < len(CAP) else TOTAL
        t1 = max(t1, min(t0 + floor, nxt))
        st = f' style="top:{top[0] if top else 640}px"'
        out.append(f'<div id="cap{i}" class="ov cap"{st}>{html.escape(txt)}</div>')
        data.append({"id": f"cap{i}", "t0": round(t0, 3), "t1": round(t1, 3)})
    return "\n      ".join(out), data


SFX = {"2568.mp3": (0.00, 0.12), "2364.mp3": (0.01, 0.14), "1489.mp3": (0.71, 0.90)}


def cues(td):
    c = [(0.04, "2568.mp3", 0.3, "frame-0 tapes")]
    for t, (sec, txt, col, *_rest) in zip(td, T):
        if t["t0"] < 0.2: continue
        f, v = ("2364.mp3", 0.4) if col == "r" else ("2568.mp3", 0.28)
        c.append((t["t0"] + 0.02, f, v, f"tape prints: {html.unescape(txt.split('</span>')[0])[:28]}"))
    c.append((IMP["slow"] - 0.05, "1489.mp3", 0.3, "slow-mo replay (air whoosh under the real strike)"))
    return c


def audio_tags(td):
    L = [f'      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>']
    busy = {}
    for i, (beat, f, vol, note) in enumerate(sorted(cues(td))):
        peak, length = SFX[f]; st = max(0.0, beat - peak); length = min(length, TOTAL - st)
        trk = next(k for k in range(12, 80) if busy.get(k, -1) <= st); busy[trk] = st + length
        L.append(f'      <audio data-hf-id="hf-s{i:02d}" id="sfx-{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{st:.3f}" data-duration="{length:.2f}" '
                 f'data-track-index="{trk}" data-volume="{vol}" data-audio-group="sfx"></audio> <!-- {note} -->')
    return "\n".join(L)


def main():
    th, td = tapes(); ch, cd = caps()
    consts = {"TAPES": td, "CAP": cd, "FLASH": [IMP["fail"], IMP["hit"], IMP["slow"]], "TOTAL": TOTAL}
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{TAPES}}", th).replace("{{CAPS}}", ch).replace("{{AUDIO}}", audio_tags(td))
              .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written, total", TOTAL)
    for t, x in zip(td, T): print(f"  {t['t0']:6.2f}-{t['t1']:6.2f} {x[1][:40]}")


if __name__ == "__main__":
    main()
