"""Builds index.html from the edit decision list below.

Footage proxies live in assets/footage/{A..E}.mp4 (see tools/prepare_footage.sh).
Source clips, in shooting order: A (pour chili paste), B (stir paste),
D (kangkung in), C (sauces + tomato), E (plated + the two bottles).
Run: python3 tools/build_index.py
"""

from pathlib import Path

# id, source, media start (s), output duration (s), playback rate, has audio
EDL = [
    ("v01", "E", 1.00, 1.50, 1.0, True),   # hook: plate pushed to camera
    ("v02", "A", 12.10, 3.20, 1.0, True),  # chili paste hits the oil, steam burst
    ("v03", "A", 44.00, 1.50, 8.0, False), # timelapse: frying until the oil splits
    ("v04", "A", 65.20, 2.20, 1.0, True),  # first stir, steam
    ("v05", "B", 6.60, 3.00, 1.0, True),   # stir hard
    ("v06", "D", 10.40, 2.60, 1.0, True),  # kangkung drops in
    ("v07", "D", 15.00, 1.60, 1.5, True),  # second handful
    ("v08", "C", 10.20, 1.40, 1.0, True),  # secret #1: Tiparos fish sauce to camera
    ("v09", "C", 12.80, 1.60, 1.0, True),  # pour
    ("v10", "C", 19.50, 1.40, 1.0, True),  # secret #2: Golden Mountain
    ("v11", "C", 25.80, 2.60, 1.0, True),  # toss
    ("v12", "C", 37.90, 1.80, 1.0, True),  # tomato last
    ("v13", "E", 0.30, 3.10, 1.0, True),   # payoff: plate hero
    ("v14", "E", 6.90, 3.10, 1.3, True),   # the two bottles land
    ("v15", "E", 10.95, 3.45, 1.0, True),  # CTA hold
]

# id, file, start, duration, volume, media start, fade in, fade out
SFX = [
    ("sx-swish-1", "swish", 1.45, 0.33, 0.55, 0, 0, 0.05),
    ("sx-sizzle-1", "sizzle", 1.66, 1.90, 0.55, 0, 0, 0.6),
    ("sx-pop-1", "pop", 1.66, 0.20, 0.45, 0, 0, 0),
    ("sx-pop-2", "pop", 2.06, 0.20, 0.5, 0, 0, 0),
    ("sx-pop-3", "pop", 2.36, 0.20, 0.45, 0, 0, 0),
    ("sx-print-1", "printer-a", 3.3, 1.00, 0.4, 0.22, 0, 0.2),
    ("sx-whoosh-1", "whoosh-short", 4.55, 0.57, 0.45, 0, 0, 0),
    ("sx-sizzle-2", "sizzle", 4.70, 1.50, 0.4, 0.15, 0.1, 0.4),
    ("sx-marker-1", "marker", 4.90, 0.80, 0.45, 0, 0, 0.1),
    ("sx-tear-1", "tear-b", 8.32, 0.70, 0.45, 0, 0, 0.25),
    ("sx-print-2", "printer-b", 8.48, 1.00, 0.4, 0.05, 0, 0.25),
    ("sx-scribble-1", "scribble", 8.90, 1.10, 0.35, 0.1, 0, 0.3),
    ("sx-whoosh-2", "whoosh-deep", 10.90, 1.40, 0.4, 0, 0, 0.4),
    ("sx-punch-1", "punch", 11.80, 0.60, 0.6, 0, 0, 0.1),
    ("sx-tear-2", "tear-a", 11.67, 0.90, 0.4, 0.3, 0, 0.3),
    ("sx-print-3", "printer-a", 12.15, 1.00, 0.4, 0.22, 0, 0.2),
    ("sx-marker-2", "marker", 12.45, 0.80, 0.45, 0, 0, 0.1),
    ("sx-swish-2", "swish", 15.55, 0.33, 0.55, 0, 0, 0.05),
    ("sx-tear-3", "tear-b", 15.62, 0.70, 0.45, 0, 0, 0.25),
    ("sx-print-4", "printer-b", 15.78, 1.00, 0.4, 0.05, 0, 0.25),
    ("sx-pop-4", "pop", 15.95, 0.20, 0.55, 0, 0, 0),
    ("sx-tear-4", "tear-a", 18.42, 0.90, 0.4, 0.3, 0, 0.3),
    ("sx-print-5", "printer-a", 18.90, 1.00, 0.4, 0.22, 0, 0.2),
    ("sx-pop-5", "pop", 19.15, 0.20, 0.55, 0, 0, 0),
    ("sx-whoosh-3", "whoosh-short", 19.85, 0.57, 0.45, 0, 0, 0),
    ("sx-tear-5", "tear-b", 22.55, 0.70, 0.45, 0, 0, 0.25),
    ("sx-print-6", "printer-b", 22.70, 1.00, 0.4, 0.05, 0, 0.25),
    ("sx-riser", "riser", 21.70, 2.70, 0.4, 1.66, 0.4, 0),
    ("sx-pop-6", "pop", 22.82, 0.20, 0.45, 0, 0, 0),
    ("sx-pop-7", "pop", 22.92, 0.20, 0.4, 0, 0, 0),
    ("sx-pop-8", "pop", 23.02, 0.20, 0.45, 0, 0, 0),
    ("sx-marker-3", "marker", 23.25, 0.80, 0.45, 0, 0, 0.1),
    ("sx-tear-6", "tear-a", 24.05, 0.90, 0.4, 0.3, 0, 0.3),
    ("sx-stamp", "stamp", 25.52, 0.58, 0.75, 0, 0, 0.05),
    ("sx-bell", "bell", 25.70, 2.40, 0.5, 0, 0, 0.8),
    ("sx-whoosh-4", "whoosh-trans", 26.05, 1.50, 0.35, 0.5, 0, 0.1),
    ("sx-marker-4", "marker", 28.05, 0.80, 0.45, 0, 0, 0.1),
    ("sx-marker-5", "marker", 30.20, 0.80, 0.45, 0, 0, 0.1),
    ("sx-print-7", "printer-a", 30.62, 1.10, 0.4, 0.22, 0, 0.25),
    ("sx-stamp-2", "stamp", 31.82, 0.58, 0.55, 0, 0, 0.05),
    ("sx-pop-9", "pop", 32.45, 0.20, 0.5, 0, 0, 0),
]

