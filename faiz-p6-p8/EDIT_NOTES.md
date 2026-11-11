# Edit notes — Before vs After, P6–P8 (Faiz)

Separate short (17.87 s, 1080×1920) in a "lab / telestrator" style: graphite grid, red = before, lime = after,
Archivo Black + JetBrains Mono.

- **Before**: clip B (`1794273769635.mov`), first full swing of the lesson, impact at frame 1224 (≈40.80 s).
- **After**: clip C (`1794276442263.mov`, 60 min later), impact at frame 178 (≈5.93 s).
- Both panels are frame-locked on impact: P6 = P7−1, P7 = impact, P8 = P7+2 (30 fps source).
- Panels: crop 700×1244 (B at x230 y600, C at x180 y676) → 540×960 each, side by side at y=330.

| At (s) | Beat |
|---|---|
| 0.00–1.60 | hook: both panels frozen on P7 impact, NAMPAK BEZA?, shaft lines + ball rings |
| | (all beats below are +1.60 s in the final film) |
| 0.00–2.63 | real-time swing, BEFORE vs AFTER title |
| 2.63–3.17 | rewind 3× |
| 3.17–5.07 | slow-mo 0.25× (MCI interpolation) to P6 |
| 5.07–6.67 | P6 hold + shaft lines + horizontal reference |
| 6.77–8.57 | P7 impact hold + shaft lines + ball ring/line |
| 8.80–10.40 | P8 hold + shaft lines + horizontal reference |
| 10.40–13.07 | slow-mo follow-through, then real time |
| 13.07–16.27 | outro: 60 MINIT · P6 → P8 · SHIFT KE KIRI / HIT DOWN |

Build script for the panel footage: frame-indexed pieces (real, reverse, interpolated, holds) concatenated per clip, then `hstack`.
No speech and no music in this edit (music removed on request); SFX only.
