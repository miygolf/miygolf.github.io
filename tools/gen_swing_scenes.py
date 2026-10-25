"""Writes compositions/before.html and compositions/after.html from one template.

Both scenes share the telemetry layout (chip row, big word, phase progress strip, slow-mo chip,
impact burst); only the copy, colours and the swing timings measured from the footage differ.
"""
import sys, pathlib

TEMPLATE = r'''<template>
  <style>
    #root {
      position: absolute;
      inset: 0;
      overflow: hidden;
      font-family: "JetBrains Mono", monospace;
      color: #f4f1ea;
    }
    #P-scrim {
      position: absolute;
      left: 0;
      top: 0;
      width: 1080px;
      height: 600px;
      background: linear-gradient(180deg, rgba(10, 13, 11, 0.72) 0%, rgba(10, 13, 11, 0.42) 62%, rgba(10, 13, 11, 0) 100%);
    }
    #P-chips {
      position: absolute;
      left: 60px;
      top: 190px;
      width: 960px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 28px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }
    #P-index {
      display: flex;
      align-items: center;
      gap: 14px;
      color: {{ACCENT}};
    }
    .P-sq {
      width: 14px;
      height: 14px;
      background: {{ACCENT}};
    }
    #P-rate {
      padding: 6px 14px;
      border: 2px solid {{ACCENT}};
      color: {{ACCENT}};
      border-radius: 6px;
      opacity: 0;
    }
    #P-word {
      position: absolute;
      left: 52px;
      top: 226px;
      width: 976px;
      font-family: "League Gothic", sans-serif;
      font-size: 230px;
      line-height: 0.9;
      letter-spacing: 0.01em;
      {{WORDSTYLE}}
    }
    #P-phases {
      position: absolute;
      left: 44px;
      top: 446px;
      width: 992px;
      padding: 12px 16px 10px;
      display: flex;
      gap: 12px;
      background: rgba(10, 13, 11, 0.74);
      border-radius: 6px;
    }
    .P-ph {
      flex: 1;
    }
    .P-track {
      position: relative;
      height: 8px;
      background: rgba(244, 241, 234, 0.28);
      overflow: hidden;
    }
    .P-fill {
      position: absolute;
      inset: 0;
      background: {{ACCENT}};
      transform-origin: left center;
    }
    .P-label {
      margin-top: 8px;
      font-size: 28px;
      letter-spacing: 0.04em;
      color: rgba(244, 241, 234, 0.72);
    }
    #P-burst {
      position: absolute;
      left: {{BALLX}}px;
      top: {{BALLY}}px;
      width: 0;
      height: 0;
    }
    .P-ring {
      position: absolute;
      left: -110px;
      top: -110px;
      width: 220px;
      height: 220px;
      border-radius: 50%;
      border: 6px solid {{ACCENT}};
      opacity: 0;
    }
    #P-ring2 {
      border-width: 3px;
      border-color: #f4f1ea;
    }
    #P-tag {
      position: absolute;
      left: {{TAGX}}px;
      top: {{TAGY}}px;
      font-size: 30px;
      letter-spacing: 0.14em;
      color: #0a0d0b;
      background: {{ACCENT}};
      padding: 6px 14px;
      border-radius: 4px;
      opacity: 0;
    }
    #P-flash {
      position: absolute;
      inset: 0;
      background: #ffffff;
      opacity: 0;
    }
    {{FOCUSCSS}}
    #P-wipe {
      position: absolute;
      left: 0;
      top: 0;
      width: 1080px;
      height: 1920px;
      background: #d4ff3a;
    }
  </style>
  <div id="root" data-composition-id="{{ID}}" data-width="1080" data-height="1920">
    <div id="P-scrim"></div>
    <div id="P-chips">
      <div id="P-index"><span class="P-sq"></span><span>{{INDEX}}</span></div>
      <div id="P-rate">{{RATE}} SLOW-MO</div>
    </div>
    <h2 id="P-word">{{WORD}}</h2>
    <div id="P-phases">
      <div class="P-ph"><div class="P-track"><div id="P-f1" class="P-fill"></div></div><div id="P-l1" class="P-label">SETUP</div></div>
      <div class="P-ph"><div class="P-track"><div id="P-f2" class="P-fill"></div></div><div id="P-l2" class="P-label">BACKSWING</div></div>
      <div class="P-ph"><div class="P-track"><div id="P-f3" class="P-fill"></div></div><div id="P-l3" class="P-label">DOWNSWING</div></div>
      <div class="P-ph"><div class="P-track"><div id="P-f4" class="P-fill"></div></div><div id="P-l4" class="P-label">FINISH</div></div>
    </div>
    <div id="P-burst" data-layout-ignore>
      <div id="P-ring1" class="P-ring"></div>
      <div id="P-ring2" class="P-ring"></div>
    </div>
    <div id="P-tag">IMPACT</div>
    <div id="P-flash" data-layout-ignore></div>
    {{FOCUSEL}}
    {{WIPEEL}}
  </div>
  <script>
    const tl = gsap.timeline({ paused: true });
    // Swing phases measured from the footage (seconds, local to this scene)
    const T = { takeaway: {{TAKEAWAY}}, top: {{TOP}}, impact: {{IMPACT}}, finish: {{FINISH}} };
    const SLOW = [{{SLOW0}}, {{SLOW1}}];
    const ON = "{{ACCENT}}";
    const OFF = "rgba(244, 241, 234, 0.72)";

    {{INTRO}}

    // Phase strip: each bar fills over its phase, its label lights while it is current
    const phases = [
      ["#P-f1", "#P-l1", 0, T.takeaway],
      ["#P-f2", "#P-l2", T.takeaway, T.top],
      ["#P-f3", "#P-l3", T.top, T.impact],
      ["#P-f4", "#P-l4", T.impact, T.finish],
    ];
    phases.forEach(([fill, label, a, b]) => {
      tl.fromTo(fill, { scaleX: 0 }, { scaleX: 1, duration: b - a, ease: "none" }, a);
      tl.fromTo(label, { color: OFF }, { color: ON, duration: 0.08, ease: "none" }, a);
    });
    tl.to(["#P-l1", "#P-l2", "#P-l3"], { color: OFF, duration: 0.08, ease: "none", stagger: 0 }, T.finish + 0.01);
    tl.set("#P-l1", { color: OFF }, T.takeaway);
    tl.set("#P-l2", { color: OFF }, T.top);
    tl.set("#P-l3", { color: OFF }, T.impact);

    // Slow-motion window
    tl.fromTo("#P-rate", { opacity: 0, y: -10 }, { opacity: 1, y: 0, duration: 0.2, ease: "power2.out" }, SLOW[0]);
    tl.to("#P-rate", { opacity: 0, duration: 0.15, ease: "power2.in" }, SLOW[1] - 0.15);

    // Impact
    tl.fromTo("#P-flash", { opacity: 0 }, { opacity: {{FLASH}}, duration: 0.04, ease: "none" }, T.impact);
    tl.to("#P-flash", { opacity: 0, duration: 0.22, ease: "power2.out" }, T.impact + 0.04);
    tl.fromTo("#P-ring1", { scale: 0.15, opacity: 1 }, { scale: 1.9, opacity: 0, duration: 0.7, ease: "expo.out" }, T.impact);
    tl.fromTo("#P-ring2", { scale: 0.1, opacity: 0.9 }, { scale: 1.3, opacity: 0, duration: 0.55, ease: "expo.out" }, T.impact + 0.06);
    tl.fromTo("#P-tag", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.18, ease: "back.out(2.5)" }, T.impact + 0.05);
    tl.to("#P-tag", { opacity: 0, duration: 0.2, ease: "power2.in" }, T.impact + 0.9);

    {{FOCUSJS}}

    {{OUTRO}}
    window.__timelines["{{ID}}"] = tl;
  </script>
</template>
'''

