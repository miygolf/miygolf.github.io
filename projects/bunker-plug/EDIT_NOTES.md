# Edit notes — Bola plug / fried egg (follow-up to the bunker video)

Owner: "yang tulis egg fry tu, kau ambil footage tu, kau blend in dengan apa yang ada sekarang tu. Let's say kalau orang komen bunker, aku nak
upload video tu." Source: `egg_fry` from the same Drive folder (1V5O7fsTQ3tDUyWBKtVEx_orZs4-I7WqR) + the closing question of the bunker video
(IMG_0418). `tools/fetch.sh` -> `.src/` (not committed). Same "Label Maker" look as `projects/bunker-skrip` so the two read as one series.

## Cut (26.4 s, `tools/build_aroll.py`)
| film | source | words / picture | tapes |
|---|---|---|---|
| 0.0–1.3 | IMG_0418 17.05–18.30 | "Macam mana nak pukul bola plug?" (the bunker video's last line) | KORANG KOMEN "BUNKER" / BOLA PLUG? 🍳 (frame 0) |
| 1.3–3.1 | egg_fry 4.6–6.4 | the plugged ball, close | BOLA PLUG = FRIED EGG |
| 3.1–5.4 | egg_fry 9.8–12.9 | "Ini normal. Kalau korang buat macam ni, bola tak keluar." | FACE TERBUKA (NORMAL) / BOLA TAK KELUAR ✗ |
| 5.4–9.1 | egg_fry 13.76–17.4 | "Contoh," open-face strike (15.09), "so bola kat situ je." | CONTOH: FACE TERBUKA / BOLA KAT SITU JE ✗ |
| 9.1–14.4 | egg_fry 20.7–32.6 | "Tip dia. Instead of club face terbuka, korang tutupkan dia macam ni, biar je macam ni, ni pukul." | TIP DIA / FACE TERBUKA ✗ / TUTUP FACE CLUB ✓ / BIAR JE MACAM NI / THEN PUKUL |
| 14.4–16.9 | egg_fry 32.6–35.0 | closed-face strike (34.05), the ball comes out | BOLA KELUAR ✓ |
| 16.9–18.6 | egg_fry 33.7–34.55 at 0.5x | replay, real strike on the impact | REPLAY: FACE TERTUTUP |
| 18.6–23.4 | egg_fry 35.0–39.8 | the phone pans to the green | ATAS GREEN ✓ |
| 23.4–26.4 | egg_fry 40.9–42.7 + hold | "Okey, itu dia. Siap." | SAVE. CUBA KAT BUNKER ↓ / FACE TERBUKA ✗ · TUTUP ✓ |

- Every tape is the coach's own words (or the owner's "fried egg"); no technique claim beyond "tutup face, biar, pukul".
- Pauses inside the speech tightened by cutting between phrases (9.8–10.6 / 11.4–12.9, 25.5–27.1 / 28.4–29.7); every phrase re-transcribed: complete.
- Faces: the opening talking head (face low) and the ending (face close) get tapes/captions at the top (y 230–700); the ATAS GREEN tape ends at
  the cut so it never sits on his face. Not used: egg_fry 0–8.5 (behind the scenes).

## Sound
Real sound only + Mixkit 2568 / 2364 / 1489 (tape prints, red tapes, slow-mo whoosh). No music. Master −14 LUFS, ≤ −1 dBTP.

## Build
```
tools/fetch.sh && python3 tools/build_aroll.py && python3 tools/film_words.py && python3 tools/build_index.py
npx hyperframes@0.9.32 check && npx hyperframes@0.9.32 render -q draft -o renders/draft.mp4 && tools/master.sh renders/draft.mp4 previews/bunker-plug_preview_vN.mp4
# on "render": render -q delivery -o renders/final_raw.mp4 && tools/master.sh renders/final_raw.mp4 final/bunker-plug_1080x1920.mp4
```

## v2 (owner: "save cuba dekat range tu kau ubah kepada save cuba dekat bunker")
End tape now SAVE. CUBA KAT BUNKER ↓ (captions updated too).

## Delivery
Owner: "kau render terus je lepas kau tukar benda tu" (2026-11-24) on v2. `final/bunker-plug_1080x1920.mp4`: 26.5 s, 1080×1920, 30 fps, H.264, AAC 256k, no music.

## v3 (owner: "align wording a bit higher so viewer can see the club")
All tapes now start at y 200 and the captions sit at y 640, so the club head and the ball (y ~1000-1250 in the sand close-ups) are never covered.
Re-rendered on v3 (owner: "render", 2026-11-27): `final/bunker-plug_1080x1920.mp4` replaced.
