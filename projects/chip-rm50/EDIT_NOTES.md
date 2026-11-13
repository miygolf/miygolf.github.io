# Chip in RM50 — edit notes

Owner: "Sama buat macam bunker shot style" → same raw / chalkboard treatment as `projects/bunker-raw/` (look reused on purpose, not a new one):
slate boards with a wood rim, stepped chalk write-on, eraser wipe out of the hook, HOMEWORK end board, hard cuts, real sound, four soft chalk SFX, no music.

## Source (29.0 s, handheld beside the coach)
large-v3 full passes (ms, en) + crops (`edit/transcript.txt`):
- "30 meter." 1.64 · "Chip in, chip in." 3.38–5.58 · "50 ringgit." 5.86 (all passes agree)
- impact 16.62 (picture; sound 16.646), turf flies; "Masuk!" 20.40 (ms) / "Go in!" (en)
- camera pans to the friend on the green (black shirt, bucket hat): hands out, "Tak dapat." 26.82–28.22 (ms; en "can't reach it")
- unclear chatter not captioned (16.6–17.5, 21.3–24.5, "belah je"?). Where the ball finished is not visible: only "tak dapat" is said about it.
Faces: the coach's head is high in frame (x 300–560 / y 60–380) → boards in the right column; the friend x 300–540 / y 240–330 → end board low (y 640).

## Structure (23.7 s)
| film | segment | on screen |
| --- | --- | --- |
| 0.00–2.40 | hook: strike 0.5×, freeze on the turf | board "Kelas hari ni: CHIP 101 / 30 m · chip in = RM50 💸" (frame 0), eraser wipe |
| 2.40–8.40 | the bet | captions + board chalked line by line: jarak 30 m · target chip in 🎯 · RM50 💸 |
| 8.40–11.40 | address + shot, raw | board stays into the address |
| 11.40–14.50 | watching: "Masuk!" | note "masuk… masuk… 🙏" |
| 14.50–19.30 | the friend: hands out, "Tak dapat." | note "RM50… tak jadi 😂" |
| 19.30–23.70 | freeze | HOMEWORK board, CTA "Korang rasa boleh chip in dari 30 meter? 🤔 / Komen, share dulu 👇" |

Preview mix re-transcribed (large-v3): every captioned line heard. −14.1 LUFS, −3.0 dBTP.

## Build
```
tools/fetch.sh && python3 tools/build_aroll.py && python3 tools/build_index.py
npx hyperframes@0.9.32 check
npx hyperframes@0.9.32 render -q draft -o renders/preview_draft.mp4 && tools/master.sh renders/preview_draft.mp4 previews/chip-rm50_preview_v1.mp4
# on "render":
npx hyperframes@0.9.32 render -q delivery -o renders/final_raw.mp4 && tools/master.sh renders/final_raw.mp4 final/chip-rm50_1080x1920.mp4
```

## v2 (owner: "Buang cta. Cara aku buat chip shot ni, takeaway dengan open club face pastu release macam biasa.")
- On-screen CTA removed (and the comment/share line removed from CAPTION.md).
- New HOW section after "Tak dapat": replay 0.5× (zoom 1.2 on hands/club/ball) with two freezes and the coach's own words chalked on:
  **1 · takeaway, buka club face** (freeze 16.02, the face shows open toward the camera) and **2 · release macam biasa** (freeze 16.80, the turf flying).
  Real strike on the slowed impact. HOMEWORK board now recaps the method. 28.6 s. −14 LUFS.

## Delivery
Owner approved v2 ("Ok render", 2026-11-13). `final/chip-rm50_1080x1920.mp4`: 28.6 s, 1080×1920, 30 fps, H.264 High ~12.5 Mbps, AAC 256k, −14.1 LUFS, −2.9 dBTP.
