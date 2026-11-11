# Swing edit pipeline

Produces `output/swing_rating_edit.mp4` (1080x1920, 30fps, ~34s) from a phone clip of a golf swing.

1. Extract frames: `ffmpeg -i in.mov -q:v 2 all/f%04d.jpg`
2. Slow-mo frames (120fps interpolated from t=5.2s):
   `ffmpeg -ss 5.2 -t 1.9 -i in.mov -vf "minterpolate=fps=120:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" slow/s%04d.jpg`
3. Pose landmarks: MediaPipe Pose Landmarker (heavy) on every frame -> `work/pose.json`
4. `python3 render.py <workdir>` -> silent `work/video.mp4` (hook, slow-mo with skeleton + hand path, 4 freeze-frame cards, tempo, rating)
5. `ffmpeg -i in.mov -vn -ac 2 -ar 48000 work/orig.wav && python3 audio.py <workdir>` -> `work/audio.wav`
6. Mux: `ffmpeg -i work/video.mp4 -i work/audio.wav -c:v copy -c:a aac -b:a 192k -shortest out.mp4`

Swing timings (takeaway 5.43s, top 6.00s, impact 6.23s) and key frame indices are set at the top of `render.py`.
