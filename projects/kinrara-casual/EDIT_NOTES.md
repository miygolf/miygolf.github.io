# Kinrara recap — casual version

Owner: "lepas tu buat style lain casual simple" after delivering `projects/kinrara-recap` (v1). Same cut (v1 order: hole 18 approach + holed putt,
then both tees, end on the walk-off), new treatment:

**Look: "Casual"** — like a friend's phone story: small lowercase Lexend 600/400 in white with a thin dark outline and soft shadow, a soft dark
gradient at the top only while text is up there, a thin underline under each name, simple fades; "masuk 🙌" in pale lime on both drops.
No panels, no badges, no stamps. Hard cuts, real sound levelled, one SFX (ball drop ×2), no music. Labels: "coach reza / saya / kimi / taza",
"hole 18 · approach / putt", "tee shot". End: "coach reza · kimi / taza · saya 🤝 — jumpa round depan". 33.9 s.
Build: as kinrara-recap (same `tools/build_aroll.py`); `tools/build_index.py` + `tools/index.template.html` are this version's.

## v2 (owner: "remove background noises")
No speech, so the bed can go: highpass 180 Hz + lowpass 9 kHz, two passes of afftdn (noise-tracking nr 30, then nr 20), and a gate that opens only
for strikes / the ball in the cup (range −30 dB). Noise floor in the mastered mix fell ~25 dB; strikes and the putt are kept.
