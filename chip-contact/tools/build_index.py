"""Write index.html: A-roll, riso print freezes, punch-ins, overlay compositions and the whole sound design.

Every film time below comes from edit/timeline.json (built by build_aroll.py).
SFX are placed so the file's measured peak lands on the picture beat (start = beat - peak).
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
T = {s["id"]: s for s in json.load(open("edit/timeline.json"))["segments"]}
TOTAL = json.load(open("edit/timeline.json"))["total"]
t0 = lambda k: T[k]["t0"]
t1 = lambda k: T[k]["t1"]

LIVE = {"preset": "warm-daylight", "intensity": 0.5,
        "adjust": {"contrast": 0.14, "vibrance": 0.22, "highlights": -0.3, "saturation": 0.05},
        "details": {"vignette": 0.08}}
PRINT = {"effects": {"monoScreen": 1, "monoScreenSize": 0.15, "monoScreenAngle": 0.25, "monoScreenSpread": 0.3, "monoScreenShape": 0},
         "palette": ["#1d3fbb", "#fff4f8"]}
attr = lambda o: html.escape(json.dumps(o, separators=(",", ":")), quote=True)

# measured file peaks (s): see README
PEAK = {"166": .33, "175": .49, "1464": .11, "3115": .11, "2127": .15, "2121": .15, "2125": .15, "2364": .04, "2357": .04,
        "3005": .02, "772": .51, "1530": .35, "2380": .29, "2384": .13}
DUR = {"166": .78, "175": .61, "1464": 1.1, "3115": .57, "2127": .72, "2121": .66, "2125": .68, "2364": 1.17, "2357": .38,
       "3005": .18, "772": 1.22, "1530": 1.09, "2380": .9, "2384": .35}
sfx = []
def S(name, beat, vol, why):
    sfx.append((name, round(max(0, beat - PEAK[name]), 3), vol, why))

impact_hook = t0("hook-down") + (5.12 - 4.70)       # 0.42 -> the frame where the club meets the ball
impact_full = t0("full") + (5.12 - 3.95)
S("166", 0.33, 0.30, "open: slips settle")
S("2127", impact_hook + 0.02, 0.85, "hook strike")
S("1530", t0("hook-freeze") + 0.12, 0.70, "print feed: hook freeze")
S("2364", t0("hook-freeze") + 0.04, 0.45, "ring snaps on the ball")
S("2384", 2.2, 1.6, "slips pulled back into the drum")
S("3115", t0("full"), 1.3, "dot wipe")
S("2121", impact_full + 0.02, 0.55, "1x strike (layered on the real one)")
S("175", t0("k1-slo"), 1.8, "dot wipe")
S("3005", t0("k1-slo") + 0.2, 0.5, "key 1 slips")
S("2357", t0("k1-slo") + 0.34, 0.4, "foot rings")
S("1530", t0("k1-freeze") + 0.12, 0.65, "print feed: key 1 freeze")
S("3005", t0("k1-freeze") + 0.36, 0.35, "level lines")
S("1464", t0("k2-slo"), 0.5, "cut to the ball close-up")
S("2125", t0("k2-freeze") + 0.02, 0.7, "impact freeze")
S("772", t0("k2-freeze") + 0.02, 0.4, "impact freeze weight")
S("2380", t0("k2-freeze") + 0.15, 1.4, "print feed: key 2 freeze")
S("3005", t0("k2-slo") + 0.12, 0.5, "key 2 slips")
S("166", t0("k3-turn") - 0.2, 0.28, "zoom back out")
S("3005", t0("k3-turn") + 0.3, 0.5, "key 3 slips")
S("1464", t0("k3-turn") + 0.62, 0.45, "turn arrow draws")
S("2380", t0("k3-freeze") + 0.15, 1.4, "print feed: key 3 freeze")
S("3115", t0("cta-hold"), 1.3, "dot wipe")
S("3005", t0("cta-hold") + 0.2, 0.5, "PROBLEM SAMA?")
S("1530", t0("cta-freeze") + 0.12, 0.6, "print feed: CTA freeze")
S("2357", t0("cta-freeze") + 0.24, 0.45, "SAVE slip")
for i in range(3):
    S("3005", t0("cta-hold") + 1.85 + i * 0.16, 0.32, f"recap {i + 1}")

# music bed: Mixkit "Okay" (#780), from the downbeat before section B so the band kicks in on the hook strike
MUSIC_START = 29.645
duck = [(0, .30), (0.45, .30), (0.6, .11), (1.75, .11), (2.05, .30), (2.4, .30), (2.55, .14), (5.15, .14), (5.45, .30),
        (TOTAL - 0.9, .30), (TOTAL, 0)]
auto = {"version": 1, "lanes": [{"target": "volume", "points": [{"t": round(t, 3), "v": v} for t, v in duck]}]}
fx = {"version": 1, "nodes": [
    {"type": "highpass", "id": "hp", "label": "Clear the low end for the voice", "params": {"frequency": 90}},
    {"type": "peaking", "id": "carve", "label": "Pocket for the voice", "params": {"frequency": 2500, "gain": -5, "q": 0.8}}]}

freezes = ["hook-freeze", "k1-freeze", "k2-freeze", "k3-freeze", "cta-freeze"]
prints = "\n".join(
    f'''        <div data-hf-id="hf-pw{i}" id="pw-{k}" class="print clip" data-start="{t0(k)}" data-duration="{round(t1(k) - t0(k), 4)}" data-track-index="2">
          <img data-hf-id="hf-pi{i}" class="print-img" src="assets/stills/{k}.jpg" alt="" data-color-grading="{attr(PRINT)}" />
        </div>''' for i, k in enumerate(freezes))
rollers = "\n".join(
    f'''      <div data-hf-id="hf-rl{i}" id="rl-{k}" class="roller clip" data-start="{t0(k)}" data-duration="0.3" data-track-index="7"></div>''' for i, k in enumerate(freezes))

def comp(cid, start, end, track):
    return (f'      <div data-hf-id="hf-c-{cid}" id="{cid}" class="layer" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" '
            f'data-start="{round(start, 4)}" data-duration="{round(end - start, 4)}" data-track-index="{track}" data-track-kind="graphics" data-width="1080" data-height="1920"></div>')

comps = "\n".join([
    comp("hook", 0, t0("full"), 3),
    comp("full", t0("full"), t1("full"), 3),
    comp("keys", t0("k1-slo"), t1("k3-freeze"), 3),
    comp("cta", t0("cta-hold"), TOTAL, 3),
])
# greedy lanes so no two SFX overlap on one Studio track
lanes, lane_of = [], []
for n, st, v, w in sfx:
    for li, end in enumerate(lanes):
        if end <= st:
            lanes[li] = st + DUR[n]; lane_of.append(li); break
    else:
        lanes.append(st + DUR[n]); lane_of.append(len(lanes) - 1)
audio_sfx = "\n".join(
    f'      <audio data-hf-id="hf-s{i:02d}" id="sfx-{i:02d}" class="clip" src="assets/sfx/{n}.mp3" data-start="{st}" data-duration="{DUR[n]}" '
    f'data-track-index="{12 + lane_of[i]}" data-volume="{v}" data-audio-group="sfx"></audio> <!-- {w} -->' for i, (n, st, v, w) in enumerate(sfx))

punch = {
    "hook": (0, "713px 1920px", 1.45), "full": (t0("full"), "540px 960px", 1.0),
    "k1": (t0("k1-slo"), "400px 1920px", 1.35), "k2": (t0("k2-slo"), "713px 1920px", 1.6),
    "cta": (t0("cta-hold"), "540px 900px", 1.0),
}

page = f'''<!DOCTYPE html>
<html lang="ms">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1080, height=1920">
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      /* "Riso Press": two-ink risograph zine. Riso blue #1d3fbb + fluoro pink #ff4fa3 on pink-white #fff4f8,
         misregistered ink layers, halftone dots, every freeze printed as a blue screen print. */
      @font-face {{ font-family: "Dela Gothic One"; src: url("assets/fonts/DelaGothicOne.woff2") format("woff2"); font-display: block; }}
      @font-face {{ font-family: "Instrument Sans"; font-weight: 700; src: url("assets/fonts/InstrumentSans-700.woff2") format("woff2"); font-display: block; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #fff4f8; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      #cam-move {{ position: absolute; inset: 0; z-index: 1; transform-origin: 713px 1920px; }}
      #aroll {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      .print {{ position: absolute; inset: 0; z-index: 2; }}
      .print-img {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      /* the print drum: pink roller edge with a blue ghost, rides down the frame as the print feeds in */
      .roller {{ position: absolute; left: 0; top: 0; width: 1080px; height: 22px; z-index: 4; background: #ff4fa3;
                box-shadow: 0 9px 0 0 rgba(29, 63, 187, 0.9); }}
      .layer {{ z-index: 5; }}
      #captions {{ z-index: 8; }}
      #dots {{ z-index: 9; }}
    </style>
  </head>
  <body>
    <div data-hf-id="hf-root" id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920" data-fps="30">
      <!-- A-roll: cut, slowed and frozen by tools/build_aroll.py; live grade on the video, print grade on the freezes -->
      <div data-hf-id="hf-cam" id="cam-move">
        <video data-hf-id="hf-aroll" id="aroll" class="clip" src="assets/aroll.mp4" data-start="0" data-duration="{TOTAL}" data-track-index="1" muted playsinline
          data-color-grading="{attr(LIVE)}"></video>
{prints}
      </div>
{rollers}

{comps}
      <div data-hf-id="hf-c-captions" id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{t0("k1-slo")}" data-track-index="4" data-track-kind="captions" data-width="1080" data-height="1920"></div>
      <div data-hf-id="hf-c-dots" id="dots" data-composition-id="dots" data-composition-src="compositions/dots.html" data-start="0" data-duration="{TOTAL}" data-track-index="5" data-track-kind="graphics" data-width="1080" data-height="1920"></div>

      <!-- voice: coach line (J-cut onto the hook) + the 1x take's own sound; denoised, compressed, speech at about -16 LUFS -->
      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>

      <!-- music bed: Mixkit "Okay" (#780, Mixkit free licence), ducked under the voice -->
      <audio data-hf-id="hf-bgm" id="bgm" class="clip" src="assets/music/okay-780.mp3" data-start="0" data-duration="{TOTAL}" data-media-start="{MUSIC_START}" data-track-index="11" data-volume="1" data-timeline-role="music" data-audio-group="music"
        data-fx-chain="{attr(fx)}" data-automation="{attr(auto)}"></audio>

      <!-- sound design (Mixkit premium SFX, file name = Mixkit id): start = picture beat - file peak -->
{audio_sfx}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      const cam = "#cam-move";
      // punch-ins: [film time, transform-origin, scale]
      {json.dumps([list(v) for v in punch.values()])}.forEach(([t, o, s]) => tl.set(cam, {{ transformOrigin: o, scale: s }}, t));
      // hook strike: a short push on contact
      tl.fromTo(cam, {{ scale: 1.45 }}, {{ scale: 1.5, duration: 0.08, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }}, {round(impact_hook, 3)});
      // key 2 -> key 3: ease back out from the ball as it pops up
      tl.fromTo(cam, {{ scale: 1.6, transformOrigin: "713px 1920px" }}, {{ scale: 1.0, duration: 0.55, ease: "power2.inOut", immediateRender: false }}, {round(t1("k2-out") - 0.55, 3)});
      // CTA: slow settle
      tl.fromTo(cam, {{ scale: 1.0 }}, {{ scale: 1.04, duration: {round(t0("cta-freeze") - t0("cta-hold"), 3)}, ease: "none", immediateRender: false }}, {t0("cta-hold")});
      // print freezes: the blue screen print feeds in top-down behind a pink roller
      {json.dumps([[f"#pw-{k}", f"#rl-{k}", t0(k)] for k in freezes])}.forEach(([p, r, t]) => {{
        tl.fromTo(p, {{ clipPath: "inset(0 0 100% 0)" }}, {{ clipPath: "inset(0 0 0% 0)", duration: 0.24, ease: "power2.inOut" }}, t);
        tl.fromTo(r, {{ y: -30, opacity: 1 }}, {{ y: 1930, duration: 0.24, ease: "power2.inOut" }}, t);
      }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
open("index.html", "w").write(page)
print("index.html written;", len(sfx), "sfx; total", TOTAL)
