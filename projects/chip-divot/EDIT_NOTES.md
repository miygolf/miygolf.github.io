# Chip atas green — "Ada divot ke tak?" — edit notes

HyperFrames 0.9.18 · 1080×1920 · 30 fps · 20.3 s · status: **draft preview v1** (`previews/chip-divot_preview_draft_v1.mp4`), waiting for
the owner's OK before the delivery render.

## Look: "Poll Sticker" (new, not in the style log)
- The edit plays like a story poll that the footage answers: "Boleh ke chip atas green?" → BOLEH ✓ → "TAK ADA DIVOT."
- Type: Sora 800/700/600 (stickers, captions) + Geist Mono 700 (pills, speed chips, labels).
- Palette: white sticker cards, violet #6b3cff (the answer), coral #ff5d4f (the doubt, "DIVOT?"), ink #16131c, lilac #efeaff.
- Shapes: rounded white sticker cards (radius 36–44 px, tilted 2–4°, soft drop shadow); captions as white sticker lines with the key word violet.
- Motion: spring pops with squash (elastic), finger-tap ripple on the poll, poll bar fills violet + check draws, focus brackets snap onto
  the contact and the turf, speed chip that changes with the footage (0.3× / 1× / 1.75× / 1× / 1.5× / 2.2× / 1×), sticker peel exits,
  white lens bloom + punch on every cut, sparkles on the clean turf, proof captures fly in like stickers.
- No colour grade (house style).

## Story (faster-whisper large-v3, Malay; `edit/transcript.txt`)
The first pass heard "Mesti tak boleh" at 8.8 s and "Clean" at 15.6 s; re-run on boosted pieces it is **"Mestilah boleh."** (four of
five runs) and **"Clean."** is said at 20.8–21.3 s, over the turf. The 15.6 s "Clean" was a hallucination on wind noise.

| film | source | what |
| --- | --- | --- |
| 0–2.17 | 10.45–11.10 @0.3× | HOOK: backswing + downswing in slow motion, push-in onto the club and ball. Card on frame 0: "UJI · ATAS GREEN / ADA DIVOT KE TAK?" (right of the face). Voice: "Boleh tak kita pakai chip ataupun wedge?" (pauses removed) |
| 2.17–2.97 | freeze 11.10 | contact frozen, shutter, focus brackets "IMPACT" |
| 2.97–6.60 | 8.55–12.20 @1× | address + the chip, real strike. Poll sticker left of the face; "Mestilah boleh." taps BOLEH ✓. Rings at the ball on contact |
| 6.60–9.70 | 12.20–13.60 @1.75×, 13.60–15.90 | pan to the green, ball rolls up by the pin |
| 9.70–12.40 | 16.30–17.20 @1.5×, 17.20–20.20 @2.2×, 20.20–20.95 | swing back to the golfer, walk up, tilt down to the spot ("02 CHECK RUMPUT") |
| 12.40–14.90 | freeze 20.95 | wedge resting on the spot: brackets "DIVOT?", voice "Clean.", then music drop + "TAK ADA DIVOT." ✓ + sparkles |
| 14.90–17.00 | freeze 20.95 | proof: 01 IMPACT (contact still) / 02 LEPAS CHIP (turf still), "0 divot · rumput clean" |
| 17.00–20.30 | freeze 20.95 | CTA: "CHIP ATAS GREEN? / MESTILAH BOLEH. / Strike clean, rumput tak rosak." + "BERANI TRY? KOMEN ↓" |

Cut out: waggles and practice swings (0–8.5 s), "So, kita on the green." (the hook card says it), the pauses inside the question,
the camera wobble 15.9–16.3 s, the slow walk (2.2×).
Not claimed: anything about rules or club policy on chipping from greens; only what the frames show (contact, turf intact) and the
owner's own words ("Mestilah boleh", "Clean").

## Face / safe zone
All text inside x 60–930, y 168–1330. Faces: hook frame 0 at x 220–400 / y 200–370 (hook card at x ≥ 520); demo at x 470–600 /
y 370–520 (poll card at x 60–380, step pill top right above the head); swing-back shot face top-left for ~0.6 s (speed chip hidden
there, step 02 enters only once the head is out of frame). Every other shot has no face. Checked in snapshots.

## Sound
- `assets/voice.wav` (tools/build_aroll.py): question pieces, "Mestilah boleh." (+10 dB), the real strike in sync (no offset needed:
  audio peak and contact on the same frame), roll ambience (−8 dB), "Clean." (+9 dB); denoise, compression, loudnorm −16 LUFS.
- Music: Mixkit #1141 "Funkee Monkeee". Measured in the draft: question voice −15.5 dB vs music+SFX −25.6; "Mestilah boleh" −14.8 vs
  −29.1; "Clean." −12.6 vs −38.1. The track's own break sits under the roll + walk, the drop lands on TAK ADA DIVOT.
- 27 SFX cues (Mixkit), each tied to something on screen (`assets/sfx/CREDITS.md`).
- Final (when approved): render `-q delivery`, then `tools/master.sh` (−14 LUFS / −1.5 dBTP).

## Rebuild
```
tools/fetch.sh                  # source -> .src/, 16 kHz audio -> .work/
python3 tools/transcribe.py     # edit/transcript.json + .txt
python3 tools/build_aroll.py    # A-roll, proof stills, voice, edit/timeline.json
python3 tools/build_index.py    # index.html (stickers, captions, music, SFX)
npx hyperframes@0.9.18 check
npx hyperframes@0.9.18 render -q draft -o renders/preview_draft.mp4
npx hyperframes@0.9.18 render -q delivery -o renders/final_raw.mp4
tools/master.sh renders/final_raw.mp4 final/chip-divot_1080x1920.mp4
```
