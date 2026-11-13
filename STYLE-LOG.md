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
