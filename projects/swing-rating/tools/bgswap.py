#!/usr/bin/env python3
"""Background swap: puts each source clip on the Xpark PJ South range photo (.src/xpark/xpark_pj_south.jpg, supplied by the owner).

Per clip (tripod, so the background never moves):
  person  = MediaPipe selfie-multiclass segmentation on a square crop round the pose box, edge-refined with a guided filter
  club    = pixels that differ from a clean plate of the clip's own background (per-pixel median over frames where the person
            isn't there), outside the body: keeps the shaft and club head, which the person model drops
  ground  = the mat, feet, ball and real shadow are kept from the footage (rows below GROUND, feathered), so he stands on something
  alpha = max(person, club, ground); background = a 9:16 crop of the photo, upscaled, light blur (depth of field), tone-matched.
Writes .src/comp/clip<i>.mov (1080x1920, 59.94 fps, every source frame, near-lossless H.264) that build_aroll.py reads instead of the
original video. Audio still comes from the original clip.

  python3 tools/bgswap.py [clip ...] [--test]     (--test: a few key frames -> work/bgswap_proto.jpg, no video)
"""
import json, os, subprocess, sys
import cv2, numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
FPS = "60000/1001"
PHOTO = os.path.join(ROOT, ".src", "xpark", "xpark_pj_south.jpg")
POSE = json.load(open(os.path.join(ROOT, "edit", "pose.json")))
# per clip: photo crop x (633 wide = 9:16 of the 1125 tall photo), ground line (film px, rows below are kept from the footage), feather
CFG = {
    3: dict(view="dtl", crop_x=1340, ground=1365, feather=40),
    1: dict(view="dtl", crop_x=1340, ground=1435, feather=40),
    2: dict(view="face", crop_x=60, ground=1325, feather=36),
    4: dict(view="face", crop_x=60, ground=1185, feather=36),
}
TEST = {3: [168, 183], 1: [84, 100], 2: [54, 69], 4: [84, 105]}

_seg = None
def segmenter():
    global _seg
    if _seg is None:
        _seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
            base_options=mpt.BaseOptions(model_asset_path=os.path.join(ROOT, "work", "seg.tflite")), output_confidence_masks=True))
    return _seg


def read_frames(clip):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, ".src", f"clip{clip}.mov"), "-vf", f"scale={W}:{H}:flags=lanczos",
                          "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def person_mask(img, lms):
    xs = [p[0] * W for p in lms]; ys = [p[1] * H for p in lms]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    side = int(max(max(xs) - min(xs), max(ys) - min(ys)) * 1.45 + 120)
    x0, y0 = int(cx - side / 2), int(cy - side / 2)
    pad = np.zeros((side, side, 3), np.uint8)
    sx0, sy0, sx1, sy1 = max(x0, 0), max(y0, 0), min(x0 + side, W), min(y0 + side, H)
    pad[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = img[sy0:sy1, sx0:sx1]
    r = segmenter().segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(pad)))
    m = 1.0 - r.confidence_masks[0].numpy_view().astype(np.float32)
    m = cv2.resize(m, (side, side), interpolation=cv2.INTER_LINEAR)
    out = np.zeros((H, W), np.float32)
    out[sy0:sy1, sx0:sx1] = m[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0]
    return out


def refine(img, m):
    g = cv2.ximgproc.guidedFilter(guide=img, src=m, radius=6, eps=0.01 * 255 * 255 * 0.02)
    return np.clip(g, 0, 1)


