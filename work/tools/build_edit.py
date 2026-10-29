"""Cuts src/raw.mp4 into assets/edit.mp4: pauses, the false start ("apa-apa yang aa
lebih"), the "aa" fillers and the repeated "take away ... luar kaki kanan" line are
removed; "kita tak nak terlebih macam ni" is moved to the front as the hook."""
import json, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent
SEGS = [("H", 41.78, 43.25), ("A1", 0.00, 0.78), ("A2", 1.28, 2.58), ("A3", 2.96, 4.26),
        ("A4", 5.52, 6.30), ("B1", 11.26, 13.86), ("B2", 14.90, 16.50), ("C1", 17.44, 19.72),
        ("C2", 20.14, 21.94), ("C3", 24.06, 25.00), ("C4", 25.58, 27.22), ("D1", 29.54, 32.05),
        ("E1", 34.66, 35.98), ("E2", 37.56, 38.36), ("E3", 39.48, 41.50), ("F1", 45.48, 46.22),
        ("F2", 46.70, 49.80)]
FPS = 30
f, rows, t = [], [], 0.0
for i, (n, s, e) in enumerate(SEGS):
    s, e = round(s * FPS) / FPS, round(e * FPS) / FPS
    d = e - s
    f.append(f"[0:v]trim=start={s:.4f}:end={e:.4f},setpts=PTS-STARTPTS[v{i}]")
    f.append(f"[0:a]atrim=start={s:.4f}:end={e:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={d - 0.02:.4f}:d=0.02[a{i}]")
    rows.append((n, round(s, 3), round(e, 3), round(t, 3), round(t + d, 3)))
    t += d
f.append("".join(f"[v{i}][a{i}]" for i in range(len(SEGS))) + f"concat=n={len(SEGS)}:v=1:a=1[vc][ac]")
f.append("[vc]scale=1080:1920:flags=lanczos,unsharp=5:5:0.4[vo]")
f.append("[ac]highpass=f=75,afftdn=nr=8:nf=-30,acompressor=threshold=-18dB:ratio=2.5:attack=8:release=120,"
         "loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000[ao]")
script = ROOT / "src/edit.filtergraph"
script.write_text(";\n".join(f))
json.dump(rows, open(ROOT / "src/cuts.json", "w"), indent=0)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / "src/raw.mp4"), "-filter_complex_script", str(script),
                "-map", "[vo]", "-map", "[ao]", "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-g", "30",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                str(ROOT / "assets/edit.mp4")], check=True)
print(f"assets/edit.mp4 {t:.2f}s")
