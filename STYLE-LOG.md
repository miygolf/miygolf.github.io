# Style log

Each video gets a look that differs from the ones before it.

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| Golf before/after, weight shift (branch `ccr-7270250b`) | A Telemetry / B Editorial sync / C Kinetic / D Blueprint | JetBrains Mono + League Gothic; serif; bold sans; mono | black + lime; paper + terracotta; white/black + yellow; cobalt | phase strip, burst rings, stacked sync, word pops, crosshairs |
| Golf transformation (branch `ccr-a37c6980`) | Power wipe + split screen | Anton | red / green, gold glow | wipe, side-by-side |
| **Golf "22 minit" impact + transition** (`projects/golf-impact-22min/`) | **Replay Desk**: broadcast replay + telestrator | Unbounded 900 + Space Grotesk | ink #0d0e12, paper #f5f3ee, pink #ff3d7f (before), mint #31f2c0 (after) | skewed replay bands + rolling clock 13:28 ↔ 13:06, hand-drawn rings, freeze + flash + punch-in, wipe slider |
| **PRGR 02 × KBS TGI 60 custom build commercial** (`projects/prgr02-build/`) | **Spec Plate**: machined steel badge plates cut like the PRGR cavity badge, engraved type, red hanko seal | Barlow Condensed 800/600/500 | brushed steel #f4f5f6→#b8bcc2, graphite ink #222428, KBS red #d7191f, end card on the logo's black | plates slot in and seat, engrave reveal behind a red cutter line, red iris out of a tag, zoom-through, measure-line wipe, hanko press — **v3 pure footage, no text; v4 products cut out and floated over golf-course video (Mixkit), parallax** |

## Lessons
- MIY Golf product commercials: the owner wants purely footage + SFX — no logo, no titles, no description lines, no stamps (PRGR 02 build, 2026-10-29).
- Product shots for MIY Golf: the owner wants a golf-course background behind the products, not the workshop bench (2026-10-29).
- Golf lesson before/after: the owner wants the coach's own diagnosis on screen (causes → numbered fix steps), titled by lesson length ("60 MIN LESSON"), no clock times, 30–45 s, and the final with SFX only — no music (2026-11-05).
- Captions: casual Malay ("je", "la", "korang", short lines, 3 numbered steps, "save, try kat range"); see `CLAUDE.md` (2026-11-05).

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **ZQ UAV VTOL "Drone atau pesawat?"** (`projects/zq-uav/`) | **Sectional**: aeronautical-chart overlay | Michroma + IBM Plex Sans Condensed | ink #0b0c10, paper #f4f6f8, airspace magenta #ff2e88 / #e8137a blocks | numbered chips, climb tape, dashed flight path + waypoints, optical-flow-tracked callout rings, screen brackets, white flash + magenta ring on the music drop |

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| Kusyen donut v2 (branch `ccr-5823e76b`) | Blueberry Cloud: cream sticker labels, navy outline | Nunito 800-900 | cream, navy, butter, bubblegum | sticker pops, whips, doodle arrow, iris |
| **Golf "60 min lesson" before/after — body clearance fix** (`projects/golf-88-minit/`) | **Contact Sheet**: film-lab proof sheet — sprocket strip, edge codes, loupe, grease pencil | Bricolage Grotesque 800 (condensed) + DM Mono 500 + Permanent Marker | film black #0e0c0a, photo paper #f6f2e9, edge-code amber #ff8a1f (#c4500a on paper) | film-advance band whips through each cut, shutter flash + frame border on every freeze, magnifying loupe that tracks the body, grease-pencil loops and "?" marks, prints dropped on a proof sheet — previews had a music bed, final is SFX only |

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| Chip contact (branch `ccr-316a69f9`) | Riso Press | Dela Gothic One + Instrument Sans 700 | riso blue, fluoro pink, paper | misregistered slips, halftone dot wipes |
| Putting wrist / Eye-line (branch `ccr-20c8d510`) | Yardage Book / Eye-Line Lab HUD | League Gothic + Space Mono / Outfit + JetBrains Mono | green-cream-yellow / dark glass, lime, coral | see `DESIGN_LOG.md` on that branch |
| Play a hole, birdie hole 1 (branch `ccr-f80be2c7`) | Arcade Round (retro golf game) | Bungee + Silkscreen | violet, sun, ink | pixel HUD, power meter, pixel wipes, BIRDIE burst |
| Golf POV (branch `ccr-3def0113`) | dark green + lime + flag red | — | ground #06120c, lime #c8ff2e, flag #ff3b30 | see that branch |
| **Match play 1 lawan 1, hole 2 KRTU — Iqbal vs Farhan** (branch `claude/practical-maxwell-wcz0rh`, `projects/match-play-hole2/`) | **Title Fight**: fight-night match-play broadcast, red corner vs blue corner | Big Shoulders Display 900 + Oxanium 700 | red #ff2a3d (Iqbal), blue #2b6cff (Farhan), gold #ffc23a (result), ink #0b0b10 | 12° slash plates with hard ink shadows, slash wipes in the incoming player's colour, diagonal VS card + ring bell, shockwave ring + punch on strikes, drawn shot plan, FAT!/BOGEY stamps, letterbox on the deciding putt, KO result slam + gold burst, HUD bar turns gold with W; captions skewed with corner-colour shadow; music bed (Mixkit #400) with the break under the deciding putt |

