#!/usr/bin/env python3
"""Generate the HyperFrames project (index.html + compositions) for the golf POV edit.
Source of truth: edl.py (cuts), this file (overlays/sfx/captions)."""
import sys, json, re, os
sys.path.insert(0, '/home/user/work/edl')
from edl import EDL

PROJ = '/home/user/video-claude/golf-pov'
TOTAL = 90.0
FREEZE_DUR = 0.90

# ---------------------------------------------------------------- timeline
clips = []
t = 0.0
for cid, a, b, o in EDL:
    sp = o.get('speed', 1.0)
    dur = round((b - a) / sp, 3)
    clips.append(dict(id=cid, a=a, b=b, start=round(t, 3), dur=dur, speed=sp, mute=o.get('mute', False)))
    t += dur
    if o.get('freeze_after'):
        clips.append(dict(id='f02', freeze=True, start=round(t, 3), dur=FREEZE_DUR))
        t += FREEZE_DUR
CONTENT_END = round(t, 3)
END_DUR = round(TOTAL - CONTENT_END, 3)
C = {c['id']: c for c in clips}


def at(cid, src_t):
    """output time of a source timestamp inside clip cid"""
    c = C[cid]
    assert c['a'] - 0.01 <= src_t <= c['b'] + 0.01, (cid, src_t)
    return round(c['start'] + (src_t - c['a']) / c['speed'], 3)


def S(cid):
    return C[cid]['start']


def E(cid):
    return round(C[cid]['start'] + C[cid]['dur'], 3)


# ---------------------------------------------------------------- transcript words
TR = json.load(open('/home/user/work/src/transcript.json'))
WORDS = [w for s in TR['segments'] for w in s['words']]


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def word_times(cid, tokens, src_from=None, src_to=None, hook=False):
    """map caption tokens to output times using transcript words inside the clip range."""
    if hook:
        a, b = 722.10, 725.05
        base = lambda st: round(st - a, 3)  # hook voice plays from t=0
    else:
        a, b = C[cid]['a'], C[cid]['b']
        base = lambda st: at(cid, min(max(st, a), b))
    lo = src_from if src_from is not None else a
    hi = src_to if src_to is not None else b
    pool = [w for w in WORDS if lo - 0.05 <= w['s'] <= hi]
    out = []
    j = 0
    for tok in tokens:
        n = norm(tok)
        hit = None
        for k in range(j, min(j + 6, len(pool))):
            pn = norm(pool[k]['w'])
            if pn and (pn == n or (len(n) > 2 and (pn.startswith(n[:3]) or n.startswith(pn[:3])))):
                hit = k
                break
        if hit is not None:
            out.append(base(pool[hit]['s']))
            j = hit + 1
        else:
            out.append(None)
    # interpolate gaps
    known = [(i, v) for i, v in enumerate(out) if v is not None]
    if not known:
        s0 = base(lo)
        return [round(s0 + i * 0.22, 3) for i in range(len(tokens))]
    for i, v in enumerate(out):
        if v is None:
            prev = [(k, x) for k, x in known if k < i]
            nxt = [(k, x) for k, x in known if k > i]
            if prev and nxt:
                (k0, x0), (k1, x1) = prev[-1], nxt[0]
                out[i] = round(x0 + (x1 - x0) * (i - k0) / (k1 - k0), 3)
            elif prev:
                out[i] = round(prev[-1][1] + 0.2 * (i - prev[-1][0]), 3)
            else:
                out[i] = round(nxt[0][1] - 0.2 * (nxt[0][0] - i), 3)
    return out


# caption groups: (clip, text, highlight-words, src_from, src_to)
# '*word' marks the accent word
CAPS = [
    ('hook', 'Bunker ni memang', 722.10, 723.10),
    ('hook', 'most of the time', 723.10, 723.85),
    ('hook', 'you akan *hit *short.', 723.85, 725.05),
    ('c03', 'Aku jalan, ya.', None, None),
    ('c06a', 'First time kau pakai *driver ni?', None, None),
    ('c06b', 'Lain.', None, None),
    ('c06c', '*Berat sikit.', None, None),
    ('c08', 'First ball ni nampak bagaimana?', 148.55, 149.9),
    ('c08', '*Lepas.', 150.2, 150.8),
    ('c08', 'Oh, lepas lah.', 150.9, 152.0),
    ('c09', 'Bola kau okey.', 198.3, 199.2),
    ('c09', 'Bola kau middle *fairway tu.', 199.2, 200.8),
    ('c09', 'Lepas *100.', 200.9, 201.9),
    ('c09', '100 lagi ke green,', 202.0, 203.2),
    ('c09', 'lebih kurang.', 203.2, 203.65),
    ('c10', '*Relax lah. Kau *forcing.', 370.5, 371.7),
    ('c10', 'Relax dulu.', 371.7, 372.5),
    ('c10', 'First few holes ni.', 372.6, 374.3),
    ('c10', 'Dapat *redeem dulu.', 374.4, 375.8),
    ('c13', 'Ambil lah first ball tadi,', 539.5, 540.85),
    ('c13', 'yang masuk *bunker.', 540.85, 541.5),
    ('c14', 'So kita try to do', 715.6, 716.6),
    ('c14', '*normal *pitch,', 716.6, 718.0),
    ('c14', 'but then you kena make sure', 718.0, 720.2),
    ('c14', 'you *accelerate.', 720.2, 721.0),
    ('c15', 'Kita *visualize', 729.15, 729.8),
    ('c15', 'mana nak hantar bola tu.', 729.8, 731.85),
    ('c16', 'We do normal.', 733.3, 734.1),
    ('c16', 'Normal...', 734.1, 734.75),
    ('c17', '*pitch.', 735.4, 735.95),
    ('c18', 'Tak *keluar pula.', None, None),
    ('c20', 'Tak pusing. Kiri.', 852.9, 854.75),
    ('c20', 'Kau habis pukul macam ni.', 854.75, 855.7),
    ('c21', '*Double *bogey,', 861.9, 863.1),
    ('c21', 'easy man.', 863.1, 864.0),
    ('c22', '*Dahsyatnya!', 911.9, 912.6),
    ('c23', 'Such a *good *player.', 915.35, 916.5),
    ('c23', 'So, any tips for', 916.6, 917.4),
    ('c23', '*green *reading, Iqbal?', 917.4, 918.95),
    ('c24', 'Lepas *birdie terus *tergamam.', None, None),
    ('c25', 'Tengok *slope.', 971.35, 972.6),
    ('c25', '*Uphill.', 973.1, 973.7),
    ('c25', '*Downhill.', 973.7, 974.3),
]


