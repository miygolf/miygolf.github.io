# REVIEW — chip-contact

Source: `IMG_6411.MOV` (Drive), 1080×1920 (rotated), 30 fps, 8.37 s. Output: 1080×1920, 30 fps, 16.4 s.

## Transcript (faster-whisper large-v3, Malay + auto, word stamps)
- 0.42–1.46 coach (off camera): "Contact with the ball is good."
- ~5.9–6.3 coach: "Good."
- Everything else: no speech. Picture beats: address 0–4.1, backswing 4.1–4.75, impact 5.12 (frame 154),
  body turns to the target 5.4+, held finish to 8.37.

## Cut
- Removed: 4 s of standing at address (the waiting), the coach line is kept but moved (J-cut) onto the hook.
- Hook (0–2.5): downswing → impact at 0.43 → 0.4× slow-mo → print freeze on the ball in the air → 0.5× ball leaves.
  Title on frame 0: "CHIP SHOT / NI RUPA CONTACT YANG BERSIH". Coach's "Contact with the ball is good." plays over it.
- 1× full speed (2.5–5.3) with the take's own sound and "Good."
- Keys: 1 Kaki senyap (0.5× backswing, rings stay on both feet; freeze at the top),
  2 Kena bersih (0.4× into impact, freeze on the contact frame, ring + dot burst on the ball),
  3 Dada pusing ke target (1× turn, freeze, arc arrow on the open side of the body).
- CTA (12.8–16.4): "PROBLEM SAMA? / SAVE. TRY KAT RANGE ↓" + recap 1-2-3.
- Copy note: the coach only said "contact is good"; keys 1 and 3 are what the frames show (feet don't move,
  chest faces the target at the finish). No "head stays down" — she turns her head with the ball, so that claim was dropped.

## Look — "Riso Press" (new; not in STYLE-LOG / DESIGN_LOG)
- Two-ink risograph zine: riso blue `#1d3fbb` + fluoro pink `#ff4fa3` on pink-white paper `#fff4f8`.
- Type: Dela Gothic One (titles), Instrument Sans 700 (labels).
- Every text block is a paper slip that feeds out top-down; the pink ink lands 6/4 px out of register on purpose (multiply).
- Every freeze is printed: the frame becomes a blue screen print (HyperFrames monoScreen, custom 2-colour palette) that feeds
  in behind a pink roller bar. Live footage: light warm-daylight grade.
- Transitions: halftone dot wipe (pink over blue grid of dots) at 2.5, 5.3, 12.8.
- Hook strike: the whole title sheet jolts out of register and settles.
- Registration crosshairs ⊕ on the hook and CTA.

## Safe zone / faces
- All text inside x 60–930, y 168–1330. Hook and keys 1–2 are punched in (1.45 / 1.35 / 1.6 from the bottom) so the head
  is out of frame and the ball/feet sit higher; key 3 and CTA blocks sit low (y 940+ / 766+) because the head is at y 300–520.
- The foot rings in key 1 dip to y ~1440 (graphic, no text).

## Sound
- Voice: coach line + 1× take, highpass 90 Hz, afftdn, presence +3 dB, 3:1 compression, speech lifted to about −16 LUFS.
- Music: Mixkit "Okay" (ska, 155 BPM) from its section B downbeat, so the band kicks in on the hook strike;
  volume 0.30, ducked to 0.11 under the coach line and 0.14 under the 1× take; high-pass 90 Hz and a −5 dB dip at 2.5 kHz.
- SFX: Mixkit (see `assets/sfx/CREDITS.md`), each with a cause on screen, peak placed on the picture beat.
- Final master (after "render"): −14 LUFS, ≤ −1 dBTP.

## Rebuild
```
python3 tools/build_aroll.py   # needs .src/upright.mp4 + .src/raw.MOV (see tools/fetch.sh)
python3 tools/build_index.py
npx hyperframes@0.9.18 check
npx hyperframes@0.9.18 render -q draft
```
