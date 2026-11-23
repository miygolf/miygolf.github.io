#!/usr/bin/env python3
"""Writes index.html for MIY GOLF Ep1 "Break 100": a top-down "Range Map" explainer rebuilt in HyperFrames, every beat anchored to a word
of the owner's voice-over (edit/voice_map.json from tools/build_voice.py). The owner's slide video (.src/ep1.mp4) is the storyboard
(content, numbers, wording); no footage is used. SFX: Mixkit. No music.
Run from the project folder:  python3 tools/build_index.py
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VM = json.load(open(os.path.join(ROOT, "edit", "voice_map.json")))
P = {p["key"]: p for p in VM["pieces"]}
TOTAL = round(VM["total_voice"] + 2.4, 3)       # hold the CTA card after the last word


def ft(src):
    """recording time -> film time (through the tightened piece maps)"""
    for p in VM["pieces"]:
        a, b = p["src"]
        if a - 0.02 <= src <= b + 0.02:
            src = src + p.get("offset", 0.0)           # transcript time -> real sound (measured per phrase)
            m = p["map"]; best = m[0]
            for s, f in m:
                if s <= src: best = (s, f)
            return round(best[1] + (src - best[0]), 3)
    raise ValueError(src)


S = lambda k: P[k]["start"]; E = lambda k: P[k]["end"]
# word anchors (recording seconds, large-v3)
W = {k: ft(v) for k, v in {
    "minit": 2.52, "drill3": 3.86, "tak": 4.92, "cantik": 5.64, "break": 1.44, "range": 9.42, "tiga": 10.82,
    "satu": 11.94, "sasaran": 13.22, "fairway": 14.70, "pukul10": 16.42, "driver": 17.26, "kira": 18.62, "masuk1": 20.24,
    "bawah6": 21.50, "hybrid": 23.40, "wood": 24.22, "mana": 25.48, "kayu": 28.42, "teeoff": 30.32,
    "kedua": 31.56, "7iron": 32.66, "rendah": 34.36, "punch": 36.00, "meter": 37.74, "pokok": 39.78, "jarang": 42.26, "lapan": 47.44,
    "ketiga": 49.10, "lag": 49.66, "berhenti": 51.84, "panjang": 53.84, "bukanmasuk": 56.76,
    "pergi": 58.82, "teeoff2": 62.62, "bagitahu": 64.32, "dari10": 67.00}.items()}

# captions: one short line per piece (spoken words, cleaned)
CAPS = [("hook1", "30 minit je."), ("hook2", "3 drill. Tak payah swing cantik."), ("ep", "Episod 1, Break 100."),
        ("intro", "Dekat range minggu ni, kau buat 3 benda ni."),
        ("d1a", "Satu, pilih 2 sasaran untuk fairway."), ("d1b", "Pukul 10 bola dengan driver."), ("d1c", "Kira berapa banyak yang masuk."),
        ("d1d", "Kalau bawah 6, cuba hybrid atau 3 wood."), ("d1e", "Mana lagi banyak masuk, consider kayu tu untuk tee off."),
        ("d2a", "Yang kedua, 7 iron, bola rendah atau punch, 20–30 meter."), ("d2b", "Ini pukulan masa kau belakang pokok."),
        ("d2c", "Jarang orang latih kat range, sebab tu hole jadi 8."),
        ("d3a", "Yang ketiga, lag putt jauh."), ("d3b", "Objektif: berhenti dalam 1 panjang putter, bukan masuk."),
        ("cta", "Pergi range minggu ni, buat drill tee off tu, bagitahu aku berapa masuk dari 10.")]


def caps_html():
    out, data = [], []
    for i, (k, t) in enumerate(CAPS):
        out.append(f'<div id="cap{i}" class="ov cap">{html.escape(t)}</div>')
        data.append({"id": f"cap{i}", "t0": round(S(k) - 0.05, 3), "t1": round((S(CAPS[i + 1][0]) - 0.08) if i + 1 < len(CAPS) else TOTAL - 0.1, 3)})
    return "\n      ".join(out), data


SFX = {"2568.mp3": (0.00, 0.12), "1120.mp3": (0.10, 0.14), "3005.mp3": (0.03, 0.17), "2125.mp3": (0.16, 0.30), "2073.mp3": (0.01, 0.20),
       "166.mp3": (0.30, 0.50), "1489.mp3": (0.71, 0.90), "2364.mp3": (0.01, 0.14), "2357.mp3": (0.24, 0.32)}
SEC = {"d1": S("d1a"), "d2": S("d2a"), "d3": S("d3a"), "cta": S("cta")}


def cues():
    c = [(0.05, "3005.mp3", 0.35, "30 MINIT stamps in"), (W["drill3"], "2364.mp3", 0.35, "3 DRILL"), (W["cantik"] + 0.1, "2568.mp3", 0.45, "red pen strike"),
         (W["break"], "3005.mp3", 0.35, "BREAK 100"), (W["break"] + 0.6, "2364.mp3", 0.3, "99 circled"),
         (S("intro") + 0.1, "1120.mp3", 0.35, "tile 1"), (S("intro") + 0.35, "1120.mp3", 0.35, "tile 2"), (S("intro") + 0.6, "1120.mp3", 0.35, "tile 3")]
    for k, t in SEC.items():
        c.append((t - 0.12, "166.mp3", 0.3, f"page slide {k}"))
    c += [(W["sasaran"], "2357.mp3", 0.3, "flag 1"), (W["sasaran"] + 0.25, "2357.mp3", 0.3, "flag 2")]
    for i in range(10):
        c.append((W["kira"] + 0.1 + i * 0.16, "2568.mp3", 0.3, f"driver dot {i}"))
    for i in range(10):
        c.append((W["hybrid"] + 0.1 + i * 0.12, "2568.mp3", 0.25, f"hybrid dot {i}"))
    c += [(W["kayu"], "3005.mp3", 0.35, "tee-off chip"),
          (W["punch"] + 0.05, "2125.mp3", 0.35, "punch strike"), (W["punch"] + 0.25, "1489.mp3", 0.25, "low flight draws"),
          (W["jarang"] + 0.3, "3005.mp3", 0.3, "hole-8 chip"), (W["lapan"], "2364.mp3", 0.4, "8 pulse"),
          (W["berhenti"], "2073.mp3", 0.35, "putt 1"), (W["berhenti"] + 0.5, "2073.mp3", 0.3, "putt 2"), (W["berhenti"] + 1.0, "2073.mp3", 0.3, "putt 3"),
          (W["bukanmasuk"], "2364.mp3", 0.35, "BUKAN MASUK"),
          (W["dari10"], "3005.mp3", 0.35, "dari 10?")]
    return c


def audio_tags():
    L = [f'      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{VM['total_voice'] - 0.1:.3f}" data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>',
         f'      <audio data-hf-id="hf-music" id="music" class="clip" src="assets/music_bed.wav" data-start="0" data-duration="{TOTAL}" data-track-index="11" data-volume="1" data-audio-group="music"></audio> <!-- Mixkit 175 Digital Clouds, continuous bed, gentle dip under the voice (tools/build_music.py) -->']
    busy = {}
    for i, (beat, f, vol, note) in enumerate(sorted(cues())):
        peak, length = SFX[f]; st = max(0.0, beat - peak); length = min(length, TOTAL - st)
        trk = next(k for k in range(12, 80) if busy.get(k, -1) <= st); busy[trk] = st + length
        L.append(f'      <audio data-hf-id="hf-s{i:02d}" id="sfx-{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{st:.3f}" data-duration="{length:.2f}" '
                 f'data-track-index="{trk}" data-volume="{vol}" data-audio-group="sfx"></audio> <!-- {note} -->')
    return "\n".join(L)


def main():
    caps, capdata = caps_html()
    consts = {"W": W, "TOTAL": TOTAL, "CAP": capdata, "SEC": SEC, "P": {k: [S(k), E(k)] for k in P}}
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{CAPS}}", caps)
              .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written, total", TOTAL)
    print({k: v for k, v in W.items()})


if __name__ == "__main__":
    main()
