#!/usr/bin/env bash
# Downloads the source clip from Drive and makes the upright 1080x1920 intermediate used by build_aroll.py.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .src
curl -sSL -o .src/raw.MOV "https://drive.usercontent.google.com/download?id=1AyrMrb_TVWiesc0S8LhZznPEjBow7DL4&export=download&confirm=t"
ffmpeg -v error -y -i .src/raw.MOV -vf "scale=1080:1920:flags=lanczos,setsar=1,fps=30" -an -c:v libx264 -preset slow -crf 12 -pix_fmt yuv420p -g 15 .src/upright.mp4
