#!/usr/bin/env python3
"""Before/after swing transformation video.

Layout: BEFORE (3s) -> power wipe + whoosh -> AFTER -> wipe + whoosh ->
side-by-side split screen (slow-mo, synced on impact) -> short hold.
No background music: only the clips' own sound plus whoosh SFX.

Usage:
  python3 transformasi.py --before B.mp4 --impact-before 2.95 \
      --after A.mp4 --impact-after 4.98 --font Anton-Regular.ttf --out out.mp4
"""
import argparse
import os
import subprocess
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
SR = 48000

RED = (229, 57, 53)
GREEN = (34, 197, 94)
GLOW = np.array([255, 205, 80], np.float32)  # warm gold edge glow

BEFORE_SEC = 3.0      # before shown alone before the wipe starts
WIPE_SEC = 0.4        # wipe duration
AFTER_SEC = 3.5       # after segment incl. both wipes (clamped to clip length)
PRE_IMPACT = 2.0      # seconds before impact where each full-screen segment starts
SPLIT_PRE, SPLIT_POST = 1.5, 1.2   # split-screen window around impact (source seconds)
SLOWMO = 0.5
HOLD_SEC = 1.2
CLIP_GAIN = 2.0       # phone audio is quiet; lift it so the strike is audible

PANEL_W, PANEL_H = 540, 960
PANEL_Y = (H - PANEL_H) // 2


# ---------------------------------------------------------------- media io

def probe_duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", path])
    return float(out)


def read_frames(path, start, dur, size, fps):
    """Yield RGB uint8 frames (autorotated, scaled to size)."""
    w, h = size
    proc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", path,
        "-t", f"{dur:.3f}", "-an",
        "-vf", f"fps={fps},scale={w}:{h}:flags=lanczos",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = w * h * 3
    last = None
    try:
        while True:
            buf = proc.stdout.read(n)
            if len(buf) < n:
                break
            last = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
            yield last
        # pad with the last frame so callers never run dry at clip ends
        while last is not None:
            yield last
    finally:
        proc.kill()
        proc.wait()


def read_audio(path, start, dur, tempo=1.0):
    """Clip audio as float stereo; tempo<1 slows it down without pitch shift."""
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", path,
        "-t", f"{dur:.3f}", "-vn", "-ac", "2", "-ar", str(SR),
        "-af", f"atempo={tempo}", "-f", "f32le", "-"])
    a = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    want = int(round(dur / tempo * SR))
    if len(a) < want:
        a = np.vstack([a, np.zeros((want - len(a), 2), np.float32)])
    return a[:want]


# ---------------------------------------------------------------- graphics

def ease_in_out_cubic(u):
    u = min(max(u, 0.0), 1.0)
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def ease_out_cubic(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 3


def pop_scale(u):
    """0 -> overshoot 1.12 -> settle 1.0 (label pop-in)."""
    if u <= 0:
        return 0.0
    if u < 0.6:
        return 0.5 + 0.62 * ease_out_cubic(u / 0.6)
    return 1.12 - 0.12 * ease_out_cubic((u - 0.6) / 0.4)


def make_pill(text, color, font_path, size):
    font = ImageFont.truetype(font_path, size)
    l, t, r, b = font.getbbox(text)
    tw, th = r - l, b - t
    padx, pady = int(size * 0.45), int(size * 0.22)
    pw, ph = tw + 2 * padx, th + 2 * pady
    sh = 18  # room for shadow
    img = Image.new("RGBA", (pw + 2 * sh, ph + 2 * sh), (0, 0, 0, 0))
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (sh, sh + 8, sh + pw, sh + ph + 8), radius=ph // 2, fill=(0, 0, 0, 150))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((sh, sh, sh + pw, sh + ph), radius=ph // 2,
                        fill=color + (255,), outline=(255, 255, 255, 255), width=5)
    d.text((sh + padx - l, sh + pady - t), text, font=font, fill=(255, 255, 255, 255))
    return img


def make_text(text, font_path, size, color=(255, 255, 255)):
    font = ImageFont.truetype(font_path, size)
    l, t, r, b = font.getbbox(text)
    pad = 16
    img = Image.new("RGBA", (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0))
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((pad - l, pad - t + 5), text, font=font, fill=(0, 0, 0, 170))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(img).text((pad - l, pad - t), text, font=font, fill=color + (255,))
    return img


