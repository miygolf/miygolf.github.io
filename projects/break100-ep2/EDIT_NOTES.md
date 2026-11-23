# Edit notes — MIY GOLF Ep2 · Break 100 (split into 2 parts)

Owner: "pecahkan kepada part 1 dan part 2 untuk episod 2 ni". Source: silent slide video `.src/ep2.mp4` (53 s, storyboard: wording, numbers,
diagrams) + separate voice-over `.src/vo.wav` (89 s). Neither is committed.

## Voice (tools/build_voice.py)
- Transcribed with faster-whisper large-v3 (Malay, domain prompt) + crop re-runs at every boundary (`edit/vo_words.json`, `edit/transcript.txt`).
- Every cut measured on the audio, same rules as Ep1 (endings heard in full, fades only over silence, only pauses > 0.55 s shortened).
  This recording's room noise sits at about −46 dBFS, so silence is < −43 dBFS and an onset > −36 dBFS; soft words (the swallowed "kau" before
  "terlepas") count as an onset from −41 dBFS.
- "Break 100." runs straight into "Kau pernah" with no pause: tails are capped at the next phrase's start so no cut carries the next word.
- Removed: room noise / breath before "Episod" (0–2.6 s) and the stray "Ok. Ok." (75.6–76.7 s) between the stat and the CTA.
- Order per part (part.json, tools/make_parts.py):
  - **Part 1/2 (46.0 s)**: "Kau pernah tak masuk bunker 3 kali baru keluar?" → "Episod 2, Break 100." → "Episod ni untuk kau. 30 minit, 3 drill."
    → Drill 1 garisan dalam pasir → CTA "Pergi practice area minggu ni, … dari 10, berapa kau keluar dari bunker sekali pukulan je." → "Like untuk part 2 👍".
  - **Part 2/2 (45.4 s)**: opens on "Fokus tempat mendarat, bukan lubang." → Drill 2 chip ke tuala → Drill 3 bulatan 1 meter → putt stat
    (3–6 kaki: 60% handicap tengah–tinggi vs 76% scratch, source MyGolfSpy as on the owner's slide) → "Pergi practice area minggu ni." + 3-drill recap card.
- Check: each part's voice and final mix re-transcribed (large-v3): every phrase complete, no "Ok", no word leaking across a cut.

## Look: "Range Map" (same as Ep1, owner: "ikut tema episod 1 yang paling awal tu … aku suka warna cream yellowish punya background")
v1 preview used a new "Blueprint" look; v2 switches to Ep1's cream-paper Range Map (Hanken Grotesk + Geist Mono, fairway green, red pen, green page sweep with the yardage stake, ink caption strip).
v1 notes:
Cyanotype drafting sheet: white line-work drawn on, dimension lines with end ticks (5 cm · 1 inci, 1 M), drafting title block for the episode
(+ red-pencil "UNTUK KAU" stamp), Architects Daughter hand-lettered notes written on left→right, a parallel rule slides down between drills.
Archivo 800/900 (wdth 112–125) + JetBrains Mono 700 + Architects Daughter. Blueprint #123f7d / #0a2a59, line #eaf2ff, pencil yellow #ffd84a, red pencil #ff7a66.
Diagrams follow the owner's slides (bunker line + ball 5 cm ahead, target 8/10; towel on the green, 10 chips; 6 balls on a 1 m ring, reset on a miss).
Tallies (8/10, 6/10) are examples, as on the slides.

## Sound
Mixkit "Digital Clouds" continuous bed (same as Ep1, the owner's choice of "presentation" music), voice on top; Mixkit SFX each tied to an on-screen cause
(`assets/sfx/CREDITS.md`). Mastered with tools/master.sh: −14 LUFS, ≤ −1 dBTP, 1080×1920, 30 fps.

## Build
```
python3 tools/make_parts.py
cd parts/pN && python3 tools/build_voice.py && python3 tools/build_music.py <total = total_voice + 2.4> && python3 tools/build_index.py
npx hyperframes@0.9.32 check && npx hyperframes@0.9.32 render -q draft -o renders/draft.mp4 && ../../tools/master.sh renders/draft.mp4 ../../previews/break100-ep2_partN_preview_v1.mp4
# on "render": render -q delivery -o renders/final_raw.mp4 && ../../tools/master.sh renders/final_raw.mp4 ../../final/break100-ep2_partN_1080x1920.mp4
```
