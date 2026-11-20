#!/usr/bin/env python3
"""Writes index.html for the lesson montage: "Polaroid" — each finish freezes into an instant photo with a marker caption, shutter + whirr;
end board of the three prints. No names (owner), no speech, no music. Run from the project folder: python3 tools/build_index.py
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
TOTAL = TL["_total"]; B = TL["_beats"]; S = lambda n: TL[n]["start"]; E = lambda n: TL[n]["end"]
STU = [("01", "19.11 · malam"), ("02", "19.11 · malam"), ("03", "20.11 · pagi")]
SFX = {"1430.mp3": (0.14, 0.40), "1440.mp3": (0.17, 0.62)}
CUES = [(S("hook_freeze"), "1430.mp3", 0.5, "hook freeze shutter")]
for i in range(1, 4):
    CUES += [(S(f"s{i}_fin"), "1430.mp3", 0.55, f"polaroid {i} shutter"), (S(f"s{i}_fin") + 0.25, "1440.mp3", 0.25, f"print {i} out")]
CUES += [(S("end_freeze") + 0.2 + k * 0.22, "1440.mp3", 0.25, f"end print {k}") for k in range(3)]


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
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": B, "STU": STU}
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    out = tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written, total", TOTAL)


if __name__ == "__main__":
    main()
