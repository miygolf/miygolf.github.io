# ZQ UAV — "Drone atau pesawat?" (HyperFrames)

Vertical 1080×1920, 30 fps, 21.5 s. Source: `src/raw.mp4` (29.3 s, 720×1280 @60).

## Transcript
No speech in the source: Whisper large-v3 + Silero VAD found none (the track is steady
wind/handling noise). The story is carried by on-screen type, music and SFX; the source
audio is muted.

## Cut (src/cuts.json → tools/build_edit.py)
| Film | Source | Speed | Beat |
| --- | --- | --- | --- |
| 0.0–2.0 | 27.3–29.3 | 1× | HOOK: nose-on close-up, "DRONE? / ATAU PESAWAT?" |
| 2.0–5.0 | 0.8–5.3 | 1.5× | approach — "NAIK TEGAK, macam drone." |
| 5.0–9.0 | 5.2–10.0 | 1.2× | wing pass — "TERBANG JAUH, macam pesawat." |
| 9.0–13.0 | 10.0–14.4 | 1.1× | orbit to front — tracked callouts V-TAIL, 4× ROTOR VTOL |
| 13.0–17.5 | 20.4–24.9 | 1× | RadioMaster AX12 + live map |
| 17.5–21.5 | 14.4–18.4 | 1× | drop: "DUA-DUA." → ZQ UAV logo |
Dropped: the repeated side pass (src 17–20) and the second orbit back to the nose (25–27).

## Design: "Sectional" (aeronautical chart)
- Ink #0b0c10, paper #f4f6f8, airspace magenta #ff2e88 / #e8137a (white-on-magenta blocks).
- Michroma (wide, echoes the logo) + IBM Plex Sans Condensed.
- Numbered chips (01–04), climb tape, dashed flight path with waypoints, LK-tracked callout rings
  (`tools/track.py` → `tools/build_anatomi.py`), screen brackets, magenta ring around the logo.
- Text only in y 236–720 (IG Reels safe band), logo badge top-right; nothing over the aircraft's body.

## Sound
- Music: `assets/bgm/bed.wav`, MusicGen (facebook/musicgen-medium, seed 11), trimmed from 2.3 s so its
  drop lands on the logo at 17.5 s; beats at every 0.5 s of film time (120 bpm).
- SFX: Freesound via Openverse (see `assets/sfx/CREDITS.md`) + HyperFrames bundled click/whoosh.

## Privacy
The car number plate (film 13.0–17.5 s and 19.2–21.5 s) is tracked with LK optical flow from
hand-picked seeds (`tools/track_plate.py` → `src/plate_track.json`) and pixelated + blurred with a
feathered edge (`tools/blur_plate.py`), baked into `assets/footage/edit.mp4`.

## Build
```
python3 tools/build_edit.py      # cut raw -> assets/footage/edit_clean.mp4
python3 tools/track_plate.py     # plate track on the clean cut
python3 tools/blur_plate.py      # hide the plate -> assets/footage/edit.mp4
python3 tools/track.py           # optional: re-track callout anchors (reads edit_clean.mp4)
python3 tools/build_anatomi.py   # anatomi scene from tracks
npx hyperframes check
npx hyperframes render -q delivery -o renders/final-raw.mp4
# then two-pass loudnorm to -14 LUFS / -1.5 dBTP
```
Delivered: `final/ZQ-UAV_FINAL_1080x1920.mp4` (repo root), -14.0 LUFS, -1.3 dBFS peak.
```
```
