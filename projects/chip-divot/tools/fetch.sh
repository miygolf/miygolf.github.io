#!/usr/bin/env bash
# Downloads the source clip (Google Drive, owner: MIY Golf) into .src/ and the 16 kHz audio used for transcription into .work/
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .src .work
curl -sSL -o .src/clip1.mov "https://drive.usercontent.google.com/download?id=1kLv20TB5WTc5_sDsplt48f9UK3VC4xGS&export=download&confirm=t"
ffmpeg -v error -y -i .src/clip1.mov -vn -ac 1 -ar 16000 .work/a1.wav
