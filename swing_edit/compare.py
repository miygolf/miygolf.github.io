"""Side-by-side comparison edit of two swings (1080x1920 @30fps).

Usage: python3 compare.py <compare.json> <workdir_left> <workdir_right> <outdir> [preview frame numbers...]
Each workdir is laid out as for render.py (all/, slow/, work/pose.json). Writes <outdir>/video.mp4 and
<outdir>/timeline.json (read by compare_audio.py).
"""
import glob, json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

CC = json.load(open(sys.argv[1]))
OUT = sys.argv[4]
PY, PW, PH = 330, 540, 960          # panel top, panel size
BG_COL = (11, 15, 13)

class Swing:
    def __init__(self, sc, wd, ox):
        self.c = json.load(open(sc["config"])); self.wd = wd; self.ox = ox
        self.label = sc["label"]; self.col = COLORS[sc["color"]]; self.crop = sc["crop"]
        c = self.c
        self.fps = c["src_fps"]; T = c["times"]
        self.take, self.top, self.imp = T["takeaway"], T["top"], T["impact"]
        self.fr = c["frames"]; self.ball = tuple(c["ball"])
        self.slow_t0, self.slow_fps = c["slow"]["t0"], c["slow"]["fps"]
        self.n_slow = len(glob.glob(f"{wd}/slow/s*.jpg"))
        self.pose = load_pose(f"{wd}/work/pose.json"); self.n = len(self.pose)
        self._cache = {}
        pa, pt, pi = (self.pose[self.fr[k]] for k in ("addr", "top", "imp"))
        self.torso = math.dist(mid(pa, 23, 24), mid(pa, 11, 12))
        butt = lambda p: min(p[23][0], p[24][0])
        self.m = {
            "spine_addr": spine_angle(pa), "spine_imp": spine_angle(pi),
            "head_move": math.dist(pa[0], pt[0]) / self.torso * 100,
            "hip_push": (butt(pi) - butt(pt)) / self.torso * 100,
            "head_drop": (pi[0][1] - pa[0][1]) / self.torso * 100,
            "bs": self.top - self.take, "ds": self.imp - self.top,
        }
        self.m["spine_loss"] = self.m["spine_addr"] - self.m["spine_imp"]
        self.m["ratio"] = self.m["bs"] / self.m["ds"]
    def view(self, zmul=1.0):
        return View(W / self.crop["w"] * zmul, self.crop["cx"], self.crop["cy"], PW, PH)
    def real(self, t):
        i = min(max(int(round(t * self.fps)), 0), self.n - 1)
        if i not in self._cache:
            if len(self._cache) > 8: self._cache.clear()
            self._cache[i] = Image.open(f"{self.wd}/all/f{i + 1:04d}.jpg").convert("RGB")
        return self._cache[i]
    def frame_idx(self, i): return self.real(i / self.fps)
    def slowimg(self, t):
        k = 1 + int(round((t - self.slow_t0) * self.slow_fps))
        if 1 <= k <= self.n_slow: return Image.open(f"{self.wd}/slow/s{k:04d}.jpg").convert("RGB")
        return self.real(t)
    def p(self, t): return interp_pose(self.pose, t * self.fps)
    def P(self, v, pt):  # source px -> canvas px
        x, y = v.pt(pt); return (x + self.ox, y + PY)

L = Swing(CC["left"], sys.argv[2], 0)
R = Swing(CC["right"], sys.argv[3], PW)
SW = (L, R)

def canvas(imgs):
    im = Image.new("RGBA", (W, H), BG_COL + (255,))
    for s, src in zip(SW, imgs): im.paste(src, (s.ox, PY))
    return im

