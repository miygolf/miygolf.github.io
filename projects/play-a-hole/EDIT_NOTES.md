# Play a hole with me (Tasik Nine, KRTU Subang) — edit notes

HyperFrames 0.9.18 · 1080×1920 · 30 fps · 42.1 s · status: **draft preview, waiting for "render"**

## Look: "Arcade Round" (new, not in the style log)
- The hole played like a retro golf game: pixel HUD (HOLE 1 · PAR 4, SHOT pips → BIRDIE −1), POWER meter that fills on each
  backswing and snaps full on contact, distance counter (117 m), pixel shot tracer, PAUSED / REWIND hook, BIRDIE! burst with pixel
  confetti and a −1 coin, "HOLE 1 CLEAR!" results screen.
- Type: Bungee (titles, captions) + Silkscreen 700 (HUD labels). Palette: violet #6a2cff, sun #ffd21f, ink #140b2e, white.
- Shapes: panels with stepped 8-bit corners (four single-axis ink shadows), bevel highlight; all motion on `steps()` eases.
- Transitions: pixel-block wipes (seeded random order) on every cut; 4K push-ins toward the cup baked into the A-roll.

## Story (transcribed with faster-whisper large-v3; Malay + English)
| film | source | what |
| --- | --- | --- |
| 0–3.6 | clip4 10.25–13.0 + freeze | HOOK: putt rolling, push-in to the cup, freeze an inch short — "MASUK KE TAK?" over Iqbal's own line "Ok, kita tengok boleh buat birdie tak?" (clip3) |
| 3.6–4.1 | clip4 reversed 6× | REWIND |
| 4.1–7.8 | clip1 8.9–12.6 | Tee shot, HOLE 1 card, power meter, TEE OFF! |
| 7.8–14.1 | clip2 19.7–25.0 (0.35× through contact) | Approach, "117" distance counter (117 m), slow-mo strike, pixel tracer, ON THE GREEN |
| 14.1–21.8 | clip3 7.0–14.7 + tightened voice | "Alright, tadi second shot 117 meter, so ada dalam 12 kaki kot, 10 kaki macam tu lah" (pauses cut) |
| 21.8–29.3 | clip4 8.6–15.1 (0.5× on the last roll) | Putt for birdie, target brackets, drop → BIRDIE!, "Dahsyatnya!" |
| 29.3–36.8 | clip4 17.4–24.9 | "Such a good player… any tips for green reading, Coach Iqbal?" / "Green reading." |
| 36.8–42.1 | freeze clip4 24.9 | Results + CTA "Nak tips green reading? Komen GREEN" |

Cut out: the flight partners' tee shots, chatter, long address/waggles, walking, the unclear green-reading answer at the end of clip4.

## Face / safe zone
All graphics inside x 60–930, y 168–1330. Per-shot face boxes checked in snapshots: tee (head ~x 220, y 860 → graphics right/top),
approach (head ~x 270, y 860, tracer stays right of it), putt (head top-left), end freeze (face x 300–560, y 480–860 → results panel starts y 950).

## Sound
- Voice track `assets/voice.wav` built by `tools/build_aroll.py`: denoise, compression, loudnorm −16 LUFS. Real strike sounds kept.
- Music: Mixkit "A Game" (#777), ducked to 0.085 under speech (≈ 17 dB below the voice), 0.32 elsewhere; its breakdown
  sits under the putt and the drop lands on the birdie.
- 22 Mixkit SFX ids, 34 cues, each tied to something on screen (list in `assets/sfx/CREDITS.md`).
- Draft mix measured: −17.3 LUFS integrated. Final: master to −14 LUFS / −1 dBTP (house rule).

## Rebuild
```
tools/fetch.sh                 # sources -> .src/
python3 tools/build_aroll.py   # A-roll + voice + edit/timeline.json
python3 tools/build_index.py   # index.html (graphics, captions, music, SFX)
npx hyperframes@0.9.18 check
npx hyperframes@0.9.18 render -q draft -o renders/preview_draft.mp4
```
