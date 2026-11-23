#!/usr/bin/env python3
"""Writes index.html for MIY GOLF Ep2 "Break 100" (bunker line / chip to towel / 1 m circle) in the "Blueprint" look, every beat anchored to a
word of the owner's voice-over (edit/voice_map.json from tools/build_voice.py). The owner's slide video (.src/ep2.mp4) is the storyboard
(content, numbers, wording); no footage. SFX: Mixkit (assets/sfx/CREDITS.md). Music: continuous Mixkit "Digital Clouds" bed (tools/build_music.py).
Split parts: part.json (tools/make_parts.py) picks the pieces; scenes whose phrases are absent are skipped.
Run from the project folder:  python3 tools/build_index.py
"""
import json, os, html, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VM = json.load(open(os.path.join(ROOT, "edit", "voice_map.json")))
P = {p["key"]: p for p in VM["pieces"]}
TOTAL = round(VM["total_voice"] + 2.4, 3)       # hold the end card after the last word
PART = json.load(open(os.path.join(ROOT, "part.json"))) if os.path.exists(os.path.join(ROOT, "part.json")) else {}


def ft(src):
    """recording time -> film time (through the tightened piece maps); None if the phrase is not in this cut"""
    for p in VM["pieces"]:
        a, b = p["src"]
        if a - 0.02 <= src <= b + 0.02:
            m = p["map"]; best = m[0]
            for s, f in m:
                if s <= src: best = (s, f)
            return round(best[1] + (src - best[0]), 3)
    return None


S = lambda k: P[k]["start"]; E = lambda k: P[k]["end"]
# word anchors: (recording s, lag). Full-pass whisper words run ~0.2 s early on this recording (lag 0.2); crop re-runs are on time (lag 0).
_A = {"bunker": (5.70, .2), "tiga": (6.12, .2), "keluar": (7.80, .2), "untuk": (9.00, .2), "minit": (10.10, .2),
      "garisan": (14.36, .2), "pukul": (16.78, .2), "tepat": (17.26, .2), "payah": (19.22, .2), "konsisten": (21.74, .2), "letak": (23.96, .2),
      "cm": (25.94, .2), "target": (28.50, .2), "lapan": (30.14, .2), "kisah": (33.28, .2), "lubang1": (35.00, .2),
      "kedua": (36.30, .2), "green": (40.28, .2), "mendarat": (42.28, .2),
      "tuala": (39.18, .2), "chip": (42.86, 0), "kira": (45.68, 0), "fokus": (48.20, 0), "bukan": (49.90, 0),
      "susun": (52.16, .2), "bulatan": (55.38, .2), "meter": (56.20, .2), "masukkan": (57.86, .2), "terlepas": (61.48, 0), "balik": (63.50, .2),
      "putt": (65.14, 0), "kaki": (67.02, 0), "handicap": (67.62, 0), "p60": (70.58, 0), "scratch": (72.68, 0), "p76": (73.68, 0),
      "pergi": (77.30, 0), "bagitahu": (80.54, 0), "dari10": (81.20, 0), "bunker2": (84.88, 0), "sekali2": (85.42, 0)}
W = {}
for k, (v, lag) in _A.items():
    t = ft(v + lag)
    if t is not None: W[k] = t

# captions: one short line per piece (spoken words, cleaned)
CAPS = [("hook", "Kau pernah masuk bunker 3 kali baru keluar?"), ("ep", "Episod 2, Break 100."), ("forkau", "Episod ni untuk kau. 30 minit, 3 drill."),
        ("d1a", "Satu: lukis satu garisan atas pasir,"), ("d1b", "pukul tepat kat garisan. Tak payah bola dulu."),
        ("d1c", "Dah konsisten? Letak bola 5 cm (1 inci) depan garisan."), ("d1d", "Target 8/10 keluar sekali. Dekat ke jauh lubang, tak kisah."),
        ("d2a", "Dua: letak tuala atas green, tempat bola mendarat."), ("d2b", "Chip 10 bola, kira berapa mendarat atas tuala."),
        ("d2c", "Fokus tempat mendarat, bukan lubang."),
        ("d3a", "Last: susun 6 bola, bulatan 1 meter keliling lubang. Masuk semua berturut-turut."), ("d3b", "Terlepas satu? Buat balik."),
        ("d3c", "Putt 3–6 kaki: handicap tengah–tinggi masuk 60% je."), ("d3d", "Scratch golfer: 76%."),
        ("cta", "Pergi practice area minggu ni. Bagitahu aku: dari 10, berapa keluar bunker sekali pukul?"), ("out", "Pergi practice area minggu ni.")]
