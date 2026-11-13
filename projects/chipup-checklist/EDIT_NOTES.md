# Chipping checklist — edit notes

Owner: "Sama educational style macam sebelum ni tapi ubah format skit" → same raw, relaxed, educational treatment as the chalkboard edits
(hard cuts, real sound, few soft SFX, no music), in a new format: **"Notebook Checklist"** — a lined notebook page (blue rules, red margin,
binder holes, tape) pinned in the left column; each point gets a checkbox ticked in red pen as the coach says it, key words highlighted;
recap page + "Kelas habis ✌️" sticky over the closing selfie. Shantell Sans 800 + Patrick Hand + Noto Color Emoji.
Paper #fffdf4, rule blue #a9c8ea, margin red #e2675f, ballpoint blue #1f3fa8, red pen #d93a2b, highlighter #eaff6a.

## Transcript (large-v3 full ms + en, crops; `edit/transcript.txt`)
- "Kita nak chip [?]" 2.16–3.40: "chip up ke" / "chip up here" / "chip uphill" / "cip api" across passes → captioned "Kita nak chip…", title **CHIPPING**.
- "Okay, ball position saya akan letak kat tengah." · "Slightly depan sikit, tak apa." · "Weight pula kiri."
- "Okay, club face dia…" + "normal je, tak perlu buka pun." (crop: ms "buka", en "no need to open it")
- impact 19.22 (sound 19.24); camera pans to the green; the person filming turns the phone on himself and holds up two fingers (freeze 26.75).
- Cut: "Right, … Coach [name], sorry" opening, the pause 13.6–15.3, "Baik"/"That's it" (passes disagree).

## Structure (21.9 s)
| film | segment | on screen |
| --- | --- | --- |
| 0.00–2.20 | hook: chip 0.5×, freeze | page "Nota hari ni: CHIPPING / 3 benda je ✍️" (frame 0) |
| 2.20–12.87 | the coach's points | checklist page; tick 1 on "tengah", sub-line on "depan sikit", tick 2 on "kiri", tick 3 on "buka" |
| 12.87–15.73 | address + chip, raw | page leaves after the take-away |
| 15.73–18.03 | camera follows to the green | — |
| 18.03–18.73 | selfie ✌️ | — |
| 18.73–22.6 | v2: the same person laughing (coach-duff clip2, 26.30–26.95), freeze on the smile | recap page (all ticked) + "Kelas habis ✌️" |

## Build
```
tools/fetch.sh && python3 tools/build_aroll.py && python3 tools/build_index.py
npx hyperframes@0.9.32 check
npx hyperframes@0.9.32 render -q draft -o renders/preview_draft.mp4 && tools/master.sh renders/preview_draft.mp4 previews/chipup-checklist_preview_v1.mp4
# on "render":
npx hyperframes@0.9.32 render -q delivery -o renders/final_raw.mp4 && tools/master.sh renders/final_raw.mp4 final/chipup-checklist_1080x1920.mp4
```

## v2 (owner: "Muka hujung tu ejas bagi senyum" → option 1)
No frame of this clip has a smile (checked every frame 26.2–26.96), and no face editing is done. The owner chose to close on the same person
laughing the same morning: `projects/coach-duff` clip2 (IMG_0188) 26.30–26.95 at 1×, freeze on 26.95 (big smile; same shirt and cap).
That clip is `.src/clip2.mov` here (tools/fetch.sh fetches it).

## v3 + delivery (owner: "Part hand gesture peace buang pastu render")
- The two-finger selfie removed: the camera's move to the green cuts straight to the laugh; sticky now "Kelas habis 😄".
- `final/chipup-checklist_1080x1920.mp4`: 21.8 s, 1080×1920, 30 fps, H.264 High ~12.7 Mbps, AAC 256k, −14.0 LUFS, −2.9 dBTP.
- Still open: "chip up" vs "chip uphill" (title kept neutral: CHIPPING).
