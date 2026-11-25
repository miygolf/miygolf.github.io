#!/usr/bin/env bash
# Drive folder 1kSC55PwCnVJP7e4ofjFRbHKVqOg0FGT5 (25 Nov 2026, early extension script) -> .src/ (owner's footage, not committed)
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .src/IMG_0448.MOV ] || curl -sSL -o .src/IMG_0448.MOV "https://drive.usercontent.google.com/download?id=1QF7HZcvU_L4yNX3u9TOcjM_UaVHTYBjo&export=download&confirm=t"
ls -la .src
