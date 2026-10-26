#!/usr/bin/env python3
"""Blur the golfer's face through a whole clip (pre-pass for transformasi.py).

Tracks the head with MediaPipe Pose (works even when the face is turned away
mid-swing), smooths the track, and covers it with a feathered heavy blur.
Output keeps the clip's own audio and is rendered at 1080x1920 / 60fps.

Usage:
  python3 blur_face.py --model pose_landmarker_heavy.task in.mp4 out.mp4
"""
import argparse
import subprocess

import cv2
import mediapipe as mp
import numpy as np

W, H, FPS = 1080, 1920, 60
HEAD = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]   # nose, eyes, ears, mouth
L_SH, R_SH, L_HIP, R_HIP = 11, 12, 23, 24
MIN_R = 60


def frames(path):
    proc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-i", path, "-an",
        "-vf", f"fps={FPS},scale={W}:{H}:flags=lanczos",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        buf = proc.stdout.read(n)
        if len(buf) < n:
            break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    proc.wait()


def head_of(lms):
    """(cx, cy, r) in pixels for one pose."""
    pts = np.array([(lms[i].x * W, lms[i].y * H) for i in HEAD])
    cx, cy = pts.mean(0)
    sh = np.array([(lms[i].x * W, lms[i].y * H) for i in (L_SH, R_SH)]).mean(0)
    hip = np.array([(lms[i].x * W, lms[i].y * H) for i in (L_HIP, R_HIP)]).mean(0)
    torso = np.linalg.norm(sh - hip)
    spread = np.ptp(pts, 0).max()
    return cx, cy, max(0.34 * torso, 0.9 * spread, MIN_R)


def track(path, model):
    opts = mp.tasks.vision.PoseLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=model),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_poses=3, min_pose_detection_confidence=0.3,
        min_tracking_confidence=0.3)
    out, prev = [], None
    with mp.tasks.vision.PoseLandmarker.create_from_options(opts) as det:
        for i, f in enumerate(frames(path)):
            res = det.detect_for_video(
                mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f)),
                int(i * 1000 / FPS))
            heads = [head_of(p) for p in res.pose_landmarks]
            if not heads:
                out.append(None)
                continue
            if prev is None:
                # the client is the biggest person in frame
                h = max(heads, key=lambda h: h[2])
            else:
                h = min(heads, key=lambda h: np.hypot(h[0] - prev[0], h[1] - prev[1]))
                if np.hypot(h[0] - prev[0], h[1] - prev[1]) > 4 * prev[2]:
                    out.append(None)        # only a bystander found this frame
                    continue
            out.append(h)
            prev = h
    return out


def smooth(track_, win=7):
    a = np.array([t if t is not None else (np.nan,) * 3 for t in track_], float)
    idx = np.arange(len(a))
    for c in range(3):
        ok = ~np.isnan(a[:, c])
        a[:, c] = np.interp(idx, idx[ok], a[ok, c])
    k = np.ones(win) / win
    pad = np.pad(a, ((win // 2, win // 2), (0, 0)), mode="edge")
    return np.stack([np.convolve(pad[:, c], k, "valid") for c in range(3)], 1)


def cover(f, cx, cy, r):
    rx, ry = r * 1.05, r * 1.25
    x0, x1 = int(max(cx - rx * 1.4, 0)), int(min(cx + rx * 1.4, W))
    y0, y1 = int(max(cy - ry * 1.4, 0)), int(min(cy + ry * 1.4, H))
    if x1 <= x0 or y1 <= y0:
        return f
    roi = f[y0:y1, x0:x1].astype(np.float32)
    # pixelate then blur: unreadable but still looks smooth on screen
    small = cv2.resize(roi, (max(1, roi.shape[1] // 18), max(1, roi.shape[0] // 18)),
                       interpolation=cv2.INTER_AREA)
    blurred = cv2.GaussianBlur(cv2.resize(small, roi.shape[1::-1], interpolation=cv2.INTER_LINEAR),
                               (0, 0), r * 0.15)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    m = np.clip((1.15 - d) / 0.15, 0, 1)[..., None]       # feathered ellipse
    out = f.copy()
    out[y0:y1, x0:x1] = (roi * (1 - m) + blurred * m).astype(np.uint8)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--debug", action="store_true", help="draw the tracked head circle")
    ap.add_argument("src")
    ap.add_argument("dst")
    args = ap.parse_args()

    raw = track(args.src, args.model)
    found = sum(t is not None for t in raw)
    print(f"{args.src}: head found in {found}/{len(raw)} frames")
    heads = smooth(raw)

    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", args.src, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
        "-crf", "14", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", args.dst],
        stdin=subprocess.PIPE)
    for f, (cx, cy, r) in zip(frames(args.src), heads):
        f = cover(f, cx, cy, r)
        if args.debug:
            f = cv2.circle(f.copy(), (int(cx), int(cy)), int(r), (0, 255, 255), 3)
        enc.stdin.write(f.tobytes())
    enc.stdin.close()
    enc.wait()


if __name__ == "__main__":
    main()
