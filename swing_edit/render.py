"""Render a vertical swing-analysis edit (1080x1920 @30fps) from extracted frames + pose data.

Usage: python3 render.py <config.json> <workdir> [frame numbers to dump as preview stills...]
  workdir must contain:
    all/f%04d.jpg     every frame of the source clip, scaled to 1080x1920 (src_fps from config)
    slow/s%04d.jpg    120fps motion-interpolated frames starting at config slow.t0
    work/pose.json    MediaPipe pose landmarks keyed by 0-based frame index
Writes work/video.mp4 (silent) and work/timeline.json (read by audio.py).
"""
import glob, json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

C = json.load(open(sys.argv[1]))
D = sys.argv[2]
SRC_FPS = C["src_fps"]
T = C["times"]; T_TAKEAWAY, T_TOP, T_IMPACT = T["takeaway"], T["top"], T["impact"]
FR = C["frames"]; I_ADDR, I_TOP, I_IMP, I_FIN = FR["addr"], FR["top"], FR["imp"], FR["fin"]
SLOW_T0, SLOW_FPS = C["slow"]["t0"], C["slow"]["fps"]
VIEW_CX, VIEW_CY = C["view"]["cx"], C["view"]["cy"]
BALL = tuple(C["ball"])


# ---------- pose ----------
POSE = load_pose(f"{D}/work/pose.json")
N = len(POSE)
def pose_at(fi): return interp_pose(POSE, fi)
def spine(i): p = POSE[i]; return angle_from_vertical(mid(p, 23, 24), mid(p, 11, 12))

# numbers available to config text as {name}
BS, DS = T_TOP - T_TAKEAWAY, T_IMPACT - T_TOP
VALS = {"addr_angle": round(spine(I_ADDR)), "imp_angle": round(spine(I_IMP)),
        "angle_loss": round(spine(I_ADDR) - spine(I_IMP)),
        "rknee_addr": round(joint_angle(POSE[I_ADDR], 24, 26, 28)), "rknee_top": round(joint_angle(POSE[I_TOP], 24, 26, 28)),
        "bs": f"{BS:.2f}", "ds": f"{DS:.2f}", "ratio": f"{BS / DS:.1f}"}
def fmt(s): return s.format(**VALS)


_cache = {}
def frame(i):
    i = min(max(i, 0), N - 1)
    if i not in _cache:
        if len(_cache) > 6: _cache.clear()
        _cache[i] = Image.open(f"{D}/all/f{i + 1:04d}.jpg").convert("RGB")
    return _cache[i]
def slow(k): return Image.open(f"{D}/slow/s{k:04d}.jpg").convert("RGB")
N_SLOW = C["slow"].get("n") or len(glob.glob(f"{D}/slow/s*.jpg"))

def skeleton(d, p, view, alpha=230):
    q = [view.pt(x) for x in p]
    for a, b in BONES: d.line([q[a], q[b]], fill=(255, 255, 255, int(alpha * .75)), width=5)
    for j in (11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28):
        x, y = q[j]; d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=LIME + (alpha,), outline=(0, 0, 0, alpha), width=2)
    hx, hy = q[0]; d.ellipse((hx - 34, hy - 34, hx + 34, hy + 34), outline=LIME + (int(alpha * .8),), width=4)

PHASES = C["phases"]
def phase_of(t):
    for t_end, name in PHASES:
        if t < t_end: return name
    return PHASES[-1][1]

def hand_trail(d, t_now, view, alpha=255):
    pts = []; t = T_TAKEAWAY + 0.03
    while t <= t_now:
        pts.append((t, view.pt(mid(pose_at(t * SRC_FPS), 15, 16)))); t += 1 / 120
    for (t1, a), (t2, b) in zip(pts, pts[1:]):
        c = CYAN if t2 <= T_TOP + 0.04 else AMBER
        d.line([a, b], fill=c + (alpha,), width=9)
    if pts:
        x, y = pts[-1][1]; c = CYAN if t_now <= T_TOP + 0.04 else AMBER
        d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=c + (alpha,), outline=WHITE + (alpha,), width=3)

VIG = vignette()

