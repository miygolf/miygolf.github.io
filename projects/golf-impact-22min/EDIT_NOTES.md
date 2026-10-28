# "22 minit" — before/after impact edit (HyperFrames)

Source: Google Drive folder `1kptuZSNf8-Zq_3cTnAplmOHGZtOv1p4J`, four 4K 60 fps portrait clips shot 2026-10-28.
Rebuild the cut footage and stills: `tools/prepare_footage.sh <folder with the four VID_*.mp4>`.

| Clip | Role | Impact frame (s) |
| --- | --- | --- |
| `VID_20261028_130606.mp4` | Before, down the line (13:06) | 4.430 |
| `VID_20261028_130630.mp4` | Before, face on (13:06) | 6.778 |
| `VID_20261028_132845.mp4` | After, down the line (13:28) | 6.133 |
| `VID_20261028_132901.mp4` | After, face on (13:29) | 5.333 |

The filenames' timestamps are the hook: the two sessions are 22 minutes apart.

## Transcript (faster-whisper medium, `ms` + auto, word timestamps)

No usable speech. The clips hold range ambience, other bays' strikes and the swing itself.
Whisper returned noise tokens on 130606, nothing on 130630, "Tunggu lagi … Baik" (low confidence,
background) on 132845, and the usual "thanks for watching" hallucination on 132901. So the edit is
cut on picture beats (top of swing, impact), not on words, and there is no voice to protect in the mix.

## Cuts (22.85 s, 1080×1920, 30 fps)

| Out (s) | Source | Note |
| --- | --- | --- |
| 0.00–2.17 | after face-on 5.07–5.62 @ 0.3–0.35× | Hook: "22 MINIT." on frame 0, freeze on impact at 0.80 |
| 2.17–3.25 | after face-on reversed @ 3× | Rewind + replay bands, clock 13:28 → 13:06 |
| 3.25–6.58 | before DTL 3.30–4.43 | Takeaway at 1×, **transition** at 0.22×, freeze on impact |
| 6.58–9.0 | before face-on 6.55–6.78 @ 0.35× | Freeze on impact, telestrator on the trail knee |
| 8.83–10.2 | — | Fast-forward bands, clock 13:06 → 13:28 |
| 9.78–15.25 | after DTL + face-on | Same structure as before, then release at 1× through the strike |
| 16.25–19.65 | impact stills | Wipe slider before ↔ after (after still re-framed so feet and ball line up) |
| 19.65–22.85 | after finish (6.0 s) | Recap + CTA |

Cut away: ~3 s of address/waggle before each swing and every post-finish walk-off.

## Coaching copy (editable variables)

The telestrator labels are read off the frames only: before face-on, the trail (right) knee kicks in
toward the target at impact; after face-on, the knee holds and the hands lead the clubhead. Every
line is a composition variable (`bfKneeVal`, `afKneeVal`, `afHandVal`, the transition/impact subs, the
hook line and the CTA), so a coach can change the wording without touching layout.

## Look: "Replay Desk" (broadcast telestrator)

Unbounded 900 + Space Grotesk; ink `#0d0e12`, paper `#f5f3ee`, **pink `#ff3d7f` = before**,
**mint `#31f2c0` = after**. Motion signature: skewed broadcast replay bands with a rolling clock,
hand-drawn telestrator rings (wobbly, overshooting ellipses), freeze + white flash + 8–10 % punch-in
on each impact, a wipe-slider comparison.

## Safe zones

Every word sits in y 186–1290 and x 56–900 (TikTok/IG top bar, right rail, caption/handle area).
Faces: hook/after face-on y 670–800, before face-on y 560–730 (≈ 500–660 after the punch-in),
DTL y 600–780. Titles end at y ≈ 460; rings and labels sit at hips, knees, hands and ball; the
compare divider rests at x 720 / 330 / 760 / 330, never on the face (x 450–610).

## Sound

No music (as asked). Bed: the range's own ambience (quiet stretches of all four clips, crossfaded).
The 1× clips keep their own sound, including the after strike at 15.37 s.
SFX: Mixkit (free licence), ids = file names in `assets/sfx/`: 2122 sharp golf hit + 1430/1433
camera shutter on each freeze, 1088 tape rewind, 1474/3115 band sweeps, 166 transition sweep,
3120 tech slide on telestrator draws and wipes, 2303 label hit, 1490/1492 whips,
790 riser into the release, 2908 trailer impact on the after strike, 2299 bass hit on the outro.
Each placed so its peak lands one frame after the picture.

Master: `tools/master.sh` (two-pass loudnorm −14 LUFS + −2 dB limiter). Preview measured
−15.0 LUFS, −0.8 dBTP (measured, not listened to).
