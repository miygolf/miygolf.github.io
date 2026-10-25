# video-claude

Before → after golf swing edits (adjustment: **weight shift**), built with HyperFrames.
Each folder is a standalone HyperFrames project (`npx hyperframes@0.8.196 render` inside it).

| Folder | Concept | Look | Length |
| --- | --- | --- | --- |
| `golf-swing-edit/` | A — Telemetry: slow-mo hook, before, after, split-screen finish | Black + lime, phase progress strip, weight-shift bracket | 13.4 s |
| `option-b-sync/` | B — Sync: before above, after below, impacts frame-aligned, then freezes on top / impact / finish | Editorial paper, serif, terracotta | 10.6 s |
| `option-c-kinetic/` | C — Kinetic: "DULU vs SEKARANG" creator style, word-pop captions, punch-in + shake on impact | White/black captions, yellow highlight | 12.6 s |
| `option-d-blueprint/` | D — Blueprint: frame-exact freeze breakdown A1–A3 / B1–B3, crosshairs, impact vs impact end plate | Cobalt grid, mono labels | 14.7 s |

`tools/` holds the scripts that cut the source clips (`build_segments.sh`), build freeze-frame clips
(`build_freeze.py`), generate the telemetry scenes (`gen_swing_scenes.py`) and render previews
(`render_previews.sh`). Transcript and cut list: `golf-swing-edit/EDIT_NOTES.md`.
