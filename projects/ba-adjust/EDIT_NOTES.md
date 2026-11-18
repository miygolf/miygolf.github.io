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
  adalah kes early extension tu" · fix 3 "after ni finishing cantik je". The student's name and the comparisons to another player are not used.

## Structure
| film | segment |
| --- | --- |
| 0.00–2.10 | hook: AFTER down-the-line into impact 0.5×, freeze; title slate on frame 0 |
| 2.10–4.90 | TAKE 01 BEFORE at 1×, real strike |
| 4.90–18.77 | coach's analysis: ✓ backswing sama · 1 tangan atas plane · 2 badan terangkat (quote cards on the top panel) |
| 18.77–21.27 | TAKE 02 AFTER at 1× |
| 21.27–34.57 | analysis: 1 turun dalam plane · 2 lutut masuk / tak early extension · 3 finish cantik (cards on the bottom panel) |
| 34.57–37.97 | full-speed face-on replay: before, after |
| 37.97–41.37 | after finish freeze, CTA "Problem sama? / Save. Cuba kat range ↓" + recap |
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
