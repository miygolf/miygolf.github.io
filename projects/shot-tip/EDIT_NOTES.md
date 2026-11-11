# Tip: bola dalam bunker, plenty of green — Coach Farhan — edit notes

HyperFrames 0.9.32 · 1080×1920 · 30 fps · 25.4 s · status: **final delivered** (`final/shot-tip_1080x1920.mp4`, 52 MB):
H.264 High ~16 Mbps, AAC 256k 48 kHz, −14.2 LUFS, peak −1.5 dBFS. Owner approved draft preview v1 unchanged ("cun", 2026-11-11).

Request (2026-11-11): HyperFrames, transcribe first, motion graphics and SFX where they belong, premium SFX, never over the face,
TikTok/IG safe zone, cut repeats and awkward pauses, strongest hook, preview before render, a design not used before, "tip how to play this shot",
**no background music** (the request also says "letak background music"; the last instruction, "no background music", wins: SFX only).

## Look: "Shot Manual" (new, not in the style log)
- The coach's tip as a fold-out instruction leaflet: each step is a paper panel that unfolds from its crease, numbered with an ink disc,
  condensed headline in the coach's own words, a mono spec line under it.
- Type: Anybody (variable width; 850 at wdth 62 for headlines, 700 at wdth 88 for captions) + Azeret Mono 600 (labels) + Noto Color Emoji.
- Palette: paper #fbfbf6, ink #111316, signal cyan #10bfff (fills and lines only, never cyan text on paper), mute #5d6168.
- Motion: panels unfold (rotateX from the top edge, crease shading fades), fold back up to leave; accordion-fold wipe (paper / grey / cyan panels)
  into the tip and into the replay; dashed flight line + pulsing landing ring for "visualize"; checklist pips tick before the swing;
  warning triangle on ACCELERATE; stamp on the 0.5× replay; captions are paper strips, each word lights as spoken, key word underlined cyan;
  white flash + small punch on the strikes. No colour grade (iPhone's own colour).

## Transcript (faster-whisper large-v3; Malay pass `edit/transcript.txt`, English pass `edit/transcript_en.txt`, words pinned with `tools/pin_words.py`)
- Narrator (behind the phone): 0.00–0.86 "Coach Farhan, ni" · 1.5 s pause (cut) · 2.38–3.08 "nak buat macam mana ni?" · 3.46–4.38 "Ada tip tak?"
- Coach: 4.78–7.62 "Kita ada plenty of green to play." · 8.38–9.68 "So nak buka pun," (incomplete, cut, camera pans away) ·
  11.20–12.48 "Okay dah, silap bawa kayu, bawa 60." · 12.74–14.96 "So kita try to do normal pitch," · 15.46–17.88 "but then you kena make sure you accelerate"
  (word end pinned with the next word in the crop; it is soft, lifted +5 dB) · 17.92–22.02 "because bunker ni memang most of the time you akan hit shot." (unclear ending, cut) ·
  22.34 "So kita try." (cut) · 25.38–26.14 "Satu atau dua," (cut) · 26.18–28.82 "kita visualize mana you nak hantar bola tu." · 30.00–30.80 "Kita do normal," (repeat, cut) · 30.80–31.36 "normal pitch."
- Shot: backswing 33.62, **impact 34.24** (sound transient 34.25 and the frame agree), finish 34.6–35.3, then the camera pans to the green (ball not visible, cut).
- 36.7–37.4 the narrator's reaction: first pass "Keluat lah", English pass "Get out, bro", boosted re-runs disagree → kept as sound over the replay, **not captioned**.
- 39.78–40.52 "Let's go."

Not claimed on screen: what "silap bawa kayu" means beyond the club he has (60°), distances, why to accelerate (that line was unclear and is cut).
Step sub-lines are plain-word glosses of what he said: "guna 60° tu je" (he only has the 60), "make sure, jangan slow" (accelerate), "mana nak hantar bola".

## Cut
| film (s) | source | what |
| --- | --- | --- |
| 0.00–0.97 | 33.00–33.95 | HOOK: the real shot from address into the backswing, title panel on frame 0 "SHOT NI MAIN MACAM MANA?", narrator's question over it |
| 0.97–1.60 | 33.95–34.27 @0.5× | through impact (every 60 fps frame), flash + punch on 1.55 |
| 1.60–3.13 | freeze 34.27 | ball leaving in a puff of sand · "3 STEP JE ↓" tag · "Ada tip tak?" |
| 3.13–6.13 | 4.70–7.70 | fold wipe → 00 SITUASI · PLENTY OF GREEN, GREEN → chip as he points the club |
| 6.13–7.40 | 11.30–12.58 | "silap bawa kayu, bawa 60" · KAYU 60° 😅 chip |
| 7.40–9.67 | 12.70–14.98 | 01 NORMAL PITCH |
| 9.67–12.17 | 15.40–17.90 | punch-in hides the jump cut · 02 ACCELERATE + warning triangle |
| 12.17–14.93 | 26.12–28.90 | 03 VISUALIZE, dashed flight line from the ball out over the right lip to a TARGET ring |
| 14.93–19.50 | 30.72–35.30 | "normal pitch." · checklist 1 PITCH / 2 ACCEL / 3 TARGET ticks · the shot at 1×, flash on impact 18.45 |
| 19.50–21.10 | 33.95–34.75 @0.5× | fold wipe → REPLAY 0.5×, tight on the strike · STEP 2 ✓ ACCELERATE stamp · narrator's reaction |
| 21.10–24.07 | 39.30–42.25 | "Let's go!" · end leaflet: 1 NORMAL PITCH / 2 ACCELERATE / 3 VISUALIZE · "SAVE DULU, TRY NEXT ROUND 📌" |
| 24.07–25.37 | freeze 42.25 | end card hold |

## Face / safe zone
All text inside x 60–930, y 168–1330. Checked in snapshots (`npx hyperframes snapshot`):
- Talking shots: head y ≈ 490–760 on the film → panels at y 192–~410 (above the cap), captions at y 1188+ (over the legs / sand), chips on the right over the grass.
- Hook: framed so the cap sits under the title panel (head y ≈ 630); tag right of the head.
- Replay: head at the top-left of the tight frame → only a small REPLAY tag top-right and the stamp right of the body.
- End: head y ≈ 765–860 → leaflet y 192–~560, SAVE tag above the cap.

## Sound
- `assets/voice.wav` (`tools/build_aroll.py`): sync sound of each piece, narrator's question re-spaced over the hook, real strike kept (and re-used on the 0.5× hits),
  "accelerate" lifted +5 dB, denoise, compression, loudnorm −16 LUFS. **No music.**
- 30 SFX cues (Mixkit ids, `assets/sfx/CREDITS.md`), each tied to something on screen; anything over a spoken word is ≤ 0.3 volume and the step-2 / 60° sounds land after the word.
- Preview checked by re-transcribing its mix: every captioned line is heard except "accelerate", which whisper hears as a mumble both in the source crop and the mix (the coach says it softly; both full-clip passes agree on the word).
- Delivery (when approved): `render -q delivery`, then `tools/master.sh` (−14 LUFS / −1.5 dBTP, H.264 CRF 17 ≤ 16 Mbps).

## Rebuild
```
tools/fetch.sh                  # source -> .src/, 16 kHz audio -> work/
python3 tools/transcribe.py     # edit/transcript.json (+ python3 tools/transcribe.py en)
python3 tools/build_aroll.py    # assets/aroll.mp4, assets/voice.wav, edit/timeline.json
python3 tools/build_index.py    # index.html (panels, chips, flight line, captions, SFX)
npx hyperframes@0.9.32 check
npx hyperframes@0.9.32 render -q draft -o renders/preview_draft.mp4
npx hyperframes@0.9.32 render -q delivery -o renders/final_raw.mp4
tools/master.sh renders/final_raw.mp4 final/shot-tip_1080x1920.mp4
```
