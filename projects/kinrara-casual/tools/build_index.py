#!/usr/bin/env python3
"""Casual version of the Kinrara recap: small lowercase phone-style text, hard cuts, real sound, one SFX (the ball dropping). No music.
Run from the project folder:  python3 tools/build_index.py
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
TOTAL = TL["_total"]; B = TL["_beats"]; S = lambda n: TL[n]["start"]; E = lambda n: TL[n]["end"]
NAME = {"reza": "coach reza", "me": "saya", "kimi": "kimi", "taza": "taza"}
NOTE = {"appr": "hole 18 · approach", "putt": "hole 18 · putt"}
SIDE = {"appr": "R"}
LABELS = [(seg, NAME[who], NOTE.get(seg, "tee shot")) for seg, who in TL["_who"]]
CUES = [(B["hook_drop"], 0.5), (B["putt_drop"], 0.45)]


def main():
    tags = []
    data = []
    for i, (seg, nm, note) in enumerate(LABELS):
        side = SIDE.get(seg, "L"); pos = "left:70px;" if side == "L" else "right:150px; text-align:right;"
        tags.append(f'<div id="lb{i}" class="ov lab" style="{pos}"><div class="nm">{nm}</div><div class="nt">{note}</div></div>')
        data.append({"id": f"lb{i}", "t0": round(S(seg) + 0.1, 3), "t1": round(E(seg) - 0.12, 3)})
    au = [f'      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>']
    for i, (t, v) in enumerate(CUES):
        au.append(f'      <audio data-hf-id="hf-s{i}" id="sfx-{i}" class="clip" src="assets/sfx/2073.mp3" data-start="{max(0, t - 0.01):.3f}" data-duration="0.20" data-track-index="{12 + i}" data-volume="{v}" data-audio-group="sfx"></audio> <!-- ball drops -->')
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": B, "LAB": data}
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", "\n".join(au)).replace("{{LABELS}}", "\n      ".join(tags))
              .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written, total", TOTAL)


if __name__ == "__main__":
    main()