def build_caps():
    groups = []
    for i, (cid, text, f, to) in enumerate(CAPS):
        toks = text.split()
        clean = [x.lstrip('*') for x in toks]
        times = word_times(cid if cid != 'hook' else 'c01', clean, f, to, hook=(cid == 'hook'))
        if cid == 'hook':
            g_end = round((to if to else 725.05) - 722.10, 3)
            clip_end = S('c02')
        else:
            src_to = to if to is not None else C[cid]['b']
            g_end = at(cid, min(src_to, C[cid]['b']))
            clip_end = E(cid)
        g_start = round(min(times[0], times[0]) - 0.04, 3)
        groups.append(dict(words=[dict(t=x, w=w, hi=tok.startswith('*')) for x, w, tok in zip(times, clean, toks)],
                           start=max(0.12, g_start), end=g_end, clip_end=clip_end))
    # each group lasts until next group starts (if same clip & close) or its end+0.25 capped by clip end
    for i, g in enumerate(groups):
        nxt = groups[i + 1]['start'] if i + 1 < len(groups) else TOTAL
        g['end'] = round(min(max(g['end'] + 0.25, g['words'][-1]['t'] + 0.45), nxt - 0.02, g['clip_end'] + 0.35), 3)
        g['end'] = round(min(g['end'], nxt - 0.02), 3)
    return groups


CAPGROUPS = build_caps()

# ---------------------------------------------------------------- key moments (output seconds)
M = dict(
    hook_impact=at('c02', 737.12),
    freeze=S('f02'),
    title=S('c03'),
    drive_impact=at('c04', 63.55),
    friend_impact=at('c05', 114.96),
    driver_q=at('c06a', 118.85),
    cart=S('c07'),
    dist100=at('c09', 201.08),
    relax=S('c10'),
    y145=at('c11', 429.8),
    iron_impact=at('c12', 446.47),
    friend2_impact=at('c13', 537.72),
    bunker_start=S('c14'),
    chk1=at('c14', 717.2),
    chk2=at('c14', 720.44),
    chk3=at('c15', 729.36),
    bunker_impact=at('c17', 737.12),
    fail=at('c18', 739.58),
    chip_impact=at('c19', 824.31),
    green_start=S('c20'),
    dbogey=at('c21', 862.01),
    birdie=at('c22', 911.86),
    tip2=at('c25', 971.5),
    selfie=S('c26'),
    endcard=CONTENT_END,
)

if __name__ == '__main__' and '--print' in sys.argv:
    for c in clips:
        print(f"{c['id']:5s} {c['start']:7.3f} -> {c['start']+c['dur']:7.3f}  ({c['dur']:.3f})")
    print('content end', CONTENT_END, 'endcard', END_DUR)
    for k, v in M.items():
        print(f'  {k:16s} {v:7.3f}')
    for g in CAPGROUPS:
        print(f"  cap {g['start']:6.2f}-{g['end']:6.2f} " + ' '.join(f"{w['w']}@{w['t']:.2f}" for w in g['words']))
    sys.exit(0)

# ---------------------------------------------------------------- SFX placement
# (file, peak offset inside file, output time the peak should hit (+1 frame), volume, id)
PK = {'whoosh.mp3': 0.162, 'whoosh-short.mp3': 0.162, 'whoosh-cinematic.mp3': 2.503, 'impact-bass-1.mp3': 0.073,
      'impact-bass-2.mp3': 1.986, 'pop.mp3': 0.12, 'click-soft.mp3': 0.073, 'click.mp3': 0.073,
      'glitch-1.mp3': 0.82, 'glitch-3.mp3': 1.823, 'error.mp3': 0.745, 'sparkle.mp3': 0.027,
      'riser.mp3': 3.472, 'ping.mp3': 0.324, 'applause.mp3': 0.507}
F1 = 1 / 30
DUR = {'whoosh.mp3': 0.575, 'whoosh-short.mp3': 0.575, 'whoosh-cinematic.mp3': 5.544, 'impact-bass-1.mp3': 2.116,
       'impact-bass-2.mp3': 2.592, 'pop.mp3': 0.72, 'click-soft.mp3': 0.366, 'click.mp3': 0.366, 'glitch-1.mp3': 2.638,
       'glitch-3.mp3': 3.096, 'error.mp3': 1.62, 'sparkle.mp3': 1.802, 'riser.mp3': 4.4, 'ping.mp3': 1.32, 'applause.mp3': 6.32}
SFX = [
    ('impact-bass-1.mp3', 0.03, 0.20),             # frame-0 hit under the hook line
    ('impact-bass-2.mp3', M['freeze'], 0.55),      # freeze hit (swell into impact)
    ('glitch-3.mp3', M['freeze'] + 0.10, 0.22),
    ('whoosh-cinematic.mp3', M['title'] + 0.05, 0.42),
    ('click-soft.mp3', M['title'] + 0.55, 0.35),   # HUD on
    ('pop.mp3', M['title'] + 0.85, 0.28),
    ('impact-bass-1.mp3', M['drive_impact'], 0.30),
    ('whoosh-short.mp3', M['drive_impact'] + 0.10, 0.35),
    ('pop.mp3', M['driver_q'] + 0.05, 0.30),
    ('whoosh.mp3', M['cart'] + 0.04, 0.40),
    ('click-soft.mp3', M['cart'] + 0.20, 0.30),
    ('ping.mp3', M['dist100'] + 0.05, 0.22),
    ('pop.mp3', M['relax'] + 0.35, 0.30),
    ('click.mp3', M['y145'] + 0.02, 0.30),
    ('impact-bass-1.mp3', M['iron_impact'], 0.28),
    ('whoosh-cinematic.mp3', M['bunker_start'] + 0.02, 0.36),
    ('pop.mp3', M['chk1'] + 0.05, 0.30),
    ('click.mp3', M['chk2'] + 0.05, 0.30),
    ('pop.mp3', M['chk3'] + 0.05, 0.30),
    ('impact-bass-2.mp3', M['bunker_impact'], 0.40),
    ('error.mp3', M['fail'] + 0.10, 0.36),
    ('glitch-1.mp3', M['fail'] + 0.05, 0.20),
    ('whoosh-short.mp3', M['chip_impact'] + 0.08, 0.30),
    ('whoosh.mp3', M['green_start'] + 0.02, 0.32),
    ('glitch-1.mp3', M['dbogey'] + 0.05, 0.26),
    ('impact-bass-1.mp3', M['dbogey'] + 0.02, 0.30),
    ('riser.mp3', M['birdie'] - 0.05, 0.22),
    ('impact-bass-2.mp3', M['birdie'] + 0.05, 0.45),
    ('sparkle.mp3', M['birdie'] + 0.10, 0.32),
    ('applause.mp3', M['birdie'] + 0.10, 0.30),
    ('pop.mp3', M['tip2'] + 0.05, 0.30),
    ('whoosh-cinematic.mp3', M['endcard'] + 0.02, 0.40),
    ('pop.mp3', M['endcard'] + 0.55, 0.28),
    ('pop.mp3', M['endcard'] + 0.80, 0.26),
    ('pop.mp3', M['endcard'] + 1.05, 0.28),
    ('impact-bass-1.mp3', M['endcard'] + 1.55, 0.26),
]


