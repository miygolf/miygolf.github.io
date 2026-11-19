# Kinrara recap — edit notes

Drive folder 1JaOAR5R1cVyvUQVPdNlqJBex6J4nSiA_ (19 Nov 2026, Kinrara Golf Club). 33.9 s, no speech in any clip, no music.
Players (owner): **Coach Reza** = black shirt · **Kimi** = blue + navy bucket hat · **Saya** (owner) = blue patterned shirt + black cap · **Taza** = white bucket hat.

**Look: "Flight Pass"** — tournament lanyard badges: each player's swing gets a badge that drops on its strap (player colour), clips in and sways,
then swings away; MASUK stamps on the holed putt; end card "The squad" with the four passes. Onest 800 + Spline Sans Mono 600 + Noto Color Emoji.
Card #fbfbf8, ink #15171a, Reza charcoal #1b1b1b + gold #ffc93c, Saya coral #e2452a, Kimi blue #1f7fd6, Taza sand #e9c27a (white text needs ≥3:1).

| film | clip | what |
| --- | --- | --- |
| 0.00–2.90 | IMG_0344 | hook: the putt dropping 0.5× (ball in at 2.85), freeze; "Recap hari ni" title on frame 0, MASUK stamp |
| 2.90–14.67 | c1_1..4 | tee: Coach Reza, Saya, Taza, Kimi ("Tee shot") |
| 14.67–23.20 | c2_1..4 | next tee: Taza, Coach Reza, Kimi, Saya |
| 23.20–26.30 | IMG_0338 | **Hole 18** (owner): Saya, approach |
| 26.30–30.70 | IMG_0344 | Hole 18 putt at 1×: rolls in, picks it out; "Hole 18: MASUK! ⛳" |
| 30.70–33.90 | IMG_0344 | Saya walking off the green, freeze; "The squad" lineup |

Where tee shots landed is not visible (wide tee cams): no claims about results.
Build: `tools/fetch.sh`, `python3 tools/build_aroll.py`, `python3 tools/build_index.py`, check, render, `tools/master.sh`.

## v2 (owner: "vid iphone tu hole 18")
The iPhone approach + putt are hole 18 → moved to the end so the round closes on the holed putt; badges "Hole 18 · Approach / Putt".
The compose_video tee clips carry their export time (after the round), so their badges just say "Tee shot".

## Delivery
Owner chose **v1** ("render v1", 2026-11-19): original order (hole 18 approach + putt first, then the tee shots) with times on the badges.
The v1 tool files were restored from git (commit 3211098) and rendered. `final/kinrara-recap_1080x1920.mp4`: 33.9 s, 1080×1920, 30 fps,
H.264 High ~12.7 Mbps, AAC 256k, −14.0 LUFS, −2.9 dBTP. v2 (hole 18 last) stays in git history and previews/.
