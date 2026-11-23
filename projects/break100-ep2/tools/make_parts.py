#!/usr/bin/env python3
"""Splits Ep2 "Break 100" into 2 standalone shorts (owner: "pecahkan kepada part 1 dan part 2 untuk episod 2 ni").
Each part is its own HyperFrames project in parts/pN with a part.json; build_voice.py / build_index.py read it.
  Part 1: hook "Kau pernah tak masuk bunker 3 kali baru keluar?" + Episod 2 + 30 minit 3 drill + Drill 1 (garisan dalam pasir),
          ends on the bunker CTA ("dari 10, berapa kau keluar dari bunker sekali pukulan je") + "Like untuk part 2".
  Part 2: hook "Fokus tempat mendarat, bukan lubang." + Drill 2 (chip ke tuala) + Drill 3 (bulatan 1 meter, 60% vs 76%),
          ends "Pergi practice area minggu ni." + 3-drill recap card.
Run from the project folder: python3 tools/make_parts.py
"""
import json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = {
    "p1": {"part": 1, "label": "1/2", "pieces": ["hook", "ep", "forkau", "d1a", "d1b", "d1c", "d1d", "cta"], "like": "Like untuk part 2"},
    "p2": {"part": 2, "label": "2/2", "pieces": ["d2c", "d2a", "d2b", "d3a", "d3b", "d3c", "d3d", "out"],
           "out_title": "3 drill <em>siap.</em>", "out_next": "Save. Try minggu ni ↓"},
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
    pid = f"break100-ep2-part{cfg['part']}"
    json.dump({"id": pid, "name": pid, "createdAt": "2026-11-23T10:00:00.000Z"}, open(os.path.join(d, "meta.json"), "w"))
    json.dump(cfg, open(os.path.join(d, "part.json"), "w"), ensure_ascii=False, indent=1)
    print("made", d)
