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
def _try(v):
    try:
        return ft(v)
    except ValueError:
        return None


_W = {k: _try(v) for k, v in {
    "minit": 2.52, "drill3": 3.86, "tak": 4.92, "cantik": 5.64, "break": 1.44, "range": 9.42, "tiga": 10.82,
    "satu": 11.94, "sasaran": 13.22, "fairway": 14.70, "pukul10": 16.42, "driver": 17.26, "kira": 18.62, "masuk1": 20.24,
    "bawah6": 21.50, "hybrid": 23.40, "wood": 24.22, "mana": 25.48, "kayu": 28.42, "teeoff": 30.32,
    "kedua": 31.56, "7iron": 32.66, "rendah": 34.36, "punch": 36.00, "meter": 37.74, "pokok": 39.78, "jarang": 42.26, "lapan": 47.44,
    "ketiga": 49.10, "lag": 49.66, "berhenti": 51.84, "panjang": 53.84, "bukanmasuk": 56.76,
    "pergi": 58.82, "buat": 61.20, "teeoff2": 62.62, "bagitahu": 64.32, "dari10": 67.00}.items()}
W = {k: v for k, v in _W.items() if v is not None}

# captions: one short line per piece (spoken words, cleaned)
CAPS = [("hook1", "30 minit je."), ("hook2", "3 drill. Tak payah swing cantik."), ("ep", "Episod 1, Break 100."),
        ("intro", "Dekat range minggu ni, kau buat 3 benda ni."),
        ("d1a", "Satu, pilih 2 sasaran untuk fairway."), ("d1b", "Pukul 10 bola dengan driver."), ("d1c", "Kira berapa banyak yang masuk."),
        ("d1d", "Kalau bawah 6, cuba hybrid atau 3 wood."), ("d1e", "Mana lagi banyak masuk, consider kayu tu untuk tee off."),
        ("d2a", "Yang kedua, 7 iron, bola rendah atau punch, 20–30 meter."), ("d2b", "Ini pukulan masa kau belakang pokok."),
        ("d2c", "Jarang orang latih kat range, sebab tu hole jadi 8."),
        ("d3a", "Yang ketiga, lag putt jauh."), ("d3b", "Objektif: berhenti dalam 1 panjang putter, bukan masuk."),
        ("cta", "Pergi range minggu ni, buat drill tee off tu, bagitahu aku berapa masuk dari 10."), ("out", "Pergi range minggu ni.")]
CAPS = sorted([c for c in CAPS if c[0] in P], key=lambda c: S(c[0]))


def caps_html():
    out, data = [], []
    for i, (k, t) in enumerate(CAPS):
        out.append(f'<div id="cap{i}" class="ov cap">{html.escape(t)}</div>')
        data.append({"id": f"cap{i}", "t0": round(S(k) - 0.05, 3) if S(k) > 0.5 else 0.0, "t1": round((S(CAPS[i + 1][0]) - 0.08) if i + 1 < len(CAPS) else TOTAL - 0.1, 3)})
    return "\n      ".join(out), data


SFX = {"2568.mp3": (0.00, 0.12), "1120.mp3": (0.10, 0.14), "3005.mp3": (0.03, 0.17), "2125.mp3": (0.16, 0.30), "2073.mp3": (0.01, 0.20),
       "166.mp3": (0.30, 0.50), "1489.mp3": (0.71, 0.90), "2364.mp3": (0.01, 0.14), "2357.mp3": (0.24, 0.32)}
_G = {"d1": ["d1a", "d1b", "d1c", "d1d", "d1e"], "d2": ["d2a", "d2b", "d2c"], "d3": ["d3a", "d3b"], "cta": ["cta"], "out": ["out"]}
SEC = {k: min(S(x) for x in v if x in P) for k, v in _G.items() if any(x in P for x in v)}
PART = json.load(open(os.path.join(ROOT, "part.json"))) if os.path.exists(os.path.join(ROOT, "part.json")) else {}


def cues():
    c = []
    add = lambda key, dt, f, v, n: c.append((W[key] + dt, f, v, n)) if key in W else None
    if "hook1" in P: c.append((0.05, "3005.mp3", 0.35, "30 MINIT stamps in"))
    elif PART: c.append((0.05, "3005.mp3", 0.35, "part card on frame 0"))
    add("drill3", 0, "2364.mp3", 0.35, "3 DRILL"); add("cantik", 0.1, "2568.mp3", 0.45, "red pen strike")
    add("break", 0, "3005.mp3", 0.35, "BREAK 100"); add("break", 0.6, "2364.mp3", 0.3, "99 circled")
    if "intro" in P:
        c += [(S("intro") + 0.1 + k * 0.25, "1120.mp3", 0.35, f"tile {k + 1}") for k in range(3)]
    for k, t in SEC.items():
        if t > 0.5: c.append((t - 0.12, "166.mp3", 0.3, f"page slide {k}"))
    add("sasaran", 0, "2357.mp3", 0.3, "flag 1"); add("sasaran", 0.25, "2357.mp3", 0.3, "flag 2")
    for i in range(10):
        add("kira", 0.1 + i * 0.16, "2568.mp3", 0.3, f"driver dot {i}"); add("hybrid", 0.1 + i * 0.12, "2568.mp3", 0.25, f"hybrid dot {i}")
    add("kayu", 0, "3005.mp3", 0.35, "tee-off chip")
    add("punch", 0.05, "2125.mp3", 0.35, "punch strike"); add("punch", 0.25, "1489.mp3", 0.25, "low flight draws")
    add("jarang", 0.3, "3005.mp3", 0.3, "hole-8 chip"); add("lapan", 0, "2364.mp3", 0.4, "8 pulse")
    for k in range(3): add("berhenti", 0.5 * k, "2073.mp3", 0.35 if k == 0 else 0.3, f"putt {k + 1}")
    add("bukanmasuk", 0, "2364.mp3", 0.35, "BUKAN MASUK"); add("dari10", 0, "3005.mp3", 0.35, "dari 10?")
    if "out" in P: c.append((S("out") + 1.2, "3005.mp3", 0.3, "next-part card"))
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
    consts = {"W": W, "TOTAL": TOTAL, "CAP": capdata, "SEC": SEC, "P": {k: [S(k), E(k)] for k in P}, "PART": PART}
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{CAPS}}", caps)
              .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written, total", TOTAL)
    print({k: v for k, v in W.items()})


if __name__ == "__main__":
    main()
