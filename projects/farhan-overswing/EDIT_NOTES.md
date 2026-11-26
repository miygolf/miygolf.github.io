# Edit notes — farhan-overswing (Coach Farhan)

Owner: "buat style sama tapi ni coach farhan" + Drive folder 1iXR37yryPiZXnUjv0DzD4jqbul1y2ep9 (IMG_0433 = backswing terlalu outside, IMG_0434 =
overswing; Coach Farhan says "Next. Common mistake…" in the second, so they are a 2-part series). Same "Posture Chart" look as projects/early-extension.
Footage: `../farhan-tip/tools/fetch.sh` -> farhan-tip/.src (not committed); this project links to it and to the shared tools/fonts/SFX in farhan-tip.

- Transcribed with large-v3 (a casual-Malay prompt was needed for IMG_0434: without it whisper "translated" into formal Malay).
- Pieces (content.py) chosen on crop transcripts; inside each piece pauses > 0.5 s are cut to ~0.3 s (jump cuts), every phrase ending kept
  (0.16 s after the last sound). Final voice re-transcribed: every line complete.
- Rows are the coach's points in his words; no claim beyond what he says/demonstrates. All rows sit in the top band (y 190-460): his head
  moves between y ~550 and ~1000 as the phone zooms; captions at y 1210 (torso). Max 3 rows at a time.
- Sound: his voice (light denoise) + Mixkit 2568/2364 for rows. No music. Master −14 LUFS, ≤ −1 dBTP.

Build: `python3 tools/build_aroll.py && python3 tools/build_index.py && npx hyperframes@0.9.32 render -q draft -o renders/draft.mp4 && tools/master.sh renders/draft.mp4 previews/farhan-overswing_preview_vN.mp4`
