# Swing edit pipeline

Produces a 1080x1920 30fps swing-analysis edit (~33s) from a phone clip of a golf swing.
Each swing has a config in `configs/` (timings, key frames, card text, scores):

- `configs/swing1.json` -> `output/swing_rating_edit.mp4`
- `configs/swing2.json` -> `output/my_swing_rating_edit.mp4`

1. Extract frames: `ffmpeg -i in.mov -vf scale=1080:1920 -q:v 2 all/f%04d.jpg`
2. Slow-mo frames (120fps interpolated from config `slow.t0`):
   `ffmpeg -ss <t0> -t <len> -i in.mov -vf "minterpolate=fps=120:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" slow/s%04d.jpg`
3. Pose landmarks: MediaPipe Pose Landmarker (heavy) on every frame -> `work/pose.json`
4. `python3 render.py configs/<swing>.json <workdir>` -> silent `work/video.mp4` (hook, slow-mo with skeleton + hand path, 4 freeze-frame cards, tempo, rating)
5. `ffmpeg -i in.mov -vn -ac 2 -ar 48000 work/orig.wav && python3 audio.py <workdir>` -> `work/audio.wav`
6. Mux: `ffmpeg -i work/video.mp4 -i work/audio.wav -c:v copy -c:a aac -b:a 192k -shortest out.mp4`

Text in configs can use `{addr_angle}`, `{imp_angle}`, `{angle_loss}`, `{rknee_addr}`, `{rknee_top}`, `{bs}`, `{ds}`, `{ratio}`,
which are computed from the pose data.
