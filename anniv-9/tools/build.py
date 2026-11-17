"""Generate index.html for the 9th-anniversary polaroid film. Run: python3 tools/build.py
Edit TEXT / PLACES below to change words."""
import json, os, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS = json.load(open(os.path.join(ROOT, "assets/photos.json")))
PHOTOS.sort(key=lambda p: p["name"].replace("IMG_", ""))

TEXT = {
    "kicker": "anniversary kami yang ke-9",
    "title": "9 tahun",
    "outro_top": "9 tahun bersama",
    "outro_line": ["Terima kasih sebab", "sentiasa ada."],
}
# Only places that are clearly identifiable in the photo (sign or landmark)
PLACES = {
    "IMG_20260201_145142": "Fraser's Hill",
    "IMG_20260907_140856": "Kuala Lumpur",
    "IMG_20260907_172322": "Rembayung, KL",
    "IMG_20261101_115550": "Teluk Intan",
    "IMG_20261101_115611": "Teluk Intan",
}
MONTHS = ["Jan", "Feb", "Mac", "Apr", "Mei", "Jun", "Jul", "Ogos", "Sep", "Okt", "Nov", "Dis"]

INTRO = 4.0
SLOT = 2.0
OUTRO = 6.0
START = INTRO
TOTAL = INTRO + SLOT * len(PHOTOS) + OUTRO
OUT_T = INTRO + SLOT * len(PHOTOS)

def nice_date(d):
    return f"{int(d[6:8])} {MONTHS[int(d[4:6]) - 1]} {d[:4]}"

bg_html, card_html, js, sfx = [], [], [], []
for i, p in enumerate(PHOTOS):
    st = round(START + i * SLOT, 3)
    rot = [-3, 2.5, -2, 3.2][i % 4]
    side = 1 if i % 2 else -1
    # blurred background, crossfading
    bdur = round(min(SLOT + 0.6, TOTAL - st), 3)
    bg_html.append(f'      <img id="bg{i}" class="bg clip" src="assets/bg/{p["name"]}.jpg" alt="" data-start="{st}" data-duration="{bdur}" data-track-index="1" style="z-index:{2 + i}" />')
    js.append(f'  tl.fromTo("#bg{i}", {{opacity:0, scale:1.08}}, {{opacity:1, scale:1.0, duration:0.6, ease:"sine.out"}}, {st});')
    # polaroid card
    cdur = round(min(SLOT * 2 + 0.6, OUT_T + 0.5 - st), 3)
    place = PLACES.get(p["name"])
    date = nice_date(p["date"])
    cap = (f'<div class="place">{place}</div><div class="date">{date}</div>' if place
           else f'<div class="place">{date}</div>')
    cls = "card land" if p["land"] else "card port"
    card_html.append(
        f'      <div id="c{i}" class="{cls} clip" data-start="{st}" data-duration="{cdur}" data-track-index="2" style="z-index:{40 + i}">\n'
        f'        <div class="tape"></div>\n'
        f'        <div class="win"><img id="ci{i}" src="assets/cards/{p["name"]}.jpg" alt="" /></div>\n'
        f'        <div class="cap">{cap}</div>\n'
        f'      </div>')
    js.append(f'  tl.fromTo("#c{i}", {{y:1500, rotation:{rot + 14 * side}, opacity:1}}, {{y:0, rotation:{rot}, duration:0.75, ease:"power3.out"}}, {st});')
    js.append(f'  tl.fromTo("#ci{i}", {{scale:1.0}}, {{scale:1.07, duration:{SLOT * 2}, ease:"none"}}, {st});')
    js.append(f'  tl.to("#c{i}", {{x:{70 * side}, rotation:{rot - 6 * side}, scale:0.9, filter:"brightness(0.72)", duration:0.6, ease:"power2.out"}}, {round(st + SLOT, 3)});')
    js.append(f'  tl.to("#c{i}", {{opacity:0, y:-60, duration:0.5, ease:"sine.in"}}, {round(st + SLOT * 2, 3)});')
    js.append(f'  tl.to("#c{i} .cap", {{opacity:0, duration:0.25, ease:"sine.in"}}, {round(st + SLOT - 0.05, 3)});')
    sfx.append(("paper", st + 0.35, 0.35))

