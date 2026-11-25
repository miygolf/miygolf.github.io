#!/usr/bin/env python3
"""Writes index.html for Early Extension ("Posture Chart" look): A-roll, measured hip lines, chart rows, spoken captions, a few SFX.
Film times: edit/timeline.json (tools/build_aroll.py). Word anchors: edit/film_words.json (tools/film_words.py).
Final = real sound + SFX, no music. Run from the project folder:  python3 tools/build_index.py
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
FW = json.load(open(os.path.join(ROOT, "edit", "film_words.json")))
TOTAL = TL["_total"]; IMP = TL["_impacts"]
S = lambda n: TL[n]["start"]; E = lambda n: TL[n]["end"]


def W(seg, word, nth=0, default=None):
    hits = [a for a, b, w in FW.get(seg, []) if word.lower() in w.lower()]
    return hits[nth] if len(hits) > nth else (default if default is not None else S(seg))


# ---- measured hip lines (build_aroll.py docstring): upright source px, rows 820-1120 ----
B_ADDR, B_IMP, A_ADDR, A_IMP = 24, 110, 40, 65
SP = dict(s=0.628, cx=0, cy=380, y=330)                       # split panel transform
def sp(x, y, right=False):
    return (round((540 if right else 0) + SP["s"] * (x - SP["cx"]), 1), round(SP["y"] + SP["s"] * (y - SP["cy"]), 1))


def meas_svg(mid, x0, x1, ya, yb, yarr, tags):
    """plumb line at x0 (address), red marker at x1 (impact), arrow x0->x1 at yarr, tags [(x, y, text, colour)]"""
    head = f'<path class="head" d="M {x1 - 14} {yarr - 10} L {x1} {yarr} L {x1 - 14} {yarr + 10}" fill="none" stroke="#e2483d" stroke-width="6" stroke-linecap="round"/>' if x1 - x0 > 18 else ""
    t = "".join(f'<g class="mtag"><rect x="{x}" y="{y}" rx="4" width="{len(s) * 19 + 26}" height="46" fill="{c}"/><text x="{x + 13}" y="{y + 33}" '
                f'font-family="RMono" font-weight="600" font-size="30" fill="#fff" letter-spacing="2">{html.escape(s)}</text></g>' for x, y, s, c in tags)
    return (f'<svg class="meas" id="{mid}" viewBox="0 0 1080 1920">'
            f'<line class="plumb" x1="{x0}" y1="{ya}" x2="{x0}" y2="{yb}" stroke="#0e8c8f" stroke-width="7" stroke-linecap="round"/>'
            f'<path class="bob" d="M {x0} {yb} l -13 -22 l 26 0 z" fill="#0e8c8f"/>'
            f'<line class="imp" x1="{x1}" y1="{ya + 40}" x2="{x1}" y2="{yb - 30}" stroke="#e2483d" stroke-width="7" stroke-dasharray="12 9" stroke-linecap="round"/>'
            f'<path class="arrow" d="M {x0} {yarr} L {x1} {yarr}" fill="none" stroke="#e2483d" stroke-width="6" stroke-linecap="round"/>{head}{t}</svg>')


MEAS = [
    dict(id="m_hook", t0=S("hookfreeze") + 0.05, t1=E("hookfreeze"),
         svg=lambda i: meas_svg(i, B_ADDR, B_IMP, 780, 1150, 985, [(140, 1060, "PUNGGUNG KE DEPAN", "#e2483d")])),
    dict(id="m_before", t0=S("splitfreeze") + 0.05, t1=E("splitfreeze"),
         svg=lambda i: meas_svg(i, *[sp(B_ADDR, 0)[0], sp(B_IMP, 0)[0]], sp(0, 820)[1], sp(0, 1120)[1], sp(0, 985)[1], [(60, 1112, "LARI KE DEPAN", "#e2483d")])),
    dict(id="m_after", t0=S("splitfreeze") + 0.25, t1=E("splitfreeze"),
         svg=lambda i: meas_svg(i, *[sp(A_ADDR, 0, True)[0], sp(A_IMP, 0, True)[0]], sp(0, 820)[1], sp(0, 1120)[1], sp(0, 985)[1], [(600, 1112, "STAY", "#0e8c8f")])),
]

# ---- chart rows: (section-end, text, style, t0, x, y, tag) ----
H1, H2 = 190, 290          # top rows (range shots: head starts ~y 320 at x 420+, keep these short)
L1, L2, L3 = 930, 1030, 1130
R = [
    (E("hookpost"), "Punggung lari", "ink big", 0.0, 60, H1, ""),
    (E("hookpost"), "masa downswing?", "badfill big", 0.0, 60, H1 + 104, ""),
    (E("hookpost"), "= Early extension", "bad", S("hookfreeze") + 1.25, 60, 1120, ""),
    (E("demoC"), "Space tangan hilang", "bad", W("demoB", "naik", 0, S("demoB") + 1.4), 60, L1, "01"),
    (E("demoC"), "Shank · block kanan · thin", "bad", S("demoC") + 0.6, 60, L2, "02"),
    (E("kerusi0"), "Drill dia simple je", "ink big", S("kerusi0") + 0.05, 60, H1, ""),
    (E("kerusi0"), "Kerusi / golf bag / dinding", "", S("kerusi0") + 0.7, 60, H1 + 112, ""),
    (E("kerusi"), "Setup: punggung touch kerusi", "", S("kerusi") + 0.3, 60, L1, "01"),
    (E("kerusi"), "Backswing: punggung kanan stay", "", W("kerusi", "angkat", 0, S("kerusi") + 3.8), 60, L2, "02"),
    (E("kerusi"), "Downswing: punggung kiri tolak kerusi", "good", W("kerusi", "down", 0, S("kerusi") + 5.9), 60, L3 - 10, "03"),
    (E("slow"), "Slow dulu · 10 kali", "good big", S("slow") + 0.1, 60, L1 - 10, ""),
    (E("slow"), "Rasa punggung stay kat belakang", "", S("slow") + 1.2, 60, L2 + 20, ""),
    (E("chairhit"), "That's it ✓", "good big", IMP["chair"] + 0.15, 60, L1, ""),
    (E("splitpost"), "Before", "ink", S("splitpre") + 0.05, 60, 350, ""),
    (E("splitpost"), "After", "good", S("splitpre") + 0.05, 600, 350, ""),
    (E("splitpost"), "Nampak beza dia?", "ink big", S("splitfreeze") + 1.3, 60, 1196, ""),
    (TOTAL, "Try dulu sebelum warm-up", "ink", S("end") + 0.2, 60, 840, ""),     # the end: his face fills the top half -> rows low
    (TOTAL, "Komen \"DRILL\" <span class='emo' style='font-size:52px'>👇</span>", "good big", S("end") + 0.9, 60, 936, ""),
    (TOTAL, "Part 2: rotation", "", S("end") + 1.5, 60, 1062, ""),
]
CAP = [
    ("Apa itu early extension?", W("hookfreeze", "apa"), E("hookfreeze") - 0.05),
    ("First of all, dia angkat backswing, dia naik badan.", S("demoA") + 0.05, E("demoB") - 0.05),
    ("Lepas tu bila dia turun, dia turun je macam tu.", S("demoC") + 0.05, E("demoC") - 0.05),
    ("Ambil golf bag ataupun kerusi.", S("kerusi0") + 0.05, E("kerusi0") - 0.05),
    ("Kerusi ni sebagai kita nak dapatkan rasa je.", S("kerusi") + 0.05, W("kerusi", "angkat", 0, S("kerusi") + 3.8) - 0.05),
    ("Angkat backswing.", W("kerusi", "angkat", 0, S("kerusi") + 3.8), W("kerusi", "down", 0, S("kerusi") + 5.9) - 0.1),
    ("Downswing tu bagi rasa, tolak je kerusi tu.", W("kerusi", "down", 0, S("kerusi") + 5.9), W("kerusi", "then", 0, S("kerusi") + 9.7) - 0.05),
    ("Then follow through.", W("kerusi", "then", 0, S("kerusi") + 9.7), E("kerusi") - 0.03),
    ("Buat slow-slow, backswing slow je.", S("slow") + 0.05, E("slow") - 0.05),
    ("Okey, itu dia.", W("end", "okey", 0, S("end") + 0.7), TOTAL),
]
CAPTOP = {}


def rows():
    out, data = [], []
    for i, (t1, txt, st, t0, x, y, k) in enumerate(R):
        kk = f"<span class='k'>{k}</span>" if k else ""
        vis = " opacity:1;" if t0 < 0.2 else ""
        out.append(f'<div id="r{i}" class="ov row {st}" style="left:{x}px; top:{y}px;{vis}"><div class="tab"></div><div class="tx">{kk}{txt}</div></div>')
        data.append({"id": f"r{i}", "t0": round(t0, 3), "t1": round(t1, 3)})
    return "\n      ".join(out), data


def caps():
    out, data = [], []
    for i, (txt, t0, t1) in enumerate(CAP):
        floor = 0.5 + 0.3 * len(txt.split()) + 0.1
        nxt = CAP[i + 1][1] - 0.05 if i + 1 < len(CAP) else TOTAL
        t1 = max(t1, min(t0 + floor, nxt))
        st = f' style="top:{CAPTOP[txt]}px"' if txt in CAPTOP else ""
        out.append(f'<div id="cap{i}" class="ov cap"{st}>{html.escape(txt)}</div>')
        data.append({"id": f"cap{i}", "t0": round(t0, 3), "t1": round(t1, 3)})
    return "\n      ".join(out), data


SFX = {"2568.mp3": (0.00, 0.12), "2364.mp3": (0.01, 0.14), "1489.mp3": (0.71, 0.90)}


def cues(rd):
    c = [(0.04, "2568.mp3", 0.3, "frame-0 rows")]
    for r, x in zip(rd, R):
        if r["t0"] < 0.2: continue
        bad = "bad" in x[2]
        c.append((r["t0"] + 0.03, "2364.mp3" if bad else "2568.mp3", 0.38 if bad else 0.26, f"row: {html.unescape(x[1].split('<')[0])[:30]}"))
    for m in MEAS:
        c.append((m["t0"] + 0.55, "2364.mp3", 0.32, f"impact marker ({m['id']})"))
    c.append((S("hookslow") + 0.05, "1489.mp3", 0.25, "into slow motion"))
    c.append((S("splitpre") + 0.05, "1489.mp3", 0.25, "into the split slow motion"))
    return c


def audio_tags(rd):
    L = [f'      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>']
    busy = {}
    seen = set(); cl = []
    for cue in sorted(cues(rd)):
        key = (round(cue[0], 2), cue[1])
        if key not in seen: seen.add(key); cl.append(cue)
    for i, (beat, f, vol, note) in enumerate(cl):
        peak, length = SFX[f]; st = max(0.0, beat - peak); length = min(length, TOTAL - st)
        trk = next(k for k in range(12, 80) if busy.get(k, -1) <= st); busy[trk] = st + length
        L.append(f'      <audio data-hf-id="hf-s{i:02d}" id="sfx-{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{st:.3f}" data-duration="{length:.2f}" '
                 f'data-track-index="{trk}" data-volume="{vol}" data-audio-group="sfx"></audio> <!-- {note} -->')
    return "\n".join(L)


def main():
    rh, rd = rows(); ch, cd = caps()
    mh = "\n      ".join(m["svg"](m["id"]) for m in MEAS)
    consts = {"ROWS": rd, "CAP": cd, "MEAS": [{"id": m["id"], "t0": round(m["t0"], 3), "t1": round(m["t1"], 3)} for m in MEAS],
              "FLASH": [IMP["hook"], IMP["chair"], IMP["split"]], "TOTAL": TOTAL}
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{MEAS}}", mh).replace("{{ROWS}}", rh).replace("{{CAPS}}", ch)
              .replace("{{AUDIO}}", audio_tags(rd)).replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written, total", TOTAL)


if __name__ == "__main__":
    main()
