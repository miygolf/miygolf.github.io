# Kelas Bunker 101 (raw) — edit notes

Same clip as `projects/bunker-nyaris/` (IMG_0193). Owner brief: educational style with a little humour, relaxed, **less SFX, raw**, let the green be heard.

**Look: "Kelas Bunker 101"** — chalk on raw footage: small slate boards with a thin wood rim, notes chalked on (write-on wipe in short steps),
a hand-drawn chalk circle round the cup, double chalk underline on STOCK SHOT, an eraser that wipes the hook board clean, HOMEWORK end board.
Cabin Sketch 700 + Kalam 400/700 + Noto Color Emoji. Slate #25312b, chalk #f3f0e6, chalk yellow #ffe07a, chalk pink #ff9fb8, rim wood #8b5e3c.
Hard cuts, every story segment at 1× with its own sound, five soft chalk SFX, no music. Wide framing (hook 1.25–1.34×, everything else full frame).

## Transcript
large-v3 full passes (ms, en) + the crops from bunker-nyaris (`edit/transcript.txt`). Newly captioned vs the neon cut:
"Favourite bunker nampaknya… hari ni?" (the name after it is unclear — not captioned) and "Saya boleh tunjuk banyak sikit educational video."
A small laugh behind the phone after "Bunker sahaja" is kept as sound.

## The green ("check")
The landing itself happens inside the camera whip (blurred). What you see and hear raw: the ball rolling in, slowing as it passes right by the cup
(chalk circle, tracked on the flag + pole offset because the handheld camera drifts), "What a player!" from behind the phone, the green's own quiet.

## Structure (22.7 s)
| film | segment | on screen |
| --- | --- | --- |
| 0.00–2.53 | hook: ball at the cup 0.5×, freeze | board "Kelas hari ni: BUNKER 101 / stock shot · ±20 ft" (frame 0), chalk circle + "nyaris!! 😱", eraser wipes the board |
| 2.53–6.47 | "Favourite bunker nampaknya… hari ni?" "Bunker sahaja." | captions, note "bunker je? ok… 😅" |
| 6.47–9.63 | "Saya boleh tunjuk banyak sikit educational video." | note "KELAS BERMULA 📚" |
| 9.63–13.30 | "Almost similar, about 20 feet. Kita main stock shot." | board "jarak: ±20 ft / STOCK SHOT" + double underline |
| 13.30–15.17 | address + swing, raw | — |
| 15.17–16.57 | camera whips to the green, raw 1× | — |
| 16.57–19.27 | the roll past the cup, "What a player!" | chalk circle on the cup, caption in the sky |
| 19.27–22.67 | freeze | HOMEWORK board, "Korang pernah nyaris hole-out? 👇" |

Preview mix re-transcribed (medium): every captioned line heard.

## Build
```
tools/fetch.sh
python3 tools/build_aroll.py && python3 tools/build_index.py      # flag track for the cup circle: edit/flag_roll.json
npx hyperframes@0.9.32 check
npx hyperframes@0.9.32 render -q draft -o renders/preview_draft.mp4 && tools/master.sh renders/preview_draft.mp4 previews/bunker-raw_preview_v1.mp4
# on "render":
npx hyperframes@0.9.32 render -q delivery -o renders/final_raw.mp4 && tools/master.sh renders/final_raw.mp4 final/bunker-raw_1080x1920.mp4
```

## v2 (owner: "Stock shot. Macam ada sound yg sangkut tu delete")
- Every "stop shot" → **"stock shot"** (caption, hook board, plan board, homework board, CAPTION.md).
- Removed the green-ambience bed under the hook and the end freeze: it was one 0.9 s piece repeated every ~0.85 s (heard as a stuck sound).
  Those two stretches now carry only the chalk SFX. `previews/bunker-raw_preview_v2.mp4`, −14.0 LUFS, −2.9 dBTP.