# ---- outro heart of mini polaroids
heart_html = []
n = len(PHOTOS); CX, CY, SC = 540, 700, 17.5
for i, p in enumerate(PHOTOS):
    t = 2 * math.pi * (i + 0.5) / n
    x = 16 * math.sin(t) ** 3
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    px, py = CX + x * SC, CY - y * SC
    rot = [-6, 4, -3, 7, -5][i % 5]
    heart_html.append(f'        <div id="m{i}" class="mini" style="left:{px - 56:.0f}px; top:{py - 66:.0f}px"><img src="assets/cards/{p["name"]}.jpg" alt="" /></div>')
    js.append(f'  tl.fromTo("#m{i}", {{x:{(540 - px) * 0.0:.0f}, y:{900 + 40 * (i % 3)}, rotation:{rot * 4}, opacity:0}}, {{y:0, rotation:{rot}, opacity:1, duration:0.6, ease:"back.out(1.6)"}}, {round(OUT_T + 0.2 + i * 0.07, 3)});')

html = f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>9 Tahun</title>
    <link rel="stylesheet" href="assets/fonts/fonts.local.css" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      :root {{ --wine: #2a1418; --blush: #f3d6d0; --gold: #e8b86b; --paper: #fbf6ee; --ink: #3a2226;
               --serif: "Fraunces", Georgia, serif; --hand: "Caveat", cursive; }}
      /* Safe area (TikTok/Reels/Shorts): x 120..888 above y 840, x 120..780 below; y 288..1248 */
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--wine); }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: var(--wine); }}
      .bg {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      #hook {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: 1; transform-origin: 50% 40%; }}
      #wash {{ position: absolute; inset: 0; z-index: 30; pointer-events: none;
              background: radial-gradient(ellipse 90% 70% at 50% 45%, rgba(42,20,24,0) 40%, rgba(42,20,24,.55) 100%); }}
      #hookscrim {{ position: absolute; inset: 0; z-index: 31; background: linear-gradient(180deg, rgba(42,20,24,.72) 0%, rgba(42,20,24,.45) 20%, rgba(42,20,24,0) 32%); }}
      #title {{ position: absolute; left: 120px; top: 300px; z-index: 60; color: var(--paper); }}
      #title .k {{ font-family: var(--hand); font-weight: 500; font-size: 64px; color: var(--blush); line-height: 1; }}
      #title .t {{ font-family: var(--serif); font-weight: 300; font-size: 150px; line-height: .95; letter-spacing: -.02em; text-shadow: 0 4px 30px rgba(0,0,0,.35); }}
      #title .t em {{ font-style: italic; color: var(--gold); }}

      .card {{ position: absolute; background: var(--paper); padding: 30px 30px 0; border-radius: 6px;
              box-shadow: 0 30px 70px rgba(0,0,0,.5), 0 2px 0 rgba(0,0,0,.08); transform-origin: 50% 40%; }}
      .card.port {{ left: 200px; top: 238px; width: 680px; height: 1007px; }}
      .card.port .win {{ width: 620px; height: 827px; }}
      .card.land {{ left: 160px; top: 420px; width: 760px; height: 705px; }}
      .card.land .win {{ width: 700px; height: 525px; }}
      .win {{ overflow: hidden; background: #ddd; }}
      .win img {{ width: 100%; height: 100%; object-fit: cover; display: block; transform-origin: 50% 45%; }}
      .cap {{ padding: 18px 12px 0 10px; color: var(--ink); }}
      .cap .place {{ font-family: var(--hand); font-weight: 500; font-size: 58px; line-height: 1; }}
      .cap .date {{ font-family: var(--serif); font-style: italic; font-weight: 300; font-size: 30px; margin-top: 6px; color: #7a5a5e; }}
      .tape {{ position: absolute; left: 50%; top: -22px; width: 190px; height: 50px; margin-left: -95px; transform: rotate(-4deg);
              background: rgba(243,214,208,.72); box-shadow: 0 2px 6px rgba(0,0,0,.12); }}

      #outro {{ position: absolute; inset: 0; z-index: 90; background: radial-gradient(ellipse 80% 60% at 50% 45%, #47232a 0%, var(--wine) 75%); }}
      .mini {{ position: absolute; width: 112px; height: 132px; background: var(--paper); padding: 8px 8px 0; border-radius: 3px;
              box-shadow: 0 10px 24px rgba(0,0,0,.45); }}
      .mini img {{ width: 96px; height: 96px; object-fit: cover; display: block; }}
      #o_top {{ position: absolute; left: 120px; right: 192px; top: 300px; text-align: center; z-index: 95; }}
      #o_top .a {{ font-family: var(--serif); font-style: italic; font-weight: 300; font-size: 92px; color: var(--paper); line-height: 1; }}
      #o_bot {{ position: absolute; left: 120px; width: 660px; top: 1090px; text-align: center; z-index: 95; font-family: var(--hand); font-weight: 500;
               font-size: 60px; line-height: 1.02; color: var(--blush); }}
      #heartglow {{ position: absolute; left: 240px; top: 420px; width: 600px; height: 600px; z-index: 91; border-radius: 50%;
                   background: radial-gradient(circle, rgba(232,184,107,.28) 0%, rgba(232,184,107,0) 65%); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920" data-fps="30">
      <img id="hook" class="clip" src="assets/cards/hook.jpg" alt="" data-start="0" data-duration="{INTRO + 0.6}" data-track-index="1" />
      <div id="hookscrim" class="clip" data-start="0" data-duration="{INTRO + 0.3}" data-track-index="3"></div>
      <div id="title" class="clip" data-start="0.3" data-duration="{INTRO - 0.3}" data-track-index="4">
        <div class="k" id="tk">{TEXT['kicker']}</div>
        <div class="t" id="tt"><em>9</em> tahun</div>
      </div>
{chr(10).join(bg_html)}
      <div id="wash" class="clip" data-start="{INTRO}" data-duration="{OUT_T - INTRO}" data-track-index="3"></div>
{chr(10).join(card_html)}
      <div id="outro" class="clip" data-start="{OUT_T}" data-duration="{OUTRO}" data-track-index="5">
        <div id="heartglow"></div>
{chr(10).join(heart_html)}
        <div id="o_top"><div class="a">{TEXT['outro_top']}</div></div>
        <div id="o_bot">{'<br />'.join(TEXT['outro_line'])}</div>
      </div>
      <audio id="music" src="assets/audio/music.m4a" data-start="0" data-duration="{TOTAL}" data-volume="1" data-track-index="8"></audio>
__SFX__
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#hook", {{scale:1.0}}, {{scale:1.08, duration:{INTRO + 0.6}, ease:"none"}}, 0);
      tl.fromTo("#tk", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.9, ease:"power2.out"}}, 0.3);
      tl.fromTo("#tt", {{opacity:0, y:30, filter:"blur(10px)"}}, {{opacity:1, y:0, filter:"blur(0px)", duration:1.2, ease:"power3.out"}}, 0.7);
      tl.to("#title", {{opacity:0, y:-20, duration:0.5, ease:"sine.in"}}, {INTRO - 0.55});
      tl.to("#hook", {{opacity:0, duration:0.6, ease:"sine.inOut"}}, {INTRO});
{chr(10).join(js)}
      tl.fromTo("#outro", {{opacity:0}}, {{opacity:1, duration:0.5, ease:"sine.out"}}, {OUT_T});
      tl.fromTo("#heartglow", {{scale:0.4, opacity:0}}, {{scale:1.15, opacity:1, duration:1.6, ease:"sine.out"}}, {OUT_T + 1.6});
      tl.fromTo("#o_top", {{opacity:0, y:24}}, {{opacity:1, y:0, duration:1.0, ease:"power2.out"}}, {OUT_T + 1.4});
      tl.fromTo("#o_bot", {{opacity:0, y:24}}, {{opacity:1, y:0, duration:1.0, ease:"power2.out"}}, {OUT_T + 2.2});
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
sfx += [("chime", OUT_T + 1.6, 0.45)]
LEN = {"paper": 0.5, "chime": 2.0}
tags = [f'      <audio id="sfx{k:02d}" src="assets/audio/sfx_{n}.m4a" data-start="{round(st, 3)}" data-duration="{LEN[n]}" data-volume="{v}" data-track-index="{9 + k % 2}"></audio>'
        for k, (n, st, v) in enumerate(sfx)]
html = html.replace("__SFX__", "\n".join(tags))
open(os.path.join(ROOT, "index.html"), "w").write(html)
print("ok total", TOTAL, "photos", len(PHOTOS))
