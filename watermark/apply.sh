#!/usr/bin/env bash
# Burn the casual IG watermark into a vertical video (Reels 1080x1920).
#
#   watermark/apply.sh input.mp4 output.mp4 iqbal.yusoff ["ride santai je"]
#
# Env overrides: POS_X / POS_Y (top-left of watermark, px on 1080x1920),
# BOB=0 to disable the gentle float, CRF (default 21).
set -euo pipefail

in=${1:?input video}
out=${2:?output video}
handle=${3:?instagram handle}
tagline=${4:-}

here=$(cd "$(dirname "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

python3 "$here/make_watermark.py" --handle "$handle" --tagline "$tagline" -o "$tmp/wm.png" >/dev/null

# Default spot: top-left, just under the Reels header bar and clear of the
# right-side buttons and bottom caption area (IG safe zone).
pos_x=${POS_X:-40}
pos_y=${POS_Y:-230}
bob=${BOB:-1}
crf=${CRF:-21}

if [[ $bob == 1 ]]; then
  y_expr="$pos_y+4*sin(2*PI*t/3)"   # slow 3s float, +/-4px
else
  y_expr="$pos_y"
fi

ffmpeg -hide_banner -loglevel error -y \
  -i "$in" -loop 1 -i "$tmp/wm.png" \
  -filter_complex "\
[1:v]format=rgba,fade=t=in:st=0.3:d=0.8:alpha=1[wm];\
[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1[base];\
[base][wm]overlay=x=$pos_x:y='$y_expr':eval=frame:shortest=1,format=yuv420p[v]" \
  -map "[v]" -map 0:a? \
  -c:v libx264 -preset slow -crf "$crf" -maxrate 8M -bufsize 16M -profile:v high -r 30 \
  -c:a aac -b:a 192k -movflags +faststart \
  "$out"

echo "done -> $out"