- Match play hole 2 (2026-11-09, preview): owner asked for a music bed again, voice kept clear (ducked ≈ 16 dB under speech). Only the hole shown is scored on screen — no overall match status unless the owner gives it.
- Match play hole 2 v2 (2026-11-09): owner said the grade was too bright → darker grade (gamma 0.86, highlights pulled to 0.88). Wanted ≥ 60 s, a bit longer (now 75 s), and an outro message ("pukul jauh tak semestinya boleh menang"). Keep long SFX (rumbles, cheers, bells) off spoken lines.
- Match play hole 2 final (2026-11-09): owner then asked to **remove the colour grade entirely** (no grade, no vignette) — delivered on the iPhone's own colour. Default to ungraded footage next time unless asked.
| **Chip atas green — "Ada divot ke tak?"** (branch `claude/beautiful-ptolemy-y3e0cd`, `projects/chip-divot/`) | **Poll Sticker**: the edit plays like a story poll the footage answers | Sora 800/700/600 + Geist Mono 700 | white sticker cards, violet #6b3cff (answer), coral #ff5d4f (doubt), ink #16131c, lilac #efeaff | rounded tilted stickers with spring/squash pops, finger-tap ripple + poll bar fill + drawn check, focus brackets snapping on contact and turf, live speed chip (0.3× … 2.2×), sticker peel exits, white lens bloom + punch on cuts, sparkles, proof captures; captions as white sticker lines, key word violet; music bed (Mixkit #1141) with its break under the walk-back and the drop on the answer |

- Chip atas green (2026-11-10, final): owner asked for a music bed again (voice ≈ 14 dB over it, bed ducked under the real strike too). Re-check quiet lines on a boosted piece: first-pass whisper heard "Mesti tak boleh", it was "Mestilah boleh" — the meaning flips. Approved the first draft as is.

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **Farhan chip + putt "MASUK"** (branch `ccr-57d78901-egq2p0`, `projects/farhan-masuk/`) | **Group Chat**: the hole told like the friends' chat thread — casual, low animation | Plus Jakarta Sans 800 + Bagel Fat One + Noto Color Emoji | tangerine #e2530b (sent bubbles), white, ink #17181c, ink pills rgba(23,24,28,.74) | words light up in the bubble as they're spoken, centre "date" pills per shot, typing indicator → sticker on the hook freeze, MASUK!! sticker on the drop; hard cuts, no wipes, no grade, no music |

- Farhan MASUK (2026-11-11, delivered from preview v1 unchanged): owner asked for **casual style, less animation** — one bubble/pill/sticker at a time, hard cuts, SFX kept soft and off the voice.
  The narrator films and talks quietly behind the phone: lift his pieces (+9 dB) before mastering so he sits on top of the course noise.