CAPS = sorted([c for c in CAPS if c[0] in P], key=lambda c: S(c[0]))


def caps_html():
    out, data = [], []
    for i, (k, t) in enumerate(CAPS):
        out.append(f'<div id="cap{i}" class="ov cap">{html.escape(t)}</div>')
        data.append({"id": f"cap{i}", "t0": round(S(k) - 0.05, 3) if S(k) > 0.5 else 0.0,
                     "t1": round((S(CAPS[i + 1][0]) - 0.08) if i + 1 < len(CAPS) else TOTAL - 0.1, 3)})
    return "\n      ".join(out), data


# scene sections
_d2c_first = "d2c" in P and "d2a" in P and S("d2c") < S("d2a")
_G = {"hook": ["hook"], "ep": ["ep", "forkau"], "d1": ["d1a", "d1b", "d1c", "d1d"],
      "q2": ["d2c"] if _d2c_first else [], "d2": ["d2a", "d2b"] + ([] if _d2c_first else ["d2c"]),
      "d3": ["d3a", "d3b", "d3c", "d3d"], "cta": ["cta"], "out": ["out"]}
SEC = {k: min(S(x) for x in v if x in P) for k, v in _G.items() if any(x in P for x in v)}
LIKE_T = None
if PART.get("like"):
    LIKE_T = round(W["sekali2"] + 1.2, 3) if "sekali2" in W else round(S("out") + 2.0, 3)

D1 = [1, 1, 0, 1, 1, 1, 1, 0, 1, 1]          # example: 8 of 10 out first time (target)
D2 = [1, 0, 1, 1, 0, 1, 0, 1, 1, 0]          # example: 6 of 10 land on the towel
IN_PTS = [(262, 200), (300, 262), (350, 205), (392, 250), (282, 232), (340, 280)]
OUT_PTS = [(530, 215), (200, 340), (490, 320), (160, 220)]


def land_svg():
    ii, oo, out = iter(IN_PTS), iter(OUT_PTS), []
    for v in D2:
        x, y = next(ii) if v else next(oo)
        if v: out.append(f'<circle class="land" data-o="{x} {y}" cx="{x}" cy="{y}" r="13" fill="#ffd84a" stroke="#0a2a59" stroke-width="3"/>')
        else: out.append(f'<g class="land" data-o="{x} {y}"><circle cx="{x}" cy="{y}" r="13" fill="none" stroke="#ff7a66" stroke-width="4"/>'
                         f'<path d="M {x-7} {y-7} L {x+7} {y+7} M {x+7} {y-7} L {x-7} {y+7}" stroke="#ff7a66" stroke-width="4"/></g>')
    return "\n          ".join(out)


def ring_svg():
    out = []
    for a in (30, 90, 150, 210, 270, 330):
        x, y = 330 + 150 * math.cos(math.radians(a)), 250 + 150 * math.sin(math.radians(a))
        out.append(f'<circle class="rb" data-o="{x:.0f} {y:.0f}" cx="{x:.0f}" cy="{y:.0f}" r="15" fill="#eaf2ff" stroke="#0a2a59" stroke-width="3"/>')
    return "\n          ".join(out)


SFX = {"2568.mp3": (0.00, 0.12), "1120.mp3": (0.10, 0.14), "3005.mp3": (0.03, 0.17), "2125.mp3": (0.16, 0.30), "2073.mp3": (0.01, 0.20),
       "166.mp3": (0.30, 0.50), "1489.mp3": (0.71, 0.90), "2364.mp3": (0.01, 0.14), "2357.mp3": (0.24, 0.32)}


