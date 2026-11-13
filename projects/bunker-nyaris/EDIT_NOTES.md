# Bunker, nyaris masuk — edit notes

**Look: "Neon Clubhouse"** — the shot told in the 19th-hole bar's neon signs: tube lettering on smoked-glass plates with a glowing tube frame,
signs flicker on (with an electric buzz), a neon scan line wipes between scenes, a neon tracker ring rides the ball and a pink ring pulses
as it passes the cup. Tilt Neon + Sora 700/800 + Noto Color Emoji. Tube pink #ff3d8b, tube aqua #39f3ff, tube core #fff4fa, smoked glass rgba(9,7,20,.74). No grade.

## Source
`clip1` IMG_0193 (25.2 s, handheld). The coach in a greenside bunker; the person filming asks a question (unclear across passes: not captioned).
- Transcript: faster-whisper small + medium full passes, cropped re-runs (medium, large-v3), `edit/transcript.txt`.
- "about **20** feet": medium full pass + 4 medium crops + 4 large-v3 crops say 20; small (and the first noise-reduced mix) heard 30.
  The mix's noise reduction was softened so the word stays clear (medium re-check of the preview mix: "about 20 feet").
- "Kita main stop shot" is said quietly by the coach (~15 dB under the lines before it): lifted +9 dB.
- Impact 20.74 (picture; sound 20.749). The ball rolls in from the left, **passes right by the cup** (22.83–22.90) and keeps rolling right
  (still creeping at 25.2). So: "nyaris masuk / sikit lagi" — no claim that it stopped.

## Structure (16.5 s)
| film | segment | on screen |
| --- | --- | --- |
| 0.00–2.33 | hook: ball at the cup 0.5×, freeze as it passes | NYARIS MASUK sign flickers on (frame 0), cup rings, 😱 |
| 2.33–3.60 | "Bunker sahaja." (walking in) | caption |
| 3.60–7.13 | "Almost similar, about 20 feet. Kita main stop shot." | captions + ≈20 ft sign, then STOP SHOT sign (held through the address) |
| 7.13–8.98 | address + swing 1× (v2: starts tight on the coach, pulls out to full frame by ~8.3) | pink flash + punch on impact |
| 8.98–9.68 | whip to the green 2× | neon scan rides the whip |
| 9.68–11.63 | the roll 1× | tracker ring on the ball, cup pulse, NYARIS!, "What a player! 🔥" (in the trees: the ball is low) |
| 11.63–12.60 | replay 0.5× tight on the splash | REPLAY ½× |
| 12.60–16.53 | the green, freeze | SIKIT LAGI! end sign, "Korang pernah nyaris hole-out? 👇" (below the ball) |

## Rules applied
- Safe band x 60–930, y 168–1330; faces checked in snapshots (signs in the sky band, captions low, roll caption up in the trees).
- Cut: the opening question, "educational video" aside, the second "stop shot", the camera walk-in, waiting at address.
- No music. Master: static gain + oversampled limiter at −3 dBFS (AAC overshot a sharp electric-glitch SFX to +3.4 dBTP at −2 dBFS).

## Build
```
tools/fetch.sh
python3 tools/build_aroll.py          # also re-run the ball tracker snippet in EDIT_NOTES history if the EDL changes (edit/ball_roll.json)
python3 tools/build_index.py
npx hyperframes@0.9.32 check
npx hyperframes@0.9.32 render -q draft -o renders/preview_draft.mp4 && tools/master.sh renders/preview_draft.mp4 previews/bunker-nyaris_preview_v1.mp4
# on "render":
npx hyperframes@0.9.32 render -q delivery -o renders/final_raw.mp4 && tools/master.sh renders/final_raw.mp4 final/bunker-nyaris_1080x1920.mp4
```

## Versions
- v1 (`previews/bunker-nyaris_preview_v1.mp4`, `VARIANT=v1`): slow punch-in on the far address, close address at full frame.
- v2 (`previews/bunker-nyaris_preview_v2_zoomout.mp4`, default `VARIANT=zoomout`): owner asked "zoom out at address" — far address at full frame;
  close address starts at 1.38× on the coach and eases out to full frame before the take-away, so the swing and the splash play wide.
- v3 (`previews/bunker-nyaris_preview_v3_wide.mp4`, default `VARIANT=wide`): owner: "bagi nampak surrounding" — hook 1.25–1.36× (was 1.9–2.2×)
  so the green, trees and hills read, both addresses at full frame, replay 1.2–1.28× (was 1.6–1.75×). Hook cup ring position is computed from the zoom.

## Delivery
Owner approved v3 ("Render", 2026-11-13). `final/bunker-nyaris_1080x1920.mp4`: 16.5 s, 1080×1920, 30 fps, H.264 High ~12.5 Mbps, AAC 256k 48 kHz, −14.1 LUFS, −2.1 dBTP.
