#!/usr/bin/env python3
"""Splits Ep1 "Break 100" into 3 standalone shorts (owner: "pecahkan video seminit ni pada 3 video, so aku boleh hantar seminggu 3 video").
Each part is its own HyperFrames project in parts/pN with a part.json; build_voice.py / build_index.py read it to pick and order the
voice pieces, and the template skips the scenes that are not in the part.
  Part 1: hook "30 minit je. 3 drill..." + Episod 1 + intro + Drill 1 (tee off), ends on the full CTA ("bagitahu aku berapa masuk dari 10").
  Part 2: hook "Ini pukulan masa kau belakang pokok." + Drill 2 (punch), ends "Pergi range minggu ni." + next-part card.
  Part 3: "Yang ketiga, lag jauh." + Drill 3 (lag putt), ends "Pergi range minggu ni." + 3-drill recap card.
Run from the project folder: python3 tools/make_parts.py   (then build each part, see EDIT_NOTES.md)
"""
import json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = {
    "p1": {"part": 1, "label": "1/3", "hdr": "Ep1 · Break 100",
           "pieces": ["hook1", "hook2", "ep", "intro", "d1a", "d1b", "d1c", "d1d", "d1e", "cta"]},
    "p2": {"part": 2, "label": "2/3", "hdr": "Ep1 · Break 100",
           "pieces": ["d2b", "d2a", "d2c", "out"],
           "out_title": "Punch rendah,<br>20–30 meter.", "out_next": "Next: Drill 3 · Lag putt jauh →"},
    "p3": {"part": 3, "label": "3/3", "hdr": "Ep1 · Break 100",
           "pieces": ["d3a", "d3b", "out"],
           "out_title": "3 drill siap.<br>Tee off. Punch.<br>Lag putt.", "out_next": "Save. Try minggu ni ↓"},
}

for name, cfg in PARTS.items():
    d = os.path.join(ROOT, "parts", name)
    os.makedirs(os.path.join(d, "edit"), exist_ok=True)
    os.makedirs(os.path.join(d, "assets"), exist_ok=True)
    if os.path.exists(os.path.join(d, "tools")): shutil.rmtree(os.path.join(d, "tools"))
    shutil.copytree(os.path.join(ROOT, "tools"), os.path.join(d, "tools"), ignore=shutil.ignore_patterns("__pycache__", "make_parts.py"))
    for sub in ("fonts", "sfx", "music"):
        if os.path.exists(os.path.join(d, "assets", sub)): shutil.rmtree(os.path.join(d, "assets", sub))
        shutil.copytree(os.path.join(ROOT, "assets", sub), os.path.join(d, "assets", sub))
    shutil.copy(os.path.join(ROOT, "edit", "vo_words.json"), os.path.join(d, "edit"))
    src = os.path.join(d, ".src")
    if not os.path.lexists(src): os.symlink("../../.src", src)
    for f in ("package.json", "hyperframes.json"):
        shutil.copy(os.path.join(ROOT, f), d)
    pid = f"break100-ep1-part{cfg['part']}"
    json.dump({"id": pid, "name": pid, "createdAt": "2026-11-23T10:00:00.000Z"}, open(os.path.join(d, "meta.json"), "w"))
    json.dump(cfg, open(os.path.join(d, "part.json"), "w"), ensure_ascii=False, indent=1)
    print("made", d)
