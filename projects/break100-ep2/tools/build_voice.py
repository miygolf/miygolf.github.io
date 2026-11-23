#!/usr/bin/env python3
"""Builds the voice-over track for MIY GOLF Ep2 "Break 100" (bunker / chip / 1 m circle) from the owner's recording (.src/vo.wav, 89 s).

Same cutting rules as Ep1 (owner: "jangan potong yang hujung-hujung, bagi dengar jelas"): every cut measured on the audio, phrase endings
kept with their decay + tail, fades only over silence, only pauses > 0.55 s shortened. This recording's room noise sits at about -46 dBFS
(Ep1: -55), so "silence" here is < -43 dBFS and an onset is > -36 dBFS.
Removed: the stray "Ok. Ok." (75.6-76.7 s) between the stat and the CTA, and the room noise / breath before "Episod" (0-2.6 s).
Split into parts by part.json (tools/make_parts.py). Word times: faster-whisper large-v3 + crop re-runs (edit/vo_words.json).
Writes assets/voice.wav (-16 LUFS) and edit/voice_map.json. Run from the project folder: python3 tools/build_voice.py
"""
import json, os, subprocess, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
GAP = 0.32

# (key, src_start, src_end, text) - src times in the recording (measured on the audio + crop transcripts)
PIECES = [
    ("hook", 4.44, 8.22, "Kau pernah tak masuk bunker 3 kali baru keluar?"),
    ("ep", 2.62, 4.32, "Episod 2, Break 100."),
    ("forkau", 8.54, 11.66, "Episod ni untuk kau. 30 minit, 3 drill."),
    ("d1a", 12.24, 15.90, "Yang pertama, kau lukis satu garisan atas pasir tu,"),
    ("d1b", 15.90, 21.00, "lepas tu kau pukul tepat pada garisan tu, tak payah bola dulu pun tak apa."),
    ("d1c", 21.00, 28.00, "Lepas dah konsisten, kau letak bola 5 cm ataupun 1 inci depan garisan,"),
    ("d1d", 28.00, 35.50, "target 8 dari 10 keluar sekali, tak kisah dekat atau jauh dari lubang."),
    ("d2a", 35.56, 42.88, "Yang kedua, kau letak tuala atas green sebagai tempat bola mendarat."),
    ("d2b", 42.88, 48.10, "Chip 10 bola, kira berapa mendarat atas tuala."),
    ("d2c", 48.14, 51.40, "Fokus tempat mendarat, bukan lubang."),
    ("d3a", 51.60, 60.50, "Yang terakhir, susun 6 bola dalam bulatan 1 meter keliling lubang, masukkan semua berturut-turut."),
    ("d3b", 60.76, 64.00, "Kau terlepas satu, buat balik."),
    ("d3c", 64.80, 72.62, "Putt 3 hingga 6 kaki ni, golfer handicap tengah hingga tinggi, masukkan 60% je."),
    ("d3d", 72.62, 75.56, "Scratch golfer, 76%."),
    ("cta", 77.30, 87.15, "Pergi practice area minggu ni, lepas tu bagitahu aku dari 10, berapa kau keluar dari bunker sekali pukulan je."),
]
# extra piece for part 2: "Pergi practice area minggu ni." alone ("Lepas tu" follows softly from 79.6)
EXTRA = {"out": ("out", 77.30, 79.06, "Pergi practice area minggu ni.")}
HOOKS = ("hook", "d2c")          # a breath after the opening line of each part
_pj = os.path.join(ROOT, "part.json")
if os.path.exists(_pj):                      # split version: pick and order pieces per part (see tools/make_parts.py)
    _keys = json.load(open(_pj))["pieces"]
    _all = {pc[0]: pc for pc in PIECES}; _all.update(EXTRA)
    PIECES = [_all[k] for k in _keys]
ALL = [pc for pc in (globals().get("_all") or {pc[0]: pc for pc in PIECES}).values()]
SIL, LOUD = -43, -36             # room noise ~ -46 dBFS on this recording


def load():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, ".src", "vo.wav"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def frame_db(x, t, w=0.05):
    i = int(t * SR); seg = x[max(0, i):max(0, i) + int(w * SR)]
    return 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9) if len(seg) else -120.0


WORDS = json.load(open(os.path.join(ROOT, "edit", "vo_words.json")))


def natural_end(x, b, lim=1e9):
    """Owner: never clip the ends. Measured on the audio, not the transcript: find where the voice has really decayed after the last word
    (60 ms under -48 dBFS), keep up to 0.15 s of room tail after it, stop before the next measured onset.
    Returns (cut, decay): the fade-out only covers cut-decay (silence), never the word."""
    t = b
    while t < min(b + 0.9, lim):
        if all(frame_db(x, t + k * 0.03, 0.03) < SIL for k in range(2)):    # 60 ms of real silence = the phrase is over
            break
        t += 0.01
    d = t
    o = d
    while o < min(d + 1.0, lim) and frame_db(x, o, 0.02) < LOUD: o += 0.01
    return max(d, min(d + 0.15, o - 0.03)), d


def natural_start(x, a):
    """Measured on the audio: if the transcript start falls in silence, move forward to the real onset; otherwise walk back to the
    60 ms silence before the phrase. Start 0.04 s before the first sound (no piece may begin with the tail of the previous phrase)."""
    loud = lambda u: frame_db(x, u, 0.02) > LOUD
    soft = lambda u: frame_db(x, u, 0.02) > SIL + 2      # soft words ("kau" before "terlepas") count as the onset
    if not loud(a) and not loud(a + 0.02):
        o = a
        while o < a + 0.8 and not soft(o): o += 0.01
        return max(o - 0.04, 0.0)
    t = a
    while t > max(a - 0.25, 0.06):
        if frame_db(x, t - 0.03, 0.03) < SIL and frame_db(x, t - 0.06, 0.03) < SIL:
            return max(t - 0.02, 0.0)
        t -= 0.01
    # phrases run together (no 60 ms pause): cut at the quietest 10 ms point just before the transcript start
    grid = np.arange(a - 0.12, a + 0.02, 0.005)
    return float(min(grid, key=lambda u: frame_db(x, u, 0.01)))


