"""Build compositions/captions.html from Whisper word timings + hand-corrected text.

Usage: python3 tools/build_captions.py transcript.json voice16.wav
Word starts that Whisper stretched over a pause are snapped to the first
voiced frame (RMS VAD on the denoised voice track).
"""
import json, sys, wave, numpy as np, html

tr = json.load(open(sys.argv[1]))
w = wave.open(sys.argv[2]); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
hop = 160
db = np.array([20 * np.log10(np.sqrt((a[i*hop:(i+1)*hop] ** 2).mean()) + 1e-9) for i in range(len(a)//hop)])
sm = np.convolve(db, np.ones(5) / 5, mode='same')
voiced = sm > -44

def snap(s, e):
    i0, i1 = int(s * 100), int(e * 100)
    idx = np.nonzero(voiced[i0:i1])[0]
    return round(s + idx[0] / 100, 2) if len(idx) else s

# Corrections per segment: list of replacement tokens aligned by position.
# None = drop the word from captions; a string = shown text.
FIX = {
 0: ["Most","mistake","amateur","buat,","putting","pakai","wrist."],
 1: ["Pasal","dia","malas,","dia","tak","nak","gunakan","semua","tangan","dan","bahu,","pakai","kuasa","dari","contoh","macam","ni."],
 2: ["Tarik","belakang,","terlalu","banyak","wrist","movement."],
 3: ["So,","cara","dia?","Stick","ni","untuk","guide","you","punya","movement","tangan","dan","putter."],
 4: [None,"Straight","back,","straight","through."],
 5: ["Nampak,","wrist","movement","tu","very","little."],
 6: ["Aku","lebih","dominant","dengan","right","hand."],
 7: [None,"Rasa","position","tapak","tangan","tu,","dia","bergerak","ke","arah","target."],
 8: ["Ini","salah,","ini","nak","kipas","hati ke?"],
 9: ["Tangan","tu","tak","bergerak","dekat","position,","tolak","dengan","bergerakkan","tangan","dan","bahu."],
 10: ["Okay,","itu","untuk","aku","lah."],
}
RED = {"wrist", "wrist.", "salah,"}
GOLD = {"malas,", "tangan", "bahu,", "bahu.", "stick", "straight", "little.", "right", "hand.", "target.", "kipas", "hati ke?", "position,", "dominant", "putter."}

words = []
for si, seg in enumerate(tr):
    toks = FIX[si]
    assert len(toks) == len(seg['words']), (si, len(toks), len(seg['words']))
    for t, wd in zip(toks, seg['words']):
        if t is None: continue
        s, e = wd['s'], wd['e']
        if e - s > 0.55: s = snap(s, e)
        words.append({"text": t, "start": round(s, 2), "end": round(e, 2), "seg": si})
# merge "aku" + "lah." -> "akulah."
for i in range(len(words) - 1):
    if words[i]['text'] == 'aku' and words[i+1]['text'] == 'lah.':
        words[i]['text'] = 'akulah.'; words[i]['end'] = words[i+1]['end']; words.pop(i+1); break

# group: greedy fill to ~17 chars / 4 words; break at sentence end, pause >= .15 s,
# or a comma once the line already holds 8+ characters
groups, cur = [], []
MAXC = 17
for wd in words:
    if cur:
        prev = cur[-1]; chars = len(" ".join(x['text'] for x in cur))
        brk = (prev['text'][-1] in '.?' or wd['start'] - prev['end'] >= 0.15 or wd['seg'] != prev['seg']
               or chars + 1 + len(wd['text']) > MAXC or len(cur) >= 4
               or (prev['text'][-1] == ',' and chars >= 6))
        if brk: groups.append(cur); cur = []
    cur.append(wd)
if cur: groups.append(cur)

out_groups = []
for gi, g in enumerate(groups):
    gs = max(g[0]['start'] - 0.05, 0.1)
    ge = g[-1]['end'] + 0.12
    nxt = groups[gi+1][0]['start'] - 0.05 if gi + 1 < len(groups) else None
    if nxt is not None: ge = min(ge, nxt)
    # hold a group across a short gap instead of blinking off
    if nxt is not None and nxt - ge < 0.45: ge = nxt
    out_groups.append((gs, ge, g))

parts, js = [], []
for gi, (gs, ge, g) in enumerate(out_groups):
    spans = []
    for wi, wd in enumerate(g):
        key = wd['text'].lower()
        cls = 'w red' if key in RED else ('w gold' if key in GOLD else 'w')
        spans.append(f'<span id="cw{gi}_{wi}" class="{cls}">{html.escape(wd["text"].rstrip(",."))}</span>')
    parts.append(f'      <div id="cg{gi}" class="cap-group"><div class="cap-line">{" ".join(spans)}</div></div>')
    js.append(f'  tl.set("#cg{gi}", {{ opacity: 1, visibility: "visible" }}, {gs:.2f});')
    js.append(f'  tl.fromTo("#cg{gi} .cap-line", {{ y: 18, scale: 0.94 }}, {{ y: 0, scale: 1, duration: 0.22, ease: "back.out(1.6)" }}, {gs:.2f});')
    for wi, wd in enumerate(g):
        js.append(f'  tl.fromTo("#cw{gi}_{wi}", {{ opacity: 0.55, scale: 1 }}, {{ opacity: 1, scale: 1.08, duration: 0.08, ease: "power2.out" }}, {max(wd["start"], gs):.2f});')
        js.append(f'  tl.to("#cw{gi}_{wi}", {{ scale: 1, duration: 0.14, ease: "power2.out" }}, {max(wd["start"], gs) + 0.1:.2f});')
    js.append(f'  tl.to("#cg{gi}", {{ opacity: 0, duration: 0.08, ease: "power2.in" }}, {ge - 0.08:.2f});')
    js.append(f'  tl.set("#cg{gi}", {{ opacity: 0, visibility: "hidden" }}, {ge:.2f});')

dur = out_groups[-1][1] + 0.2
doc = f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .cap-group {{ position: absolute; left: 0; width: 1080px; top: 1196px; height: 130px;
      display: flex; align-items: center; justify-content: center; opacity: 0; visibility: hidden; overflow: visible; }}
    .cap-line {{ font-family: "Archivo Black", sans-serif; font-size: 64px; line-height: 1.05; text-transform: uppercase;
      letter-spacing: 0.01em; text-align: center; max-width: 940px; color: #FFF6E4;
      -webkit-text-stroke: 12px #0B2E23; paint-order: stroke fill;
      text-shadow: 0 6px 0 rgba(6, 26, 19, 0.55); }}
    .w {{ display: inline-block; transform-origin: 50% 70%; }}
    .w.gold {{ color: #FFC21A; }}
    .w.red {{ color: #FF5A47; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(parts)}
  </div>
  <script>
  const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
  window.__timelines["captions"] = tl;
  </script>
</template>
'''
open('compositions/captions.html', 'w').write(doc)
json.dump([{"start": gs, "end": ge, "text": " ".join(w['text'] for w in g)} for gs, ge, g in out_groups],
          open('captions.groups.json', 'w'), indent=1, ensure_ascii=False)
for gs, ge, g in out_groups: print(f"{gs:6.2f}-{ge:6.2f}  {' '.join(w['text'] for w in g)}")
print('duration', round(dur, 2))
