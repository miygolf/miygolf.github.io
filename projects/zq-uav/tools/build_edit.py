"""Cut src/raw.mp4 into assets/footage/edit_clean.mp4 (then tools/blur_plate.py -> edit.mp4) (1080x1920, 30 fps, silent) from src/cuts.json.
Each cut: [id, src_in, src_out, speed]. Prints film-time start of every cut."""
import json, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent
cuts = json.load(open(ROOT / "src/cuts.json"))
parts, t = [], 0.0
for i, (cid, a, b, sp) in enumerate(cuts):
    d = (b - a) / sp
    parts.append(f"[0:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp},fps=30,scale=1080:1920:flags=lanczos,setsar=1[v{i}]")
    print(f"{cid}: film {t:6.3f} -> {t + d:6.3f}  (src {a}-{b} x{sp})")
    t += d
fg = ";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(len(cuts))) + f"concat=n={len(cuts)}:v=1:a=0[out]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / "src/raw.mp4"), "-filter_complex", fg, "-map", "[out]",
                "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-g", "15", "-movflags", "+faststart",
                str(ROOT / "assets/footage/edit_clean.mp4")], check=True)
print("total", round(t, 3))
