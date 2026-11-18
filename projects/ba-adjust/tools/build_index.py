#!/usr/bin/env python3
"""Writes index.html for the before/after adjustment edit: film-slate takes, numbered cause / fix cards carrying the coach's own words
(lit word by word as he says them), slate-clap section changes, CTA. Film times from edit/timeline.json. No music.
Run from the project folder:  python3 tools/build_index.py
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
VOICE = TL["_voice"]; TOTAL = TL["_total"]; B = TL["_beats"]
S = lambda n: TL[n]["start"]; E = lambda n: TL[n]["end"]
M = "clip_m4v.m4v"


def film(t, clip=M):
    for c, a, b, ft in VOICE:
        if c == clip and a - 1e-3 <= t <= b + 1e-3:
            return round(ft + (t - a), 3)
    raise ValueError(f"{clip} {t}")


# cards: id, segment, kind (cause = top panel / before, fix = bottom panel / after, note), number, headline, words [(w, t)] (* = key word)
CARDS = [
    ("k0", "m_bs", "note", "✓", "Backswing sama", [("Backswing", 7.48), ("angkat", 7.90), ("*cantik", 8.12), ("je,", 8.64), ("on", 8.76), ("*plane.", 9.62)]),
    ("k1", "m_c1", "cause", "1", "Tangan atas plane", [("Bila", 31.44), ("down", 31.68), ("swing", 31.90), ("tu,", 32.12), ("tangan", 32.40), ("tu", 33.58),
                                                     ("di", 33.70), ("*atas", 34.34), ("*swing", 34.98), ("*plane.", 35.52)]),
    ("k2", "m_c2", "cause", "2", "Badan terangkat", [("Tengok,", 80.30), ("*terangkat", 81.02), ("badan-badan.", 81.72), ("Sebab", 84.12), ("*bodi", 84.70), ("*tak", 85.06), ("*clear.", 85.16)]),
    ("k3", "m_f1", "fix", "1", "Turun dalam plane", [("Dia", 53.38), ("turun,", 54.18), ("dia", 54.70), ("*dalam", 55.16), ("*plane,", 55.56), ("so", 55.88), ("kita", 57.32), ("jadi", 57.58), ("*shallow", 57.86), ("lah.", 58.20)]),
    ("k4", "m_f2a", "fix", "2", "Lutut masuk", [("Lepas", 62.58), ("tu", 62.94), ("*lutut", 63.02), ("*masuk.", 63.58)]),
    ("k4b", "m_f2b", "fix", "2", "Tak early extension", [("Kita", 68.40), ("tak", 68.72), ("adalah", 69.08), ("kes", 69.32), ("*early", 70.08), ("*extension", 70.92), ("tu.", 71.24)]),
    ("k5", "m_f3", "fix", "3", "Finish cantik", [("After", 92.40), ("ni", 93.22), ("*finishing", 93.52), ("*cantik", 94.60), ("je.", 95.08)]),
]


def cards_html():
    out, data = [], []
    for cid, seg, kind, num, head, words in CARDS:
        spans = []
        for w, t in words:
            hot = w.startswith("*"); w = w.lstrip("*")
            spans.append(f'<span class="{"w hot" if hot else "w"}" data-t="{film(t):.3f}">{html.escape(w)}</span>')
        out.append(f'<div id="{cid}" class="ov card {kind}"><div class="hd"><span class="no">{num}</span><span class="tt">{html.escape(head)}</span></div>'
                   f'<div class="said">“{" ".join(spans)}”</div><div class="by mono">— coach</div></div>')
        data.append({"id": cid, "t0": round(S(seg) + 0.05, 3), "t1": round(E(seg) - 0.06, 3)})
    return "\n      ".join(out), data


SFX = {"2167.mp3": (0.11, 0.30), "1120.mp3": (0.10, 0.14), "2364.mp3": (0.01, 0.14), "2121.mp3": (0.14, 0.40), "175.mp3": (0.49, 0.40)}
CUES = [
    (0.02, "2167.mp3", 0.45, "slate clap: title, frame 0"),
    (B["hook_impact"], "2121.mp3", 0.25, "strike layer under the real one (0.5x)"),
    (S("b_swing") + 0.02, "2167.mp3", 0.4, "slate clap: TAKE 01 BEFORE"),
    (S("m_bs") + 0.02, "175.mp3", 0.35, "sweep into the coach's analysis"),
    (S("a_swing") + 0.02, "2167.mp3", 0.4, "slate clap: TAKE 02 AFTER"),
    (S("m_f1") + 0.02, "175.mp3", 0.35, "sweep into the analysis (after)"),
    (S("fo_b") + 0.02, "2167.mp3", 0.35, "slate clap: replay"),
    (S("end_freeze") + 0.35, "2364.mp3", 0.35, "CTA"),
] + [(d_t0 + 0.05, "1120.mp3", 0.4, f"card {c[0]}") for c, d_t0 in zip(CARDS, [S(c[1]) for c in CARDS]) if c[0] != "k4b"]


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
    ch, cd = cards_html()
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": B, "TOTAL": TOTAL, "CARDS": cd}
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{CARDS}}", ch)
              .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written, total", TOTAL)
    for d in cd: print("  ", d)


if __name__ == "__main__":
    main()
