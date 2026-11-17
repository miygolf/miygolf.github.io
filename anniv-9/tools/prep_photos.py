"""Prepare polaroid windows (3:4 portrait or 4:3 landscape) and blurred full-frame backgrounds."""
import sys, os, glob, json
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
RAW, OUT = sys.argv[1], sys.argv[2]
# vertical anchor (0 top .. 1 bottom) for 9:16 sources so faces stay in the 3:4 window
ANCHOR = {"IMG_20250607_120505": 0.72, "IMG_20250629_153305": 0.70, "IMG_20250714_081028": 0.80,
          "IMG_20250810_082150": 0.55, "IMG_20250712_133729": 0.5}
def key(f): return os.path.basename(f).replace("IMG_", "")
meta = []
for f in sorted(glob.glob(os.path.join(RAW, "*.jpg")), key=key):
    name = os.path.splitext(os.path.basename(f))[0]
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    land = im.width > im.height
    W, H = (1280, 960) if land else (1200, 1600)
    s = max(W / im.width, H / im.height); r = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    a = ANCHOR.get(name, 0.5)
    l = (r.width - W) // 2; t = int((r.height - H) * a)
    r.crop((l, t, l + W, t + H)).save(f"{OUT}/cards/{name}.jpg", quality=90)
    # blurred background
    s2 = max(1080 / im.width, 1920 / im.height); b = im.resize((round(im.width * s2), round(im.height * s2)), Image.LANCZOS)
    l2, t2 = (b.width - 1080) // 2, (b.height - 1920) // 2
    b = b.crop((l2, t2, l2 + 1080, t2 + 1920)).resize((270, 480)).filter(ImageFilter.GaussianBlur(10)).resize((1080, 1920), Image.BICUBIC)
    b = ImageEnhance.Brightness(ImageEnhance.Color(b).enhance(0.8)).enhance(0.55)
    b.save(f"{OUT}/bg/{name}.jpg", quality=85)
    d = name.replace("IMG_", "")[:8]
    meta.append({"name": name, "land": land, "date": d})
    print(name, "land" if land else "port")
# full-bleed hook image (9:16)
h = ImageOps.exif_transpose(Image.open(os.path.join(RAW, "IMG_20250712_133729.jpg"))).convert("RGB").resize((1080, 1920), Image.LANCZOS)
h.save(f"{OUT}/cards/hook.jpg", quality=92)
json.dump(meta, open(f"{OUT}/photos.json", "w"), indent=1)
