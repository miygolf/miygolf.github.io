"""TikTok review edit: BOH Camomile Harmony.

Renders animated overlays (hook, product name, 3 benefits, price tag, CTA)
frame by frame with PIL, synthesises light SFX, and composites everything on
top of the graded 1080x1920 base clip with ffmpeg.

Usage:
  python3 render.py BASE.mp4 SOURCE.mp4 OUT.mp4 [--guides] [--preview]
"""
import math
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from edit_config import (BENEFITS, CTA, FPS, H, HOOK, PRICE, PRODUCT, SAFE,
                         W)

FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"

YELLOW = (255, 200, 30, 255)
DARK = (28, 20, 10, 255)
WHITE = (255, 255, 255, 255)
RED = (230, 45, 45, 255)
SS = 2  # supersampling for smooth vector icons


# ---------------------------------------------------------------- easing ---
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_back(t, s=1.9):
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def envelope(t, start, end, fade_in=0.25, fade_out=0.2):
    """0..1 entrance progress and alpha for an element shown in [start, end)."""
    if t < start or t >= end:
        return None
    p_in = clamp((t - start) / fade_in)
    alpha = clamp((end - t) / fade_out)
    return p_in, alpha


# ----------------------------------------------------------------- text ----
def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(text, path, size, max_w):
    f = font(path, size)
    while f.getlength(text) > max_w and size > 20:
        size -= 2
        f = font(path, size)
    return f


def text_img(text, path, size, fill=WHITE, stroke=0, stroke_fill=DARK,
             max_w=None, shadow=True):
    f = fit_font(text, path, size, max_w) if max_w else font(path, size)
    l, t, r, b = f.getbbox(text, stroke_width=stroke)
    pad = 24
    img = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pos = (pad - l, pad - t)
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pos[0] + 4, pos[1] + 7), text, font=f,
                                fill=(0, 0, 0, 150), stroke_width=stroke,
                                stroke_fill=(0, 0, 0, 150))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(6)))
        d = ImageDraw.Draw(img)
    d.text(pos, text, font=f, fill=fill, stroke_width=stroke,
           stroke_fill=stroke_fill)
    return img


def stack(imgs, gap=0, align="center"):
    w = max(i.width for i in imgs)
    h = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = 0
    for i in imgs:
        x = (w - i.width) // 2 if align == "center" else 0
        out.alpha_composite(i, (x, y))
        y += i.height + gap
    return out


def pill(img, fill, pad=(36, 18), radius=None, outline=None):
    w, h = img.width + pad[0] * 2, img.height + pad[1] * 2
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius or h // 2, fill=fill,
                        outline=outline, width=6 if outline else 0)
    out.alpha_composite(img, pad)
    return out


