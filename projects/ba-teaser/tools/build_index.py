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
    best = min((x for x in VOICE if x[0] == clip), key=lambda x: min(abs(t - x[1]), abs(t - x[2])))   # word in a cut gap: snap to the nearest piece edge
    return round(best[3] + (min(max(t, best[1]), best[2]) - best[1]), 3)


# cards: id, segment, kind (cause = top panel / before, fix = bottom panel / after, note), number, headline, words [(w, t)] (* = key word)
CARDS = [
    ("k1", "m_c1", "cause", "✗", "Before", [("tangan", 33.58), ("tu", 33.62), ("di", 33.70), ("*atas", 34.34), ("*swing", 34.98), ("*plane.", 35.52)]),
    ("k3", "m_f1a", "fix", "✓", "After", [("dalam", 55.16), ("*plane,", 55.56), ("so", 55.70), ("kita", 57.32), ("jadi", 57.58), ("*shallow", 57.86), ("lah.", 58.20)]),
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
        t1 = E("m_f1b") - 0.06 if seg == "m_f1a" else E(seg) - 0.06
        data.append({"id": cid, "t0": round(S(seg) + 0.05, 3), "t1": round(t1, 3)})
    return "\n      ".join(out), data


SFX = {"2167.mp3": (0.11, 0.30), "1120.mp3": (0.10, 0.14), "2364.mp3": (0.01, 0.14), "2121.mp3": (0.14, 0.40), "175.mp3": (0.49, 0.40)}
CUES = [
    (0.02, "2167.mp3", 0.45, "slate clap: title, frame 0"),
    (B["hook_impact"], "2121.mp3", 0.25, "strike layer under the real one (0.5x)"),
    (S("b_swing") + 0.02, "2167.mp3", 0.4, "clap: BEFORE"),
    (S("a_swing") + 0.02, "2167.mp3", 0.4, "clap: AFTER"),
    (S("m_c1") + 0.02, "175.mp3", 0.3, "sweep into the analysis"),
    (S("m_c1") + 0.08, "1120.mp3", 0.4, "card 1"),
    (S("m_f1a") + 0.08, "1120.mp3", 0.4, "card 2"),
    (S("testi") + 0.05, "175.mp3", 0.3, "phone"),
    (S("end_freeze") + 0.1, "2167.mp3", 0.4, "end slate clap"),
]


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
