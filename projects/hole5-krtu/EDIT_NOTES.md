# Hole 5 KRTU — par 3, 180 m — edit notes

HyperFrames 0.9.18 · 1080×1920 · 30 fps · 61.5 s · status: **draft preview v2** (`previews/hole5-krtu_preview_draft_v2.mp4`; v2 = CTA changed to "Follow for more video"),
waiting for the owner's OK before the delivery render.

## Look: "Departure Board" (new, not in the style log)
- The hole is played like a flight: a split-flap departures board carries the hole info, every shot gets a boarding pass, and the
  outcome of each shot lands as an ink passport stamp. Ends on an ARRIVALS board ("HOLE 05 DONE / HOLE 06 SOON").
- Type: Archivo (variable width; 850 at 112 % for words, 900 for stamps) + Martian Mono 600/700 (flaps, ticket fields).
- Palette: flap black #121315 with warm white #f3efe4, departure yellow #ffd23f, stamp ultramarine #2443d8, ticket paper #f6f1e4,
  ticket ink #1b1c1f.
- Motion: flap characters riffle through letters before they land; flap-slat wipes on the two section cuts (REWIND, GREEN);
  boarding passes slide in, their stub tears off at the perforation before they leave; stamps thump down (scale 1.9 → 1, ink ring);
  a dashed yellow break line draws from the ball to the hole on "right to left"; captions are flap tiles, key word yellow;
  REPLAY / SLOW tags on the slow-motion pieces. No colour grade.

## Story (faster-whisper large-v3; Malay pass `edit/transcript.txt`, Malay + English re-pass `edit/transcript_pass2.txt`)
Only lines both passes agree on are captioned. Dropped as unclear: "Iron berapa tu? / Enam" (second pass: "Is that a good one? Yes"),
the walk-by line at the end of clip2, "Masuk, bonus" in clip3. "Aku try pakai iron five eh" was heard as "try pakai … five" by both
full-clip passes and is captioned; the boarding pass says IRON 5 from it.

| film | source | what |
| --- | --- | --- |
| 0–3.0 | clip4 15.95–17.35 + freeze | HOOK: grey's birdie putt rolls up and stops just short of the hole. Board on frame 0 (DEPARTURES · KRTU / HOLE 05 PAR 3 / STATUS BIRDIE PUTT) → "Sikit." → status flips to SIKIT JE!, stamp |
| 3.0–8.3 | clip2 0–2.3, clip1 0.3–3.3 | REWIND slat wipe → "Okay, come play with us." → hole sign under "Lubang lima, par tiga, KRTU, 180 meter." |
| 8.3–18.0 | clip2 13.0–20.0, 16.2–16.75 @0.4×, 24.4–25.75 | teal tee shot (pass 01: 180 M, PIN BELAKANG), real strike, "Good line." stamp, slow replay, "Pendek sikit." stamp |
| 18.0–30.6 | clip2 34.2–37.15, 43.05–45.2, 50.6–54.1, 51.95–52.5 @0.4×, 58.4–61.0 | grey: "180, pin belakang." / "Aku try pakai iron 5." (pass 02), strike, "Good swing." stamp, slow replay, "Center." → CENTER GREEN stamp |
| 30.6–44.5 | clip3 4.15–16.85 (pauses cut), 21.95–25.1, 25.8–28.55 | GREEN slat wipe → teal: "Putt for birdie." "Nampak dia, slope banyak." "Right to left." (break line drawn) "Sejujurnya, make sure bola sampai." "Lebih sampai je." → putt → ball stops by the pin, DEKAT PIN stamp |
| 44.5–55.5 | clip4 8.6–13.7, 13.7–15.95 @1.5×, 15.95–17.35 @0.5×, freeze | grey's birdie putt (pass 04 FINAL CALL), slow roll (every 60 fps frame), stop by the hole, "Sikit.", SIKIT LAGI! stamp, music groove returns |
| 55.5–61.5 | freeze | ARRIVALS board + CTA "Follow for more video" + "PERNAH SIKIT LAGI? KOMEN ↓" (v2, owner) |

Cut out: walking, waiting, practice swings and practice strokes, "hole five" said three times (kept once with the sign), the second
"pendek sikit", the pause before "Sejujurnya", the close walk-by at the end of clip2.
Not claimed: scores (no tap-ins are shown), names, where the teal ball lay before the putt.

## Face / safe zone
All text inside x 60–930, y 168–1330. Faces: intro at the left edge (board top, captions low); tee shots face at x 540–640 /
y 480–600 (passes x 60–500 top-left, stamps beside/below the body); slow replays face top (stamps on the left, below it);
green 1 face at x 250–520 / y 490–620 (pass 03 moved top-right, HUD hidden while it is up); green 2 face top-right (pass top-left).
Checked in snapshots.

## Sound
- `assets/voice.wav` (tools/build_aroll.py): dialogue + real strikes in sync (audio transient = impact frame on these takes, so no
  offset), "Center." +9 dB, "Sikit." +6 dB; denoise, compression, loudnorm −16 LUFS.
- Music: Mixkit #989, quiet stretch under green 2, groove back on the stop. Measured in the draft (after taking out the renderer's
  mix gain): spoken lines 8–20 dB over everything else (lowest where a stamp lands right after a word), bed ≈ 3 dB under the
  voice level between lines.
- 33 SFX cues (Mixkit), each tied to something on screen (`assets/sfx/CREDITS.md`).
- Final (when approved): render `-q delivery`, then `tools/master.sh` (−14 LUFS / −1.5 dBTP).

## Rebuild
```
tools/fetch.sh
python3 tools/transcribe.py
python3 tools/build_aroll.py
python3 tools/build_index.py
npx hyperframes@0.9.18 check
npx hyperframes@0.9.18 render -q draft -o renders/preview_draft.mp4
npx hyperframes@0.9.18 render -q delivery -o renders/final_raw.mp4
tools/master.sh renders/final_raw.mp4 final/hole5-krtu_1080x1920.mp4
```
