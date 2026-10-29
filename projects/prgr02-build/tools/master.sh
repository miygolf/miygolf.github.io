#!/usr/bin/env bash
# Two-pass loudness master to −14 LUFS, then a −2.9 dB peak limiter (true peak ≤ −1 dBTP) for TikTok and Instagram; video stream copied.
# Usage: tools/master.sh <in.mp4> <out.mp4>
set -euo pipefail
IN=$1; OUT=$2
J=$(ffmpeg -hide_banner -i "$IN" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$J" | python3 -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i "$IN" -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,alimiter=limit=0.72:attack=2:release=60:level=false,aresample=48000" \
  -c:a aac -b:a 192k -movflags +faststart "$OUT"
