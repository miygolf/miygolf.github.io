# Chipping: backswing jangan terlebih — HyperFrames edit

Vertical 1080×1920, 27 s. Source: `src/raw.mp4` (52 s).

## Design: "Fairway Notes"
Different from the source's earlier edit (white all-caps captions with blue word boxes):
- Dark fairway-green glass **caption deck** at the top (y 164–456) that also hides the
  source's burned-in subtitles; chapter tag + 01/04 counter + lime progress bar.
- Sentence-case Outfit 800 captions, karaoke dim→full, key words in Playfair Display
  italic lime.
- Cream "yardage book" side cards (x 626–950, y 846–1300) — right of the golfer, never on the face,
  clear of TikTok/IG top bar, right rail and bottom caption zone.
- Palette: ink #0b2b1e, cream #f5f0e1, lime #d4ff3a (alignment sticks), signal #e8361f.
- Fonts: Outfit, Playfair Display, League Gothic, JetBrains Mono.

## Build
```
python3 tools/build_edit.py      # cut raw → assets/edit.mp4
python3 tools/build_captions.py  # captions deck
python3 tools/build_scenes.py    # graphics scenes
python3 tools/build_index.py     # root: punch-ins, music, SFX
npx hyperframes check && npx hyperframes render -q delivery -o renders/final-raw.mp4
# then two-pass ffmpeg loudnorm to -14 LUFS / -1.5 dBTP (video stream copied)
```
