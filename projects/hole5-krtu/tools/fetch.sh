#!/usr/bin/env bash
# Downloads the four source clips (Google Drive, owner: MIY Golf) into .src/ and the 16 kHz audio used for transcription into .work/
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .src .work
i=1
for id in 1ZzNJxSLWod0F1v6jq3jRIffi10cjM7Im 1b1f8zvgIrifJLFH6jIA6K0_ORCz9cIL- 1sO-Inq0-67pEuEl7M70uRapo1l4RccBE 1iv0CIDRN5Tp4l6kxFF8rRq82BZXriEA8; do
  curl -sSL -o ".src/clip$i.mov" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
  ffmpeg -v error -y -i ".src/clip$i.mov" -vn -ac 1 -ar 16000 ".work/a$i.wav"
  i=$((i+1))
done