Other edits found on branches (not logged at the time): Hole 5 KRTU **Departure Board** (split-flap board, boarding passes, passport stamps; Archivo + Martian Mono; flap black, departure yellow, stamp ultramarine; branch `claude/beautiful-ptolemy-y3e0cd`),
Faiz P6–P8 **lab / telestrator** (graphite grid, red/lime, Archivo Black + JetBrains Mono; `ccr-5311858d`), first-time golf reel (loading-bar joke; `claude/intelligent-newton-2elq5i`), swing rating / saya vs adik (pose skeleton cards; `claude/laughing-dijkstra-x62sgu`).

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **Tip: pitch keluar bunker, plenty of green — Coach Farhan** (branch `ccr-0ed8529b-j52mac`, `projects/shot-tip/`) | **Shot Manual**: the tip as a fold-out instruction leaflet | Anybody (variable width: 850 @ wdth 62 headlines, 700 @ wdth 88 captions) + Azeret Mono 600 + Noto Color Emoji | paper #fbfbf6, ink #111316, signal cyan #10bfff (fills and lines only), mute #5d6168 | step panels unfold from their crease (numbered ink disc, hard ink drop shadow), accordion-fold wipe (paper / grey / cyan panels) into the tip and into the replay, dashed flight line + pulsing landing ring for "visualize", checklist pips that tick before the swing, warning triangle, ACCELERATE stamp on the 0.5× replay, paper caption strips with the key word underlined cyan; flash + punch on strikes; no grade, **no music** |

- Shot tip (2026-11-11, delivered from preview v1 unchanged, approved with "cun"): owner asked for **no background music** (SFX only) on a coach tip video. The coach's key word ("accelerate") was soft and whisper's word end was early:
  pin word ends with a cropped re-run that includes the next word, not just the word itself, before cutting. Reaction lines heard differently by each pass are kept as sound but not captioned.

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **Draw elak dahan, 154 ke pin — shot tracer** (branch `ccr-0ed8529b-j52mac`, `projects/tracer/`) | **Glass Tracer**: clean broadcast built around the tracer, frosted-glass cards | Manrope 800/700 + Fragment Mono | glass white rgba(255,255,255,.64), ink navy #0b1736, coral #ff5a36 → gold #ffc93a (tracer gradient), ice #c9f3ff | cards materialise from blur with a specular sheen, full-height glass sweep transitions, plan drawn into the scene (blocked straight line + X, branch rings, draw curve, aim rings, pin flag), broadcast-style red tracer tapering with distance (v1 was a coral→gold comet; owner wanted it more realistic) over a ghost of the plan, 1.6× push-in on a stage that keeps the tracer locked, ground ripple on landing; no grade, no music |

- Tracer (2026-11-12, delivered from preview v5): owner asked for a **shot tracer**. From a tripod behind the golfer the ball is trackable by frame differencing only for ~0.4 s
  (it disappears into the tree line); measure the launch, continue with a fitted curve, and say which part is estimated. Zoom in on the flight so the shape reads. Owner prefers a **realistic tracer** (thin red line tapering with distance, small head) over a stylised comet, and wants the draw shape readable: round, out right, turning left *before* the aim point (the bunker), into the pin.
  Added the result clip from the green (over the pin → birdie putt runs by → putt back drops, "good save"); a result section after the shot works well for this owner.

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **Rate swing sebelum vs selepas adjust** (branch `ccr-beb826e1-xrjzst`, `projects/swing-rating/`) | **Card Grade**: the swing graded like a collectible card | Rubik Mono One + Schibsted Grotesk 800/700 + Chivo Mono 600 | ink #101014, label stock #f6f5f0, rust #ff5b24 (before, "common"), holo #7cf3ff→#b18cff→#ff8fd0→#ffe27a (after; deep holo for text on white) | slab label plates flick in (rotateY), rounded card edge + foil glint snaps round every freeze, frame shrinks into an acrylic grading slab (card art + stat bars + grade roll-up), diagonal foil sweeps between sections, UPGRADE stamp + sparkles, pose-tracked spine lines with angle arcs, head pins above the cap on a push-in; no grade, no music |

