#!/usr/bin/env bash
# Cut the four source clips into the segments the edit uses.
#   tools/prepare_footage.sh <folder holding the four VID_20261105_*.mp4>
# Sources are 4K portrait (rotation -90) at ~60 fps (variable frame rate). Cuts are by source frame index.
# 1x  segments: every 2nd frame -> 30 fps, with the clip's own sound.
# 0.5x segments: every frame played at 30 fps (real frames, no interpolation), silent.
set -euo pipefail
SRC=${1:?folder with the VID_*.mp4 files}
HERE=$(cd "$(dirname "$0")/.." && pwd)
OUT="$HERE/assets/footage"; ST="$HERE/assets/stills"
mkdir -p "$OUT" "$ST"

BFO="$SRC/VID_20261105_095511.mp4"   # 09:55 face-on      impact frame 153
BDTL="$SRC/VID_20261105_095523.mp4"  # 09:55 down-the-line impact frame 82
AFO="$SRC/VID_20261105_112306.mp4"   # 11:23 face-on      impact frame 184
ADTL="$SRC/VID_20261105_112337.mp4"  # 11:23 down-the-line impact frame 188

# Gentle, shared look: a touch of contrast and warmth, shadows lifted for the backlit DTL range.
GRADE_FO="eq=contrast=1.04:saturation=1.06,colorbalance=rs=0.02:bs=-0.02"
GRADE_DTL="curves=all='0/0.04 0.25/0.32 0.6/0.66 1/0.97',eq=contrast=1.02:saturation=1.08,colorbalance=rs=0.02:bs=-0.02"
SCALE="scale=1080:1920:flags=lanczos,setsar=1"
V="-c:v libx264 -preset slow -crf 15 -pix_fmt yuv420p -movflags +faststart"
A="-c:a aac -b:a 192k -ar 48000"

# name src first last speed grade
seg () {
  local name=$1 src=$2 a=$3 b=$4 speed=$5 grade=$6
  if [ "$speed" = "1" ]; then
    # real timestamps of frames a and b+1 (the sources are variable frame rate)
    local ts; ts=$(ffprobe -v error -select_streams v -show_entries frame=pts_time -of csv=p=0 "$src" \
      | python3 -c "import sys; t=[float(l.split(',')[0]) for l in sys.stdin if l.strip()]; print(f'{t[$a]:.6f} {t[min($b+1,len(t)-1)]:.6f}')")
    set -- $ts
    ffmpeg -v error -y -i "$src" \
      -vf "trim=start_frame=$a:end_frame=$((b+1)),setpts=PTS-STARTPTS,fps=30,$grade,$SCALE" \
      -af "atrim=start=$1:end=$2,asetpts=PTS-STARTPTS" $V $A "$OUT/$name.mp4"
  else
    ffmpeg -v error -y -i "$src" \
      -vf "trim=start_frame=$a:end_frame=$((b+1)),setpts=N/30/TB,$grade,$SCALE" -r 30 -an $V "$OUT/$name.mp4"
  fi
  echo "$name $(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$OUT/$name.mp4") frames"
}
still () { # name src frame grade
  ffmpeg -v error -y -i "$1" -vf "select='eq(n\,$2)',$3,$SCALE" -frames:v 1 -q:v 2 "$ST/$4.jpg"; echo "still $4"; }

seg hook   "$AFO"  160 183 0.5 "$GRADE_FO"    # AFTER top of backswing -> impact
seg a1     "$BFO"   64 137 1   "$GRADE_FO"    # BEFORE takeaway -> downswing
seg a2     "$BDTL"  66 113 1   "$GRADE_DTL"   # BEFORE DTL through impact (frame 82)
seg a3     "$BDTL"  59  77 0.5 "$GRADE_DTL"   # BEFORE DTL replay: top -> delivery (cause 1)
seg a4     "$BFO"  127 152 0.5 "$GRADE_FO"    # BEFORE face-on into impact (cause 2)
seg b1     "$AFO"  118 167 1   "$GRADE_FO"    # AFTER takeaway -> downswing
seg b2     "$ADTL" 172 219 1   "$GRADE_DTL"   # AFTER DTL through impact (frame 188)
seg b3     "$AFO"  154 169 0.5 "$GRADE_FO"    # AFTER transition (step 1)
seg b4     "$ADTL" 175 182 0.5 "$GRADE_DTL"   # AFTER into delivery (step 2)
seg b5     "$AFO"  184 229 1   "$GRADE_FO"    # AFTER impact -> finish (step 3)
seg c1     "$AFO"  118 237 1   "$GRADE_FO"    # AFTER full speed, face-on
seg c2     "$ADTL" 128 263 1   "$GRADE_DTL"   # AFTER full speed, down the line
seg outro  "$ADTL" 176 264 0.5 "$GRADE_DTL"   # AFTER DTL impact -> finish
still "$AFO"  184 "$GRADE_FO"  a_imp     # hook freeze
still "$BDTL"  78 "$GRADE_DTL" b_d78     # BEFORE delivery: gap + shallow shaft
still "$BFO"  153 "$GRADE_FO"  b_imp     # BEFORE impact, face-on: no clearance
still "$AFO"  170 "$GRADE_FO"  a_tr      # AFTER transition
still "$ADTL" 183 "$GRADE_DTL" a_dlv     # AFTER delivery
still "$AFO"  230 "$GRADE_FO"  a_finfo   # AFTER finish, face-on
still "$ADTL" 264 "$GRADE_DTL" a_fin     # outro hold
