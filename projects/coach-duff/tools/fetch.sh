#!/usr/bin/env bash
# Source clips from the owner's Drive (link-shared) -> .src/ ; 16 kHz mono audio -> work/ for transcription
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .src work
get(){ [ -f ".src/$2" ] || curl -sSL -o ".src/$2" "https://drive.usercontent.google.com/download?id=$1&export=download&confirm=t"; }
get 1EflazxjLXZt3pvU4E1Xj3bRRA1V1ppTp clip1.mov   # IMG_0187.MOV  ball's lie close-up, pan up to the flag (4.6 s)
get 1HwK3uPQilJTJR_tYBxtNPdjIIArOdBBN clip2.mov   # IMG_0188.MOV  tripod: coach sets up, duffs the pitch, laughs (31.3 s)
for i in 1 2; do ffmpeg -v error -y -i .src/clip$i.mov -map 0:a:0 -ac 1 -ar 16000 work/clip$i.wav; done
