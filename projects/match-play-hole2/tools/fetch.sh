#!/usr/bin/env bash
# Downloads the six source clips (Google Drive, owner: MIY Golf) into .src/ and the 16 kHz audio used for transcription into .work/
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .src .work
i=1
for id in 1hzuN9X9K5AHzkXJmcoDVRyrw3xfJ1B3R 1Eq-o5p_Fp2eq6tTV5SMadKLJmaWFd0uz 1GzIPLhjuGjMY_2eQffYv83BG5_ZBcerA 1IVb_EJAvfAlz6oB-8yJ4n38TSlESEOsU 1Fkn4g_IaGHqbLMmpNjqSI7-jaJ2diGLt 12UqDTOAvJNi5kTvF0PMTSuW86B7oKjNo; do
  curl -sSL -o ".src/clip$i.mov" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
  ffmpeg -v error -y -i ".src/clip$i.mov" -vn -ac 1 -ar 16000 ".work/a$i.wav"
  i=$((i+1))
done
