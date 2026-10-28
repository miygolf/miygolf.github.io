#!/usr/bin/env bash
# Cuts the four Drive clips into the edit's segments (slow-mo pre-rendered with motion
# interpolation) and exports the impact freeze frames from the 4K sources.
# Usage: tools/prepare_footage.sh <dir with VID_*.mp4>
set -euo pipefail
SRC=${1:?source dir}
cd "$(dirname "$0")/.."
F=assets/footage; S=assets/stills; mkdir -p "$F" "$S"
declare -A CLIP=(
  [bdtl]="$SRC/VID_20261028_130606.mp4"  # before, down the line
  [bfo]="$SRC/VID_20261028_130630.mp4"   # before, face on
  [adtl]="$SRC/VID_20261028_132845.mp4"  # after, down the line
  [afo]="$SRC/VID_20261028_132901.mp4"   # after, face on
)
SCALE="scale=1080:1920:flags=lanczos"
ENC="-c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -g 15 -movflags +faststart"

# name clip in out speed  (speed < 1 = slow motion, interpolated to 30 fps)
seg() {
  local name=$1 clip=$2 a=$3 b=$4 sp=$5
  if [ "$sp" = "1" ]; then
    ffmpeg -v error -y -ss "$a" -to "$b" -i "${CLIP[$clip]}" -vf "$SCALE,fps=30" $ENC \
      -c:a aac -b:a 192k -ar 48000 "$F/$name.mp4"
  else
    ffmpeg -v error -y -ss "$a" -to "$b" -i "${CLIP[$clip]}" -an \
      -vf "$SCALE,setpts=(PTS-STARTPTS)/$sp,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" \
      $ENC "$F/$name.mp4"
  fi
}
seg hook_a  afo  5.070 5.333 0.30
seg hook_b  afo  5.333 5.620 0.35
seg bdtl_a  bdtl 3.300 4.120 1
seg bdtl_b  bdtl 4.120 4.430 0.22
seg bfo_a   bfo  6.550 6.778 0.35
seg adtl_a  adtl 5.060 5.860 1
seg adtl_b  adtl 5.860 6.133 0.22
seg afo_a   afo  5.100 5.333 0.35
seg afo_b   afo  5.333 7.650 1
# rewind: the after swing played backwards at 3x
ffmpeg -v error -y -ss 4.40 -to 5.62 -i "${CLIP[afo]}" -an -vf "$SCALE,reverse,setpts=(PTS-STARTPTS)/3,fps=30" $ENC "$F/rewind.mp4"
# range ambience bed (no strikes nearby), used under the slow-motion parts
ffmpeg -v error -y -ss 1.0 -to 5.4 -i "${CLIP[bfo]}" -vn -c:a aac -b:a 192k -ar 48000 "$F/amb.m4a"

still() { ffmpeg -v error -y -ss "$3" -i "${CLIP[$2]}" -frames:v 1 -vf "$4" -q:v 2 "$S/$1.jpg"; }
still bdtl_imp bdtl 4.430 "$SCALE"
still bfo_imp  bfo  6.778 "$SCALE"
still adtl_imp adtl 6.133 "$SCALE"
still afo_imp  afo  5.333 "$SCALE"
still afo_fin  afo  6.000 "$SCALE"
# after-impact stills re-framed to sit on the before framing (feet and ball aligned) for the wipe
still afo_imp_al  afo  5.333 "crop=1588:2824:278:498,$SCALE"
still adtl_imp_al adtl 6.133 "crop=1912:3398:203:196,$SCALE"
# ~23 s range-ambience bed: quiet stretches of all four clips (no strikes), levelled and crossfaded
ffmpeg -v error -y \
  -ss 0.9 -to 5.6 -i "${CLIP[bfo]}" -ss 0.1 -to 3.2 -i "${CLIP[bdtl]}" \
  -ss 0.2 -to 4.5 -i "${CLIP[afo]}" -ss 2.5 -to 4.9 -i "${CLIP[adtl]}" \
  -filter_complex "[0:a]volume=-2dB[a0];[1:a]volume=0dB[a1];[2:a]volume=9dB[a2];[3:a]volume=9dB[a3];\
[a0][a1]acrossfade=d=0.6[x1];[x1][a2]acrossfade=d=0.6[x2];[x2][a3]acrossfade=d=0.6[x3];\
[x3]highpass=f=90,aresample=48000" \
  -vn -c:a pcm_s16le "$F/amb_once.wav"
# loop it twice with a 1 s crossfade at the seam
ffmpeg -v error -y -i "$F/amb_once.wav" -i "$F/amb_once.wav" -filter_complex "[0][1]acrossfade=d=1" -c:a aac -b:a 192k "$F/amb_bed.m4a"
rm -f "$F/amb_once.wav"
rm -f "$F/amb.m4a"
