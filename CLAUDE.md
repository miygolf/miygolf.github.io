# House style — MIY Golf video edits

Standing preferences from the owner. Apply them to every new video unless the request says otherwise.
Past looks and lessons are listed in `STYLE-LOG.md`. Read it before you pick a look.
Each past video's project lives on its own `ccr-*` branch (`git branch -r`), not on `main`.

## Always

- Edit with HyperFrames. Transcribe first (faster-whisper; Malay + auto) so cuts, motion graphics and SFX sit where they belong.
  Many golf clips have no speech: if so, cut on picture beats (takeaway, top, transition, impact, finish).
- **Every video gets a new look** (type, palette, motion signature) that is not already in `STYLE-LOG.md`, and is logged there after delivery.
  What carries over is the structure, copy voice and sound rules below, not the visuals.
- Never put animation or text over a face. Keep all text inside the TikTok/IG safe band: y 168–1330 and x 60–930 on 1080×1920
  (status bar at the top, action rail on the right, caption/handle at the bottom).
- Remove repeats, waggles, waiting and walk-offs. Open on the strongest hook, with text on frame 0.
- Show a draft preview before the final render. Render only when the owner says "render".

## Golf lesson before/after (format the owner approved, Nov 2026)

1. **Hook**: the after swing into impact, freeze. Title is the lesson length, e.g. "60 MIN LESSON". Never clock times (they can contradict the title).
2. **BEFORE**: full swing at 1×, real strike sound, then the coach's causes as numbered freezes ("1 …", "2 …"), each on the frame that shows it best
   (loupe, grease-pencil loop, measured gap, arrow).
3. **AFTER**: full swing at 1×, then the fix as numbered steps ("1 … 2 … 3 …"), then a **full-speed** replay of both angles.
4. **Side-by-side proof** of the same position before vs after, measured where possible.
5. **CTA**: "Problem sama?" / "Save. Cuba kat range ↓" + a one-line recap.
- Put the **coach's own diagnosis** on screen, in the coach's words. Don't invent a technical claim the frames can't show.
  If no diagnosis was given, ask for one.
- Length 30–45 s.

## Sound

- **Final = SFX only, no music** (owner's call). Previews may carry music only if asked.
- Use premium SFX (Mixkit free licence; list ids in `assets/sfx/CREDITS.md`), each with a cause on screen, peak one frame after the picture.
- Keep the real strike: the phone records audio ~0.2 s late, so play the take's sound ~0.2 s early.
- Master to −14 LUFS, true peak ≤ −1 dBTP. Deliver 1080×1920, 30 fps, H.264 ~13 Mbps.

## Caption voice (TikTok / IG) — casual Malay

Write like a coach talking to friends: short lines, "je", "la", "korang", "gila", "last-last", "try", a few emoji, no hard sell.
Name the problem in plain words, the fix as 3 numbered short lines, then "save, try kat range".
TikTok: hook line + problem + 3 steps + result + question/save. Instagram: shorter, 3–4 lines. 6 hashtags, always starting `#golfmalaysia #golftips #golflesson #golfswing`.

Example (60 min lesson, TikTok):

```
1 jam je lesson, tengok la beza dia 😮‍💨

Awal-awal tangan jauh gila dari badan, pinggul pulak tak clear langsung 😅

Kita ubah 3 benda je:
1️⃣ lower body gerak dulu
2️⃣ rasa club head depan chest
3️⃣ turn sampai habis

Last-last tangan dah rapat dengan badan, swing pun nampak lain terus 🔥

Korang ada problem sama tak? Save dulu, try kat range nanti 📌

#golfmalaysia #golftips #golflesson #golfswing #beforeandafter #fyp
```

Save each video's captions as `CAPTION.md` in its project folder.

## Reference project

`projects/golf-88-minit/` ("60 min lesson", on branch `ccr-ec317c8e-61sz45`; fetch it with `git fetch origin ccr-ec317c8e-61sz45`): `tools/prepare_footage.sh` (frame-index cuts, 0.5× = every 60 fps frame, no interpolation),
`tools/build_index.py` (whole timeline + SFX placement from one sequence), `tools/master.sh` (loudness + delivery encode), `EDIT_NOTES.md`.
