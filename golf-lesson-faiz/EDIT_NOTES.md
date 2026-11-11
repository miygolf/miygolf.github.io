# Edit notes — Golf lesson bersama Faiz

Sources: clip C = `1794276442263.mov` (10 s, result after 60 min); clip A = `1794274026226.mov` (61 s), clip B = `1794273769635.mov` (5 min 18 s). Both 1080×1920, 30 fps.

Transcribed with faster-whisper large-v3 (Malay) on denoised audio, cross-checked with a second model. Lines that the two passes did not agree on are kept as picture only (no caption).

## Cut list (a-roll `assets/video/main.mp4`, 48.0 s + 2.8 s end-card freeze = 50.8 s)

| # | At | Len | Source | In → Out | Freeze (pause at impact) | Content |
|---|---|---|---|---|---|---|
| 0 | 0.00 | 2.33 | B | 309.10 → 310.80 | 0.6 s at 0.73 (src 309.817) | hook swing |
| 1 | 2.33 | 1.67 | B | 17.55 → 19.20 |  | Itulah yang orang panggil |
| 2 | 4.00 | 1.17 | B | 20.25 → 21.40 |  | pusing tak habis |
| 3 | 5.17 | 0.90 | B | 25.05 → 25.94 |  | Badan tak pusing |
| 4 | 6.07 | 4.47 | B | 111.60 → 115.45 | 0.6 s at 8.40 (src 113.933) | swing asal + Tengok tangan tu |
| 5 | 10.53 | 2.57 | B | 291.45 → 294.00 |  | Kita nak hit down, kita kena shift |
| 6 | 13.10 | 1.87 | B | 297.20 → 299.05 |  | Atau orang kata sway ke kiri |
| 7 | 14.97 | 3.10 | B | 5.20 → 8.30 |  | coach guides swing |
| 8 | 18.07 | 3.00 | B | 124.60 → 127.60 |  | hands-on |
| 9 | 21.07 | 3.50 | B | 278.55 → 282.05 |  | Aku rasa macam tangan ni... Ha, bagus |
| 10 | 24.57 | 1.90 | A | 0.00 → 1.90 |  | Cuba buat balik. Same feel |
| 11 | 26.47 | 1.70 | A | 5.75 → 7.45 |  | Sebab Faiz kena faham |
| 12 | 28.17 | 3.13 | A | 16.00 → 18.50 | 0.6 s at 29.20 (src 17.033) | swing 1 |
| 13 | 31.30 | 1.07 | A | 23.15 → 24.20 |  | Cuba buat lagi |
| 14 | 32.37 | 3.50 | A | 28.85 → 32.35 |  | Kalau Faiz terpaksa rasa sway ke kiri |
| 15 | 35.87 | 1.03 | A | 36.75 → 37.78 |  | Betul |
| 16 | 36.90 | 2.97 | A | 49.75 → 52.10 | 0.6 s at 38.33 (src 51.183) | swing 2 |
| 17 | 39.87 | 2.40 | A | 55.35 → 57.75 |  | So kita rasa lama kat bawah |
| 18 | 42.27 | 5.73 | C | 4.20 → 9.30 | 0.6 s at 44.00 (src 5.933) | RESULT 60 min later |

v4: chapter 04 RESULT (clip C, 60 min later) before the recap: "60 MIN KEMUDIAN" title, riser into an impact freeze, RESULT stamp over the held finish.

v3: 0.6 s freeze-frame at each impact (hook, swing asal, swing 01, swing 02) with an IMPACT ring on the clubhead/ball, a bass hit and a music dip. Hands-on clips and the end card were shortened to keep 45 s. Timings now come from measured frame counts per piece.

v2 (45 s) added: original swing + "Tengok tangan tu", the first hands-on (coach guiding the swing), Faiz's own feedback "Aku rasa macam tangan ni… / Ha, bagus", and "Cuba buat lagi". The word after "tangan ni" differed between transcription passes, so the caption ends with an ellipsis.

Removed: repeated lines (e.g. second "badan tak pusing"), long practice-swing silences, unclear chatter, and awkward pauses between words.

Voice chain (ffmpeg): highpass 90 Hz → afftdn → compressor 3:1 → loudnorm -16 LUFS. Final mix measured at -16 LUFS integrated; music sits ~12 dB under speech (ducked via `data-automation`).
