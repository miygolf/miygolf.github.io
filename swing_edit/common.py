"""Shared drawing + pose helpers for render.py and compare.py."""
import json, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30

# ---------- look ----------
F = "/usr/share/fonts/opentype/inter/"
def font(name, size): return ImageFont.truetype(F + name, size)
LIME = (198, 255, 61); WHITE = (255, 255, 255); RED = (255, 77, 77)
CYAN = (61, 214, 255); AMBER = (255, 176, 32); INK = (8, 12, 10)
COLORS = {"lime": LIME, "red": RED, "amber": AMBER, "cyan": CYAN, "white": WHITE}
fBlack = lambda s: font("InterDisplay-Black.otf", s)
fBold = lambda s: font("InterDisplay-Bold.otf", s)
fSemi = lambda s: font("Inter-SemiBold.otf", s)

# ---------- pose ----------
def load_pose(path):
    """MediaPipe landmarks (normalized) -> {frame: [(x_px, y_px)] * 33}, lightly smoothed over time."""
    raw = {int(k): v for k, v in json.load(open(path)).items()}
    n = max(raw) + 1
    out = {}
    for i in range(n):
        pts = []
        for j in range(33):
            acc = [0, 0]; wsum = 0
            for o, w in ((-1, 1), (0, 2), (1, 1)):
                k = min(max(i + o, 0), n - 1)
                acc[0] += raw[k][j][0] * w; acc[1] += raw[k][j][1] * w; wsum += w
            pts.append((acc[0] / wsum * W, acc[1] / wsum * H))
        out[i] = pts
    return out

def interp_pose(pose, fi):
    n = len(pose); fi = min(max(fi, 0), n - 1)
    a = int(math.floor(fi)); b = min(a + 1, n - 1); u = fi - a
    return [(pa[0] + (pb[0] - pa[0]) * u, pa[1] + (pb[1] - pa[1]) * u) for pa, pb in zip(pose[a], pose[b])]

def mid(p, a, b): return ((p[a][0] + p[b][0]) / 2, (p[a][1] + p[b][1]) / 2)
def angle_from_vertical(hip, sh): return math.degrees(math.atan2(sh[0] - hip[0], hip[1] - sh[1]))
def spine_angle(p): return angle_from_vertical(mid(p, 23, 24), mid(p, 11, 12))
def joint_angle(p, a, b, c):
    v1 = (p[a][0] - p[b][0], p[a][1] - p[b][1]); v2 = (p[c][0] - p[b][0], p[c][1] - p[b][1])
    return math.degrees(math.acos((v1[0] * v2[0] + v1[1] * v2[1]) / math.hypot(*v1) / math.hypot(*v2)))

# ---------- motion ----------
def ease(u): u = min(max(u, 0), 1); return 1 - (1 - u) ** 3
def lerp(a, b, u): return a + (b - a) * u

class View:
    """Zoomed crop of a full 1080x1920 frame, rendered to out_w x out_h."""
    def __init__(self, z, cx, cy, out_w=W, out_h=H):
        self.out = (out_w, out_h); self.z = z * out_w / W
        w, h = out_w / self.z, out_h / self.z
        self.x0 = min(max(cx - w / 2, 0), W - w); self.y0 = min(max(cy - h / 2, 0), H - h)
        self.w, self.h = w, h
    def img(self, im):
        return im.resize(self.out, Image.LANCZOS, box=(self.x0, self.y0, self.x0 + self.w, self.y0 + self.h))
    def pt(self, p): return ((p[0] - self.x0) * self.z, (p[1] - self.y0) * self.z)

# ---------- drawing ----------
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
    L = math.dist(a, b)
    if L < 1: return
    n = int(L // (dash + gap)) + 1
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    for k in range(n):
        s = k * (dash + gap); e = min(s + dash, L)
        d.line([(a[0] + ux * s, a[1] + uy * s), (a[0] + ux * e, a[1] + uy * e)], fill=fill, width=width)

def dashed_circle(d, c, r, fill, width=5, n=18):
    for k in range(n):
        a0 = 360 / n * k; d.arc((c[0] - r, c[1] - r, c[0] + r, c[1] + r), a0, a0 + 360 / n * .6, fill=fill, width=width)

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

def vignette(w=W, h=H, top=520, bottom=640):
    v = Image.new("L", (w, h), 0); dv = ImageDraw.Draw(v)
    dv.rectangle((0, 0, w, top), fill=150); dv.rectangle((0, h - bottom, w, h), fill=170)
    v = v.filter(ImageFilter.GaussianBlur(160))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); out.putalpha(v); return out
