# Before & after adjustment — edit notes

Drive folder 1vAvvjHm1jcRnv-GNmpjir7cBmisdTn-b (18 Nov 2026, night, bay 32). Approved before/after format (CLAUDE.md), 41.4 s, no music.

**Look: "Film Slate"** — the lesson as two takes: TAKE 01 BEFORE / TAKE 02 AFTER clapperboards with hinged striped sticks that clap shut,
the coach's analysis screen recording shown as-is (his red plane line; top = before, bottom = after) between slate-black margins with
vertical BEFORE / AFTER labels, numbered quote cards that light the coach's words as he says them, CTA on a slate.
Saira Extra Condensed 800 + IBM Plex Mono 600 + Caveat 700 + Noto Color Emoji. Slate #141414, white #f2f1ec, before orange #ff7a1a, after mint #2ee59d.

## Sources
- IMG_0328 (21:21) BEFORE down-the-line, impact 11.02 · IMG_0330 (21:22) BEFORE face-on · IMG_0331 (21:39) AFTER down-the-line, impact 7.10 · IMG_0333 (21:39) AFTER face-on.
  "18 minit kemudian" = the two down-the-line takes' record times (17.6 min apart); the lesson length was not given, so it is not the title.
- `clip_m4v.m4v`: the coach's analysis (screen recording with his voice, 105.6 s). **Diagnosis in his words** (large-v3 ms + en + crops):
  backswing "angkat cantik je, on plane" (same on both) · cause 1 "bila down swing tu, tangan tu di atas swing plane" · cause 2 "terangkat
  badan-badan, sebab bodi tak clear" · fix 1 "dia turun, dia dalam plane, so kita jadi shallow lah" · fix 2 "lepas tu lutut masuk" + "kita tak
  adalah kes early extension tu" · fix 3 "after ni finishing cantik je". The coach says the student's name several times (start, ~24.3 s, ~64.3 s "lutut masuk macam <name>", ~67.9 s): whisper heard it as another name; every cut ends/starts clear of it (privacy).

## Structure
| film | segment |
| --- | --- |
| 0.00–2.10 | hook: AFTER down-the-line into impact 0.5×, freeze; title slate on frame 0 |
| 2.10–4.90 | TAKE 01 BEFORE at 1×, real strike |
| 4.90–18.77 | coach's analysis: ✓ backswing sama · 1 tangan atas plane · 2 badan terangkat (quote cards on the top panel) |
| 18.77–21.27 | TAKE 02 AFTER at 1× |
| 21.27–34.57 | analysis: 1 turun dalam plane · 2 lutut masuk / tak early extension · 3 finish cantik (cards on the bottom panel) |
| 33.83–37.43 | v2 HOMEWORK: the face-on reps are the drill (owner); the coach's line "Banyak kan buat drill tu lah, yang saya tunjuk tadi tu kan" over them |
| 37.43–41.73 | v2 the student's WhatsApp reply after class (name and profile photo pixelated + blurred), two bubbles outlined |
| 41.73–44.73 | after finish freeze, CTA "Problem sama? / Save. Cuba kat range ↓" + recap |
The coach's stacked analysis is the side-by-side proof (his own line); no measurements are claimed.
Preview mix re-transcribed (medium): every quoted line heard. −14.0 LUFS, −2.7 dBTP.

## Build
```
tools/fetch.sh && python3 tools/build_aroll.py && python3 tools/build_index.py
npx hyperframes@0.9.32 check
npx hyperframes@0.9.32 render -q draft -o renders/preview_draft.mp4 && tools/master.sh renders/preview_draft.mp4 previews/ba-adjust_preview_v1.mp4
# on "render":
npx hyperframes@0.9.32 render -q delivery -o renders/final_raw.mp4 && tools/master.sh renders/final_raw.mp4 final/ba-adjust_1080x1920.mp4
```

## v2 (owner: "front side to drill aka homework kena buat" + "blur nama privacy" with a WhatsApp screenshot)
- The face-on section is now HOMEWORK: both face-on reps at 1× with the coach's drill line (large-v3 100.5–104.0); their strikes kept low under it.
- New testimonial: the student's reply ("Nampak beza dia boss / Ini yg saya dok cari2 teknik dia tu / Alhamdulillah, puas hati dengan kelas tadi
  boss…") in a phone frame over the dimmed after finish. Name and profile photo pixelated then blurred (`assets/img/testimonial.png`, made from
  the owner's screenshot; the original is not in the repo). Backswing card trimmed 0.75 s. 44.7 s.

## v3 (owner: the name the coach says is the student's, not another player)
The "macam <name>" in the coach's voice is the student. Cuts re-checked so it is never heard: "lepas tu lutut masuk" ends at 63.80 (12 ms fade)
before "macam <name>"; the early-extension line starts at 68.36. large-v3 + medium on the final mix find no name. 44.6 s.
