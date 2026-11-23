#!/usr/bin/env python3
"""Slow background music bed (owner: "tambah background music slow je") under the voice-over.
Mixkit "Sleepy Cat" (id 135, lo-fi, ~67 bpm, Mixkit free licence) -> assets/music_bed.wav:
trimmed to the film, 1.5 s fade-in, 2.5 s fade-out, sidechain-ducked by the voice (assets/voice.wav) and set ~18-20 dB under the voice while speaking,
so the voice stays on top; it rises gently in the pauses. Run after build_voice.py: python3 tools/build_music.py <total_seconds>
"""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
total = float(sys.argv[1])
src = os.path.join(ROOT, "assets", "music", "mixkit-135-sleepy-cat.mp3")
voice = os.path.join(ROOT, "assets", "voice.wav")
out = os.path.join(ROOT, "assets", "music_bed.wav")
fc = (f"[0:a]atrim=0:{total},asetpts=N/SR/TB,aresample=48000,aformat=channel_layouts=stereo,"
      f"loudnorm=I=-28:TP=-8:LRA=7,afade=t=in:d=1.5,afade=t=out:st={total - 2.5}:d=2.5[m];"
      "[1:a]aresample=48000,aformat=channel_layouts=stereo,apad[k];"
      "[m][k]sidechaincompress=threshold=0.05:ratio=3:attack=40:release=500:makeup=1[d]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", voice, "-filter_complex", fc, "-map", "[d]", "-t", str(total), out], check=True)
print("music bed", out)
