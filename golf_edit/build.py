"""Render the workout-style edit of the 8-iron practice session.

usage: python3 build.py SRC_DIR OUT.mp4 [--work DIR]

SRC_DIR holds the original VID_*.mp4 clips from the Drive folder.
"""
import argparse
import math
import os
import subprocess
import wave
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.signal import butter, sosfilt

import music
from timeline import BAR, BEAT, CARRY, DRILL_HOLD, FPS, GOOD_CARRY, H, MOVEMENTS, SOURCES, W, build

FONT_DIR = "/usr/share/fonts/opentype/inter"
LIME = (200, 255, 46)
GREEN = (34, 197, 94)
RED = (239, 68, 68)
WHITE = (255, 255, 255)
PANEL = (12, 14, 18, 190)


def font(size, weight="Black", italic=False):
    name = f"InterDisplay-{weight}{'Italic' if italic else ''}.otf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F = {
    "label": font(34, "Bold"),
    "name": font(66, "Black", True),
    "rep_small": font(30, "Bold"),
    "rep_big": font(92, "Black", True),
    "title_kicker": font(56, "Bold"),
    "title_big": font(124, "Black", True),
    "chip": font(38, "Bold"),
    "carry": font(64, "Black", True),
    "timer": font(150, "Black", True),
    "row_name": font(50, "Black", True),
    "row_meta": font(34, "SemiBold"),
}


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_back(x):
    x = clamp(x)
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def text_w(d, s, f):
    l, _, r, _ = d.textbbox((0, 0), s, font=f)
    return r - l


def wrap(d, s, f, maxw):
    words, lines, cur = s.split(" "), [], ""
    for wd in words:
        cand = (cur + " " + wd).strip()
        if text_w(d, cand, f) <= maxw or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = wd
    lines.append(cur)
    return lines


def draw_check(d, cx, cy, r, color, width):
    pts = [(cx - 0.42 * r, cy + 0.02 * r), (cx - 0.12 * r, cy + 0.32 * r), (cx + 0.45 * r, cy - 0.3 * r)]
    d.line(pts, fill=color, width=width, joint="curve")
    for p in (pts[0], pts[2]):
        d.ellipse([p[0] - width / 2, p[1] - width / 2, p[0] + width / 2, p[1] + width / 2], fill=color)


def draw_cross(d, cx, cy, r, color, width):
    k = 0.34 * r
    for a, b in (((cx - k, cy - k), (cx + k, cy + k)), ((cx - k, cy + k), (cx + k, cy - k))):
        d.line([a, b], fill=color, width=width)
        for p in (a, b):
            d.ellipse([p[0] - width / 2, p[1] - width / 2, p[0] + width / 2, p[1] + width / 2], fill=color)


