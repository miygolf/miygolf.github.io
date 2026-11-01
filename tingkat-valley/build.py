"""Build the Tingkat Valley memory video (vertical 1080x1920, 30 fps).

Usage: python3 build.py MEDIA_DIR FONTS_DIR WORK_DIR OUTPUT.mp4 [--blur-faces]
Framing follows the Instagram Reels / TikTok safe zone: captions sit between y=260 and y=1300
so the app UI (top tabs, bottom caption/username, right-side buttons) does not cover them.
MEDIA_DIR holds the original photos/videos from the Google Drive folder.
FONTS_DIR holds GreatVibes.ttf and CormorantItalic.ttf (Google Fonts, OFL).
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

MEDIA, FONTS, WORK, OUT = sys.argv[1:5]
BLUR_FACES = "--blur-faces" in sys.argv[5:]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.makedirs(WORK, exist_ok=True)
W, H, FPS = 1080, 1920, 30
XF = 0.8  # crossfade seconds

GRADE = ("eq=contrast=1.04:saturation=1.10:gamma=1.02,"
         "colorbalance=rm=0.025:gm=0.005:bm=-0.03:rh=0.02:bh=-0.02,"
         "vignette=angle=PI/5")

# ---------------------------------------------------------------------------
# Storyboard. Photos: (file, seconds, focus_x, zoom_from, zoom_to, mode)
# Videos: (file, src_start, src_end, speed, keep_audio, layout)
# text: (big_script, small_line, y_center, appear_at, hide_at)
# ---------------------------------------------------------------------------
STORY = [
    dict(kind="photo", file="IMG_20261101_115550.jpg", dur=4.8, fx=0.5, z=(1.10, 1.0),
         text=("Tingkat Valley", "1 · 11 · 2026", 440, 0.5, 4.2)),
    dict(kind="photo", file="IMG_20261101_115614.jpg", dur=3.6, fx=0.45, z=(1.0, 1.08),
         text=(None, "it all started with a ride…", 1260, 0.4, 3.3)),
    dict(kind="video", file="FILE261101-152820-000799F.mp4", ss=4, to=32, speed=3.5, audio=False,
         layout="landscape", text=(None, "down winding green roads", 1260, 0.6, 7.2)),
    dict(kind="photo", file="IMG_20261101_153105.jpg", dur=3.8, fx=0.42, z=(1.0, 1.08),
         text=(None, "and then, we arrived", 1260, 0.5, 3.5)),
    dict(kind="video", file="VID_20261101_183948.mp4", ss=0.0, to=6.5, speed=0.75, audio=True,
         layout="portrait", text=("with you", None, 460, 1.0, 8.0)),
    dict(kind="photo", file="IMG_20261101_183850.jpg", dur=4.2, fx=0.5, z=(1.08, 1.0)),
    dict(kind="photo", file="IMG_20261101_184035.jpg", dur=4.2, fx=0.5, z=(1.0, 1.06), mode="fit"),
    dict(kind="video", file="VID_20261101_184602.mp4", ss=0.5, to=7.5, speed=0.7, audio=True,
         layout="portrait", text=(None, "where the lights glow softly", 1260, 1.0, 9.2)),
    dict(kind="photo", file="IMG_20261101_184433.jpg", dur=4.2, fx=0.54, z=(1.0, 1.08)),
    dict(kind="video", file="VID_20261101_184602.mp4", ss=21.0, to=26.6, speed=0.8, audio=True,
         layout="portrait", text=(None, "and time slowed down", 1260, 0.8, 6.4)),
    dict(kind="photo", file="IMG_20261101_184832.jpg", dur=4.2, fx=0.42, z=(1.08, 1.0)),
    dict(kind="photo", file="IMG_20261101_185209.jpg", dur=6.5, fx=0.45, z=(1.0, 1.10),
         text=("Sweet Memories", "Tingkat Valley · together", 440, 1.2, 99)),
]


def seg_duration(s):
    if s["kind"] == "photo":
        return s["dur"]
    return round((s["to"] - s["ss"]) / s["speed"], 3)


# ---------------------------------------------------------------------------
# Text overlays (transparent PNGs with soft shadow)
# ---------------------------------------------------------------------------
def text_png(idx, big, small, yc):
    path = os.path.join(WORK, f"text_{idx:02d}.png")
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(canvas), ImageDraw.Draw(shadow)
    script = ImageFont.truetype(os.path.join(FONTS, "GreatVibes.ttf"), 150)
    serif = ImageFont.truetype(os.path.join(FONTS, "CormorantItalic.ttf"), 72)
    y = yc
    items = []
    if big:
        items.append((big, script))
    if small:
        items.append((small, serif))
    heights = [d.textbbox((0, 0), t, font=f)[3] - d.textbbox((0, 0), t, font=f)[1] for t, f in items]
    gap = 30
    total = sum(heights) + gap * (len(items) - 1)
    y = yc - total // 2
    for (t, f), h in zip(items, heights):
        bb = d.textbbox((0, 0), t, font=f)
        x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        yy = y - bb[1]
        ds.text((x, yy + 4), t, font=f, fill=(0, 0, 0, 235))
        d.text((x, yy), t, font=f, fill=(255, 248, 236, 255))
        y += h + gap
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    out = Image.alpha_composite(shadow, canvas)
    out.save(path)
    return path


def text_filter(seg, idx, dur, in_label):
    """Return (extra ffmpeg inputs, filter snippet) overlaying the segment's text."""
    t = seg.get("text")
    if not t:
        return [], f"[{in_label}]null[v]"
    big, small, yc, t_in, t_out = t
    t_out = min(t_out, dur - 0.2)
    png = text_png(idx, big, small, yc)
    fl = (f"[1:v]format=rgba,fade=t=in:st={t_in}:d=0.8:alpha=1,"
          f"fade=t=out:st={t_out - 0.7}:d=0.7:alpha=1[txt];"
          f"[{in_label}][txt]overlay=0:0:shortest=1[v]")
    return ["-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", png], fl


