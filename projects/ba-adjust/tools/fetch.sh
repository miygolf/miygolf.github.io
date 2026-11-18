#!/usr/bin/env bash
# Drive folder 1vAvvjHm1jcRnv-GNmpjir7cBmisdTn-b (link-shared) -> .src/
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .src
while read -r name id; do
  [ -f ".src/$name" ] || curl -sSL -o ".src/$name" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
done <<'LIST'
IMG_0328.MOV 1AX6Bg0rPpmIdXRpPN4bbmSRMsfN_hyHi
IMG_0330.MOV 1mh2Mp4Q4r09eBF733Rx3DtqJu0cvnQyL
IMG_0331.MOV 1n0wbXIa59dPmqlrabUv8q59qxXyl3pFG
IMG_0333.MOV 1zON04MNLvzgnY2H5K0OhoyLCKq0PLLzf
clip_m4v.m4v 1FKTmB1eL4SzFS1qig1F_l9lu0uRMXMoj
LIST
