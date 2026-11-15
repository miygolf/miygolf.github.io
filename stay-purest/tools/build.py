"""Generate index.html for "Stay 1 malam di Purest" (room tour + breakfast buffet). Run: python3 tools/build.py
No background music by request: SFX only."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEG = json.load(open(os.path.join(ROOT, "assets/clips/segments.json")))
MAP = json.load(open(os.path.join(ROOT, "assets/map/map.json")))

# ------------------------------------------------------------------ shot list
# kind, id, src, dur, media_start, cls, sticker, section-start whip
shots = []
def add(kind, id_, src, dur, ms=0.0, cls="vid", sticker=None, whip=False):
    shots.append(dict(kind=kind, id=id_, src=src, dur=round(dur, 3), ms=ms, cls=cls, sticker=sticker, whip=whip))

# hook
add("img", "h1", "images/IMG_0264.jpg", 0.5, cls="food")
add("img", "h2", "images/IMG_0261.jpg", 0.5, cls="food")
add("img", "h3", "images/IMG_0262.jpg", 0.5, cls="food")
add("img", "h4", "images/IMG_0264.jpg", 1.5, cls="food")
# arrival
add("vid", "ext", "clips/v_exterior.mp4", 2.5, whip=True)
# 01 BILIK
add("vid", "r_corr", "clips/room/s03_corridor.mp4", 2.0, 1.5, sticker="Koridor ke bilik", whip=True)
add("vid", "r_reveal", "clips/room/s01_reveal.mp4", 2.2, 0.6, sticker="Masuk bilik!")
add("vid", "r_bed", "clips/room/s04_bed.mp4", 1.8, 0.0, sticker="2 katil single")
add("vid", "r_desk", "clips/room/s05_room.mp4", 1.8, 1.0, sticker="Meja + kettle")
add("vid", "r_marble", "clips/room/s06_marble.mp4", 1.8, 0.5, sticker="Bilik air marmar hitam")
add("vid", "r_shower", "clips/room/s07_shower.mp4", 1.5, 0.3, sticker="Rain shower")
add("vid", "r_amen", "clips/room/s09_amenity.mp4", 1.5, 0.5, sticker="Amenities")
add("vid", "r_coffee", "clips/room/s10_coffee.mp4", 1.5, 0.8, sticker="Kopi + teh")
add("vid", "r_wide", "clips/room/s12_wide.mp4", 2.0, 2.0)
# 02 SARAPAN
add("vid", "b_window", "clips/v_window.mp4", SEG["v_window"], whip=True)
add("vid", "b_walk", "clips/v_corridor.mp4", SEG["v_corridor"], sticker="Jalan ke sarapan &rarr;")
add("vid", "b_lift", "clips/v_lift.mp4", 1.77)
add("img", "b_resto", "images/IMG_0265.jpg", 1.5, cls="food", sticker="Restoran hotel", whip=True)
FOOD = [("IMG_0266", "Nasi goreng + telur", "07:58"), ("IMG_0264", "Nasi lemak", "08:05"),
        ("IMG_0261", "Roti jala + kari", "08:14"), ("IMG_0263", "Bubur + buah", "08:24"),
        ("IMG_0260", "Kuih tradisional", "08:25"), ("IMG_0262", "Dim sum + pastri", "08:38")]
for i, (p, lab, _) in enumerate(FOOD):
    add("img", f"b_f{i}", f"images/{p}.jpg", 1.25, cls="food", sticker=lab)

t = 0.0
for s in shots:
    s["start"] = round(t, 3); t += s["dur"]
END = round(t, 3)
END_DUR = 3.6
TOTAL = round(END + END_DUR, 3)
S = {s["id"]: s for s in shots}
ROOM_IN, ROOM_OUT = S["r_corr"]["start"], S["b_window"]["start"]
BF_IN = S["b_window"]["start"]

html_media, js, sfx = [], [], []
for z, s in enumerate(shots, start=1):
    attrs = f'id="{s["id"]}" class="media {s["cls"]} clip" data-start="{s["start"]}" data-duration="{s["dur"]}" data-track-index="1" style="z-index:{z}"'
    if s["kind"] == "img":
        html_media.append(f'      <img {attrs} src="assets/{s["src"]}" alt="" />')
        js.append(f'  tl.fromTo("#{s["id"]}", {{scale:1.18, rotation:{-1.5 if z % 2 else 1.5}}}, {{scale:1.0, rotation:0, duration:{s["dur"]}, ease:"expo.out"}}, {s["start"]});')
    else:
        ms = f' data-media-start="{s["ms"]}"' if s["ms"] else ""
        html_media.append(f'      <video {attrs}{ms} src="assets/{s["src"]}" muted playsinline></video>')
        js.append(f'  tl.fromTo("#{s["id"]}", {{scale:1.1}}, {{scale:1.0, duration:{min(1.2, s["dur"])}, ease:"power3.out"}}, {s["start"]});')
    if s["whip"]:
        prev = shots[z - 2]
        js.append(f'  tl.fromTo("#{s["id"]}", {{x:300, filter:"blur(22px)"}}, {{x:0, filter:"blur(0px)", duration:0.2, ease:"power3.out"}}, {s["start"]});')
        js.append(f'  tl.to("#{prev["id"]}", {{x:-300, filter:"blur(22px)", duration:0.12, ease:"power2.in"}}, {round(s["start"] - 0.12, 3)});')
        sfx.append(("whoosh", s["start"] - 0.12, 0.7))
    elif z > 1 and s["id"] not in ("h2", "h3", "h4"):
        sfx.append(("shutter" if s["cls"] == "food" else "pop", s["start"], 0.45 if s["cls"] != "food" else 0.6))

# stickers
html_st = []
for k, s in enumerate(x for x in shots if x["sticker"]):
    tilt = [-3, 2, -2, 3][k % 4]
    st = round(s["start"] + 0.08, 3); du = round(s["dur"] - 0.08, 3)
    html_st.append(f'      <div id="st_{s["id"]}" class="sticker clip" data-start="{st}" data-duration="{du}" data-track-index="4">{s["sticker"]}</div>')
    js.append(f'  tl.fromTo("#st_{s["id"]}", {{scale:0.4, rotation:{tilt - 10}, opacity:0}}, {{scale:1, rotation:{tilt}, opacity:1, duration:0.32, ease:"back.out(2.2)"}}, {st});')
    sfx.append(("pop", st, 0.5))

# breakfast clock (room footage has no clock: it was filmed after breakfast)
walk = S["b_walk"]
clocks = [("07:52", BF_IN + 0.3), ("07:53", walk["start"] + 1.6), ("07:54", walk["start"] + 3.0), ("07:55", S["b_resto"]["start"])]
clocks += [(c, S[f"b_f{i}"]["start"]) for i, (_, _, c) in enumerate(FOOD)]
html_ck = []
for i, (txt, st) in enumerate(clocks):
    nxt = clocks[i + 1][1] if i + 1 < len(clocks) else END
    du = (S["b_lift"]["start"] - st) if txt == "07:54" else (nxt - st)
    html_ck.append(f'        <span id="ck{i}" class="tm clip" data-start="{round(st, 3)}" data-duration="{round(du, 3)}" data-track-index="5">{txt}</span>')
    js.append(f'  tl.fromTo("#ck{i}", {{y:26, opacity:0}}, {{y:0, opacity:1, duration:0.22, ease:"power3.out"}}, {round(st, 3)});')
    if i in (1, 2):
        sfx.append(("tick", st, 0.5))

# map
def map_svg(sfx_, w):
    h = round(w * MAP["H"] / MAP["W"]); px, py = MAP["pin"]
    return f'''<svg class="mapsvg" viewBox="0 0 {MAP["W"]} {MAP["H"]}" width="{w}" height="{h}">
          <path d="{MAP["others"]}" fill="#185a64"/>
          <path d="{MAP["malaysia"]}" fill="#FFF3E2"/>
          <circle cx="{MAP["kl"][0]}" cy="{MAP["kl"][1]}" r="4" fill="#0E3B43"/>
          <text data-layout-ignore x="{MAP["kl"][0] + 8}" y="{MAP["kl"][1] + 5}" font-family="Space Mono" font-size="15" font-weight="700" fill="#0E3B43">KL</text>
          <circle id="ring{sfx_}" cx="{px}" cy="{py}" r="14" fill="none" stroke="#FF6B2C" stroke-width="4"/>
          <g transform="translate({px} {py})"><g id="pin{sfx_}"><path d="M0 0 C -7 -12 -15 -18 -15 -28 A 15 15 0 1 1 15 -28 C 15 -18 7 -12 0 0 Z" fill="#FF6B2C" stroke="#0E3B43" stroke-width="3"/><circle cx="0" cy="-28" r="5.5" fill="#0E3B43"/></g></g>
        </svg>'''

EXT = S["ext"]["start"]
MAP_IN, PIN = EXT + 0.3, EXT + 0.6
js += [f'  tl.fromTo("#mapA", {{scale:0.5, rotation:-8, opacity:0}}, {{scale:1, rotation:-2, opacity:1, duration:0.4, ease:"back.out(1.8)"}}, {MAP_IN});',
       f'  tl.fromTo("#pinA", {{y:-90, opacity:0}}, {{y:0, opacity:1, duration:0.45, ease:"bounce.out"}}, {PIN});',
       f'  tl.fromTo("#ringA", {{scale:0.2, opacity:1, transformOrigin:"50% 50%"}}, {{scale:3.2, opacity:0, duration:0.9, ease:"power2.out"}}, {PIN + 0.35});',
       f'  tl.fromTo("#capA", {{x:-30, opacity:0}}, {{x:0, opacity:1, duration:0.3, ease:"power3.out"}}, {PIN + 0.3});']
sfx += [("stamp", EXT + 0.2, 1.0), ("pop", MAP_IN, 0.55), ("ping", PIN + 0.3, 0.6)]

# section chips
for cid, st, du in (("sec1", ROOM_IN, ROOM_OUT - ROOM_IN), ("sec2", BF_IN, END - BF_IN)):
    js.append(f'  tl.fromTo("#{cid}", {{x:-80, opacity:0}}, {{x:0, opacity:1, duration:0.3, ease:"power3.out"}}, {st});')

# "esok pagi" bridge on the wide room shot
W = S["r_wide"]
js.append(f'  tl.fromTo("#bridge", {{scale:0.5, rotation:-12, opacity:0}}, {{scale:1, rotation:-4, opacity:1, duration:0.35, ease:"back.out(2.4)"}}, {W["start"] + 0.2});')
sfx.append(("pop", W["start"] + 0.2, 0.55))

LIFT = S["b_lift"]["start"]
sfx += [("ding", LIFT + 0.15, 0.75)]
sfx += [("impact", 0.0, 0.9), ("shutter", 0.5, 0.7), ("shutter", 1.0, 0.7), ("pop", 1.0, 0.55), ("whoosh", 2.86, 0.7)]
sfx += [("whoosh", END - 0.1, 0.75), ("stamp", END + 0.65, 1.0), ("pop", END + 0.95, 0.45), ("pop", END + 1.3, 0.55), ("ping", END + 1.55, 0.5)]

html = f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Stay 1 malam di Purest</title>
    <link rel="stylesheet" href="assets/fonts/fonts.local.css" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      :root {{ --sun: #ff6b2c; --paper: #fff3e2; --teal: #0e3b43; --yolk: #ffd23f;
               --grot: "Bricolage Grotesque", "Inter", sans-serif; --mono: "Space Mono", monospace; }}
      /* Safe area (TikTok/Reels/Shorts): x 120..888 above y 840, x 120..780 below; y 288..1248 */
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--teal); }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: var(--teal); }}
      .media {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform-origin: 50% 50%; }}
      .scrim {{ position: absolute; inset: 0; z-index: 30; pointer-events: none;
               background: linear-gradient(180deg, rgba(8,28,32,.62) 0%, rgba(8,28,32,.30) 24%, rgba(8,28,32,0) 38%); }}
      #hook {{ position: absolute; left: 120px; top: 300px; width: 768px; z-index: 50; }}
      #hook .chip {{ display: inline-block; font-family: var(--mono); font-weight: 700; font-size: 30px; letter-spacing: .06em;
                    background: var(--teal); color: var(--yolk); padding: 10px 18px; border-radius: 10px; }}
      #hook .big {{ font-family: var(--grot); font-weight: 800; font-size: 168px; line-height: .86; color: var(--paper);
                   letter-spacing: -.035em; margin-top: 18px; text-shadow: 0 6px 0 var(--teal), 0 10px 40px rgba(0,0,0,.45); }}
      #hook .big span {{ display: inline-block; }}
      #hook .sub {{ display: inline-block; margin-top: 26px; font-family: var(--grot); font-weight: 800; font-size: 54px; color: var(--teal);
                   background: var(--yolk); padding: 6px 20px 10px; border-radius: 12px; transform: rotate(-2deg); }}
      #stamp {{ position: absolute; left: 120px; top: 330px; z-index: 50; padding: 18px 30px 22px; border: 7px solid var(--sun);
               border-radius: 20px; background: rgba(14,59,67,.88); color: var(--paper); transform-origin: 30% 50%; }}
      #stamp .d {{ font-family: var(--grot); font-weight: 800; font-size: 120px; line-height: .9; letter-spacing: -.03em; }}
      #stamp .dt {{ font-family: var(--mono); font-weight: 700; font-size: 32px; color: var(--yolk); margin-top: 10px; letter-spacing: .06em; }}
      .mapcard {{ position: absolute; z-index: 52; background: var(--teal); border: 6px solid var(--paper); border-radius: 26px; overflow: hidden;
                 box-shadow: 0 18px 50px rgba(0,0,0,.35); }}
      .mapsvg {{ display: block; }}
      #mapA {{ left: 120px; top: 640px; }}
      .cap {{ position: absolute; z-index: 53; font-family: var(--grot); font-weight: 800; color: var(--teal); background: var(--paper);
             border-radius: 14px; padding: 12px 22px 14px; box-shadow: 0 10px 30px rgba(0,0,0,.25); font-size: 46px; }}
      .cap small {{ display: block; font-family: var(--mono); font-weight: 700; font-size: 28px; color: var(--sun); letter-spacing: .06em; }}
      #capA {{ left: 380px; top: 700px; }}
      .sec {{ position: absolute; left: 120px; top: 312px; z-index: 56; font-family: var(--mono); font-weight: 700; font-size: 30px;
             color: var(--teal); background: var(--yolk); padding: 8px 16px; border-radius: 10px; letter-spacing: .06em; }}
      .sticker {{ position: absolute; left: 120px; top: 380px; z-index: 55; max-width: 740px; font-family: var(--grot); font-weight: 800; font-size: 60px;
                 line-height: 1; color: var(--teal); background: var(--paper); padding: 16px 26px 20px; border-radius: 16px;
                 border: 5px solid var(--teal); box-shadow: 8px 8px 0 var(--sun); transform-origin: 0% 50%; }}
      #clock {{ position: absolute; left: 120px; top: 500px; z-index: 55; height: 64px; width: 210px; }}
      #clock .tm {{ position: absolute; left: 0; top: 0; font-family: var(--mono); font-weight: 700; font-size: 40px; color: var(--paper);
                   background: var(--teal); padding: 8px 18px; border-radius: 10px; letter-spacing: .04em; }}
      #ting {{ position: absolute; left: 160px; top: 720px; z-index: 55; font-family: var(--grot); font-weight: 800; font-size: 150px; color: var(--yolk);
              text-shadow: 0 7px 0 var(--sun), 0 12px 40px rgba(0,0,0,.4); transform-origin: 30% 60%; }}
      #bridge {{ position: absolute; left: 150px; top: 600px; z-index: 55; font-family: var(--grot); font-weight: 800; font-size: 110px; line-height: .92;
                color: var(--paper); text-shadow: 0 6px 0 var(--teal), 0 10px 40px rgba(0,0,0,.5); transform-origin: 0 50%; }}
      #bridge span {{ color: var(--yolk); }}
      #endcard {{ position: absolute; inset: 0; z-index: 70; background: var(--teal); }}
      #endcard .e1 {{ position: absolute; left: 120px; top: 330px; font-family: var(--grot); font-weight: 800; font-size: 150px; line-height: .86;
                     color: var(--paper); letter-spacing: -.04em; }}
      #endcard .done {{ position: absolute; left: 150px; top: 610px; font-family: var(--grot); font-weight: 800; font-size: 80px; color: var(--sun);
                       border: 8px solid var(--sun); border-radius: 18px; padding: 6px 26px 12px; transform-origin: 40% 50%; }}
      #endcard .line {{ position: absolute; left: 124px; top: 780px; font-family: var(--mono); font-weight: 700; font-size: 36px; color: var(--yolk); }}
      #endcard .emap {{ position: absolute; left: 124px; top: 860px; opacity: .9; }}
      #endcard .loc {{ position: absolute; left: 350px; top: 940px; font-family: var(--grot); font-weight: 500; font-size: 40px; color: var(--paper); line-height: 1.2; }}
      #endcard .cta {{ position: absolute; left: 124px; top: 1140px; max-width: 650px; font-family: var(--grot); font-weight: 800; font-size: 44px; line-height: 1.05;
                      color: var(--teal); background: var(--yolk); padding: 14px 24px 18px; border-radius: 16px; box-shadow: 8px 8px 0 var(--sun); transform-origin: 0 50%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920" data-fps="30">
{chr(10).join(html_media)}
      <div id="scrimhook" class="scrim clip" data-start="0" data-duration="3" data-track-index="2" style="z-index:31;background:linear-gradient(180deg, rgba(8,28,32,.55) 0%, rgba(8,28,32,.5) 30%, rgba(8,28,32,.25) 42%, rgba(8,28,32,0) 52%)"></div>
      <div id="scrim" class="scrim clip" data-start="0" data-duration="{LIFT}" data-track-index="2"></div>
      <div id="scrim2" class="scrim clip" data-start="{S['b_resto']['start']}" data-duration="{round(END - S['b_resto']['start'], 3)}" data-track-index="2"></div>

      <div id="hook" class="clip" data-start="0" data-duration="3" data-track-index="3">
        <div class="chip">PUREST HOTEL &middot; SUNGAI PETANI</div>
        <div class="big"><span id="hw1">STAY 1</span><br /><span id="hw2">MALAM</span></div>
        <div class="sub" id="hsub">+ breakfast buffet</div>
      </div>

      <div id="stamp" class="clip" data-start="{EXT + 0.05}" data-duration="{round(S['ext']['dur'] - 0.05, 3)}" data-track-index="3">
        <div class="d">1 MALAM</div>
        <div class="dt">PACKAGE + SARAPAN</div>
      </div>
      <div id="mapA" class="mapcard clip" data-start="{MAP_IN}" data-duration="{round(ROOM_IN - MAP_IN, 3)}" data-track-index="3">
        {map_svg("A", 240)}
      </div>
      <div id="capA" class="cap clip" data-start="{round(PIN + 0.3, 3)}" data-duration="{round(ROOM_IN - PIN - 0.3, 3)}" data-track-index="4"><small>LOKASI</small>Sungai Petani,<br />Kedah</div>

      <div id="sec1" class="sec clip" data-start="{ROOM_IN}" data-duration="{round(W['start'] - ROOM_IN, 3)}" data-track-index="6">01 / BILIK</div>
      <div id="sec2" class="sec clip" data-start="{BF_IN}" data-duration="{round(END - BF_IN, 3)}" data-track-index="6">02 / SARAPAN</div>
      <div id="bridge" class="clip" data-start="{round(W['start'] + 0.2, 3)}" data-duration="{round(W['dur'] - 0.2, 3)}" data-track-index="4">Esok pagi&hellip;<br /><span>sarapan!</span></div>
{chr(10).join(html_st)}
      <div id="clock" class="clip" data-start="{clocks[0][1]}" data-duration="{round(END - clocks[0][1], 3)}" data-track-index="5">
{chr(10).join(html_ck)}
      </div>
      <div id="ting" class="clip" data-layout-ignore data-start="{round(LIFT + 0.15, 3)}" data-duration="1.4" data-track-index="4">TING!</div>

      <div id="endcard" class="clip" data-start="{END}" data-duration="{END_DUR}" data-track-index="7">
        <div class="e1">STAY<br />1 MALAM</div>
        <div class="done">SELESAI!</div>
        <div class="line">Bilik + breakfast buffet</div>
        <div class="emap">{map_svg("C", 200)}</div>
        <div class="loc">Purest Hotel<br />Sungai Petani, Kedah</div>
        <div class="cta">Save untuk trip nanti!</div>
      </div>
__SFX__
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
      tl.fromTo("#hook .chip", {{y:-30, opacity:0}}, {{y:0, opacity:1, duration:0.25, ease:"back.out(2)"}}, 0.0);
      tl.fromTo("#hw1", {{scale:1.8, opacity:0}}, {{scale:1, opacity:1, duration:0.3, ease:"expo.out"}}, 0.05);
      tl.fromTo("#hw2", {{scale:1.8, opacity:0}}, {{scale:1, opacity:1, duration:0.3, ease:"expo.out"}}, 0.5);
      tl.fromTo("#hsub", {{x:-60, opacity:0}}, {{x:0, opacity:1, duration:0.35, ease:"back.out(2)"}}, 1.0);
      tl.to("#hook", {{x:-300, filter:"blur(20px)", opacity:0, duration:0.14, ease:"power2.in"}}, 2.86);
      tl.fromTo("#stamp", {{scale:2.4, rotation:-14, opacity:0}}, {{scale:1, rotation:-4, opacity:1, duration:0.22, ease:"power4.in"}}, {EXT + 0.05});
      tl.to("#stamp", {{x:-300, filter:"blur(20px)", opacity:0, duration:0.12, ease:"power2.in"}}, {round(ROOM_IN - 0.12, 3)});
      tl.fromTo("#ting", {{scale:0.2, rotation:-20, opacity:0}}, {{scale:1, rotation:-6, opacity:1, duration:0.3, ease:"back.out(3)"}}, {LIFT + 0.15});
      tl.to("#ting", {{scale:1.15, opacity:0, duration:0.25, ease:"power2.in"}}, {LIFT + 1.3});
      tl.fromTo("#endcard", {{y:1920}}, {{y:0, duration:0.35, ease:"expo.out"}}, {END});
      tl.fromTo("#endcard .e1", {{y:80, opacity:0}}, {{y:0, opacity:1, duration:0.4, ease:"expo.out"}}, {END + 0.1});
      tl.fromTo("#endcard .done", {{scale:2.6, rotation:-16, opacity:0}}, {{scale:1, rotation:-5, opacity:1, duration:0.2, ease:"power4.in"}}, {END + 0.45});
      tl.fromTo("#endcard .line", {{x:-40, opacity:0}}, {{x:0, opacity:1, duration:0.3, ease:"power3.out"}}, {END + 0.75});
      tl.fromTo("#endcard .emap", {{scale:0.6, opacity:0}}, {{scale:1, opacity:0.9, duration:0.4, ease:"back.out(1.8)"}}, {END + 0.95});
      tl.fromTo("#endcard .loc", {{x:-40, opacity:0}}, {{x:0, opacity:1, duration:0.3, ease:"power3.out"}}, {END + 0.95});
      tl.fromTo("#pinC", {{y:-90, opacity:0}}, {{y:0, opacity:1, duration:0.45, ease:"bounce.out"}}, {END + 1.15});
      tl.fromTo("#ringC", {{scale:0.2, opacity:1, transformOrigin:"50% 50%"}}, {{scale:3.2, opacity:0, duration:0.9, ease:"power2.out"}}, {END + 1.5});
      tl.fromTo("#endcard .cta", {{scale:0.4, rotation:-10, opacity:0}}, {{scale:1, rotation:-2, opacity:1, duration:0.35, ease:"back.out(2.2)"}}, {END + 1.3});
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
LEN = {"impact": 1.4, "shutter": 0.16, "pop": 0.12, "whoosh": 0.42, "stamp": 0.35, "ping": 1.0, "tick": 0.05, "ding": 1.6}
tags = []
for k, (n, st, vol) in enumerate(sorted(sfx, key=lambda x: x[1])):
    st = max(0.0, st)
    tags.append(f'      <audio id="sfx{k:02d}" src="assets/audio/sfx_{n}.m4a" data-start="{round(st, 3)}" data-duration="{round(min(LEN[n], TOTAL - st), 3)}" data-volume="{vol}" data-track-index="{9 + k % 3}"></audio>')
html = html.replace("__SFX__", "\n".join(tags))
open(os.path.join(ROOT, "index.html"), "w").write(html)
print("ok total", TOTAL, "shots", len(shots), "sfx", len(sfx))
for s in shots:
    print(f"  {s['start']:6.2f} {s['dur']:5.2f} {s['id']}")