# ---------------------------------------------------------------------------
# Segment renderers
# ---------------------------------------------------------------------------
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", "-an"]


def ease(p):
    return p * p * (3 - 2 * p)


def prep_photo(seg):
    im = ImageOps.exif_transpose(Image.open(os.path.join(MEDIA, seg["file"]))).convert("RGB")
    if BLUR_FACES:
        import faces
        boxes = [b for b in faces.detect(im) if b[4] >= 0.7]
        print(f"       blurring {len(boxes)} face(s)")
        im = faces.blur_faces(im, boxes)
    sw, sh = int(W * 1.3), int(H * 1.3)
    if seg.get("mode") == "fit":
        bg = ImageOps.fit(im, (sw // 4, sh // 4), Image.LANCZOS).filter(ImageFilter.GaussianBlur(14))
        bg = bg.resize((sw, sh), Image.BICUBIC)
        bg = Image.eval(bg, lambda v: int(v * 0.6))
        fg = im.copy()
        fg.thumbnail((sw, sh), Image.LANCZOS)
        bg.paste(fg, ((sw - fg.width) // 2, (sh - fg.height) // 2))
        return bg
    iw, ih = im.size
    cw = min(iw, round(ih * 9 / 16))
    ch = round(cw * 16 / 9)
    left = min(max(0, round(seg["fx"] * iw - cw / 2)), iw - cw)
    top = (ih - ch) // 2
    return im.crop((left, top, left + cw, top + ch)).resize((sw, sh), Image.LANCZOS)


def render_photo(seg, idx, path):
    src = prep_photo(seg)
    sw, sh = src.size
    dur = seg["dur"]
    n = int(round(dur * FPS))
    z0, z1 = seg["z"]
    extra, tf = text_filter(seg, idx, dur, "base")
    cmd = (["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"] + extra +
           ["-filter_complex", f"[0:v]{GRADE},format=yuv420p[base];{tf}", "-map", "[v]"] +
           ENC + [path])
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        e = ease(i / max(1, n - 1))
        z = z0 + (z1 - z0) * e
        # visible window in source pixels: full source width at zoom 1.0
        vw = sw / z
        vh = sh / z
        left = (sw - vw) / 2
        top = (sh - vh) / 2
        frame = src.transform((W, H), Image.AFFINE,
                              (vw / W, 0, left, 0, vh / H, top), resample=Image.BICUBIC)
        p.stdin.write(frame.tobytes())
    p.stdin.close()
    assert p.wait() == 0


def render_video(seg, idx, path):
    dur = seg_duration(seg)
    sp = seg["speed"]
    src = os.path.join(MEDIA, seg["file"])
    if seg["layout"] == "landscape":
        base = (f"[0:v]setpts=(PTS-STARTPTS)/{sp},fps={FPS},split[a][b];"
                f"[a]scale={W//4}:{H//4}:force_original_aspect_ratio=increase,crop={W//4}:{H//4},"
                f"boxblur=10:2,scale={W}:{H},eq=brightness=-0.05:saturation=1.1[bg];"
                f"[b]crop=iw*0.6:ih*0.9:iw*0.2:0,scale={W}:-2[fg];"
                f"[bg][fg]overlay=0:(H-h)/2,{GRADE},format=yuv420p[base]")
    else:
        base = (f"[0:v]setpts=(PTS-STARTPTS)/{sp},fps={FPS},"
                f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos:out_range=tv,"
                f"crop={W}:{H},{GRADE},format=yuv420p[base]")
    extra, tf = text_filter(seg, idx, dur, "base")
    cmd = (["ffmpeg", "-v", "error", "-y", "-ss", str(seg["ss"]), "-t", str(seg["to"] - seg["ss"]),
            "-i", src] + extra +
           ["-filter_complex", f"{base};{tf}", "-map", "[v]", "-t", str(dur)] + ENC + [path])
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
durs = [seg_duration(s) for s in STORY]
starts = []
acc = 0.0
for i, d in enumerate(durs):
    starts.append(acc)
    acc += d - XF
total = sum(durs) - XF * (len(durs) - 1)
print(f"segments={len(STORY)} total={total:.2f}s")

seg_paths = []
for i, s in enumerate(STORY):
    path = os.path.join(WORK, f"seg_{i:02d}.mp4")
    print(f"  [{i:02d}] {s['kind']:5s} {s['file']} {durs[i]:.2f}s @ {starts[i]:.2f}s")
    (render_photo if s["kind"] == "photo" else render_video)(s, i, path)
    seg_paths.append(path)

music = os.path.join(WORK, "music.wav")
subprocess.run([sys.executable, os.path.join(HERE, "music.py"), music, f"{total:.3f}"], check=True)

# Video crossfade chain
inputs, fc = [], []
for p in seg_paths:
    inputs += ["-i", p]
prev = "0:v"
for i in range(1, len(seg_paths)):
    off = starts[i]
    lab = f"x{i}"
    fc.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[{lab}]")
    prev = lab
fc.append(f"[{prev}]fade=t=in:st=0:d=1.0,fade=t=out:st={total - 2.0:.3f}:d=2.0,format=yuv420p[vout]")

# Audio: music + soft natural ambience from the evening clips
n_in = len(seg_paths)
inputs += ["-i", music]
amix = [f"[{n_in}:a]volume=1.0[mus]"]
labels = ["[mus]"]
k = n_in + 1
for i, s in enumerate(STORY):
    if s["kind"] == "video" and s.get("audio"):
        inputs += ["-ss", str(s["ss"]), "-t", str(s["to"] - s["ss"]), "-i", os.path.join(MEDIA, s["file"])]
        d = durs[i]
        ms = int(starts[i] * 1000)
        amix.append(f"[{k}:a]atempo={s['speed']},aformat=sample_rates=44100:channel_layouts=stereo,"
                    f"highpass=f=120,volume=0.45,afade=t=in:d=0.8,afade=t=out:st={d - 0.9:.3f}:d=0.9,"
                    f"adelay={ms}|{ms}[amb{i}]")
        labels.append(f"[amb{i}]")
        k += 1
amix.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=first,"
            f"alimiter=limit=0.95,afade=t=out:st={total - 2.5:.3f}:d=2.5[aout]")

cmd = (["ffmpeg", "-v", "error", "-y"] + inputs +
       ["-filter_complex", ";".join(fc + amix), "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-maxrate", "7M", "-bufsize", "14M", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
        "-t", f"{total:.3f}", OUT])
subprocess.run(cmd, check=True)
print("done ->", OUT)
