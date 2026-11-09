# Match play 1 lawan 1 — hole 2, KRTU (Iqbal vs Farhan) — edit notes

HyperFrames 0.9.18 · 1080×1920 · 30 fps · 75.4 s · status: **draft preview v2** (`previews/match-play-hole2_preview_draft_v2.mp4`, 720p copy of the draft render). Final not rendered yet.

v2 (owner feedback): darker grade (was too bright), longer cut (64 → 75 s), outro message "PUKUL JAUH TAK SEMESTINYA BOLEH MENANG", long SFX trimmed so every spoken line stays ≥ 8 dB above the bed (only the 0.3 s KO punch sits on the ball drop).

## Look: "Title Fight" (new, not in the style log)
- Hole 2 as a fight-night match-play broadcast: red corner IQBAL, blue corner FARHAN, gold for the result.
- Type: Big Shoulders Display 900 (titles, captions) + Oxanium 700 (labels). Palette: red #ff2a3d, blue #2b6cff, gold #ffc23a, ink #0b0b10, white.
- Shapes: plates cut on a 12° slash with hard ink offset shadows; captions skewed, white with an ink stroke and a drop shadow in the
  player's corner colour, key word gold.
- Motion: slash wipes (ink + corner colour + white) on every section cut, plates slam in from the right, shockwave ring + camera
  punch + flash on every strike, diagonal VS card with a ring bell, letterbox on the deciding putt, KO-style result slam with a gold burst,
  the HUD fight bar turns gold with a W for the winner.

## Grade (v2)
`eq=contrast=1.10:saturation=1.06:gamma=0.86`, curves pulling mids and highlights down (sky tamed), colour balance a little cool in the
shadows and warm in the highlights. Applied in `tools/build_aroll.py` (GRADE) to every segment and the VS stills.

## Story (transcribed with faster-whisper large-v3, Malay + English; `edit/transcript.txt`)
v2 timings shift from the table below (v1): added "154." + "kita ada branch kat depan tu" + "supaya elak" to Iqbal's plan, "kita control sikit"
to Farhan's, "Kenapa jadi begitu?" before his why, "Hole 2, Iqbal." before the birdie read, and a 7.5 s outro: result card →
"FARHAN 150 M KE PIN · IQBAL 154 M" → PUKUL JAUH / TAK SEMESTINYA / BOLEH MENANG. → "SETUJU? KOMEN ↓ · HOLE 3 NEXT".
Music: quiet build under the VS card and tee shots, first drop on the cut into Iqbal's approach (11.77 s), break under the par putt,
second drop on the ball going in (64.73 s).

| film | source | what |
| --- | --- | --- |
| 0–3.5 | clip4 16.2–18.95 + freeze | HOOK: Farhan's chip comes out fat → "Astagfirullah." → freeze, "TAPI… SIAPA MENANG?" (text on frame 0: IQBAL · 1 LAWAN 1 · FARHAN / HOLE 2) |
| 3.5–6.2 | stills clip6 81.05, clip1 13.5 | VS card: RED CORNER IQBAL vs BLUE CORNER FARHAN, MATCH PLAY · HOLE 2 · PAR 4 · KRTU SUBANG; music drop + ring bell |
| 6.2–11.8 | clip1 3.55–6.25, 37.85–40.75 | Tee shots (Farhan, then Iqbal), real strike sound |
| 11.8–22.0 | clip2 12.4–17.4, 38.3–41.5, 49.3–51.45 | Iqbal's approach: "Saya akan buat draw … aim kat bunker … bagi dia curve masuk" over his view, drawn curve around the branch; swing; "Buat a good shot. Tapi over sikit." |
| 22.0–29.2 | clip3 18.4–21.8, 29.95–33.4 | Farhan's approach: "middle, 150 … pakai P, bola kat belakang"; swing |
| 29.2–34.0 | clip4 16.95–17.95 @0.5×, 28.85–32.95 | Chip replay (FAT!), Farhan's own why: "you try to scoop … the weight tertinggal belakang" (pause cut, punch-in hides the jump) |
| 34.0–41.2 | clip5 0.62–1.9, 29.0–33.7, 35.85–36.99 | "Hole 2, disaster" → putt → "Bogey." (BOGEY stamp) |
| 41.2–52.2 | clip6 21.95–31.7, 34.0–35.35 | Iqbal's birdie putt: "I think for birdie. Fast, downhill putt. Left to right. Back to back birdie." over a 4K push-in, pull back with the roll ("need to slow down"), "Okay, not too bad." |
| 52.2–57.8 | clip6 72.35–76.6 (0.4× on the roll) | Par putt, letterbox, "MASUK = MENANG HOLE"; music break under the roll, drop + KO on the ball going in: IQBAL MENANG HOLE 2! "Good save!" |
| 57.8–64.3 | clip6 79.2–81.1 + freeze | "Next hole." → result card (IQBAL PAR 4 W / FARHAN BOGEY 5) + CTA "HOLE 3, FARHAN BALAS?" |

Cut out: the third player in the flight (tee shots, intro, coaching chatter), walking, waiting, waggles, the repeated "need to slow down",
whisper's hallucinated "Terima kasih kerana menonton" at the end of clip4, and pauses inside every spoken line.
Not claimed: overall match status (only hole 2 is shown). Farhan's score is his own word ("Bogey").

## Face / safe zone
All text inside x 60–930, y 168–1330. Faces sit at y 340–880, x 120–580 across the shots, so: HUD at y 178–256 (hidden on the
close-up "disaster" shot), shot plates top-right (y 286–460), captions in the y 1110–1320 band, VS names placed beside the faces,
result card below Iqbal's face on the final freeze. Checked in snapshots.

## Sound
- `assets/voice.wav` (tools/build_aroll.py): pauses removed, denoise, compression, loudnorm −16 LUFS. Real strike sounds kept.
- Music: Mixkit track #400 (~144 BPM) from the VS card on; first drop on the VS slam, break under the par putt, second drop on the
  ball going in. 0.30 bed, 0.08 under speech (≈ 16 dB below), 0.40–0.44 on the two drops.
- SFX: Mixkit ids + HyperFrames bundle + a synthesised ring bell, 49 cues, each tied to something on screen (`assets/sfx/CREDITS.md`).
- Final (when approved): render `-q delivery`, then `tools/master.sh` (two-pass loudnorm −14 LUFS / −1.5 dBTP, H.264 CRF 17 ≤ 16 Mbps).

## Rebuild
```
tools/fetch.sh                  # sources -> .src/, 16 kHz audio -> .work/
python3 tools/transcribe.py     # edit/transcript.json + .txt (faster-whisper large-v3)
python3 tools/make_bell.py      # ring bell SFX
python3 tools/build_aroll.py    # A-roll, VS stills, voice, edit/timeline.json
python3 tools/build_index.py    # index.html (graphics, captions, music, SFX)
npx hyperframes@0.9.18 check
npx hyperframes@0.9.18 render -q draft -o renders/preview_draft.mp4
```
