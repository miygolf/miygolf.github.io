#!/usr/bin/env bash
# Source clips from the owner's Drive (link-shared) -> .src/clip1..3.mov ; 16 kHz mono audio -> work/ for transcription
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .src work
IDS=(1MSj1Gy8GHw6MnQPFcC9HlQU5y6qc4Vkd 1jinchzNSKeJyLfXMwborOD0mXD1mS_Ui 1VFRN9BmISdK1vTmk4S5yOYWa2cERROVD)   # IMG_0058, IMG_0062, IMG_0063
for i in 1 2 3; do
  id=${IDS[$((i-1))]}
  [ -f ".src/clip$i.mov" ] || curl -sSL -o ".src/clip$i.mov" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
  ffmpeg -v error -y -i ".src/clip$i.mov" -map 0:a:0 -ac 1 -ar 16000 "work/clip$i.wav"
done