def brand(d, alpha=200):
    text(d, (W // 2, 70), C.get("brand", "SWING CHECK  ·  AI BREAKDOWN"), fSemi(28), fill=WHITE, anchor="mm", alpha=alpha)

# ---------- segments ----------
frames_out = []; marks = {}
def emit(name, fn, n):
    marks[name] = len(frames_out)
    for k in range(n): frames_out.append((fn, k, n))

# S1 hook: real speed
HK = C["hook"]
N_HOOK = int(round((HK["t1"] - HK["t0"]) * FPS))
def s1(k, n):
    t = HK["t0"] + k / FPS; i = int(round(t * SRC_FPS))
    dt = t - T_IMPACT
    punch = (1 - dt / 0.2) * 0.07 if 0 <= dt < 0.2 else 0
    v = View(HK.get("zoom", 1.18) + punch, HK.get("cx", VIEW_CX + 40), HK.get("cy", VIEW_CY))
    im = v.img(frame(i)).convert("RGBA"); im.alpha_composite(VIG)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    brand(d)
    u = ease(k / 10); y = lerp(-120, 0, u)
    text(d, (W // 2, 210 + y), HK["title"], fBlack(112 if len(HK["title"]) <= 13 else 96), anchor="mm", alpha=int(255 * u))
    text(d, (W // 2, 310 + y), HK["sub"], fBold(52), fill=LIME, anchor="mm", alpha=int(255 * u))
    chip(d, (60, H - 200), "REAL SPEED", fBold(34), alpha=int(230 * u))
    im.alpha_composite(o)
    if 0 <= dt < 0.1:
        im.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(170 * (1 - dt / 0.1)))))
    return im.convert("RGB")
emit("hook", s1, N_HOOK)

# S2 slow-mo with skeleton, hand path, phase labels, stopwatch, impact hold
K_IMP = 1 + round((T_IMPACT - SLOW_T0) * SLOW_FPS)
HOLD = 18
SLOW_SEQ = list(range(1, K_IMP + 1)) + [K_IMP] * HOLD + list(range(K_IMP + 1, N_SLOW + 1))
def s2(k, n):
    ks = SLOW_SEQ[k]; t = SLOW_T0 + (ks - 1) / SLOW_FPS
    v = View(lerp(1.28, 1.42, ease(k / n)), VIEW_CX, VIEW_CY)
    im = v.img(slow(ks)).convert("RGBA"); im.alpha_composite(VIG)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    fade_in = ease(k / 12)
    hand_trail(d, t, v, alpha=int(255 * fade_in))
    skeleton(d, pose_at(t * SRC_FPS), v, alpha=int(230 * fade_in))
    brand(d)
    text(d, (W // 2, 190), "SLOW-MO", fBlack(96), anchor="mm")
    chip(d, (W // 2 - 70, 262), f"{FPS / SLOW_FPS:.2f}x SPEED", fBold(30), bg=WHITE)
    ph = phase_of(t); col = RED if ph == "IMPACT" else LIME
    panel(d, (60, H - 240, W - 60, H - 70), fill=(8, 12, 10, 190))
    text(d, (100, H - 218), "FASA", fSemi(28), fill=(180, 190, 185), shadow=False)
    text(d, (100, H - 180), ph, fBlack(64), fill=col, shadow=False)
    text(d, (W - 100, H - 218), "MASA", fSemi(28), fill=(180, 190, 185), anchor="ra", shadow=False)
    text(d, (W - 100, H - 184), f"{max(0.0, t - T_TAKEAWAY):0.2f}s", fBlack(70), anchor="ra", shadow=False)
    d.line([(W // 2 - 250, 335), (W // 2 - 200, 335)], fill=CYAN, width=9)
    text(d, (W // 2 - 188, 317), "backswing", fSemi(28))
    d.line([(W // 2 + 20, 335), (W // 2 + 70, 335)], fill=AMBER, width=9)
    text(d, (W // 2 + 82, 317), "downswing", fSemi(28))
    im.alpha_composite(o)
    j = k - (K_IMP - 1)
    if 0 <= j < HOLD:
        bx, by = v.pt(BALL)
        if j < 3: im.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - j / 3)))))
        r = 30 + j * 16; o2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(o2)
        a = int(255 * (1 - j / HOLD))
        d2.ellipse((bx - r, by - r, bx + r, by + r), outline=WHITE + (a,), width=8)
        text(d2, (W - 50, by - 190), "IMPACT!", fBlack(84), fill=RED, anchor="rm", alpha=max(a, 120))
        im.alpha_composite(o2)
    return im.convert("RGB")
emit("slow", s2, len(SLOW_SEQ))

# ---------- freeze-frame cards ----------
def card_base(i, k, n, ghost=None, ghost_alpha=0):
    v = View(lerp(1.32, 1.44, ease(k / n)), VIEW_CX, VIEW_CY)
    src = frame(i)
    if ghost is not None and ghost_alpha > 0: src = Image.blend(src, frame(ghost), ghost_alpha)
    im = v.img(src).convert("RGBA")
    im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 40))); im.alpha_composite(VIG)
    return v, im

def card_text(d, k, num, cd):
    col = COLORS[cd.get("color", "lime")]
    u = ease(k / 9); brand(d)
    x = lerp(-300, 60, u)
    chip(d, (x + 22, 150), f"{num:02d}  {cd['label']}", fBold(34), bg=col, fg=WHITE if col == RED else INK, alpha=int(255 * u))
    title = fmt(cd["title"])
    text(d, (60, 230), title, fBlack(76 if len(title) < 18 else 64), alpha=int(255 * u))
    ub = ease((k - 6) / 10)
    if ub > 0:
        y0 = H - 400 + (1 - ub) * 80
        panel(d, (50, y0, W - 50, y0 + 300), fill=(8, 12, 10, int(215 * ub)))
        for j, s in enumerate(cd["lines"]):
            text(d, (95, y0 + 40 + j * 66), fmt(s), fSemi(38), alpha=int(255 * ub), shadow=False)
        text(d, (W - 95, y0 + 260), cd["score"], fBlack(66), fill=col, anchor="rd", alpha=int(255 * ub), shadow=False)
        text(d, (95, y0 + 260), "markah", fSemi(28), fill=(170, 180, 175), anchor="ld", alpha=int(255 * ub), shadow=False)

def card_setup(k, n, cd):
    v, im = card_base(I_ADDR, k, n)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    p = POSE[I_ADDR]; hip = mid(p, 23, 24); sh = mid(p, 11, 12)
    H_, S_ = v.pt(hip), v.pt(sh)
    ext = (S_[0] + (S_[0] - H_[0]) * .35, S_[1] + (S_[1] - H_[1]) * .35)
    ua = ease((k - 8) / 14)
    dashed(d, H_, (H_[0], H_[1] - 380 * ua + 1), WHITE + (220,), width=5)
    partial_line(d, H_, ext, ua, fill=LIME + (255,), width=10)
    ang = angle_from_vertical(hip, sh)
    if ua > .5:
        r = 150; d.arc((H_[0] - r, H_[1] - r, H_[0] + r, H_[1] + r), -90, -90 + ang * ease((k - 15) / 10), fill=LIME + (255,), width=7)
        text(d, (H_[0] + 120, H_[1] - 230), f"{ang:.0f}°", fBlack(70), fill=LIME, alpha=int(255 * ease((k - 18) / 8)))
    card_text(d, k, cd["num"], cd)
    im.alpha_composite(o); return im.convert("RGB")

def card_top(k, n, cd):
    v, im = card_base(I_TOP, k, n)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    hand_trail(d, T_TAKEAWAY + (T_TOP - T_TAKEAWAY) * ease((k - 4) / 20), v)
    p = POSE[I_TOP]
    ua = ease((k - 22) / 10)
    if ua > 0:
        hx, hy = v.pt(p[0])
        if cd.get("head_ghost"):
            ax, ay = v.pt(POSE[I_ADDR][0]); dashed_circle(d, (ax, ay), 60, WHITE + (int(220 * ua),))
        d.ellipse((hx - 60, hy - 60, hx + 60, hy + 60), outline=LIME + (int(255 * ua),), width=6)
        text(d, (hx + 40, hy - 130), "kepala stabil", fBold(40), fill=LIME, alpha=int(255 * ua))
        ex = cd.get("extra")
        if ex == "across":
            hands, ch = v.pt(cd["club_hands"]), v.pt(cd["club_head"])
            tip = (hands[0] + (ch[0] - hands[0]) * 3.2, hands[1] + (ch[1] - hands[1]) * 3.2)
            dashed(d, ch, (lerp(ch[0], tip[0], ua), lerp(ch[1], tip[1], ua)), AMBER + (255,), width=6)
            if ua > .7:
                text(d, (tip[0] - 10, tip[1] + 20), "across the line", fBold(40), fill=AMBER, anchor="ra")
                text(d, (tip[0] - 10, tip[1] + 70), "shaft tunjuk kanan target", fSemi(30), anchor="ra")
        elif ex == "knee":
            pa = POSE[I_ADDR]
            qa = [v.pt(pa[j]) for j in (24, 26, 28)]; qt = [v.pt(p[j]) for j in (24, 26, 28)]
            d.line(qa, fill=(255, 255, 255, int(200 * ua)), width=6, joint="curve")
            d.line(qt, fill=AMBER + (int(255 * ua),), width=9, joint="curve")
            kx, ky = qt[1]
            d.ellipse((kx - 14, ky - 14, kx + 14, ky + 14), fill=AMBER + (int(255 * ua),))
            text(d, (kx + 100, ky - 60), "lutut kanan", fBold(40), fill=AMBER, alpha=int(255 * ua))
            text(d, (kx + 100, ky - 10), f"{VALS['rknee_addr']}° → {VALS['rknee_top']}°", fBlack(48), fill=AMBER, alpha=int(255 * ua))
            text(d, (kx + 100, ky + 50), "putih = address", fSemi(28), alpha=int(255 * ua))
        bl = cd.get("butt_line")
        if bl:
            butt_a = min(POSE[I_ADDR][23][0], POSE[I_ADDR][24][0]) - 20
            a, b = v.pt((butt_a, bl[0])), v.pt((butt_a, bl[1]))
            dashed(d, a, (a[0], lerp(a[1], b[1], ua)), WHITE + (220,), width=5)
            text(d, (a[0] + 16, a[1] - 14), "depth pinggul OK", fSemi(30), anchor="lb", alpha=int(255 * ua))
    card_text(d, k, cd["num"], cd)
    im.alpha_composite(o); return im.convert("RGB")

def card_impact(k, n, cd):
    col = COLORS[cd.get("color", "red")]
    ga = 0.42 * ease((k - 10) / 14)
    v, im = card_base(I_IMP, k, n, ghost=I_ADDR, ghost_alpha=ga)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    pa, pi = POSE[I_ADDR], POSE[I_IMP]
    ha, sa = mid(pa, 23, 24), mid(pa, 11, 12); hi, si = mid(pi, 23, 24), mid(pi, 11, 12)
    butt_a = min(pa[23][0], pa[24][0]) - 25
    bl = cd["butt_line"]
    u1 = ease((k - 8) / 12)
    top = v.pt((butt_a, bl[0])); bot = v.pt((butt_a, bl[1]))
    dashed(d, top, (top[0], lerp(top[1], bot[1], u1) + 1), WHITE + (235,), width=6)
    if u1 > .6:
        lbl = "garis punggung (address)"; tw = d.textlength(lbl, font=fSemi(32))
        text(d, (max(top[0] + 20, tw + 40), top[1] - 14), lbl, fSemi(32), anchor="rb", alpha=int(255 * u1))
    u2 = ease((k - 18) / 12)
    A1, B1 = v.pt(ha), v.pt(sa); A2, B2 = v.pt(hi), v.pt(si)
    partial_line(d, A1, (B1[0] + (B1[0] - A1[0]) * .3, B1[1] + (B1[1] - A1[1]) * .3), u2, fill=WHITE + (230,), width=8)
    partial_line(d, A2, (B2[0] + (B2[0] - A2[0]) * .3, B2[1] + (B2[1] - A2[1]) * .3), u2, fill=col + (255,), width=10)
    u3 = ease((k - 30) / 10)
    if u3 > 0:
        shift = min(pi[23][0], pi[24][0]) - min(pa[23][0], pa[24][0])
        if shift > 10:
            bi = v.pt((min(pi[23][0], pi[24][0]) - 10, bl[2])); ba = v.pt((butt_a, bl[2]))
            arrow(d, (ba[0] - 10, ba[1]), (lerp(ba[0], bi[0] + 40, u3), bi[1]), col + (255,), width=10)
        text(d, (B2[0] + 60, B2[1] - 140), f"{spine(I_ADDR):.0f}° → {spine(I_IMP):.0f}°", fBlack(64), fill=col, alpha=int(255 * u3))
        if cd.get("head_dip"):
            hA, hI = v.pt(pa[0]), v.pt(pi[0])
            dashed_circle(d, hA, 58, WHITE + (int(230 * u3),))
            d.ellipse((hI[0] - 58, hI[1] - 58, hI[0] + 58, hI[1] + 58), outline=AMBER + (int(255 * u3),), width=6)
            text(d, (hI[0] + 75, hI[1] + 10), cd["head_dip"], fBold(38), fill=AMBER, alpha=int(255 * u3))
    card_text(d, k, cd["num"], cd)
    if ga > 0: text(d, (W - 60, 330), "bayang = posisi address", fSemi(30), anchor="ra", alpha=int(255 * min(1, ga / .42)))
    im.alpha_composite(o); return im.convert("RGB")

def card_finish(k, n, cd):
    v, im = card_base(I_FIN, k, n)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    p = POSE[I_FIN]
    ua = ease((k - 8) / 12)
    if ua > 0:
        lf = v.pt(p[27]); hip = v.pt(mid(p, 23, 24)); hd = v.pt(p[0])
        dashed(d, (lf[0], lf[1] + 30), (lf[0], lerp(lf[1] + 30, hd[1] - 60, ua)), LIME + (240,), width=6)
        if ua > .8:
            cx, cy = hip[0] + 190, hip[1] - 80
            d.ellipse((cx - 50, cy - 50, cx + 50, cy + 50), fill=LIME + (255,))
            d.line([(cx - 24, cy + 2), (cx - 6, cy + 22), (cx + 26, cy - 20)], fill=INK + (255,), width=10)
            text(d, (cx + 70, cy - 26), "balance", fBold(44), fill=LIME)
    card_text(d, k, cd["num"], cd)
    im.alpha_composite(o); return im.convert("RGB")

CARD_FN = {"setup": card_setup, "top": card_top, "impact": card_impact, "finish": card_finish}
CARD = 105
for j, cd in enumerate(C["cards"]):
    cd["num"] = j + 1
    emit(f"card{j + 1}", (lambda f, c: (lambda k, n: f(k, n, c)))(CARD_FN[cd["type"]], cd), CARD + cd.get("extra_frames", 0))

# ---------- tempo + rating on blurred background ----------
BG = None
def blurred_bg():
    global BG
    if BG is None:
        im = View(1.3, VIEW_CX, VIEW_CY).img(frame(I_FIN)).filter(ImageFilter.GaussianBlur(28)).convert("RGBA")
        im.alpha_composite(Image.new("RGBA", (W, H), (6, 14, 9, 165))); BG = im
    return BG.copy()

NUM_TEMPO = len(C["cards"]) + 1
def c_tempo(k, n):
    im = blurred_bg(); d = ImageDraw.Draw(im)
    u = ease(k / 10); brand(d)
    chip(d, (82, 170), f"{NUM_TEMPO:02d}  TEMPO", fBold(34), alpha=int(255 * u))
    text(d, (60, 250), "TEMPO SWING", fBlack(92), alpha=int(255 * u))
    def bar(y, label, val, col, delay):
        ub = ease((k - delay) / 16)
        text(d, (80, y), label, fBold(44), alpha=int(255 * ease((k - delay) / 6)), shadow=False)
        d.rounded_rectangle((80, y + 70, W - 80, y + 130), 30, fill=(255, 255, 255, 30))
        wmax = (W - 160) * val / 0.8
        if ub > 0: d.rounded_rectangle((80, y + 70, 80 + max(60, wmax * ub), y + 130), 30, fill=col)
        text(d, (W - 80, y), f"{val * ub:0.2f}s", fBlack(56), fill=col, anchor="ra", alpha=int(255 * ease((k - delay) / 6)), shadow=False)
    bar(520, "Backswing", BS, CYAN, 8)
    bar(720, "Downswing", DS, AMBER, 20)
    ur = ease((k - 36) / 10)
    if ur > 0:
        text(d, (W // 2, 1060), f"{BS / DS:.1f} : 1", fBlack(170), fill=LIME, anchor="mm", alpha=int(255 * ur))
        text(d, (W // 2, 1180), "nisbah tempo", fSemi(40), anchor="mm", alpha=int(255 * ur))
        panel(d, (60, 1300, W - 60, 1560), fill=(8, 12, 10, int(200 * ur)))
        for j, s in enumerate(C["tempo"]["lines"]):
            text(d, (100, 1335 + j * 68), fmt(s), fSemi(40), alpha=int(255 * ur), shadow=False)
    return im.convert("RGB")
emit("tempo", c_tempo, CARD)

RT = C["rating"]
def c_rating(k, n):
    im = blurred_bg(); d = ImageDraw.Draw(im)
    u = ease(k / 10); brand(d)
    text(d, (W // 2, 200), "SWING RATING", fBlack(84), anchor="mm", alpha=int(255 * u))
    val = RT["overall"] * ease((k - 4) / 30)
    text(d, (W // 2 - 30, 400), f"{val:0.1f}", fBlack(240), fill=LIME, anchor="rm", alpha=int(255 * u))
    text(d, (W // 2 - 10, 440), "/10", fBlack(110), anchor="lm", alpha=int(255 * u))
    if k > 34:
        f = fBold(32); tw = d.textlength(RT["tag"], font=f)
        chip(d, (W // 2 - tw / 2, 560), RT["tag"], f, alpha=int(255 * ease((k - 34) / 8)))
    for j, (name, s, cname) in enumerate(RT["scores"]):
        col = COLORS[cname]; y = 690 + j * 112; ub = ease((k - 10 - j * 5) / 16)
        text(d, (80, y), name, fBold(40), alpha=int(255 * ease((k - 10 - j * 5) / 6)), shadow=False)
        d.rounded_rectangle((80, y + 54, W - 80, y + 82), 14, fill=(255, 255, 255, 35))
        if ub > 0: d.rounded_rectangle((80, y + 54, 80 + max(28, (W - 160) * s / 10 * ub), y + 82), 14, fill=col)
        text(d, (W - 80, y), f"{s * ub:0.1f}", fBlack(44), fill=col, anchor="ra", alpha=int(255 * ease((k - 10 - j * 5) / 6)), shadow=False)
    uf = ease((k - 60) / 12)
    if uf > 0:
        fc = COLORS[RT.get("fix_color", "red")]
        y0 = 1300 + (1 - uf) * 100
        panel(d, (50, y0, W - 50, y0 + 470), fill=(8, 12, 10, int(225 * uf)), outline=fc + (int(255 * uf),), width=4)
        chip(d, (95, y0 + 40), "FIX NO.1", fBold(34), bg=fc, fg=WHITE if fc == RED else INK, alpha=int(255 * uf))
        text(d, (95, y0 + 110), RT["fix_title"], fBlack(62), alpha=int(255 * uf), shadow=False)
        for j, s in enumerate(RT["fix_lines"]):
            text(d, (95, y0 + 210 + j * 66), fmt(s), fSemi(40), alpha=int(255 * uf), shadow=False)
    return im.convert("RGB")
emit("rating", c_rating, 200)

# ---------- encode ----------
print("total frames", len(frames_out), "duration %.2fs" % (len(frames_out) / FPS))
json.dump({"frames": len(frames_out), "marks": marks, "k_imp": K_IMP, "hold": HOLD,
           "hook": HK, "slow_t0": SLOW_T0, "slow_fps": SLOW_FPS, "n_slow": N_SLOW, "impact": T_IMPACT},
          open(f"{D}/work/timeline.json", "w"), indent=1)
only = sys.argv[3:]
if only:
    for f in map(int, only):
        fn, k, n = frames_out[f]; fn(k, n).save(f"{D}/frames/prev_{f:04d}.jpg", quality=88)
    sys.exit()
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                       "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                       f"{D}/work/video.mp4"], stdin=subprocess.PIPE)
for idx, (fn, k, n) in enumerate(frames_out):
    ff.stdin.write(fn(k, n).tobytes())
    if idx % 200 == 0: print(idx, flush=True)
ff.stdin.close(); ff.wait()
print("done")
