#!/usr/bin/env bash
# Delivery master for TikTok/IG: two-pass loudnorm to -14 LUFS / -1.5 dBTP; H.264 High CRF 18 capped at 13 Mbps (house spec; keeps a ~55 s final under GitHub's 100 MB).
#   tools/master.sh <rendered.mp4> <out.mp4>
set -euo pipefail
IN=$1; OUT=$2
J=$(ffmpeg -hide_banner -i "$IN" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$J" | python3 -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i "$IN" -c:v libx264 -preset slow -crf 18 -maxrate 13M -bufsize 26M -profile:v high -pix_fmt yuv420p -r 30 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" \
  -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$OUT"
