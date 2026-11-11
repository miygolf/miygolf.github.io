# First time main golf — Reel edit

Vertical 1080×1920, 14.4s, H.264/AAC, loudness normalised to −14 LUFS (fits IG Reels / TikTok / Shorts).

**Output:** `first-time-golf-reel.mp4`

## Edit breakdown
| Time | Beat |
|---|---|
| 0.0–2.8s | Hook: "FIRST TIME MAIN GOLF ⛳" + "hari pertama. zero experience." with a slow push-in |
| 2.8–5.8s | Swing #1, slow-mo (frame-interpolated) zoom to the ball, flash + shake on contact → "CONTACT!" → "eh, boleh tahan 👀" |
| 5.8–7.7s | Whip-flash to Swing #2, waggle sped up 2× |
| 7.7–9.5s | The long pause at the top becomes the joke: "loading swing..." progress bar crawling to 99% "(masih loading)", with speeding-up ticks |
| 9.5–10.8s | Bar hits 100% → slow-mo downswing → "SENT IT! 🚀" |
| 10.8–11.7s | "DAY 1: DONE ✅" |
| 11.7–14.4s | End card: "Everyone starts at Day 1." + "Giliran korang pula? ⛳" |

Audio is the original ambience plus the real club contact sounds re-timed onto the slow-mo impacts, with synthesized whooshes, bass hits, pop blips and loading ticks. No music, so a trending sound can be added in-app.

## Rebuild
Put the source clip at `first-time-golf/src/in.mov`, then from `first-time-golf/scripts/`:
```
python3 base.py      # speed ramps + slow-mo interpolation -> base.mp4
python3 compose.py   # text, zooms, flashes, loading bar -> video_only.mp4
python3 audio.py     # sound design -> audio.wav
ffmpeg -i video_only.mp4 -i audio.wav -map 0:v -map 1:a -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -shortest final.mp4
```