def cues():
    c = []
    add = lambda key, dt, f, v, n: c.append((W[key] + dt, f, v, n)) if key in W else None
    c.append((0.05, "3005.mp3", 0.35, "title on frame 0"))
    if "hook" in P:
        tA = W.get("bunker", 1.2); tK = W.get("keluar", tA + 2)
        c += [(tA + 0.35, "2568.mp3", 0.35, "arc 1 hits the lip ✗"), ((tA + tK) / 2 + 0.35, "2568.mp3", 0.35, "arc 2 ✗"),
              (tK + 0.4, "2364.mp3", 0.35, "arc 3 out ✓")]
    for k, t in SEC.items():
        if t > 0.5 and k != "q2": c.append((t - 0.05, "166.mp3", 0.3, f"parallel rule slides ({k})"))
    if "ep" in P: c.append((S("ep") + 0.05, "3005.mp3", 0.35, "title block"))
    add("untuk", 0, "2364.mp3", 0.4, "UNTUK KAU stamp")
    for i in range(3): add("minit", i * 0.25, "1120.mp3", 0.35, f"drill tile {i + 1}")
    add("garisan", -0.1, "1489.mp3", 0.25, "line drawn in the sand")
    add("pukul", 0.1, "2125.mp3", 0.35, "splash 1 on the line")
    for i in (1, 2): add("pukul", 0.1 + i * 0.35, "2568.mp3", 0.3, f"splash {i + 1}")
    add("letak", 0.05, "2357.mp3", 0.3, "ball placed"); add("cm", 0, "2568.mp3", 0.3, "5 cm dimension")
    for i in range(10): add("lapan", 0.1 + i * 0.14, "2568.mp3", 0.25, f"target dot {i + 1}")
    add("lapan", 1.5, "3005.mp3", 0.35, "8/10")
    if "q2" in SEC: add("bukan", 0.15, "2568.mp3", 0.4, "red-pencil strike on 'lubang'")
    add("tuala", 0, "2357.mp3", 0.3, "towel")
    for i in range(10): add("chip", 0.25 + i * 0.16, "2568.mp3", 0.25, f"landing {i + 1}")
    add("kira", 1.2, "3005.mp3", 0.35, "6/10")
    if "q2" not in SEC: add("fokus", 0, "2364.mp3", 0.35, "FOKUS chip")
    add("bulatan", 0, "1489.mp3", 0.25, "1 m circle drawn"); add("meter", 0, "2568.mp3", 0.3, "radius 1 m")
    for i in range(6): add("susun", 0.1 + i * 0.12, "2568.mp3", 0.22, f"ball {i + 1} placed")
    for i in range(6): add("masukkan", 0.34 + i * 0.3, "2073.mp3", 0.3, f"ball {i + 1} drops")
    add("terlepas", 0.4, "2364.mp3", 0.4, "counter resets to 0/6")
    add("putt", 0, "3005.mp3", 0.3, "stat card"); add("p60", -0.1, "1120.mp3", 0.3, "60% bar"); add("p76", -0.1, "1120.mp3", 0.3, "76% bar")
    if "out" in P:
        for i in range(3): c.append((S("out") + 0.5 + i * 0.3, "1120.mp3", 0.3, f"recap row {i + 1}"))
        c.append((S("out") + 1.6, "3005.mp3", 0.3, "end chip"))
    add("dari10", 0, "3005.mp3", 0.35, "10 circles")
    if LIKE_T is not None: c.append((LIKE_T, "3005.mp3", 0.3, "like-for-part-2 chip"))
    return c


def audio_tags():
    L = [f'      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{VM["total_voice"] - 0.1:.3f}" data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>',
         f'      <audio data-hf-id="hf-music" id="music" class="clip" src="assets/music_bed.wav" data-start="0" data-duration="{TOTAL}" data-track-index="11" data-volume="1" data-audio-group="music"></audio> <!-- Mixkit 175 Digital Clouds, continuous bed (tools/build_music.py) -->']
    busy = {}
    for i, (beat, f, vol, note) in enumerate(sorted(cues())):
        peak, length = SFX[f]; st = max(0.0, beat - peak); length = min(length, TOTAL - st)
        trk = next(k for k in range(12, 80) if busy.get(k, -1) <= st); busy[trk] = st + length
        L.append(f'      <audio data-hf-id="hf-s{i:02d}" id="sfx-{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{st:.3f}" data-duration="{length:.2f}" '
                 f'data-track-index="{trk}" data-volume="{vol}" data-audio-group="sfx"></audio> <!-- {note} -->')
    return "\n".join(L)


def main():
    caps, capdata = caps_html()
    consts = {"W": W, "TOTAL": TOTAL, "CAP": capdata, "SEC": SEC, "P": {k: [S(k), E(k)] for k in P}, "PART": PART, "LIKE_T": LIKE_T, "D1": D1, "D2": D2}
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags()).replace("{{CAPS}}", caps)
              .replace("{{DOTS10}}", "<i></i>" * 10).replace("{{DOTS10B}}", "<i></i>" * 10).replace("{{CDOTS}}", "<i></i>" * 10)
              .replace("{{LAND}}", land_svg()).replace("{{RING6}}", ring_svg())
              .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written, total", TOTAL, "sections", SEC)


if __name__ == "__main__":
    main()
