# Review — PRGR 02 × KBS TGI 60 × MCC Plus 4 bench film (v3, preview stage)

## Source
- No video arrived with the request: only four 960×1280 chat photos (PRGR 02 heads, KBS TGI 60 shafts,
  Golf Pride MCC Plus 4 grips). The owner said to build it from the photos. No voice, nothing to transcribe,
  no face on screen (legs/feet only, in two photos).
- Photos upscaled 2× (lanczos + light unsharp) into `assets/stills/` (`src_*.jpg` are the originals).

## History
- v1 "Spec Plate": steel badge plates with titles + description lines, hanko seal, MIY Golf logo end card.
- v2: logo and description lines removed.
- v3 (owner: "purely video je… kosong hanya video n sfx"): every on-screen word, plate, seal, measure line and
  logo removed. What is left: the photos, camera moves, transitions and sound. SFX whose only cause was text
  (plate slides, engraving, recap word hits, stamp, CUT tick) were dropped with it.
- Two deliveries of v3: with the music bed (`v3_music`) and SFX only (`v3_sfx`, the bed muted).

## v4 (owner: "background atas padang golf")
- Every product is cut out (BiRefNet-general via rembg; the HyperFrames remove-background model is for people and
  kept only the legs). The row photo adds a separate grip pass, the flat lay a shaft-bundle and grip pass; pens and
  paper masked out; edges pulled in 2 px past the dark mat fringe.
- Behind them: real golf-course video (Mixkit, people cropped out), 9:16 crops softened (gblur 2.5) for depth,
  drifting against the camera for parallax. Products carry a soft drop shadow. Same cut, camera moves and sound.
- Hook framing raised (cy 700 → 640) so the cut bottom edge of the heads stays off frame.

## The cut (22.75 s, 124 BPM grid, seams on beats 5/13/21/27/35/41)
| t (s) | shot | move | sound |
|---|---|---|---|
| 0–2.42 | close-up of wrapped 02 heads | drift, punch-in on the badge at 1.21, whip up | wrap crinkle, riser, sweep, whip |
| 2.42–6.29 | row of heads | lands from below on the drop, tracks up the row; red iris out of the Golf Pride grip | bass hit + clubs clank, sweep |
| 6.29–10.16 | KBS TGI 60 shaft (turned 8.3° level) | irises open from the label, tracks KBS → TGI 60, zoom-through | metal shing, whip |
| 10.16–13.07 | shaft bundle (length marks) | fast pan settling on the marks | tape measure |
| 12.77–16.94 | grips | wipe on, pan MCC Plus 4 → Golf Pride, blur swap out | sweep, sweep |
| 16.94–19.84 | the whole set | pull back, drift down the heads, dip | clubs clank |
| 19.84–22.75 | head badge close-up | settles, slow track | trailer impact |

## Measured
- `check`: ok, 0 errors. Kept: `container_overflow` on `#sh-rot` (the rotated photo is meant to overflow its clip).
- `v3_music`: −14.1 LUFS, −2.2 dBTP. `v3_sfx`: −15.0 LUFS, −2.5 dBTP (`tools/master.sh`: two-pass loudnorm,
  4× oversampled limiter, AAC 256k — 192k AAC overshot to +0.4 dBTP on the metal shing). Measured, not heard.

## Weakest shot / next
- The chat photos are small (960×1280) and soft at 2× zoom (the shaft shot most). Phone originals would sharpen every shot.
- The products are studio-lit indoor photos over overcast outdoor footage: it reads as a hero product composite, not as the clubs lying on the grass.
- With no words, the film relies on the pictures: real clips of a grip going on or a shaft being cut would carry it further.