- Rate swing (2026-11-12, delivered from preview v1 unchanged, approved with "cun"): owner asked me to **rate** the swing before/after with no coach diagnosis given. Ratings come from pose measurements
  (MediaPipe): spine angle lost at impact 18° → 7°, head shift at the top, finish; tempo not rated because the two camera angles disagreed. Clips had no speech.

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **Coach pun duff — "Part of the game"** (branch `claude/gifted-davinci-2netbk`, `projects/coach-duff/`) | **Trail Cam**: the blooper as wildlife footage — trail-camera data bar + naturalist's field tags | Fraunces (opsz 144, SOFT, WONK; italic punchlines) + Share Tech Mono + Noto Color Emoji | bark ink #16130e, card khaki #efe5c8, trail-cam amber #ffb21a, REC red #ff3b2f, stamp moss #2f5a2c | real record clock that races on FF ×7 and runs backwards on the rewind, khaki tags swing in on a string and sway, shutter flash per trigger, desaturated tape rewind with tracking bands, tracked flag ring, setup stopwatch, crickets on the stare, field-guide entry card on the freeze; bird ambience bed, no grade, no music — **delivered from preview v1 unchanged** |

- Coach duff (2026-11-13, delivered from preview v1 unchanged, "ok render"): blooper with no speech; owner asked for **no background music** (said both "letak background music" and "no background music" — the later one and the house rule won).
  Ambience SFX (birds, crickets) carried the nature-doc joke instead.

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **Bunker, nyaris masuk** (branch `claude/gifted-davinci-2netbk`, `projects/bunker-nyaris/`) | **Neon Clubhouse**: the 19th-hole bar's neon signs | Tilt Neon + Sora 700/800 + Noto Color Emoji | tube pink #ff3d8b, tube aqua #39f3ff, tube core #fff4fa, smoked glass rgba(9,7,20,.74) | signs stutter-flicker on with an electric buzz, glowing tube frames, neon scan-line wipes, neon tracker ring riding the ball, pink pulse ring at the cup, pink-tinted impact flash; no grade, no music — **delivered from preview v3 (wide)** |

- Bunker nyaris (2026-11-13, delivered from v3 "render"): owner asked for a zoom-out at address (v2), then "bagi nampak surrounding" (v3: everything near full frame) — this owner prefers wide framing that shows the course over tight punch-ins. Ball from the bunker rolled right past the cup — hook on the near-miss, not on the strike.
  Numbers the coach says (distance) need a large-model crop check: small heard "30", medium/large-v3 crops heard "20"; strong noise reduction in the mix also turned it into "30".

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **Uneven lie: downhill tutorial** (branch `claude/gifted-davinci-2netbk`, `projects/downhill-lie/`) | **Spirit Level**: a builder's level — yellow tool-body cards with a glass vial | Big Shoulders Display 900 + Figtree 800 + Red Hat Mono 600 + Noto Color Emoji | level yellow #ffd400, ink #121212, vial mint #bff3cf, aluminium #a7afb6 | cards slide in tilted and level out as the bubble glides to centre (number in the bubble), card tips off level on "menurun", tilted hazard-edged band wipes, ground marks riding the tracked ball (stance bracket, grip ring, low-point ring + ? markers, left-foot arrow), recap card; no grade, no music, wide framing — **delivered from preview v1 + end voice muted** |

- Downhill lie (2026-11-13, delivered: owner asked to mute the voice at the end — never use the clip tail as room tone if it carries talk from behind the phone): face-on tutorial with the coach's own words (large-v3 transcript; one tip "… kanan sikit" held back as unclear).
  Face-on: target is screen right, so "kiri/kanan" are drawn as a top-down diagram or on the named foot, never as a bare screen arrow.

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **Kelas Bunker 101 (raw cut of the bunker near-miss)** (branch `claude/gifted-davinci-2netbk`, `projects/bunker-raw/`) | **Chalkboard**: chalk notes on raw footage | Cabin Sketch 700 + Kalam 400/700 + Noto Color Emoji | slate #25312b, chalk #f3f0e6, chalk yellow #ffe07a, chalk pink #ff9fb8, rim wood #8b5e3c | small slate boards, stepped chalk write-on, hand-drawn chalk circle tracked on the cup, double chalk underline, eraser wipe, HOMEWORK end board; hard cuts, 1× real sound, five soft SFX, no music — **delivered from preview v3** |

