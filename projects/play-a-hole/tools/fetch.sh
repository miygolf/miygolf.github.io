#!/usr/bin/env bash
# Downloads the four source clips (Google Drive, owner: MIY Golf) into .src/
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .src
i=1
for id in 1z6WvnatvnJWiY_zdOqau1T_QKyZJpeN6 1S0M4IOBNe9Oycso3SmnYOoqKyISgr-ta 1sDcqCiJD3zyhkitWx8LvEi8I4GrG2Ljr 1uQeJoCAg0jOKBwTHYEyLqI-_bXCHS2Tf; do
  curl -sSL -o ".src/clip$i.mp4" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
  i=$((i+1))
done
