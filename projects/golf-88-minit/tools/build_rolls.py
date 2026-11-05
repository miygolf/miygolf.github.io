"""Write compositions/rolla.html and rollb.html from one template.

Each roll: a film-advance band covers the cut in, an edge-code chip names the roll,
a REPLAY tag marks the 0.5x replay, then the freeze: shutter flash, frame border,
title, and a loupe that stops on the hips, then the trail knee, each stop signed in
grease pencil. Positions are in 1080x1920 frame pixels, read off the impact stills.
Run:  python3 tools/build_rolls.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

ROLLS = {
    "rolla": dict(
        roll="BEFORE", clock="09:55", frame="12A", still="assets/stills/b_imp.jpg",
        title="Before.",
        stops=[(615, 955), (505, 1200)],
        labels=[("pinggul", 70, 900, -4), ("lutut", 690, 1160, 3)],
        # local times (scene starts 0.15 s before its cut)
        T=dict(cut=0.15, replay=2.1833, freeze=3.05, loupe=3.2, l1=3.967, move=4.35, l2=4.767, under=5.567, out=6.05),
        dur=6.35,
    ),
    "rollb": dict(
        roll="AFTER", clock="11:23", frame="14A", still="assets/stills/a_imp.jpg",
        title="After.",
        stops=[(600, 822), (462, 1122)],
        labels=[("pinggul", 70, 770, -4), ("lutut", 650, 1085, 3)],
        T=dict(cut=0.15, replay=1.7833, freeze=2.65, loupe=2.8, l1=3.567, move=3.95, l2=4.367, under=5.167, out=5.7),
        dur=5.95,
    ),
}

TEMPLATE = r"""<template>
  <style>
    @font-face { font-family: "Bricolage Grotesque"; src: url("assets/fonts/Bricolage-800.woff2") format("woff2"); font-weight: 800; font-stretch: 75% 100%; }
    @font-face { font-family: "DM Mono"; src: url("assets/fonts/DMMono-500.woff2") format("woff2"); font-weight: 500; }
    @font-face { font-family: "Permanent Marker"; src: url("assets/fonts/PermanentMarker.woff2") format("woff2"); font-weight: 400; }
    #root { position: absolute; inset: 0; overflow: hidden; }
    .ID-band {
      position: absolute; left: 0; top: 0; width: 1080px; height: 1180px; background: #0e0c0a;
      background-image:
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1080' height='72'%3E%3Crect x='18' y='22' width='36' height='28' rx='6' fill='%23f6f2e9' fill-opacity='.9'/%3E%3Crect x='1026' y='22' width='36' height='28' rx='6' fill='%23f6f2e9' fill-opacity='.9'/%3E%3C/svg%3E");
      background-size: 1080px 72px; background-repeat: repeat-y;
    }
    .ID-band::before, .ID-band::after {
      content: ""; position: absolute; left: 76px; right: 76px; height: 4px; background: #2a2520;
    }
    .ID-band::before { top: 300px; } .ID-band::after { top: 880px; }
    .ID-band span {
      position: absolute; left: 96px; font: 500 30px/1 "DM Mono", monospace; letter-spacing: .14em; color: #ff8a1f;
    }
    #ID-strip {
      position: absolute; left: 0; top: 0; width: 46px; height: 1920px; background: rgba(14, 12, 10, .82);
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='46' height='72'%3E%3Crect x='10' y='22' width='26' height='22' rx='5' fill='%23f6f2e9' fill-opacity='.75'/%3E%3C/svg%3E");
      background-size: 46px 72px; background-repeat: repeat-y;
    }
    #ID-chip {
      position: absolute; left: 72px; top: 190px; display: flex; align-items: center; gap: 18px;
      font: 500 36px/1 "DM Mono", monospace; letter-spacing: .08em; color: #ff8a1f;
      background: rgba(14, 12, 10, .8); padding: 14px 22px 14px 16px; border-radius: 6px;
    }
    #ID-chip i { display: block; width: 16px; height: 22px; border-radius: 4px; background: #ff8a1f; }
    #ID-chip em { font-style: normal; color: #f6f2e9; }
    #ID-replay {
      position: absolute; left: 72px; top: 272px; font: 500 30px/1 "DM Mono", monospace; letter-spacing: .14em;
      color: #14110e; background: #ff8a1f; padding: 10px 16px; border-radius: 4px;
    }
    #ID-title {
      position: absolute; left: 66px; top: 280px; width: 860px;
      font: 800 108px/0.92 "Bricolage Grotesque", sans-serif; font-stretch: 78%; letter-spacing: -.01em;
      color: #f6f2e9; text-shadow: 0 5px 0 rgba(14, 12, 10, .55), 0 0 36px rgba(14, 12, 10, .4);
    }
    #ID-under { position: absolute; left: 60px; top: 392px; width: 640px; height: 60px; overflow: visible; }
    #ID-frame { position: absolute; inset: 0; border-radius: 34px; box-shadow: 0 0 0 26px #0e0c0a, inset 0 0 0 3px rgba(255, 138, 31, .9); }
    #ID-flash { position: absolute; inset: 0; background: #fffaf0; opacity: 0; }
    #ID-lp {
      position: absolute; left: 0; top: 0; width: DIAMpx; height: DIAMpx; border-radius: 50%; overflow: hidden;
      border: 10px solid #14110e; box-shadow: 0 0 0 4px #ff8a1f, 0 18px 40px rgba(0, 0, 0, .45);
    }
    #ID-lp img { position: absolute; left: 0; top: 0; width: ZWpx; height: ZHpx; }
    #ID-lp::after {
      content: ""; position: absolute; inset: 0; border-radius: 50%;
      background: radial-gradient(circle at 32% 26%, rgba(255, 255, 255, .28), transparent 34%),
                  radial-gradient(circle, transparent 62%, rgba(14, 12, 10, .35) 100%);
    }
    .ID-lab {
      position: absolute; font: 400 70px/1 "Permanent Marker", cursive; color: #ff8a1f;
      text-shadow: 0 3px 0 #14110e, 0 0 18px rgba(14, 12, 10, .6);
    }
    .ID-ring { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }
  </style>
  <div id="root" data-composition-id="ID" data-width="1080" data-height="1920"
    data-composition-variables='VARS'>
    <div id="ID-strip-host" class="clip" data-start="CUT" data-duration="STRIPDUR" data-layout-ignore><div id="ID-strip"></div></div>
    <div id="ID-frame-host" class="clip" data-start="FREEZE" data-duration="FRAMEDUR" data-layout-ignore><div id="ID-frame"></div></div>
    <div id="ID-chip-host" class="clip" data-start="CUT" data-duration="CHIPDUR"><div id="ID-chip"><i></i><span>ROLL</span><em data-var-text="clock">CLOCK</em></div></div>
    <div id="ID-replay-host" class="clip" data-start="REPAT" data-duration="REPDUR"><div id="ID-replay">REPLAY · ½×</div></div>
    <div id="ID-title-host" class="clip" data-start="FREEZE" data-duration="FRAMEDUR"><div id="ID-title" data-var-text="title">TITLE</div></div>
    <div id="ID-under-host" class="clip" data-start="UNDER" data-duration="UNDERDUR" data-layout-ignore>
      <svg id="ID-under" viewBox="0 0 640 60"><path id="ID-under-p" d="M6 38 C 120 22, 260 30, 380 26 S 560 18, 632 30" fill="none" stroke="#ff8a1f" stroke-width="11" stroke-linecap="round"/></svg>
    </div>
    <div id="ID-rings-host" class="clip" data-start="L1" data-duration="RINGDUR" data-layout-ignore>
      <svg class="ID-ring" viewBox="0 0 1080 1920">
        <path id="ID-ring1" d="RING1" fill="none" stroke="#ff8a1f" stroke-width="9" stroke-linecap="round"/>
        <path id="ID-ring2" d="RING2" fill="none" stroke="#ff8a1f" stroke-width="9" stroke-linecap="round"/>
      </svg>
    </div>
    <div id="ID-lab1-host" class="clip" data-start="L1" data-duration="RINGDUR"><div id="ID-lab1" class="ID-lab" style="left:LAB1Xpx;top:LAB1Ypx" data-var-text="lab1">LAB1</div></div>
    <div id="ID-lab2-host" class="clip" data-start="L2" data-duration="RING2DUR"><div id="ID-lab2" class="ID-lab" style="left:LAB2Xpx;top:LAB2Ypx" data-var-text="lab2">LAB2</div></div>
    <div id="ID-lp-host" class="clip" data-start="LOUPE" data-duration="LPDUR" data-layout-ignore><div id="ID-lp"><img id="ID-lp-img" src="STILL" alt="" /></div></div>
    <div id="ID-flash-host" class="clip" data-start="FLASHAT" data-duration="0.5" data-layout-ignore><div id="ID-flash"></div></div>
    <div id="ID-band-host" class="clip" data-start="0" data-duration="0.36" data-layout-ignore><div class="ID-band" id="ID-band"><span style="top:250px">▸ FRAMENO</span><span style="top:900px">▸ NEXTNO</span></div></div>
  </div>
  <script>
    const P = PARAMS;
    const tl = gsap.timeline({ paused: true });
    const T = P.T, R = P.r, Z = P.zoom;
    // film advance: a frame gap with sprockets whips up through the cut
    tl.fromTo("#ID-band", { y: 1920 }, { y: -1180, duration: 0.34, ease: "power1.inOut" }, 0);
    // edge-code chip and sprocket strip
    tl.fromTo("#ID-chip", { x: -40, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: "power3.out" }, T.cut + 0.05);
    tl.fromTo("#ID-strip", { x: -46 }, { x: 0, duration: 0.25, ease: "power3.out" }, T.cut);
    tl.fromTo("#ID-replay", { x: -30, opacity: 0 }, { x: 0, opacity: 1, duration: 0.2, ease: "power3.out" }, T.replay);
    // freeze
    tl.fromTo("#ID-flash", { opacity: 0.9 }, { opacity: 0, duration: 0.3, ease: "power2.out" }, T.freeze);
    tl.fromTo("#ID-frame", { scale: 1.07, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.22, ease: "power4.out" }, T.freeze);
    tl.fromTo("#ID-chip", { y: 0 }, { y: -6, duration: 0.1, yoyo: true, repeat: 1, ease: "power2.out" }, T.freeze);
    tl.fromTo("#ID-title", { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.34, ease: "power3.out" }, T.freeze + 0.1);
    // loupe: container and magnified image move together, so the lens always shows what is under it
    const [s1, s2] = P.stops;
    const box = (p) => ({ x: p[0] - R, y: p[1] - R });
    const img = (p) => ({ x: R - 10 - Z * p[0], y: R - 10 - Z * p[1] });
    tl.set("#ID-lp", box(s1), 0);
    tl.set("#ID-lp-img", img(s1), 0);
    tl.fromTo("#ID-lp", { scale: 0.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(1.5)" }, T.loupe);
    tl.to("#ID-lp", { ...box(s2), duration: 0.35, ease: "power2.inOut" }, T.move);
    tl.to("#ID-lp-img", { ...img(s2), duration: 0.35, ease: "power2.inOut" }, T.move);
    tl.to("#ID-lp", { scale: 0.2, opacity: 0, duration: 0.22, ease: "power2.in" }, T.out);
    // grease pencil: ring where the lens stopped, then the word
    const draw = (sel, at, d) => {
      tl.fromTo(sel, { strokeDasharray: 1600, strokeDashoffset: 1600 }, { strokeDashoffset: 0, duration: d, ease: "power1.inOut" }, at);
    };
    draw("#ID-ring1", T.l1 - 0.05, 0.3);
    draw("#ID-ring2", T.l2 - 0.05, 0.3);
    tl.fromTo("#ID-lab1", { opacity: 0, scale: 0.7, rotation: P.labels[0][3] - 6 }, { opacity: 1, scale: 1, rotation: P.labels[0][3], duration: 0.22, ease: "back.out(2)" }, T.l1);
    tl.fromTo("#ID-lab2", { opacity: 0, scale: 0.7, rotation: P.labels[1][3] + 6 }, { opacity: 1, scale: 1, rotation: P.labels[1][3], duration: 0.22, ease: "back.out(2)" }, T.l2);
    tl.fromTo("#ID-under-p", { strokeDasharray: 700, strokeDashoffset: 700 }, { strokeDashoffset: 0, duration: 0.28, ease: "power1.out" }, T.under);
    window.__timelines["ID"] = tl;
  </script>
</template>
"""


def ring(cx, cy, r):
    """A hand-drawn loop that overshoots its start, like a grease-pencil circle."""
    rx, ry = r * 0.78, r * 0.62
    return (f"M {cx - rx:.0f} {cy - 8:.0f} "
            f"C {cx - rx:.0f} {cy - ry - 14:.0f}, {cx + rx + 12:.0f} {cy - ry - 6:.0f}, {cx + rx:.0f} {cy + 4:.0f} "
            f"S {cx - 6:.0f} {cy + ry + 14:.0f}, {cx - rx - 6:.0f} {cy + 10:.0f} "
            f"S {cx - 20:.0f} {cy - ry - 2:.0f}, {cx + 34:.0f} {cy - ry - 12:.0f}")


def build(cid, c):
    r, zoom = 150, 2.0
    T = c["T"]
    end = c["dur"]
    params = dict(T=T, r=r, zoom=zoom, stops=c["stops"], labels=c["labels"])
    variables = [
        {"id": "clock", "type": "string", "label": "Roll time", "default": c["clock"]},
        {"id": "title", "type": "string", "label": "Freeze title", "default": c["title"]},
        {"id": "lab1", "type": "string", "label": "Loupe stop 1 label", "default": c["labels"][0][0]},
        {"id": "lab2", "type": "string", "label": "Loupe stop 2 label", "default": c["labels"][1][0]},
    ]
    nums = {"12A": ("12A", "13"), "14A": ("14A", "15")}[c["frame"]]
    s = TEMPLATE
    rep = {
        "VARS": json.dumps(variables, ensure_ascii=False),
        "PARAMS": json.dumps(params),
        "DIAM": str(2 * r), "ZW": str(int(1080 * zoom)), "ZH": str(int(1920 * zoom)),
        "STILL": c["still"], "TITLE": c["title"], "CLOCK": c["clock"],
        "CUT": f"{T['cut']}", "STRIPDUR": f"{end - T['cut']:.3f}", "CHIPDUR": f"{end - T['cut']:.3f}",
        "REPAT": f"{T['replay']}", "REPDUR": f"{T['freeze'] - T['replay']:.3f}",
        "FREEZE": f"{T['freeze']}", "FRAMEDUR": f"{end - T['freeze']:.3f}", "FLASHAT": f"{T['freeze']}",
        "UNDER": f"{T['under']}", "UNDERDUR": f"{end - T['under']:.3f}",
        "LOUPE": f"{T['loupe']}", "LPDUR": f"{T['out'] + 0.3 - T['loupe']:.3f}",
        "L1": f"{T['l1'] - 0.05:.3f}", "L2": f"{T['l2'] - 0.05:.3f}",
        "RINGDUR": f"{end - T['l1'] + 0.05:.3f}", "RING2DUR": f"{end - T['l2'] + 0.05:.3f}",
        "RING1": ring(*c["stops"][0], r), "RING2": ring(*c["stops"][1], r),
        "LAB1X": str(c["labels"][0][1]), "LAB1Y": str(c["labels"][0][2]),
        "LAB2X": str(c["labels"][1][1]), "LAB2Y": str(c["labels"][1][2]),
        "LAB1": c["labels"][0][0], "LAB2": c["labels"][1][0],
        "FRAMENO": nums[0], "NEXTNO": nums[1],
    }
    # longest keys first so e.g. RING2DUR is not eaten by RING2
    for k in sorted(rep, key=len, reverse=True):
        s = s.replace(k, rep[k])
    s = s.replace(">ROLL<", f">{c['roll']} ·<")
    s = s.replace("ID-", f"{cid}-").replace('"ID"', f'"{cid}"').replace("#ID", f"#{cid}").replace(".ID", f".{cid}")
    (HERE / "compositions" / f"{cid}.html").write_text(s)
    print("wrote", cid)


for cid, c in ROLLS.items():
    build(cid, c)
