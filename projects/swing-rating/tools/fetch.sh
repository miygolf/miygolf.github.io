#!/usr/bin/env bash
# Source clips from the owner's Drive (link-shared) -> .src/clip<n>.mov ; 16 kHz mono audio + every frame at 540x960 -> work/
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .src work/f
IDS=(1IUSsSk9XTuJe3bY0WBb9GbXpaSqz5M4X 1Twj1hCFl63O6Mw67kNPGBZxXiCpcxvVf 1wyN0ltJgXBlNM85J-_Xhr-FwsXQcwYKo 1RyxgL0z4Hx3ihvw2lSw-aptm9utD31id)
for i in 1 2 3 4; do
  [ -f .src/clip$i.mov ] || curl -sSL -o .src/clip$i.mov "https://drive.usercontent.google.com/download?id=${IDS[$((i-1))]}&export=download&confirm=t"
  ffmpeg -v error -y -i .src/clip$i.mov -map 0:a:0 -ac 1 -ar 16000 work/clip$i.wav
  ffmpeg -v error -y -i .src/clip$i.mov -vf scale=540:960 -q:v 3 work/f/c${i}_%03d.jpg
done
# pose model for tools/pose.py
[ -f work/pose_heavy.task ] || curl -sSL -o work/pose_heavy.task https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task
