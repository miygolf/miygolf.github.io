#!/usr/bin/env bash
# Drive folder 1_FPhXSj8QvGqvLePeI6cifAqqU8iQz2- (28 Nov 2026, "recap today lesson") -> .src/ (footage, not committed)
set -euo pipefail
cd "$(dirname "$0")/.."
while read -r id name; do
  [ -f ".src/$name" ] || curl -sSL -o ".src/$name" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
done <<'L'
1TWyuGSPzb1WrMkUuhF7UxCItavOE2CDx IMG_0474.MOV
1uggzJHtKepbgQYmZhdXv6hBM3uaWe-xK IMG_0480.MOV
1ITL_RqK-YlnAzQanN_x5SzJL5RwD1zn- IMG_0485.MOV
1iUN18wlITyOqXAebL0ueNFRPtIfEAf-3 IMG_0494.MOV
1G-g7pXpZ9riEqviyd-7OngcshA31bYqt IMG_0505.MOV
L
ls -la .src
