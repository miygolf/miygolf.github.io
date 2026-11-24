#!/usr/bin/env python3
"""Writes index.html for the Bunker Shot script video ("Label Maker" look): A-roll, embossed tapes, spoken captions, a few SFX.
Film times: edit/timeline.json (tools/build_aroll.py). Word anchors: edit/film_words.json (tools/film_words.py, crops on the film's own audio).
Final = real sound + SFX, no music (house rule). Run from the project folder:  python3 tools/build_index.py
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
FW = json.load(open(os.path.join(ROOT, "edit", "film_words.json")))
TOTAL = TL["_total"]; IMP = TL["_impacts"]
S = lambda n: TL[n]["start"]; E = lambda n: TL[n]["end"]
QPLUG = 17.12 - 13.58                               # IMG_0418: "Macam mana nak pukul bola plug?" starts 3.54 s into the CTA
LAND = round(S("slow2") + (6.0 - 3.55), 3)        # IMG_0413 6.0: the phone has settled on the green -> punch in on the landed ball
# owner v5 "zoom in dekat bola land tu": 3x punch-in that follows the two balls (edit/ball_track.json, tools/track_balls.py) and keeps them
# at C on screen while the handheld phone drifts. Element transform: p' = O + T + s(p - O), O = CSS transform-origin.
O, C, ZMAX = (700.0, 978.0), (620.0, 1000.0), 3.0      # owner v6: the ball right of the middle pin; both pins stay in frame
def zoom_keys():
    tr = json.load(open(os.path.join(ROOT, "edit", "ball_track.json")))
    keys = []
    for src_t, bx, by, _n in tr:
        t = S("slow2") + (src_t - 3.55)
        if t < LAND or t > E("slow2"): continue
        u = min(1.0, (t - LAND) / 0.9); e = u * u * (3 - 2 * u)              # smoothstep ramp over 0.9 s
        sc = 1 + (ZMAX - 1) * e
        tx = (C[0] - O[0] - sc * (bx - O[0])) * e; ty = (C[1] - O[1] - sc * (by - O[1])) * e
        keys.append([round(t, 3), round(sc, 3), round(tx, 1), round(ty, 1)])
    return keys


def W(seg, word, nth=0, default=None):
    """film time of the nth word in a segment that contains `word` (crop transcript), else default"""
    hits = [a for a, b, w in FW.get(seg, []) if word.lower() in w.lower()]
    return hits[nth] if len(hits) > nth else (default if default is not None else S(seg))


# sections: tapes stack inside a section and peel off when it ends
SEC = {"hook": (0.0, E("skull")), "rahsia": (S("rahsia"), E("rahsia")), "face": (S("face"), E("face")), "stance": (S("stance"), E("stance")),
       "weight": (S("weight"), E("weight")), "line": (S("line"), E("line")), "nobola": (S("nobola"), E("nobola")),
       "contoh": (S("contoh"), E("contoh")), "letak": (S("letak"), E("letakshot")), "shot": (S("shot"), E("shot")),
       "slow": (S("slow"), E("slow2")), "penalty": (S("penalty"), E("penalty")), "cta": (S("cta"), TOTAL)}
BASE = {"rahsia": 860, "shot": 1010, "slow": 1010, "land": 420, "penalty": 230, "cta": 230}   # rahsia: below the close face; IMG_0418 talking head sits LOW (face y 900-1330): tapes + captions go above it
# (section, text, colour k/y/r/w, film time, tilt deg, big?) — wording from the owner's script, numbers = the set-up steps
T = [
    ("hook", "Bola tak keluar", "k", 0.0, -2.0, True), ("hook", "bunker?", "y", 0.0, 1.5, True),
    ("hook", "Top · skull ✗", "r", W("skull", "top"), -1.5, False),
    ("rahsia", "Rahsia dia:", "k", S("rahsia") + 0.08, -1.5, False),
    ("rahsia", "Jangan pukul bola ✗", "r", W("rahsia", "jangan"), 1.0, False),
    ("rahsia", "Pukul pasir ✓", "y", W("rahsia", "bola", 0, S("rahsia") + 2.2) + 0.1, -1.0, True),
    ("face", "<span class='n'>01</span>Buka face, baru grip", "k", S("face") + 0.08, -1.2, False),
    ("face", "Face open ✓", "y", E("face") - 1.3, 1.2, False),
    ("stance", "<span class='n'>02</span>Kaki lebar", "k", S("stance") + 0.05, -1.0, False),
    ("stance", "Benam dalam pasir", "w", S("stance") + 0.6, 1.0, False),
    ("weight", "<span class='n'>03</span>Bola depan · berat kiri", "k", S("weight") + 0.05, -1.2, False),
    ("weight", "Blast!", "y", E("weight") - 1.0, 2.0, True),
    ("line", "Drill: lukis 1 line", "k", S("line") + 0.05, -1.2, False),
    ("nobola", "Tanpa bola dulu", "w", S("nobola") + 0.05, 1.0, False),
    ("contoh", "Target = line", "y", IMP["contoh"] - 0.05, -1.2, True),
    ("contoh", "Bukan bola ✗", "r", IMP["contoh"] + 0.55, 1.2, False),
    ("letak", "Bola depan line sikit", "k", S("letak") + 0.05, -1.0, False),
    ("letak", "Pukul line ✓", "y", IMP["letakshot"] - 0.05, 1.5, True),
    ("shot", "Swing penuh", "k", S("shot") + 0.55, -1.2, False),
    ("shot", "Jangan slow down", "r", IMP["shot"] - 0.45, 1.2, False),
    ("slow", "Pasir yang bawa", "y", IMP["slow"], -1.5, True), ("slow", "bola keluar", "k", IMP["slow"] + 0.35, 1.2, True),
    ("land", "Mendarat atas green ✓", "y", LAND + 0.6, -1.5, False),
    ("penalty", "One more thing", "k", S("penalty") + 0.65, -1.2, False),   # IMG_0418 1.55-2.2: he walks back from the phone, face high -> wait
    ("penalty", "Club jangan sentuh pasir", "r", W("penalty", "club"), 1.0, False),
    ("penalty", "Penalty 2 pukulan", "w", W("penalty", "club") + 0.9, -1.5, True),
    ("cta", "Komen \"bunker\" <span class='emo' style='font-size:50px'>👇</span>", "y", W("cta", "bang", 0, S("cta") + 0.8), -1.5, True),
    ("cta", "Macam mana nak pukul", "k", S("cta") + QPLUG, 1.2, False),            # owner v7: highlight the plug question
    ("cta", "bola plug? <span class='emo' style='font-size:66px'>🍳</span>", "r", S("cta") + QPLUG + 0.55, -2.0, True),
]
# spoken captions (cleaned), (text, t0, t1)
CAP = [
    ("Alamak.", S("hook") + 2.17, E("hook")),
    ("Ataupun… top, skull.", W("skull", "ataupun"), E("skull") - 0.05),
    ("Rahsia dia, korang jangan pukul bola. Korang pukul pasir.", S("rahsia") + 0.05, E("rahsia") - 0.05),
    ("Cut sikit, so bagi dia open.", S("face") + 0.08, E("face") - 0.05),
    ("Korang kangkang besar-besar.", S("stance") + 0.05, E("stance") - 0.05),
    ("Weight belah kiri, and then blast.", S("weight") + 0.05, E("weight") - 0.05),
    ("Korang buat satu line. Tak payah pukul bola dulu.", S("line") + 0.05, E("nobola") - 0.05),
    ("Contoh macam ni…", S("contoh") + 0.4, IMP["contoh"] - 0.3),
    ("Pukul line tu. Letak depan line.", E("contoh") - 0.75, E("letak") - 0.05),
    ("One more thing: dalam pasir, club tu jangan sentuh pasir.", S("penalty") + 0.65, E("penalty") - 0.05, 586),
    ("Komen \"bunker\" kalau korang nak bola plug.", S("cta") + 0.05, S("cta") + QPLUG - 0.05, 640),
    ("Macam mana nak pukul bola plug?", S("cta") + QPLUG, TOTAL, 640),
]


def tapes():
    out, data, stack = [], [], {}
    order = list(dict.fromkeys(x[0] for x in T))
    first = {sec: min(x[3] for x in T if x[0] == sec) for sec in order}
    for i, (sec, txt, col, t0, r, big) in enumerate(T):
        # a section's tapes stay until the next section's first tape prints (readable even when the speech is quick)
        nxt = order.index(sec) + 1
        b = first[order[nxt]] - 0.05 if nxt < len(order) else TOTAL
        if sec == "land": b = E("slow2") - 0.02          # never carried onto the talking head (his face is high there)
        k = stack.get(sec, 0); stack[sec] = k + 1
        y = BASE.get(sec, 780) + sum(126 if T[j][5] else 106 for j in range(len(T)) if T[j][0] == sec and j < i)
        plain = html.unescape(txt.split("</span>")[-1]) if "<span" in txt else txt
        nch = max(len(plain), 4)
        style = f"top:{y}px;" + (f" opacity:1; transform: rotate({r}deg);" if t0 < 0.2 else "")
        out.append(f'<div id="tp{i}" class="ov tape {col}{" big" if big else ""}" style="{style}">{txt}</div>')
        pulse = []
        if sec == "cta":                                     # owner v7: highlight the ending - the CTA tapes pulse on the plug question and at the end
            pulse = [round(S("cta") + QPLUG + 1.2, 3), round(TOTAL - 1.0, 3)] if "Komen" in txt or "plug" in txt else [round(TOTAL - 1.0, 3)]
        data.append({"id": f"tp{i}", "t0": round(t0, 3), "t1": round(b, 3), "r": r, "print": round(min(0.05 * nch, 0.55), 2), "steps": min(nch, 14), "pulse": pulse})
    return "\n      ".join(out), data


def caps():
    out, data = [], []
    for i, (txt, t0, t1, *top) in enumerate(CAP):
        floor = 0.5 + 0.3 * len(txt.split()) + 0.1                    # readable floor, may run past the cut, never into the next line
        nxt = CAP[i + 1][1] - 0.05 if i + 1 < len(CAP) else TOTAL
        t1 = max(t1, min(t0 + floor, nxt))
        st = f' style="top:{top[0]}px"' if top else ""
        out.append(f'<div id="cap{i}" class="ov cap"{st}>{html.escape(txt)}</div>')
        data.append({"id": f"cap{i}", "t0": round(t0, 3), "t1": round(t1, 3)})
    return "\n      ".join(out), data


SFX = {"2568.mp3": (0.00, 0.12), "2364.mp3": (0.01, 0.14), "1489.mp3": (0.71, 0.90)}


def cues(td):
    c = [(0.04, "2568.mp3", 0.3, "frame-0 tapes")]
    for t, (sec, txt, col, *_rest) in zip(td, T):
        if t["t0"] < 0.2: continue
        f, v = ("2364.mp3", 0.4) if col == "r" and "Penalty" not in txt else ("2568.mp3", 0.28)
        if "Penalty" in txt: f, v = "2364.mp3", 0.5
        c.append((t["t0"] + 0.02, f, v, f"tape prints: {html.unescape(txt.split('</span>')[-1])[:28]}"))
    c.append((IMP["slow"] - 0.05, "1489.mp3", 0.3, "slow-mo blast (air whoosh under the real strike)"))
    c.append((LAND + 0.75, "2364.mp3", 0.35, "ring drawn round the landed ball"))
    c.append((S("cta") + QPLUG + 1.2, "2364.mp3", 0.4, "plug question tapes pulse"))
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
    consts = {"LAND": LAND, "LAND_END": E("slow2"), "ZOOM": zoom_keys(), "TAPES": td, "CAP": cd, "FLASH": [IMP["contoh"], IMP["letakshot"], IMP["slow"]], "TOTAL": TOTAL}
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{TAPES}}", th).replace("{{CAPS}}", ch).replace("{{AUDIO}}", audio_tags(td))
              .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written, total", TOTAL)
    for t, x in zip(td, T): print(f"  {t['t0']:6.2f}-{t['t1']:6.2f} {x[1][:40]}")


if __name__ == "__main__":
    main()
