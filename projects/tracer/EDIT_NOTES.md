# Draw elak dahan — 154 ke pin, with shot tracer — edit notes

HyperFrames 0.9.32 · 1080×1920 · 30 fps · 32.0 s · status: **draft preview v1** (`previews/tracer-draw_preview_draft_v1.mp4`, 720p for review),
waiting for the owner's OK ("render") before the delivery render.

Request (2026-11-12): add a shot tracer; HyperFrames; transcribe first; motion graphics and SFX where they belong; premium SFX; never over the face;
TikTok/IG safe zone; voice must stay on top; cut repeats and awkward pauses; strongest hook; preview before render; a design not used before.
No music asked for → SFX only (house rule).

## Look: "Glass Tracer" (new, not in the style log)
- Clean broadcast look built around the tracer: frosted-glass cards (backdrop blur + saturate, bright 1.5 px edge, inner highlight) that
  materialise from a blur, with a specular sheen sweeping across once they land; a full-height glass sweep as the transition.
- The plan is drawn into the scene while he explains it (static tripod shot of the hole): straight line to the pin with an X at the branch,
  rings on the branch, the draw curving out toward the bunker and back to the pin, aim rings on the bunker, a pin flag.
- The flight: glowing comet tracer (coral → gold gradient, white core, blurred glow, bright head) over a faint ghost of the planned curve,
  push-in to 1.6× during the flight on a stage that scales video and drawings together, ground ripple on landing, "OVER SIKIT" card with a leader.
- Type: Manrope 800/700 + Fragment Mono. Palette: glass white rgba(255,255,255,.64), ink navy #0b1736, coral #ff5a36, gold #ffc93a, ice #c9f3ff.
- No colour grade.

## Transcript (faster-whisper large-v3; `edit/transcript*.txt`; word times re-run on the assembled voice track)
- 0.25–1.30 "154" (reading the distance) · 4.0–5.65 "Ok, disebabkan" · 6.45–8.85 "ke pin kita ada branch kat depan tu." · 9.3–11.25 "Ada sikit je pokok kat depan tu." ·
  12.85–14.6 "So, saya akan buat" · 1.6 s pause (cut) · 16.2–17.3 "draw sikit" · 18.15–19.4 "supaya elak." · 19.85–21.35 "Kita aim kat bunker." · 22.05–23.4 "Bagi dia curve masuk."
  (all said quietly off-frame left while the camera shows the hole)
- 24.5 walks in, 25–38.8 settles and waggles (cut) · takeaway 38.9 · **impact 39.80** · 45.74–49.32 "Oh, what a good shot." (very quiet, lifted +4 dB) · 50.8–52.2 "Tapi over sikit."
- "154" has no unit in the audio: shown as "154 · ke pin" with no m/yd.

## The tracer — what is measured and what is estimated
- **Measured**: ball at address (385,1359) on the film; impact 39.80 (sound transient 39.82, frames agree); the ball's position frame by frame for the first
  0.4 s by differencing the 4K frames (`tools/track_ball.py`; camera on a tripod): it climbs to (522,838) while drifting right (the "start right" of the draw).
- **Estimated**: after 0.4 s the ball is a few pixels wide in front of the tree line and can't be followed (`tools/track_sky.py` found nothing above it).
  The rest is a smooth continuation: the measured climb rate decays like 1/(t+0.076)² (fit on the tracked points), giving ~70–100 px more climb, apex
  ≈ y 772 near 1.8 s, then curving left and down to a landing just past the pin at 5.6 s (he says "Oh, what a good shot" 6 s after impact, "tapi over sikit").
- **Pin and bunker positions are estimates** from the far green (pale sand face on the mound = bunker; pin placed left of it, behind the branch line).
  If the owner knows where the pin / landing really were, move `PIN`, `BUNKER`, `LAND` in `tools/build_index.py`.

## Cut
| film (s) | source | what |
| --- | --- | --- |
| 0.00–2.00 | 38.55–40.55 | HOOK: swing into impact, tracer leaves the club; glass title "154 · ke pin · Draw elak dahan 🌳" on frame 0; "154" over it |
| 2.00–14.93 | 4.0–23.4 in 8 pieces | the plan, pauses cut (static picture, joins don't show): chips 1 Dahan depan pin / 2 Draw sikit / 3 Aim kat bunker / 4 Curve masuk, drawings in the scene |
| 14.93–22.13 | 38.30–45.50 | glass sweep → address, swing, the whole flight at 1× with the tracer, push-in to 1.6×, landing ripple 22.03 |
| 22.13–26.03 | 45.50–49.40 | "Oh, what a good shot." while he watches (he is out of frame in the push-in) |
| 26.03–32.03 | freeze 49.40 | "Tapi over sikit." + OVER SIKIT card, then the end card (plan recap) + "Save, try kat range 📌" |

## Face / safe zone
All text inside x 60–930, y 168–1330. The owner's face is only visible at the left (x < 260, y ≈ 850–960) while he addresses / watches, and it is out of frame
in the 1.6× push-in that covers the reaction and the end freeze (when he turns toward the camera). Cards sit in the sky (top band and the right column).

## Sound
- `assets/voice.wav` (`tools/build_aroll.py`): sync sound of each piece, "154" over the hook, denoise + presence EQ + compression (he talks quietly off-frame),
  loudnorm −16 LUFS; "Oh, what a good shot" lifted +4 dB. **No music.**
- 27 SFX cues (Mixkit, `assets/sfx/CREDITS.md`), each tied to something on screen; chip / pin / sweep sounds moved off the spoken words.
- Preview checked by re-transcribing its mix: every line is heard; "Bagi dia curve masuk" is the quietest (whisper hears "curve masuk" in the English pass).
- Delivery (when approved): `render -q delivery`, then `tools/master.sh` (−14 LUFS / −1.5 dBTP, H.264 CRF 17 ≤ 16 Mbps).

## Rebuild
```
tools/fetch.sh                  # source -> .src/, 16 kHz audio -> work/
python3 tools/transcribe.py     # edit/transcript.json (+ en)
python3 tools/track_ball.py 39.78 1.2 900 300 2160 2000     # launch points (printed; copied into build_index.py)
python3 tools/build_aroll.py    # assets/aroll.mp4, assets/voice.wav, edit/timeline.json
python3 tools/build_index.py    # index.html
npx hyperframes@0.9.32 render -q draft -o renders/preview_draft.mp4
npx hyperframes@0.9.32 render -q delivery -o renders/final_raw.mp4
tools/master.sh renders/final_raw.mp4 final/tracer-draw_1080x1920.mp4
```