def scene(cfg):
    s = TEMPLATE
    s = s.replace("P-", cfg["prefix"] + "-")
    for k, v in cfg["repl"].items():
        s = s.replace("{{" + k + "}}", v.replace("P-", cfg["prefix"] + "-"))
    assert "{{" not in s
    return s

FOCUS_CSS = '''#P-focus {
      position: absolute;
      left: 220px;
      top: 860px;
      width: 290px;
      height: 470px;
      opacity: 0;
    }
    .P-corner {
      position: absolute;
      width: 46px;
      height: 46px;
      border-color: #d4ff3a;
      border-style: solid;
      border-width: 0;
    }
    #P-c1 { left: 0; top: 0; border-left-width: 6px; border-top-width: 6px; }
    #P-c2 { right: 0; top: 0; border-right-width: 6px; border-top-width: 6px; }
    #P-c3 { left: 0; bottom: 0; border-left-width: 6px; border-bottom-width: 6px; }
    #P-c4 { right: 0; bottom: 0; border-right-width: 6px; border-bottom-width: 6px; }
    #P-focus-tag {
      position: absolute;
      left: 220px;
      top: 802px;
      padding: 6px 14px;
      font-size: 30px;
      letter-spacing: 0.1em;
      color: #0a0d0b;
      background: #d4ff3a;
      border-radius: 4px;
      opacity: 0;
    }'''
