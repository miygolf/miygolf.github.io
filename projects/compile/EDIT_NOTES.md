# 1 Round @ Templer Park — compilation edit notes

Owner: "Compile semua 90-120s" with the Drive folder 1kptuZSNf8-Zq_3cTnAplmOHGZtOv1p4J (16 clips). 93.4 s.

**Look: "Yardage Book"** — the round as pages of a yardage book: kraft-paper chapter tabs (number roundel, Young Serif title, mono sub-line,
real record time), a pencil "round tracker" line across the top with a tick per chapter and a red dot walking the round, kraft caption strips
with the key word underlined in pencil red, cover-style title and end cards. Young Serif + Sometype Mono + Noto Color Emoji.
Kraft #d8c49c, ink green #1f3a2b, pencil red #c2412d, chalk #fbf7ec. Flat fills only (HyperFrames warns past ~40 heavy-overlay elements).
Raw: hard cuts, each segment's own sound levelled to the same loudness (90th-pct frame RMS → −24 dBFS, ±10 dB), page/pencil SFX only, no music.

## Clips (shooting order) → chapters
| # | clip | time | chapter | what's used |
| --- | --- | --- | --- | --- |
| hook | IMG_0193 | 09:00 | — | ball passing the cup 0.5×, freeze, "Nyaris masuk 😱" |
| title | IMG_0215 | 11:32 | — | scenery pan, "1 Round · Templer Park" |
| 01 | IMG_0176 | 07:40 | Chipping 101 | ball position tengah / depan sikit / weight kiri / face normal, the chip |
| 02 | IMG_0188 | 08:27 | Coach pun duff | setup 7× → duff → laugh |
| 03 | IMG_0192 | 08:54 | Hantar pin | "Jangan gerak, kita nak hantar pin dalam hole" (large-v3), the shot |
| 04 | IMG_0193 | 09:00 | Bunker | question, "about 20 feet, stock shot", shot, whip, roll past the cup, "What a player!" |
| 05 | IMG_0203 | 10:01 | Downhill lie | menurun / tendency kiri / ball position tengah / pegang pendek / weight kaki kiri / shot |
| 06 | IMG_0205 | 10:12 | Tee shot | two drives in the mist |
| 07 | IMG_0206 | 10:19 | 80 meter | "KD cakap 80 meter" (large-v3), the shot |
| 08 | IMG_0211 | 11:05 | Chip in = RM50? | the bet, the chip, "Tak dapat" |
| 09 | IMG_0214 | 11:30 | Divot cam | ground-level strike (landscape source, centre-cropped 9:16), 0.5× on the turf |
| 10 | IMG_0216 | 11:36 | Hole 18 | "Iconic hole, Templer Park, 18" (large-v3), tee shot, end card |

Not used: IMG_0213 (putting, too far to read), IMG_0187 (lie close-up), IMG_0041 (9 Nov, another course: "pro pun miss … life goes on"),
IMG_5564 / IMG_6392 / IMG_6411 (other golfers at ranges, October / early November).
Uncaptioned on purpose (passes disagree): "kuatnya bang" (0206), "good shot" (0205), "takut takut" (0213).

## Build
```
tools/fetch.sh                      # all 16 clips
python3 tools/build_aroll.py && python3 tools/build_index.py
npx hyperframes@0.9.32 check
npx hyperframes@0.9.32 render -q draft -o renders/preview_draft.mp4 && tools/master.sh renders/preview_draft.mp4 previews/templer-round_preview_v1.mp4
# on "render":
npx hyperframes@0.9.32 render -q delivery -o renders/final_raw.mp4 && tools/master.sh renders/final_raw.mp4 final/templer-round_1080x1920.mp4
```
The 93 s masters (~150 MB) are over GitHub's 100 MB file limit: previews/ and final/ mp4 are git-ignored here; delivered directly.

## Delivery
Owner approved v1 ("ok render", 2026-11-13). `final/templer-round_1080x1920.mp4`: 93.4 s, 1080×1920, 30 fps, H.264 High ~13.1 Mbps, AAC 256k,
−14.0 LUFS, −2.9 dBTP, 152 MB (git-ignored: over GitHub's 100 MB limit; delivered directly).
