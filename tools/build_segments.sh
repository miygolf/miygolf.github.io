#!/bin/bash
# Cuts the raw clips into the edited segments (1080x1920, 30fps) used by the HyperFrames project.
# Usage: tools/build_segments.sh <clipA.mp4> <clipB.mp4> <project_dir>
set -euo pipefail
A="$1"; B="$2"; P="$3"
OUT="$P/assets/footage"; TMP="$(mktemp -d)"
SCALE="scale=1080:1920:flags=lanczos,setsar=1"
ENC="-c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -g 30 -an"

# part <src> <start> <end> <speed> <out>
part() {
  local src=$1 ss=$2 to=$3 speed=$4 out=$5
  local d; d=$(python3 -c "print($to-$ss)")
  if [ "$speed" = "1" ]; then
    ffmpeg -v error -y -ss "$ss" -t "$d" -i "$src" -vf "$SCALE,fps=30" $ENC "$out"
  else
    ffmpeg -v error -y -ss "$ss" -t "$d" -i "$src" \
      -vf "$SCALE,setpts=PTS/$speed,minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,fps=30" $ENC "$out"
  fi
}
join() { local out=$1; shift; : > "$TMP/list.txt"; for f in "$@"; do echo "file '$f'" >> "$TMP/list.txt"; done
  ffmpeg -v error -y -f concat -safe 0 -i "$TMP/list.txt" -c copy "$out"; }

# Hook: swing 2 impact, slow motion (0.35x)
part "$B" 10.25 10.95 0.35 "$OUT/hook.mp4"
# Swing 1: real time -> 0.4x through impact -> real time (idle tail after finish removed)
part "$A" 0.85 2.35 1   "$TMP/a1.mp4"
part "$A" 2.35 2.75 0.4 "$TMP/a2.mp4"
part "$A" 2.75 3.35 1   "$TMP/a3.mp4"
join "$OUT/swing1.mp4" "$TMP/a1.mp4" "$TMP/a2.mp4" "$TMP/a3.mp4"
# Swing 2: the ~8.7 s of standing at address is removed
part "$B" 8.75 10.45 1   "$TMP/b1.mp4"
part "$B" 10.45 10.85 0.4 "$TMP/b2.mp4"
part "$B" 10.85 12.90 1   "$TMP/b3.mp4"
join "$OUT/swing2.mp4" "$TMP/b1.mp4" "$TMP/b2.mp4" "$TMP/b3.mp4"

# Finish-position stills for the end comparison
ffmpeg -v error -y -ss 3.25 -i "$A" -frames:v 1 -vf "$SCALE" -q:v 2 "$P/assets/stills/finish1.jpg"
ffmpeg -v error -y -ss 11.70 -i "$B" -frames:v 1 -vf "$SCALE" -q:v 2 "$P/assets/stills/finish2.jpg"

# Ambient track on the edited timeline: real-time parts keep their sound, slow-mo parts are silent
# (SFX carry them). Layout: hook 2.0 | swing1 1.5+1.0+0.6 | swing2 1.7+1.0+2.05
ffmpeg -v error -y -i "$A" -i "$B" -filter_complex "
 anullsrc=r=48000:cl=stereo,atrim=0:2.0[h];
 [0:a]atrim=0.85:2.35,asetpts=PTS-STARTPTS,afade=t=out:st=1.42:d=0.08[a1];
 anullsrc=r=48000:cl=stereo,atrim=0:1.0[a2];
 [0:a]atrim=2.75:3.35,asetpts=PTS-STARTPTS,afade=t=in:d=0.08,afade=t=out:st=0.5:d=0.1[a3];
 [1:a]atrim=8.75:10.45,asetpts=PTS-STARTPTS,afade=t=in:d=0.1,afade=t=out:st=1.62:d=0.08[b1];
 anullsrc=r=48000:cl=stereo,atrim=0:1.0[b2];
 [1:a]atrim=10.85:12.90,asetpts=PTS-STARTPTS,afade=t=in:d=0.08,afade=t=out:st=1.85:d=0.2[b3];
 [h][a1][a2][a3][b1][b2][b3]concat=n=7:v=0:a=1[out]" -map "[out]" -c:a pcm_s16le "$P/assets/footage/ambient.wav"
rm -rf "$TMP"
for f in hook swing1 swing2; do printf "%s %s\n" $f "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$f.mp4")"; done
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/ambient.wav"