def paste_center(frame, overlay, cx, cy, scale=1.0):
    """Alpha-composite RGBA overlay onto an RGB float/uint8 numpy frame."""
    if scale <= 0.01:
        return frame
    if abs(scale - 1.0) > 1e-3:
        overlay = overlay.resize((max(1, int(overlay.width * scale)),
                                  max(1, int(overlay.height * scale))), Image.BILINEAR)
    ov = np.asarray(overlay, np.float32)
    oh, ow = ov.shape[:2]
    x0, y0 = int(cx - ow / 2), int(cy - oh / 2)
    fx0, fy0 = max(x0, 0), max(y0, 0)
    fx1, fy1 = min(x0 + ow, frame.shape[1]), min(y0 + oh, frame.shape[0])
    if fx1 <= fx0 or fy1 <= fy0:
        return frame
    sub = ov[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]
    a = sub[..., 3:4] / 255.0
    out = frame.astype(np.float32, copy=True)
    out[fy0:fy1, fx0:fx1] = out[fy0:fy1, fx0:fx1] * (1 - a) + sub[..., :3] * a
    return out


def zoom(frame, s, dx=0.0, dy=0.0):
    """Center zoom by factor s (>=1) with optional pixel offset (shake)."""
    if abs(s - 1.0) < 1e-3 and dx == 0 and dy == 0:
        return frame
    h, w = frame.shape[:2]
    cw, ch = w / s, h / s
    x0 = (w - cw) / 2 + dx / s
    y0 = (h - ch) / 2 + dy / s
    x0 = min(max(x0, 0), w - cw)
    y0 = min(max(y0, 0), h - ch)
    img = Image.fromarray(np.clip(frame, 0, 255).astype(np.uint8))
    img = img.resize((w, h), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
    return np.asarray(img, np.float32)


XS = np.arange(W, dtype=np.float32)[None, :]
YS = np.arange(H, dtype=np.float32)[:, None]
SLANT = np.tan(np.radians(14))


def wipe(a, b, p):
    """Diagonal right-to-left wipe from a to b with a glowing edge, p in [0,1]."""
    span = W + 2 * SLANT * H / 2 + 120
    c = (W + SLANT * H / 2 + 60) - span * p
    d = XS - (c + SLANT * (YS - H / 2))        # >0 : already revealed (b)
    m = np.clip(d / 2.0 + 0.5, 0, 1)[..., None]
    out = a * (1 - m) + b * m
    # glow: hot white core + gold halo + light streak trailing into the new clip
    core = np.exp(-(d / 7.0) ** 2)
    halo = np.exp(-(d / 45.0) ** 2)
    trail = np.where(d > 0, np.exp(-d / 160.0), 0.0) * 0.35
    out = out + core[..., None] * 255 * 0.95 + (halo + trail)[..., None] * GLOW * 0.55
    return out


# ---------------------------------------------------------------- audio

def whoosh(dur, f0, f1, f2, pan_from, pan_to, seed):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, 1, n, dtype=np.float64)
    noise = rng.standard_normal(n)
    peak = 0.55
    fc = np.where(t < peak, f0 * (f1 / f0) ** (t / peak),
                  f1 * (f2 / f1) ** ((t - peak) / (1 - peak)))
    # time-varying resonant band-pass (state variable filter)
    q = 2.2
    low = band = 0.0
    y = np.empty(n)
    for i in range(n):
        f = 2 * np.sin(np.pi * fc[i] / SR)
        high = noise[i] - low - band / q
        band += f * high
        low += f * band
        y[i] = band + 0.25 * low
    env = np.where(t < peak, (t / peak) ** 2.5, np.exp(-(t - peak) / (1 - peak) * 5.0))
    y *= env
    y /= np.max(np.abs(y)) + 1e-9
    pan = pan_from + (pan_to - pan_from) * t      # -1 left .. +1 right
    left = y * np.sqrt((1 - pan) / 2)
    right = y * np.sqrt((1 + pan) / 2)
    return np.stack([left, right], 1).astype(np.float32)


