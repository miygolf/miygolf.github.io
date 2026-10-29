"""Writes index.html: footage plate with punch-ins, scene hosts, music and SFX."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
DUR = 27.0
cuts = json.load(open(ROOT / "src/cuts.json"))
# punch-in per cut segment (hides the jump cuts; origin keeps the deck over the old subtitles)
ZOOM = {"H": 1.12, "A1": 1.0, "A2": 1.06, "A3": 1.0, "A4": 1.08, "B1": 1.0, "B2": 1.08,
        "C1": 1.0, "C2": 1.06, "C3": 1.1, "C4": 1.0, "D1": 1.04, "E1": 1.0, "E2": 1.06,
        "E3": 1.0, "F1": 1.06, "F2": 1.0}
zooms = [[round(c[3], 3), ZOOM[c[0]]] for c in cuts]

SCENES = [  # id, start, duration
    ("hook", 0.0, 1.5), ("problem", 4.6, 5.6), ("why", 9.95, 6.6),
    ("fix", 16.45, 6.8), ("keys", 23.05, DUR - 23.05),
]
# id, file, hit time (film), peak offset in file, volume, media start, duration
SFX = [
    ("sfx-slam", "impact-bass-1", 0.0, 0.0, 0.5, 0, 1.6),
    ("sfx-scratch", "record-scratch", 1.42, 0.10, 0.45, 0.65, 1.1),
    ("sfx-wh1", "whoosh", 4.70, 0.162, 0.35, 0, 0.57),
    ("sfx-pop1", "pop", 5.26, 0.12, 0.4, 0, 0.72),
    ("sfx-pop2", "pop", 6.28, 0.12, 0.4, 0, 0.72),
    ("sfx-swell", "impact-bass-2", 9.52, 1.986, 0.42, 0, 2.59),
    ("sfx-wh2", "whoosh", 10.0, 0.162, 0.3, 0, 0.57),
    ("sfx-pop3", "pop", 11.08, 0.12, 0.38, 0, 0.72),
    ("sfx-pop4", "click-soft", 13.57, 0.073, 0.5, 0, 0.37),
    ("sfx-pop5", "pop", 14.59, 0.12, 0.38, 0, 0.72),
    ("sfx-ping1", "ping", 15.55, 0.324, 0.3, 0, 1.32),
    ("sfx-build", "whoosh-cinematic", 16.5, 2.503, 0.28, 0, 3.2),
    ("sfx-spark1", "sparkle", 16.6, 0.027, 0.32, 0, 1.8),
    ("sfx-chime", "chime", 18.13, 0.418, 0.22, 0, 2.0),
    ("sfx-wrong", "error", 19.95, 0.745, 0.22, 0, 1.62),
    ("sfx-pop6", "pop", 20.38, 0.12, 0.4, 0, 0.72),
    ("sfx-ping2", "ping", 21.2, 0.324, 0.3, 0, 1.32),
    ("sfx-wh3", "whoosh", 23.13, 0.162, 0.35, 0, 0.57),
    ("sfx-tick1", "click-soft", 23.35, 0.073, 0.5, 0, 0.37),
    ("sfx-tick2", "click-soft", 23.65, 0.073, 0.5, 0, 0.37),
    ("sfx-tick3", "click-soft", 24.3, 0.073, 0.5, 0, 0.37),
    ("sfx-spark2", "sparkle", 24.36, 0.027, 0.3, 0, 1.8),
    ("sfx-note", "notification", 25.25, 0.229, 0.32, 0, 2.0),
]

def bed_lane(points):
    return json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [{"t": t, "v": v} for t, v in points]}]}).replace('"', "&quot;")

scene_hosts = "\n".join(
    f'''      <div id="{sid}" class="clip" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html"
        data-start="{s}" data-duration="{round(d, 3)}" data-track-index="{3 + i}" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: {5 + i}"></div>'''
    for i, (sid, s, d) in enumerate(SCENES))

sfx_tags = "\n".join(
    f'      <audio id="{aid}" class="clip" src="assets/sfx/{f}.mp3" data-start="{round(max(0, hit - pk), 3)}" '
    f'data-duration="{dur}" data-media-start="{ms}" data-volume="{vol}" data-track-index="{20 + i % 3}" data-audio-group="sfx"></audio>'
    for i, (aid, f, hit, pk, vol, ms, dur) in enumerate(SFX))

html = f'''<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      /* "Fairway notes": dark fairway glass deck, cream yardage cards, alignment-stick lime */
      :root {{
        --ink: #0b2b1e;
        --cream: #f5f0e1;
        --lime: #d4ff3a;
        --signal: #e8361f;
      }}
      * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }}
      html,
      body {{
        width: 1080px;
        height: 1920px;
        overflow: hidden;
        background: #06140e;
      }}
      #root {{
        position: relative;
        width: 1080px;
        height: 1920px;
        overflow: hidden;
      }}
      #cam {{
        position: absolute;
        inset: 0;
        transform-origin: 560px 300px;
        z-index: 1;
      }}
      #plate {{
        position: absolute;
        left: 0;
        top: 0;
        width: 1080px;
        height: 1920px;
        object-fit: cover;
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      <div id="cam">
        <video id="plate" class="clip" src="assets/edit.mp4" data-start="0" data-duration="{DUR}" data-track-index="0"
          data-has-audio="true" data-volume="1" playsinline></video>
      </div>
{scene_hosts}
      <div id="captions" class="clip" data-composition-id="captions" data-composition-src="compositions/captions.html"
        data-start="0" data-duration="{DUR}" data-track-index="2" data-track-kind="captions"
        data-width="1080" data-height="1920" style="z-index: 20"></div>
      <audio id="bgm-hook" class="clip" src="assets/bgm/bed.wav" data-start="0" data-duration="1.44" data-volume="0.14"
        data-fade-out="0.04" data-track-index="10" data-audio-group="music"></audio>
      <audio id="bgm" class="clip" src="assets/bgm/bed.wav" data-start="1.5" data-duration="{DUR - 1.5}" data-volume="1"
        data-fade-in="0.08" data-fade-out="0.9" data-track-index="11" data-audio-group="music"
        data-automation="{bed_lane([(0, 0.14), (23.6, 0.14), (24.0, 0.4), (DUR - 1.5, 0.4)])}"></audio>
{sfx_tags}
    </div>
    <script>
      (function () {{
        const tl = gsap.timeline({{ paused: true }});
        const ZOOMS = {json.dumps(zooms)};
        ZOOMS.forEach(([t, s]) => tl.set("#cam", {{ scale: s }}, t));
        // slam shake on the hook stamp
        [[0.0, 7, -5], [0.04, -6, 4], [0.08, 4, -3], [0.12, -2, 2], [0.16, 0, 0]].forEach(([t, x, y]) =>
          tl.set("#cam", {{ x, y }}, t));
        // small kick when "sangat tinggi" lands
        [[9.52, 0, 5], [9.56, 0, -4], [9.6, 0, 2], [9.64, 0, 0]].forEach(([t, x, y]) => tl.set("#cam", {{ x, y }}, t));
        window.__timelines["main"] = tl;
      }})();
    </script>
  </body>
</html>
'''
(ROOT / "index.html").write_text(html)
print("index.html written")
