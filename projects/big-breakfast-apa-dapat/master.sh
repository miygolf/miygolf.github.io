#!/usr/bin/env bash
# Loudness master for social: two-pass loudnorm to -14 LUFS, then a true-peak limiter. Video stream copied.
# usage: ./master.sh <in.mp4> <out.mp4>
set -euo pipefail
in="$1"; out="$2"
read -r I TP LRA TH OFF < <(ffmpeg -hide_banner -i "$in" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 \
  | sed -n '/^{/,/^}/p' | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh'],d['target_offset'])")
ffmpeg -v error -y -i "$in" -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$I:measured_TP=$TP:measured_LRA=$LRA:measured_thresh=$TH:offset=$OFF:linear=true,aresample=192000,alimiter=limit=0.79:level=false:attack=1:release=50,aresample=48000" \
  -c:a aac -b:a 256k -movflags +faststart "$out"
ffmpeg -hide_banner -i "$out" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
