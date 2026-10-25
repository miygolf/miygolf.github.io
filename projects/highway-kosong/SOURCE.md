# Source

- Footage: `compose_video_1792315752276.mp4` (Google Drive, id `1woOWNmyArRHVyBBa_t9Edk1DySmUyKRh`),
  2160×3840 HEVC, 47.8 s. Transcoded to 1080×1920 H.264 (`-crf 17 -g 30`) at `assets/raw.mp4`
  before previewing or rendering (not committed, 144 MB):
  `ffmpeg -i <source> -vf scale=1080:1920:flags=lanczos,format=yuv420p -c:v libx264 -crf 17 -g 30 -c:a aac -b:a 192k assets/raw.mp4`
- Transcript: none usable. The audio is engine and wind only (no speech); whisper large-v3 in both
  `ms` and auto mode returned repeated hallucinated lines, so the edit is cut on picture beats.
- Shots in the source: 0–8.9 group ride, 8.9–20.8 empty straight, 20.9–30 stop at a junction,
  30–38.5 360 selfie (rider's helmet within x 0–700, y 480–1100), 39.5–47.8 back on the highway.
- Sound: the footage's own engine/wind is the bed (0.45 per scene). SFX from Mixkit (free licence),
  ids in `assets/sfx/<id>.mp3`.
- Final mix: `render -q delivery`, then two-pass `loudnorm=I=-14:TP=-1.5:LRA=11:linear=true` with the
  video stream copied (≈ −14.5 LUFS, peak ≈ −1.2 dBFS).
- Fonts: Overpass (variable) and Barlow Condensed italic 800/900, Google Fonts (OFL), in `assets/fonts/`.