TOPVIG = Image.new("RGBA", (W, H), (0, 0, 0, 0))
def frame_chrome(d, sub, k):
    text(d, (W // 2, 52), CC.get("brand", "SWING CHECK  ·  HEAD TO HEAD"), fSemi(26), anchor="mm", alpha=200)
    u = ease(k / 10)
    tl, tr = L.label, R.label
    f = fBlack(100)
    wl = ImageDraw.Draw(Image.new("L", (1, 1))).textlength(tl, font=f); wv = ImageDraw.Draw(Image.new("L", (1, 1))).textlength(" vs ", font=fBlack(60))
    wr = ImageDraw.Draw(Image.new("L", (1, 1))).textlength(tr, font=f)
    x0 = W / 2 - (wl + wv + wr) / 2
    text(d, (x0, 160), tl, f, fill=L.col, anchor="lm", alpha=int(255 * u))
    text(d, (x0 + wl + wv / 2, 168), "vs", fBlack(60), anchor="mm", alpha=int(255 * u))
    text(d, (x0 + wl + wv, 160), tr, f, fill=R.col, anchor="lm", alpha=int(255 * u))
    if sub: text(d, (W // 2, 262), sub, fBold(40), anchor="mm", alpha=int(255 * u))
    # panel labels + divider
    d.rectangle((PW - 2, PY, PW + 2, PY + PH), fill=(255, 255, 255, 230))
    for s in SW:
        chip(d, (s.ox + 34, PY + 30), s.label, fBold(32), bg=s.col, alpha=240)

def skeleton(d, s, v, p, alpha=230):
    q = [s.P(v, x) for x in p]
    for a, b in BONES: d.line([q[a], q[b]], fill=(255, 255, 255, int(alpha * .7)), width=4)
    for j in (11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28):
        x, y = q[j]; d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=s.col + (alpha,), outline=(0, 0, 0, alpha), width=2)
    hx, hy = q[0]; d.ellipse((hx - 24, hy - 24, hx + 24, hy + 24), outline=s.col + (int(alpha * .8),), width=3)

def hand_trail(d, s, v, t_now, alpha=255):
    pts = []; t = s.take + 0.03
    while t <= t_now: pts.append(s.P(v, mid(s.p(t), 15, 16))); t += 1 / 120
    if len(pts) > 1: d.line(pts, fill=s.col + (alpha,), width=6, joint="curve")
    if pts:
        x, y = pts[-1]; d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=s.col + (alpha,), outline=WHITE + (alpha,), width=2)

frames_out = []; marks = {}
def emit(name, fn, n):
    marks[name] = len(frames_out)
    for k in range(n): frames_out.append((fn, k, n))

# ---------- A: real speed, synced at impact ----------
RT_PRE, RT_POST = 1.3, 1.1
N_RT = int(round((RT_PRE + RT_POST) * FPS))
def seg_real(k, n):
    dt = -RT_PRE + k / FPS
    punch = (1 - dt / 0.2) * 0.06 if 0 <= dt < 0.2 else 0
    views = [s.view(1 + punch) for s in SW]
    im = canvas([v.img(s.real(s.imp + dt)) for s, v in zip(SW, views)])
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    frame_chrome(d, CC["intro_sub"], k)
    chip(d, (W // 2 - 95, PY + PH + 60), "REAL SPEED", fBold(34), alpha=int(230 * ease(k / 10)))
    text(d, (W // 2, PY + PH + 190), "disegerakkan masa impact", fSemi(34), anchor="mm", alpha=int(220 * ease((k - 10) / 10)))
    im.alpha_composite(o)
    if 0 <= dt < 0.1:
        fl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(fl).rectangle((0, PY, W, PY + PH), fill=(255, 255, 255, int(170 * (1 - dt / 0.1))))
        im.alpha_composite(fl)
    return im.convert("RGB")
emit("real", seg_real, N_RT)

# ---------- B: slow-mo, phase-synced (both reach takeaway/top/impact together) ----------
PRE, POST = 0.13, 0.44
def keys(s): return [s.take - PRE, s.take, s.top, s.imp, s.imp + POST]
SEGS = [max(kl[i + 1] - kl[i], kr[i + 1] - kr[i]) for kl, kr in [(keys(L), keys(R))] for i in range(4)]
BOUND = [0];
for x in SEGS: BOUND.append(BOUND[-1] + x)
SLOW_RATE = 120                      # common-timeline samples per second -> 0.25x at 30fps
N_SL = int(BOUND[-1] * SLOW_RATE); HOLD = 18
F_IMP = int(BOUND[3] * SLOW_RATE)
PHASE_NAMES = ["ADDRESS", "BACKSWING", "DOWNSWING", "FOLLOW-THRU"]
def src_time(s, tau):
    ks = keys(s)
    for i in range(4):
        if tau <= BOUND[i + 1] or i == 3:
            u = (tau - BOUND[i]) / (BOUND[i + 1] - BOUND[i]); return lerp(ks[i], ks[i + 1], min(max(u, 0), 1)), i
SL_SEQ = list(range(0, F_IMP + 1)) + [F_IMP] * HOLD + list(range(F_IMP + 1, N_SL))
def seg_slow(k, n):
    f = SL_SEQ[k]; tau = f / SLOW_RATE
    j = k - F_IMP
    views = [s.view(lerp(1.0, 1.08, ease(k / n))) for s in SW]
    ts = [src_time(s, tau)[0] for s in SW]; ph = src_time(L, tau)[1]
    name = PHASE_NAMES[ph]
    if abs(tau - BOUND[2]) < 0.025: name = "TOP"
    if 0 <= j < HOLD + 6: name = "IMPACT"
    im = canvas([v.img(s.slowimg(t)) for s, v, t in zip(SW, views, ts)])
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    a = int(255 * ease(k / 12))
    for s, v, t in zip(SW, views, ts):
        hand_trail(d, s, v, t, alpha=a); skeleton(d, s, v, s.p(t), alpha=int(230 * a / 255))
    frame_chrome(d, "SLOW-MO 0.25x  ·  fasa disegerakkan", k)
    yb = PY + PH
    text(d, (W // 2, yb + 95), name, fBlack(84), fill=RED if name == "IMPACT" else WHITE, anchor="mm")
    for s, t in zip(SW, ts):
        cx = s.ox + PW // 2
        panel(d, (s.ox + 40, yb + 170, s.ox + PW - 40, yb + 470), fill=(255, 255, 255, 18), outline=s.col + (120,), width=3)
        text(d, (cx, yb + 215), s.label, fBold(34), fill=s.col, anchor="mm", shadow=False)
        text(d, (cx, yb + 300), f"{spine_angle(s.p(t)):.0f}°", fBlack(84), anchor="mm", shadow=False)
        text(d, (cx, yb + 360), "spine tilt", fSemi(28), fill=(180, 190, 185), anchor="mm", shadow=False)
        text(d, (cx, yb + 425), f"{max(0, t - s.take):0.2f}s", fBold(40), anchor="mm", shadow=False)
    im.alpha_composite(o)
    if 0 <= j < HOLD:
        o2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(o2)
        if j < 3: d2.rectangle((0, PY, W, PY + PH), fill=(255, 255, 255, int(190 * (1 - j / 3))))
        for s, v in zip(SW, views):
            bx, by = s.P(v, s.ball); r = 20 + j * 10
            d2.ellipse((bx - r, by - r, bx + r, by + r), outline=WHITE + (int(255 * (1 - j / HOLD)),), width=6)
        im.alpha_composite(o2)
    return im.convert("RGB")
emit("slow", seg_slow, len(SL_SEQ))

# ---------- C: freeze-frame comparison cards ----------
def verdict(d, k, cd, yb):
    w = cd["winner"]
    col = L.col if w == "left" else R.col if w == "right" else WHITE
    lbl = f"MENANG: {L.label}" if w == "left" else f"MENANG: {R.label}" if w == "right" else "SERI"
    u = ease((k - 34) / 8)
    if u > 0:
        f = fBlack(46); tw = d.textlength(lbl, font=f)
        chip(d, (W / 2 - tw / 2, yb + 395), lbl, f, bg=col, fg=INK, alpha=int(255 * u), pad=(30, 14))
        for i, line in enumerate(cd["lines"]):
            text(d, (W // 2, yb + 505 + i * 50), line, fSemi(34), anchor="mm", alpha=int(255 * u), shadow=False)

def stat_rows(d, k, rows, yb):
    for i, (name, lv, rv) in enumerate(rows):
        u = ease((k - 10 - i * 6) / 10); y = yb + 70 + i * 150
        if u <= 0: continue
        text(d, (W // 2, y), name, fSemi(32), fill=(180, 190, 185), anchor="mm", alpha=int(255 * u), shadow=False)
        text(d, (PW // 2, y + 70), lv, fBlack(72), fill=L.col, anchor="mm", alpha=int(255 * u), shadow=False)
        text(d, (PW + PW // 2, y + 70), rv, fBlack(72), fill=R.col, anchor="mm", alpha=int(255 * u), shadow=False)

def card(kind, cd):
    def fn(k, n):
        fi = {"setup": "addr", "top": "top", "impact": "imp", "finish": "fin"}[kind]
        views = [s.view(lerp(1.0, 1.06, ease(k / n))) for s in SW]
        ga = 0.42 * ease((k - 10) / 14) if kind == "impact" else 0
        imgs = []
        for s, v in zip(SW, views):
            src = s.frame_idx(s.fr[fi])
            if ga: src = Image.blend(src, s.frame_idx(s.fr["addr"]), ga)
            imgs.append(v.img(src))
        im = canvas(imgs)
        dk = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(dk).rectangle((0, PY, W, PY + PH), fill=(0, 0, 0, 45)); im.alpha_composite(dk)
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
        ua = ease((k - 8) / 14)
        for s, v in zip(SW, views):
            p = s.pose[s.fr[fi]]; pa = s.pose[s.fr["addr"]]
            if kind == "setup":
                Hp, Sp = s.P(v, mid(p, 23, 24)), s.P(v, mid(p, 11, 12))
                ext = (Sp[0] + (Sp[0] - Hp[0]) * .35, Sp[1] + (Sp[1] - Hp[1]) * .35)
                dashed(d, Hp, (Hp[0], Hp[1] - 260 * ua + 1), WHITE + (220,), width=4, dash=16, gap=10)
                partial_line(d, Hp, ext, ua, fill=s.col + (255,), width=7)
                if ua > .6: text(d, (Hp[0] + 60, Hp[1] - 190), f"{spine_angle(p):.0f}°", fBlack(56), fill=s.col)
            elif kind == "top":
                hand_trail(d, s, v, s.take + (s.top - s.take) * ease((k - 4) / 20))
                if ua > 0:
                    dashed_circle(d, s.P(v, pa[0]), 40, WHITE + (int(220 * ua),), width=4)
                    hx, hy = s.P(v, p[0]); d.ellipse((hx - 40, hy - 40, hx + 40, hy + 40), outline=s.col + (int(255 * ua),), width=5)
            elif kind == "impact":
                butt_a = min(pa[23][0], pa[24][0]) - 20
                hy = mid(pa, 23, 24)[1]
                top_, bot_ = s.P(v, (butt_a, hy - 160)), s.P(v, (butt_a, hy + 200))
                dashed(d, top_, (top_[0], lerp(top_[1], bot_[1], ua) + 1), WHITE + (235,), width=4, dash=16, gap=10)
                u2 = ease((k - 18) / 12)
                for pp, c, wd in ((pa, WHITE, 5), (p, s.col, 7)):
                    A_, B_ = s.P(v, mid(pp, 23, 24)), s.P(v, mid(pp, 11, 12))
                    partial_line(d, A_, (B_[0] + (B_[0] - A_[0]) * .3, B_[1] + (B_[1] - A_[1]) * .3), u2, fill=c + (255,), width=wd)
            elif kind == "finish":
                if ua > 0:
                    lf, hd = s.P(v, p[27]), s.P(v, p[0])
                    dashed(d, (lf[0], lf[1] + 20), (lf[0], lerp(lf[1] + 20, hd[1] - 40, ua)), s.col + (240,), width=5, dash=16, gap=10)
        frame_chrome(d, None, 99)
        u = ease(k / 9)
        chip(d, (lerp(-200, 60, u), 236), f"{cd['num']:02d}  {cd['label']}", fBold(32), alpha=int(255 * u))
        text(d, (W - 60, 256), cd["title"], fBlack(48), anchor="rm", alpha=int(255 * u))
        if kind == "impact" and ga: text(d, (W // 2, PY + PH - 34), "bayang = posisi address", fSemi(28), anchor="mm", alpha=int(255 * ga / .42))
        stat_rows(d, k, cd["rows"], PY + PH)
        verdict(d, k, cd, PY + PH)
        im.alpha_composite(o)
        return im.convert("RGB")
    return fn

def fmt_rows(rows):
    out = []
    for name, key, unit, dec in rows:
        out.append((name, f"{L.m[key]:.{dec}f}{unit}", f"{R.m[key]:.{dec}f}{unit}"))
    return out

for i, cd in enumerate(CC["cards"]):
    cd["num"] = i + 1
    cd["rows"] = fmt_rows(cd["stats"]) if "stats" in cd else [tuple(r) for r in cd["rows_text"]]
    emit(f"card{i + 1}", card(cd["type"], cd), 120)

# ---------- D: tempo ----------
def blur_bg():
    im = Image.new("RGBA", (W, H), BG_COL + (255,))
    for s in SW: im.paste(s.view().img(s.frame_idx(s.fr["fin"])), (s.ox, PY))
    im = im.filter(ImageFilter.GaussianBlur(26))
    im.alpha_composite(Image.new("RGBA", (W, H), (6, 14, 9, 175)))
    return im.convert("RGB")
BLUR = blur_bg()
TEMPO = CC["tempo"]
def seg_tempo(k, n):
    im = BLUR.copy(); d = ImageDraw.Draw(im, "RGBA"); u = ease(k / 10)
    text(d, (W // 2, 52), CC.get("brand", "SWING CHECK  ·  HEAD TO HEAD"), fSemi(26), anchor="mm", alpha=200)
    chip(d, (82, 150), f"{len(CC['cards']) + 1:02d}  TEMPO", fBold(32), alpha=int(255 * u))
    text(d, (60, 230), "SIAPA LEBIH SANTAI?", fBlack(70), alpha=int(255 * u))
    for i, s in enumerate(SW):
        y = 400 + i * 470; ub = ease((k - 8 - i * 10) / 16)
        text(d, (80, y), s.label, fBlack(56), fill=s.col, alpha=int(255 * u), shadow=False)
        text(d, (W - 80, y + 4), f"{s.m['ratio']:.1f} : 1", fBlack(72), fill=s.col, anchor="ra", alpha=int(255 * ease((k - 30 - i * 10) / 10)), shadow=False)
        for j, (nm, val, c) in enumerate((("Backswing", s.m["bs"], CYAN), ("Downswing", s.m["ds"], AMBER))):
            yy = y + 120 + j * 140
            text(d, (80, yy), nm, fBold(36), alpha=int(255 * u), shadow=False)
            text(d, (W - 80, yy), f"{val * ub:.2f}s", fBlack(40), fill=c, anchor="ra", alpha=int(255 * u), shadow=False)
            d.rounded_rectangle((80, yy + 55, W - 80, yy + 95), 20, fill=(255, 255, 255, 30))
            if ub > 0: d.rounded_rectangle((80, yy + 55, 80 + max(40, (W - 160) * val / 0.7 * ub), yy + 95), 20, fill=c)
    verdict(d, k, TEMPO, 1180)
    return im.convert("RGB")
emit("tempo", seg_tempo, 120)

# ---------- E: scorecard ----------
SC = CC["scorecard"]
def seg_score(k, n):
    im = BLUR.copy(); d = ImageDraw.Draw(im, "RGBA"); u = ease(k / 10)
    text(d, (W // 2, 52), CC.get("brand", "SWING CHECK  ·  HEAD TO HEAD"), fSemi(26), anchor="mm", alpha=200)
    text(d, (W // 2, 170), "SCORECARD", fBlack(96), anchor="mm", alpha=int(255 * u))
    cx = {"name": 90, "l": 690, "r": 920}
    text(d, (cx["l"], 300), L.label, fBlack(46), fill=L.col, anchor="mm", alpha=int(255 * u), shadow=False)
    text(d, (cx["r"], 300), R.label, fBlack(46), fill=R.col, anchor="mm", alpha=int(255 * u), shadow=False)
    for i, (name, lv, rv) in enumerate(SC["rows"]):
        y = 400 + i * 120; ur = ease((k - 8 - i * 6) / 10)
        if ur <= 0: continue
        d.rounded_rectangle((60, y - 48, W - 60, y + 48), 22, fill=(255, 255, 255, int(16 * ur)))
        text(d, (cx["name"], y), name, fBold(44), anchor="lm", alpha=int(255 * ur), shadow=False)
        for x, val, other, s in ((cx["l"], lv, rv, L), (cx["r"], rv, lv, R)):
            win = val > other
            if win: d.rounded_rectangle((x - 85, y - 38, x + 85, y + 38), 19, fill=s.col + (int(255 * ur),))
            text(d, (x, y), f"{val:.1f}", fBlack(52), fill=INK if win else (230, 235, 232), anchor="mm", alpha=int(255 * ur), shadow=False)
    yo = 400 + len(SC["rows"]) * 120 + 40; uo = ease((k - 50) / 14)
    if uo > 0:
        lo, ro = SC["overall"]
        d.line([(60, yo - 40), (W - 60, yo - 40)], fill=(255, 255, 255, int(120 * uo)), width=2)
        text(d, (cx["name"], yo + 40), "OVERALL", fBlack(56), anchor="lm", alpha=int(255 * uo), shadow=False)
        text(d, (cx["l"], yo + 40), f"{lo * uo:.1f}", fBlack(84), fill=L.col, anchor="mm", alpha=int(255 * uo), shadow=False)
        text(d, (cx["r"], yo + 40), f"{ro * uo:.1f}", fBlack(84), fill=R.col, anchor="mm", alpha=int(255 * uo), shadow=False)
    uw = ease((k - 78) / 10)
    if uw > 0:
        win = L if SC["overall"][0] > SC["overall"][1] else R
        lbl = f"{win.label} MENANG!"
        f = fBlack(80); tw = d.textlength(lbl, font=f)
        y = 1560 + (1 - uw) * 60
        chip(d, (W / 2 - tw / 2, y), lbl, f, bg=win.col, alpha=int(255 * uw), pad=(44, 22))
        text(d, (W // 2, y + 170), SC["sub"], fSemi(36), anchor="mm", alpha=int(255 * uw), shadow=False)
    return im.convert("RGB")
emit("score", seg_score, 170)

# ---------- F: what each can learn ----------
LN = CC["learn"]
def seg_learn(k, n):
    im = BLUR.copy(); d = ImageDraw.Draw(im, "RGBA"); u = ease(k / 10)
    text(d, (W // 2, 52), CC.get("brand", "SWING CHECK  ·  HEAD TO HEAD"), fSemi(26), anchor="mm", alpha=200)
    text(d, (W // 2, 180), "SALING BELAJAR", fBlack(92), anchor="mm", alpha=int(255 * u))
    boxes = [(L.col, LN["left_title"], LN["left_lines"]), (R.col, LN["right_title"], LN["right_lines"]), (WHITE, LN["both_title"], LN["both_lines"])]
    for i, (col, title, lines) in enumerate(boxes):
        ub = ease((k - 8 - i * 14) / 12)
        if ub <= 0: continue
        y0 = 320 + i * 450 + (1 - ub) * 60
        panel(d, (50, y0, W - 50, y0 + 400), fill=(8, 12, 10, int(220 * ub)), outline=col + (int(255 * ub),), width=4)
        text(d, (95, y0 + 45), title, fBlack(52), fill=col, alpha=int(255 * ub), shadow=False)
        for j, s in enumerate(lines):
            text(d, (95, y0 + 145 + j * 62), s, fSemi(40), alpha=int(255 * ub), shadow=False)
    return im.convert("RGB")
emit("learn", seg_learn, 165)

# ---------- encode ----------
print("total frames", len(frames_out), "duration %.2fs" % (len(frames_out) / FPS))
for s in SW: print(s.label, {k: round(v, 2) for k, v in s.m.items()})
os.makedirs(OUT, exist_ok=True)
json.dump({"frames": len(frames_out), "marks": marks, "rt_pre": RT_PRE, "f_imp": F_IMP, "hold": HOLD,
           "left": {"impact": L.imp}, "right": {"impact": R.imp}}, open(f"{OUT}/timeline.json", "w"), indent=1)
only = sys.argv[5:]
if only:
    for f in map(int, only):
        fn, k, n = frames_out[f]; fn(k, n).save(f"{OUT}/prev_{f:04d}.jpg", quality=88)
    sys.exit()
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                       "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                       f"{OUT}/video.mp4"], stdin=subprocess.PIPE)
for idx, (fn, k, n) in enumerate(frames_out):
    ff.stdin.write(fn(k, n).tobytes())
    if idx % 200 == 0: print(idx, flush=True)
ff.stdin.close(); ff.wait()
print("done")
