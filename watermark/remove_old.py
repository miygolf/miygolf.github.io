#!/usr/bin/env python3
"""Remove the old baked-in @IQBAL.YUSOFF watermarks from a video by inpainting.

The old watermark only ever sits at a few fixed spots (under the PiP, mid-left,
and the end card), fading between them. For each frame we template-match each
element in a small search window; where it is present we inpaint exactly its
glyph pixels, so the rest of the frame is untouched.

  python3 watermark/remove_old.py input.mp4 output.mp4 [--debug-mask mask.mp4]

Needs: numpy, opencv-python-headless, ffmpeg.
"""
import argparse
import os
import subprocess
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "old_templates")
W, H = 1080, 1920

SEARCH = 10       # px search radius around each expected spot
HOLD = 10         # frames: keep masking this long around a confident hit (covers fades)
CONFIDENT = 0.60

# Template crops carry an 8px margin: the inner part is matched, the whole
# crop (glyph descenders/halo included) is masked.
MARGIN = 8

# name, template file, expected top-left (x, y) of the full crop
ELEMENTS = [
    ("pip_icon", "icon.png", (924, 444)),
    ("pip_text", "text.png", (774, 534)),
    ("left_icon", "icon.png", (114, 1254)),
    ("left_text", "text.png", (116, 1344)),
    ("end_text", "end_text.png", (397, 1030)),
]
# Scrolling "Shadow Bass King • Nothing is Impossible" line under the PiP text:
# no stable template, so mask thin bright strokes in this box while pip_text shows.
PIP_SUB_BOX = (636, 586, 1014, 632)   # x0, y0, x1, y1
# End-card IG logo (colour gradient on dark background).
END_ICON_BOX = (462, 828, 620, 984)


def frames(path, pix_fmt, ch):
    p = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={W}:{H}",
         "-f", "rawvideo", "-pix_fmt", pix_fmt, "-"],
        stdout=subprocess.PIPE)
    n = W * H * ch
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, ch) if ch > 1 else np.frombuffer(buf, np.uint8).reshape(H, W)
    p.wait()


def load_templates():
    t = {}
    for name, fname, pos in ELEMENTS:
        g = cv2.imread(os.path.join(TPL, fname), cv2.IMREAD_GRAYSCALE)
        # glyph = clearly brighter than the template's own background
        glyph = (g.astype(int) > np.percentile(g, 35) + 45).astype(np.uint8) * 255
        glyph = cv2.dilate(glyph, np.ones((3, 3), np.uint8), iterations=3)
        t[name] = (g, glyph, pos)
    return t


def match(gray, tpl, pos):
    tpl = tpl[MARGIN:-MARGIN, MARGIN:-MARGIN]
    th, tw = tpl.shape
    x, y = pos[0] + MARGIN, pos[1] + MARGIN
    x0, y0 = max(0, x - SEARCH), max(0, y - SEARCH)
    x1, y1 = min(W, x + tw + SEARCH), min(H, y + th + SEARCH)
    r = cv2.matchTemplate(gray[y0:y1, x0:x1], tpl, cv2.TM_CCOEFF_NORMED)
    _, mx, _, loc = cv2.minMaxLoc(r)
    return mx, (x0 + loc[0] - MARGIN, y0 + loc[1] - MARGIN)


def scan(path, tpls):
    """Pass 1: per-frame score + location for each element.

    Each element is matched on luma and on max(B, G, R) (which makes the
    gradient-coloured IG icon look like the white one); the better hit wins.
    """
    scores, locs = {k: [] for k in tpls}, {k: [] for k in tpls}
    for bgr in frames(path, "bgr24", 3):
        g = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        v = bgr.max(2)
        for k, (tpl, _, pos) in tpls.items():
            s, l = max(match(g, tpl, pos), match(v, tpl, pos))
            scores[k].append(s)
            locs[k].append(l)
    n = len(next(iter(scores.values())))
    present = {}
    for k in tpls:
        s = np.array(scores[k])
        hit = s >= CONFIDENT
        # dilate hits in time so fade-in/out frames are covered too
        k1 = np.ones(2 * HOLD + 1)
        present[k] = np.convolve(hit.astype(float), k1, "same") > 0
        # where weak, reuse nearest confident location
        last = tpls[k][2]
        fixed = []
        for i in range(n):
            if hit[i]:
                last = locs[k][i]
            fixed.append(last)
        locs[k] = fixed
    return n, present, locs


def thin_bright(gray, box, thr=10):
    x0, y0, x1, y1 = box
    roi = gray[y0:y1, x0:x1]
    top = cv2.morphologyEx(roi, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    m = (top > thr).astype(np.uint8) * 255
    return cv2.dilate(m, np.ones((3, 3), np.uint8), iterations=2)


def end_icon_mask(rgb, box):
    x0, y0, x1, y1 = box
    roi = rgb[y0:y1, x0:x1].astype(int)
    sat = roi.max(2) - roi.min(2)
    m = ((roi.max(2) > 110) | (sat > 70)).astype(np.uint8) * 255
    return cv2.dilate(m, np.ones((3, 3), np.uint8), iterations=3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--crf", default="14")
    ap.add_argument("--debug-mask", help="also write the mask as a video")
    a = ap.parse_args()

    tpls = load_templates()
    n, present, locs = scan(a.input, tpls)
    for k in tpls:
        print(f"{k:10s} present in {present[k].sum():4d}/{n} frames", file=sys.stderr)

    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
         "-i", a.input, "-map", "0:v", "-map", "1:a?",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", a.crf, "-pix_fmt", "yuv420p",
         "-c:a", "copy", "-shortest", a.output],
        stdin=subprocess.PIPE)
    dbg = None
    if a.debug_mask:
        dbg = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray",
             "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-c:v", "libx264", "-crf", "28",
             "-pix_fmt", "yuv420p", a.debug_mask],
            stdin=subprocess.PIPE)

    for i, bgr in enumerate(frames(a.input, "bgr24", 3)):
        if i >= n:
            break
        bgr = bgr.copy()
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        mask = np.zeros((H, W), np.uint8)
        for k, (_, glyph, _) in tpls.items():
            if present[k][i]:
                x, y = locs[k][i]
                gh, gw = glyph.shape
                mask[y:y + gh, x:x + gw] |= glyph
        if present["pip_text"][i]:
            x0, y0, x1, y1 = PIP_SUB_BOX
            mask[y0:y1, x0:x1] |= thin_bright(gray, PIP_SUB_BOX)
        if present["end_text"][i]:
            x0, y0, x1, y1 = END_ICON_BOX
            mask[y0:y1, x0:x1] |= end_icon_mask(bgr, END_ICON_BOX)
        if mask.any():
            bgr = cv2.inpaint(bgr, mask, 6, cv2.INPAINT_TELEA)
        enc.stdin.write(bgr.tobytes())
        if dbg:
            dbg.stdin.write(mask.tobytes())

    enc.stdin.close()
    enc.wait()
    if dbg:
        dbg.stdin.close()
        dbg.wait()
    print(f"done -> {a.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