def background(cfg, plate, keep):
    ph = cv2.cvtColor(cv2.imread(PHOTO), cv2.COLOR_BGR2RGB)
    x = cfg["crop_x"]; crop = ph[:, x:x + 633]
    bg = cv2.resize(crop, (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    bg = cv2.GaussianBlur(bg, (0, 0), 2.2)
    # tone match halfway toward the footage's own background (exposure/white balance of the day), measured on visible plate pixels
    sel = keep[..., 0] < 0.05
    for c in range(3):
        mb, sb = bg[..., c][sel].mean(), bg[..., c][sel].std() + 1e-3
        mf, sf = plate[..., c][sel].mean(), plate[..., c][sel].std() + 1e-3
        bg[..., c] = (bg[..., c] - mb) * (1 + 0.5 * (sf / sb - 1)) + mb + 0.5 * (mf - mb)
    return np.clip(bg, 0, 255)


def ground_mask(cfg):
    y = np.arange(H, dtype=np.float32)[:, None]
    g = np.clip((y - (cfg["ground"] - cfg["feather"])) / (2 * cfg["feather"]), 0, 1)
    return np.repeat(g, W, axis=1)


def process(clip, test=False):
    cfg = CFG[clip]
    print(f"clip{clip}: reading", flush=True)
    F = read_frames(clip); n = len(F)
    lm = POSE[f"clip{clip}"]
    # the face-on phone drifts a pixel or two: estimate each frame's shift against frame 0 on the background only (ECC, translation)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61))
    small = lambda im: cv2.resize(cv2.cvtColor(im, cv2.COLOR_RGB2GRAY), (W // 4, H // 4)).astype(np.float32)
    ref = small(F[0])
    pmask = {}
    def pm_of(i):
        if i not in pmask:
            pmask[i] = person_mask(F[i], lm[i])
        return pmask[i]
    shifts = np.zeros((n, 2), np.float32)
    for i in range(1, n):
        m = (cv2.dilate((pm_of(i) > 0.3).astype(np.uint8), k) == 0).astype(np.uint8)
        m = cv2.resize(m, (W // 4, H // 4), interpolation=cv2.INTER_NEAREST)
        wm = np.eye(2, 3, dtype=np.float32); wm[:, 2] = shifts[i - 1] / 4
        try:
            _, wm = cv2.findTransformECC(ref, small(F[i]), wm, cv2.MOTION_TRANSLATION,
                                         (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 60, 1e-4), m, 5)
        except cv2.error:
            pass
        shifts[i] = wm[:, 2] * 4
        if i % 3: pmask.pop(i, None)
    print(f"  clip{clip} drift: max |dx| {np.abs(shifts[:, 0]).max():.1f}px |dy| {np.abs(shifts[:, 1]).max():.1f}px", flush=True)
    to_ref = lambda im, i: cv2.warpAffine(im, np.float32([[1, 0, -shifts[i, 0]], [0, 1, -shifts[i, 1]]]), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    to_frm = lambda im, i: cv2.warpAffine(im, np.float32([[1, 0, shifts[i, 0]], [0, 1, shifts[i, 1]]]), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    # clean plate (frame-0 coords): per-pixel median over sampled frames where the (dilated) person mask is off
    idx = list(range(0, n, 4))
    stack = np.empty((len(idx), H, W, 3), np.uint8); valid = np.empty((len(idx), H, W), bool)
    for j, i in enumerate(idx):
        pm = cv2.dilate((pm_of(i) > 0.3).astype(np.uint8), k)
        stack[j] = to_ref(F[i], i); valid[j] = to_ref(pm, i) == 0
    pmask.clear()
    plate = np.zeros((H, W, 3), np.float32); have = np.zeros((H, W), bool)
    for y0 in range(0, H, 96):                                   # row blocks keep the NaN median small in memory
        blk = stack[:, y0:y0 + 96].astype(np.float32); vb = valid[:, y0:y0 + 96]
        blk[~vb] = np.nan
        with np.errstate(all="ignore"):
            import warnings; warnings.simplefilter("ignore")
            med = np.nanmedian(blk, axis=0)
        have[y0:y0 + 96] = ~np.isnan(med[..., 0]); plate[y0:y0 + 96] = np.nan_to_num(med, nan=0.0)
    del stack, valid
    gx = cv2.Sobel(cv2.cvtColor(plate.astype(np.uint8), cv2.COLOR_RGB2GRAY), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(cv2.cvtColor(plate.astype(np.uint8), cv2.COLOR_RGB2GRAY), cv2.CV_32F, 0, 1, ksize=3)
    edge = cv2.dilate(np.hypot(gx, gy), np.ones((3, 3), np.uint8))           # busy plate edges need a bigger difference
    haveU = have.astype(np.uint8)
    gm = ground_mask(cfg)
    bg = background(cfg, plate, np.maximum(gm, (~have).astype(np.float32))[..., None])
    frames = TEST[clip] if test else range(n)
    out = []
    if not test:
        os.makedirs(os.path.join(ROOT, ".src", "comp"), exist_ok=True)
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", FPS, "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "10", "-pix_fmt", "yuv420p",
                                "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                                os.path.join(ROOT, ".src", "comp", f"clip{clip}.mov")], stdin=subprocess.PIPE)
    ko = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    for i in frames:
        img = F[i]
        pm = refine(img, person_mask(img, lm[i]))
        pl = to_frm(plate, i); hv = to_frm(haveU, i) > 0; ed = to_frm(edge, i)
        d = np.abs(img.astype(np.float32) - pl).max(axis=2) - 0.25 * ed
        # club can only be within ~a club length of the hands: kills leaf / pillar flicker elsewhere
        L = lm[i]; hx, hy = (L[15][0] + L[16][0]) / 2 * W, (L[15][1] + L[16][1]) / 2 * H
        tor = np.hypot((L[11][0] + L[12][0] - L[23][0] - L[24][0]) / 2 * W, (L[11][1] + L[12][1] - L[23][1] - L[24][1]) / 2 * H)
        near = np.zeros((H, W), np.uint8); cv2.circle(near, (int(hx), int(hy)), int(2.1 * tor), 1, -1)
        mot = ((d > 40) & hv & (near > 0)).astype(np.uint8)
        mot = cv2.morphologyEx(mot, cv2.MORPH_OPEN, ko)
        cnt, lab, st, _ = cv2.connectedComponentsWithStats(mot, 8)
        keepc = np.zeros(cnt, np.uint8); keepc[1:] = st[1:, cv2.CC_STAT_AREA] >= 25
        mot = keepc[lab].astype(np.float32)
        mot = cv2.GaussianBlur(cv2.dilate(mot, ko), (0, 0), 1.2)
        a = np.maximum.reduce([pm, np.clip(mot * 1.4, 0, 1), gm])[..., None]
        comp = (img * a + bg * (1 - a)).astype(np.uint8)
        if test:
            out.append(comp)
        else:
            enc.stdin.write(comp.tobytes())
            if i % 40 == 0: print(f"  clip{clip} {i}/{n}", flush=True)
    if test:
        return out
    enc.stdin.close(); enc.wait()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    clips = [int(a) for a in args] or [3, 2, 4, 1]
    if "--test" in sys.argv:
        tiles = []
        for c in clips:
            tiles += process(c, test=True)
        sheet = np.hstack([cv2.resize(t, (540, 960)) for t in tiles])
        cv2.imwrite(os.path.join(ROOT, "work", "bgswap_proto.jpg"), cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR))
        print("work/bgswap_proto.jpg")
    else:
        for c in clips:
            process(c)
