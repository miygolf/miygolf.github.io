# Farhan — chip, putt, MASUK — edit notes

HyperFrames 0.9.32 · 1080×1920 · 30 fps · 21.9 s · status: **draft preview v1** (`previews/farhan-masuk_preview_draft_v1.mp4`).
Not rendered for delivery yet: render only when the owner says "render".

Request (2026-11-11): HyperFrames, transcribe first, motion graphics and SFX where they belong, premium SFX, never over the face,
TikTok/IG safe zone, voice must stay on top, cut repeats and awkward pauses, strongest hook, new design, **casual style with less animation**.

## Look: "Group Chat" (new, not in the style log)
- The hole told the way it lands in the friends' group chat. The narrator's lines are tangerine "sent" bubbles (right), each word lights up
  as it's spoken; shot labels are small ink "date" pills in the centre; one sticker word per beat; a typing indicator for the suspense.
- Type: Plus Jakarta Sans 800 (bubbles, pills) + Bagel Fat One (stickers) + Noto Color Emoji.
- Palette: tangerine #e2530b (white text 3.8:1), bubble white #ffffff, ink #17181c, pill ink rgba(23,24,28,0.74), muted #8b9098.
- Motion (kept low on purpose): bubbles grow out of their tail corner, pills fade up, stickers pop with a small tilt, hard cuts between shots,
  no wipes, no colour grade (iPhone's own colour).

## Transcript (faster-whisper large-v3, Malay; `edit/transcript.json`, words pinned with cropped re-runs + the speech energy)
- clip1 (IMG_0058, tee): 0.0–0.8 "(Si/Encik) Farhan" · 1.3–2.6 unclear (cut) · 3.05–4.7 "Tengok dia boleh convert birdie ke" · 1.4 s pause (cut to 0.22 s) ·
  6.1–7.2 "bogey, kita tengok." Waggles 3–11.5 (cut). Impact 12.43.
- clip2 (IMG_0062, chip): no speech (whisper's "Terima kasih kerana menonton" is a hallucination). Contact 13.05, camera follows the ball to the pin.
- clip3 (IMG_0063, putt): "Pau-pau/Opa" 0–1.5 unclear (cut) · stroke 8.85 · **ball drops 10.25** (checked frame by frame) · 11.0–11.95 "Tu nasib" ·
  12.4–13.2 "nasib tu, yang mana nasib" (repeat, cut) · picks the ball out 13.6–14.5 · stands up facing camera 15.0.
- The name word is unclear ("Encik" vs "Si"), so it is not captioned; the pill says FARHAN instead.

## Cut
| film (s) | source | what |
| --- | --- | --- |
| 0.00–2.17 | clip3 7.60–9.75 | HOOK: the putt, wide. Narrator's line from the tee over it, word by word in the bubble (text on frame 0) |
| 2.17–2.97 | clip3 9.75–10.15 @0.5× | cut in tight on the cup, ball rolling to the lip |
| 2.97–4.83 | freeze 10.15 | ball on the lip: typing… → **MASUK KE TAK? 👀** |
| 4.83–5.70 | clip1 0.00–0.85 | "Farhan" walking onto the tee · pill FARHAN · TEE SHOT |
| 5.70–8.63 | clip1 11.30–14.25 | driver, real strike (+ Mixkit layer) |
| 8.63–12.43 | clip2 11.95–15.75 | CHIP 🤞, camera follows the ball |
| 12.43–17.20 | clip3 7.20–11.98 | PUTT ⛳ full, drop at 15.48 → **MASUK!! 🔥**, "Tu nasib 😂" bubble |
| 17.20–18.57 | clip3 13.62–15.00 | picks the ball out of the cup |
| 18.57–21.87 | freeze 15.00 | end card: CHIP → PUTT → MASUK ✅ · "Skill ke nasib? 😂 Komen 👇" |

Not claimed on screen: the score on the hole (no one says it; the narrator's "birdie ke… bogey" is shown as his words only), the hole number, distances.

## Face / safe zone
All text inside x 60–930, y 168–1330. Checked in snapshots:
- hook wide: head at y ≈ 650 → bubbles at y 228–500, right side. The tight cup shot has no face in frame (a cut, not a push-in, so the head
  never travels through the bubbles). Sticker sits under the ball (ball y ≈ 860, sticker y 1108+).
- tee: head x ≈ 480, y ≈ 420–540 → pill at y 196–250. Chip: head y ≈ 600 → pill at the top. Putt: head x ≈ 525, y ≈ 625 → MASUK!! at y 236–380,
  "Tu nasib" bubble right of the head (x ≥ 640). End freeze: face y ≈ 345 → end card at y 1086–1320 (over the legs/grass).

## Sound
- `assets/voice.wav` (`tools/build_aroll.py`): narrator pieces lifted +9 dB over the course ambience, pause after "ke" cut, denoise, compression, loudnorm −16 LUFS.
  Real strike, chip and cup sounds kept. No music (house rule: final = SFX only).
- 18 SFX cues (Mixkit ids, `assets/sfx/CREDITS.md`), each tied to something on screen; nothing louder than 0.3 sits on a spoken word.
- Preview measured: speech ≈ −18 dB RMS vs ambience ≈ −23 dB; whisper re-transcribes every spoken line from the mixed preview.
- Delivery (when approved): `render -q delivery`, then `tools/master.sh` (−14 LUFS / −1.5 dBTP, H.264 CRF 17 ≤ 16 Mbps).

## Rebuild
```
tools/fetch.sh                  # sources -> .src/, 16 kHz audio -> work/
python3 tools/transcribe.py     # edit/transcript.json
python3 tools/build_aroll.py    # assets/aroll.mp4, assets/voice.wav, edit/timeline.json
python3 tools/build_index.py    # index.html (bubbles, pills, stickers, SFX)
npx hyperframes@0.9.32 check
npx hyperframes@0.9.32 render -q draft -o renders/preview_draft.mp4
npx hyperframes@0.9.32 render -q delivery -o renders/final_raw.mp4
tools/master.sh renders/final_raw.mp4 final/farhan-masuk_1080x1920.mp4
```
