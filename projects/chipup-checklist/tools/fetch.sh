#!/usr/bin/env bash
# Source clip from the owner's Drive (link-shared) -> .src/clip1.mov ; 16 kHz mono audio -> work/ for transcription
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .src work
ID=1rbIagHxNsKkSNS3PHLpE7W0XRQhWeI9y   # chip up by the bunker (27.0 s)
[ -f .src/clip1.mov ] || curl -sSL -o .src/clip1.mov "https://drive.usercontent.google.com/download?id=$ID&export=download&confirm=t"
ffmpeg -v error -y -i .src/clip1.mov -map 0:a:0 -ac 1 -ar 16000 work/clip1.wav
