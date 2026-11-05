"""Generate index.html (picture order, scene hosts, music and SFX) from one sequence.

Edit SEQ / the scene starts / CUES here, then:  python3 tools/build_index.py
Durations of footage come from the files on disk (tools/prepare_footage.sh makes them).
"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def dur(rel):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(HERE / rel)], capture_output=True, text=True).stdout
    return round(float(out), 4)


# (id, kind, src, duration or None, extra)   kind: v = video, s = still (freeze)
SEQ = [
    ("v-hook", "v", "footage/hook.mp4", None, ""),
    ("s-hook", "s", "stills/a_imp.jpg", 1.6, "1.035"),
    # BEFORE 09:55
    ("v-a1", "v", "footage/a1.mp4", None, "audio"),
    ("v-a2", "v", "footage/a2.mp4", None, ""),
    ("v-a3", "v", "footage/a3.mp4", None, ""),
    ("s-a1", "s", "stills/b_d78.jpg", 2.2, "1.012"),    # cause 1: hands far from body
    ("v-a4", "v", "footage/a4.mp4", None, ""),
    ("s-a2", "s", "stills/b_imp.jpg", 2.2, "1.012"),    # cause 2: no body clearance
    # AFTER 11:23
    ("v-b1", "v", "footage/b1.mp4", None, "audio"),
    ("v-b2", "v", "footage/b2.mp4", None, ""),
    ("v-b3", "v", "footage/b3.mp4", None, ""),
    ("s-b1", "s", "stills/a_tr.jpg", 2.2, "1.012"),     # step 1: lower body first
    ("v-b4", "v", "footage/b4.mp4", None, ""),
    ("s-b2", "s", "stills/a_dlv.jpg", 2.2, "1.012"),    # step 2: club head in front of chest
    ("v-b5", "v", "footage/b5.mp4", None, ""),
    ("s-b3", "s", "stills/a_finfo.jpg", 2.2, "1.012"),  # step 3: turn all the way
    ("v-c1", "v", "footage/c1.mp4", None, ""),          # full speed, face-on
    ("v-c2", "v", "footage/c2.mp4", None, ""),          # full speed, down the line
]
COMPARE_AT, COMPARE_DUR = None, 4.25   # compare starts 0.25 s before the last clip ends (paper covers it)
OUTRO_VIDEO = ("v-out", "footage/outro.mp4")
OUTRO_HOLD = ("s-out", "stills/a_fin.jpg", 1.1633)

MUSIC = False  # owner asked for SFX only (no music bed) on the final

t = 0.0
rows = []
at = {}
for vid, kind, src, d, extra in SEQ:
    d = d if d is not None else dur(f"assets/{src}")
    rows.append((vid, kind, src, round(t, 4), d, extra))
    at[vid] = round(t, 4)
    t += d
seq_end = round(t, 4)
COMPARE_AT = round(seq_end - 0.25, 4)
OUT_AT = round(COMPARE_AT + COMPARE_DUR, 4)
out_d = dur(f"assets/{OUTRO_VIDEO[1]}")
rows.append((OUTRO_VIDEO[0], "v", OUTRO_VIDEO[1], OUT_AT, out_d, ""))
rows.append((OUTRO_HOLD[0], "s", OUTRO_HOLD[1], round(OUT_AT + out_d, 4), OUTRO_HOLD[2], "1.02"))
TOTAL = round(OUT_AT + out_d + OUTRO_HOLD[2], 4)
at["v-out"] = OUT_AT

# Extend the last sequence clip under the paper slide-in so nothing black shows.
pic = []
z = 1
pushes = []
for vid, kind, src, start, d, extra in rows:
    if vid == "v-c2":
        d = round(d + 0.3, 4)  # last frame holds under the paper (video holds its last frame)
    if kind == "v":
        sound = 'data-has-audio="true" data-volume="0.9"' if extra == "audio" else "muted"
        pic.append(f'      <video id="{vid}" class="clip full" src="assets/{src}" data-start="{start}" data-duration="{d}" data-track-index="0" {sound} playsinline style="z-index:{z}"></video>')
    else:
        pic.append(f'      <div id="{vid}" class="clip still-wrap" data-start="{start}" data-duration="{d}" data-track-index="0" style="z-index:{z}"><img id="{vid}-img" src="assets/{src}" alt="" /></div>')
        pushes.append(f'      push("#{vid}-img", {start}, {d}, {extra});')
    z += 1

# scene hosts (start, duration)
ROLLA = (round(at["v-a1"] - 0.15, 4), round(at["v-b1"] - at["v-a1"] + 0.3, 4))
ROLLB = (round(at["v-b1"] - 0.15, 4), round(COMPARE_AT + 0.3 - (at["v-b1"] - 0.15), 4))
hosts = [
    ("hook", 0, at["v-a1"]),
    ("rolla", *ROLLA),
    ("rollb", *ROLLB),
    ("compare", COMPARE_AT, COMPARE_DUR),
    ("outro", OUT_AT, round(TOTAL - OUT_AT, 4)),
]
gfx = []
for i, (cid, s, d) in enumerate(hosts):
    gfx.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{s}" data-duration="{d}" data-track-index="{i + 1}" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:{40 + i}"></div>')

# ---------- sound ----------
# Impact (visual) times
IMP = {
    "a2": at["v-a2"] + 7 / 30, "b2": at["v-b2"] + 7 / 30,
    "c1": at["v-c1"] + 33 / 30, "c2": at["v-c2"] + 30 / 30, "out": OUT_AT + 12 / 30,
}
FREEZES = [r for r in rows if r[1] == "s"]


def lane(pts):
    j = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [{"t": round(a, 3), "v": v} for a, v in pts]}]}, separators=(",", ":"))
    return j.replace('"', "&quot;")


duck = []
for k in ("a2", "b2", "c1", "c2", "out"):
    duck += [(IMP[k] - 0.3, None), (IMP[k] - 0.15, 0.24), (IMP[k] + 0.35, 0.24), (IMP[k] + 0.6, None)]
pts = [(0, 0.42)]
base = lambda x: 0.42 if x < at["v-a1"] else (0.46 if x >= COMPARE_AT else 0.36)
for x, v in duck:
    pts.append((x, base(x) if v is None else v))
pts.append((TOTAL, 0.46))
pts.sort()

aud = [] if not MUSIC else [f'      <audio id="music" data-timeline-role="music" class="clip" src="assets/music/hiphop02.mp3" data-start="0" data-duration="{TOTAL}" data-media-start="0.49" data-track-index="10" data-volume="1" data-fade-out="1.6"\n        data-automation="{lane(pts)}"></audio>']
# real strikes from each 1x take, pulled earlier to undo the phone's audio lag
NAT = [("nat-a2", "footage/a2.mp4", at["v-a2"], 0.22), ("nat-b2", "footage/b2.mp4", at["v-b2"], 0.2),
       ("nat-c1", "footage/c1.mp4", at["v-c1"], 0.17), ("nat-c2", "footage/c2.mp4", at["v-c2"], 0.18)]
for i, src, st, ms in NAT:
    d = round(dur(f"assets/{src}") - ms, 3)
    aud.append(f'      <audio id="{i}" class="clip" src="assets/{src}" data-start="{st}" data-duration="{d}" data-media-start="{ms}" data-track-index="11" data-volume="1.3" data-fade-out="0.15"></audio>')

PEAK = {"1473": .185, "1438": .117, "2909": .127, "1489": .715, "1442": 0, "1444": 0, "2121": .153, "2126": .175,
        "1440": .166, "1491": .296, "2998": .067, "1468": .309, "1530": .358, "2369": .171, "1143": .63}
CAP = {"2909": 2.2, "1489": 1.3, "1442": 0.45, "1444": 0.45, "1143": 2.6}
cues = []  # (id, file, picture time, volume, extra)
cues += [("sx-hook-swing", "1473", 0.6, .45, ""), ("sx-hook-shutter", "1438", 0.8, 1, ""), ("sx-hook-bass", "2909", 0.8, .55, ' data-fade-out="0.8"')]
for n, cut in (("1", at["v-a1"]), ("2", at["v-b1"])):
    cues += [(f"sx-adv{n}-air", "1489" if n == "1" else "1491", cut, .55 if n == "1" else .8, ""),
             (f"sx-adv{n}-proj", "1442" if n == "1" else "1444", cut - 0.18, .8, ' data-media-start="%s" data-fade-in="0.04" data-fade-out="0.12"' % ("1.0" if n == "1" else "0.3"))]
cues += [("sx-a2-hit", "2121", IMP["a2"], .45, ""), ("sx-b2-hit", "2126", IMP["b2"], .45, ""),
         ("sx-c1-hit", "2126", IMP["c1"], .35, ""), ("sx-c2-hit", "2121", IMP["c2"], .35, "")]
shutters = ["1438", "1440"]
for i, (vid, kind, src, start, d, extra) in enumerate(FREEZES[1:-1]):
    cues.append((f"sx-{vid}-shutter", shutters[i % 2], start, 1 if shutters[i % 2] == "1438" else .7, ""))
    cues.append((f"sx-{vid}-mark", "2998", start + 0.5, .55, ""))
# slow-mo whooshes into freezes
for vid in ("v-a3", "v-a4", "v-b3", "v-b5"):
    nxt = [r for r in rows if r[3] > at[vid]][0]
    cues.append((f"sx-{vid}-swing", "1473" if vid in ("v-a3", "v-b5") else "1468", nxt[3] - 0.15, .4, ""))
cues += [("sx-a2-loupe", "1491", at["s-a2"] + 0.48, .7, ""), ("sx-a2-mark2", "2998", at["s-a2"] + 0.84, .5, "")]
cues += [("sx-full-whoosh", "1468", at["v-c1"], .5, "")]
C = COMPARE_AT
cues += [("sx-cmp-air", "1468", C + 0.2, .5, ""), ("sx-cmp-paper1", "1530", C + 0.42, 1, ""), ("sx-cmp-paper2", "1530", C + 0.67, .9, ""),
         ("sx-cmp-mark1", "2998", C + 1.1, .6, ""), ("sx-cmp-mark2", "2998", C + 1.45, .6, ""), ("sx-cmp-scribble", "2369", C + 1.85, .9, "")]
cues += [("sx-out-air", "1489", OUT_AT, .5, ""), ("sx-out-hit", "2126", IMP["out"], .6, ""),
         ("sx-out-impact", "1143", IMP["out"] + 0.03, .55, ' data-fade-out="0.8"'), ("sx-out-mark", "2369", OUT_AT + 1.3, .8, "")]

tracks = {}
for cid, f, pic_t, vol, ex in cues:
    start = round(max(0, pic_t + 1 / 30 - PEAK[f]), 3)
    ms = float(ex.split('data-media-start="')[1].split('"')[0]) if "media-start" in ex else 0
    d = CAP.get(f, round(dur(f"assets/sfx/{f}.mp3") - ms - 0.01, 3))
    tr = 12
    while any(not (start + d <= s0 or start >= s0 + d0) for s0, d0 in tracks.get(tr, [])):
        tr += 1
    tracks.setdefault(tr, []).append((start, d))
    aud.append(f'      <audio id="{cid}" class="clip" src="assets/sfx/{f}.mp3" data-start="{start}" data-duration="{d}" data-track-index="{tr}" data-volume="{vol}"{ex}></audio>')

TEMPLATE = (HERE / "tools" / "index.template.html").read_text()
html = (TEMPLATE.replace("{{TOTAL}}", str(TOTAL)).replace("{{PICTURE}}", "\n".join(pic))
        .replace("{{GRAPHICS}}", "\n".join(gfx)).replace("{{AUDIO}}", "\n".join(aud))
        .replace("{{PUSHES}}", "\n".join(pushes)))
(HERE / "index.html").write_text(html)
print(json.dumps({"total": TOTAL, "at": at, "compare": COMPARE_AT, "outro": OUT_AT, "hosts": hosts,
                  "impacts": {k: round(v, 3) for k, v in IMP.items()}}, indent=1))
