# Edit notes — Early extension, owner's script (±40 s)

Owner sent the script (6 shots) + Drive folder 1kSC55PwCnVJP7e4ofjFRbHKVqOg0FGT5 (25 Nov 2026): one clip, IMG_0448 (3:04, face-on from the toe
side, driving range, noise-gated lapel audio). `tools/fetch.sh` -> `.src/` (not committed).

## Script vs footage
- No talking-head takes of shots 2 and 6, and no wall: those script lines are on screen as chart rows, in the script's words.
- The drill on camera is the chair behind the hips (same feel as the wall): rows say "kerusi", and "Kerusi / golf bag / dinding" covers the wall.
- Angle is face-on, not from behind; the fault shows clearly from here (the hips move towards the ball).
- Not used: drill 1 detail (foot back, 60-88 s) except "Buat slow-slow, backswing slow je", and drill 3 (grip down, 148-175 s), kept for part 2.

## Cut (37.5 s, `tools/build_aroll.py`)
| film | script | source | on screen |
|---|---|---|---|
| 0.0-4.8 | 1 | swing 1 (the first, before any drill) at 1x, 0.5x into impact, freeze + "Apa itu early extension?" | PUNGGUNG LARI / MASA DOWNSWING? (frame 0); plumb line on the hips at address, red marker at impact, PUNGGUNG KE DEPAN / = EARLY EXTENSION |
| 4.8-12.1 | 1-2 | slow demo: "First of all, dia angkat backswing, dia naik badan. Lepas tu bila dia turun, dia turun je macam tu." | 01 SPACE TANGAN HILANG / 02 SHANK · BLOCK KANAN · THIN |
| 12.1-25.0 | 3 | chair drill: "Ambil golf bag ataupun kerusi." + "Kerusi ni sebagai kita nak dapatkan rasa je. Angkat backswing. Downswing tu bagi rasa, tolak je kerusi tu. Then follow through." | DRILL DIA SIMPLE JE / KERUSI · GOLF BAG · DINDING / 01 SETUP / 02 BACKSWING / 03 DOWNSWING |
| 25.0-28.1 | 4 | "Buat slow-slow, backswing slow je." | SLOW DULU · 10 KALI / RASA PUNGGUNG STAY KAT BELAKANG |
| 28.1-29.9 | 3 | full swing with the chair (real strike) | THAT'S IT ✓ |
| 29.9-34.0 | 5 | split: swing 1 (before) and the last swing (after), synced on impact, 0.5x, freeze | BEFORE / AFTER, plumb lines + markers, LARI KE DEPAN / STAY, NAMPAK BEZA DIA? |
| 34.0-37.5 | 6 | "Okey, itu dia." (walks up to the phone) + hold | TRY DULU SEBELUM WARM-UP / KOMEN "DRILL" 👇 / PART 2: ROTATION |

## Measurement (before/after)
Back of the hips = leftmost trouser pixel (rows y 970-1030, upright frame; the left frame edge is background, so not clipped):
swing 1 address x ~24 -> impact ~110 (≈85 px towards the ball); last swing address ~40 -> impact ~65 (≈25 px). Lines drawn at those x.
The "after" swing is the last one in the clip (after both drills, gripped down).

## Look: "Posture Chart"
A physio posture assessment: teal plumb line dropping with its bob on the hips at address, red dashed marker at impact, arrow measuring the gap;
points arrive as clinical chart rows (tab slides in, row wipes open); the before/after is a two-panel assessment sheet on ink.
Familjen Grotesk 700/600 + Reddit Mono 600 + Noto Color Emoji. Chart white #f5f8f7, ink #13202b, teal #0e8c8f, marker red #e2483d.

## Sound
Real sound + Mixkit 2568 / 2364 / 1489 (rows, red rows and impact markers, into slow motion); real strikes laid on the frozen impacts. No music.
Master −14 LUFS, ≤ −1 dBTP. Every phrase re-transcribed on the final mix: complete.

## Build
```
tools/fetch.sh && python3 tools/build_aroll.py && python3 tools/film_words.py && python3 tools/build_index.py
npx hyperframes@0.9.32 check && npx hyperframes@0.9.32 render -q draft -o renders/draft.mp4 && tools/master.sh renders/draft.mp4 previews/early-extension_preview_vN.mp4
# on "render": render -q delivery -o renders/final_raw.mp4 && tools/master.sh renders/final_raw.mp4 final/early-extension_1080x1920.mp4
```

## v2 (owner: "drill tu kau ambil footage yang last kali tu, yang aku choke down, yang aku pegang pendek tu")
The drill is now drill 3, gripped down (IMG_0448 155.5-176.3): "7 iron, tak kisahlah berapa iron pun, korang pegang pendek. Sebab kalau korang early
extension, korang akan miss the ball completely. So untuk kita dapatkan stay, stay bawah, pegang je pendek untuk rasakan ... buntut kita ni ke belakang."
(false start "but" cut), then the gripped-down swing at 1x. Rows: DRILL DIA SIMPLE JE / PEGANG PENDEK (CHOKE DOWN) / EARLY EXTENSION = MISS BOLA /
01 SETUP: PEGANG PENDEK / 02 STAY BAWAH / 03 RASA PUNGGUNG KE BELAKANG / SLOW DULU · 10 KALI / THAT'S IT ✓. Chair drill and "buat slow-slow" removed.
The split's "after" is this same swing. 36.2 s.
