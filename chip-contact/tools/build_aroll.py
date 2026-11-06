"""Build the A-roll (video only) and the voice track from edit/edl.json.

Slow-motion uses motion-compensated interpolation (minterpolate) so 30 fps
footage stays smooth at 0.4-0.5x. Freezes are held single frames, also exported
as JPG stills so the riso "print" treatment can sit on top of them.
Prints the output timeline (film seconds) for every segment.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
edl = json.load(open("edit/edl.json"))
src = edl["source"]
FPS = 30
tmp = "edit/segs"
os.makedirs(tmp, exist_ok=True)
os.makedirs("assets/stills", exist_ok=True)
ENC = ["-an", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", "15"]


def run(cmd):
    subprocess.run(cmd, check=True)


timeline = []
t = 0.0
lst = []
for i, s in enumerate(edl["segments"]):
    out = f"{tmp}/{i:02d}-{s['id']}.mp4"
    if "freeze" in s:
        still = f"assets/stills/{s['id']}.jpg"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['freeze']:.3f}", "-i", src, "-frames:v", "1", "-q:v", "1", still])
        n = round(s["dur"] * FPS)
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", still, "-frames:v", str(n),
             "-vf", "scale=1080:1920,setsar=1,format=yuv420p"] + ENC + [out])
        d = n / FPS
    else:
        span = s["end"] - s["src"]
        sp = s["speed"]
        n = round(span / sp * FPS)
        vf = ""
        if sp != 1.0:
            # interpolate to FPS/sp, then stretch time by 1/sp so playback is FPS
            vf = f"minterpolate=fps={FPS / sp:.4f}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,setpts=PTS/{sp},fps={FPS},"
        vf = f"trim=duration={span + 0.2:.3f},setpts=PTS-STARTPTS,{vf}setsar=1,tpad=stop_mode=clone:stop_duration=1"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['src']:.3f}", "-i", src, "-vf", vf, "-frames:v", str(n)] + ENC + [out])
        d = n / FPS
    lst.append(f"file '{os.path.basename(out)}'")
    timeline.append({**s, "t0": round(t, 4), "t1": round(t + d, 4)})
    t += d

open(f"{tmp}/list.txt", "w").write("\n".join(lst) + "\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt", "-c", "copy", "-movflags", "+faststart", "assets/aroll.mp4"])
total = round(t, 4)

# ---- voice track: coach lines + the 1x take's own sound, cleaned and lifted ----
parts = []
for v in edl["voice"]:
    parts.append((v["src"], v["end"], v["at"]))
for seg in timeline:
    if seg.get("audio"):
        parts.append((seg["src"], seg["end"], seg["t0"]))
F = 0.03
chains = []
for k, (a, b, at) in enumerate(parts):
    d = b - a
    chains.append(f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,afade=t=in:d={F},afade=t=out:st={d - F:.3f}:d={F},adelay={int(at * 1000)}|{int(at * 1000)}[p{k}]")
mix = "".join(f"[p{k}]" for k in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0,"
# cleanup: rumble cut, broadband denoise, presence lift, gentle compression
mix += "highpass=f=90,afftdn=nr=12:nf=-42,equalizer=f=3000:t=q:w=1.2:g=3,acompressor=threshold=-24dB:ratio=3:attack=5:release=120:makeup=2,"
mix += f"apad=whole_dur={total},atrim=0:{total},volume=VOLUME_DB dB[out]"
fc = ";".join(chains) + ";" + mix


def render_voice(gain_db, path):
    run(["ffmpeg", "-v", "error", "-y", "-i", ".src/raw.MOV", "-filter_complex", fc.replace("VOLUME_DB", f"{gain_db:.2f}"),
         "-map", "[out]", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s24le", path])


# measure the coach's line alone and lift it so speech sits at about -16 LUFS
render_voice(0, f"{tmp}/voice0.wav")
v0 = edl["voice"][0]
r = subprocess.run(["ffmpeg", "-i", f"{tmp}/voice0.wav", "-ss", str(v0["at"]), "-t", str(v0["end"] - v0["src"]), "-af", "ebur128", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
I = float([ln for ln in r.splitlines() if ln.strip().startswith("I:")][-1].split()[1])
gain = -16.0 - I
render_voice(gain, "assets/voice.wav")
print(f"voice line measured {I:.1f} LUFS -> gain {gain:+.1f} dB")

json.dump({"total": total, "segments": timeline}, open("edit/timeline.json", "w"), indent=1)
for seg in timeline:
    print(f"{seg['id']:12s} {seg['t0']:6.3f}-{seg['t1']:6.3f}")
print("total", total)