def sfx_tags():
    out = []
    for i, (f, t_hit, vol) in enumerate(SFX):
        st = round(t_hit + F1 - PK[f], 3)
        mstart = 0.0
        if st < 0:
            mstart, st = -st, 0.0
        if f == 'riser.mp3':  # only the last ~2.4s of the build into the hit
            pass
        out.append(f'      <audio id="sfx-{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{st}"'
                   f' data-duration="{round(DUR[f] - mstart - 0.01, 3)}" data-media-start="{round(mstart,3)}" data-volume="{vol}" data-track-index="{20 + i % 6}"></audio>')
    return '\n'.join(out)


# ---------------------------------------------------------------- music bed lane
def speech_spans():
    spans = []
    for g in CAPGROUPS:
        spans.append((g['start'], g['end']))
    spans.sort()
    merged = []
    for a, b in spans:
        if merged and a - merged[-1][1] < 0.9:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return merged


BGM_START = M['title'] - 0.02
BGM_UP, BGM_DUCK = 0.30, 0.13


def bgm_lane():
    pts = [(0.0, BGM_UP)]
    for a, b in speech_spans():
        a2, b2 = a - BGM_START, b - BGM_START
        if b2 <= 0:
            continue
        a2 = max(a2, 0.0)
        pts += [(round(max(a2 - 0.25, 0), 3), BGM_UP), (round(a2, 3), BGM_DUCK), (round(b2, 3), BGM_DUCK), (round(b2 + 0.35, 3), BGM_UP)]
    # dedupe/sort, keep monotonic
    pts.sort()
    clean = []
    for t_, v in pts:
        if clean and t_ <= clean[-1][0]:
            clean[-1] = (clean[-1][0], min(clean[-1][1], v))
        else:
            clean.append((t_, v))
    # end card: lift a little
    ec = M['endcard'] - BGM_START
    clean = [p for p in clean if p[0] < ec] + [(round(ec, 3), BGM_DUCK), (round(ec + 0.4, 3), 0.42)]
    return json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [{"t": a, "v": v} for a, v in clean]}]})


# ---------------------------------------------------------------- HTML writers
FONTS_CSS = ''


def video_tags():
    out = []
    z = 1
    for c in clips:
        if c.get('freeze'):
            out.append(f'        <img id="f02" class="clip media" src="assets/img/freeze-bunker.jpg" data-start="{c["start"]}" data-duration="{c["dur"]}" data-track-index="0" alt="" />')
            continue
        audio = 'muted' if c['mute'] else 'data-has-audio="true"'
        out.append(f'        <video id="{c["id"]}" class="clip media" src="assets/clips/{c["id"]}.mp4" data-start="{c["start"]}" data-duration="{c["dur"]}" data-track-index="0" playsinline {audio}></video>')
    out.append(f'        <img id="endplate" class="clip media" src="assets/img/endplate.jpg" data-start="{CONTENT_END}" data-duration="{END_DUR}" data-track-index="0" alt="" />')
    return '\n'.join(out)


def host(cid, start, dur, kind='graphics', track=5):
    return (f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" '
            f'data-start="{start}" data-duration="{dur}" data-track-index="{track}" data-track-kind="{kind}" '
            f'data-width="1080" data-height="1920"></div>')


SCENES = [
    # id, start, dur
    ('hook', 0.0, round(M['title'] + 0.05, 3)),
    ('intro', M['title'], round(E('c04') - M['title'], 3)),
    ('driver', S('c05'), round(E('c06c') - S('c05'), 3)),
    ('cart', S('c07'), C['c07']['dur']),
    ('distance', S('c09'), C['c09']['dur']),
    ('relax', S('c10'), C['c10']['dur']),
    ('yardage', S('c11'), round(E('c12') - S('c11'), 3)),
    ('bunker', S('c14'), round(E('c18') + 1.9 - S('c14'), 3)),
    ('bogey', S('c21'), C['c21']['dur']),
    ('birdie', S('c22'), round(E('c24') - S('c22'), 3)),
    ('slope', S('c25'), C['c25']['dur']),
    ('endcard', CONTENT_END, END_DUR),
]

# whip/wipe transitions at section seams (output time of the cut)
WIPES = [M['title'], S('c07'), S('c14'), S('c20'), CONTENT_END]
# camera punches on impacts: (time, strength)
PUNCH = [(M['hook_impact'], 0.07), (M['drive_impact'], 0.06), (M['friend_impact'], 0.04), (M['iron_impact'], 0.06),
         (M['friend2_impact'], 0.035), (M['bunker_impact'], 0.07), (M['chip_impact'], 0.05), (M['birdie'], 0.05)]


