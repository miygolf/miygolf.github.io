#!/usr/bin/env python3
"""Writes index.html for the 28.11 lesson recap ("Stamp Card" look): A-roll, the loyalty card with a stamp per swing, replay tags, end CTA.
Film times: edit/timeline.json (tools/build_aroll.py). Final = real sound + SFX, no music. Run from the project folder: python3 tools/build_index.py
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
TOTAL = TL["_total"]; IMP = TL["_impacts"]
S = lambda n: TL[n]["start"]; E = lambda n: TL[n]["end"]
N = 5
STAMPS = [IMP[f"s{i}"] for i in range(1, N + 1)]
ROT = [-8, 6, -4, 9, -6]
TAGS = [{"id": f"tg{i}", "t0": round(S(f"r{i}") + 0.02, 3), "t1": round(E(f"r{i}"), 3)} for i in range(1, N + 1)]
SFX = {"3005.mp3": (0.03, 0.17), "2364.mp3": (0.01, 0.14), "1489.mp3": (0.71, 0.90), "2568.mp3": (0.00, 0.12)}


def audio_tags():
    c = [(0.04, "3005.mp3", 0.3, "card + title on frame 0")]
    for i, t in enumerate(STAMPS): c.append((t + 0.16, "2364.mp3", 0.45, f"stamp {i + 1} lands"))
    for i in range(1, N + 1): c.append((S(f"r{i}") + 0.02, "1489.mp3", 0.18, f"into replay {i}"))
    c.append((S("end") + 0.35, "3005.mp3", 0.3, "end CTA"))
    L = [f'      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>']
    busy = {}
    for k, (beat, f, vol, note) in enumerate(sorted(c)):
        peak, length = SFX[f]; st = max(0.0, beat - peak); length = min(length, TOTAL - st)
        trk = next(t for t in range(12, 80) if busy.get(t, -1) <= st); busy[trk] = st + length
        L.append(f'      <audio data-hf-id="hf-s{k:02d}" id="sfx-{k:02d}" class="clip" src="assets/sfx/{f}" data-start="{st:.3f}" data-duration="{length:.2f}" '
                 f'data-track-index="{trk}" data-volume="{vol}" data-audio-group="sfx"></audio> <!-- {note} -->')
    return "\n".join(L)


def main():
    slots = "".join(f'<div class="slot">{i + 1}<div class="stamp" id="st{i}"><b>{i + 1:02d}</b></div></div>' for i in range(N))
    tags = "\n      ".join(f'<div id="tg{i}" class="ov tag"><span class="r">0.5×</span> replay</div>' for i in range(1, N + 1))
    consts = {"STAMPS": STAMPS, "ROT": ROT, "TAGS": TAGS, "S1": S("s1"), "END": S("end"), "TOTAL": TOTAL}
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{SLOTS}}", slots).replace("{{TAGS}}", tags).replace("{{AUDIO}}", audio_tags())
              .replace("{{CONSTS}}", json.dumps(consts)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written, total", TOTAL)


if __name__ == "__main__":
    main()
