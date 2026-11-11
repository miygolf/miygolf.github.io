"""Render a vertical swing-analysis edit (1080x1920 @30fps) from extracted frames + pose data.

Usage: python3 render.py <workdir>
  workdir must contain:
    all/f%04d.jpg     every frame of the source clip (30fps)
    slow/s%04d.jpg    120fps motion-interpolated frames starting at t=5.2s
    work/pose.json    MediaPipe pose landmarks keyed by 0-based frame index
Writes work/video.mp4 (silent) — audio is built by audio.py and muxed afterwards.
"""
import json, math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
D = sys.argv[1]

# ---------- swing timing (seconds in source clip, from frame-by-frame review) ----------
T_TAKEAWAY, T_TOP, T_IMPACT = 5.43, 6.00, 6.233
I_ADDR, I_TOP, I_IMP, I_FIN = 156, 180, 187, 210
SLOW_T0 = 5.2

# ---------- look ----------
F = "/usr/share/fonts/opentype/inter/"
def font(name, size): return ImageFont.truetype(F + name, size)
LIME = (198, 255, 61); WHITE = (255, 255, 255); RED = (255, 77, 77)
CYAN = (61, 214, 255); AMBER = (255, 176, 32); INK = (8, 12, 10)
fBlack = lambda s: font("InterDisplay-Black.otf", s)
fBold = lambda s: font("InterDisplay-Bold.otf", s)
fSemi = lambda s: font("Inter-SemiBold.otf", s)

# ---------- pose ----------
RAW = {int(k): v for k, v in json.load(open(f"{D}/work/pose.json")).items()}
N = max(RAW) + 1
def smooth(idx):
    out = {}
    for i in range(N):
        pts = []
        for j in range(33):
            acc = [0, 0]; wsum = 0
            for o, w in ((-1, 1), (0, 2), (1, 1)):
                k = min(max(i + o, 0), N - 1)
                acc[0] += RAW[k][j][0] * w; acc[1] += RAW[k][j][1] * w; wsum += w
            pts.append((acc[0] / wsum * W, acc[1] / wsum * H))
        out[i] = pts
    return out
POSE = smooth(RAW)
def pose_at(fi):
    a = int(math.floor(fi)); b = min(a + 1, N - 1); u = fi - a
    return [(pa[0] + (pb[0] - pa[0]) * u, pa[1] + (pb[1] - pa[1]) * u) for pa, pb in zip(POSE[a], POSE[b])]
def mid(p, a, b): return ((p[a][0] + p[b][0]) / 2, (p[a][1] + p[b][1]) / 2)

# ---------- helpers ----------
def ease(u): u = min(max(u, 0), 1); return 1 - (1 - u) ** 3
def lerp(a, b, u): return a + (b - a) * u

class View:
    def __init__(self, z, cx, cy):
        self.z = z; w, h = W / z, H / z
        self.x0 = min(max(cx - w / 2, 0), W - w); self.y0 = min(max(cy - h / 2, 0), H - h)
        self.w, self.h = w, h
    def img(self, im):
        return im.resize((W, H), Image.LANCZOS, box=(self.x0, self.y0, self.x0 + self.w, self.y0 + self.h))
    def pt(self, p): return ((p[0] - self.x0) * self.z, (p[1] - self.y0) * self.z)

_cache = {}
def frame(i):
    if ('f', i) not in _cache:
        _cache.clear(); _cache[('f', i)] = Image.open(f"{D}/all/f{i + 1:04d}.jpg").convert("RGB")
    return _cache[('f', i)]
def slow(k): return Image.open(f"{D}/slow/s{k:04d}.jpg").convert("RGB")

def text(d, xy, s, f, fill=WHITE, anchor="la", shadow=True, alpha=255):
    if shadow:
        d.text((xy[0] + 3, xy[1] + 4), s, font=f, fill=(0, 0, 0, int(150 * alpha / 255)), anchor=anchor)
    d.text(xy, s, font=f, fill=fill[:3] + (alpha,), anchor=anchor)

def panel(d, box, r=28, fill=(8, 12, 10, 200), outline=None, width=3):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)

