#!/usr/bin/env python3
"""Writes index.html: the whole HyperFrames timeline (A-roll, trail-cam HUD, field-note tags, SFX) from one place.

Film times come from edit/timeline.json (tools/build_aroll.py). No speech in the takes, so every graphic and sound sits on a picture beat.
SFX start = picture beat - file peak (peak lands on the beat). No music (owner's call); the bird bed and crickets are ambience, not music.

Run from the project folder:  python3 tools/build_index.py
"""
import json, os
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
B = dict(TL["_beats"])
S = lambda n: TL[n]["start"]
E = lambda n: TL[n]["end"]
TOTAL = TL["_total"]

# ---- trail-cam clock: the phones' own record start (QuickTime creationdate, +08:00) + source time ----
REC = {1: datetime(2026, 11, 13, 8, 27, 29), 2: datetime(2026, 11, 13, 8, 27, 57)}
import importlib.util
spec = importlib.util.spec_from_file_location("ar", os.path.join(ROOT, "tools", "build_aroll.py")); AR = importlib.util.module_from_spec(spec); spec.loader.exec_module(AR)
CLOCK = []   # [film_start, film_end, src_start_epoch_s, rate]  (rate<0 = rewind, 0 = freeze)
for s in AR.EDL:
    t0, t1 = S(s["name"]), E(s["name"])
    base = (REC[s["clip"]] - REC[2]).total_seconds()
    if s.get("kind") == "freeze":
        CLOCK.append([t0, t1, base + s["a"], 0])
    elif s.get("kind") == "rev":
        CLOCK.append([t0, t1, base + s["b"], -s["speed"]])
    else:
        CLOCK.append([t0, t1, base + s["a"], s["speed"]])
CLOCK = [[round(a, 4) for a in c] for c in CLOCK]

# setup stopwatch: from the address (src 5.5) to the take-away (src 21.6) = 16 s
ADDRESS_SRC, TAKEAWAY_SRC = 5.5, 21.6

# ---- positions measured on the A-roll (film px) ----
FLAG = (524, 362)          # flag on the green at src 2.83 (lie_flag); the handheld camera drifts down after it -> FLAGK track (src t, x, y)
FLAGK = [(2.83, 524, 362), (2.90, 512, 386), (2.97, 512, 402), (3.10, 530, 436), (3.23, 522, 446), (3.40, 520, 462)]
TURF = (421, 1060)         # turf chunk in the replay (12.3-12.9)

# ---- SFX: file -> (peak s, usable length s) ----  Mixkit ids, see assets/sfx/CREDITS.md
SFX = {
    "1430.mp3": (0.14, 0.40), "1440.mp3": (0.17, 0.62), "1092.mp3": (0.30, 1.05), "1096-ff.mp3": (0.0, 2.2),
    "2121.mp3": (0.14, 0.40), "753.mp3": (0.06, 0.47), "2498.mp3": (0.17, 0.50), "1119.mp3": (0.15, 0.25),
    "2364.mp3": (0.01, 0.14), "772.mp3": (0.41, 0.75), "27.mp3": (0.25, 0.85), "166.mp3": (0.30, 0.60),
    "39.mp3": (0.00, 1.20),
}
TAG_T = {"lie_note": S("lie") + 0.22, "flag": B["lie_flag"] + 0.04, "spec": S("walk") + 0.55, "ff_note": S("ff") + 0.15,
         "stare": B["shot_stare"] + 0.18, "turf": B["replay_impact"] + 0.32, "pog": S("laugh") + 0.62, "end": S("end_freeze")}
