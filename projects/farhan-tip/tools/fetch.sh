#!/usr/bin/env bash
# Drive folder 1iXR37yryPiZXnUjv0DzD4jqbul1y2ep9 (Coach Farhan) -> .src/ (footage, not committed)
set -euo pipefail
cd "$(dirname "$0")/.."
while read -r id name; do
  [ -f ".src/$name" ] || curl -sSL -o ".src/$name" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
done <<'L'
1E2FZIVcoSTXo5wFWqksU4JpFT9F2P1Xr IMG_0433.MOV
1Ep6Z-dpZpvT_WdoG0ysIGcoVhpAlcsD6 IMG_0434.MOV
L
ls -la .src
