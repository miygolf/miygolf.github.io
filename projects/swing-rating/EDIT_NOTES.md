# Rate swing: sebelum vs selepas adjust — edit notes

HyperFrames 0.9.32 · 1080×1920 · 30 fps · 43.3 s · status: **final delivered** (`final/swing-rating_1080x1920.mp4`, 54 MB): H.264 High ~10 Mbps, AAC 256k 48 kHz, −14.0 LUFS, peak −1.1 dBFS.
Owner approved draft preview v1 unchanged ("cun", 2026-11-12).

Request (2026-11-12): HyperFrames, transcribe first, motion graphics + premium SFX where they belong, never over the face, TikTok/IG safe zone,
voice not buried, cut repeats and awkward pauses, strongest hook, preview before render, a design not used before, and
**"rate his swing before and after adjustment"**.

## Footage (4 clips, iPhone 4K HEVC HLG 59.94 fps, tripod, upright)
Ordered by recording time: before = earlier, after = later.

| clip | time | view | phase | address · takeaway · top · impact · finish (frame @59.94) |
| --- | --- | --- | --- | --- |
| clip3 | 09:50:20 | down the line, open range | BEFORE | 134 · 137 · 168 · 183 · ~230 (first ~2.2 s standing over the ball, cut) |
| clip2 | 09:50:41 | face on, bay 7 | BEFORE | 8 · 10 · 54 · 69 · ~110 |
| clip4 | 10:00:14 | face on, bay 7 | AFTER | 33 · 36 · 84 · 105 · ~150 |
| clip1 | 10:25:28 | down the line, open range | AFTER | 48 · 51 · 84 · 100 · ~170 |

## Transcript
faster-whisper large-v3, Malay + auto pass, every clip (`edit/transcript.txt`): **no speech**. Each pass returns only the stock
hallucination "Terima kasih kerana menonton!" / "Thank you for watching" on range noise. So there is no voice to protect and no captions;
cuts sit on swing beats, and the only sync sound is the real strike (camera audio lands ~0.025 s after the impact frame; read that much later).

## The rating (mine, from measurements, no coach diagnosis given)
MediaPipe Pose Landmarker (heavy) on every frame (`tools/pose.py` → `edit/pose.json`), metrics at the key frames (`tools/metrics.py` → `edit/metrics.json`).
Lines on screen are drawn from these landmarks, so they sit on the body.

| | before | after | on screen |
| --- | --- | --- | --- |
| Spine tilt from vertical at address (DTL) | 30° | 28° | SETUP 7.0 → 7.0 |
| Spine tilt at impact (DTL) | 13° (lost 18°) | 21° (lost 7°) | IMPACT 4.5 → 7.5, "-18°" vs "-7°" |
| Hips toward the ball, address → impact (% torso) | 16 % | 9 % | "pinggul tolak ke bola" / "pinggul stay" |
| Head shift at the top (face on, % torso) | 13 % away from target | 4 % | KEPALA 6.5 → 7.5 ("lari sikit" / "stay tengah") |
| Head rise at the top (DTL, % torso) | 8 % | 1 % | (supports KEPALA) |
| Finish | balanced, held | balanced, held | FINISH 8.0 → 8.0 |
| **Overall (mean)** | **6.5** | **7.5** | UPGRADE +1.0 |

Not rated: tempo (DTL says ~2.1:1 both times, face on says 2.9 → 2.3; the two angles disagree, so no claim).
Head **drops** more at impact after (20 % vs 12 % torso) → shown as "NEXT: kepala jangan dip masa impact".
"Apa yang berubah" lists only what the measurements show changed; it does not claim what the coach said.