def boom(dur=0.45):
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = 45 + 60 * np.exp(-t * 18)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    y = np.sin(phase) * np.exp(-t * 9)
    y[: int(0.004 * SR)] += np.random.default_rng(3).standard_normal(int(0.004 * SR)) * 0.4
    y /= np.max(np.abs(y))
    return np.stack([y, y], 1).astype(np.float32)


def add_at(track, clip, t, gain):
    i = int(t * SR)
    j = min(len(track), i + len(clip))
    if j > i:
        track[i:j] += clip[: j - i] * gain


def fade(a, fin, fout):
    a = a.copy()
    ni, no = int(fin * SR), int(fout * SR)
    if ni:
        a[:ni] *= np.linspace(0, 1, ni)[:, None]
    if no:
        a[-no:] *= np.linspace(1, 0, no)[:, None]
    return a


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--impact-before", type=float, required=True)
    ap.add_argument("--impact-after", type=float, required=True)
    ap.add_argument("--font", required=True)
    ap.add_argument("--title", default="TRANSFORMASI SWING")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    dur_b, dur_a = probe_duration(args.before), probe_duration(args.after)

    # ---- timeline
    a0 = max(0.0, args.impact_before - PRE_IMPACT)
    b0 = max(0.0, args.impact_after - PRE_IMPACT)
    after_len = min(AFTER_SEC + WIPE_SEC, dur_a - b0 - 0.05)
    t_w1 = BEFORE_SEC                       # wipe 1 start
    t_w2 = t_w1 + after_len - WIPE_SEC      # wipe 2 start
    split_src = SPLIT_PRE + SPLIT_POST
    split_len = split_src / SLOWMO
    t_end = t_w2 + split_len + HOLD_SEC
    nframes = int(round(t_end * FPS))

    sb0 = max(0.0, args.impact_before - SPLIT_PRE)
    sa0 = max(0.0, args.impact_after - SPLIT_PRE)
    src_fps = round(FPS / SLOWMO)

    before_fr = read_frames(args.before, a0, BEFORE_SEC + WIPE_SEC + 0.2, (W, H), FPS)
    after_fr = read_frames(args.after, b0, after_len + 0.2, (W, H), FPS)
    split_b = read_frames(args.before, sb0, split_src + 0.1, (PANEL_W, PANEL_H), src_fps)
    split_a = read_frames(args.after, sa0, split_src + 0.1, (PANEL_W, PANEL_H), src_fps)

    # ---- graphics assets
    lbl_before = make_pill("BEFORE", RED, args.font, 130)
    lbl_after = make_pill("AFTER", GREEN, args.font, 130)
    sm_before = make_pill("BEFORE", RED, args.font, 84)
    sm_after = make_pill("AFTER", GREEN, args.font, 84)
    title = make_text(args.title, args.font, 96)
    slow_tag = make_text("SLOW MOTION", args.font, 54, (255, 205, 80))
    # top-left so the label stays clear of the golfer's head in any camera angle
    LBL_Y = 230
    lbl_x = lambda img: 30 + img.width / 2

    # split-screen background: dark vertical gradient
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    split_bg = (np.array([18, 18, 22], np.float32) * (1 - g)
                + np.array([4, 4, 6], np.float32) * g) * np.ones((1, W, 1), np.float32)

    def split_frame(t_local):
        fb = next(split_b) if t_local < split_len else split_frame.last_b
        fa = next(split_a) if t_local < split_len else split_frame.last_a
        split_frame.last_b, split_frame.last_a = fb, fa
        f = split_bg.copy()
        f[PANEL_Y:PANEL_Y + PANEL_H, 0:PANEL_W] = fb
        f[PANEL_Y:PANEL_Y + PANEL_H, PANEL_W:W] = fa
        f[PANEL_Y:PANEL_Y + PANEL_H, PANEL_W - 3:PANEL_W + 3] = 255
        s = pop_scale((t_local - 0.15) / 0.35)
        f = paste_center(f, title, W / 2, PANEL_Y - 250, min(1.0, s) if s else 0)
        f = paste_center(f, sm_before, PANEL_W / 2, PANEL_Y - 80, pop_scale((t_local - 0.3) / 0.3))
        f = paste_center(f, sm_after, PANEL_W + PANEL_W / 2, PANEL_Y - 80,
                         pop_scale((t_local - 0.45) / 0.3))
        if t_local < split_len:
            f = paste_center(f, slow_tag, W / 2, PANEL_Y + PANEL_H + 90)
        return f

    # ---- audio
    total = np.zeros((int(t_end * SR) + SR, 2), np.float32)
    aud_b = fade(read_audio(args.before, a0, BEFORE_SEC + WIPE_SEC), 0.05, WIPE_SEC)
    aud_a = fade(read_audio(args.after, b0, after_len), 0.03, WIPE_SEC)
    add_at(total, aud_b, 0, CLIP_GAIN)
    add_at(total, aud_a, t_w1, CLIP_GAIN)
    # split screen: both clips' own sound slowed to match the slow-mo
    for path, s0 in ((args.before, sb0), (args.after, sa0)):
        add_at(total, fade(read_audio(path, s0, split_src, SLOWMO), 0.3, 0.6),
               t_w2, CLIP_GAIN * 0.6)
    w1 = whoosh(0.75, 250, 3800, 900, 0.8, -0.8, 1)
    w2 = whoosh(0.65, 300, 3000, 800, 0.7, -0.7, 2)
    # whoosh peaks (55% in) at the wipe's midpoint; boom lands as the wipe completes
    add_at(total, w1, t_w1 + WIPE_SEC / 2 - 0.55 * 0.75, 0.85)
    add_at(total, boom(), t_w1 + WIPE_SEC - 0.02, 0.6)
    add_at(total, w2, t_w2 + WIPE_SEC / 2 - 0.55 * 0.65, 0.6)
    total = total[: int(t_end * SR)]
    total = np.clip(total, -1, 1)

    tmp = tempfile.mkdtemp()
    wav = os.path.join(tmp, "mix.wav")
    with wave.open(wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((total * 32767).astype("<i2").tobytes())

    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart", args.out], stdin=subprocess.PIPE)

    rng = np.random.default_rng(7)
    for i in range(nframes):
        t = i / FPS
        if t < t_w1:
            f = next(before_fr).astype(np.float32)
            f = paste_center(f, lbl_before, lbl_x(lbl_before), LBL_Y, pop_scale(t / 0.35))
        elif t < t_w1 + WIPE_SEC:
            u = (t - t_w1) / WIPE_SEC
            fb = zoom(next(before_fr).astype(np.float32), 1.0 + 0.08 * u)
            fb = paste_center(fb, lbl_before, lbl_x(lbl_before), LBL_Y)
            fa = zoom(next(after_fr).astype(np.float32), 1.18 - 0.18 * ease_out_cubic(u * 0.8))
            f = wipe(fb, fa, ease_in_out_cubic(u))
        elif t < t_w2:
            la = t - t_w1                       # time since after started
            # short camera shake as the wipe lands
            shake = max(0.0, 1 - (la - WIPE_SEC) / 0.25) * 14
            f = zoom(next(after_fr).astype(np.float32), 1.02 if shake else 1.0,
                     rng.uniform(-shake, shake), rng.uniform(-shake, shake))
            # white flash as the wipe lands
            fl = max(0.0, 1 - (la - WIPE_SEC) / 0.15) * 0.45
            if fl > 0:
                f = f * (1 - fl) + 255 * fl
            f = paste_center(f, lbl_after, lbl_x(lbl_after), LBL_Y, pop_scale((la - WIPE_SEC * 0.6) / 0.35))
        elif t < t_w2 + WIPE_SEC:
            u = (t - t_w2) / WIPE_SEC
            fa = zoom(next(after_fr).astype(np.float32), 1.0 + 0.08 * u)
            fa = paste_center(fa, lbl_after, lbl_x(lbl_after), LBL_Y)
            f = wipe(fa, split_frame(t - t_w2), ease_in_out_cubic(u))
        else:
            f = split_frame(t - t_w2)
        enc.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    print(f"wrote {args.out}: {t_end:.2f}s, {nframes} frames")


if __name__ == "__main__":
    main()
