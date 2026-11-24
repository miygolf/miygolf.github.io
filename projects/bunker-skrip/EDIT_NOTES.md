# Edit notes — Bunker shot, owner's script (±40 s)

Owner sent the script (6 shots) + Drive folder 1V5O7fsTQ3tDUyWBKtVEx_orZs4-I7WqR (24 Nov 2026): IMG_0413/0414/0415 (swing + pan to the green,
no sound), IMG_0417 (2:15, the lesson: talk, set-up, line drill), IMG_0418 (talking head: penalty + CTA), IMG_0419 (club face close-up, a shot
followed to the green), demo_top_n_skull (ball stays in / skull), egg_fry (for the next video, not used). `tools/fetch.sh` -> `.src/` (not committed).

## Cut (41.1 s, `tools/build_aroll.py`)
| film | script shot | source | on screen |
|---|---|---|---|
| 0.0–2.6 | 1 | demo 7.45–10.10: ball stays in, "Alamak." | BOLA TAK KELUAR / BUNKER? (frame 0) |
| 2.6–5.1 | 1 | demo 31.7–34.2 skull + voice IMG_0417 "Ataupun, top, skull." | TOP · SKULL ✗ |
| 5.1–8.2 | 2 | IMG_0417 47.04–50.15 "Rahsia dia, korang jangan pukul bola, korang pukul pasir." | RAHSIA DIA / JANGAN PUKUL BOLA ✗ / PUKUL PASIR ✓ |
| 8.2–12.2 | 3 | IMG_0419 club face close-up + voice IMG_0417 "grip ke logo, cut sikit, so bagi dia open." | 01 BUKA FACE, BARU GRIP / FACE OPEN ✓ |
| 12.2–13.7 | 3 | IMG_0417 "korang kangkang besar-besar." | 02 KAKI LEBAR / BENAM DALAM PASIR |
| 13.7–16.9 | 3 | IMG_0417 "Weight belah kiri, and then blast." | 03 BOLA DEPAN · BERAT KIRI / BLAST! |
| 16.9–24.1 | 4 | IMG_0417 line drill: "korang buat satu line", "tak payah pukul bola dulu", "contoh macam ni" + swing on the line, "pukul line tu", "letak depan line" | DRILL: LUKIS 1 LINE / TANPA BOLA DULU / TARGET = LINE / BUKAN BOLA ✗ / BOLA DEPAN LINE SIKIT |
| 24.1–28.0 | 5 | IMG_0413 shot at 1x (owner v2: "klip 0:25 ganti dengan" IMG_0413), the phone follows the ball to the green; the clip has no sound, so IMG_0419's real strike sits on the impact | SWING PENUH / JANGAN SLOW DOWN |
| 28.0–31.2 | 5 | IMG_0413 impact at 0.5x (every 60 fps frame) + the pan to the green; IMG_0419's strike placed on the impact | PASIR YANG BAWA / BOLA KELUAR |
| 31.2–36.3 | 6 | IMG_0418 "one more thing dalam pasir, korang jangan sentuh… club tu jangan sentuh pasir" | ONE MORE THING / CLUB JANGAN SENTUH PASIR / PENALTY 2 PUKULAN |
| 36.3–41.1 | 6 | IMG_0418 "komen bunker kalau korang nak bola plug." + 1.6 s hold | KOMEN "BUNKER" 👇 / NEXT: BOLA PLUG 🍳 |

- Script lines with no matching recording ("Swing penuh. Jangan slow down.", "Pasir yang bawa bola keluar.", "Bola depan… berat kaki kiri",
  "Penalty two strokes") are on screen as tapes, in the script's words.
- Cut before "sebab ni consider penalty area": a bunker is not a penalty area under the Rules; the penalty for grounding the club in a
  bunker is the general penalty (2 strokes), shown as in the owner's script.
- Word times: full-pass whisper ran 0.3–0.5 s early on these recordings, so every cut was re-measured on the audio energy and re-transcribed
  as a crop; on-film word anchors come from crop runs on the film's own audio (`tools/film_words.py`). Each phrase checked: no word clipped.
- Faces: IMG_0418 sits low in frame (face y 900–1330), so the penalty / CTA tapes and captions go above it (y 230–760);
  everything else is below the face. All inside x 60–930, y 168–1330.

## Look: "Label Maker"
Embossed label-maker tape: each tip prints letter by letter (stepped reveal), settles with a small tilt and a hard shadow, and peels off when
the next section starts. Black = the steps (numbered 01–03), yellow = the key cue, red = the mistake / the penalty, white = the detail.
Oswald 600 uppercase (tape) + Gabarito 700 (spoken captions, dark pill) + Noto Color Emoji.

## Sound
Real sound only (house rule: no music in the final) + Mixkit SFX: a soft tap per printed tape (2568), a pop on the red mistakes and the
penalty (2364), an air woosh under the slow-motion blast (1489). Master: −14 LUFS, ≤ −1 dBTP, 1080×1920, 30 fps.

## Build
```
tools/fetch.sh && python3 tools/build_aroll.py && python3 tools/film_words.py && python3 tools/build_index.py
npx hyperframes@0.9.32 check && npx hyperframes@0.9.32 render -q draft -o renders/draft.mp4 && tools/master.sh renders/draft.mp4 previews/bunker-skrip_preview_vN.mp4
# on "render": render -q delivery -o renders/final_raw.mp4 && tools/master.sh renders/final_raw.mp4 final/bunker-skrip_1080x1920.mp4
```
