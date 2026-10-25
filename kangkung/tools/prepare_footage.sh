#!/usr/bin/env bash
# Download the 5 source clips from Google Drive and make H.264 proxies
# (1080x1920, 30 fps, keyframe every 15 frames, loudness-normalised sound).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p assets/footage .src
declare -A IDS=(
  [A]=13_3Zv40nJHoNmaVnG0exMuwyhBVe2MEl   # VID_20261023_135625 — pour chili paste
  [B]=1AVWpJDRscRFoqp0C8vmkty3sBOsQfKU4   # stir paste
  [C]=1ayWZ3yn9MMTlbEJj79FG8vmwz6OJm3nU   # sauces + tomato
  [D]=1IEcAD0FwMoHnOLCfWcagj1mH_AvmAyjH   # kangkung in
  [E]=1CTBBf7jIrm-ysFi0Ism-R9G-4j97JQol   # plated + bottles
)
for n in "${!IDS[@]}"; do
  [ -f ".src/$n.mp4" ] || curl -sSL -o ".src/$n.mp4" "https://drive.usercontent.google.com/download?id=${IDS[$n]}&export=download&confirm=t"
  ffmpeg -v error -y -i ".src/$n.mp4" -vf "scale=1080:1920,fps=30,format=yuv420p" \
    -c:v libx264 -preset medium -crf 17 -g 15 -keyint_min 15 -sc_threshold 0 \
    -c:a aac -b:a 192k -ar 48000 -af "loudnorm=I=-19:LRA=11:TP=-2" -movflags +faststart \
    "assets/footage/$n.mp4"
done
