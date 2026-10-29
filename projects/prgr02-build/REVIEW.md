# Review — "Dibina, bukan dibeli siap" (preview stage)

## Source
- No video arrived with the request: only four 960×1280 chat photos (PRGR 02 heads, KBS TGI 60 shafts,
  Golf Pride MCC Plus 4 grips). The Drive folder "Claude Video" only holds the 28 Oct swing clips already used.
  The owner said to build it from the photos ("ya kasi jadi je"), so: no voice, nothing to transcribe,
  no face on screen (only legs/feet in two photos, all below the copy).
- Photos upscaled 2× (lanczos + light unsharp) into `assets/stills/`.

## Creative calls
- Storyline: a build sheet — hook "DIBINA. bukan dibeli siap." → the three parts, each with its own move →
  the fitting step (length) → recap equation + hanko → DM CTA over the head badge. Not built: a price/promo cut, a
  before/after "off-the-rack vs custom" cut.
- Look "Spec Plate" (SPEC.md): steel badge plates cut like the PRGR cavity badge, KBS red as the only accent,
  Barlow Condensed. Unlike every previous look in STYLE-LOG.md.
- Cut on a 124 BPM grid; the music's drop lands on the first head shot (2.419 s); seams on beats 5/13/21/27/35/41.
- Transitions: whip (hook→head), red iris out of the tag (head→shaft), zoom-through (shaft→length),
  measure-line wipe (length→grip), blur swap (grip→recap), dip cut (recap→logo).
- Copy claims kept to what the products print or what a fitter does: "Kepala besi dari Jepun", "Graphite tour",
  "Ringan di tangan" (60 g class graphite vs steel), "Reduced taper" not used on screen.

## Revision v2 (owner: "buang logo dan semua description")
- Logo end card removed; the CTA plate "CUSTOM BUILD & FITTING / DM KAMI." now sits on a close-up of a head badge.
- Every description line under the plate titles removed (hook line, Kepala besi dari Jepun, Graphite tour…, Shaft dipotong…, Golf Pride. Saiz…, Tempah set…).
- Brand text gone from the hook tag ("Custom build") and the hanko (ring "DIBINA · CUSTOM", centre "LULUS").

## Measured
- v2 preview after `tools/master.sh` (limiter −2.9 dB): −14.1 LUFS integrated, −1.7 dBTP. Measured, not heard.
- `check`: ok, 0 errors. Kept: `line_unread` on the hanko ring text (decorative seal, 0.77 s);
  `container_overflow` on `#sh-rot` (the rotated photo is meant to overflow its clip).
- Safe zones: every word inside y 270–1330 and x 64–924 (right rail clear); copy also inside the 3:4 grid crop.
- Preview after `tools/master.sh`: v1 −14.0 LUFS, −1.5 dBTP; v2 see below. Measured, not heard.

## Weakest shot / next
- The chat photos are small (960×1280) and soft at 2× zoom (shaft shot most). Originals from the phone would sharpen every shot.
- A 2–3 s clip of hands fitting a grip or cutting a shaft would make the "dibina" claim real footage instead of stills.
