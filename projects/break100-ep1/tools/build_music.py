#!/usr/bin/env python3
"""Background music under the voice-over.
v4 (owner: "background music yang berterusan macam kau buat presentation, bagi orang rasa best untuk dengar sampai habis"):
Mixkit "Digital Clouds" (id 175, corporate/chill, steady level) as a CONTINUOUS bed: constant presence from frame 0 to the end card,
only a gentle 3 dB dip under the voice (no pumping), voice ~13 dB on top.
(v3 used "Sleepy Cat" with heavy ducking: too sleepy and it came and went.)
Mixkit "Sleepy Cat" (id 135, lo-fi, ~67 bpm, Mixkit free licence) -> assets/music_bed.wav:
trimmed to the film, 1.5 s fade-in, 2.5 s fade-out, sidechain-ducked by the voice (assets/voice.wav) and set ~18-20 dB under the voice while speaking,
so the voice stays on top; it rises gently in the pauses. Run after build_voice.py: python3 tools/build_music.py <total_seconds>
"""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
total = float(sys.argv[1])
src = os.path.join(ROOT, "assets", "music", "mixkit-175-digital-clouds.mp3")
voice = os.path.join(ROOT, "assets", "voice.wav")
out = os.path.join(ROOT, "assets", "music_bed.wav")
fc = (f"[0:a]atrim=0:{total},asetpts=N/SR/TB,aresample=48000,aformat=channel_layouts=stereo,"
      f"loudnorm=I=-27:TP=-6:LRA=5,afade=t=in:d=0.6,afade=t=out:st={total - 2.2}:d=2.2[m];"
      "[1:a]aresample=48000,aformat=channel_layouts=stereo,apad[k];"
      "[m][k]sidechaincompress=threshold=0.12:ratio=1.6:attack=120:release=900:makeup=1[d]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", voice, "-filter_complex", fc, "-map", "[d]", "-t", str(total), out], check=True)
print("music bed", out)