FOCUS_EL = '''<div id="P-focus" data-layout-ignore>
      <div id="P-c1" class="P-corner"></div><div id="P-c2" class="P-corner"></div>
      <div id="P-c3" class="P-corner"></div><div id="P-c4" class="P-corner"></div>
    </div>
    <div id="P-focus-tag">WEIGHT SHIFT</div>'''
FOCUS_JS = '''// Weight-shift focus on the lower body, from the top of the backswing through the finish
    tl.fromTo("#P-focus", { opacity: 0, scale: 1.15 }, { opacity: 1, scale: 1, duration: 0.25, ease: "expo.out" }, T.top);
    tl.fromTo("#P-focus-tag", { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.22, ease: "power3.out" }, T.top + 0.05);
    tl.fromTo("#P-focus-tag", { scale: 1 }, { scale: 1.12, duration: 0.12, ease: "power2.out", yoyo: true, repeat: 1, transformOrigin: "left center" }, T.impact);
    tl.to(["#P-focus", "#P-focus-tag"], { opacity: 0, duration: 0.2, ease: "power2.in" }, 4.3);'''

BEFORE = {
    "prefix": "bf",
    "repl": {
        "ID": "before", "INDEX": "01 / BEFORE", "WORD": "BEFORE", "RATE": "0.4×",
        "ACCENT": "#f4f1ea",
        "WORDSTYLE": "color: rgba(10, 13, 11, 0.55); -webkit-text-stroke: 4px #f4f1ea;",
        "TAKEAWAY": "0.3", "TOP": "1.2", "IMPACT": "2.1", "FINISH": "2.8",
        "SLOW0": "1.5", "SLOW1": "2.5", "FLASH": "0.3",
        "BALLX": "564", "BALLY": "1362", "TAGX": "680", "TAGY": "1262",
        "WIPEEL": '<div id="P-wipe" data-layout-ignore></div>',
        "FOCUSCSS": "", "FOCUSEL": "", "FOCUSJS": "",
        "INTRO": """tl.fromTo("#P-word", { x: -60, opacity: 0 }, { x: 0, opacity: 1, duration: 0.35, ease: "expo.out" }, 0);
    tl.fromTo("#P-chips", { y: -16, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, 0.05);
    tl.fromTo("#P-phases", { opacity: 0 }, { opacity: 1, duration: 0.25, ease: "power2.out" }, 0.12);""",
        # Lime panel rises over the last frames and covers the cut into AFTER
        "OUTRO": """tl.fromTo("#P-wipe", { yPercent: 100 }, { yPercent: 0, duration: 0.24, ease: "power3.in" }, 2.86);""",
    },
}
AFTER = {
    "prefix": "af",
    "repl": {
        "ID": "after", "INDEX": "02 / AFTER · WEIGHT SHIFT",
        "FOCUSCSS": FOCUS_CSS, "FOCUSEL": FOCUS_EL, "FOCUSJS": FOCUS_JS, "WORD": "AFTER", "RATE": "0.4×",
        "ACCENT": "#d4ff3a",
        "WORDSTYLE": "color: #d4ff3a;",
        "TAKEAWAY": "0.5", "TOP": "1.45", "IMPACT": "2.25", "FINISH": "3.1",
        "SLOW0": "1.7", "SLOW1": "2.82", "FLASH": "0.55",
        "BALLX": "653", "BALLY": "1238", "TAGX": "770", "TAGY": "1138",
        "WIPEEL": '<div id="P-wipe" data-layout-ignore></div>',
        # (the wipe starts covering the frame) Panel continues up and off, revealing AFTER; the word slams in behind it
        "INTRO": """tl.fromTo("#P-wipe", { yPercent: 0 }, { yPercent: -100, duration: 0.3, ease: "power3.out" }, 0);
    tl.fromTo("#P-word", { scale: 1.25, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "expo.out", transformOrigin: "left center" }, 0.08);
    tl.fromTo("#P-chips", { y: -16, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, 0.12);
    tl.fromTo("#P-phases", { opacity: 0 }, { opacity: 1, duration: 0.25, ease: "power2.out" }, 0.18);""",
        "OUTRO": """tl.to(["#P-word", "#P-chips", "#P-phases"], { y: -30, opacity: 0, duration: 0.2, ease: "power3.in", stagger: 0.03 }, 4.6);
    tl.to("#P-scrim", { opacity: 0, duration: 0.2, ease: "power2.in" }, 4.62);""",
    },
}

out = pathlib.Path(sys.argv[1])
(out / "before.html").write_text(scene(BEFORE))
(out / "after.html").write_text(scene(AFTER))
print("ok")
