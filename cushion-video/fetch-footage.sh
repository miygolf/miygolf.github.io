#!/usr/bin/env bash
# Downloads the three source clips from the shared Drive folder and converts them
# to H.264 (Chrome cannot decode the phone's HEVC) with the rotation applied.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p assets/footage .src
declare -A IDS=(
  [clip1]=12MVGLhq4bGe9CZEDWx8hEfUkTMuG4QoZ  # on the office chair
  [clip2]=1klmbCh_AiFZfYqhNOQczwpPmoqaR3uxp  # squeeze test
  [clip3]=1DWuVTLCOm7yBd_JtiWb6W4UJc_nzrwrP  # rotate + hole close-up
)
for name in "${!IDS[@]}"; do
  curl -sSL -o ".src/$name.mp4" "https://drive.usercontent.google.com/download?id=${IDS[$name]}&export=download&confirm=t"
  ffmpeg -v error -y -i ".src/$name.mp4" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -g 30 -r 30 -an -movflags +faststart "assets/footage/$name.mp4"
done

# ref_grab.mp4, ref_sew.mp4 and ref_press.mp4 are crops of the earlier edit
# (kusyen-final-sfx-sahaja.mp4), which is not in the Drive folder:
#   card shots:  -ss 4.75 / 6.6, crop=545:640:275:575 scaled to 1080x1268 over a blurred fill
#   press shot:  -ss 12.72 -t 1.15, crop=652:1160:200:760 scaled to 1080x1920
