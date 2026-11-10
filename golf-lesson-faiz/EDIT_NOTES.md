# Edit notes — Golf lesson bersama Faiz

Sources: clip A = `1794274026226.mov` (61 s), clip B = `1794273769635.mov` (5 min 18 s). Both 1080×1920, 30 fps.

Transcribed with faster-whisper large-v3 (Malay) on denoised audio, cross-checked with a second model. Lines that the two passes did not agree on are kept as picture only (no caption).

## Cut list (a-roll `assets/video/main.mp4`, 29.28 s + 2.8 s end-card freeze = 32.08 s)

| # | At | Len | Source | In → Out | Content |
|---|---|---|---|---|---|
| 0 | 0.00 | 1.70 | B | 309.10 → 310.80 | hook swing |
| 1 | 1.70 | 1.65 | B | 17.55 → 19.20 | Itulah yang orang panggil |
| 2 | 3.35 | 1.15 | B | 20.25 → 21.40 | pusing tak habis |
| 3 | 4.50 | 0.89 | B | 25.05 → 25.94 | Badan tak pusing |
| 4 | 5.39 | 2.55 | B | 291.45 → 294.00 | Kita nak hit down, kita kena shift |
| 5 | 7.94 | 1.85 | B | 297.20 → 299.05 | Atau orang kata sway ke kiri |
| 6 | 9.79 | 3.50 | B | 124.50 → 128.00 | hands-on |
| 7 | 13.29 | 1.90 | A | 0.00 → 1.90 | Cuba buat balik. Same feel |
| 8 | 15.19 | 1.70 | A | 5.75 → 7.45 | Sebab Faiz kena faham |
| 9 | 16.89 | 2.70 | A | 16.00 → 18.70 | swing 1 |
| 10 | 19.59 | 3.50 | A | 28.85 → 32.35 | Kalau Faiz terpaksa rasa sway ke kiri |
| 11 | 23.09 | 1.03 | A | 36.75 → 37.78 | Betul |
| 12 | 24.12 | 2.60 | A | 49.70 → 52.30 | swing 2 |
| 13 | 26.72 | 2.40 | A | 55.35 → 57.75 | So kita rasa lama kat bawah |

Removed: repeated lines (e.g. second "badan tak pusing"), long practice-swing silences, unclear chatter, and awkward pauses between words.

Voice chain (ffmpeg): highpass 90 Hz → afftdn → compressor 3:1 → loudnorm -16 LUFS. Final mix measured at -16 LUFS integrated; music sits ~12 dB under speech (ducked via `data-automation`).
