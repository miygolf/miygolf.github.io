#!/usr/bin/env python3
"""Writes index.html for a Coach Farhan tip in the "Posture Chart" look (same as projects/early-extension, owner: "buat style sama"):
A-roll, chart rows, spoken captions, a few SFX. Rows/captions come from content.py (source times, mapped onto the film through
edit/timeline.json). Final = real sound + SFX, no music. Run from the project folder: python3 tools/build_index.py
"""
import json, os, html, importlib.util

PROJ = os.getcwd()
spec = importlib.util.spec_from_file_location("content", os.path.join(PROJ, "content.py")); C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
TL = json.load(open(os.path.join(PROJ, "edit", "timeline.json")))
TOTAL = TL["total"]
SEGS = [s for s in TL["segs"] if s.get("kind") != "freeze"]


def F(t, clip=None):
    """source time (in `clip`, default C.SRC) -> film time (a time inside a removed pause maps to the next kept frame)"""
    if t == "end": return TOTAL
    clip = clip or C.SRC
    segs = [s for s in SEGS if s.get("src", C.SRC) == clip]
    for s in segs:
        if s["a"] - 1e-3 <= t <= s["b"] + 1e-3: return round(s["start"] + t - s["a"], 3)
        if t < s["a"]: return s["start"]
    return TOTAL


def rows():
    out, data = [], []
    for i, r in enumerate(C.ROWS):
        t0, t1 = F(r["t"], r.get("src")), F(r["until"], r.get("usrc", r.get("src")))
        kk = f"<span class='k'>{r['tag']}</span>" if r.get("tag") else ""
        vis = " opacity:1;" if t0 < 0.2 else ""
        out.append(f'<div id="r{i}" class="ov row {r.get("st", "")}" style="left:{r.get("x", 60)}px; top:{r["y"]}px;{vis}"><div class="tab"></div><div class="tx">{kk}{r["text"]}</div></div>')
        data.append({"id": f"r{i}", "t0": round(t0, 3), "t1": round(t1, 3)})
    return "\n      ".join(out), data


def caps():
    out, data = [], []
    def cs(c): return c[3] if len(c) > 3 and isinstance(c[3], str) else None
    for i, cap in enumerate(C.CAPS):
        txt, a, b = cap[:3]; top = [x for x in cap[3:] if isinstance(x, int)]
        t0, t1 = F(a, cs(cap)), F(b, cs(cap))
        floor = 0.5 + 0.3 * len(txt.split()) + 0.1
        nxt = F(C.CAPS[i + 1][1], cs(C.CAPS[i + 1])) - 0.05 if i + 1 < len(C.CAPS) else TOTAL
        t1 = max(t1, min(t0 + floor, nxt))
        st = f' style="top:{top[0]}px"' if top else ""
        out.append(f'<div id="cap{i}" class="ov cap"{st}>{html.escape(txt)}</div>')
        data.append({"id": f"cap{i}", "t0": round(t0, 3), "t1": round(t1, 3)})
    return "\n      ".join(out), data


SFX = {"2568.mp3": (0.00, 0.12), "2364.mp3": (0.01, 0.14), "1489.mp3": (0.71, 0.90)}


def audio_tags(rd):
    c = [(0.04, "2568.mp3", 0.3, "frame-0 rows")]
    for r, x in zip(rd, C.ROWS):
        if r["t0"] < 0.2: continue
        bad = "bad" in x.get("st", "")
        c.append((r["t0"] + 0.03, "2364.mp3" if bad else "2568.mp3", 0.38 if bad else 0.26, f"row: {html.unescape(x['text'].split('<')[0])[:30]}"))
    L = [f'      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>']
    busy, seen, k = {}, set(), 0
    for beat, f, vol, note in sorted(c):
        if (round(beat, 2), f) in seen: continue
        seen.add((round(beat, 2), f))
        peak, length = SFX[f]; st = max(0.0, beat - peak); length = min(length, TOTAL - st)
        trk = next(t for t in range(12, 80) if busy.get(t, -1) <= st); busy[trk] = st + length
        L.append(f'      <audio data-hf-id="hf-s{k:02d}" id="sfx-{k:02d}" class="clip" src="assets/sfx/{f}" data-start="{st:.3f}" data-duration="{length:.2f}" '
                 f'data-track-index="{trk}" data-volume="{vol}" data-audio-group="sfx"></audio> <!-- {note} -->'); k += 1
    return "\n".join(L)


def main():
    rh, rd = rows(); ch, cd = caps()
    consts = {"ROWS": rd, "CAP": cd, "MEAS": [], "FLASH": [], "TOTAL": TOTAL}
    tpl = open(os.path.join(PROJ, "tools", "index.template.html")).read()
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{MEAS}}", "").replace("{{ROWS}}", rh).replace("{{CAPS}}", ch)
              .replace("{{AUDIO}}", audio_tags(rd)).replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(PROJ, "index.html"), "w").write(out)
    print("index.html written, total", TOTAL)


if __name__ == "__main__":
    main()