- Bunker raw (2026-11-13, preview v1): owner asked for **educational + a little humour, relaxed, less SFX, raw**, and to hear the green. Low-motion notes, hard cuts, real sound carries it.
  v2: the coach's word is **"stock shot"** (not "stop shot": whisper heard "stop-sharp / stock shower / stock shaft"); and never loop a short ambience piece under a freeze — the owner hears the repeat as a stuck sound ("sound yg sangkut").

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **Chip in RM50 (30 m)** (branch `claude/gifted-davinci-2netbk`, `projects/chip-rm50/`) | **Chalkboard, reused on request** ("sama buat macam bunker shot style") | as Kelas Bunker 101 | as Kelas Bunker 101 | boards in the right column (head high in frame), bet chalked line by line, eraser wipe, HOMEWORK board, v2 adds a 0.5× replay with the coach's two steps chalked on freezes; hard cuts, real sound, soft chalk SFX — **delivered from preview v2** |

- Chip RM50 (2026-11-13, preview v1): the owner asked to repeat the bunker-raw style — a request to reuse a look overrides "every video gets a new look".
  v2: the owner gave his own method ("takeaway dengan open club face, pastu release macam biasa") and asked to drop the CTA: a replay with numbered freezes in his words beats a CTA here.

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **Chipping checklist (ball tengah, weight kiri, face normal)** (branch `claude/gifted-davinci-2netbk`, `projects/chipup-checklist/`) | **Notebook Checklist**: lined notebook page with red-pen ticks (same raw educational treatment, new format) | Shantell Sans 800 + Patrick Hand + Noto Color Emoji | paper #fffdf4, rule blue #a9c8ea, margin red #e2675f, ballpoint #1f3fa8, red pen #d93a2b, highlighter #eaff6a | page slides into the left column, checkbox ticked in red pen on each spoken point, highlighter on key words, paper caption strips, recap page + sticky note over a closing laugh (v2: borrowed from the same morning's duff clip because the selfie had no smile); hard cuts, real sound, six soft SFX, no music — **delivered (v3: selfie removed)** |

- Chipping checklist (2026-11-13, preview v1): owner asked for the same educational style with a slightly different format — kept the raw treatment, swapped chalk boards for a notebook checklist.

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **1 Round @ Templer Park — compilation (93 s)** (branch `claude/gifted-davinci-2netbk`, `projects/compile/`) | **Yardage Book**: kraft chapter tabs + pencil round tracker | Young Serif + Sometype Mono + Noto Color Emoji | kraft #d8c49c, ink green #1f3a2b, pencil red #c2412d, chalk #fbf7ec | 10 numbered chapter tabs with the real record time, top round-tracker line with ticks and a walking red dot, kraft caption strips with pencil-red underline, cover-style title/end cards; hard cuts, levelled real sound, page/pencil SFX, no music — **delivered from preview v1** |

- Compilation (2026-11-13): "compile semua" from the Drive folder → one round in shooting order, one consistent look across clips that were edited in different styles; per-segment loudness levelling; off-day / other-golfer clips left out and listed.

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **Before & after adjustment (bay 32, night)** (branch `claude/gifted-davinci-2netbk`, `projects/ba-adjust/`) | **Film Slate**: TAKE 01 / TAKE 02 clapperboards + the coach's own analysis recording | Saira Extra Condensed 800 + IBM Plex Mono 600 + Caveat 700 + Noto Color Emoji | slate #141414, white #f2f1ec, before orange #ff7a1a, after mint #2ee59d | clapper sticks clap shut on each take, the coach's stacked before/after analysis with his red plane line between slate margins and vertical labels, numbered quote cards lit word by word in his voice, homework card on the face-on drill, blurred-name WhatsApp testimonial in a phone frame; no music — **delivered from preview v5** |

