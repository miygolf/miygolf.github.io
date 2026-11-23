---
name: break100-episode
description: Build a MIY GOLF "Break 100" episode (or any slide-video + separate voice-over explainer) in the owner-approved cream "Range Map" look, split into weekly parts. Use when the owner sends a silent slide video (storyboard) plus a voice-over recording for a Break 100 episode, or asks for "macam episod 1 / Range Map / cream background" style.
---

# Break 100 episode — Range Map explainer, split into parts

Owner-approved format (Ep1 and Ep2, Nov 2026). The owner said: "aku suka, aku like style ni". For this series, do NOT invent a
new look per episode. Keep the cream Range Map look; only the diagrams change with the drills. This overrides the "new look every video" rule
in CLAUDE.md for the Break 100 series only.

Reference projects: `projects/break100-ep1/` (3 parts) and `projects/break100-ep2/` (2 parts). Both are on branch `claude/gifted-davinci-2netbk`.
The tool kit in `kit/` is a copy of Ep2's tools: start from it.

## Inputs
- `MIY_GOLF_EpN_Break100_9x16.mp4`: the owner's silent slide video. It is the **storyboard**: wording, numbers, diagram ideas, drill names,
  any stat and its source. Never use it as footage.
- `epN_break_100.wav`: the voice-over. The voice leads everything.

## Look: "Range Map" (keep exactly)
- Cream paper `#f3eee2` with a dot grid (radial-gradient 1.2px, 36px). Ink `#141714`, fairway `#2f8a3e`, light fairway `#a8d68f`,
  rough `#6fae5a`, flag red `#e8412c`, sand `#e7d6a6`.
- Hanken Grotesk 800/700/600 for headlines and captions, Geist Mono 600/700 uppercase for labels, Noto Color Emoji only inside `.emo` spans.
  Copy the fonts from `projects/break100-ep1/assets/fonts/` (or google/fonts raw: `ofl/hankengrotesk/HankenGrotesk[wght].ttf`,
  `ofl/geistmono/GeistMono[wght].ttf`).
- Header: "MIY GOLF · EpN · Break 100", a green part tag ("1/2"), and 3 drill progress bars.
- Drill headline: big green number with a "10 MINIT" pill, title 82px on one line.
- Diagrams are top-down plans drawn like a plotter: green dashed lines draw on, balls white with an ink rim, misses red, results as green/red dot tallies.
- Episode card: an ink-bordered white grid. Drill tiles: white with an ink border and an 8px ink offset shadow.
- Captions: an ink strip at y 1176 with paper text, Hanken 700 at 42px, at most 2 lines. Shorten the text if a line would wrap to 3.
- Transition between sections: a full-screen green page sweep with a white/red yardage stake (x −1180 → 1180, 0.56 s).
- Chips: green with white text and a 6px ink shadow. End chips: "Like untuk part N 👍" on every part except the last, and a recap list
  with "Save. Try minggu ni ↓" on the last part.
- Safe band: x 60–930, y 168–1330 on 1080×1920. Text appears on frame 0.

## Sound
- Continuous Mixkit "Digital Clouds" bed (music id 175, `https://assets.mixkit.co/music/175/175.mp3`). Run `tools/build_music.py <total>`:
  loudnorm −27 LUFS with only a gentle sidechain dip. The owner wants "presentation" music that runs to the end, never sleepy or heavily ducked.
- SFX are the Mixkit set in `kit/SFX-CREDITS.md` (`https://assets.mixkit.co/active_storage/sfx/<id>/<id>-preview.mp3`). Every sound needs a cause on screen.
- Master with `tools/master.sh`: −14 LUFS, ≤ −1 dBTP, H.264 CRF 17, 30 fps, AAC 256k.

## Voice cutting rules (the owner checks these)
1. Transcribe with faster-whisper large-v3 (`language="ms"`, domain prompt), decoding the audio yourself with ffmpeg to a numpy array
   (the installed `av` breaks `transcribe(path)`). Save `edit/vo_words.json` and `edit/transcript.txt`.
2. **Measure the noise floor first** (20 ms RMS, p10). Set `SIL` about 3 dB above the floor and `LOUD` about 10 dB above it in `build_voice.py`.
   Ep1's floor was −55 dBFS; Ep2's was −46 dBFS.
3. Full-pass whisper word times can be 0.2–0.8 s early. Set every piece boundary from the **audio** (energy print and crop re-transcription
   with 0.5 s padding). Never set a boundary from the transcript alone.
4. "Jangan potong yang hujung-hujung": every phrase ending must be heard fully. The fade covers only silence, the tail is capped at the next
   phrase's start, and contiguous phrases are cut as one run.
5. Remove repeats, stray "Ok", breaths and room noise before the first word. Lead with the strongest line; each part opens on its own strongest line.
6. Afterwards, re-transcribe each part's voice and the final mix. Every phrase must be complete, with no word leaking across a cut.

## Steps
1. `mkdir projects/break100-epN/{.src,edit,assets/{fonts,sfx,music},previews,final}`. Copy `kit/*` (tools, package.json, hyperframes.json,
   .gitignore), the fonts, the SFX and the music. Put the inputs in `.src/` (they are not committed).
2. Look at the storyboard: a contact sheet at 1 frame per 2 s, `tile=7x4`.
3. Transcribe, measure the floor, and print 40 ms energy around every boundary. Write `PIECES` (key, src_start, src_end, text), `EXTRA`
   (the part-ending line) and `HOOKS` in `build_voice.py`.
4. Plan the parts in `make_parts.py`, each 30–45 s and standalone:
   - Part 1: hook, episode card, drill 1, the CTA, and "Like untuk part 2".
   - Later parts: open on a strong line, then the drills, then "Pergi … minggu ni." and an end card.
5. Rewrite the drill scenes in `index.template.html` (SVG diagrams from the storyboard) and the anchors/captions/cues in `build_index.py`.
   Anchors are `(recording time, lag)` pairs and must be measured.
6. Per part: `build_voice.py`, then `build_music.py <total_voice+2.4>`, then `build_index.py`, then `npx --yes hyperframes@0.9.32 check`.
   Fix layout, contrast, type-floor (≥ 28 px) and dead-stretch (> 3 s) findings. A contrast flag on the sweep's mid-transition frame is expected.
7. Run `hyperframes snapshot --at …` and look at every scene for overlaps and anything outside the safe band. Then render a draft and master it
   to `previews/break100-epN_partK_preview_v1.mp4`.
8. Write `CAPTION.md` (casual Malay, TikTok and IG per part, the 6 hashtags from CLAUDE.md, a "Like untuk part 2" line), `EDIT_NOTES.md`
   and a `STYLE-LOG.md` row. Commit, push and send the previews.
9. Final only when the owner says "render": `render -q delivery`, then `master.sh` into `final/break100-epN_partK_1080x1920.mp4`.
