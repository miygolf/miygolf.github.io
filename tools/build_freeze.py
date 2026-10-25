"""Builds a freeze-frame breakdown clip: plays a segment and holds chosen frames (30 fps, frame-exact).

Usage: build_freeze.py <in.mp4> <out.mp4> <start_frame> <freeze_frame>:<hold_frames> [...]
Prints the local hold windows (seconds) for timing the graphics.
"""
import subprocess, sys

src, out, start = sys.argv[1], sys.argv[2], int(sys.argv[3])
holds = [tuple(map(int, a.split(":"))) for a in sys.argv[4:]]
parts, cur, t, windows = [], start, 0, []
for i, (f, n) in enumerate(holds):
    parts.append(f"[0:v]trim=start_frame={cur}:end_frame={f},setpts=N/30/TB[p{i}]")
    parts.append(f"[0:v]trim=start_frame={f}:end_frame={f + 1},setpts=N/30/TB,loop=loop={n - 1}:size=1:start=0[h{i}]")
    t += (f - cur) / 30
    windows.append((round(t, 3), round(t + n / 30, 3)))
    t += n / 30
    cur = f + 1
labels = "".join(f"[p{i}][h{i}]" for i in range(len(holds)))
fc = ";".join(parts) + f";{labels}concat=n={2 * len(holds)}:v=1:a=0,fps=30[v]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", fc, "-map", "[v]",
                "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-g", "30", "-an", out], check=True)
print("holds", windows, "total", round(t, 3))
