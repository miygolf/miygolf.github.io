"""Generate index.html for "Pagi di Purest" (Hari 1 trip vlog). Run: python3 tools/build.py"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEG = json.load(open(os.path.join(ROOT, "assets/clips/segments.json")))
MAP = json.load(open(os.path.join(ROOT, "assets/map/map.json")))
TOTAL = 26.5
USE_MUSIC = False  # user asked for no background music (SFX only)
FD = 1.25   # seconds per plate
EXT = 12.5 + 6 * FD  # exterior start (20.0)
FOOD = [  # photo, label, clock
    ("IMG_0266", "Nasi goreng + telur", "07:58"),
    ("IMG_0264", "Nasi lemak", "08:05"),
    ("IMG_0261", "Roti jala + kari", "08:14"),
    ("IMG_0263", "Dim sum + pastri", "08:24"),
    ("IMG_0260", "Kuih tradisional", "08:25"),
    ("IMG_0262", "Bubur + buah", "08:38"),
]

MUSIC_TAG = (f'      <audio id="music" src="assets/audio/music.m4a" data-start="0" data-duration="{TOTAL}" data-volume="1" data-track-index="8"></audio>\n' if USE_MUSIC else "")

# ---------------------------------------------------------------- media timeline
media = []  # (id, kind, src, start, dur, cls)
def m(id_, kind, src, start, dur, cls):
    media.append(dict(id=id_, kind=kind, src=src, start=round(start, 3), dur=round(dur, 3), cls=cls))

m("h1", "img", "IMG_0264", 0.0, 0.5, "food")
m("h2", "img", "IMG_0261", 0.5, 0.5, "food")
m("h3", "img", "IMG_0263", 1.0, 0.5, "food")
m("h4", "img", "IMG_0264", 1.5, 1.5, "food")
m("window", "vid", "v_window", 3.0, SEG["v_window"], "vid")
t = 3.0 + SEG["v_window"]
m("corridor", "vid", "v_corridor", t, SEG["v_corridor"], "vid"); t += SEG["v_corridor"]
m("lift", "vid", "v_lift", t, 11.0 - t, "vid")
m("resto", "img", "IMG_0265", 11.0, 1.5, "food")
for i, (p, _, _) in enumerate(FOOD):
    m(f"f{i}", "img", p, 12.5 + i * FD, FD, "food")
m("exterior", "vid", "v_exterior", EXT, 3.0, "vid")
END = EXT + 3.0
WHIPS = {"window", "corridor", "resto", "exterior"}

def S(id_):
    return next(x for x in media if x["id"] == id_)

html_media, js = [], []
for z, x in enumerate(media, start=1):
    if x["kind"] == "img":
        html_media.append(f'      <img id="{x["id"]}" class="media {x["cls"]} clip" src="assets/images/{x["src"]}.jpg" alt="" data-start="{x["start"]}" data-duration="{x["dur"]}" data-track-index="1" style="z-index:{z}" />')
        js.append(f'  tl.fromTo("#{x["id"]}", {{scale:1.18, rotation:{-1.5 if z % 2 else 1.5}}}, {{scale:1.0, rotation:0, duration:{x["dur"]}, ease:"expo.out"}}, {x["start"]});')
    else:
        html_media.append(f'      <video id="{x["id"]}" class="media {x["cls"]} clip" src="assets/clips/{x["src"]}.mp4" data-start="{x["start"]}" data-duration="{x["dur"]}" data-track-index="1" style="z-index:{z}" muted playsinline></video>')
        js.append(f'  tl.fromTo("#{x["id"]}", {{scale:1.08}}, {{scale:1.0, duration:{min(1.2, x["dur"])}, ease:"power3.out"}}, {x["start"]});')
    if x["id"] in WHIPS:
        js.append(f'  tl.fromTo("#{x["id"]}", {{x:300, filter:"blur(22px)"}}, {{x:0, filter:"blur(0px)", duration:0.2, ease:"power3.out"}}, {x["start"]});')
        prev = media[z - 2]
        js.append(f'  tl.to("#{prev["id"]}", {{x:-300, filter:"blur(22px)", duration:0.12, ease:"power2.in"}}, {round(x["start"] - 0.12, 3)});')

# ---------------------------------------------------------------- stickers + clock
stickers = [("st_walk", "Jalan ke sarapan &rarr;", S("corridor")["start"] + 0.15, S("corridor")["dur"] - 0.15),
            ("st_resto", "Restoran hotel", 11.06, 1.44)]
for i, (p, label, clk) in enumerate(FOOD):
    stickers.append((f"st_f{i}", label, 12.56 + i * FD, FD - 0.06))
stickers.append(("st_ext", "Purest Hotel", EXT + 0.15, 2.85))
html_st = []
for k, (sid, label, st, du) in enumerate(stickers):
    tilt = [-3, 2, -2, 3][k % 4]
    html_st.append(f'      <div id="{sid}" class="sticker clip" data-start="{round(st, 3)}" data-duration="{round(du, 3)}" data-track-index="4" style="--tilt:{tilt}deg">{label}</div>')
    js.append(f'  tl.fromTo("#{sid}", {{scale:0.4, rotation:{tilt - 10}, opacity:0}}, {{scale:1, rotation:{tilt}, opacity:1, duration:0.32, ease:"back.out(2.2)"}}, {round(st, 3)});')

clocks = [("07:52", S("corridor")["start"] + 0.15), ("07:53", 7.0), ("07:54", 8.4), ("07:55", 11.0)]
clocks += [(clk, 12.5 + i * FD) for i, (_, _, clk) in enumerate(FOOD)] + [("08:57", EXT)]
clock_end = END
html_clock = []
for i, (txt, st) in enumerate(clocks):
    nxt = clocks[i + 1][1] if i + 1 < len(clocks) else clock_end
    if i == 3:  # lift: hide the clock between 07:54 and the restaurant
        pass
    du = (S("lift")["start"] - st) if txt == "07:54" else (nxt - st)
    html_clock.append(f'        <span id="ck{i}" class="tm clip" data-start="{round(st, 3)}" data-duration="{round(du, 3)}" data-track-index="5">{txt}</span>')
    js.append(f'  tl.fromTo("#ck{i}", {{y:26, opacity:0}}, {{y:0, opacity:1, duration:0.22, ease:"power3.out"}}, {round(st, 3)});')

plates = []
for i in range(len(FOOD)):
    plates.append(f'        <span id="pl{i}" class="pl clip" data-start="{12.5 + i}" data-duration="1" data-track-index="6">PINGGAN {i + 1}/{len(FOOD)}</span>')

# ---------------------------------------------------------------- map svg
def map_svg(idsfx, w):
    h = round(w * MAP["H"] / MAP["W"])
    px, py = MAP["pin"]
    return f'''<svg class="mapsvg" viewBox="0 0 {MAP["W"]} {MAP["H"]}" width="{w}" height="{h}">
          <path d="{MAP["others"]}" fill="#185a64"/>
          <path id="land{idsfx}" d="{MAP["malaysia"]}" fill="#FFF3E2"/>
          <circle cx="{MAP["kl"][0]}" cy="{MAP["kl"][1]}" r="4" fill="#0E3B43"/>
          <text x="{MAP["kl"][0] + 8}" y="{MAP["kl"][1] + 5}" data-layout-ignore font-family="Space Mono" font-size="15" font-weight="700" fill="#0E3B43">KL</text>
          <circle id="ring{idsfx}" cx="{px}" cy="{py}" r="14" fill="none" stroke="#FF6B2C" stroke-width="4"/>
          <g transform="translate({px} {py})"><g id="pin{idsfx}"><path d="M0 0 C -7 -12 -15 -18 -15 -28 A 15 15 0 1 1 15 -28 C 15 -18 7 -12 0 0 Z" fill="#FF6B2C" stroke="#0E3B43" stroke-width="3"/><circle cx="0" cy="-28" r="5.5" fill="#0E3B43"/></g></g>
        </svg>'''

MAP1_IN, PIN1 = 3.3, 3.6
MAP2_IN, PIN2 = EXT + 0.35, EXT + 0.6

for sfx, tin, tpin in (("A", MAP1_IN, PIN1), ("B", MAP2_IN, PIN2)):
    js.append(f'  tl.fromTo("#map{sfx}", {{scale:0.5, rotation:-8, opacity:0}}, {{scale:1, rotation:-2, opacity:1, duration:0.4, ease:"back.out(1.8)"}}, {tin});')
    js.append(f'  tl.fromTo("#pin{sfx}", {{y:-90, opacity:0}}, {{y:0, opacity:1, duration:0.45, ease:"bounce.out"}}, {tpin});')
    js.append(f'  tl.fromTo("#ring{sfx}", {{scale:0.2, opacity:1, transformOrigin:"50% 50%"}}, {{scale:3.2, opacity:0, duration:0.9, ease:"power2.out"}}, {tpin + 0.35});')
    js.append(f'  tl.fromTo("#cap{sfx}", {{x:-30, opacity:0}}, {{x:0, opacity:1, duration:0.3, ease:"power3.out"}}, {tpin + 0.3});')

html = f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Pagi di Purest - Hari 1</title>
    <link rel="stylesheet" href="assets/fonts/fonts.local.css" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      :root {{
        --sun: #ff6b2c; --paper: #fff3e2; --teal: #0e3b43; --yolk: #ffd23f;
        --grot: "Bricolage Grotesque", "Inter", sans-serif; --mono: "Space Mono", monospace;
        /* Safe area (TikTok/Reels/Shorts): x 120..888 above y 840, x 120..780 below; y 288..1248 */
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--teal); }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: var(--teal); }}
      .media {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform-origin: 50% 50%; }}
      .scrim {{ position: absolute; inset: 0; z-index: 30; pointer-events: none;
               background: linear-gradient(180deg, rgba(8,28,32,.62) 0%, rgba(8,28,32,.30) 22%, rgba(8,28,32,0) 36%); }}

      /* hook */
      #hook {{ position: absolute; left: 120px; top: 300px; width: 768px; z-index: 50; }}
      #hook .chip {{ display: inline-block; font-family: var(--mono); font-weight: 700; font-size: 30px; letter-spacing: .08em;
                    background: var(--teal); color: var(--yolk); padding: 10px 18px; border-radius: 10px; }}
      #hook .big {{ font-family: var(--grot); font-weight: 800; font-size: 176px; line-height: .86; color: var(--paper);
                   letter-spacing: -.035em; margin-top: 18px; text-shadow: 0 6px 0 var(--teal), 0 10px 40px rgba(0,0,0,.45); }}
      #hook .big span {{ display: inline-block; }}
      #hook .sub {{ display: inline-block; margin-top: 26px; font-family: var(--grot); font-weight: 800; font-size: 54px; color: var(--teal);
                   background: var(--yolk); padding: 6px 20px 10px; border-radius: 12px; transform: rotate(-2deg); }}

      /* day stamp */
      #stamp {{ position: absolute; left: 120px; top: 330px; z-index: 50; padding: 18px 30px 22px; border: 7px solid var(--sun);
               border-radius: 20px; background: rgba(14,59,67,.88); color: var(--paper); transform-origin: 30% 50%; }}
      #stamp .d {{ font-family: var(--grot); font-weight: 800; font-size: 132px; line-height: .9; letter-spacing: -.03em; }}
      #stamp .dt {{ font-family: var(--mono); font-weight: 700; font-size: 32px; color: var(--yolk); margin-top: 10px; letter-spacing: .06em; }}

      /* map cards */
      .mapcard {{ position: absolute; z-index: 52; background: var(--teal); border: 6px solid var(--paper); border-radius: 26px; overflow: hidden;
                 box-shadow: 0 18px 50px rgba(0,0,0,.35); transform-origin: 50% 50%; }}
      .mapsvg {{ display: block; }}
      #mapA {{ left: 120px; top: 640px; }}
      #mapB {{ left: 120px; top: 880px; }}
      .cap {{ position: absolute; z-index: 53; font-family: var(--grot); font-weight: 800; color: var(--teal); background: var(--paper);
             border-radius: 14px; padding: 12px 22px 14px; box-shadow: 0 10px 30px rgba(0,0,0,.25); }}
      .cap small {{ display: block; font-family: var(--mono); font-weight: 700; font-size: 28px; color: var(--sun); letter-spacing: .06em; }}
      #capA {{ left: 380px; top: 700px; font-size: 46px; }}
      #capB {{ left: 330px; top: 960px; font-size: 38px; max-width: 440px; }}

      /* stickers + clock */
      .sticker {{ position: absolute; left: 120px; top: 312px; z-index: 55; max-width: 740px; font-family: var(--grot); font-weight: 800; font-size: 60px;
                 line-height: 1; color: var(--teal); background: var(--paper); padding: 16px 26px 20px; border-radius: 16px;
                 border: 5px solid var(--teal); box-shadow: 8px 8px 0 var(--sun); transform-origin: 0% 50%; }}
      #clock {{ position: absolute; left: 120px; top: 430px; z-index: 55; height: 64px; width: 210px; }}
      #clock .tm {{ position: absolute; left: 0; top: 0; font-family: var(--mono); font-weight: 700; font-size: 40px; color: var(--paper);
                   background: var(--teal); padding: 8px 18px; border-radius: 10px; letter-spacing: .04em; }}
      #plates {{ position: absolute; left: 350px; top: 438px; z-index: 55; }}
      #plates .pl {{ position: absolute; left: 0; top: 0; white-space: nowrap; font-family: var(--mono); font-weight: 700; font-size: 28px; color: var(--teal);
                    background: var(--yolk); padding: 8px 14px; border-radius: 10px; }}
      #ting {{ position: absolute; left: 160px; top: 720px; z-index: 55; font-family: var(--grot); font-weight: 800; font-size: 150px; color: var(--yolk);
              text-shadow: 0 7px 0 var(--sun), 0 12px 40px rgba(0,0,0,.4); transform-origin: 30% 60%; }}

      /* end card */
      #endcard {{ position: absolute; inset: 0; z-index: 70; background: var(--teal); }}
      #endcard .e1 {{ position: absolute; left: 120px; top: 330px; font-family: var(--grot); font-weight: 800; font-size: 168px; line-height: .86;
                     color: var(--paper); letter-spacing: -.04em; }}
      #endcard .done {{ position: absolute; left: 150px; top: 520px; font-family: var(--grot); font-weight: 800; font-size: 84px; color: var(--sun);
                       border: 8px solid var(--sun); border-radius: 18px; padding: 6px 26px 12px; transform-origin: 40% 50%; }}
      #endcard .line {{ position: absolute; left: 124px; top: 700px; font-family: var(--mono); font-weight: 700; font-size: 38px; color: var(--yolk); }}
      #endcard .emap {{ position: absolute; left: 124px; top: 800px; opacity: .9; }}
      #endcard .cta {{ position: absolute; left: 124px; top: 1110px; max-width: 650px; font-family: var(--grot); font-weight: 800; font-size: 44px; line-height: 1.05;
                    color: var(--teal); background: var(--yolk); padding: 14px 24px 18px; border-radius: 16px; box-shadow: 8px 8px 0 var(--sun); transform-origin: 0 50%; }}
      #endcard .cta b {{ color: var(--yolk); background: var(--teal); padding: 0 12px 4px; border-radius: 8px; }}
      #endcard .loc {{ position: absolute; left: 350px; top: 880px; font-family: var(--grot); font-weight: 500; font-size: 40px; color: var(--paper); line-height: 1.2; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920" data-fps="30">
{chr(10).join(html_media)}
      <div id="scrim" class="scrim clip" data-start="0" data-duration="{S('lift')['start']}" data-track-index="2"></div>
      <div id="scrim2" class="scrim clip" data-start="11.0" data-duration="{round(END - 11.0, 3)}" data-track-index="2"></div>

      <div id="hook" class="clip" data-start="0" data-duration="3" data-track-index="3">
        <div class="chip">STAY 1 MALAM + BREAKFAST</div>
        <div class="big"><span id="hw1">BUFFET</span><br /><span id="hw2">PAGI</span></div>
        <div class="sub" id="hsub">ada apa je?</div>
      </div>

      <div id="stamp" class="clip" data-start="3.05" data-duration="2.1" data-track-index="3">
        <div class="d">1 MALAM</div>
        <div class="dt">PACKAGE + SARAPAN</div>
      </div>
      <div id="mapA" class="mapcard clip" data-start="{MAP1_IN}" data-duration="{round(S('corridor')['start'] - MAP1_IN, 3)}" data-track-index="3">
        {map_svg("A", 240)}
      </div>
      <div id="capA" class="cap clip" data-start="{round(PIN1 + 0.3, 3)}" data-duration="{round(S('corridor')['start'] - PIN1 - 0.3, 3)}" data-track-index="4"><small>LOKASI</small>Sungai Petani,<br />Kedah</div>

{chr(10).join(html_st)}
      <div id="clock" class="clip" data-start="{clocks[0][1]}" data-duration="{round(clock_end - clocks[0][1], 3)}" data-track-index="5">
{chr(10).join(html_clock)}
      </div>
      <div id="ting" class="clip" data-layout-ignore data-start="9.42" data-duration="1.4" data-track-index="4">TING!</div>

      <div id="mapB" class="mapcard clip" data-start="{MAP2_IN}" data-duration="{round(END - MAP2_IN, 3)}" data-track-index="3">
        {map_svg("B", 180)}
      </div>
      <div id="capB" class="cap clip" data-start="{round(PIN2 + 0.3, 3)}" data-duration="{round(END - PIN2 - 0.3, 3)}" data-track-index="4">Jalan Indah,<br />Sungai Petani</div>

      <div id="endcard" class="clip" data-start="{END}" data-duration="{round(TOTAL - END, 3)}" data-track-index="7">
        <div class="e1">SARAPAN</div>
        <div class="done">TERMASUK!</div>
        <div class="line">Package 1 malam + breakfast</div>
        <div class="loc">Purest Hotel<br />Sungai Petani, Kedah</div>
        <div class="emap">{map_svg("C", 200)}</div>
        <div class="cta">Nak tengok bilik dia? Komen <b>BILIK</b></div>
      </div>

{MUSIC_TAG}__SFX__
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}

      // hook
      tl.fromTo("#hook .chip", {{y:-30, opacity:0}}, {{y:0, opacity:1, duration:0.25, ease:"back.out(2)"}}, 0.0);
      tl.fromTo("#hw1", {{scale:1.8, opacity:0}}, {{scale:1, opacity:1, duration:0.3, ease:"expo.out"}}, 0.05);
      tl.fromTo("#hw2", {{scale:1.8, opacity:0}}, {{scale:1, opacity:1, duration:0.3, ease:"expo.out"}}, 0.5);
      tl.fromTo("#hsub", {{x:-60, opacity:0}}, {{x:0, opacity:1, duration:0.35, ease:"back.out(2)"}}, 1.0);
      tl.to("#hook", {{x:-300, filter:"blur(20px)", opacity:0, duration:0.14, ease:"power2.in"}}, 2.86);

      // day stamp
      tl.fromTo("#stamp", {{scale:2.4, rotation:-14, opacity:0}}, {{scale:1, rotation:-4, opacity:1, duration:0.22, ease:"power4.in"}}, 3.05);
      tl.fromTo("#stamp", {{y:0}}, {{y:6, duration:0.08, yoyo:true, repeat:1, ease:"sine.inOut"}}, 3.27);

      // lift TING
      tl.fromTo("#ting", {{scale:0.2, rotation:-20, opacity:0}}, {{scale:1, rotation:-6, opacity:1, duration:0.3, ease:"back.out(3)"}}, 9.42);
      tl.to("#ting", {{scale:1.15, opacity:0, duration:0.25, ease:"power2.in"}}, 10.55);

      // end card
      tl.fromTo("#endcard", {{y:1920}}, {{y:0, duration:0.35, ease:"expo.out"}}, {END});
      tl.fromTo("#endcard .e1", {{y:80, opacity:0}}, {{y:0, opacity:1, duration:0.4, ease:"expo.out"}}, {END + 0.1});
      tl.fromTo("#endcard .done", {{scale:2.6, rotation:-16, opacity:0}}, {{scale:1, rotation:-5, opacity:1, duration:0.2, ease:"power4.in"}}, {END + 0.45});
      tl.fromTo("#endcard .line", {{x:-40, opacity:0}}, {{x:0, opacity:1, duration:0.3, ease:"power3.out"}}, {END + 0.75});
      tl.fromTo("#endcard .loc", {{x:-40, opacity:0}}, {{x:0, opacity:1, duration:0.3, ease:"power3.out"}}, {END + 0.95});
      tl.fromTo("#endcard .cta", {{scale:0.4, rotation:-10, opacity:0}}, {{scale:1, rotation:-2, opacity:1, duration:0.35, ease:"back.out(2.2)"}}, {END + 1.25});
      tl.fromTo("#endcard .emap", {{scale:0.6, opacity:0}}, {{scale:1, opacity:0.9, duration:0.4, ease:"back.out(1.8)"}}, {END + 0.95});
      tl.fromTo("#pinC", {{y:-90, opacity:0}}, {{y:0, opacity:1, duration:0.45, ease:"bounce.out"}}, {END + 1.15});
      tl.fromTo("#ringC", {{scale:0.2, opacity:1, transformOrigin:"50% 50%"}}, {{scale:3.2, opacity:0, duration:0.9, ease:"power2.out"}}, {END + 1.5});

      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""

# ---------------------------------------------------------------- SFX cue sheet
SFX = []  # (name, time, volume)
SFX += [("impact", 0.0, 0.9), ("shutter", 0.5, 0.7), ("shutter", 1.0, 0.7), ("pop", 1.0, 0.55), ("whoosh", 2.86, 0.7)]
SFX += [("stamp", 3.25, 1.0), ("pop", MAP1_IN, 0.6), ("ping", PIN1 + 0.3, 0.6), ("pop", PIN1 + 0.3, 0.4)]
SFX += [("whoosh", S("corridor")["start"] - 0.12, 0.7), ("pop", S("corridor")["start"] + 0.15, 0.55), ("tick", 7.0, 0.5), ("tick", 8.4, 0.5)]
SFX += [("ding", 9.38, 0.75), ("whoosh", 10.88, 0.7), ("pop", 11.06, 0.55), ("tick", 11.0, 0.45)]
for i in range(len(FOOD)):
    SFX += [("shutter", 12.5 + i * FD, 0.65), ("pop", 12.56 + i * FD, 0.5)]
SFX += [("whoosh", EXT - 0.12, 0.7), ("pop", EXT + 0.15, 0.55), ("pop", MAP2_IN, 0.5), ("ping", PIN2 + 0.3, 0.5)]
SFX += [("whoosh", END - 0.1, 0.75), ("stamp", END + 0.65, 1.0), ("pop", END + 0.75, 0.45), ("pop", END + 1.25, 0.55), ("ping", END + 1.5, 0.5)]
LEN = {"impact": 1.4, "shutter": 0.16, "pop": 0.12, "whoosh": 0.42, "stamp": 0.35, "ping": 1.0, "tick": 0.05, "ding": 1.6}
sfx_html = []
for k, (n, st, vol) in enumerate(sorted(SFX, key=lambda x: x[1])):
    du = round(min(LEN[n], TOTAL - st), 3)
    sfx_html.append(f'      <audio id="sfx{k:02d}" src="assets/audio/sfx_{n}.m4a" data-start="{round(st, 3)}" data-duration="{du}" data-volume="{vol}" data-track-index="{9 + k % 3}"></audio>')
html = html.replace("__SFX__", "\n".join(sfx_html))
open(os.path.join(ROOT, "index.html"), "w").write(html)
print("ok", len(media), "shots", len(SFX), "sfx")
for x in media:
    print(f"  {x['start']:6.2f} {x['dur']:5.2f} {x['id']}")
