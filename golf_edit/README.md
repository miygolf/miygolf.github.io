# Golf workout edit

Turns the 8-iron practice clips (Drive folder, `VID_20261028_*.mp4`) into a
workout-style vertical video (1080×1920, 30 fps, 75 s):

- movement name banner at the top, with a rep counter (or a hold timer for the drill)
- every rep in real time, then a 0.5× slow-mo replay
- ✓ / ✗ on the full swings, judged from the launch monitor carry
  (✓ at 140+ yds, session best 150 yds)
- synthesised ~128.6 BPM track (14 frames per beat); every cut is on a bar line and every impact on a beat,
  with the real club-on-ball sound layered in
- closing summary screen with all four movements

```
python3 build.py /path/to/clips out.mp4 --work work/   # add --reuse to keep rendered segments
python3 timeline.py                                    # print the edit decision list
```

Needs ffmpeg, numpy, scipy, Pillow and the Inter Display fonts.
The edit points (impact times, drill hold, monitor shot) live in `timeline.py`.
