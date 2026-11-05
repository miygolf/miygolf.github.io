# "88 minit" — before (09:55) / after (11:23) (HyperFrames)

Source: Google Drive folder `1kptuZSNf8-Zq_3cTnAplmOHGZtOv1p4J`, four 4K portrait clips (~60 fps, variable frame rate)
shot 2026-11-05. Rebuild cuts and stills: `tools/prepare_footage.sh <folder with the four VID_*.mp4>`.
Roll scenes are generated: edit `tools/build_rolls.py`, then `python3 tools/build_rolls.py`.

| Clip | What | Impact frame (index) |
| --- | --- | --- |
| `VID_20261105_095511.mp4` | 09:55 face-on | 153 |
| `VID_20261105_095523.mp4` | 09:55 down the line | 82 |
| `VID_20261105_112306.mp4` | 11:23 face-on | 184 |
| `VID_20261105_112337.mp4` | 11:23 down the line | 188 |

## Transcript

faster-whisper `medium`, `ms` and auto-language, word timestamps: **no speech in any clip**. Whisper returned only
the "Terima kasih kerana menonton!" / "Thanks for watching!" hallucination (no_speech_prob 0.75–0.80) or nothing.
The clips hold range ambience and the strike. So the edit is cut on picture beats (takeaway, top, impact) and there
is no voice to protect in the mix; the music is ducked under the real strikes instead.

## Story (22.0 s, 1080×1920, 30 fps)

v1 was a spot-the-difference; the owner asked for **before and after** (v2): 09:55 = BEFORE, 11:23 = AFTER.
No coaching diagnosis is written on screen (none was given); the loupe marks where to look (pinggul, lutut).
Every line is a composition variable.

| Out (s) | Source | Beat |
| --- | --- | --- |
| 0.00–2.40 | AFTER face-on top → impact @0.5×, freeze | Hook "88 MINIT." on frame 0, tape "Before → After. / Satu sesi." |
| 2.40–4.43 | BEFORE face-on 1× → match cut to DTL through impact | chip "BEFORE · 09:55", real strike sound |
| 4.43–8.60 | BEFORE face-on replay @0.5×, freeze | "Before." loupe: pinggul → lutut |
| 8.60–10.23 | AFTER face-on 1× → DTL through impact | chip "AFTER · 11:23", real strike sound |
| 10.23–14.40 | AFTER face-on replay @0.5×, freeze | "After." loupe: pinggul → lutut |
| 14.40–18.00 | both impact stills | Proof sheet "BEFORE vs AFTER", grease-pencil loops, "88 minit. Satu sesi." |
| 18.00–22.00 | AFTER DTL impact → finish @0.5×, hold | CTA "88 MINIT JE." / "Nak swing macam ni? Komen ↓" / "SAVE · cuba kat range nanti" |

Cut away: 1–2 s of address/waggle before every swing, the walk-off after each finish.
Slow motion is 0.5× of the 60 fps source = every real frame, no interpolation (no club warping).

## Safe zones and faces

Words sit in y 190–1330 and x 60–930 (TikTok/IG status bar, right action rail, caption band).
Faces: 09:55 face-on y 640–800, 11:23 face-on y 470–640, DTL y 540–860, all at x 420–620. Titles end at
y ≈ 410; loupe and loops sit on hips and the trail knee; labels go beside the body, never over the head.

## Sound

Music: Mixkit "Hip Hop 02" (#738, Mixkit free licence), entered at 0.49 s so a beat lands on the hook freeze;
bed 0.36–0.46, ducked to 0.24 under each real strike, 1.4 s fade-out.
Real strike: the DTL clips' own audio, played 0.20–0.24 s early (the phone records audio ~0.2 s late).
SFX (Mixkit, ids = file names in `assets/sfx/`): 2121/2126 golf strikes layered under the real ones, 1438/1440
vintage shutter on each freeze, 2909 bass hit on the hook, 1473/1468 swing whooshes on the slow-mo, 1489/1491
air whoosh + 1442/1444 projector on the film-advance cuts, 2998 marker line on each grease-pencil mark,
1530 paper slide on the prints, 2369 scribble on "?" and the CTA, 1143 deep impact on the final strike.
Peaks placed one frame after the picture (measured with `hyperframes audio`).

Preview measured −17.7 LUFS, −2.8 dBTP, no clipping (measured, not listened to). Final: master to −14 LUFS.

## Fonts

Bricolage Grotesque, DM Mono, Permanent Marker — Google Fonts, SIL Open Font License 1.1.
