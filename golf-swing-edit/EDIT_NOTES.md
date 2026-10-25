# Before → After swing edit (HyperFrames)

Source: `VID_20261025_150916.mp4` (clip 1, **before**) and `VID_20261025_154706.mp4` (clip 2, **after adjustment**), 4K 60 fps portrait.

## Transcript (faster-whisper medium, word timestamps)

| Clip | Time (s) | Speech | Used? |
| --- | --- | --- | --- |
| 2 | 2.38–4.36 | "Good. Good for two." (background, while standing at address) | Cut with the idle address |
| 2 | 11.62–12.08 | "Nice." (right after the after-swing) | Kept, captioned, boosted, music ducked |

Clip 1 has no speech.

## Cuts

| Out (s) | Source | Note |
| --- | --- | --- |
| 0.00–2.10 | clip 2, 10.25–10.95 @ 0.35× | Hook: after swing through impact, slow motion |
| 2.10–5.20 | clip 1, 0.85–3.35 | Before; 0.4× through impact; idle tail after finish removed |
| 5.20–10.07 | clip 2, 8.75–12.90 | After; ~8.7 s of standing at address removed; 0.4× through impact |
| 10.07–13.40 | finish frames of both | Split screen BEFORE / AFTER + comment prompt |

Impact frames: hook 1.15 s, before 4.20 s, after 7.45 s (the music drop and the bass hit land here).

## Sound

- Music: original track generated locally with MusicGen (medium), no licence needed; trimmed so its drop lands on the after impact.
- SFX: HyperFrames bundled library (Pixabay Content License, see `assets/sfx/CREDITS.md`).
- Range ambience kept from the footage; "Nice." boosted with a voice EQ.

Rebuild the footage segments: `../tools/build_segments.sh <clip1> <clip2> .`
Regenerate the before/after scenes: `python3 ../tools/gen_swing_scenes.py compositions`
