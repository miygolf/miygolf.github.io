# Coach pun duff — edit notes

**Look: "Trail Cam"** — the duff told as wildlife footage. The tripod phone is a trail camera (amber data bar with the phone's real record clock,
REC dot, mode pill REW / FF ×7 / REPLAY ½× / CAPTURED, shutter flash on every trigger); the narration is a naturalist's field tags
(khaki card stock on a string, punched hole, soft serif). Fraunces (opsz 144, SOFT 100, WONK 1; italic) + Share Tech Mono + Noto Color Emoji.
Palette: bark ink #16130e, card khaki #efe5c8, trail-cam amber #ffb21a, REC red #ff3b2f, stamp moss #2f5a2c. No grade.

## Sources
- `clip1` IMG_0187 (4.6 s, handheld): ball's lie close-up, tilt up to the flag, drifts down to the tripod spot.
- `clip2` IMG_0188 (31.3 s, tripod): coach walks in, ~16 s of setup (address 5.5 → take-away 21.6), impact 22.15 (sound peak 22.166),
  a chunk of turf flies, stare, walks to the phone laughing.
- **No speech** in either clip (faster-whisper small, ms + auto: only end-of-silence hallucinations, `edit/transcript.txt`). Cut on picture beats.

## Structure (18.4 s)
| film | segment | what's on screen |
| --- | --- | --- |
| 0.00–2.63 | hook: strike 0.5×, freeze on the turf in the air | title tag on frame 0 "Coach pun boleh *duff.*", shutter flash, TERTANGKAP 📸 stamp |
| 2.63–3.53 | rewind ×21 over the setup (desaturated, tracking bands) | ◀◀ pill, clock runs backwards |
| 3.53–5.93 | habitat: lie close-up (1.6×), flag (1×) | tag "Habitat · Fairway · Lie: cantik ✅", tracked ring + "SASARAN 🚩" chip |
| 5.93–7.73 | walk-in 1.4× | specimen tag "Coach · *Coachus golfus* · tahap: pro 🏅" (right column, clear of the face) |
| 7.73–9.93 | setup fast-forwarded 7× (15.4 s → 2.2 s) | "Pemerhatian: Setup… lama sikit 😅", stopwatch 00:00 → 00:16 (stops on the take-away) |
| 9.93–12.13 | the shot at 1× + the stare | flash/shake on impact, bird squeak, "…senyap. 🦗" + crickets |
| 12.13–13.33 | replay 0.5×, tight on the turf | "Bukti: Tanah 🌱 terbang dulu" + arrow to the chunk |
| 13.33–14.97 | walks to the phone laughing | "Part of the *game.*" (right column) |
| 14.97–18.37 | freeze on the laugh | shutter flash, entry card "duff (n.) bila tanah kena dulu, baru bola · Status: biasa je · Coach pun? kena jugak 😂", CTA "Korang last duff bila? 👇" |

## Rules applied
- Safe band x 60–930, y 168–1330. Faces checked in snapshots: hook framed below the face (1.5× on hands/club/ball); address face x 220–340 / y 380–520,
  tags in the right column; laugh/end face x 20–540 / y 0–600 → the full data bar and mode pill leave at the laugh, a compact REC/clock pill sits at x 600–930.
- Repeats / awkward pauses cut: empty fairway before the walk-in, the 16 s of waggles (fast-forwarded so the joke lands), the walk-off where the shirt fills the frame.
- **No music** (owner: "No background music"). Birds and crickets are ambience SFX, not music. The take's own strike is lifted and kept.
- Claims kept to what the frames show: the turf flies on impact; the ball's landing is not visible, so it is not described.

## Build
```
tools/fetch.sh                          # sources -> .src/, 16 kHz wav -> work/
python3 tools/build_aroll.py            # EDL -> assets/aroll.mp4, assets/voice.wav, edit/timeline.json
python3 tools/build_index.py            # index.html (graphics + SFX)
npx hyperframes@0.9.32 check
npx hyperframes@0.9.32 render -q draft -o renders/preview_draft.mp4
tools/master.sh renders/preview_draft.mp4 previews/coach-duff_preview_v1.mp4      # preview, -14 LUFS
# when the owner says "render":
npx hyperframes@0.9.32 render -q delivery -o renders/final_raw.mp4
tools/master.sh renders/final_raw.mp4 final/coach-duff_1080x1920.mp4
```

## Delivery
Owner approved preview v1 unchanged ("ok render", 2026-11-13). `final/coach-duff_1080x1920.mp4`: 18.4 s, 1080×1920, 30 fps, H.264 High ~13.6 Mbps,
AAC 256k 48 kHz, −14.2 LUFS, −1.3 dBTP. `tools/master.sh` now does static gain + an oversampled limiter (the old two-pass loudnorm
left this mix at −0.3 / +1.0 dBTP because the strike transients are short and loud).