- Before/after (2026-11-18, preview v1): the coach sent his own analysis screen recording with voice-over — use it as the diagnosis (his words, his lines) and as the side-by-side proof.
  v2: the face-on clips were the drill → "homework"; owner added the student's WhatsApp reply as a testimonial — always pixelate + blur the contact's name and photo.
  Delivered v5 (2026-11-19): title "60 MIN LESSON · before → after: 35 minit kemudian" (owner's figures). When the coach's voice says the student's name, cut around it (the transcript may hear it as another name).
- Teaser for the before & after (2026-11-19, `projects/ba-teaser/`, preview v1): 12 s cut-down in the same Film Slate look (series consistency beats a new look for a teaser of an existing video). Delivered from preview v1.

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **Kinrara recap (19 Nov, four-ball)** (branch `claude/gifted-davinci-2netbk`, `projects/kinrara-recap/`) | **Flight Pass**: tournament lanyard badges per player | Onest 800 + Spline Sans Mono 600 + Noto Color Emoji | card #fbfbf8, ink #15171a, charcoal+gold (coach), coral #e2452a, blue #1f7fd6, sand #e9c27a | badge drops on a coloured strap, clips in, sways, swings away; MASUK stamps on the holed putt; end "The squad" lineup of passes; real sound levelled, no music — **delivered from preview v1** (owner chose v1 over the hole-18-last v2) |

- Kinrara recap (2026-11-19): owner named who's who by clothing; the owner is labelled "Saya". Keep stamps/badges off faces when a golfer bends at the cup.
| **Kinrara recap — casual version** (`projects/kinrara-casual/`) | **Casual**: phone-story lowercase text, no panels | Lexend 600/400 + Noto Color Emoji | white + thin dark outline, pale lime #e6ff7a accent | simple fades, underlined names, one SFX; same cut as kinrara-recap v1 — **preview v1** |

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **Lesson montage — 3 students, no names** (`projects/lesson-1120/`) | **Polaroid**: finishes freeze into instant prints on a cork board | Albert Sans 800/600 + Gochi Hand + Noto Color Emoji | print white #fbfaf6, cork #2a241d, marker #20242b, tape #f3e7b8, tomato #ff5a3c | 1× swing → 0.5× impact → finish shrinks/tilts into a polaroid with a marker caption, shutter + print SFX, end board of three prints; noise-cleaned strikes, no music — **delivered from preview v2** (labels: single session · beginner lesson 2 · ayah saya) |

- Lesson montage (2026-11-20): three students, no names (owner) → "student 01/02/03". Keep the hook unzoomed when a title sits in the top band.

| Video | Look | Type | Palette | Motion signature |
| --- | --- | --- | --- | --- |
| **MIY GOLF Ep1 · Break 100 (voice-over explainer, no footage)** (`projects/break100-ep1/`) | **Range Map**: printed course-guide page, top-down diagrams | Hanken Grotesk 800/600 + Geist Mono 600 + Noto Color Emoji | paper #f3eee2, ink #141714, fairway #2f8a3e, light fairway #a8d68f, rough #6fae5a, flag red #e8412c | plotter-drawn dashed lines, flags pop, result dots stamp in per shot, red-pen strike/circle, green page sweep with a yardage stake between drills, ink caption strip; voice re-ordered for the hook; v2 delivered without music; v3 slow lo-fi bed (too sleepy, ducked) → **v4 continuous presentation bed: Mixkit 175 Digital Clouds, steady, voice ~13 dB on top** — preview v4; then **split into 3 weekly posts** (1/3 tee off 38 s, 2/3 punch 21 s, 3/3 lag putt 13 s) with a part tag in the header and next-part / recap end cards |
| **MIY GOLF Ep2 · Break 100 (bunker line / chip to towel / 1 m circle), split in 2 parts** (`projects/break100-ep2/`) | **Range Map, reused on request** ("ikut tema episod 1 yang paling awal tu … aku suka warna cream yellowish punya background"); v1 tried a new "Blueprint" look (cyanotype drafting sheet, Archivo + JetBrains Mono + Architects Daughter) — rejected | as Ep1: Hanken Grotesk 800/700 + Geist Mono + Noto Color Emoji | as Ep1: paper #f3eee2, ink #141714, fairway #2f8a3e, light fairway #a8d68f, flag red #e8412c, sand #e7d6a6 | as Ep1 (plotter-drawn diagrams, green page sweep with the yardage stake, ink caption strip) + Ep2 diagrams: bunker line + 5 cm dimension, towel landings, 6 balls on a 1 m ring, putt stat bars; part 1 ends "Like untuk part 2" — **delivered v2** |
| **Bunker shot — owner's script, ±40 s** (`projects/bunker-skrip/`) | **Label Maker**: embossed label-maker tapes print letter by letter, stick with a tilt, peel off per section | Oswald 600 uppercase + Gabarito 700 + Noto Color Emoji | tape black #1c1c1e, yellow #f6c514, red #d3262e, white #f1efe8; captions on a dark pill | stepped print reveal, back-out settle, peel-up exit; numbered set-up steps 01–03; red tape = the mistake; no music — **delivered v7** (0:25 shot = IMG_0413; ball-in-front-of-line in full + its shot; "grip ke logo" cut; landing shown: tracked 3x punch-in + ring on the ball right of the middle pin; ending highlights "Macam mana nak pukul bola plug?") |
| **Bola plug / fried egg — reply to the "BUNKER" comments** (`projects/bunker-plug/`) | **Label Maker, reused on purpose** (owner: "blend in dengan apa yang ada sekarang"; it is the bunker video's part 2) | as Bunker shot | as Bunker shot | opens on the bunker video's last question + KORANG KOMEN "BUNKER" tape; open face ✗ vs closed face ✓; slow-mo replay; end tape "Save. Cuba kat bunker" — **delivered v2** |
| **Early extension — owner's script, ±40 s** (`projects/early-extension/`) | **Posture Chart**: physio posture assessment — plumb line on the hips, red impact marker, chart rows, two-panel before/after sheet | Familjen Grotesk 700/600 + Reddit Mono 600 + Noto Color Emoji | chart white #f5f8f7, ink #13202b, teal #0e8c8f, marker red #e2483d | plumb line drops with a bounce bob, dashed marker scales in, arrow measures the hip move (measured: ~85 px before vs ~25 px after); rows: tab slide + wipe; drill = grip down (choke down); no music — preview v2 |

- Break 100 Ep1 (2026-11-23): owner sent a silent slide video + a separate voice-over → rebuild the slides in HyperFrames around the voice, hook line moved to the front, repeat dropped. Owner then asked to split the 1-min episode into 3 posts for one week: each part needs its own frame-0 hook (part 2 opens on its strongest line) and an end card pointing to the next part.
  v2 lesson: never trust transcript word ends for cuts (they can run 0.5 s early); measure the decay on the audio and keep the tail — the owner wants phrase endings heard clearly.
  v4 lesson: when the owner asks for background music on an explainer he means a continuous, upbeat-chill "presentation" bed at a steady level (light dip only), not a sleepy track with heavy ducking.
- Early extension (2026-11-25): script asked for a wall drill + talking heads the footage didn't have; show the script's lines as text and the drill that was filmed (chair), and say so. A before/after can be measured on the frames (back-of-hips pixel at address vs impact) when the camera is static.
- Bunker skrip (2026-11-24): the owner now writes the script; follow its shot order, use his recorded words where they exist and put the script's own lines on screen where no take says them. Talking-head framing can put the face LOW in frame — check per clip before placing text. Don't repeat a rule the coach mis-states ("penalty area"); cut the clause and show the correct rule from his script.
- Break 100 Ep2 (2026-11-23): same slide + voice-over format, split in 2 parts from the start. The recording's room noise was ~10 dB higher than Ep1, so silence/onset thresholds are set per recording (measure the floor first), and cut tails are capped at the next phrase's start (words can run together with no pause). The Break 100 series keeps Ep1's cream Range Map look (owner's call) — for this series, don't make a new look per episode.