def chip(d, xy, s, f, bg=LIME, fg=INK, alpha=255, pad=(22, 12)):
    l, t, r, b = d.textbbox(xy, s, font=f)
    d.rounded_rectangle((l - pad[0], t - pad[1], r + pad[0], b + pad[1]), (b - t) // 2 + pad[1], fill=bg[:3] + (alpha,))
    d.text(xy, s, font=f, fill=fg[:3] + (alpha,))
    return r + pad[0]

def dashed(d, a, b, fill, width=5, dash=22, gap=14):
    L = math.dist(a, b); n = int(L // (dash + gap)) + 1
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    for k in range(n):
        s = k * (dash + gap); e = min(s + dash, L)
        d.line([(a[0] + ux * s, a[1] + uy * s), (a[0] + ux * e, a[1] + uy * e)], fill=fill, width=width)

def arrow(d, a, b, fill, width=8, head=26):
    d.line([a, b], fill=fill, width=width)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    for s in (2.6, -2.6):
        d.line([b, (b[0] + head * math.cos(ang + s), b[1] + head * math.sin(ang + s))], fill=fill, width=width)

def partial_line(d, a, b, u, **kw):
    if u <= 0: return
    d.line([a, (lerp(a[0], b[0], u), lerp(a[1], b[1], u))], **kw)

BONES = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16), (11, 23), (12, 24), (23, 24),
         (23, 25), (25, 27), (24, 26), (26, 28), (27, 31), (28, 32)]
def skeleton(d, p, view, alpha=230):
    q = [view.pt(x) for x in p]
    for a, b in BONES: d.line([q[a], q[b]], fill=(255, 255, 255, int(alpha * .75)), width=5)
    for j in (11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28):
        x, y = q[j]; d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=LIME + (alpha,), outline=(0, 0, 0, alpha), width=2)
    hx, hy = q[0]; d.ellipse((hx - 34, hy - 34, hx + 34, hy + 34), outline=LIME + (int(alpha * .8),), width=4)

def phase_of(t):
    if t < T_TAKEAWAY: return "ADDRESS"
    if t < 5.95: return "BACKSWING"
    if t < 6.07: return "TOP"
    if t < 6.215: return "DOWNSWING"
    if t < 6.33: return "IMPACT"
    if t < 6.62: return "FOLLOW-THRU"
    return "FINISH"

def hand_trail(d, t_now, view, alpha=255):
    pts = []; t = T_TAKEAWAY + 0.03
    while t <= t_now:
        fi = t * 30
        pts.append((t, view.pt(mid(pose_at(fi), 15, 16)))); t += 1 / 120
    for (t1, a), (t2, b) in zip(pts, pts[1:]):
        c = CYAN if t2 <= T_TOP + 0.04 else AMBER
        d.line([a, b], fill=c + (alpha,), width=9)
    if pts:
        x, y = pts[-1][1]; c = CYAN if t_now <= T_TOP + 0.04 else AMBER
        d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=c + (alpha,), outline=WHITE + (alpha,), width=3)

def vignette():
    v = Image.new("L", (W, H), 0); dv = ImageDraw.Draw(v)
    dv.rectangle((0, 0, W, 520), fill=150); dv.rectangle((0, H - 640, W, H), fill=170)
    v = v.filter(ImageFilter.GaussianBlur(160))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0)); out.putalpha(v); return out
VIG = vignette()