## Look: "Card Grade" (new, not in the style log)
The swing graded like a collectible card. Grading-slab label plates (white stock, colour strip, mono cert line) flick in with a card-flick
rotateY; every freeze snaps a rounded card edge round the frame with a foil glint running once along it; the grade sections shrink the
frame into a clear acrylic slab (card art left, four stat rows with bars right, grade rolls up on the label). BEFORE = common card (rust strip),
AFTER = holo card (iridescent strip and shimmer, UPGRADE stamp, sparkles). Section changes are a diagonal foil sweep + soft flash.
Type: Rubik Mono One + Schibsted Grotesk 800/700 + Chivo Mono 600. Palette: ink #101014, stock #f6f5f0, rust #ff5b24, holo #7cf3ff→#b18cff→#ff8fd0→#ffe27a
(deep holo #0093b8→#5b2cff→#d42682→#c27a00 for text on white). No colour grade (iPhone's own colour).

## Cut (film s)
| film | source | what |
| --- | --- | --- |
| 0.00–0.93 | clip3 / clip1, impact-0.46 → impact @0.5× | HOOK split screen, both DTL swings synced into impact; RATE SWING plate on frame 0, SEBELUM / SELEPAS tags |
| 0.93–3.53 | freeze on both impacts | card edge, spine lines (address dashed, impact solid + angle arc), "?.?" grades, "mana satu lagi power? 🤔" |
| 3.53–5.43 | clip3 2.05–3.95 | foil sweep → 01 SEBELUM ADJUST, full swing 1×, real strike |
| 5.43–6.13 | clip3 2.70→impact @0.5× | 0.5× replay |
| 6.13–9.43 | freeze impact | lines 30° → 13°, "-18° POSTUR HILANG", "pinggul tolak ke bola → badan bangun" |
| 9.43–13.03 | clip2 0→top, freeze top, push-in 1.7× | pins above the cap: address x vs top x, arrow, "KEPALA LARI SIKIT" |
| 13.03–14.53 | clip2 top → 2.40 | rest of the swing 1×, real strike |
| 14.53–17.33 | freeze finish | frame shrinks into the BEFORE slab: grade 6.5, stat rows |
| 17.33–23.53 | clip1 | foil sweep → 02 SELEPAS ADJUST, 1×, 0.5×, freeze: 28° → 21°, "-7° POSTUR STAY" |
| 23.53–28.53 | clip4 | face on, freeze top + push-in, "KEPALA STAY", rest of swing |
| 28.53–31.93 | freeze finish | AFTER holo slab: 7.5, UPGRADE +1.0, sparkles |
| 31.93–36.20 | split clip3 / clip1, 1×, synced on impact | SIDE BY SIDE full speed, then the impact freeze with "-18°" vs "-7°" (answers the hook) |
| 36.20–38.90 | clip1 0.66–3.36 | after swing 1× again, "3 BENDA JE": pinggul stay belakang / dada tunduk sampai impact / kepala lebih stay |
| 38.90–43.30 | freeze, back to camera | 6.5 › 7.5, NEXT chip, CTA "Nak aku rate swing korang? Comment RATE ↓ · save dulu 📌" |

## Face / safe zone
All text inside x 60–930, y 168–1330. Head boxes (from pose, printed by `tools/build_index.py`) checked against every plate in snapshots:
DTL heads y ≈ 750–965 → plates and callouts in the sky above (y ≤ 620) and notes over the legs (y ≥ 1180); face-on freezes push in on the head
and keep text below it (y ≥ 1050) with only small pins above the cap; slabs put the face inside the card art; the end card's golfer has his back to camera.

## Sound
`assets/voice.wav` (`tools/build_aroll.py`): sync camera sound of each 1× piece (the real strikes), strikes re-used on the slowed freezes, range ambience under freezes,
light denoise + limiter, loudnorm −18 LUFS. **No music.** 75 SFX cues (Mixkit, `assets/sfx/CREDITS.md`), each tied to something on screen.
Delivery (when approved): `render -q delivery`, then `tools/master.sh` (−14 LUFS / −1.5 dBTP, H.264 ≤ 13 Mbps).

## Rebuild
```
tools/fetch.sh                  # sources -> .src/, audio + frames -> work/, pose model
python3 tools/transcribe.py     # edit/transcript.json/.txt (no speech)
python3 tools/pose.py           # edit/pose.json
python3 tools/metrics.py        # edit/metrics.json
python3 tools/build_aroll.py    # assets/aroll.mp4, assets/voice.wav, edit/timeline.json
python3 tools/build_index.py    # index.html
npx hyperframes@0.9.32 check
npx hyperframes@0.9.32 render -q draft -o renders/preview_draft.mp4
npx hyperframes@0.9.32 render -q delivery -o renders/final_raw.mp4
tools/master.sh renders/final_raw.mp4 final/swing-rating_1080x1920.mp4
```