MUSIC_START = 40.0  # into "Cool Cool Bossa", past the quiet intro
MUSIC_VOLUME = 0.13

total = round(sum(d for _, _, _, d, _, _ in EDL), 2)


def fmt(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


videos = []
t = 0.0
for i, (vid, src, ms, dur, rate, audio) in enumerate(EDL):
    sound = 'data-has-audio="true" data-volume="1" data-fade-in="0.03" data-fade-out="0.04"' if audio else "muted"
    rate_attr = f' data-playback-rate="{fmt(rate)}"' if rate != 1.0 else ""
    videos.append(
        f'        <video id="{vid}" class="clip shot" src="assets/footage/{src}.mp4" playsinline {sound}\n'
        f'          data-start="{fmt(t)}" data-duration="{fmt(dur)}" data-media-start="{fmt(ms)}"{rate_attr}\n'
        f'          data-track-index="0"></video>'
    )
    t = round(t + dur, 2)

audios = [
    f'    <audio id="music" class="clip" src="assets/music/cool-cool-bossa.mp3" data-start="0" '
    f'data-duration="{fmt(total)}" data-media-start="{fmt(MUSIC_START)}" data-volume="{MUSIC_VOLUME}" '
    f'data-fade-in="0.2" data-fade-out="1.2" data-track-index="10"></audio>'
]
lanes = []  # end time per lane
for sid, f, st, dur, vol, ms, fi, fo in sorted(SFX, key=lambda r: r[2]):
    lane = next((i for i, end in enumerate(lanes) if end <= st), None)
    if lane is None:
        lanes.append(0)
        lane = len(lanes) - 1
    lanes[lane] = st + dur
    extra = ""
    if ms:
        extra += f' data-media-start="{fmt(ms)}"'
    if fi:
        extra += f' data-fade-in="{fmt(fi)}"'
    if fo:
        extra += f' data-fade-out="{fmt(fo)}"'
    audios.append(
        f'    <audio id="{sid}" class="clip" src="assets/sfx/{f}.mp3" data-start="{fmt(st)}" '
        f'data-duration="{fmt(dur)}" data-volume="{vol}"{extra} data-track-index="{11 + lane}"></audio>'
    )

template = Path(__file__).with_name("index.template.html").read_text()
out = (
    template.replace("{{TOTAL}}", fmt(total))
    .replace("{{VIDEOS}}", "\n".join(videos))
    .replace("{{AUDIO}}", "\n".join(audios))
)
Path(__file__).resolve().parent.parent.joinpath("index.html").write_text(out)
print("index.html written, duration", total)