def brand(d, alpha=200):
    text(d, (W // 2, 70), "SWING CHECK  ·  AI BREAKDOWN", fSemi(28), fill=(255, 255, 255), anchor="mm", alpha=alpha)

# ---------- segments ----------
frames_out = []
def emit(fn, n):
    for k in range(n): frames_out.append((fn, k, n))

# S1 hook: real speed 5.0s..7.4s
def s1(k, n):
    i = 150 + k
    punch = 0
    if I_IMP <= i < I_IMP + 6: punch = (1 - (i - I_IMP) / 6) * 0.07
    v = View(1.18 + punch, 440, 1080)
    im = v.img(frame(i)).convert("RGBA"); im.alpha_composite(VIG)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    brand(d)
    u = ease(k / 10)
    y = lerp(-120, 0, u)
    text(d, (W // 2, 210 + y), "RATE SWING NI", fBlack(112), anchor="mm", alpha=int(255 * u))
    text(d, (W // 2, 310 + y), "berapa markah?", fBold(52), fill=LIME, anchor="mm", alpha=int(255 * u))
    chip(d, (60, H - 200), "REAL SPEED", fBold(34), alpha=int(230 * u))
    im.alpha_composite(o)
    if I_IMP <= i < I_IMP + 3:
        im.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(170 * (1 - (i - I_IMP) / 3)))))
    return im.convert("RGB")
emit(s1, 72)

# S2 slow-mo with skeleton, hand path, phase labels, stopwatch, impact hold
K_IMP = 1 + round((T_IMPACT - SLOW_T0) * 120)
HOLD = 18
SLOW_SEQ = list(range(1, K_IMP + 1)) + [K_IMP] * HOLD + list(range(K_IMP + 1, 206))
def s2(k, n):
    ks = SLOW_SEQ[k]; t = SLOW_T0 + (ks - 1) / 120; fi = t * 30
    u_all = k / n
    v = View(lerp(1.28, 1.42, ease(u_all)), 400, 1090)
    im = v.img(slow(ks)).convert("RGBA"); im.alpha_composite(VIG)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    p = pose_at(fi)
    fade_in = ease(k / 12)
    hand_trail(d, t, v, alpha=int(255 * fade_in))
    skeleton(d, p, v, alpha=int(230 * fade_in))
    brand(d)
    text(d, (W // 2, 190), "SLOW-MO", fBlack(96), anchor="mm")
    chip(d, (W // 2 - 70, 262), "0.25x SPEED", fBold(30), bg=WHITE)
    ph = phase_of(t)
    col = RED if ph == "IMPACT" else LIME
    panel(d, (60, H - 330, W - 60, H - 120), fill=(8, 12, 10, 205))
    text(d, (100, H - 300), "FASA", fSemi(30), fill=(180, 190, 185), shadow=False)
    text(d, (100, H - 252), ph, fBlack(68), fill=col, shadow=False)
    sw = max(0.0, t - T_TAKEAWAY)
    text(d, (W - 100, H - 300), "MASA", fSemi(30), fill=(180, 190, 185), anchor="ra", shadow=False)
    text(d, (W - 100, H - 258), f"{sw:0.2f}s", fBlack(78), anchor="ra", shadow=False)
    # legend
    d.line([(100, H - 150), (150, H - 150)], fill=CYAN, width=9)
    text(d, (165, H - 168), "backswing", fSemi(28), shadow=False)
    d.line([(370, H - 150), (420, H - 150)], fill=AMBER, width=9)
    text(d, (435, H - 168), "downswing", fSemi(28), shadow=False)
    im.alpha_composite(o)
    if K_IMP <= ks and k < K_IMP + HOLD:
        j = k - (K_IMP - 1)
        bx, by = v.pt((640, 1395))
        if j < 3: im.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - j / 3)))))
        if j < HOLD:
            r = 30 + j * 16; o2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(o2)
            a = int(255 * (1 - j / HOLD))
            d2.ellipse((bx - r, by - r, bx + r, by + r), outline=WHITE + (a,), width=8)
            text(d2, (W - 50, by - 190), "IMPACT!", fBlack(84), fill=RED, anchor="rm", alpha=max(a, 120))
            im.alpha_composite(o2)
    return im.convert("RGB")
emit(s2, len(SLOW_SEQ))

# Cards: freeze-frame analysis
def card_base(i, k, n, ghost=None, ghost_alpha=0):
    v = View(lerp(1.32, 1.44, ease(k / n)), 400, 1090)
    src = frame(i)
    if ghost is not None and ghost_alpha > 0:
        src = Image.blend(src, frame(ghost), ghost_alpha)
    im = v.img(src).convert("RGBA")
    im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 40))); im.alpha_composite(VIG)
    return v, im

def card_text(d, k, num, label, title, lines, score, col=LIME):
    u = ease(k / 9)
    brand(d)
    x = lerp(-300, 60, u)
    chip(d, (x + 22, 150), f"{num:02d}  {label}", fBold(34), bg=col, alpha=int(255 * u))
    text(d, (60, 230), title, fBlack(76 if len(title) < 18 else 64), fill=WHITE, alpha=int(255 * u))
    ub = ease((k - 6) / 10)
    if ub > 0:
        y0 = H - 400 + (1 - ub) * 80
        panel(d, (50, y0, W - 50, y0 + 300), fill=(8, 12, 10, int(215 * ub)))
        for j, s in enumerate(lines):
            text(d, (95, y0 + 40 + j * 66), s, fSemi(38), alpha=int(255 * ub), shadow=False)
        text(d, (W - 95, y0 + 300 - 40), score, fBlack(66), fill=col, anchor="rd", alpha=int(255 * ub), shadow=False)
        text(d, (95, y0 + 300 - 40), "markah", fSemi(28), fill=(170, 180, 175), anchor="ld", alpha=int(255 * ub), shadow=False)

CARD = 105
def angle_from_vertical(hip, sh): return math.degrees(math.atan2(sh[0] - hip[0], hip[1] - sh[1]))

def c1(k, n):  # SETUP
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
    card_text(d, k, 1, "SETUP", "POSTUR AGAK TEGAK",
              ["Spine tilt ~%d° - kurang hinge pinggul." % round(ang),
               "Tolak punggung ke belakang,", "lutut flex sikit, dada atas bola."], "6/10")
    im.alpha_composite(o); return im.convert("RGB")
emit(c1, CARD)