def tighten(x, a0):
    """Shorten only long pauses (> 0.55 s under -50 dBFS) to 0.32 s, keeping 0.20 s after the last sound and 0.12 s before the next,
    so every word's ending and the breath into the next phrase stay. Returns audio + full src->local frame map."""
    h = int(0.02 * SR)
    n = len(x) // h
    rms = np.array([np.sqrt(np.mean(x[i * h:(i + 1) * h] ** 2)) + 1e-9 for i in range(n)])
    quiet = 20 * np.log10(rms) < SIL
    keep = np.ones(n, bool)
    i = 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            if (j - i) * 0.02 > 0.55 and i > 0 and j < n:
                keep[i + 10:j - 6] = False            # keep 0.20 s after, 0.12 s before
            i = j
        else:
            i += 1
    out, tmap, local = [], [], 0.0
    for i in range(n):
        if keep[i]:
            seg = x[i * h:(i + 1) * h].copy()
            if out and not keep[i - 1]:
                f = int(0.015 * SR); seg[:f] *= np.linspace(0, 1, f)
            if i + 1 < n and not keep[i + 1]:
                f = int(0.015 * SR); seg[-f:] *= np.linspace(1, 0, f)
            out.append(seg); tmap.append((a0 + i * 0.02, local)); local += 0.02
    return np.concatenate(out), tmap


def main():
    x = load()
    # pieces that run on in the recording (next starts where this one ends) are cut as ONE run: no gap, no fade between them
    runs = []
    for pc in PIECES:
        if runs and abs(pc[1] - runs[-1][-1][2]) < 0.1:
            runs[-1].append(pc)
        else:
            runs.append([pc])
    buf, pieces, t = [np.zeros(int(0.25 * SR), np.float32)], [], 0.25
    tails = []
    for run in runs:
        a = natural_start(x, run[0][1])
        # never run into the next phrase of the recording ("Break 100." runs straight into "Kau pernah")
        lim = min([pc[1] for pc in ALL if pc[1] > run[-1][2] - 0.01] + [1e9]) - 0.03
        b, decay = natural_end(x, run[-1][2], lim)
        seg, tmap = tighten(x[int(a * SR):int(b * SR)], a)
        fi, fo = int(0.015 * SR), max(int(0.008 * SR), int((b - decay) * SR))
        seg[:fi] *= np.linspace(0, 1, fi); seg[-fo:] *= np.linspace(1, 0, fo)
        tails.append((run[-1][0], round(b - run[-1][2], 2), round(frame_db(x, decay - 0.06, 0.06), 1), round(frame_db(x, b - 0.03, 0.03), 1)))
        def loc(src):
            best = tmap[0]
            for s_, l_ in tmap:
                if s_ <= src: best = (s_, l_)
            return t + best[1] + min(src - best[0], 0.02)
        offs = [float(np.clip(natural_start(x, pc[1]) + 0.04 - (pc[1] + 0.06), -0.2, 0.9)) for pc in run]
        for k, (key, pa, pb, text) in enumerate(run):
            st = loc(max(pa + (offs[k] if k else 0.0), a))
            en = loc(run[k + 1][1] + offs[k + 1]) if k + 1 < len(run) else t + len(seg) / SR
            # whisper's word times run up to ~0.8 s early on this recording: measure this phrase's real onset and keep the offset,
            # so build_index can move every word anchor onto the actual sound
            off = float(np.clip(natural_start(x, pa) + 0.04 - (pa + 0.06), -0.2, 0.9))
            pieces.append({"key": key, "src": [pa, pb], "start": round(st, 3), "end": round(en, 3), "text": text, "offset": round(off, 2),
                           "map": [[round(s_, 2), round(t + l_, 3)] for s_, l_ in tmap[::5] if pa - 0.3 <= s_ <= pb + 1.2]})
        buf.append(seg); t += len(seg) / SR
        g = 0.55 if run[-1][0] in HOOKS else GAP       # a breath after the hook so it lands before the episode title
        buf.append(np.zeros(int(g * SR), np.float32)); t += g
    y = np.concatenate(buf)
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True)
    raw = os.path.join(ROOT, "edit", "voice_raw.wav")
    with wave.open(raw, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
                    "highpass=f=80,afftdn=nf=-45:nr=8,equalizer=f=3000:t=q:w=1.2:g=2,acompressor=threshold=-22dB:ratio=3:attack=5:release=120:makeup=3,"
                    "loudnorm=I=-16:TP=-2:LRA=8", "-ar", str(SR), "-ac", "2", os.path.join(ROOT, "assets", "voice.wav")], check=True)
    total = round(t + 0.1, 3)
    json.dump({"total_voice": total, "pieces": pieces}, open(os.path.join(ROOT, "edit", "voice_map.json"), "w"), indent=1)
    print("voice", total, "s")
    print("run tails (piece, extended s, last 60 ms of voice dBFS, level at the cut dBFS):", tails)
    for p in pieces: print(f"  {p['start']:6.2f}-{p['end']:6.2f} {p['key']:6} off {p['offset']:+.2f}  {p['text']}")


if __name__ == "__main__":
    main()
