"""Builds compositions/captions.html: the top caption deck (covers the source's
burned-in subtitles) with word-timed karaoke groups. Word times are spread by
syllable inside each cut segment's measured speech window."""
import json, re, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
cuts = {r[0]: r for r in json.load(open(ROOT / "src/cuts.json"))}

# segment -> (speech window in source seconds, words). *word* = emphasis.
SPEECH = [
    ("H",  41.83, 43.02, "Kita tak nak *terlebih* macam ni."),
    ("A1",  0.06,  0.71, "Kalau kita *chipping,*"),
    ("A2",  1.34,  2.51, "kita kena selalu aware"),
    ("A3",  3.01,  4.18, "kita punya *back* *swing* tu,"),
    ("A4",  5.59,  6.20, "tak nak ke *dalam.*"),
    ("B1", 11.33, 13.79, "Back swing kita *terlebih* pada *kaki* *kanan* kita ni,"),
    ("B2", 14.97, 16.42, "*margin* *of* *error* dia sangat *tinggi.*"),
    ("C1", 17.50, 19.65, "Sebab tangan kita akan *compensate* dengan"),
    ("C2", 20.20, 21.86, "*rotate,* kita main *wrist,*"),
    ("C3", 24.13, 24.93, "badan jadi *stuck.*"),
    ("C4", 25.65, 27.16, "So ada banyak *kemungkinan* kat situ."),
    ("D1", 29.60, 31.97, "Kalau boleh, kita nak *maintain* di *luar* *kaki* *kanan.*"),
    ("E1", 34.73, 35.92, "Sini, kita tak nak *sini.*"),
    ("E2", 37.63, 38.29, "*Sini* *je.*"),
    ("E3", 39.51, 41.46, "*Ngam-ngam* kaki kanan pun still *okey* lah."),
    ("F1", 45.54, 46.16, "*Weight* belah *kiri,*"),
    ("F2", 46.77, 47.44, "maintain *triangle.*"),
]

# caption groups: (segment, first word index, last word index exclusive)
GROUPS = [
    ("H", 0, 6),
    ("A1", 0, 3), ("A2", 0, 4), ("A3", 0, 5), ("A4", 0, 4),
    ("B1", 0, 4), ("B1", 4, 9),
    ("B2", 0, 4), ("B2", 4, 6),
    ("C1", 0, 4), ("C1", 4, 6), ("C2", 0, 4), ("C3", 0, 3),
    ("C4", 0, 4), ("C4", 4, 6),
    ("D1", 0, 4), ("D1", 4, 9),
    ("E1", 0, 5), ("E2", 0, 2),
    ("E3", 0, 3), ("E3", 3, 7),
    ("F1", 0, 3), ("F2", 0, 2),
]

def syl(w):
    return max(1, len(re.findall(r"[aeiouy]+", w.lower())))

words = {}
for seg, s0, s1, text in SPEECH:
    name, src_in, src_out, ed_in, ed_out = cuts[seg]
    toks = text.split()
    weights = [syl(t.strip("*,.")) for t in toks]
    total = sum(weights)
    a = ed_in + (s0 - src_in)
    b = ed_in + (s1 - src_in)
    t = a
    out = []
    for tok, wgt in zip(toks, weights):
        d = (b - a) * wgt / total
        emph = tok.startswith("*")
        out.append({"text": tok.strip("*"), "start": round(t, 3), "end": round(t + d, 3), "emph": emph})
        t += d
    words[seg] = out

groups = []
for i, (seg, a, b) in enumerate(GROUPS):
    ws = words[seg][a:b]
    groups.append({"id": f"cap-g{i}", "words": ws, "start": ws[0]["start"], "end": ws[-1]["end"]})

# hold each group until the next one opens (no flicker in tiny gaps)
for i, g in enumerate(groups):
    nxt = groups[i + 1]["start"] if i + 1 < len(groups) else g["end"] + 0.25
    g["show"] = round(max(0.1, g["start"] - 0.06), 3)
    g["hide"] = round(nxt - 0.04 if nxt - g["end"] < 0.6 else g["end"] + 0.25, 3)

def word_html(gi, wi, w):
    cls = "cap-w emph" if w["emph"] else "cap-w"
    return f'<span id="cap-g{gi}-w{wi}" class="{cls}">{html.escape(w["text"])}</span>'

group_html = "\n".join(
    f'        <div id="{g["id"]}" class="cap-group"><div class="cap-line">'
    + " ".join(word_html(gi, wi, w) for wi, w in enumerate(g["words"]))
    + "</div></div>"
    for gi, g in enumerate(groups)
)

timing = [{"id": g["id"], "show": g["show"], "hide": g["hide"],
           "w": [[w["start"], w["end"]] for w in g["words"]]} for g in groups]

tpl = (ROOT / "tools/captions.template.html").read_text()
out = tpl.replace("<!--GROUPS-->", group_html).replace("/*TIMING*/[]", json.dumps(timing))
(ROOT / "compositions/captions.html").write_text(out)
json.dump(groups, open(ROOT / "src/caption_groups.json", "w"), indent=1)
for g in groups:
    print(f'{g["show"]:6.2f}-{g["hide"]:6.2f}  ' + " ".join(w["text"] for w in g["words"]))
