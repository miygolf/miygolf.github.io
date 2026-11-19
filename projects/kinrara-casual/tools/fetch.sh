#!/usr/bin/env bash
# Drive folder 1JaOAR5R1cVyvUQVPdNlqJBex6J4nSiA_ (link-shared) -> .src/
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .src
while read -r name id; do
  [ -f ".src/$name" ] || curl -sSL -o ".src/$name" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
done <<'LIST'
IMG_0338.MOV 1toB9uozd-m80XqfgEfJ288gU5QWRts3d
IMG_0344.MOV 1nlWfKL4E8C1SVhCzAyh1pUVlJBrLosU3
c1_1.mp4 1RgIAxcNN7jKbSzUzsY97oQ9bTUjLFwD2
c1_2.mp4 1n0zpLN2RKPmprgMG04cB-uRjR4OOcK7T
c1_3.mp4 1tqFkKkLHweiRoMt_Kx1GdcZd4CPeNgma
c1_4.mp4 1n9Tene2ACqyfrDjfVclkFZinHkK0g-GR
c2_1.mp4 1Kj5qZGhKBB-iiUohgD1PHxjQBDYzzAM8
c2_2.mp4 1yr6Bn5POP9quPQfQsx_LyZHFtu3auh2X
c2_3.mp4 1hOXesxg_8G6czzl1Fe5ifx-3D3QHZi2g
c2_4.mp4 1BFoT98LOIzu3RH8Y-3jV82uV-GPUouqs
LIST
