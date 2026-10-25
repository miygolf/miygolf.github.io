#!/bin/bash
# Renders a draft preview for each project and loudness-normalises it for social playback.
set -e
for p in "$@"; do
  (cd "$p" && mkdir -p renders && npx -y hyperframes@0.8.196 render --quality draft --workers 3 --output renders/raw.mp4 >/dev/null 2>&1)
  d=$(python3 -c "import re;print(re.search(r'id=\"root\"[^>]*?data-duration=\"([0-9.]+)\"', open('$p/index.html').read(), re.S).group(1))")
  ffmpeg -v error -y -i "$p/renders/raw.mp4" -c:v copy -af "loudnorm=I=-14.5:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 192k -t "$d" -movflags +faststart "$p/renders/preview.mp4"
  rm "$p/renders/raw.mp4"
  echo "$p done ($d s)"
done
