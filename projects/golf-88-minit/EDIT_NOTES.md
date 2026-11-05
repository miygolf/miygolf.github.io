# "60 min lesson" — before / after, body clearance fix (HyperFrames)

(Project folder keeps its first working name, `golf-88-minit`.)

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

## Story (32.5 s, 1080×1920, 30 fps)

v1 spot-the-difference → v2 before/after → v3 coach's diagnosis → v4 35 s with three causes →
**v5 (current): title "60 MIN LESSON", the "tangan drop too shallow" beat removed.**
Clock times (09:55 / 11:23) are taken off screen so they don't contradict the 60-minute title.
Coach: no body clearance and the hands too far from the body. Fix: after the transition the lower body moves
first, feel the club head in front of the chest, turn all the way. At delivery the before swing's hands sit
~220 px from the belly vs ~140 px after (1080-wide frame), which the proof sheet measures.
Timeline is generated: `python3 tools/build_index.py` (edit SEQ / cues there).

| Out (s) | Source | Beat |
| --- | --- | --- |
| 0.00–2.40 | AFTER face-on top → impact @0.5×, freeze | Hook "60 MIN / LESSON." + tape "Before → After. / Fix body clearance." |
| 2.40–4.43 | BEFORE face-on 1× → DTL through impact | chip "BEFORE", real strike |
| 4.43–7.27 | BEFORE DTL replay → freeze frame 78 | "1 Tangan jauh dari badan." + measured gap "jarak" |
| 7.27–10.33 | BEFORE face-on replay → freeze impact frame 153 | "2 Takde body clearance." loupe + loop on hips, "pinggul tak clear" |
| 10.33–11.97 | AFTER face-on 1× → DTL through impact | chip "AFTER", real strike |
| 11.97–14.70 | AFTER transition → freeze frame 170 | "1 Lower body gerak dulu." arrow round the hips |
| 14.70–17.17 | AFTER DTL → freeze frame 183 | "2 Club head depan chest." loop + short gap "tangan dekat badan" |
| 17.17–20.13 | AFTER impact → finish 1× → freeze frame 230 | "3 Turn habis." arrow round the waist |
| 20.13–24.40 | AFTER full swing 1×, face-on then DTL | "FULL SPEED · 1×" "Semua sekali." both real strikes |
| 24.15–28.40 | DTL delivery stills | Proof sheet: gap "jauh" vs "dekat", "Tangan dekat badan. / Lower body dulu. Turn habis." |
| 28.40–32.53 | AFTER DTL impact → finish @0.5×, hold | CTA "Problem sama?" / "Save. Cuba kat range ↓" / "60 MIN LESSON · lower body dulu, turn habis" |

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

Preview v5 measured −18.3 LUFS, −2.5 dBTP, no clipping (measured, not listened to). Final: master to −14 LUFS.

## Fonts

Bricolage Grotesque, DM Mono, Permanent Marker — Google Fonts, SIL Open Font License 1.1.
