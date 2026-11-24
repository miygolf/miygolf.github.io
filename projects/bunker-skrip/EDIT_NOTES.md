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
| 3 | IMG_0419 club face close-up + voice IMG_0417 "cut sikit, so bagi dia open." ("grip ke logo" removed, owner v3) | 01 BUKA FACE, BARU GRIP / FACE OPEN ✓ |
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

## v3 (owner: "part yang ukur depan line tu kau bagi nampak penuh, bagi ada shot kat situ. grip ke logo buang")
- "Grip ke logo" cut from the face section (voice now starts at "cut sikit").
- The ball set in front of the line is shown in full (IMG_0417 116.4–119.5), then a jump cut to the address and the shot from it (126.2–128.65, impact 127.87, his "Eh!"), with a PUKUL LINE ✓ tape on the impact.

## v4 (owner: "last part yang slow motion tu, yang full swing tu, kau bagi nampak bola tu land kat mana")
- The slow-motion shot now follows the phone's pan to the end of IMG_0413 (to 8.2 s) where it settles on the green, punches in 1.8x on the yellow flag,
  and draws a yellow ring round the balls beside it, with a MENDARAT ATAS GREEN ✓ tape. Other practice balls already lie on that green, so the ring marks
  the landing area by the flag rather than claiming one ball.
- IMG_0418 opens with the coach walking back from the phone (face high, 1.55-2.2 s): the penalty tapes and caption now start once he is seated (+0.65 s),
  the caption is two lines at y 586, and the green tape is never carried onto the talking head. 47.4 s.

## v5 (owner: "zoom in dekat bola land tu")
- The punch-in is now 4.5x on the two balls by the flag and follows them: `tools/track_balls.py` tracks them in IMG_0413 5.9-8.2 s (the handheld
  phone drifts ~100 px), `build_index.py` turns the track into scale/translate keys that keep them centred, so the ring stays on them.

## v6 (owner: "salah tu area kau zoom in tu, dia duduk belah kanan. Pin tengah belah kanan")
- The landed ball is the one right of the middle pin, at the right pin's base (IMG_0413 6.6 s: x 700 / y 978). Tracked (relative-brightness test, the ball is
  ~6 px), 3x punch-in that keeps it at (620, 1000) with both pins in frame, small ring on it.

## v7 (owner: "yang ending tu, komen bunker macam mana nak pukul bola plug. Kau highlight part tu")
- The CTA now runs through "Macam mana nak pukul bola plug?" (IMG_0418 17.12-18.20) before the hold. Highlight: MACAM MANA NAK PUKUL (black) +
  BOLA PLUG? 🍳 (big red) print on the question, the three CTA tapes pulse on it (pop) and again before the end, and stay to the last frame;
  the question has its own caption. 48.9 s.
