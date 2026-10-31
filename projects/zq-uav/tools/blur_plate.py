"""Hide the car number plate: assets/footage/edit_clean.mp4 + src/plate_track.json -> assets/footage/edit.mp4.
Pixelates then blurs a padded box around the tracked plate, with a feathered edge."""
import cv2, json, numpy as np, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent
PAD = 1.35  # box grows 35% around the tracked plate size
tr = {int(k): v for k, v in json.load(open(ROOT / "src/plate_track.json")).items()}
cap = cv2.VideoCapture(str(ROOT / "assets/footage/edit_clean.mp4"))
W, H = int(cap.get(3)), int(cap.get(4))
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "30",
                        "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-g", "15",
                        "-movflags", "+faststart", str(ROOT / "assets/footage/edit.mp4")], stdin=subprocess.PIPE)
f = 0
while True:
    ok, img = cap.read()
    if not ok: break
    if f in tr:
        x, y, w, h = tr[f]; w, h = w * PAD, h * PAD
        x0, y0 = int(max(0, x - w / 2 - 20)), int(max(0, y - h / 2 - 20))
        x1, y1 = int(min(W, x + w / 2 + 20)), int(min(H, y + h / 2 + 20))
        if x1 - x0 > 8 and y1 - y0 > 8:
            roi = img[y0:y1, x0:x1]
            small = cv2.resize(roi, (max(1, (x1 - x0) // 14), max(1, (y1 - y0) // 14)), interpolation=cv2.INTER_AREA)
            hidden = cv2.GaussianBlur(cv2.resize(small, (x1 - x0, y1 - y0), interpolation=cv2.INTER_NEAREST), (0, 0), 7)
            m = np.zeros((y1 - y0, x1 - x0), np.float32)
            cv2.ellipse(m, (int(x - x0), int(y - y0)), (int(w / 2 + 6), int(h / 2 + 6)), 0, 0, 360, 1, -1)
            m = cv2.GaussianBlur(m, (0, 0), 6)[..., None]
            img[y0:y1, x0:x1] = (hidden * m + roi * (1 - m)).astype(np.uint8)
    enc.stdin.write(img.tobytes()); f += 1
enc.stdin.close(); enc.wait()
print("edit.mp4 written,", f, "frames,", len(tr), "with the plate hidden")
