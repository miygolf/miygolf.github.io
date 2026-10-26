#!/usr/bin/env python3
"""Generate a casual-style Instagram watermark as a transparent PNG.

Look: soft translucent pill, gradient IG glyph, lowercase handle,
optional hand-written tagline tilted underneath.

  python3 watermark/make_watermark.py --handle iqbal.yusoff -o wm.png
  python3 watermark/make_watermark.py --handle iqbal.yusoff --tagline "ride santai je" -o wm_tag.png
"""
import argparse
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_HANDLE = os.path.join(HERE, "fonts", "Poppins-SemiBold.ttf")
FONT_TAGLINE = os.path.join(HERE, "fonts", "Caveat.ttf")

# Supersampling factor: draw big, downscale for smooth edges.
SS = 4

# Instagram brand gradient stops, bottom-left -> top-right.
IG_STOPS = [
    (0.00, (254, 218, 117)),
    (0.25, (250, 126, 30)),
    (0.50, (214, 41, 118)),
    (0.75, (150, 47, 191)),
    (1.00, (79, 91, 213)),
]


def lerp_color(stops, t):
    t = max(0.0, min(1.0, t))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            k = (t - t0) / (t1 - t0)
            return tuple(round(a + (b - a) * k) for a, b in zip(c0, c1))
    return stops[-1][1]


def diagonal_gradient(size, stops):
    w, h = size
    small = Image.new("RGB", (64, 64))
    px = small.load()
    for y in range(64):
        for x in range(64):
            # 0 at bottom-left, 1 at top-right
            px[x, y] = lerp_color(stops, (x + (63 - y)) / 126)
    return small.resize((w, h), Image.BILINEAR)


def ig_glyph(size, colorful=True):
    """Instagram camera glyph (rounded square + lens + flash dot)."""
    s = size
    mask = Image.new("L", (s, s), 0)
    d = ImageDraw.Draw(mask)
    stroke = round(s * 0.085)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=round(s * 0.28), outline=255, width=stroke)
    r = s * 0.22
    c = s / 2
    d.ellipse([c - r, c - r, c + r, c + r], outline=255, width=stroke)
    dr = s * 0.055
    dx, dy = s * 0.745, s * 0.255
    d.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=255)

    fill = diagonal_gradient((s, s), IG_STOPS) if colorful else Image.new("RGB", (s, s), "white")
    out = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    out.paste(fill, (0, 0), mask)
    return out


def make_watermark(handle, tagline="", height=72, colorful=True, bg_alpha=0.38):
    handle = "@" + handle.lstrip("@").lower()
    H = height * SS
    pad_x = round(H * 0.34)
    icon = round(H * 0.50)
    gap = round(H * 0.20)

    font = ImageFont.truetype(FONT_HANDLE, round(H * 0.38))
    tb = font.getbbox(handle)
    text_w = tb[2] - tb[0]
    pill_w = pad_x + icon + gap + text_w + pad_x

    # Tagline sits below the pill, slightly tilted for a hand-written feel.
    tag_img = None
    if tagline:
        tfont = ImageFont.truetype(FONT_TAGLINE, round(H * 0.60))
        tfont.set_variation_by_name("Bold")
        tgb = tfont.getbbox(tagline)
        tw, th = tgb[2] - tgb[0], tgb[3] - tgb[1]
        tpad = round(H * 0.12)
        tag_img = Image.new("RGBA", (tw + 2 * tpad, th + 2 * tpad), (0, 0, 0, 0))
        td = ImageDraw.Draw(tag_img)
        td.text((tpad - tgb[0], tpad - tgb[1]), tagline, font=tfont, fill=(255, 255, 255, 245))
        tag_img = tag_img.rotate(4, resample=Image.BICUBIC, expand=True)

    margin = round(H * 0.30)  # room for the soft shadow
    tag_h = tag_img.height - round(H * 0.10) if tag_img else 0
    tag_w = (tag_img.width + round(H * 0.25)) if tag_img else 0
    W = max(pill_w, tag_w) + 2 * margin
    Ht = H + tag_h + 2 * margin
    canvas = Image.new("RGBA", (W, Ht), (0, 0, 0, 0))

    px, py = margin, margin
    radius = H // 2

    # Soft drop shadow keeps it readable over bright skies.
    shadow = Image.new("L", (W, Ht), 0)
    ImageDraw.Draw(shadow).rounded_rectangle(
        [px, py + round(H * 0.06), px + pill_w, py + H + round(H * 0.06)], radius=radius, fill=70
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(H * 0.12))
    canvas.paste((0, 0, 0, 255), (0, 0), shadow)

    pill = Image.new("RGBA", (W, Ht), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle(
        [px, py, px + pill_w, py + H],
        radius=radius,
        fill=(20, 20, 24, round(255 * bg_alpha)),
        outline=(255, 255, 255, 70),
        width=max(1, round(SS * 1.2)),
    )
    canvas = Image.alpha_composite(canvas, pill)

    glyph = ig_glyph(icon, colorful)
    canvas.alpha_composite(glyph, (px + pad_x, py + (H - icon) // 2))

    d = ImageDraw.Draw(canvas)
    tx = px + pad_x + icon + gap - tb[0]
    ty = py + (H - (tb[3] - tb[1])) // 2 - tb[1]
    d.text((tx, ty), handle, font=font, fill=(255, 255, 255, 250))

    if tag_img:
        # Text shadow for the tagline too.
        tsh = Image.new("RGBA", tag_img.size, (0, 0, 0, 0))
        tsh.putalpha(tag_img.getchannel("A").point(lambda a: a * 0.45).filter(ImageFilter.GaussianBlur(SS * 2)))
        tx0 = px + round(H * 0.25)
        ty0 = py + H - round(H * 0.08)
        canvas.alpha_composite(tsh, (tx0, ty0 + SS * 2))
        canvas.alpha_composite(tag_img, (tx0, ty0))

    return canvas.resize((math.ceil(W / SS), math.ceil(Ht / SS)), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--handle", required=True, help="Instagram username, with or without @")
    ap.add_argument("--tagline", default="", help="optional hand-written line under the pill")
    ap.add_argument("--height", type=int, default=72, help="pill height in px (72 suits 1080x1920)")
    ap.add_argument("--mono", action="store_true", help="white IG glyph instead of gradient")
    ap.add_argument("--bg-alpha", type=float, default=0.38, help="pill background opacity 0-1")
    ap.add_argument("-o", "--output", default="watermark.png")
    a = ap.parse_args()

    img = make_watermark(a.handle, a.tagline, a.height, not a.mono, a.bg_alpha)
    img.save(a.output)
    print(f"{a.output} {img.width}x{img.height}")


if __name__ == "__main__":
    main()