CUES = [
    (0.03, "1119.mp3", 0.30, "title types on, frame 0"),
    (0.22, "1119.mp3", 0.22, "title line 2"),
    (B["hook_impact"], "2121.mp3", 0.38, "strike layer (0.5x)"),
    (B["hook_impact"] + 0.02, "753.mp3", 0.55, "turf thud: the chunk"),
    (B["hook_turf"], "1430.mp3", 0.55, "trail-cam shutter on the freeze"),
    (B["hook_turf"] + 0.01, "772.mp3", 0.22, "freeze weight under the flash"),
    (B["hook_turf"] + 0.38, "2364.mp3", 0.30, "TERTANGKAP stamp"),
    (S("rew") + 0.30, "1092.mp3", 0.42, "tape rewind over the setup"),
    (S("lie") + 0.01, "1440.mp3", 0.30, "tape stops: play clunk"),
    (TAG_T["lie_note"] + 0.05, "1119.mp3", 0.26, "habitat note"),
    (TAG_T["lie_note"] + 0.55, "2364.mp3", 0.22, "lie tick"),
    (TAG_T["flag"], "2364.mp3", 0.26, "flag ring"),
    (TAG_T["spec"] - 0.02, "166.mp3", 0.30, "specimen tag swings in"),
    (TAG_T["spec"] + 0.26, "1430.mp3", 0.35, "trail cam triggers (TRIG 002)"),
    (S("ff") + 0.02, "1096-ff.mp3", 0.45, "reel fast-forward whirr"),
    (TAG_T["ff_note"] + 0.05, "1119.mp3", 0.22, "observation note"),
    (B["shot_takeaway"], "2364.mp3", 0.26, "stopwatch stops at the take-away"),
    (B["shot_impact"], "2121.mp3", 0.30, "strike layer"),
    (B["shot_impact"] + 0.02, "753.mp3", 0.62, "turf thud"),
    (B["shot_impact"] + 0.48, "27.mp3", 0.22, "a bird squeaks at it"),
    (B["shot_stare"] + 0.05, "39.mp3", 1.0, "crickets through the stare"),
    (S("replay") - 0.02, "166.mp3", 0.32, "whip into the replay"),
    (B["replay_impact"], "2121.mp3", 0.30, "replay strike layer"),
    (B["replay_impact"] + 0.02, "2498.mp3", 0.40, "replay thud"),
    (TAG_T["turf"] + 0.05, "1119.mp3", 0.24, "turf label"),
    (TAG_T["pog"], "1119.mp3", 0.24, "Part of"),
    (TAG_T["pog"] + 0.28, "1119.mp3", 0.24, "the game."),
    (TAG_T["end"], "1440.mp3", 0.50, "shutter: the laugh captured"),
    (TAG_T["end"] + 0.36, "1119.mp3", 0.24, "entry card"),
    (TAG_T["end"] + 0.66, "1119.mp3", 0.20, "definition"),
    (TAG_T["end"] + 0.96, "1119.mp3", 0.20, "status"),
    (TAG_T["end"] + 1.20, "2364.mp3", 0.28, "CTA tag"),
]
# ambience beds (not music): birds under the picture, ducked under the rewind / fast-forward
BEDS = [  # (start, end, file, media start, vol)
    (0.0, S("rew"), "1210-bed.mp3", 0.0, 0.30),
    (S("lie"), S("ff"), "1210-bed.mp3", 2.0, 0.42),
    (S("ff"), S("shot"), "1210-bed.mp3", 4.0, 0.14),
    (S("shot"), B["shot_stare"], "1210-bed.mp3", 6.5, 0.42),
    (S("replay"), TOTAL, "1210-bed.mp3", 9.0, 0.36),
]


def audio_tags():
    L = [f'      <audio data-hf-id="hf-voice" id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" '
         f'data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>',
         "      <!-- ambience beds (Mixkit 1210 forest birds; not music) -->"]
    for i, (a, b, f, ms, v) in enumerate(BEDS):
        L.append(f'      <audio data-hf-id="hf-bed{i}" id="bed-{i}" class="clip" src="assets/sfx/{f}" data-start="{a:.3f}" data-duration="{b - a:.3f}" '
                 f'data-media-start="{ms:.2f}" data-track-index="11" data-volume="{v}" data-audio-group="sfx"></audio>')
    L.append("      <!-- sound design: Mixkit ids (assets/sfx/CREDITS.md). start = picture beat - file peak. No music. -->")
    busy = {}
    for i, (beat, f, vol, note) in enumerate(sorted(CUES)):
        peak, length = SFX[f]
        st = beat - peak; ms = 0.0
        if st < 0: ms += -st; length += st; st = 0.0
        length = min(length, TOTAL - st)
        trk = next(k for k in range(12, 60) if busy.get(k, -1) <= st)
        busy[trk] = st + length
        mattr = f' data-media-start="{ms:.3f}"' if ms > 0 else ""
        L.append(f'      <audio data-hf-id="hf-s{i:02d}" id="sfx-{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{st:.3f}" '
                 f'data-duration="{length:.2f}"{mattr} data-track-index="{trk}" data-volume="{vol}" data-audio-group="sfx"></audio> <!-- {note} -->')
    return "\n".join(L)


def main():
    tpl = open(os.path.join(ROOT, "tools", "index.template.html")).read()
    consts = {"T": {k: v for k, v in TL.items() if not k.startswith("_")}, "B": B, "TOTAL": TOTAL, "CLOCK": CLOCK,
              "REC0": REC[2].strftime("%Y-%m-%dT%H:%M:%S"), "ADDR": ADDRESS_SRC, "TAKE": TAKEAWAY_SRC, "TAG": {k: round(v, 3) for k, v in TAG_T.items()},
              "FLAG": FLAG, "TURF": TURF,
              "FLAGK": [[round(S("lie_flag") + (t - 2.50), 3), x - FLAG[0], y - FLAG[1]] for t, x, y in FLAGK]}
    out = (tpl.replace("{{TOTAL}}", str(TOTAL)).replace("{{AUDIO}}", audio_tags())
              .replace("{{CONSTS}}", json.dumps(consts, ensure_ascii=False)))
    for k, v in {"FX": FLAG[0], "FY": FLAG[1], "TX": TURF[0], "TY": TURF[1]}.items():
        out = out.replace("{{" + k + "}}", str(v))
    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print("index.html written:", len(CUES), "sfx cues, total", TOTAL)
    for k, v in TAG_T.items():
        print(f"  {k:9} {v:6.2f}")


if __name__ == "__main__":
    main()
