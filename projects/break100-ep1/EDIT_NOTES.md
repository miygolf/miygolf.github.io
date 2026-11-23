# MIY GOLF Ep1 · Break 100 — edit notes

Owner uploads (23 Nov 2026): `MIY_GOLF_Ep1_Break100_9x16.mp4` (46 s, silent slide video: dark green, 3 drills) and
`Recorder_-_20261123-0941.wav` (69.9 s voice-over). No footage, no faces. The slides are the storyboard; the episode is rebuilt in HyperFrames
around the voice. 62 s.

## Voice (tools/build_voice.py)
large-v3 (ms, domain prompt) + crop re-runs → `edit/vo_words.json`. Cut list:
- **Hook first**: "30 minit je. 3 drill. Tak payah swing cantik." then "Episod 1, Break 100." (the recording opens with the episode line).
- Dropped the repeat "Kalau kau ada 30 minit je," — the line starts at "dekat range minggu ni, kau buat 3 benda ni."
- Silences > 0.30 s inside each piece collapsed to 0.14 s; 0.22 s between pieces. 69.9 s → 59.6 s of voice.
- Denoise + presence EQ + compression, −16 LUFS before the master. The voice is the only bed (no music).
Read as (whisper mis-hears): "tee off" ("T of 2", "take off"), "range" ("Davirin"), "lag" ("pak"), "putter length" ("pata length").

## Look: "Range Map"
A printed course-guide page: cream dotted paper, top-down diagrams that draw on like a plotter, red pen marks, a grass-green page sweep with a
white/red yardage stake between drills, ink caption strip. Hanken Grotesk 800/600 + Geist Mono 600. Paper #f3eee2, ink #141714, fairway #2f8a3e,
light fairway #a8d68f, rough #6fae5a, flag red #e8412c.

| film | voice | on screen |
| --- | --- | --- |
| 0–4.1 | "30 minit je. 3 drill. Tak payah swing cantik." | giant 30 / minit je (frame 0), 3 drill, red-pen strike through "swing cantik" |
| 4.1–6.4 | "Episod 1, Break 100." | BREAK 100 + score card: 100 struck, 99 circled |
| 6.4–9.1 | "Dekat range minggu ni, kau buat 3 benda ni." | three tiles 01 tee off · 02 punch · 03 lag putt, 30-minute bar fills |
| 9.1–25.9 | drill 1 | fairway map, two flags on the edges, 10 driver shots (5/10), hybrid 8/10 ("nombor contoh"), chips "Bawah 6? Cuba hybrid / 3 wood", "Lagi banyak masuk = kayu tee off kau" |
| 25.9–41.4 | drill 2 | tree: high shot crossed out, low punch drawn under the branches, 20–30 m; "Belakang pokok? Punch bawah."; "Hole jadi 8 😬" |
| 41.4–50.4 | drill 3 | green from above, 1-putter-length zone round the cup, putts from 6 · 9 · 12 m roll in to stop inside it; "Berhenti dekat. Bukan masuk." |
| 50.4–62.0 | CTA | "Driver kau dapat berapa dari 10?" + 10 empty dots, "Bagitahu aku 👇", WhatsApp line from the slide |
Preview re-transcribed (medium): every line heard. −14.0 LUFS, −2.9 dBTP.

## Build
```
python3 tools/build_voice.py && python3 tools/build_index.py
npx hyperframes@0.9.32 check
npx hyperframes@0.9.32 render -q draft -o renders/preview_draft.mp4 && tools/master.sh renders/preview_draft.mp4 previews/break100-ep1_preview_v1.mp4
# on "render":
npx hyperframes@0.9.32 render -q delivery -o renders/final_raw.mp4 && tools/master.sh renders/final_raw.mp4 final/break100-ep1_1080x1920.mp4
```
The owner's source video and recording stay in `.src/` (not committed).

## v2 (owner: "part awkward moment tu kau jangan potong yang hujung-hujung … bagi dengar jelas")
- Whisper's word times on this recording run 0.4–0.8 s EARLY ("3 drill" is really at 4.38 s, "Aku" at 42.18 s, "Pergi" at 59.62 s),
  so v1's cuts clipped phrase endings and its 12–100 ms fade-outs sat on the last syllable.
- Every cut is now measured on the audio: a phrase ends where the voice has decayed (60 ms under −48 dBFS) plus up to 0.15 s of tail,
  stopping before the next measured onset; it starts 0.04 s before the first sound (or snaps forward if the transcript start is in silence;
  if phrases run together, at the quietest 10 ms point). The fade-out only covers the silent tail. Phrases that run on are never split.
- Only pauses longer than 0.55 s are shortened (to 0.32 s, keeping 0.20 s after the last sound); 0.32 s between phrases, 0.55 s after the hook.
- Every animation / caption anchor is shifted by its phrase's measured onset offset, so graphics land on the words.
- Check: each phrase's last 1.6 s re-transcribed on its own (large-v3) — every final word complete. 61.9 s, −14.0 LUFS, −2.8 dBTP.

## Delivery
Owner approved v2 ("render", 2026-11-23). `final/break100-ep1_1080x1920.mp4`: 61.9 s, 1080×1920, 30 fps, H.264 High CRF 17 (flat graphics compress to ~0.5 Mbps), AAC 256k, −14.0 LUFS, −2.8 dBTP.

## v3 (owner: "Kau tambah background music slow je")
Mixkit "Sleepy Cat" (music id 135, lo-fi ~67 bpm) as `assets/music_bed.wav`: trimmed to the film, 1.5 s fade-in / 2.5 s fade-out, sidechain-ducked
by the voice (ratio 3, release 0.5 s). Measured: while speaking the voice sits **18.3 dB above** the music; in pauses the music rises to −30 dBFS.
Preview mix re-transcribed (medium): every line still heard. −14.0 LUFS, −2.8 dBTP. Build: `python3 tools/build_music.py <total>` after build_voice.py.
