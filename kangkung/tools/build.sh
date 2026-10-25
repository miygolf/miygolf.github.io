#!/usr/bin/env bash
# Regenerate index.html from the EDL, then re-apply the footage grade.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/build_index.py
npx --yes hyperframes@0.8.197 media-treatment --selector ".shot" --apply --json \
  --grading '{"adjust":{"contrast":0.08,"vibrance":0.22,"saturation":0.04,"temperature":0.05,"tint":-0.04},"details":{"vignette":0.12}}' >/dev/null
echo "graded"
