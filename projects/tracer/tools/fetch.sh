#!/usr/bin/env bash
# Source clip from the owner's Drive (link-shared) -> .src/clip1.mov ; 16 kHz mono audio -> work/ for transcription
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .src work
ID=1Eq-o5p_Fp2eq6tTV5SMadKLJmaWFd0uz   # IMG_0030.MOV (the shot)
ID2=12UqDTOAvJNi5kTvF0PMTSuW86B7oKjNo  # IMG_0034.MOV (the result on the green)
[ -f .src/clip1.mov ] || curl -sSL -o .src/clip1.mov "https://drive.usercontent.google.com/download?id=$ID&export=download&confirm=t"
[ -f .src/clip2.mov ] || curl -sSL -o .src/clip2.mov "https://drive.usercontent.google.com/download?id=$ID2&export=download&confirm=t"
ffmpeg -v error -y -i .src/clip1.mov -map 0:a:0 -ac 1 -ar 16000 work/clip1.wav
ffmpeg -v error -y -i .src/clip2.mov -map 0:a:0 -ac 1 -ar 16000 work/clip2.wav
