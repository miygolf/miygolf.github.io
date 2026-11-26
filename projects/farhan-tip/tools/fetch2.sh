#!/usr/bin/env bash
# Drive folder 1kdg1-yniuvbw5lYDmWUgn0FBLFQRZOe3 (Coach Farhan, batch 2) -> .src/ (footage, not committed)
set -euo pipefail
cd "$(dirname "$0")/.."
while read -r id name; do
  [ -f ".src/$name" ] || curl -sSL -o ".src/$name" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
done <<'L'
1A3n_vA0iFAaL0UvChxhA9bRD5G4RGtxZ IMG_0429.MOV
1Z4ZBzO2QgsGYiF2RY6QRfglLsCop9Su0 IMG_0431.MOV
1Uypg6R69TbLaNxLrwM2sXhv8UAkVgcXR IMG_0432.MOV
L
ls -la .src