def drop_shadow(img, offset=(0, 12), blur=18, alpha=110):
    m = 40
    out = Image.new("RGBA", (img.width + m * 2, img.height + m * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    a = img.split()[3].point(lambda v: v * alpha // 255)
    sh.paste((0, 0, 0, 255), (m + offset[0], m + offset[1]), a)
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(img, (m, m))
    return out


# ---------------------------------------------------------------- icons ----
def icon_canvas(size):
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img), s


def finish(img, size):
    return img.resize((size, size), Image.LANCZOS)


def icon_no_caffeine(size):
    img, d, s = icon_canvas(size)
    d.ellipse((0, 0, s - 1, s - 1), fill=YELLOW)
    # cup
    cx, cy, k = s * 0.47, s * 0.55, s / 100
    d.rounded_rectangle((cx - 22 * k, cy - 18 * k, cx + 18 * k, cy + 20 * k),
                        8 * k, fill=DARK)
    d.ellipse((cx + 10 * k, cy - 10 * k, cx + 32 * k, cy + 12 * k),
              outline=DARK, width=int(6 * k))
    for i, x in enumerate((-12, 0, 12)):
        d.arc((cx + (x - 5) * k, cy - 42 * k, cx + (x + 5) * k, cy - 24 * k),
              90, 270, fill=DARK, width=int(4 * k))
    # prohibition ring + slash
    d.ellipse((10 * k, 10 * k, s - 10 * k, s - 10 * k), outline=RED,
              width=int(8 * k))
    a = math.radians(45)
    r = s / 2 - 14 * k
    d.line((s / 2 - r * math.cos(a), s / 2 - r * math.sin(a),
            s / 2 + r * math.cos(a), s / 2 + r * math.sin(a)), fill=RED,
           width=int(8 * k))
    return finish(img, size)


def icon_teabag(size):
    img, d, s = icon_canvas(size)
    k = s / 100
    d.ellipse((0, 0, s - 1, s - 1), fill=YELLOW)
    d.line((50 * k, 20 * k, 50 * k, 36 * k), fill=DARK, width=int(3 * k))
    d.line((50 * k, 20 * k, 70 * k, 22 * k), fill=DARK, width=int(3 * k))
    d.rounded_rectangle((64 * k, 16 * k, 80 * k, 30 * k), 3 * k, fill=WHITE,
                        outline=DARK, width=int(3 * k))
    d.polygon([(34 * k, 44 * k), (50 * k, 34 * k), (66 * k, 44 * k),
               (66 * k, 78 * k), (34 * k, 78 * k)], fill=(250, 240, 215, 255),
              outline=DARK)
    d.line([(34 * k, 44 * k), (50 * k, 34 * k), (66 * k, 44 * k),
            (66 * k, 78 * k), (34 * k, 78 * k), (34 * k, 44 * k)], fill=DARK,
           width=int(4 * k), joint="curve")
    for x, y in ((44, 56), (55, 60), (47, 68), (58, 70), (52, 50)):
        d.ellipse(((x - 3) * k, (y - 2) * k, (x + 3) * k, (y + 2) * k),
                  fill=(160, 120, 40, 255))
    return finish(img, size)


def icon_flower(size):
    img, d, s = icon_canvas(size)
    k = s / 100
    d.ellipse((0, 0, s - 1, s - 1), fill=YELLOW)
    c = s / 2
    for i in range(12):
        a = math.radians(i * 30)
        x, y = c + math.cos(a) * 22 * k, c + math.sin(a) * 22 * k
        petal = Image.new("RGBA", (int(18 * k), int(36 * k)), (0, 0, 0, 0))
        ImageDraw.Draw(petal).ellipse((0, 0, petal.width - 1, petal.height - 1),
                                      fill=WHITE, outline=(220, 210, 190, 255),
                                      width=int(2 * k))
        petal = petal.rotate(-math.degrees(a) + 90, expand=True,
                             resample=Image.BICUBIC)
        img.alpha_composite(petal, (int(x - petal.width / 2),
                                    int(y - petal.height / 2)))
    d = ImageDraw.Draw(img)
    d.ellipse((c - 13 * k, c - 13 * k, c + 13 * k, c + 13 * k),
              fill=(255, 170, 0, 255), outline=(200, 120, 0, 255),
              width=int(3 * k))
    return finish(img, size)


def icon_moon(size):
    img, d, s = icon_canvas(size)
    k = s / 100
    d.ellipse((8 * k, 8 * k, 80 * k, 80 * k), fill=(255, 225, 120, 255))
    d.ellipse((30 * k, 0, 100 * k, 70 * k), fill=(0, 0, 0, 0))
    f = font(FONT_BLACK, int(22 * k))
    d.text((62 * k, 50 * k), "z", font=f, fill=WHITE)
    d.text((74 * k, 30 * k), "z", font=font(FONT_BLACK, int(28 * k)), fill=WHITE)
    return finish(img, size)


def icon_bag(size):
    """Yellow shopping bag, like TikTok Shop's product anchor."""
    img, d, s = icon_canvas(size)
    k = s / 100
    d.arc((32 * k, 8 * k, 68 * k, 48 * k), 180, 360, fill=DARK,
          width=int(7 * k))
    d.rounded_rectangle((14 * k, 28 * k, 86 * k, 94 * k), 12 * k, fill=YELLOW,
                        outline=DARK, width=int(5 * k))
    d.ellipse((30 * k, 38 * k, 38 * k, 46 * k), fill=DARK)
    d.ellipse((62 * k, 38 * k, 70 * k, 46 * k), fill=DARK)
    d.arc((34 * k, 40 * k, 66 * k, 72 * k), 20, 160, fill=DARK,
          width=int(6 * k))
    return finish(img, size)


def price_tag(label, price):
    w, h = 560, 300
    s = SS
    img = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    notch = 110 * s
    poly = [(notch, 0), (w * s - 1, 0), (w * s - 1, h * s - 1), (notch, h * s - 1),
            (0, h * s / 2)]
    d.polygon(poly, fill=YELLOW)
    d.line(poly + [poly[0]], fill=DARK, width=8 * s, joint="curve")
    d.ellipse((58 * s, h * s / 2 - 22 * s, 102 * s, h * s / 2 + 22 * s),
              fill=(60, 40, 10, 255))
    img = img.resize((w, h), Image.LANCZOS)
    lab = text_img(label, FONT_BOLD, 44, fill=DARK, shadow=False)
    pr = text_img(price, FONT_BLACK, 120, fill=DARK, shadow=False,
                  max_w=w - 170)
    body = stack([lab, pr], gap=-30)
    img.alpha_composite(body, (130 + (w - 130 - body.width) // 2,
                               (h - body.height) // 2))
    return img


def arrow(length, color=YELLOW):
    s = SS
    img = Image.new("RGBA", (60 * s, length * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((22 * s, 0, 38 * s, (length - 40) * s), fill=color)
    d.polygon([(0, (length - 46) * s), (60 * s - 1, (length - 46) * s),
               (30 * s, length * s - 1)], fill=color)
    return img.resize((60, length), Image.LANCZOS)


# ------------------------------------------------------------- elements ----
def build_assets():
    a = {}
    inner_w = SAFE[2] - SAFE[0] - 40

    hook_l1 = text_img(HOOK["line1"], FONT_BLACK, 116, stroke=10,
                       max_w=inner_w)
    hook_l2 = text_img(HOOK["line2"], FONT_BLACK, 116, fill=YELLOW, stroke=10,
                       max_w=inner_w)
    a["hook"] = stack([icon_moon(150), hook_l1, hook_l2], gap=-14)
    a["hook_sub"] = pill(text_img(HOOK["sub"], FONT_BOLD, 50, fill=DARK,
                                  shadow=False, max_w=inner_w - 80),
                         fill=WHITE)

    name = text_img(PRODUCT["name"], FONT_BLACK, 84, fill=DARK, shadow=False,
                    max_w=inner_w - 80)
    tagline = text_img(PRODUCT["tagline"], FONT_BOLD, 40, fill=DARK,
                       shadow=False)
    a["product"] = drop_shadow(pill(stack([name, tagline], gap=-26),
                                    fill=YELLOW, pad=(44, 14), radius=40))

    icons = [icon_no_caffeine, icon_teabag, icon_flower]
    a["benefits"] = []
    for i, b in enumerate(BENEFITS):
        ic = icons[i](190)
        badge = pill(text_img(f"{i + 1}/3", FONT_BLACK, 36, fill=DARK,
                              shadow=False), fill=WHITE, pad=(18, 0))
        txt_w = inner_w - 190 - 40
        title = stack([text_img(line, FONT_BLACK, 104, stroke=9, max_w=txt_w)
                       for line in b["title"]], gap=-30, align="left")
        sub = text_img(b["sub"], FONT_BOLD, 44, fill=YELLOW, stroke=5,
                       max_w=txt_w)
        text = stack([title, sub], gap=-10, align="left")
        h = max(ic.height, text.height)
        card = Image.new("RGBA", (ic.width + 20 + text.width, h + 40),
                         (0, 0, 0, 0))
        card.alpha_composite(drop_shadow(ic, blur=10)
                             .resize((ic.width, ic.height)), (0, 40 + (h - ic.height) // 2))
        card.alpha_composite(badge, (ic.width - badge.width + 16, 20))
        card.alpha_composite(text, (ic.width + 20, 40 + (h - text.height) // 2))
        a["benefits"].append(card)

    a["tag"] = drop_shadow(price_tag(PRICE["label"], PRICE["text"]))
    a["tag_note"] = text_img(PRICE["note"], FONT_BOLD, 44, stroke=5,
                             max_w=inner_w) if PRICE.get("note") else None

    a["cta_bag"] = drop_shadow(icon_bag(240), blur=14)
    a["cta_text"] = stack([
        text_img(line, FONT_BLACK, 120, fill=YELLOW if i else WHITE, stroke=11,
                 max_w=inner_w) for i, line in enumerate(CTA["lines"])],
        gap=-26)
    a["cta_sub"] = pill(text_img(CTA["sub"], FONT_BOLD, 46, fill=DARK,
                                 shadow=False, max_w=inner_w - 80), fill=WHITE)
    a["arrow"] = arrow(170)
    return a


def place(frame, img, cx, cy, scale=1.0, alpha=1.0, angle=0.0, pivot=None):
    if alpha <= 0.01 or scale <= 0.01:
        return
    if scale != 1.0:
        img = img.resize((max(1, int(img.width * scale)),
                          max(1, int(img.height * scale))), Image.BICUBIC)
    if angle:
        img = img.rotate(angle, expand=True, resample=Image.BICUBIC,
                         center=pivot)
    if alpha < 1.0:
        img = img.copy()
        img.putalpha(img.split()[3].point(lambda v: int(v * alpha)))
    frame.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))


def safe_guides(frame):
    ov = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    x0, y0, x1, y1 = SAFE
    shade = (255, 0, 80, 70)
    d.rectangle((0, 0, W, y0), fill=shade)
    d.rectangle((0, y1, W, H), fill=shade)
    d.rectangle((0, y0, x0, y1), fill=shade)
    d.rectangle((x1, y0, W, y1), fill=shade)
    d.rectangle(SAFE, outline=(0, 255, 120, 255), width=4)
    f = font(FONT_BOLD, 30)
    d.text((x0 + 10, y0 + 8), "TIKTOK SAFE ZONE", font=f, fill=(0, 255, 120, 255))
    d.text((x1 + 8, 700), "UI", font=f, fill=WHITE)
    d.text((40, y1 + 140), "CAPTION / MUSIC / BEG KUNING", font=f, fill=WHITE)
    frame.alpha_composite(ov)


def render_frame(t, a, guides):
    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx = (SAFE[0] + SAFE[2]) / 2

    # Hook: problem statement, punchy pop-in right from frame 0.
    e = envelope(t, HOOK["start"], HOOK["end"], fade_in=0.18)
    if e:
        p, al = e
        shake = math.sin(t * 60) * 6 * clamp(1 - t / 0.5)
        place(frame, a["hook"], cx + shake, 470, 0.6 + 0.4 * ease_out_back(p), al)
        p2 = clamp((t - HOOK["start"] - 0.35) / 0.25)
        place(frame, a["hook_sub"], cx, 780 + 40 * (1 - ease_out_cubic(p2)),
              alpha=al * p2)

    e = envelope(t, PRODUCT["start"], PRODUCT["end"])
    if e:
        p, al = e
        place(frame, a["product"], cx - (1 - ease_out_cubic(p)) * 700, 1270, alpha=al)

    for b, img in zip(BENEFITS, a["benefits"]):
        e = envelope(t, b["start"], b["end"], fade_in=0.3)
        if e:
            p, al = e
            place(frame, img, cx, 1250, 0.4 + 0.6 * ease_out_back(p), al)

    e = envelope(t, PRICE["start"], PRICE["end"], fade_in=0.45)
    if e:
        p, al = e
        dt = t - PRICE["start"]
        y = -200 + (1080 + 200) * ease_out_back(p, 1.2)
        swing = 22 * math.exp(-dt * 2.2) * math.sin(dt * 9)
        place(frame, a["tag"], cx, y, 1.3, al, angle=swing)
        if a["tag_note"]:
            p2 = clamp((dt - 0.6) / 0.25)
            place(frame, a["tag_note"], cx, 1300, 0.6 + 0.4 * ease_out_back(p2),
                  al * p2)
        # sparkle burst when the tag lands
        if 0.3 < dt < 1.0:
            d = ImageDraw.Draw(frame)
            k = (dt - 0.3) / 0.7
            for i in range(10):
                ang = i * math.pi / 5
                r0, r1 = 220 + 160 * k, 250 + 200 * k
                col = (255, 230, 90, int(255 * (1 - k)))
                d.line((cx + math.cos(ang) * r0, 1080 + math.sin(ang) * r0 * 0.7,
                        cx + math.cos(ang) * r1, 1080 + math.sin(ang) * r1 * 0.7),
                       fill=col, width=10)

    e = envelope(t, CTA["start"], CTA["end"], fade_in=0.35, fade_out=0.01)
    if e:
        p, al = e
        dt = t - CTA["start"]
        bounce = abs(math.sin(dt * 5)) * 26 * clamp(dt / 0.4)
        place(frame, a["cta_bag"], cx, 560 - bounce,
              0.3 + 0.7 * ease_out_back(p), al, angle=math.sin(dt * 5) * 6)
        p2 = clamp((dt - 0.15) / 0.3)
        place(frame, a["cta_text"], cx, 870, 0.5 + 0.5 * ease_out_back(p2), p2)
        p3 = clamp((dt - 0.45) / 0.3)
        place(frame, a["cta_sub"], cx, 1110, alpha=p3)
        p4 = clamp((dt - 0.7) / 0.3)
        place(frame, a["arrow"], cx, 1300 + math.sin(dt * 8) * 22, alpha=p4)

    if guides:
        safe_guides(frame)
    return frame


# ----------------------------------------------------------------- audio ---
def synth_sfx(duration, sr=48000):
    n = int(duration * sr)
    out = np.zeros(n, dtype=np.float32)

    def add(sig, at):
        i = int(at * sr)
        j = min(n, i + len(sig))
        out[i:j] += sig[: j - i]

    def pop(f0=420, f1=900, dur=0.09, amp=0.35):
        tt = np.arange(int(dur * sr)) / sr
        f = np.linspace(f0, f1, len(tt))
        return amp * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 40)

    def ding(f=1320, dur=1.2, amp=0.28):
        tt = np.arange(int(dur * sr)) / sr
        s = sum(np.sin(2 * np.pi * f * m * tt) / m for m in (1, 2.01, 3.03))
        return amp * s * np.exp(-tt * 4)

    def whoosh(dur=0.35, amp=0.18):
        tt = np.arange(int(dur * sr)) / sr
        noise = np.random.default_rng(1).standard_normal(len(tt))
        env = np.sin(np.pi * tt / dur) ** 2
        k = np.ones(30) / 30
        return amp * np.convolve(noise, k, "same") * env

    add(whoosh(), max(0, HOOK["start"]))
    add(pop(300, 700), HOOK["start"] + 0.02)
    add(whoosh(), PRODUCT["start"])
    for b in BENEFITS:
        add(pop(), b["start"] + 0.05)
    add(whoosh(0.4), PRICE["start"])
    add(ding(), PRICE["start"] + 0.35)
    add(ding(1568, amp=0.2), PRICE["start"] + 0.47)
    add(pop(500, 1200), CTA["start"] + 0.05)
    add(ding(1760, amp=0.18), CTA["start"] + 0.25)
    return out


def write_wav(path, data, sr=48000):
    data = np.clip(data, -1, 1)
    pcm = (data * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


# ------------------------------------------------------------------ main ---
def main():
    base, source, out = sys.argv[1:4]
    guides = "--guides" in sys.argv
    preview = "--preview" in sys.argv

    dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", base]).decode())
    n_frames = int(round(dur * FPS))

    sfx_path = out + ".sfx.wav"
    write_wav(sfx_path, synth_sfx(dur + 1))

    a = build_assets()
    vf_out = "scale=720:1280:flags=lanczos" if preview else "null"
    cmd = [
        "ffmpeg", "-v", "error", "-y",
        "-i", base,
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-",
        "-i", source,
        "-i", sfx_path,
        "-filter_complex",
        f"[0:v][1:v]overlay=0:0:format=auto,{vf_out},format=yuv420p[v];"
        # original ambience (water pour, sachet) is quiet: lift it, then mix SFX
        "[2:a]highpass=f=80,afftdn=nf=-45,loudnorm=I=-20:TP=-2,"
        "aresample=48000,aformat=channel_layouts=stereo[amb];"
        "[3:a]aformat=channel_layouts=stereo[sfx];"
        "[amb][sfx]amix=inputs=2:duration=first:normalize=0,"
        "alimiter=limit=0.95[a]",
        "-map", "[v]", "-map", "[a]",
        "-t", f"{dur:.3f}",
        "-c:v", "libx264", "-preset", "medium",
        "-crf", "23" if preview else "17",
        "-profile:v", "high", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        out,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n_frames):
        proc.stdin.write(render_frame(i / FPS, a, guides).tobytes())
    proc.stdin.close()
    proc.wait()
    if proc.returncode:
        sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