def badge(kind, r):
    """Round ✓ / ✗ badge, drawn 2x and downsampled for clean edges."""
    s = 2
    size = int(2 * r * 1.25 * s)
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = size / 2
    col = GREEN if kind == "ok" else RED
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([c - r * s * 1.12, c - r * s * 1.12, c + r * s * 1.12, c + r * s * 1.12], fill=col + (150,))
    im = Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(14 * s)))
    d = ImageDraw.Draw(im)
    d.ellipse([c - r * s, c - r * s, c + r * s, c + r * s], fill=col + (255,), outline=WHITE + (255,), width=int(7 * s))
    (draw_check if kind == "ok" else draw_cross)(d, c, c, r * s, WHITE + (255,), int(r * 0.2 * s))
    return im.resize((size // s, size // s), Image.LANCZOS)


BADGES = {k: badge(k, 120) for k in ("ok", "bad")}
SMALL_BADGES = {k: badge(k, 26) for k in ("ok", "bad")}


def paste_scaled(base, im, cx, cy, scale, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    w, h = im.size
    im2 = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.BILINEAR)
    if alpha < 1:
        a = im2.getchannel("A").point(lambda v: int(v * alpha))
        im2.putalpha(a)
    base.alpha_composite(im2, (int(cx - im2.width / 2), int(cy - im2.height / 2)))


def rounded(d, box, r, fill, outline=None, width=0):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


# ---------------------------------------------------------------- layers

def banner_layer(mi, right_label, right_value, dots=None):
    """Static top banner: movement number + name, plus a counter box on the right."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    mv = MOVEMENTS[mi]
    x0, y0, x1 = 48, 110, W - 48
    box_w = 230
    name_lines = wrap(d, mv["name"], F["name"], x1 - x0 - box_w - 80)
    y1 = y0 + 78 + 74 * len(name_lines) + (40 if dots else 14)
    rounded(d, (x0, y0, x1 - box_w - 16, y1), 28, PANEL)
    d.rectangle((x0, y0 + 24, x0 + 10, y1 - 24), fill=LIME)
    d.text((x0 + 40, y0 + 26), f"GERAKAN {mi + 1}/{len(MOVEMENTS)}", font=F["label"], fill=LIME)
    for i, ln in enumerate(name_lines):
        d.text((x0 + 38, y0 + 70 + 74 * i), ln, font=F["name"], fill=WHITE)
    if dots:
        n, cur = dots
        for i in range(n):
            cx, cy = x0 + 50 + i * 34, y1 - 30
            col = LIME if i < cur else (255, 255, 255, 90)
            d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=col)
    bx0 = x1 - box_w
    rounded(d, (bx0, y0, x1, y1), 28, LIME + (255,))
    tw = text_w(d, right_label, F["rep_small"])
    d.text((bx0 + (box_w - tw) / 2, y0 + 28), right_label, font=F["rep_small"], fill=(10, 10, 10))
    return im, (bx0, y0, x1, y1), right_value


def draw_counter(im, box, value, pulse):
    d = ImageDraw.Draw(im)
    bx0, y0, x1, y1 = box
    f = F["rep_big"]
    tw = text_w(d, value, f)
    l, t, r, b = d.textbbox((0, 0), value, font=f)
    cy = (y0 + 60 + y1) / 2
    d.text((bx0 + (x1 - bx0 - tw) / 2 - l, cy - (b - t) / 2 - t), value, font=f, fill=(10, 10, 10))
    if pulse > 0:
        rounded(d, (bx0 - 6, y0 - 6, x1 + 6, y1 + 6), 32, None, outline=WHITE + (int(255 * pulse),), width=6)


def chip(im, text, cx, cy, fill=PANEL, color=WHITE, f=None, alpha=1.0, dot=None):
    f = f or F["chip"]
    d = ImageDraw.Draw(im)
    tw = text_w(d, text, f)
    pad = 30
    extra = 34 if dot else 0
    w = tw + 2 * pad + extra
    h = f.size + 34
    fa = fill[:3] + (int((fill[3] if len(fill) > 3 else 255) * alpha),)
    rounded(d, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), h / 2, fa)
    if dot:
        d.ellipse((cx - w / 2 + pad - 2, cy - 11, cx - w / 2 + pad + 20, cy + 11), fill=dot + (int(255 * alpha),))
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    d.text((cx - w / 2 + pad + extra - l, cy - (b - t) / 2 - t), text, font=f, fill=color + (int(255 * alpha),))


def flash(im, a):
    if a > 0.01:
        im.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * a))))


def dim(im, a):
    if a > 0.01:
        im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * a))))


def bottom_gradient(h=700, a=0.75):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    arr = np.zeros((H, W, 4), np.uint8)
    ramp = (np.clip((np.arange(H) - (H - h)) / h, 0, 1) ** 1.5 * 255 * a).astype(np.uint8)
    arr[..., 3] = ramp[:, None]
    g = Image.fromarray(arr, "RGBA")
    return g


GRAD = bottom_gradient()


def beat_pulse(t):
    """1 on every beat, decaying over ~0.2 s (t is absolute timeline time)."""
    ph = (t % BEAT) / BEAT
    return math.exp(-ph * 6)


class Overlay:
    def __init__(self, segs, thumbs):
        self.segs = segs
        self.thumbs = thumbs
        self.cache = {}

    def static(self, key, fn):
        if key not in self.cache:
            self.cache[key] = fn()
        return self.cache[key]

    def frame(self, t):
        seg = next(s for s in reversed(self.segs) if s["t0"] <= t + 1e-9)
        lt = t - seg["t0"]
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        getattr(self, "f_" + seg["kind"])(im, seg, lt, t)
        return im

    # --- segment renderers
    def f_intro(self, im, s, lt, t):
        im.alpha_composite(GRAD)
        d = ImageDraw.Draw(im)
        a1 = ease_out((lt - 0.2) / 0.5)
        a2 = ease_out((lt - BEAT * 2) / 0.5)
        y = 1340 + 60 * (1 - a1)
        d.text((60, y), "SESI LATIHAN", font=F["title_kicker"], fill=LIME + (int(255 * a1),))
        for i, ln in enumerate(["GOLF", "WORKOUT"]):
            ai = ease_out((lt - 0.35 - 0.25 * i) / 0.5)
            d.text((54 - 80 * (1 - ai), 1410 + 128 * i), ln, font=F["title_big"], fill=WHITE + (int(255 * ai),))
        chip(im, "8 IRON  ·  4 GERAKAN", 60 + 250, 1720, fill=(255, 255, 255, 40), alpha=a2)
        flash(im, 0.6 * clamp(1 - (lt - s["impact"]) / 0.18) if lt >= s["impact"] else 0)

    def f_title(self, im, s, lt, t):
        mv = MOVEMENTS[s["mi"]]
        dim(im, 0.62 * ease_out(lt / 0.15))
        d = ImageDraw.Draw(im)
        a = ease_out(lt / 0.35)
        cy = 860
        kick = f"GERAKAN {s['mi'] + 1}"
        d.text((70 - 60 * (1 - a), cy - 150), kick, font=F["title_kicker"], fill=LIME + (int(255 * a),))
        fbig, lines = self.static(("title_font", s["mi"]), lambda: fit_title(d, mv["name"], W - 150))
        lh = int(fbig.size * 1.05)
        for i, ln in enumerate(lines):
            ai = ease_out((lt - 0.08 - 0.08 * i) / 0.35)
            d.text((64 + 90 * (1 - ai), cy - 70 + lh * i), ln, font=fbig, fill=WHITE + (int(255 * ai),))
        wipe = ease_out((lt - 0.25) / 0.5)
        yb = cy - 70 + lh * len(lines) + 30
        d.rectangle((70, yb, 70 + (W - 140) * wipe, yb + 12), fill=LIME)
        info = "TIMER" if mv.get("drill") else f"{len(mv['reps'])} REP"
        chip(im, info, 70 + 110, yb + 90, fill=(255, 255, 255, 46), alpha=ease_out((lt - 0.45) / 0.3))
        flash(im, 0.35 * clamp(1 - lt / 0.12))

    def _rep_common(self, im, s, lt, t):
        layer, box, val = self.static(("banner", s["mi"], s["rep"]), lambda: banner_layer(
            s["mi"], "REP", f"{s['rep']}/{s['nreps']}", dots=(s["nreps"], s["rep"])))
        im.alpha_composite(layer)
        draw_counter(im, box, val, 0.0)
        return box

    def _mark(self, im, s, appear_lt, lt):
        if not s.get("mark"):
            return
        p = (lt - appear_lt) / 0.35
        if p < 0:
            return
        cx, cy = W - 230, 760  # open sky / range, clear of the golfer
        paste_scaled(im, BADGES[s["mark"]], cx, cy, ease_back(p))
        if s.get("carry"):
            col = GREEN if s["mark"] == "ok" else RED
            chip(im, f"CARRY {s['carry']} yds", cx - 20, cy + 190, fill=(12, 14, 18, 210),
                 f=F["chip"], alpha=ease_out((lt - appear_lt - 0.15) / 0.3), dot=col)

    def f_rep(self, im, s, lt, t):
        box = self._rep_common(im, s, lt, t)
        imp = s["impact"]
        # counter pops on the impact beat
        if imp <= lt < imp + 0.3:
            draw_counter(im, box, "", 1 - (lt - imp) / 0.3)
        flash(im, 0.45 * clamp(1 - (lt - imp) / 0.12) if lt >= imp else 0)
        self._mark(im, s, imp + 0.55, lt)

    def f_slow(self, im, s, lt, t):
        box = self._rep_common(im, s, lt, t)
        chip(im, "SLOW-MO  0.5x", W / 2, 1680, fill=(12, 14, 18, 170), dot=LIME)
        self._mark(im, s, -10, lt)  # already shown, stays up during the replay

    def f_drill(self, im, s, lt, t):
        h0, h1 = s["hold"]
        held = clamp(lt - h0, 0, h1 - h0)
        layer, box, _ = self.static(("banner", s["mi"], "timer"), lambda: banner_layer(s["mi"], "TIMER", ""))
        im.alpha_composite(layer)
        draw_counter(im, box, f"{held:.1f}s", 0.0)
        d = ImageDraw.Draw(im)
        cx, cy, r = W / 2, 1360, 170
        a = ease_out((lt - (h0 - 0.4)) / 0.3)
        if a <= 0:
            chip(im, "BERSEDIA…", cx, cy, fill=(12, 14, 18, 190))
            return
        # ring timer that fills while the club is held at the top
        target = 2.0
        prog = held / target
        rounded(d, (cx - r - 30, cy - r - 30, cx + r + 30, cy + r + 30), r + 30, (12, 14, 18, int(170 * a)))
        d.arc((cx - r, cy - r, cx + r, cy + r), 0, 360, fill=(255, 255, 255, int(60 * a)), width=22)
        if prog > 0:
            d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * prog, fill=LIME + (int(255 * a),), width=22)
        txt = f"{held:.1f}"
        l, tp, rr, b = d.textbbox((0, 0), txt, font=F["timer"])
        d.text((cx - (rr - l) / 2 - l, cy - (b - tp) / 2 - tp - 18), txt, font=F["timer"], fill=WHITE + (int(255 * a),))
        sub = "SAAT" if lt < h1 else "SIAP"
        tw = text_w(d, sub, F["label"])
        d.text((cx - tw / 2, cy + 70), sub, font=F["label"], fill=LIME + (int(255 * a),))
        label = "TAHAN DI ATAS" if lt < h1 else "HAYUN TURUN"
        chip(im, label, cx, cy - r - 90, fill=LIME + (255,), color=(10, 10, 10), alpha=a)

    def f_monitor(self, im, s, lt, t):
        layer, box, _ = self.static(("banner", s["mi"], "data"), lambda: banner_layer(s["mi"], "DATA", ""))
        im.alpha_composite(layer)
        draw_counter(im, box, "#98", 0.0)
        d = ImageDraw.Draw(im)
        a = ease_out(lt / 0.3)
        x0, y0, x1 = 60, 1340, W - 60
        rows = [("#95", 133), ("#96", 147), ("#97", 107), ("#98", 150)]
        y1 = y0 + 90 + 76 * len(rows)
        rounded(d, (x0, y0 + 40 * (1 - a), x1, y1 + 40 * (1 - a)), 28, (12, 14, 18, int(215 * a)))
        oy = 40 * (1 - a)
        d.text((x0 + 36, y0 + 26 + oy), "LAUNCH MONITOR · 8 IRON · CARRY", font=F["label"], fill=LIME + (int(255 * a),))
        best = max(c for _, c in rows)
        for i, (shot, c) in enumerate(rows):
            ai = ease_out((lt - 0.15 - i * BEAT / 2) / 0.25) * a
            y = y0 + 92 + 76 * i + oy
            d.text((x0 + 36, y), shot, font=F["row_meta"], fill=(255, 255, 255, int(200 * ai)))
            bw = (x1 - x0 - 380) * c / best * ai
            col = GREEN if c >= GOOD_CARRY else RED
            rounded(d, (x0 + 130, y + 6, x0 + 130 + max(bw, 20), y + 44), 19, col + (int(255 * ai),))
            d.text((x1 - 210, y), f"{c} yds", font=F["row_meta"], fill=WHITE + (int(255 * ai),))
            sb = SMALL_BADGES["ok" if c >= GOOD_CARRY else "bad"]
            paste_scaled(im, sb, x1 - 50, y + 25, ai)

    def f_summary(self, im, s, lt, t):
        dim(im, 0.55)
        d = ImageDraw.Draw(im)
        a = ease_out(lt / 0.4)
        d.text((64, 150 - 40 * (1 - a)), "RINGKASAN", font=F["title_kicker"], fill=LIME + (int(255 * a),))
        d.text((58, 215 - 40 * (1 - a)), "SEMUA GERAKAN", font=font(96, "Black", True), fill=WHITE + (int(255 * a),))
        rows = summary_rows()
        y = 400
        rh = 290
        for i, (name, meta, marks) in enumerate(rows):
            ai = ease_out((lt - 0.3 - i * BEAT) / 0.35)
            if ai <= 0:
                continue
            ox = 80 * (1 - ai)
            yy = y + i * (rh + 26)
            rounded(d, (48 + ox, yy, W - 48 + ox, yy + rh), 30, (12, 14, 18, int(205 * ai)))
            th = self.thumbs[i]
            th2 = th.copy()
            th2.putalpha(th2.getchannel("A").point(lambda v: int(v * ai)))
            im.alpha_composite(th2, (int(70 + ox), int(yy + 22)))
            d = ImageDraw.Draw(im)
            tx = 70 + th.width + 34 + ox
            d.text((tx, yy + 34), f"{i + 1:02d}", font=F["label"], fill=LIME + (int(255 * ai),))
            nl = wrap(d, name, F["row_name"], W - 48 - tx - 30)
            for j, ln in enumerate(nl):
                d.text((tx, yy + 78 + 58 * j), ln, font=F["row_name"], fill=WHITE + (int(255 * ai),))
            my = yy + 86 + 58 * len(nl)
            for j, ln in enumerate(meta):
                d.text((tx, my + 44 * j), ln, font=F["row_meta"], fill=(220, 220, 220, int(255 * ai)))
            if marks:
                mx = tx
                for kind, n in marks:
                    paste_scaled(im, SMALL_BADGES[kind], mx + 26, yy + rh - 46, ai)
                    d.text((mx + 62, yy + rh - 68), f"× {n}", font=F["row_meta"], fill=WHITE + (int(255 * ai),))
                    mx += 170


def fit_title(d, name, maxw):
    """Largest title size (<=124 px) at which every wrapped line fits."""
    for size in range(124, 60, -4):
        f = font(size, "Black", True)
        lines = wrap(d, name, f, maxw)
        if all(text_w(d, ln, f) <= maxw for ln in lines):
            return f, lines
    return f, lines


def summary_rows():
    rows = []
    for mv in MOVEMENTS:
        if mv.get("drill"):
            rows.append((mv["short"], [f"Tahan di atas · {DRILL_HOLD[1] - DRILL_HOLD[0]:.1f} s"], None))
            continue
        n = len(mv["reps"])
        carries = [CARRY.get(k) for k in mv["reps"] if CARRY.get(k)]
        if carries:
            ok = sum(c >= GOOD_CARRY for c in carries)
            meta = [f"{n} rep · terbaik {max(carries)} yds carry"]
            rows.append((mv["short"], meta, [("ok", ok), ("bad", len(carries) - ok)]))
        else:
            rows.append((mv["short"], [f"{n} rep · slow-mo replay"], None))
    return rows


# ---------------------------------------------------------------- video

def run(cmd):
    subprocess.run(cmd, check=True)


def make_segment(src_dir, s, out):
    src = os.path.join(src_dir, s["src"])
    nframes = round((s["t0"] + s["dur"]) * FPS) - round(s["t0"] * FPS)
    if s["kind"] == "summary":
        vf = f"scale={W}:{H},boxblur=28:3,loop=loop={nframes}:size=1:start=0,setpts=N/{FPS}/TB"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['ss']:.3f}", "-i", src, "-vf", vf,
             "-frames:v", str(nframes), "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", str(FPS), out])
        return
    srcdur = s["dur"] * s["speed"] + 0.2
    vf = f"setpts=PTS/{s['speed']},fps={FPS},scale={W}:{H}:flags=lanczos,setsar=1"
    if s["kind"] == "slow":  # gentle push-in on the replay
        vf += f",scale={int(W * 1.08)}:{int(H * 1.08)},crop={W}:{H}"
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['ss']:.3f}", "-t", f"{srcdur:.3f}", "-i", src,
         "-vf", vf, "-frames:v", str(nframes), "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18",
         "-pix_fmt", "yuv420p", "-r", str(FPS), out])


def thumbs(src_dir, work):
    """Square-ish crops for the summary rows."""
    picks = [("VID_20261028_130606.mp4", SOURCES["dtl1"][1] - 0.6), ("VID_20261028_130630.mp4", SOURCES["fo1"][1] - 0.45),
             ("VID_20261028_142056.mp4", 52.0), ("VID_20261028_142056.mp4", SOURCES["s98"][1] + 0.7)]
    out = []
    for i, (f, t) in enumerate(picks):
        p = os.path.join(work, f"thumb{i}.png")
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", os.path.join(src_dir, f),
             "-frames:v", "1", "-vf", "scale=540:960", p])
        im = Image.open(p).convert("RGBA")
        im = im.crop((0, 120, 540, 120 + 700)).resize((190, 246), Image.LANCZOS)
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), 20, fill=255)
        im.putalpha(mask)
        out.append(im)
    return out


def club_sounds(src_dir, work, segs):
    """Real club-on-ball sound from each clip, placed on the real-time impact beat."""
    cache = {}
    sfx = []
    sos = butter(4, 2000, "high", fs=music.SR, output="sos")
    for s in segs:
        if s["kind"] != "rep":
            continue
        f, vis = SOURCES[s["key"]]
        if f not in cache:
            wav = os.path.join(work, f + ".wav")
            run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(src_dir, f), "-ac", "1", "-ar", str(music.SR), wav])
            with wave.open(wav) as w:
                cache[f] = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        x = cache[f]
        a, b = int((vis - 0.1) * music.SR), int((vis + 0.3) * music.SR)
        hpx = np.abs(sosfilt(sos, x[a:b]))
        pk = a + int(np.argmax(hpx))  # the audible click, slightly after the visual impact
        clip = x[pk - int(0.01 * music.SR): pk + int(0.35 * music.SR)].copy()
        clip *= np.linspace(1, 0, len(clip)) ** 2
        clip /= np.abs(clip).max() + 1e-9
        sfx.append((s["t0"] + s["impact"] + (pk / music.SR - vis) - 0.01, clip, 0.55))
    return sfx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--work", default="work")
    ap.add_argument("--reuse", action="store_true", help="keep already-rendered segments")
    args = ap.parse_args()
    os.makedirs(args.work, exist_ok=True)

    segs, total = build()
    parts = [os.path.join(args.work, f"seg{i:02d}_{s['kind']}.mp4") for i, s in enumerate(segs)]
    todo = [(s, p) for s, p in zip(segs, parts) if not (args.reuse and os.path.exists(p))]
    with ThreadPoolExecutor(3) as pool:
        list(pool.map(lambda sp: make_segment(args.src, *sp), todo))
    lst = os.path.join(args.work, "concat.txt")
    with open(lst, "w") as fh:
        fh.writelines(f"file '{os.path.abspath(p)}'\n" for p in parts)
    base = os.path.join(args.work, "base.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base])

    track = music.render(club_sounds(args.src, args.work, segs))
    mwav = os.path.join(args.work, "music.wav")
    with wave.open(mwav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(music.SR)
        w.writeframes((track * 32767).astype(np.int16).tobytes())

    ov = Overlay(segs, thumbs(args.src, args.work))
    nframes = int(round(total * FPS))
    proc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-i", base,
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", mwav,
        "-filter_complex", "[0:v][1:v]overlay=format=auto,format=yuv420p[v]",
        "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
        "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-t", f"{total:.3f}", "-movflags", "+faststart", args.out,
    ], stdin=subprocess.PIPE)
    for n in range(nframes):
        proc.stdin.write(ov.frame(n / FPS).tobytes())
        if n % 150 == 0:
            print(f"overlay {n}/{nframes}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("done", args.out)


if __name__ == "__main__":
    main()
