"""Generate index.html for the Purest Hotel stay film from assets/clips/segments.json.

Edit TEXT below to change the on-screen words, then run:  python3 tools/build.py
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEG = json.load(open(os.path.join(ROOT, "assets/clips/segments.json")))

TEXT = {
    "name": "Purest Hotel",
    "place": "Sungai Petani",
    "year": "2026",
    "memory": ["Satu malam yang tenang,", "terasa seperti di rumah."],
}

XF = 0.6          # crossfade length (s)
PHOTO_DUR = 4.4   # exterior still, Ken Burns
END_DUR = 3.8     # closing card

# Shot order. ("photo",) is the exterior still.
ORDER = ["s01_reveal", "photo", "s03_corridor", "s04_bed", "s05_room", "s06_marble",
         "s07_shower", "s09_amenity", "s10_coffee", "s11_card", "s12_wide"]

# Ken Burns per shot: (scale_from, scale_to, x_from, x_to, y_from, y_to) in px
KB = {
    "s01_reveal":   (1.10, 1.03, 0, 0, 0, 0),
    "photo":        (1.04, 1.16, 0, -20, 40, -30),
    "s03_corridor": (1.04, 1.12, 0, 0, 0, 0),
    "s04_bed":      (1.08, 1.03, 0, 0, 0, 0),
    "s05_room":     (1.04, 1.10, 0, 0, 0, 0),
    "s06_marble":   (1.10, 1.04, 0, 0, -20, 20),
    "s07_shower":   (1.04, 1.10, 0, 0, 0, 0),
    "s08_vanity":   (1.08, 1.03, 0, 0, 0, 0),
    "s09_amenity":  (1.03, 1.09, 0, 0, 0, 0),
    "s10_coffee":   (1.08, 1.03, 0, 0, 0, 0),
    "s11_card":     (1.04, 1.10, 0, 0, 0, 0),
    "s12_wide":     (1.03, 1.10, 0, 0, 0, 0),
}

shots, t = [], 0.0
for i, sid in enumerate(ORDER):
    dur = PHOTO_DUR if sid == "photo" else SEG[sid]["duration"]
    shots.append({"id": sid, "start": round(t, 3), "dur": round(dur, 3)})
    t += dur - XF
end_start = round(t, 3)
TOTAL = round(end_start + END_DUR, 3)

def s(id_):
    return next(x for x in shots if x["id"] == id_)

title_in = s("photo")["start"] + 0.5
title_out = s("photo")["start"] + s("photo")["dur"] - 0.55
mem = s("s12_wide")
mem_in = mem["start"] + 0.7

media_html, tl_js = [], []
for z, sh in enumerate(shots, start=1):
    sid, st, du = sh["id"], sh["start"], sh["dur"]
    if sid == "photo":
        media_html.append(f'      <img id="w_{sid}" class="media clip" src="assets/images/exterior.jpg" alt="Purest Hotel exterior" data-start="{st}" data-duration="{du}" data-track-index="1" style="z-index:{z}" />')
    else:
        media_html.append(f'      <video id="w_{sid}" class="media clip" src="assets/clips/{sid}.mp4" data-start="{st}" data-duration="{du}" data-track-index="1" style="z-index:{z}" muted playsinline></video>')
    a, b, x0, x1, y0, y1 = KB[sid]
    tl_js.append(f'  tl.fromTo("#w_{sid}", {{scale:{a}, x:{x0}, y:{y0}}}, {{scale:{b}, x:{x1}, y:{y1}, duration:{du}, ease:"none"}}, {st});')
    if z > 1:
        tl_js.append(f'  tl.fromTo("#w_{sid}", {{opacity:0}}, {{opacity:1, duration:{XF}, ease:"sine.inOut"}}, {st});')

mem_words = []
for li, line in enumerate(TEXT["memory"]):
    words = "".join(f'<span class="w">{w}</span> ' for w in line.split())
    mem_words.append(f'<span class="line">{words.strip()}</span>')

html = f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Purest Hotel - Kenangan</title>
    <link rel="stylesheet" href="assets/fonts/fonts.local.css" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      :root {{
        --ivory: #f4eee4;
        --sand: #cdbb9f;
        --espresso: #221d18;
        --serif: "Cormorant Garamond", Georgia, serif;
        --sans: "Jost", "Inter", sans-serif;
        /* TikTok / Reels safe area: keep type inside x 120..888, y 288..1248 (x<=780 below y 840) */
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--espresso); }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: var(--espresso); }}
      .shot {{ position: absolute; inset: 0; overflow: hidden; }}
      .media {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform-origin: 50% 50%; }}
      .scrim {{ position: absolute; inset: 0; pointer-events: none; z-index: 40; }}
      #scrim-top, #scrim-bottom {{ opacity: 0; }}
      #scrim-top {{ background: linear-gradient(180deg, rgba(20,16,12,.70) 0%, rgba(20,16,12,.50) 30%, rgba(20,16,12,.22) 44%, rgba(20,16,12,0) 58%); }}
      #scrim-bottom {{ background: linear-gradient(0deg, rgba(20,16,12,.74) 20%, rgba(20,16,12,.52) 34%, rgba(20,16,12,.22) 48%, rgba(20,16,12,0) 62%); }}
      #vignette {{ background: radial-gradient(ellipse 80% 70% at 50% 48%, rgba(0,0,0,0) 55%, rgba(12,9,6,.38) 100%); z-index: 39; }}

      /* Title card */
      #title {{ position: absolute; left: 124px; right: 200px; top: 330px; z-index: 50; color: var(--ivory); }}
      #title .kicker {{ font-family: var(--sans); font-weight: 300; font-size: 30px; letter-spacing: .42em; text-transform: uppercase; color: var(--sand); }}
      #title .name {{ font-family: var(--serif); font-weight: 300; font-size: 150px; line-height: .92; letter-spacing: -.01em; margin-top: 26px; text-shadow: 0 2px 24px rgba(0,0,0,.25); }}
      #title .place {{ font-family: var(--serif); font-style: italic; font-weight: 400; font-size: 66px; margin-top: 18px; text-shadow: 0 2px 18px rgba(0,0,0,.25); }}
      #title .rule {{ width: 240px; height: 1.5px; background: var(--sand); margin-top: 34px; transform-origin: 0 50%; }}

      /* Memory line */
      #memory {{ position: absolute; left: 124px; right: 300px; top: 1040px; z-index: 50; color: var(--ivory); }}
      #memory .rule {{ width: 72px; height: 1.5px; background: var(--sand); margin-bottom: 30px; transform-origin: 0 50%; }}
      #memory .line {{ display: block; font-family: var(--serif); font-style: italic; font-weight: 300; font-size: 60px; line-height: 1.14; text-shadow: 0 2px 20px rgba(0,0,0,.35); }}
      #memory .w {{ display: inline-block; }}

      /* Closing card */
      #endcard {{ position: absolute; inset: 0; z-index: 60; background: var(--ivory); color: var(--espresso);
                  display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding-top: 470px; }}
      #endcard .mark {{ width: 1.5px; height: 90px; background: var(--espresso); opacity: .55; transform-origin: 50% 0; }}
      #endcard .name {{ font-family: var(--serif); font-weight: 300; font-size: 104px; margin-top: 40px; letter-spacing: .01em; }}
      #endcard .meta {{ font-family: var(--sans); font-weight: 300; font-size: 28px; letter-spacing: .42em; text-transform: uppercase; margin-top: 26px; padding-left: .42em; opacity: .75; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920" data-fps="30">
{chr(10).join(media_html)}
      <div id="vignette" class="scrim clip" data-start="0" data-duration="{TOTAL}" data-track-index="2"></div>
      <div id="scrim-top" class="scrim clip" data-start="{round(title_in - 0.5, 3)}" data-duration="{round(title_out - title_in + 1.2, 3)}" data-track-index="3"></div>
      <div id="scrim-bottom" class="scrim clip" data-start="{round(mem['start'], 3)}" data-duration="{round(end_start - mem['start'] + XF, 3)}" data-track-index="3"></div>

      <div id="title" class="clip" data-start="{round(title_in, 3)}" data-duration="{round(title_out - title_in + 0.6, 3)}" data-track-index="4">
        <div class="kicker">{TEXT['year']}</div>
        <div class="name">{TEXT['name'].replace(' ', '<br />', 1)}</div>
        <div class="place">{TEXT['place']}</div>
        <div class="rule"></div>
      </div>

      <div id="memory" class="clip" data-start="{round(mem_in, 3)}" data-duration="{round(end_start - mem_in + XF, 3)}" data-track-index="4">
        <div class="rule"></div>
        {''.join(mem_words)}
      </div>

      <div id="endcard" class="clip" data-start="{end_start}" data-duration="{END_DUR}" data-track-index="5">
        <div class="mark"></div>
        <div class="name">{TEXT['name']}</div>
        <div class="meta">{TEXT['place']} &middot; {TEXT['year']}</div>
      </div>

      <audio id="music" src="assets/audio/music.m4a" data-start="0" data-duration="{TOTAL}" data-volume="1" data-fade-out="2.5" data-track-index="6"></audio>
      <audio id="sfx-title" src="assets/audio/sfx_air.m4a" data-start="{round(title_in - 1.0, 3)}" data-duration="2.2" data-volume="0.55" data-track-index="7"></audio>
      <audio id="sfx-memory" src="assets/audio/sfx_air.m4a" data-start="{round(mem_in - 0.9, 3)}" data-duration="2.2" data-volume="0.45" data-track-index="8"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      // Footage: slow Ken Burns + soft crossfades
{chr(10).join(tl_js)}

      // Title card
      tl.fromTo("#scrim-top", {{opacity:0}}, {{opacity:1, duration:1.0, ease:"sine.out"}}, {title_in - 0.5:.3f});
      tl.fromTo("#title .kicker", {{opacity:0, y:14}}, {{opacity:1, y:0, duration:1.0, ease:"power2.out"}}, {title_in:.3f});
      tl.fromTo("#title .name", {{opacity:0, y:28, filter:"blur(10px)"}}, {{opacity:1, y:0, filter:"blur(0px)", duration:1.4, ease:"power3.out"}}, {title_in + 0.15:.3f});
      tl.fromTo("#title .place", {{opacity:0, y:18}}, {{opacity:1, y:0, duration:1.2, ease:"power2.out"}}, {title_in + 0.55:.3f});
      tl.fromTo("#title .rule", {{scaleX:0}}, {{scaleX:1, duration:1.3, ease:"power2.inOut"}}, {title_in + 0.75:.3f});
      tl.to("#title", {{opacity:0, y:-12, duration:0.6, ease:"sine.in"}}, {title_out:.3f});
      tl.to("#scrim-top", {{opacity:0, duration:0.7, ease:"sine.in"}}, {title_out + 0.1:.3f});

      // Memory line
      tl.fromTo("#scrim-bottom", {{opacity:0}}, {{opacity:1, duration:1.0, ease:"sine.out"}}, {mem['start']:.3f});
      tl.fromTo("#memory .rule", {{scaleX:0}}, {{scaleX:1, duration:0.9, ease:"power2.inOut"}}, {mem_in:.3f});
      tl.fromTo("#memory .w", {{opacity:0, y:16, filter:"blur(8px)"}}, {{opacity:1, y:0, filter:"blur(0px)", duration:0.9, ease:"power2.out", stagger:0.16}}, {mem_in + 0.25:.3f});

      // Closing card
      tl.fromTo("#endcard", {{opacity:0}}, {{opacity:1, duration:{XF + 0.3}, ease:"sine.inOut"}}, {end_start:.3f});
      tl.fromTo("#endcard .mark", {{scaleY:0}}, {{scaleY:1, duration:1.0, ease:"power2.out"}}, {end_start + 0.5:.3f});
      tl.fromTo("#endcard .name", {{opacity:0, y:20, filter:"blur(8px)"}}, {{opacity:1, y:0, filter:"blur(0px)", duration:1.2, ease:"power3.out"}}, {end_start + 0.75:.3f});
      tl.fromTo("#endcard .meta", {{opacity:0}}, {{opacity:0.75, duration:1.0, ease:"sine.out"}}, {end_start + 1.25:.3f});

      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
open(os.path.join(ROOT, "index.html"), "w").write(html)
print("total", TOTAL, "end_start", end_start)
for sh in shots:
    print(f"  {sh['start']:6.2f}  {sh['dur']:5.2f}  {sh['id']}")
