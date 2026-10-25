# Review — "Satu Highway, Kita Je" (preview stage)

## Creative calls
- No speech in the source (engine/wind only), so the edit is cut on picture beats; 47.8 s → 25.4 s.
- Hook: the one car-free stretch of the straight (src 17.6–20.6) with "SATU HIGHWAY" on screen at
  frame 0 and "KITA JE." slamming at 0.42 s; zoom-through into the vanishing point.
- Look: Malaysian highway signage (green signs, amber warning diamond, lane-marking wipe, overhead
  gantry end card). Deliberately unlike the previous "Kes Ditutup" case-file edit.
- One riser→impact in the film, on the "AKU." reveal over the 360 selfie.
- Conservative grade on all footage (contrast +0.12, highlights −0.25, vibrance +0.3, warmth +0.04).
- No music: the request was SFX; the footage's engine sound is the bed. Music can be added in-app.

## Measured
- `check`: 0 errors; the 5 warnings are headless-GL driver console messages.
- Contrast: 16/16 text checks pass after the ink stickers behind amber type.
- Face-safe: S5 helmet within x 0–700, y 480–1100; every S5 card sits above y 785 or right of x 600,
  and the band clears before the rider stands (helmet rises to y≈480 at 4.25 s).
- Draft loudness after `loudnorm`: −16.0 LUFS integrated, −0.8 dBFS sample peak. Measured, not heard.

## Delivered
- `render -q delivery`, then two-pass `loudnorm=I=-14:TP=-1.5:LRA=11:linear=true` (video stream copied):
  −14.5 LUFS integrated, −1.2 dBFS peak, 1080×1920 30 fps, 25.5 s, ~100 MB.

## Weakest shot / next
- S3 (2.56 s) is the shortest read; "JALAN LURUS / TAK HABIS-HABIS" holds about 1.8 s.
