#!/usr/bin/env bash
# Delivery master for TikTok/IG: static gain to -14 LUFS, then an oversampled (192 kHz) limiter at -2 dBFS so the AAC lands <= -1 dBTP;
# H.264 High CRF 17 capped at 13 Mbps, 30 fps, AAC 256k 48 kHz.
#   tools/master.sh <rendered.mp4> <out.mp4>
set -euo pipefail
IN=$1; OUT=$2
lufs(){ ffmpeg -hide_banner -i "$1" -af "$2ebur128" -f null - 2>&1 | sed -n '/Summary/,$p' | awk '/I:/{print $2; exit}'; }
LIM="aresample=192000,alimiter=limit=0.794:attack=1:release=80:level=disabled,aresample=48000"
G=0
for pass in 1 2 3; do   # gain, limit, re-measure: the limiter shaves a little loudness, so iterate
  I=$(lufs "$IN" "volume=${G}dB,$LIM,")
  G=$(python3 -c "print(round($G + (-14.0 - $I), 2))")
done
ffmpeg -v error -y -i "$IN" -c:v libx264 -preset slow -crf 17 -maxrate 13M -bufsize 26M -profile:v high -pix_fmt yuv420p -r 30 \
  -af "volume=${G}dB,$LIM" -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$OUT"
echo "gain ${G} dB"
