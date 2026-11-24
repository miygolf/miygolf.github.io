#!/usr/bin/env bash
# Same Drive folder as projects/bunker-skrip (1V5O7fsTQ3tDUyWBKtVEx_orZs4-I7WqR) -> .src/ (owner's footage, not committed)
set -euo pipefail
cd "$(dirname "$0")/.."
while read -r id name; do
  [ -e ".src/$name" ] || curl -sSL -o ".src/$name" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
done <<'L'
1CVMoqRcJ6nDMSVT0rbGkEtZkhrg6P018 egg_fry.MOV
1rZiNk83YuZyAQhTWQBUgJJ049-sc2vR4 IMG_0418.MOV
L
