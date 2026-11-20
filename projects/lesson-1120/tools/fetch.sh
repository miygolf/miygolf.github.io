#!/usr/bin/env bash
# Drive folder "Golf Lesson" 1r-oIAmpoBExYVC6MEixDWunlK6T5W5DA (link-shared) -> .src/
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .src
while read -r name id; do
  [ -f ".src/$name" ] || curl -sSL -o ".src/$name" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
done <<'LIST'
IMG_0352.MOV 1y4MJ741kh0uES51mOVS-8O4Z-5r9Ay1Z
IMG_0355.MOV 1t92TpV1tT3WXT0wMXEWvx4vibuLAVCQM
IMG_0368.MOV 1jATPkfwVMZjYlivrmVsxp95Ll9oQbpae
LIST
