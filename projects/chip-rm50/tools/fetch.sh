#!/usr/bin/env bash
# Source clip from the owner's Drive (link-shared) -> .src/clip1.mov ; 16 kHz mono audio -> work/ for transcription
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .src work
ID=1sNjCS2huX0XgUHE-S69Y_y_r33rGjDGI   # chip 30 m, RM50 bet (29.0 s)
[ -f .src/clip1.mov ] || curl -sSL -o .src/clip1.mov "https://drive.usercontent.google.com/download?id=$ID&export=download&confirm=t"
ffmpeg -v error -y -i .src/clip1.mov -map 0:a:0 -ac 1 -ar 16000 work/clip1.wav
