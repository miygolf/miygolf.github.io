#!/usr/bin/env bash
# Crown driver tercabut — edit 9:16 (hook 3 + ending tenang)
# Guna: ./build.sh <folder_klip_sumber> <fail_output.mp4>
set -euo pipefail

SRC=${1:?folder klip sumber}
OUT=${2:?fail output}
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

SWING=$SRC/VID_20260928_122133.mp4   # tee shot, 60fps
HEAD=$SRC/VID_20260928_122208.mp4    # close-up kepala driver
CROWN=$SRC/VID_20260928_122225.mp4   # cari & kutip crown
DUSK=$SRC/VID_20261025_181152.mp4    # padang waktu senja
FALL=$SRC/VID_20261025_182602.mp4    # air terjun tepi tasik

BOLD=/usr/share/fonts/opentype/inter/Inter-Black.otf
SOFT=/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf
FIT="scale=1080:1920:flags=lanczos,setsar=1"
# Draf: CRF=21 (default). Render final: CRF=17 PRESET=slow
ENC=(-c:v libx264 -preset "${PRESET:-medium}" -crf "${CRF:-21}" -pix_fmt yuv420p -r 30
     -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart)

# Tulis teks ke fail supaya tak perlu escape tanda baca dalam drawtext
txt() { printf '%s' "$2" > "$WORK/$1.txt"; }
txt hook1 "Sekali swing je…"
txt hook2 "crown driver aku HILANG."
txt fly   "Tengok apa yang terbang ↑"
txt model "Callaway Elyte Max Fast"
txt crown "“Ini dia punya crown.”"
txt end1  "Driver boleh ganti."
txt end2  "Petang macam ni, tak boleh."

# Kapsyen besar: putih/kuning, outline hitam, sepertiga atas (elak UI TikTok di bawah)
cap() { # nama warna y mula [tamat] [saiz]
  local en="gte(t,$4)"; [[ -n ${5:-} ]] && en="between(t,$4,$5)"
  echo "drawtext=fontfile=$BOLD:textfile=$WORK/$1.txt:fontsize=${6:-74}:fontcolor=$2:borderw=7:bordercolor=black:x=(w-text_w)/2:y=$3:enable='$en'"
}
# Kapsyen lembut untuk ending: fade in perlahan
softcap() { # nama y mula
  echo "drawtext=fontfile=$SOFT:textfile=$WORK/$1.txt:fontsize=60:fontcolor=white:shadowcolor=black@0.6:shadowx=3:shadowy=3:x=(w-text_w)/2:y=$2:alpha='clip((t-$3)/0.8,0,1)':enable='gte(t,$3)'"
}

# A. Hook — kepala driver yang dah takde crown
ffmpeg -v error -y -ss 0 -t 2.4 -i "$HEAD" \
  -vf "$FIT,$(cap hook1 white 380 0),$(cap hook2 yellow 470 0.6)" \
  "${ENC[@]}" "$WORK/a.mp4"

# B. Downswing, kelajuan biasa
ffmpeg -v error -y -ss 9.0 -t 1.0 -i "$SWING" \
  -vf "$FIT" "${ENC[@]}" "$WORK/b.mp4"

# C. Impak slow-mo 2x (60fps -> 30fps) + zoom perlahan ke arah serpihan yang terbang
ZOOM="1+0.45*clip((t-1.0)/1.2,0,1)"
ffmpeg -v error -y -ss 10.0 -t 1.1 -i "$SWING" \
  -filter_complex "[0:v]setpts=2*PTS,fps=30,scale=w='trunc(1080*($ZOOM)/2)*2':h='trunc(1920*($ZOOM)/2)*2':eval=frame:flags=lanczos,crop=1080:1920:x='(in_w-1080)*0.55':y='(in_h-1920)*0.35',setsar=1,$(cap fly white 300 0.5 "" 64)[v];
                   [0:a]adelay=200|200,apad,atrim=0:2.2[a]" \
  -map "[v]" -map "[a]" -t 2.2 "${ENC[@]}" "$WORK/c.mp4"

# D. Reaksi lepas pukul
ffmpeg -v error -y -ss 12.4 -t 1.8 -i "$SWING" \
  -vf "$FIT" "${ENC[@]}" "$WORK/d.mp4"

# E. Tunjuk model driver (sole + face)
ffmpeg -v error -y -ss 2.5 -t 1.8 -i "$HEAD" \
  -vf "$FIT,$(cap model white 380 0)" "${ENC[@]}" "$WORK/e.mp4"

# F. Jumpa crown atas fairway dan kutip
ffmpeg -v error -y -ss 2.0 -t 5.4 -i "$CROWN" \
  -vf "$FIT,$(cap crown white 380 0.4 3.2)" "${ENC[@]}" "$WORK/f.mp4"

# G. Ending tenang — senja + air terjun, crossfade dan fade out
ffmpeg -v error -y -ss 1.0 -t 4.7 -i "$DUSK" -t 4.7 -i "$FALL" \
  -filter_complex "[0:v]$FIT,$(softcap end1 760 0.6)[v0];
                   [1:v]$FIT,$(softcap end2 760 0.6)[v1];
                   [v0][v1]xfade=transition=fade:duration=0.8:offset=3.9,fade=t=out:st=7.6:d=1.0[v];
                   [0:a][1:a]acrossfade=d=0.8,afade=t=out:st=7.6:d=1.0[a]" \
  -map "[v]" -map "[a]" "${ENC[@]}" "$WORK/g.mp4"

# Sambung A–F (potongan terus), kemudian crossfade lembut masuk ending
printf "file '%s'\n" "$WORK"/{a,b,c,d,e,f}.mp4 > "$WORK/list.txt"
ffmpeg -v error -y -f concat -safe 0 -i "$WORK/list.txt" -c copy "$WORK/main.mp4"
MAIN=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$WORK/main.mp4")
OFF=$(echo "$MAIN - 0.6" | bc -l)

ffmpeg -v error -y -i "$WORK/main.mp4" -i "$WORK/g.mp4" \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.6:offset=$OFF[v];
                   [0:a][1:a]acrossfade=d=0.6[a]" \
  -map "[v]" -map "[a]" "${ENC[@]:0:10}" -c:a pcm_s16le "$WORK/joined.mkv"

# Kuatkan ke -14 LUFS (standard TikTok/IG); limiter tahan peak bunyi impak bawah -1.5 dBFS.
# Limiter makan sedikit loudness, jadi ukur semula dan tambah gain sekali lagi.
lufs() { ffmpeg -hide_banner -i "$1" -af ebur128 -f null - 2>&1 | sed -n 's/^ *I: *\(-*[0-9.]*\) LUFS/\1/p' | tail -1; }
ffmpeg -v error -y -i "$WORK/joined.mkv" -vn -c:a pcm_s16le "$WORK/raw.wav"
GAIN=$(echo "-14 - ($(lufs "$WORK/raw.wav"))" | bc -l)
for pass in 1 2; do
  ffmpeg -v error -y -i "$WORK/raw.wav" \
    -af "volume=${GAIN}dB,alimiter=limit=0.84:attack=1:release=60:level=disabled" "$WORK/norm.wav"
  GAIN=$(echo "$GAIN + (-14 - ($(lufs "$WORK/norm.wav")))" | bc -l)
done
ffmpeg -v error -y -i "$WORK/joined.mkv" -i "$WORK/norm.wav" -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"

echo "Siap: $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s)"