def c2(k, n):  # TOP
    v, im = card_base(I_TOP, k, n)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    ut = ease((k - 4) / 20)
    hand_trail(d, T_TAKEAWAY + (T_TOP - T_TAKEAWAY) * ut, v)
    p = POSE[I_TOP]; hx, hy = v.pt(p[0])
    ua = ease((k - 22) / 10)
    if ua > 0:
        d.ellipse((hx - 60, hy - 60, hx + 60, hy + 60), outline=LIME + (int(255 * ua),), width=6)
        text(d, (hx + 40, hy - 130), "kepala stabil", fBold(40), fill=LIME, alpha=int(255 * ua))
        hands, ch = v.pt((280, 756)), v.pt((430, 840))
        tip = (hands[0] + (ch[0] - hands[0]) * 3.2, hands[1] + (ch[1] - hands[1]) * 3.2)
        dashed(d, ch, (lerp(ch[0], tip[0], ua), lerp(ch[1], tip[1], ua)), AMBER + (255,), width=6)
        if ua > .7:
            text(d, (tip[0] - 10, tip[1] + 20), "across the line", fBold(40), fill=AMBER, anchor="ra")
            text(d, (tip[0] - 10, tip[1] + 70), "shaft tunjuk kanan target", fSemi(30), fill=WHITE, anchor="ra")
    card_text(d, k, 2, "TOP", "LEBAR & TINGGI",
              ["Arc lebar, kepala & pinggul stabil.",
               "Tapi kayu sikit 'across the line' -", "shaft tunjuk kanan target."], "7/10")
    im.alpha_composite(o); return im.convert("RGB")
emit(c2, CARD)

def c3(k, n):  # IMPACT - early extension
    ga = 0.42 * ease((k - 10) / 14)
    v, im = card_base(I_IMP, k, n, ghost=I_ADDR, ghost_alpha=ga)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    pa, pi = POSE[I_ADDR], POSE[I_IMP]
    ha, sa = mid(pa, 23, 24), mid(pa, 11, 12); hi, si = mid(pi, 23, 24), mid(pi, 11, 12)
    butt_a = min(pa[23][0], pa[24][0]) - 25
    u1 = ease((k - 8) / 12)
    top = v.pt((butt_a, 930)); bot = v.pt((butt_a, 1330))
    dashed(d, top, (top[0], lerp(top[1], bot[1], u1) + 1), WHITE + (235,), width=6)
    if u1 > .6: text(d, (top[0] + 20, top[1] - 14), "garis punggung (address)", fSemi(32), anchor="rb", alpha=int(255 * u1))
    u2 = ease((k - 18) / 12)
    A1, B1 = v.pt(ha), v.pt(sa); A2, B2 = v.pt(hi), v.pt(si)
    partial_line(d, A1, (B1[0] + (B1[0] - A1[0]) * .3, B1[1] + (B1[1] - A1[1]) * .3), u2, fill=WHITE + (230,), width=8)
    partial_line(d, A2, (B2[0] + (B2[0] - A2[0]) * .3, B2[1] + (B2[1] - A2[1]) * .3), u2, fill=RED + (255,), width=10)
    u3 = ease((k - 30) / 10)
    if u3 > 0:
        bi = v.pt((min(pi[23][0], pi[24][0]) - 10, 1150)); ba = v.pt((butt_a, 1150))
        arrow(d, (ba[0] - 10, ba[1]), (lerp(ba[0], bi[0] + 40, u3), bi[1]), RED + (255,), width=10)
        aa, ai = angle_from_vertical(ha, sa), angle_from_vertical(hi, si)
        text(d, (B2[0] + 60, B2[1] - 140), f"{aa:.0f}° → {ai:.0f}°", fBlack(64), fill=RED, alpha=int(255 * u3))
    card_text(d, k, 3, "IMPACT", "EARLY EXTENSION",
              ["Pinggul tertolak ke arah bola,", "badan 'berdiri' masa impact.",
               "Spine angle hilang ~10°."], "5/10", col=RED)
    if ga > 0: text(d, (W - 60, 330), "bayang = posisi address", fSemi(30), anchor="ra", alpha=int(255 * min(1, ga / .42)))
    im.alpha_composite(o); return im.convert("RGB")
emit(c3, CARD + 15)

def c4(k, n):  # FINISH
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
    card_text(d, k, 4, "FINISH", "FINISH SEIMBANG",
              ["Berat penuh ke kaki kiri,", "tali pinggang hadap target.",
               "Hold finish macam pro. Mantap!"], "8.5/10")
    im.alpha_composite(o); return im.convert("RGB")
emit(c4, CARD)

