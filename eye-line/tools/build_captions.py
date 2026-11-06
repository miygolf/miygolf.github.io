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
 0: ["Nampak","kena!","Kebanyakan","orang","akan","ada","mistake","tu","sebab","dia","buat","benda","yang","salah."],
 1: ["Position","mata","kita","ni,","itu","yang","paling","penting."],
 2: ["Mata,","kalau","boleh,","you","kena","directly","atas","bola."],
 3: ["Macam","mana","kita","nak","buat?","Bila","kita","letak","bola","dekat","tengah-tengah",None,"kaki,","mata","on","top."],
 4: ["Kita","letak","satu","bola","dekat","mata","kiri.","Then","you","jatuhkan."],
 5: ["Kalau","kena,","maksudnya","position","tu","almost","perfect."],
 6: ["Bila","kena,","ini","position","mata","kita","betul."],
 7: ["Then","from","that","position,","kita","ambil","putter,","letak","belakang,","pegang","macam biasa,","bagi selesa,","wrist","jangan","bergerak."],
}
RED = {"mistake", "salah.", "wrist", "bergerak."}
GOLD = {"kena!", "mata", "mata,", "penting.", "directly", "atas", "bola.", "tengah-tengah", "top.", "kiri.", "jatuhkan.", "perfect.", "betul.", "putter,", "bagi selesa,", "kena,"}

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
MAXC = 19
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
        spans.append(f'<span id="cw{gi}_{wi}" class="{cls}">{html.escape(wd["text"])}</span>')
    parts.append(f'      <div id="cg{gi}" class="cap-group"><div class="cap-line">{" ".join(spans)}</div></div>')
    js.append(f'  tl.set("#cg{gi}", {{ opacity: 1, visibility: "visible" }}, {gs:.2f});')
    js.append(f'  tl.fromTo("#cg{gi} .cap-line", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power3.out" }}, {gs:.2f});')
    for wi, wd in enumerate(g):
        t0 = max(wd["start"], gs); t1 = max(wd["end"], t0 + 0.12)
        nxt = g[wi+1]["start"] if wi + 1 < len(g) else ge
        t1 = min(t1, nxt) if nxt > t0 + 0.08 else t0 + 0.08
        hl = "#FF6B57" if 'red' in spans[wi] else "#D4FF3A"
        js.append(f'  tl.fromTo("#cw{gi}_{wi}", {{ backgroundColor: "rgba(212,255,58,0)", color: "#FFFFFF" }}, {{ backgroundColor: "{hl}", color: "#0A0F0D", duration: 0.06, ease: "none" }}, {t0:.2f});')
        rest = '#FF8A7A' if 'red' in spans[wi] else ('#E4FF7A' if 'gold' in spans[wi] else '#FFFFFF')
        js.append(f'  tl.to("#cw{gi}_{wi}", {{ backgroundColor: "rgba(212,255,58,0)", color: "{rest}", duration: 0.08, ease: "none" }}, {t1:.2f});')
    js.append(f'  tl.to("#cg{gi}", {{ opacity: 0, duration: 0.08, ease: "power2.in" }}, {ge - 0.08:.2f});')
    js.append(f'  tl.set("#cg{gi}", {{ opacity: 0, visibility: "hidden" }}, {ge:.2f});')

dur = out_groups[-1][1] + 0.2
doc = f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .cap-group {{ position: absolute; left: 0; width: 1080px; top: 1150px; height: 120px;
      display: flex; align-items: center; justify-content: center; opacity: 0; visibility: hidden; overflow: visible; }}
    .cap-line {{ font-family: "Outfit", sans-serif; font-weight: 800; font-size: 62px; line-height: 1.1;
      text-align: center; max-width: 960px; color: #FFFFFF; letter-spacing: -0.01em;
      text-shadow: 0 3px 14px rgba(0, 0, 0, 0.55), 0 2px 2px rgba(0, 0, 0, 0.6); }}
    .w {{ display: inline-block; padding: 0 12px; border-radius: 16px; }}
    .w.gold {{ color: #E4FF7A; }}
    .w.red {{ color: #FF8A7A; }}
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
