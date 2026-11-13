# Uneven lie: downhill — edit notes

**Look: "Spirit Level"** — the lesson told with a builder's level. Every card is a level-yellow tool body with aluminium end caps and a mint glass vial;
it slides in tilted (the slope) and levels out as its bubble glides to the centre lines (step numbers sit in the bubble). The LIE card tips back
off level on "menurun". Section changes are a tilted yellow band with hazard edges. Ground marks ride the tracked ball: stance bracket + centre line
(step 1), grip ring (2), low-point ring and two "?" markers on "sini ke, sini ke" (3), left-foot arrow and a ball-first ring (4).
Big Shoulders Display 900 + Figtree 800 + Red Hat Mono 600 + Noto Color Emoji. Level yellow #ffd400, ink #121212, vial mint #bff3cf, aluminium #a7afb6. No grade.

## Source
`clip1` (70.4 s, handheld, face-on). Transcript: faster-whisper medium full pass + **large-v3** full passes (ms, en) + large-v3 crops (`edit/transcript.txt`).
Captioned only where the passes agree. Left out:
- the opening line from behind the phone ("... downhill, uneven lie", first word unclear) and "dah lah ... kasi dekat bawah" (unclear);
- "Kiri satu hal, [draft / jauh / daft] satu hal" (second word unclear);
- **55.2–60.1 "… kanan sikit … kiri"**: large-v3 hears "tim/letak tim kanan sikit", medium "tekan kanan sikit"; the en pass "to the right".
  It may be "aim kanan sikit" — not used until the owner confirms the word.
- "So supaya kena bola **direct**": large-v3 x3 "direct", medium "darat": captioned as "direct".
Target is screen right (face-on, right-hander), so "ke kiri" is shown as a top-down diagram in the card, not as an on-screen arrow;
"kaki kiri" is the screen-right foot.

## Structure (38.3 s)
| film | segment | on screen |
| --- | --- | --- |
| 0.00–2.70 | hook: strike 0.5× into the finish, freeze | DOWNHILL level card on frame 0 (tilted → level), "4 STEP JE ↓" |
| 2.70–6.90 | the lie: "So lie dia ni menurun macam ni." / "Nak buat apa?" | LIE · MENURUN card (tips off level on "menurun") |
| 6.90–10.53 | tendency: "...this kind of lie, memang bola pergi kiri." | BOLA KE KIRI card + curve diagram |
| 10.53–15.37 | step 1: ball position tengah | stance bracket + centre line to the ball |
| 15.37–16.87 | step 2: pegang pendek | grip ring |
| 16.87–24.33 | step 3: practice swing, low point, "sini ke, sini ke" | low-point ring + two ? markers |
| 24.33–29.80 | step 4: weight belah kaki kiri, supaya kena bola direct | left-foot arrow, ball-first ring |
| 29.80–32.70 | the shot at 1× | band wipe in, flash + punch on impact |
| 32.70–34.70 | camera follows the ball 2× | — |
| 34.70–38.30 | fairway freeze | recap card 1–4 + "SAVE. TRY KAT RANGE 📌" |

Preview mix re-transcribed (medium): every captioned line is heard.

## Build
```
tools/fetch.sh
python3 tools/build_aroll.py      # then re-run the ball tracker (EDIT history: edit/ball_track.json) if the EDL changes
python3 tools/build_index.py
npx hyperframes@0.9.32 check
npx hyperframes@0.9.32 render -q draft -o renders/preview_draft.mp4 && tools/master.sh renders/preview_draft.mp4 previews/downhill-lie_preview_v1.mp4
# on "render":
npx hyperframes@0.9.32 render -q delivery -o renders/final_raw.mp4 && tools/master.sh renders/final_raw.mp4 final/downhill-lie_1080x1920.mp4
```