# Tempo card + rating card on blurred background
BG = None
def blurred_bg():
    global BG
    if BG is None:
        im = View(1.3, 400, 1090).img(frame(I_FIN)).filter(ImageFilter.GaussianBlur(28)).convert("RGBA")
        im.alpha_composite(Image.new("RGBA", (W, H), (6, 14, 9, 165))); BG = im
    return BG.copy()

BS, DS = T_TOP - T_TAKEAWAY, T_IMPACT - T_TOP
def c5(k, n):
    im = blurred_bg(); d = ImageDraw.Draw(im)
    u = ease(k / 10); brand(d)
    chip(d, (82, 170), "05  TEMPO", fBold(34), alpha=int(255 * u))
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
        for j, s in enumerate(["Pro biasanya ~3 : 1.", "Backswing laju sikit - slow down,", "biar badan habis pusing dulu."]):
            text(d, (100, 1335 + j * 68), s, fSemi(40), alpha=int(255 * ur), shadow=False)
    return im.convert("RGB")
emit(c5, CARD)

SCORES = [("Setup", 6.0, LIME), ("Backswing", 7.0, LIME), ("Impact", 5.0, RED), ("Tempo", 7.0, LIME), ("Finish", 8.5, LIME)]
OVERALL = 6.5
def c6(k, n):
    im = blurred_bg(); d = ImageDraw.Draw(im)
    u = ease(k / 10); brand(d)
    text(d, (W // 2, 200), "SWING RATING", fBlack(84), anchor="mm", alpha=int(255 * u))
    uo = ease((k - 4) / 30)
    val = OVERALL * uo
    text(d, (W // 2 - 30, 400), f"{val:0.1f}", fBlack(240), fill=LIME, anchor="rm", alpha=int(255 * u))
    text(d, (W // 2 - 10, 440), "/10", fBlack(110), anchor="lm", alpha=int(255 * u))
    if k > 34: chip(d, (W // 2 - 245, 560), "SOLID BASE - BOLEH NAIK LAGI", fBold(32), alpha=int(255 * ease((k - 34) / 8)))
    for j, (name, s, col) in enumerate(SCORES):
        y = 690 + j * 112; ub = ease((k - 10 - j * 5) / 16)
        text(d, (80, y), name, fBold(40), alpha=int(255 * ease((k - 10 - j * 5) / 6)), shadow=False)
        d.rounded_rectangle((80, y + 54, W - 80, y + 82), 14, fill=(255, 255, 255, 35))
        if ub > 0: d.rounded_rectangle((80, y + 54, 80 + max(28, (W - 160) * s / 10 * ub), y + 82), 14, fill=col)
        text(d, (W - 80, y), f"{s * ub:0.1f}", fBlack(44), fill=col, anchor="ra", alpha=int(255 * ease((k - 10 - j * 5) / 6)), shadow=False)
    uf = ease((k - 60) / 12)
    if uf > 0:
        y0 = 1300 + (1 - uf) * 100
        panel(d, (50, y0, W - 50, y0 + 470), fill=(8, 12, 10, int(225 * uf)), outline=RED + (int(255 * uf),), width=4)
        chip(d, (95, y0 + 40), "FIX NO.1", fBold(34), bg=RED, fg=WHITE, alpha=int(255 * uf))
        text(d, (95, y0 + 110), "Early extension", fBlack(62), alpha=int(255 * uf), shadow=False)
        for j, s in enumerate(["Drill: address dengan punggung", "sentuh dinding / kerusi. Kekalkan", "sentuhan sampai lepas impact."]):
            text(d, (95, y0 + 210 + j * 66), s, fSemi(40), alpha=int(255 * uf), shadow=False)
    return im.convert("RGB")
emit(c6, 200)

# ---------- encode ----------
print("total frames", len(frames_out), "duration %.2fs" % (len(frames_out) / FPS))
json.dump({"frames": len(frames_out), "s1": 72, "s2": len(SLOW_SEQ), "k_imp": K_IMP, "hold": HOLD},
          open(f"{D}/work/timeline.json", "w"))
only = sys.argv[2:]  # optional: frame numbers to dump as stills for preview
if only:
    for f in map(int, only):
        fn, k, n = frames_out[f]; fn(k, n).save(f"{D}/frames/prev_{f:04d}.jpg", quality=88)
    sys.exit()
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                       "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                       f"{D}/work/video.mp4"], stdin=subprocess.PIPE)
for idx, (fn, k, n) in enumerate(frames_out):
    ff.stdin.write(fn(k, n).tobytes())
    if idx % 100 == 0: print(idx, flush=True)
ff.stdin.close(); ff.wait()
print("done")