def index_html():
    hosts = '\n'.join(host(sid, st, du, track=5 + i % 3) for i, (sid, st, du) in enumerate(SCENES))
    hosts += '\n' + host('hud', M['title'], round(CONTENT_END - M['title'], 3), track=9)
    hosts += '\n' + host('captions', 0.0, TOTAL, kind='captions', track=10)
    wipes = '\n'.join(f'      <div id="wipe-{i}" class="clip wipe" data-start="{round(t_ - 0.17, 3)}" data-duration="0.4" data-track-index="12"></div>' for i, t_ in enumerate(WIPES))
    wipe_js = '\n'.join(
        f'      tl.fromTo("#wipe-{i}", {{ xPercent: -130, skewX: -8 }}, {{ xPercent: 0, skewX: -8, duration: 0.16, ease: "power3.in" }}, {round(t_ - 0.16, 3)});\n'
        f'      tl.to("#wipe-{i}", {{ xPercent: 130, duration: 0.2, ease: "power3.out" }}, {round(t_, 3)});'
        for i, t_ in enumerate(WIPES))
    punch_js = '\n'.join(
        f'      tl.fromTo("#cam", {{ scale: 1 }}, {{ scale: {1 + s:.3f}, duration: 0.06, ease: "power2.out", immediateRender: false }}, {round(t_ + F1, 3)});\n'
        f'      tl.to("#cam", {{ scale: 1, duration: 0.45, ease: "power3.out" }}, {round(t_ + F1 + 0.06, 3)});\n'
        f'      tl.fromTo("#flash", {{ opacity: 0.0 }}, {{ opacity: 0.22, duration: 0.03, immediateRender: false }}, {round(t_ + F1, 3)});\n'
        f'      tl.to("#flash", {{ opacity: 0, duration: 0.22, ease: "power2.out" }}, {round(t_ + F1 + 0.03, 3)});'
        for t_, s in PUNCH)
    fz = M['freeze']
    return f'''<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      :root {{
        --ground: #06120c;
        --ink: #ffffff;
        --lime: #c8ff2e;
        --flag: #ff3b30;
        --night: rgba(6, 18, 12, 0.78);
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }}
      #cam {{ position: absolute; inset: 0; transform-origin: 50% 46%; z-index: 1; }}
      [data-track-kind="graphics"] {{ z-index: 20; }}
      [data-track-kind="captions"] {{ z-index: 30; }}
      .media {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #flash {{ position: absolute; inset: 0; background: #fff; opacity: 0; z-index: 5; pointer-events: none; }}
      .wipe {{ position: absolute; top: -10%; left: -20%; width: 140%; height: 120%; z-index: 40;
              background: linear-gradient(100deg, transparent 0%, transparent 18%, var(--lime) 18.2%, var(--lime) 44%, #0b2a1a 44.2%, #0b2a1a 82%, transparent 82.2%);
              }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
      <div id="cam">
{video_tags()}
      </div>
      <div id="flash"></div>
{wipes}
      <audio id="hook-voice" class="clip" src="assets/audio/hook-voice.wav" data-start="0" data-volume="1" data-track-index="2"></audio>
      <audio id="bgm" class="clip" src="assets/audio/bgm-summer-chill.mp3" data-start="{BGM_START}" data-duration="{round(TOTAL - BGM_START, 3)}" data-media-start="0" data-volume="1" data-fade-in="0.05" data-fade-out="1.6" data-track-index="3"
        data-automation="{bgm_lane().replace(chr(34), '&quot;')}"></audio>
{sfx_tags()}
{hosts}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
{punch_js}
      // freeze-frame push toward the ball
      tl.fromTo("#f02", {{ scale: 1.0 }}, {{ scale: 1.18, duration: {FREEZE_DUR}, ease: "power2.out", transformOrigin: "49% 65%" }}, {fz});
{wipe_js}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''


# ---------------------------------------------------------------- shared scene css
BASE_CSS = '''
      #root { position: absolute; inset: 0; overflow: visible; }
      .fd { font-family: "Archivo Black", sans-serif; }
      .fm { font-family: "JetBrains Mono", monospace; font-weight: 700; }
      .fi { font-family: "Inter", sans-serif; }
      .panel { background: rgba(6, 18, 12, 0.80); border: 2px solid rgba(200, 255, 46, 0.55); border-radius: 22px; }
      .chip { display: inline-flex; align-items: center; gap: 12px; padding: 12px 22px; border-radius: 999px;
              background: rgba(6, 18, 12, 0.82); color: #fff; font-family: "JetBrains Mono", monospace; font-weight: 700;
              font-size: 30px; letter-spacing: 0.04em; border: 2px solid rgba(200,255,46,0.6); }
      .lime { color: #c8ff2e; }
      .red { color: #ff3b30; }
      .shadow { text-shadow: 0 4px 0 rgba(0,0,0,0.35), 0 0 24px rgba(0,0,0,0.35); }
'''


def scene(cid, dur, css, body, js):
    return f'''<template>
  <style>
{BASE_CSS}
{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920" data-duration="{dur}">
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
'''


def rel(name, t_):
    """time relative to scene start"""
    st = {s[0]: s[1] for s in SCENES}
    st['hud'] = M['title']
    return round(t_ - st[name], 3)


SVG_FLAG = '<svg viewBox="0 0 40 56" width="40" height="56"><line x1="6" y1="2" x2="6" y2="54" stroke="#fff" stroke-width="4" stroke-linecap="round"/><path d="M8 4 L36 12 L8 22 Z" fill="#ff3b30"/></svg>'
SVG_CHECK = '<svg viewBox="0 0 24 24" width="34" height="34"><path d="M4 12.5 L9.5 18 L20 6" fill="none" stroke="#06120c" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
SVG_X = '<svg viewBox="0 0 24 24" width="34" height="34"><path d="M6 6 L18 18 M18 6 L6 18" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round"/></svg>'


def write_scenes():
    os.makedirs(f'{PROJ}/compositions', exist_ok=True)
    W = {}

    # ---------------- HOOK: frame-0 label + freeze question
    d = dict(SCENES_D)['hook']
    fz = rel('hook', M['freeze'])
    W['hook'] = scene('hook', d, '''
      #hk-top { position: absolute; left: 0; right: 0; top: 250px; text-align: center; }
      #hk-pov { display: inline-block; padding: 14px 26px; border-radius: 14px; background: #c8ff2e; color: #06120c;
                font-size: 40px; letter-spacing: 0.02em; }
      #hk-title { margin-top: 22px; color: #fff; font-size: 92px; line-height: 0.98; letter-spacing: -0.01em; }
      #hk-q { position: absolute; left: 0; right: 0; top: 420px; text-align: center; }
      #hk-q .l1 { font-size: 150px; line-height: 0.92; color: #fff; }
      #hk-q .l2 { font-size: 150px; line-height: 0.92; color: #c8ff2e; }
      #hk-ring { position: absolute; left: 430px; top: 1150px; width: 200px; height: 200px; border-radius: 50%;
                 border: 8px solid #c8ff2e; box-shadow: 0 0 30px rgba(200,255,46,0.7); }
''', f'''    <div id="hk-top" class="clip" data-start="0" data-duration="{fz}">
      <div id="hk-pov" class="fm">POV · KAU DALAM BUNKER</div>
      <div id="hk-title" class="fd shadow">SATU SWING.<br/>SATU PELUANG.</div>
    </div>
    <div id="hk-q" class="clip fd shadow" data-start="{fz}" data-duration="{round(d - fz, 3)}">
      <div class="l1" id="hk-q1">KELUAR</div><div class="l2" id="hk-q2">KE TAK?</div>
    </div>
    <div id="hk-ring" class="clip" data-start="{fz}" data-duration="{round(d - fz, 3)}"></div>''', f'''
    tl.fromTo("#hk-title", {{ scale: 1.06 }}, {{ scale: 1, duration: 0.5, ease: "expo.out" }}, 0);
    tl.to("#hk-top", {{ opacity: 0, duration: 0.12, ease: "power2.in" }}, {round(fz - 0.12, 3)});
    tl.fromTo("#hk-q1", {{ scale: 1.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.18, ease: "expo.out" }}, {fz});
    tl.fromTo("#hk-q2", {{ scale: 1.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.18, ease: "expo.out" }}, {round(fz + 0.12, 3)});
    tl.fromTo("#hk-ring", {{ scale: 0.3, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(1.6)" }}, {round(fz + 0.04, 3)});''')

    # ---------------- INTRO: title tag + power meter on the drive
    d = dict(SCENES_D)['intro']
    imp = rel('intro', M['drive_impact'])
    W['intro'] = scene('intro', d, '''
      #in-tag { position: absolute; left: 60px; top: 300px; }
      #in-tag .k { display: inline-block; background: #c8ff2e; color: #06120c; font-size: 30px; padding: 10px 18px; border-radius: 10px; }
      #in-tag .t { margin-top: 16px; color: #fff; font-size: 78px; line-height: 1.0; }
      #in-meter { position: absolute; left: 60px; top: 640px; width: 64px; height: 420px; border-radius: 32px; overflow: hidden;
                  background: rgba(6,18,12,0.72); border: 3px solid rgba(255,255,255,0.85); }
      #in-fill { position: absolute; left: 0; right: 0; bottom: 0; height: 100%; transform-origin: 50% 100%;
                 background: linear-gradient(0deg, #c8ff2e 0%, #c8ff2e 62%, #ffcf3a 80%, #ff3b30 100%); }
      #in-mlabel { position: absolute; left: 140px; top: 1000px; color: #fff; font-size: 30px; }
      #in-pow { position: absolute; left: 0; right: 0; top: 520px; text-align: center; font-size: 140px; color: #c8ff2e; }
''', f'''    <div id="in-tag" class="clip" data-start="0.35" data-duration="{round(imp - 1.3, 3)}">
      <div class="k fm">ROUND PAGI · GENG GOLF</div>
      <div class="t fd shadow">POV: KAU<br/>JADI AKU.</div>
    </div>
    <div id="in-meter" class="clip" data-start="{round(imp - 2.4, 3)}" data-duration="{round(d - imp + 2.3, 3)}"><div id="in-fill"></div></div>
    <div id="in-mlabel" class="clip fm shadow" data-start="{round(imp - 2.4, 3)}" data-duration="{round(d - imp + 2.3, 3)}">POWER</div>
    <div id="in-pow" class="clip fd shadow" data-start="{round(imp + 0.05, 3)}" data-duration="{round(d - imp - 0.1, 3)}">TEE OFF!</div>''', f'''
    tl.fromTo("#in-tag .k", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "expo.out" }}, 0.35);
    tl.fromTo("#in-tag .t", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, 0.5);
    tl.to("#in-tag", {{ opacity: 0, x: -40, duration: 0.2, ease: "power3.in" }}, {round(imp - 1.5, 3)});
    tl.fromTo("#in-meter", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "expo.out" }}, {round(imp - 2.4, 3)});
    tl.fromTo("#in-fill", {{ scaleY: 0.04 }}, {{ scaleY: 0.92, duration: 2.2, ease: "power2.in" }}, {round(imp - 2.3, 3)});
    tl.to("#in-fill", {{ scaleY: 1.0, duration: 0.08, ease: "power2.out" }}, {round(imp - 0.08, 3)});
    tl.fromTo("#in-pow", {{ scale: 1.8, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.2, ease: "expo.out" }}, {round(imp + 0.05, 3)});
    tl.to("#in-pow", {{ opacity: 0, y: -30, duration: 0.2, ease: "power2.in" }}, {round(d - 0.3, 3)});
    tl.to(["#in-meter", "#in-mlabel"], {{ opacity: 0, duration: 0.2 }}, {round(d - 0.3, 3)});''')

    # ---------------- DRIVER: chip
    d = dict(SCENES_D)['driver']
    q = rel('driver', M['driver_q'])
    bq = round(at('c06c', 121.92) - S('c05') - 0.04, 3)
    W['driver'] = scene('driver', d, '''
      #dr-chip { position: absolute; left: 60px; top: 330px; }
      #dr-chip .k { font-size: 30px; }
      #dr-big { position: absolute; left: 60px; top: 400px; font-size: 96px; color: #fff; line-height: 1; }
''', f'''    <div id="dr-chip" class="clip" data-start="{round(q - 0.1, 3)}" data-duration="{round(d - q, 3)}"><span class="chip"><span class="lime">NEW</span> DRIVER CHECK</span></div>
    <div id="dr-big" class="clip fd shadow" data-start="{bq}" data-duration="{round(d - bq, 3)}">BERAT<br/><span class="lime">SIKIT.</span></div>''', f'''
    tl.fromTo("#dr-chip", {{ opacity: 0, y: 20, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(1.5)" }}, {round(q - 0.1, 3)});
    tl.fromTo("#dr-big", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.18, ease: "power4.out" }}, {bq});''')

    # ---------------- CART: fast-forward
    d = dict(SCENES_D)['cart']
    lines = '\n'.join(f'      <div class="ln" id="ct-l{i}" style="top:{260 + i * 150}px;left:{(i * 197) % 700}px;width:{260 + (i * 83) % 240}px"></div>' for i in range(8))
    W['cart'] = scene('cart', d, '''
      #ct-chip { position: absolute; left: 60px; top: 330px; }
      #ct-lines { position: absolute; inset: 0; overflow: hidden; }
      .ln { position: absolute; height: 6px; border-radius: 3px; background: rgba(255,255,255,0.55); }
''', f'''    <div id="ct-lines" class="clip" data-start="0" data-duration="{d}">
{lines}
    </div>
    <div id="ct-chip" class="clip" data-start="0.1" data-duration="{round(d - 0.1, 3)}"><span class="chip"><span class="lime">&#9654;&#9654;</span> x2.5 · NEXT SHOT</span></div>''',
        '\n'.join(f'    tl.fromTo("#ct-l{i}", {{ x: 900, opacity: 0.0 }}, {{ x: -1400, opacity: 0.9, duration: {0.5 + (i % 3) * 0.12}, ease: "none" }}, {round(0.05 + (i * 0.27) % 1.6, 3)});' for i in range(8))
        + f'\n    tl.fromTo("#ct-chip", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.25, ease: "expo.out" }}, 0.1);')

    # ---------------- DISTANCE: 100m to green
    d = dict(SCENES_D)['distance']
    t0 = rel('distance', M['dist100'])
    W['distance'] = scene('distance', d, '''
      #ds-box { position: absolute; left: 60px; top: 320px; padding: 26px 34px 26px 30px; display: flex; gap: 22px; align-items: center; }
      #ds-num { font-size: 120px; color: #fff; line-height: 0.9; }
      #ds-unit { font-size: 34px; color: #c8ff2e; }
      #ds-sub { font-size: 28px; color: rgba(255,255,255,0.8); margin-top: 8px; letter-spacing: 0.08em; }
''', f'''    <div id="ds-box" class="clip panel" data-start="{round(t0 - 0.05, 3)}" data-duration="{round(d - t0 + 0.05, 3)}">
      {SVG_FLAG}
      <div><div><span id="ds-num" class="fm">~100</span><span id="ds-unit" class="fm"> M</span></div><div id="ds-sub" class="fm">KE GREEN · LEBIH KURANG</div></div>
    </div>''', f'''
    tl.fromTo("#ds-box", {{ opacity: 0, x: -60 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "expo.out" }}, {round(t0 - 0.05, 3)});
    tl.to("#ds-box", {{ opacity: 0, x: -40, duration: 0.2, ease: "power3.in" }}, {round(d - 0.22, 3)});''')

    # ---------------- RELAX: tip card
    d = dict(SCENES_D)['relax']
    W['relax'] = scene('relax', d, '''
      #rx-card { position: absolute; left: 60px; top: 320px; width: 640px; padding: 28px 32px; }
      #rx-k { display: inline-block; background: #c8ff2e; color: #06120c; font-size: 28px; padding: 8px 14px; border-radius: 8px; }
      #rx-t { margin-top: 18px; color: #fff; font-size: 70px; line-height: 1.0; }
      #rx-s { margin-top: 14px; color: rgba(255,255,255,0.85); font-size: 30px; }
''', f'''    <div id="rx-card" class="clip panel" data-start="0.3" data-duration="{round(d - 0.3, 3)}">
      <div id="rx-k" class="fm">TIP #1 · MENTAL</div>
      <div id="rx-t" class="fd">RELAX.<br/><span class="lime">JANGAN FORCE.</span></div>
      <div id="rx-s" class="fi">First few holes — redeem dulu.</div>
    </div>''', f'''
    tl.fromTo("#rx-card", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "expo.out" }}, 0.3);
    tl.fromTo("#rx-s", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {round(at('c10', 372.65) - S('c10'), 3)});
    tl.to("#rx-card", {{ opacity: 0, y: -20, duration: 0.22, ease: "power3.in" }}, {round(d - 0.25, 3)});''')

    # ---------------- YARDAGE 145 + stroke
    d = dict(SCENES_D)['yardage']
    t0 = rel('yardage', M['y145'])
    imp = rel('yardage', M['iron_impact'])
    W['yardage'] = scene('yardage', d, '''
      #yd-box { position: absolute; left: 0; right: 0; top: 300px; text-align: center; }
      #yd-n { font-size: 230px; line-height: 0.9; color: #fff; }
      #yd-u { display: inline-block; margin-top: 10px; font-size: 34px; color: #06120c; background: #c8ff2e; padding: 8px 16px; border-radius: 10px; letter-spacing: 0.1em; }
      #yd-hit { position: absolute; left: 0; right: 0; top: 560px; text-align: center; font-size: 110px; color: #c8ff2e; }
''', f'''    <div id="yd-box" class="clip" data-start="{round(t0 - 0.05, 3)}" data-duration="{round(imp - t0 - 0.2, 3)}">
      <div id="yd-n" class="fm shadow">145</div><div id="yd-u" class="fm">JARAK KE PIN</div>
    </div>
    <div id="yd-hit" class="clip fd shadow" data-start="{round(imp + 0.05, 3)}" data-duration="{round(d - imp - 0.1, 3)}">STROKE 2</div>''', f'''
    tl.fromTo("#yd-n", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "expo.out" }}, {round(t0 - 0.05, 3)});
    tl.fromTo("#yd-u", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, {round(t0 + 0.12, 3)});
    tl.to("#yd-box", {{ opacity: 0, y: -40, duration: 0.25, ease: "power3.in" }}, {round(imp - 0.5, 3)});
    tl.fromTo("#yd-hit", {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "expo.out" }}, {round(imp + 0.05, 3)});
    tl.to("#yd-hit", {{ opacity: 0, duration: 0.2 }}, {round(d - 0.3, 3)});''')

    # ---------------- BUNKER 101 checklist + fail stamp
    d = dict(SCENES_D)['bunker']
    c1, c2, c3 = rel('bunker', M['chk1']), rel('bunker', M['chk2']), rel('bunker', M['chk3'])
    fl = rel('bunker', M['fail'])
    bi = rel('bunker', M['bunker_impact'])
    items = [('NORMAL PITCH', c1), ('ACCELERATE', c2), ('VISUALIZE', c3)]
    rows = '\n'.join(f'''        <div class="row" id="bk-r{i}"><div class="box" id="bk-b{i}">{SVG_CHECK}</div><span class="fm">{txt}</span></div>''' for i, (txt, _) in enumerate(items))
    W['bunker'] = scene('bunker', d, '''
      #bk-card { position: absolute; left: 60px; top: 300px; width: 600px; padding: 26px 30px; }
      #bk-k { display: inline-block; background: #f2d49b; color: #06120c; font-size: 28px; padding: 8px 14px; border-radius: 8px; }
      #bk-t { margin-top: 14px; color: #fff; font-size: 66px; line-height: 1; }
      .row { display: flex; align-items: center; gap: 18px; margin-top: 18px; color: #fff; font-size: 38px; }
      .box { width: 48px; height: 48px; border-radius: 12px; background: #c8ff2e; display: flex; align-items: center; justify-content: center; }
      #bk-stamp { position: absolute; left: 0; right: 0; top: 330px; text-align: center; }
      #bk-stamp .s { display: inline-block; padding: 26px 40px; border: 10px solid #ff3b30; border-radius: 24px; color: #ff3b30;
                     background: rgba(6,18,12,0.55); font-size: 96px; line-height: 1; transform: rotate(-6deg); }
      #bk-stamp .m { display: block; margin-top: 16px; font-size: 40px; color: #fff; }
''', f'''    <div id="bk-card" class="clip panel" data-start="0.2" data-duration="{round(bi - 0.45, 3)}">
      <div id="bk-k" class="fm">TIP #2 · BUNKER 101</div>
      <div id="bk-t" class="fd">KELUAR DARI<br/><span class="lime">PASIR.</span></div>
{rows}
    </div>
    <div id="bk-stamp" class="clip" data-start="{round(fl - 0.02, 3)}" data-duration="{round(d - fl + 0.02, 3)}">
      <div class="s fd" id="bk-s">TAK KELUAR<span class="m fm">TEORI 3/3 · PRAKTIK 0/1</span></div>
    </div>''', f'''
    tl.fromTo("#bk-card", {{ opacity: 0, x: -60 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "expo.out" }}, 0.2);
''' + '\n'.join(f'''    tl.fromTo("#bk-r{i}", {{ opacity: 0.25 }}, {{ opacity: 1, duration: 0.15 }}, {round(t_, 3)});
    tl.fromTo("#bk-b{i}", {{ scale: 0 }}, {{ scale: 1, duration: 0.3, ease: "back.out(2)" }}, {round(t_, 3)});''' for i, (_, t_) in enumerate(items)) + f'''
    tl.set(["#bk-b0", "#bk-b1", "#bk-b2"], {{ scale: 0 }}, 0);
    tl.set(["#bk-r0", "#bk-r1", "#bk-r2"], {{ opacity: 0.25 }}, 0);
    tl.to("#bk-card", {{ opacity: 0, x: -50, duration: 0.2, ease: "power3.in" }}, {round(bi - 0.55, 3)});
    tl.fromTo("#bk-s", {{ scale: 2.2, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.2, ease: "expo.out" }}, {round(fl, 3)});
    tl.to("#bk-s", {{ opacity: 0, y: -30, duration: 0.2, ease: "power3.in" }}, {round(d - 0.22, 3)});''')

    # ---------------- DOUBLE BOGEY scorecard
    d = dict(SCENES_D)['bogey']
    t0 = rel('bogey', M['dbogey'])
    W['bogey'] = scene('bogey', d, '''
      #bg-card { position: absolute; left: 0; right: 0; top: 330px; display: flex; justify-content: center; }
      #bg-in { display: flex; align-items: stretch; border-radius: 22px; overflow: hidden; border: 3px solid #fff; }
      #bg-in .a { background: rgba(6,18,12,0.85); color: #fff; padding: 22px 30px; font-size: 40px; display: flex; flex-direction: column; justify-content: center; }
      #bg-in .a small { font-size: 28px; color: rgba(255,255,255,0.7); letter-spacing: 0.1em; }
      #bg-in .b { background: #ff3b30; color: #fff; padding: 10px 34px; font-size: 130px; line-height: 1; display: flex; align-items: center; }
''', f'''    <div id="bg-card" class="clip" data-start="{round(t0 - 0.05, 3)}" data-duration="{round(d - t0 + 0.05, 3)}">
      <div id="bg-in"><div class="a fm"><small>SCORECARD</small>DOUBLE<br/>BOGEY</div><div class="b fd" id="bg-n">+2</div></div>
    </div>''', f'''
    tl.fromTo("#bg-in", {{ opacity: 0, y: -60, rotation: -4 }}, {{ opacity: 1, y: 0, rotation: 0, duration: 0.35, ease: "back.out(1.4)" }}, {round(t0 - 0.05, 3)});
    tl.fromTo("#bg-n", {{ scale: 2 }}, {{ scale: 1, duration: 0.25, ease: "expo.out" }}, {round(t0 + 0.25, 3)});''')

    # ---------------- BIRDIE
    d = dict(SCENES_D)['birdie']
    t0 = rel('birdie', M['birdie'])
    import random
    rnd = random.Random(7)
    conf = []
    for i in range(26):
        x = rnd.randint(80, 1000); y = rnd.randint(260, 560); c = rnd.choice(['#c8ff2e', '#ffffff', '#ffcf3a', '#ff3b30'])
        w = rnd.randint(12, 22); h = rnd.randint(22, 38)
        conf.append((i, x, y, c, w, h, rnd.uniform(-260, 260), rnd.uniform(420, 900), rnd.uniform(-540, 540)))
    conf_html = '\n'.join(f'      <div class="cf" id="bd-c{i}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{c}"></div>' for i, x, y, c, w, h, *_ in conf)
    conf_js = '\n'.join(f'    tl.fromTo("#bd-c{i}", {{ opacity: 1, x: 0, y: -120, rotation: 0, scale: 0.4 }}, {{ x: {dx:.0f}, y: {dy:.0f}, rotation: {rot:.0f}, scale: 1, duration: 2.0, ease: "power2.out" }}, {round(t0 + 0.05, 3)});\n    tl.to("#bd-c{i}", {{ opacity: 0, duration: 0.5 }}, {round(t0 + 1.6, 3)});' for i, x, y, c, w, h, dx, dy, rot in conf)
    W['birdie'] = scene('birdie', d, '''
      #bd-wrap { position: absolute; left: 0; right: 0; top: 300px; text-align: center; }
      #bd-word { display: inline-block; font-size: 170px; line-height: 0.9; color: #06120c; background: #c8ff2e; padding: 18px 36px 8px; border-radius: 26px; transform: rotate(-3deg); }
      #bd-sub { margin-top: 26px; font-size: 40px; color: #fff; letter-spacing: 0.08em; }
      #bd-conf { position: absolute; inset: 0; }
      .cf { position: absolute; border-radius: 4px; opacity: 0; }
''', f'''    <div id="bd-conf" class="clip" data-start="{round(t0, 3)}" data-duration="{round(min(2.4, d - t0), 3)}">
{conf_html}
    </div>
    <div id="bd-wrap" class="clip" data-start="{round(t0, 3)}" data-duration="{round(d - t0 - 1.7, 3)}">
      <div id="bd-word" class="fd">BIRDIE</div>
      <div id="bd-sub" class="fm shadow">-1 · BUKAN AKU YANG PUKUL</div>
    </div>''', f'''
    tl.fromTo("#bd-word", {{ scale: 2.4, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.22, ease: "expo.out" }}, {round(t0, 3)});
    tl.fromTo("#bd-sub", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "expo.out" }}, {round(t0 + 0.6, 3)});
    tl.to("#bd-wrap", {{ opacity: 0, y: -30, duration: 0.22, ease: "power3.in" }}, {round(d - t0 - 1.95 + t0, 3)});
{conf_js}''')

    # ---------------- SLOPE tip
    d = dict(SCENES_D)['slope']
    up = round(at('c25', 973.26) - S('c25'), 3)
    dn = round(at('c25', 973.74) - S('c25'), 3)
    W['slope'] = scene('slope', d, '''
      #sl-card { position: absolute; left: 60px; top: 320px; width: 600px; padding: 26px 30px; }
      #sl-k { display: inline-block; background: #c8ff2e; color: #06120c; font-size: 28px; padding: 8px 14px; border-radius: 8px; }
      #sl-t { margin-top: 14px; color: #fff; font-size: 66px; line-height: 1; }
      .ar { display: flex; align-items: center; gap: 16px; margin-top: 16px; font-size: 38px; color: #fff; }
      .ar svg { flex: none; }
''', f'''    <div id="sl-card" class="clip panel" data-start="0.1" data-duration="{round(d - 0.1, 3)}">
      <div id="sl-k" class="fm">TIP #3 · GREEN READING</div>
      <div id="sl-t" class="fd">BACA<br/><span class="lime">SLOPE.</span></div>
      <div class="ar fm" id="sl-up"><svg width="54" height="40" viewBox="0 0 54 40"><path d="M4 34 L50 6 M34 6 L50 6 L46 21" fill="none" stroke="#c8ff2e" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>UPHILL</div>
      <div class="ar fm" id="sl-dn"><svg width="54" height="40" viewBox="0 0 54 40"><path d="M4 6 L50 34 M34 34 L50 34 L46 19" fill="none" stroke="#ff3b30" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>DOWNHILL</div>
    </div>''', f'''
    tl.fromTo("#sl-card", {{ opacity: 0, x: -60 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "expo.out" }}, 0.1);
    tl.fromTo("#sl-up", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.25, ease: "expo.out" }}, {up});
    tl.fromTo("#sl-dn", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.25, ease: "expo.out" }}, {dn});
    tl.to("#sl-card", {{ opacity: 0, duration: 0.15 }}, {round(d - 0.18, 3)});''')

    # ---------------- END CARD recap
    d = dict(SCENES_D)['endcard']
    recap = [('BUNKER', '1', 'tak keluar'), ('DOUBLE BOGEY', '1', 'easy man'), ('BIRDIE', '1', 'bukan aku')]
    rows = '\n'.join(f'''      <div class="rr" id="ec-r{i}"><span class="fm l">{a}</span><span class="fm n">{b}</span><span class="fi c">{c}</span></div>''' for i, (a, b, c) in enumerate(recap))
    W['endcard'] = scene('endcard', d, '''
      #ec-k { position: absolute; left: 60px; top: 300px; display: inline-block; background: #c8ff2e; color: #06120c; font-size: 30px; padding: 10px 16px; border-radius: 10px; }
      #ec-t { position: absolute; left: 60px; top: 380px; color: #fff; font-size: 110px; line-height: 0.95; }
      #ec-card { position: absolute; left: 60px; top: 640px; width: 820px; padding: 18px 30px; }
      .rr { display: flex; align-items: baseline; gap: 22px; padding: 18px 0; border-bottom: 2px solid rgba(255,255,255,0.15); color: #fff; }
      .rr:last-child { border-bottom: none; }
      .rr .l { font-size: 36px; width: 330px; }
      .rr .n { font-size: 54px; color: #c8ff2e; width: 60px; }
      .rr .c { font-size: 32px; color: rgba(255,255,255,0.8); font-style: italic; }
      #ec-cta { position: absolute; left: 60px; top: 1040px; color: #fff; font-size: 44px; }
''', f'''    <div id="ec-k" class="clip fm" data-start="0.25" data-duration="{round(d - 0.25, 3)}">ROUND RECAP</div>
    <div id="ec-t" class="clip fd shadow" data-start="0.3" data-duration="{round(d - 0.3, 3)}">MAIN<br/><span class="lime">LAGI?</span></div>
    <div id="ec-card" class="clip panel" data-start="0.45" data-duration="{round(d - 0.45, 3)}">
{rows}
    </div>
    <div id="ec-cta" class="clip fd shadow" data-start="1.5" data-duration="{round(d - 1.5, 3)}">FOLLOW <span class="lime">&#8594;</span> HOLE SETERUSNYA</div>''', f'''
    tl.fromTo("#ec-k", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "expo.out" }}, 0.25);
    tl.fromTo("#ec-t", {{ opacity: 0, filter: "blur(10px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, 0.3);
    tl.fromTo("#ec-card", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "expo.out" }}, 0.45);
''' + '\n'.join(f'    tl.fromTo("#ec-r{i}", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.25, ease: "expo.out" }}, {round(0.55 + 0.25 * i, 3)});' for i in range(3)) + f'''
    tl.fromTo("#ec-cta", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "expo.out" }}, 1.5);''')

    # ---------------- HUD (persistent): stage tracker + stroke counter
    hud_d = round(CONTENT_END - M['title'], 3)
    stages = [('TEE', M['title']), ('FAIRWAY', S('c07')), ('BUNKER', S('c14')), ('GREEN', S('c20'))]
    strokes = [M['drive_impact'], M['iron_impact'], M['bunker_impact'], M['chip_impact']]
    st_html = '\n'.join(f'        <div class="st" id="hd-s{i}"><span class="dot" id="hd-d{i}"></span><span class="fm">{n}</span></div>' for i, (n, _) in enumerate(stages))
    st_js = []
    for i, (n, t_) in enumerate(stages):
        r = round(t_ - M['title'], 3)
        st_js.append(f'    tl.to("#hd-s{i}", {{ opacity: 1, duration: 0.2 }}, {r});')
        st_js.append(f'    tl.fromTo("#hd-d{i}", {{ scale: 0.6, backgroundColor: "rgba(255,255,255,0.35)" }}, {{ scale: 1, backgroundColor: "#c8ff2e", duration: 0.3, ease: "back.out(2)" }}, {r});')
        if i > 0:
            st_js.append(f'    tl.to("#hd-s{i-1}", {{ opacity: 0.45, duration: 0.2 }}, {r});')
            st_js.append(f'    tl.to("#hd-d{i-1}", {{ backgroundColor: "rgba(255,255,255,0.55)", duration: 0.2 }}, {r});')
    num_html = '\n'.join(f'        <span class="n" id="hd-n{k}">{k}</span>' for k in range(0, 5))
    num_js = []
    for k, t_ in enumerate(strokes, start=1):
        r = round(t_ - M['title'] + F1, 3)
        num_js.append(f'    tl.to("#hd-n{k-1}", {{ yPercent: -100, opacity: 0, duration: 0.18, ease: "power3.in" }}, {r});')
        num_js.append(f'    tl.fromTo("#hd-n{k}", {{ yPercent: 100, opacity: 0 }}, {{ yPercent: 0, opacity: 1, duration: 0.25, ease: "expo.out" }}, {r});')
    W['hud'] = scene('hud', hud_d, '''
      #hd-bar { position: absolute; left: 60px; top: 192px; display: flex; gap: 10px; align-items: center; padding: 10px 18px; border-radius: 999px;
                background: rgba(6,18,12,0.70); border: 2px solid rgba(255,255,255,0.18); }
      .st { display: flex; align-items: center; gap: 6px; color: #fff; font-size: 28px; letter-spacing: 0.06em; opacity: 0.45; margin-right: 8px; }
      .dot { width: 14px; height: 14px; border-radius: 50%; background: rgba(255,255,255,0.35); }
      #hd-str { position: absolute; right: 60px; top: 192px; display: flex; align-items: center; gap: 12px; padding: 10px 18px; border-radius: 999px;
                background: rgba(6,18,12,0.70); border: 2px solid rgba(200,255,46,0.55); color: #fff; font-size: 28px; letter-spacing: 0.06em; }
      #hd-win { position: relative; width: 26px; height: 34px; overflow: hidden; }
      #hd-win .n { position: absolute; left: 0; top: 0; width: 26px; text-align: center; font-size: 30px; line-height: 34px; color: #c8ff2e; opacity: 0; }
''', f'''    <div id="hd-bar" class="clip" data-start="0.5" data-duration="{round(hud_d - 0.5, 3)}">
{st_html}
    </div>
    <div id="hd-str" class="clip fm" data-start="0.7" data-duration="{round(hud_d - 0.7, 3)}">STROKE <div id="hd-win">
{num_html}
      </div></div>''', f'''
    tl.fromTo("#hd-bar", {{ opacity: 0, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "expo.out" }}, 0.5);
    tl.fromTo("#hd-str", {{ opacity: 0, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "expo.out" }}, 0.7);
    tl.set("#hd-n0", {{ opacity: 1 }}, 0.7);
''' + '\n'.join(st_js) + '\n' + '\n'.join(num_js))

    # ---------------- CAPTIONS
    cap_html = []
    cap_js = []
    for gi, g in enumerate(CAPGROUPS):
        words = []
        for wi, w in enumerate(g['words']):
            cls = 'w hi' if w['hi'] else 'w'
            words.append(f'<span class="{cls}" id="cp{gi}-{wi}">{w["w"]}</span>')
        cap_html.append(f'    <div class="grp clip" id="cp{gi}" data-start="{g["start"]}" data-duration="{round(g["end"] - g["start"], 3)}"><div class="line fi">{" ".join(words)}</div></div>')
        for wi, w in enumerate(g['words']):
            tt = round(max(w['t'], g['start']) - 0.02, 3)
            cap_js.append(f'    tl.fromTo("#cp{gi}-{wi}", {{ opacity: 0, y: 14, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.14, ease: "back.out(2)" }}, {tt});')
        cap_js.append(f'    tl.to("#cp{gi} .line", {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, {round(g["end"] - 0.1, 3)});')
    W['captions'] = scene('captions', TOTAL, '''
      .grp { position: absolute; left: 50px; width: 880px; top: 1090px; text-align: center; }
      .line { display: inline; font-weight: 900; font-size: 64px; line-height: 1.12; color: #fff; letter-spacing: -0.01em;
              -webkit-text-stroke: 10px rgba(6,18,12,0.92); paint-order: stroke fill; text-shadow: 0 6px 14px rgba(0,0,0,0.35); }
      .w { display: inline-block; }
      .hi { color: #c8ff2e; }
''', '\n'.join(cap_html), '\n'.join(cap_js))

    for k, v in W.items():
        open(f'{PROJ}/compositions/{k}.html', 'w').write(v)


SCENES_D = [(s[0], s[2]) for s in SCENES]

if __name__ == '__main__':
    write_scenes()
    open(f'{PROJ}/index.html', 'w').write(index_html())
    print('built. total', TOTAL, 'content end', CONTENT_END)
