"""Face detection + blurring helpers (OpenCV YuNet).

Model: face_detection_yunet_2023mar.onnx from opencv_zoo, path given by YUNET_MODEL env var.
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

MODEL = os.environ.get("YUNET_MODEL", "face_detection_yunet_2023mar.onnx")


def detect(img_rgb, max_side=1600, thresh=0.6):
    """Return list of (x, y, w, h, score) face boxes in img coordinates.

    Runs at two scales (overall + 2x2 tiles) so both large selfies and small faces are found.
    """
    arr = np.asarray(img_rgb)[:, :, ::-1]  # RGB -> BGR
    ih, iw = arr.shape[:2]
    boxes = []

    def run(sub, ox, oy):
        sh, sw = sub.shape[:2]
        s = min(1.0, max_side / max(sw, sh))
        small = cv2.resize(sub, (int(sw * s), int(sh * s)), interpolation=cv2.INTER_AREA)
        det = cv2.FaceDetectorYN.create(MODEL, "", (small.shape[1], small.shape[0]), thresh, 0.3, 5000)
        _, faces = det.detect(small)
        if faces is None:
            return
        for f in faces:
            x, y, w, h = f[:4] / s
            boxes.append((x + ox, y + oy, w, h, float(f[-1])))

    run(arr, 0, 0)
    # overlapping tiles for small/distant faces
    th, tw = ih // 2, iw // 2
    for ty in (0, ih // 4, ih // 2):
        for tx in (0, iw // 4, iw // 2):
            run(arr[ty:ty + th, tx:tx + tw], tx, ty)
    return nms(boxes)


def nms(boxes, iou_thr=0.3):
    boxes = sorted(boxes, key=lambda b: -b[4])
    keep = []
    for b in boxes:
        if all(iou(b, k) < iou_thr for k in keep):
            keep.append(b)
    return keep


def iou(a, b):
    ax2, ay2, bx2, by2 = a[0] + a[2], a[1] + a[3], b[0] + b[2], b[1] + b[3]
    ix = max(0, min(ax2, bx2) - max(a[0], b[0]))
    iy = max(0, min(ay2, by2) - max(a[1], b[1]))
    inter = ix * iy
    union = a[2] * a[3] + b[2] * b[3] - inter
    return inter / union if union else 0


def blur_faces(img, boxes, grow=1.45):
    """Return a copy of PIL image with each face covered by a feathered, heavy blur."""
    if not boxes:
        return img
    iw, ih = img.size
    mask = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(mask)
    biggest = 0
    for x, y, w, h, _ in boxes:
        cx, cy = x + w / 2, y + h / 2
        rw, rh = w * grow / 2, h * grow * 1.1 / 2
        d.ellipse((cx - rw, cy - rh, cx + rw, cy + rh), fill=255)
        biggest = max(biggest, w)
    feather = max(4, int(biggest * 0.08))
    mask = mask.filter(ImageFilter.GaussianBlur(feather))
    radius = max(12, int(biggest * 0.22))
    # pixelate-then-blur gives a strong, non-recoverable smear
    small = img.resize((max(1, iw // 8), max(1, ih // 8)), Image.BILINEAR)
    blurred = small.resize(img.size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(radius / 8 + 2))
    blurred = blurred.filter(ImageFilter.GaussianBlur(radius))
    return Image.composite(blurred, img, mask)
