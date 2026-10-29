#!/usr/bin/env bash
# Cuts the golf-course backgrounds: Mixkit free stock videos (Mixkit Stock Video Free License),
# cropped to a 9:16 window with no people in it, scaled to 1080x1920 and softened (depth of field).
# Usage: tools/prepare_course.sh <dir with mixkit <id>-1080.mp4 files, named v_<id>.mp4>
set -euo pipefail
SRC=${1:?source dir}
cd "$(dirname "$0")/.."
F=assets/footage; mkdir -p "$F"
# name  mixkit-id  crop-x  start  duration
cut() {
  ffmpeg -v error -y -ss "$4" -t "$5" -i "$SRC/v_$2.mp4" -an \
    -vf "crop=608:1080:$3:0,scale=1080:1920:flags=lanczos,gblur=sigma=2.5,fps=30,format=yuv420p" \
    -c:v libx264 -preset slow -crf 18 -g 15 -movflags +faststart "$F/$1.mp4"
}
cut course_flag   2029 1060 0.0 3.0   # hook: flag, palms, bunker
cut course_rocks  2036 1370 0.0 4.0   # head: flag by the rocks
cut course_tree   2038 1250 0.0 4.0   # shaft: big tree over the fairway
cut course_villas 2035 1250 0.0 3.4   # length: flag, bunker, villas
cut course_palms  2030  150 0.0 4.4   # grip: palms and fairway
cut course_tree2  2038 1250 5.0 3.2   # recap
cut course_flag2  2029 1060 6.0 3.2   # end
