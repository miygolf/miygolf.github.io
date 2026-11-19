#!/usr/bin/env python3
"""Writes index.html for the Kinrara recap: lanyard player badges ("Flight Pass"), shot chips, end lineup. No speech, no music.
Run from the project folder:  python3 tools/build_index.py
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
TOTAL = TL["_total"]; B = TL["_beats"]; S = lambda n: TL[n]["start"]; E = lambda n: TL[n]["end"]
P = {"reza": ("Coach Reza", "Coach", "#1b1b1b", "#ffc93c"), "me": ("Saya", "Host", "#e2452a", "#ffffff"),
     "kimi": ("Kimi", "Player", "#1f7fd6", "#ffffff"), "taza": ("Taza", "Player", "#e9c27a", "#15171a")}
# badge side per segment (left unless the golfer stands on the left)
SIDE = {"appr": "R"}
WHO = TL["_who"]
SFX = {"2364.mp3": (0.01, 0.14), "1120.mp3": (0.10, 0.14), "175.mp3": (0.49, 0.40), "2121.mp3": (0.14, 0.40), "2073.mp3": (0.01, 0.20), "3005.mp3": (0.03, 0.17)}
CUES = [(0.03, "3005.mp3", 0.4, "title pops, frame 0"), (B["hook_drop"], "2073.mp3", 0.6, "ball drops in the cup (0.5x)"),
        (B["hook_drop"] + 0.08, "2364.mp3", 0.4, "MASUK stamp"), (B["putt_drop"], "2073.mp3", 0.5, "drop (1x)"),
        (B["putt_drop"] + 0.1, "2364.mp3", 0.35, "MASUK chip"), (S("tee1") if "tee1" in TL else 0, "175.mp3", 0.0, "")]
CUES = [c for c in CUES if c[2] > 0]
for seg, who in WHO:
    CUES.append((S(seg) + 0.12, "1120.mp3", 0.4, f"badge {who}"))
CUES.append((S("end_freeze") + 0.1, "175.mp3", 0.3, "lineup"))
for i in range(4): CUES.append((S("end_freeze") + 0.35 + i * 0.15, "1120.mp3", 0.35, f"lineup badge {i}"))


def audio_tags():
    L = [f'      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>']
    busy = {}
    for i, (beat, f, vol, note) in enumerate(sorted(CUES)):
        peak, length = SFX[f]; st = max(0.0, beat - peak); length = min(length, TOTAL - st)
        trk = next(k for k in range(12, 60) if busy.get(k, -1) <= st); busy[trk] = st + length
        L.append(f'      <audio data-hf-id="hf-s{i:02d}" id="sfx-{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{st:.3f}" data-duration="{length:.2f}" '
                 f'data-track-index="{trk}" data-volume="{vol}" data-audio-group="sfx"></audio> <!-- {note} -->')
    return "\n".join(L)


def badges_html():
    out, data = [], []
    for i, (seg, who) in enumerate(WHO):
        name, role, c, ink = P[who]
        side = SIDE.get(seg, "L"); pos = "left:70px;" if side == "L" else "left:640px;"
        hole = "Tee · 14:55" if seg.startswith("t1") else "Tee · 15:04" if seg.startswith("t2") else ("Approach · 14:25" if seg == "appr" else "Putt · 14:33")
        out.append(f'<div id="bd{i}" class="ov badge" style="{pos} --c:{c}; --bt:{ink};"><div class="strap"></div><div class="clip"></div>'
                   f'<div class="card"><div class="band mono">Kinrara · Flight 1</div><div class="nm">{name}</div>'
                   f'<div class="rl mono">{role}</div><div class="sh mono">{hole}</div></div></div>')
        data.append({"id": f"bd{i}", "t0": round(S(seg) + 0.05, 3), "t1": round(E(seg) - 0.15, 3)})
    lineup = "".join(f'<div class="mini" style="--c:{P[k][2]}; --bt:{P[k][3]};"><div class="nm">{P[k][0]}</div><div class="rl mono">{P[k][1]}</div></div>'
                     for k in ("reza", "me", "kimi", "taza"))
    return "\n      ".join(out), data, lineup


def main():
    bh, bd, lineup = badges_html()
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": B, "TOTAL": TOTAL, "BADGES": bd}
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{BADGES}}", bh).replace("{{LINEUP}}", lineup)
              .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written, total", TOTAL)


if __name__ == "__main__":
    main()
