"""Edit decision list for the 8-iron practice session workout-style video.

Everything is laid out on a ~128.6 BPM grid so every cut lands on a bar line
and every real-time impact lands on a beat.
"""

FPS = 30
BEAT_FRAMES = 14         # ~128.6 BPM: every beat, bar and cut is a whole frame
BEAT = BEAT_FRAMES / FPS
BAR = 4 * BEAT
BPM = 60 / BEAT
W, H = 1080, 1920

# Visually verified impact frames (seconds into each source clip).
SOURCES = {
    "dtl1": ("VID_20261028_130606.mp4", 4.45),
    "dtl2": ("VID_20261028_132845.mp4", 6.15),
    "fo1": ("VID_20261028_130630.mp4", 6.79),
    "fo2": ("VID_20261028_132901.mp4", 5.34),
    "s95": ("VID_20261028_142056.mp4", 5.05),
    "s96": ("VID_20261028_142056.mp4", 24.56),
    "s97": ("VID_20261028_142056.mp4", 61.97),
    "s98": ("VID_20261028_142056.mp4", 79.97),
    "s99": ("VID_20261028_142056.mp4", 98.24),
}

# Launch monitor (8 Iron) read off the screen filmed at ~89 s in VID_142056.
# The four swings filmed before that shot are #95-#98; #99 was hit after.
CARRY = {"s95": 133, "s96": 147, "s97": 107, "s98": 150, "s99": None}
GOOD_CARRY = 140  # within ~7% of the session best (150 yds) counts as ✓

MOVEMENTS = [
    {"name": "DOWN-THE-LINE SWING", "short": "Down-the-Line Swing", "reps": ["dtl1", "dtl2"]},
    {"name": "FACE-ON SWING", "short": "Face-On Swing", "reps": ["fo1", "fo2"]},
    {"name": "PAUSE AT TOP DRILL", "short": "Pause at Top Drill", "drill": True},
    {"name": "FULL SWING 8\u00a0IRON", "short": "Full Swing 8 Iron", "reps": ["s95", "s96", "s97", "s98", "s99"]},
]

DRILL_SRC = "VID_20261028_142056.mp4"
DRILL_START = 49.95          # 2 bars of real time from here
DRILL_HOLD = (51.0, 52.85)   # club held at the top
MONITOR_START = 89.0         # 1 bar on the launch monitor screen
SUMMARY_BARS = 4

REAL_IMPACT_AT = 5 * BEAT    # impact lands on beat 6 of the 2-bar rep
SLOW_IMPACT_AT = 2 * BEAT    # and on beat 3 of the 1-bar slow-mo replay


def mark_for(key):
    c = CARRY.get(key)
    if c is None:
        return None
    return "ok" if c >= GOOD_CARRY else "bad"


def build():
    """Return list of segments with output start times filled in."""
    segs = []
    t = 0.0

    def add(**kw):
        nonlocal t
        kw["t0"] = t
        segs.append(kw)
        t += kw["dur"]

    # Intro: best shot (#98) in slow motion behind the title.
    src, imp = SOURCES["s98"]
    add(kind="intro", src=src, ss=imp - 6 * BEAT * 0.5, speed=0.5, dur=2 * BAR, impact=6 * BEAT)

    for mi, mv in enumerate(MOVEMENTS):
        if mv.get("drill"):
            add(kind="title", mi=mi, src=DRILL_SRC, ss=DRILL_START - BAR, speed=1, dur=BAR)
            add(kind="drill", mi=mi, src=DRILL_SRC, ss=DRILL_START, speed=1, dur=2 * BAR,
                hold=(DRILL_HOLD[0] - DRILL_START, DRILL_HOLD[1] - DRILL_START))
            continue
        n = len(mv["reps"])
        for ri, key in enumerate(mv["reps"]):
            src, imp = SOURCES[key]
            real_ss = imp - REAL_IMPACT_AT
            if ri == 0:
                add(kind="title", mi=mi, src=src, ss=real_ss - BAR, speed=1, dur=BAR)
            common = dict(mi=mi, rep=ri + 1, nreps=n, key=key, mark=mark_for(key), carry=CARRY.get(key))
            add(kind="rep", src=src, ss=real_ss, speed=1, dur=2 * BAR, impact=REAL_IMPACT_AT, **common)
            add(kind="slow", src=src, ss=imp - SLOW_IMPACT_AT * 0.5, speed=0.5, dur=BAR,
                impact=SLOW_IMPACT_AT, **common)
            if key == "s98":
                add(kind="monitor", mi=mi, src=DRILL_SRC, ss=MONITOR_START, speed=1, dur=BAR)

    add(kind="summary", src=SOURCES["s98"][0], ss=SOURCES["s98"][1] + 0.9, speed=1, dur=SUMMARY_BARS * BAR)
    return segs, t


if __name__ == "__main__":
    segs, total = build()
    for s in segs:
        print(f"{s['t0']:7.3f} {s['dur']:6.3f} {s['kind']:8s} {s.get('key', s.get('mi', ''))} ss={s['ss']:.3f}")
    print("total", total, "bars", total / BAR)
