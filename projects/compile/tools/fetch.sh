#!/usr/bin/env bash
# All clips in the owner's Drive folder 1kptuZSNf8-Zq_3cTnAplmOHGZtOv1p4J (link-shared) -> .src/<name>.mov
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .src
while read -r name id; do
  [ -f ".src/$name" ] || curl -sSL -o ".src/$name" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
done <<'LIST'
IMG_0041.MOV 1Cl4v42uDNAka8YBAyzuAC10oBbs5TD0K
IMG_0176.MOV 1rbIagHxNsKkSNS3PHLpE7W0XRQhWeI9y
IMG_0188.MOV 1HwK3uPQilJTJR_tYBxtNPdjIIArOdBBN
IMG_0192.MOV 1X3jy2UH-J_wMVq1Y7DwvO6KtkMuEnd6l
IMG_0193.MOV 1tJl92tilyuik6efMv-06S4d5qxiADABs
IMG_0203.MOV 1Kjgy_3NIRk0sZHmROwPg3W6mgJ8ys3Od
IMG_0205.MOV 1Qbz4JAKRKxXjHTulvfGxCZpCT_LzN4HN
IMG_0206.MOV 1yPofMtdps95kPxAGlGZooKzCn1fJmWr0
IMG_0211.MOV 1sNjCS2huX0XgUHE-S69Y_y_r33rGjDGI
IMG_0213.MOV 1rQBZryTJAiaMsXkmN7gN-K_jdGtxH4nn
IMG_0214.MOV 1wlTcE01bT79Xlpz3Td4dszVJIP_iQAFe
IMG_0215.MOV 1kMAkZvtfMnwkKuhoxNHkaXdu6c4IuT0P
IMG_0216.MOV 1TZ4C-1BTNSUE3c0Mf95Ms09y3iHMIXjN
IMG_5564.MOV 15rIe0iSj6e4eSbVwy46mFvCpNHUy9Lv1
IMG_6392.MOV 1LKTEnCVg-Mt3j0Ratf5HoPjG92v-m9WW
IMG_6411.MOV 1AyrMrb_TVWiesc0S8LhZznPEjBow7DL4
LIST
