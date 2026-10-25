# Source

- Google Drive folder of 2026-10-25 (owner's upload). Used:
  - `VID_20261024_080247.mp4` — 62 Breakfast Club / 62 Grillstreet walk-out, 3840×2160 rotated, 60 fps, 9.8 s.
    Trimmed to 0–8.4 s (after 8.4 s the camera pans to the closed neighbour "Taugedel") and transcoded:
    `ffmpeg -i <src> -t 8.4 -vf scale=1080:1920:flags=lanczos,format=yuv420p -r 60 -c:v libx264 -crf 18 -g 30 -c:a aac assets/footage/shop.mp4`
  - `VID-20261025-WA0014.mp4` — slow pan over the Big Breakfast tray, 720×1280, 4.5 s → upscaled to `assets/footage/plate-pan.mp4`.
  - `IMG-20261025-WA0013.jpg` (the linked file) — the plated Big Breakfast → `assets/stills/plate.jpg`.
  - `assets/stills/menu.jpg` — full-res frame of the menu board at src 0.3 s of the shop clip.
- Not used: `VID_20261025_150916.mp4`, `VID_20261025_154706.mp4` (golf range swings, unrelated to the shop).
- Transcript: none usable. whisper large-v3 (`ms` and auto) returned "Terima kasih kerana menonton" /
  "I'm going to take a walk in the park" stretched evenly over each clip — the standard silence
  hallucination. The clips carry only ambience, so the edit is cut on picture beats and the music grid.
- Menu prices read from the board: The Big Breakfast set RM21.90 (ala carte RM18.90);
  Scrambled Egg Sandwich ala carte RM7.90 (lowest main on the board).
- Music: Mixkit "Motivating Mornings" (id 33, Mixkit free licence), 121 BPM, drop at track 12.09 s,
  entered at 9.092 s so the drop lands on video 3.0 s.
- SFX: Mixkit (free licence), ids are the file names in `assets/sfx/`.
- Fonts: Fredoka (variable) and Space Mono 700, Google Fonts (OFL), in `assets/fonts/`.
- Split-flap mechanism adapted from the registry block `split-flap-board`.
