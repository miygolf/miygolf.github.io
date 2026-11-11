import subprocess, math, json, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SRC = "../src/in.mov"
BASE = "base.mp4"
segs = json.load(open("segs.json"))
BASE_DUR = segs[-1]["out_start"] + segs[-1]["dur"]
END_DUR = 2.7
TOTAL = BASE_DUR + END_DUR
NFR = int(round(TOTAL * FPS))
IMPACT_A = 3.87
IMPACT_B = 9.98
CUT = 5.8            # switch to swing #2
HOLD0, HOLD1 = 7.6667, 9.5333   # pause at the top of swing #2

F_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
F_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
F_XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
F_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
LIME = (215, 255, 58)
INK = (14, 18, 12)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- text
_emoji_font = ImageFont.truetype(F_EMOJI, 109)

def is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF

def emoji_img(ch, size):
    im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=_emoji_font, embedded_color=True)
    im = im.crop(im.getbbox())
    s = size / im.height
    return im.resize((max(1, int(im.width * s)), size), Image.LANCZOS)

def text_line(s, font_path, size, fill, stroke=0, stroke_fill=INK, shadow=True):
    font = ImageFont.truetype(font_path, size)
    parts = []  # (img, is_emoji)
    buf = ""
    def flush():
        nonlocal buf
        if buf:
            bb = font.getbbox(buf, stroke_width=stroke)
            asc, desc = font.getmetrics()
            w = bb[2] + stroke * 2
            im = Image.new("RGBA", (w, asc + desc + stroke * 2), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((stroke, stroke), buf, font=font, fill=fill,
                                    stroke_width=stroke, stroke_fill=stroke_fill)
            parts.append(im)
            buf = ""
    for ch in s:
        if is_emoji(ch):
            flush()
            asc, desc = font.getmetrics()
            e = emoji_img(ch, int(size * 0.92))
            pad = Image.new("RGBA", (e.width + int(size * 0.12), asc + desc + stroke * 2), (0, 0, 0, 0))
            pad.alpha_composite(e, (int(size * 0.12), max(0, int((asc + desc) * 0.5 - e.height * 0.5) + stroke)))
            parts.append(pad)
        else:
            buf += ch
    flush()
    w = sum(p.width for p in parts)
    h = max(p.height for p in parts)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = 0
    for p in parts:
        im.alpha_composite(p, (x, 0)); x += p.width
    im = im.crop(im.getbbox())
    if shadow:
        pad = 24
        out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
        a = im.split()[3].point(lambda v: int(v * 0.55))
        sh = Image.new("RGBA", im.size, (0, 0, 0, 255)); sh.putalpha(a)
        out.alpha_composite(sh, (pad + 4, pad + 9))
        out = out.filter(ImageFilter.GaussianBlur(7))
        out.alpha_composite(im, (pad, pad))
        im = out
    return im

def stack(imgs, gap=-10):
    w = max(i.width for i in imgs); h = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); y = 0
    for i in imgs:
        out.alpha_composite(i, ((w - i.width) // 2, y)); y += i.height + gap
    return out

def pill(s, size=46, bg=LIME, fg=INK, padx=30, pady=16):
    t = text_line(s, F_XB, size, fg, shadow=False)
    w, h = t.width + padx * 2, t.height + pady * 2
    im = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((15, 21, 15 + w, 21 + h), radius=h // 2, fill=(0, 0, 0, 110))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(im).rounded_rectangle((15, 15, 15 + w, 15 + h), radius=h // 2, fill=bg)
    im.alpha_composite(t, (15 + padx, 15 + pady))
    return im

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out_back(x):
    c1, c3 = 1.9, 2.9
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def ease_out(x): return 1 - (1 - x) ** 3
def ease_in_out(x): return 3 * x * x - 2 * x * x * x

class Layer:
    """A text/graphic that pops in (scale overshoot) and fades out."""
    def __init__(self, img, cx, cy, t0, t1, pop=0.28, fade=0.14, wobble=0.0, anchor="center", slide=0):
        self.img, self.cx, self.cy, self.t0, self.t1 = img, cx, cy, t0, t1
        self.pop, self.fade, self.wobble, self.anchor, self.slide = pop, fade, wobble, anchor, slide
    def draw(self, frame, t):
        if t < self.t0 or t > self.t1: return
        p = clamp((t - self.t0) / self.pop)
        s = 0.55 + 0.45 * ease_out_back(p) if not self.slide else 1.0
        a = clamp((t - self.t0) / 0.07) * clamp((self.t1 - t) / self.fade)
        if self.wobble:
            s *= 1 + self.wobble * math.sin((t - self.t0) * 9)
        img = self.img
        if abs(s - 1) > 0.003:
            img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BICUBIC)
        if a < 1:
            img = img.copy(); img.putalpha(img.split()[3].point(lambda v: int(v * a)))
        x = self.cx - img.width // 2 if self.anchor == "center" else self.cx
        if self.slide:
            x += int(self.slide * (1 - ease_out(p)))
        frame.alpha_composite(img, (int(x), int(self.cy - img.height // 2)))

# ---------------------------------------------------------------- layers
layers = []
# Hook
hook = stack([text_line("FIRST TIME", F_BLACK, 132, WHITE, stroke=6),
              text_line("MAIN GOLF ⛳", F_BLACK, 132, LIME, stroke=6)], gap=-18)
layers.append(Layer(hook, W // 2, 430, 0.12, 2.75, pop=0.32))
layers.append(Layer(pill("hari pertama. zero experience.", 38, bg=(255, 255, 255), fg=INK), W // 2, 640, 0.55, 2.75))
# Swing labels
layers.append(Layer(pill("SWING #1", 40), 70, 200, 2.85, 5.75, slide=-260, anchor="left"))
layers.append(Layer(pill("SWING #2", 40), 70, 200, CUT, 11.7, slide=-260, anchor="left"))
# Impact A
contact = text_line("CONTACT!", F_BLACK, 150, LIME, stroke=7)
layers.append(Layer(contact, W // 2, 375, IMPACT_A, 5.0, pop=0.22, wobble=0.015))
layers.append(Layer(text_line("eh, boleh tahan 👀", F_BLACK, 86, WHITE, stroke=5), W // 2, 375, 5.02, 5.78))
# Loading bit
layers.append(Layer(text_line("loading swing...", F_BLACK, 96, WHITE, stroke=5), W // 2, 400, HOLD0 + 0.05, HOLD1 + 0.05))
layers.append(Layer(text_line("(masih loading)", F_XB, 52, (235, 235, 235), stroke=3), 800, 650, HOLD0 + 1.05, HOLD1 + 0.02))
# Impact B
sent = text_line("SENT IT! 🚀", F_BLACK, 146, LIME, stroke=7)
layers.append(Layer(sent, W // 2, 375, IMPACT_B, 10.85, pop=0.22, wobble=0.015))
layers.append(Layer(text_line("DAY 1: DONE ✅", F_BLACK, 96, WHITE, stroke=5), W // 2, 375, 10.9, BASE_DUR + 0.25))
# End card
E0 = BASE_DUR
end1 = stack([text_line("Everyone", F_BLACK, 124, WHITE, stroke=0),
              text_line("starts at", F_BLACK, 124, WHITE, stroke=0),
              text_line("Day 1.", F_BLACK, 124, LIME, stroke=0)], gap=-22)
layers.append(Layer(end1, W // 2, 820, E0 + 0.25, TOTAL + 1, pop=0.35))
layers.append(Layer(pill("Giliran korang pula? ⛳", 58), W // 2, 1150, E0 + 0.9, TOTAL + 1, pop=0.3))

# ---------------------------------------------------------------- progress bar
def draw_loading(frame, t):
    if not (HOLD0 <= t <= HOLD1 + 0.35): return
    a = clamp((t - HOLD0) / 0.12) * clamp((HOLD1 + 0.35 - t) / 0.15)
    p = clamp((t - HOLD0) / (HOLD1 - HOLD0 - 0.3))
    pct = int(99 * (1 - (1 - p) ** 1.7)) if t < HOLD1 else 100
    bw, bh = 640, 44
    x0, y0 = (W - bw) // 2, 500
    ov = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle((x0 - 6, 14 - 6, x0 + bw + 6, 14 + bh + 6), radius=(bh + 12) // 2, fill=(0, 0, 0, 150))
    fill_w = int(bw * pct / 100)
    col = LIME if pct < 100 else (90, 255, 120)
    if fill_w > bh:
        d.rounded_rectangle((x0, 14, x0 + fill_w, 14 + bh), radius=bh // 2, fill=col)
    f = ImageFont.truetype(F_XB, 40)
    d.text((W // 2, 14 + bh + 46), f"{pct}%", font=f, fill=WHITE, anchor="mm", stroke_width=3, stroke_fill=INK)
    if a < 1: ov.putalpha(ov.split()[3].point(lambda v: int(v * a)))
    frame.alpha_composite(ov, (0, y0 - 14))

def draw_ff(frame, t):
    """fast-forward badge during the 2x section"""
    s0, s1 = CUT + 0.1, 7.2
    if not (s0 <= t <= s1): return
    a = clamp((t - s0) / 0.1) * clamp((s1 - t) / 0.1)
    if int(t * 4) % 2 == 1: a *= 0.55
    ov = Image.new("RGBA", (260, 90), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.rounded_rectangle((0, 0, 250, 80), radius=40, fill=(0, 0, 0, 140))
    for i in range(2):
        x = 28 + i * 34
        d.polygon([(x, 20), (x, 60), (x + 32, 40)], fill=WHITE)
    d.text((110, 40), "2x", font=ImageFont.truetype(F_BLACK, 46), fill=WHITE, anchor="lm")
    ov.putalpha(ov.split()[3].point(lambda v: int(v * a)))
    frame.alpha_composite(ov, (W - 70 - 250 - 120, 162))

def draw_slowmo(frame, t):
    for s0, s1 in [(3.3, 5.0), (9.5333, 10.7667)]:
        if s0 <= t <= s1:
            a = clamp((t - s0) / 0.1) * clamp((s1 - t) / 0.1)
            ov = Image.new("RGBA", (300, 90), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            d.rounded_rectangle((0, 0, 290, 80), radius=40, fill=(0, 0, 0, 140))
            d.ellipse((26, 28, 50, 52), fill=(255, 70, 70) if int(t * 3) % 2 == 0 else (120, 30, 30))
            d.text((66, 40), "SLOW-MO", font=ImageFont.truetype(F_BLACK, 40), fill=WHITE, anchor="lm")
            ov.putalpha(ov.split()[3].point(lambda v: int(v * a)))
            frame.alpha_composite(ov, (W - 70 - 290 - 100, 162))

# ---------------------------------------------------------------- camera
def camera(t):
    """returns zoom, cx, cy (in source pixels), shake dx, dy, flash"""
    z, cx, cy = 1.0, W / 2, H / 2
    if t < 2.4:                       # gentle push-in on the hook
        z = 1.0 + 0.06 * ease_in_out(t / 2.4)
    elif t < 3.3:
        z = 1.06
    elif t < 5.0:                     # slow-mo push toward ball
        p = ease_in_out(clamp((t - 3.3) / 0.6))
        z = 1.06 + 0.16 * p
        cx, cy = W / 2 + (430 - W / 2) * p, H / 2 + (1050 - H / 2) * p
        if t > 4.4:
            q = ease_in_out(clamp((t - 4.4) / 0.6))
            z = 1.22 - 0.16 * q
            cx, cy = 430 + (W / 2 - 430) * q, 1050 + (H / 2 - 1050) * q
    elif t < CUT:
        z = 1.06
    elif t < HOLD0:
        z = 1.0 + 0.04 * ease_in_out(clamp((t - CUT) / 1.4))
    elif t < 9.5333:                  # creep in during the long pause
        p = ease_in_out(clamp((t - HOLD0) / (9.5333 - HOLD0)))
        z = 1.04 + 0.16 * p
        cx, cy = W / 2 + (430 - W / 2) * p, H / 2
    elif t < BASE_DUR:
        q = ease_in_out(clamp((t - 10.3) / 0.6))
        z = 1.2 - 0.14 * q
        cx, cy = 430 + (W / 2 - 430) * q, H / 2
    else:
        z, cx, cy = 1.06, W / 2, H / 2
    dx = dy = 0.0; flash = 0.0
    for ti, amp in [(IMPACT_A, 1.0), (IMPACT_B, 1.4)]:
        d = t - ti
        if 0 <= d < 0.35:
            k = math.exp(-d * 12)
            dx += amp * 18 * k * math.sin(d * 95)
            dy += amp * 14 * k * math.cos(d * 80)
            z += amp * 0.07 * k
        if -0.02 <= d < 0.16:
            flash = max(flash, amp * 0.55 * (1 - clamp(d / 0.16)))
    d = t - CUT                        # whip-flash into swing #2
    if -0.06 <= d < 0.18:
        flash = max(flash, 0.85 * (1 - clamp(abs(d) / 0.18)))
    return z, cx, cy, dx, dy, flash

def apply_camera(img, z, cx, cy, dx, dy):
    cw, ch = W / z, H / z
    x0 = clamp(cx - cw / 2, 0, W - cw) - dx / z
    y0 = clamp(cy - ch / 2, 0, H - ch) - dy / z
    x0 = clamp(x0, 0, W - cw); y0 = clamp(y0, 0, H - ch)
    return img.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BICUBIC)

def vignette():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    v = np.clip((r - 0.75) / 0.7, 0, 1) ** 1.5 * 0.45
    a = (v * 255).astype(np.uint8)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255)); im.putalpha(Image.fromarray(a))
    return im
VIG = vignette()

# ---------------------------------------------------------------- render
def main():
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", BASE, "-vf", "eq=contrast=1.06:saturation=1.12:gamma=0.98",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                            "-pix_fmt", "yuv420p", "video_only.mp4"], stdin=subprocess.PIPE)
    last = None; endbg = None
    for n in range(NFR):
        t = n / FPS
        if t < BASE_DUR - 1e-6:
            raw = dec.stdout.read(W * H * 3)
            if len(raw) == W * H * 3:
                last = Image.frombytes("RGB", (W, H), raw)
        src = last
        z, cx, cy, dx, dy, flash = camera(t)
        if t >= BASE_DUR - 1e-6:
            if endbg is None:
                endbg = apply_camera(last, 1.06, W / 2, H / 2, 0, 0)
            p = ease_out(clamp((t - BASE_DUR) / 0.45))
            fr = endbg.filter(ImageFilter.GaussianBlur(2 + 22 * p)) if p < 1 else (
                endbg_blur if 'endbg_blur' in globals() else globals().setdefault('endbg_blur', endbg.filter(ImageFilter.GaussianBlur(24))))
            fr = Image.blend(fr, Image.new("RGB", (W, H), (8, 14, 8)), 0.5 * p)
            frame = fr.convert("RGBA")
        else:
            frame = apply_camera(src, z, cx, cy, dx, dy).convert("RGBA")
        frame.alpha_composite(VIG)
        draw_slowmo(frame, t); draw_ff(frame, t); draw_loading(frame, t)
        for L in layers: L.draw(frame, t)
        out = frame.convert("RGB")
        if flash > 0:
            out = Image.blend(out, Image.new("RGB", (W, H), WHITE), clamp(flash))
        # fade out the last 0.3s
        fo = clamp((TOTAL - t) / 0.3)
        if fo < 1: out = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), out, fo)
        enc.stdin.write(out.tobytes())
        if n % 60 == 0: print(f"frame {n}/{NFR}", flush=True)
    enc.stdin.close(); enc.wait(); dec.kill()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        # render chosen timestamps as stills for checking
        ts = [float(x) for x in sys.argv[2:]]
        for t in ts:
            if t < BASE_DUR:
                raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", BASE, "-frames:v", "1", "-f", "rawvideo",
                                      "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
                src = Image.frombytes("RGB", (W, H), raw)
                z, cx, cy, dx, dy, flash = camera(t)
                frame = apply_camera(src, z, cx, cy, dx, dy).convert("RGBA")
            else:
                frame = Image.new("RGBA", (W, H), (20, 40, 20, 255))
            frame.alpha_composite(VIG)
            draw_slowmo(frame, t); draw_ff(frame, t); draw_loading(frame, t)
            for L in layers: L.draw(frame, t)
            frame.convert("RGB").resize((360, 640)).save(f"../frames/p_{t:05.2f}.jpg")
    else:
        main()
