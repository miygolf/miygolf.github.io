#!/usr/bin/env python3
"""Coach Iqbal — golf coaching video prompt generator (BEFORE → IDENTIFY → ADJUSTMENT → AFTER → COMPARISON).

Builds a 5-scene prompt for an AI video model, with one CONSISTENCY LOCK block repeated word-for-word in every scene so the golfer,
clothes, club, bay, light and camera stay identical across separate generations. Only the swing motion changes between BEFORE and AFTER,
and only by the one adjustment. On-screen text is NOT baked into the AI clips: it is listed as an overlay plan for the HyperFrames edit.

Usage:
  python3 generate.py --problem slice --fault "early extension" --adjustment "feel lutut kanan tuck in ke kiri" \
      --result straighter --camera "front 3/4" --duration 15 [--preset presets/bay32-night.json] [--out outputs/x.md]
  python3 generate.py --list            # what the library knows
New faults / adjustments / cameras / ball flights go in library.json; new golfers or bays go in presets/.
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = "Coach Iqbal · Feel The Motion"
NEGATIVE = ("no morphing, no face or body changes between scenes, no extra fingers or limbs, no club bending or duplicating, no floating or "
            "teleporting ball, no slow-motion unless stated, no camera shake, no zoom pulses, no cinematic grading, no lens flares, no glow, "
            "no particles, no speed lines, no text or logos baked into the video, no crowd, no other golfers in frame, no unrealistic ball "
            "physics, no change of clothing colour, no change of time of day")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def pick(table, key, kind):
    k = key.strip().lower()
    if k in table:
        return table[k]
    sys.exit(f"Unknown {kind} '{key}'. Known: {', '.join(table)} — add it to library.json.")


def timing(total):
    """Split the duration over the 5 scenes (BEFORE, IDENTIFY, ADJUSTMENT, AFTER, COMPARISON)."""
    w = [0.20, 0.17, 0.23, 0.20, 0.20]
    cuts, t = [], 0.0
    for x in w:
        d = round(total * x * 2) / 2
        cuts.append((t, t + d)); t += d
    a, _ = cuts[-1]; cuts[-1] = (a, float(total))
    return cuts


def lock_block(p, cam):
    g, e = p["golfer"], p["environment"]
    return (f"GOLFER: {g['identity']}. CLOTHING: {g['clothing']}. CLUB: {g['club']}. BODY: {g['proportions']}. "
            f"SETTING: {e['location']}. BACKGROUND: {e['background']}. LIGHT: {e['lighting']}. CONDITIONS: {e['weather']}. "
            f"CAMERA: {cam}; {p['camera_lock']}. STYLE: realistic smartphone-quality coaching footage on a tripod, natural movement, real-time speed.")


def build(a):
    lib = load(os.path.join(HERE, "library.json"))
    p = load(a.preset)
    cam = pick(lib["cameras"], a.camera, "camera")
    fault = pick(lib["faults"], a.fault, "fault")
    adj = pick(lib["adjustments"], a.adjustment, "adjustment")
    before_flight = pick(lib["ball_flight"], a.problem, "ball flight (problem)")
    after_flight = pick(lib["ball_flight"], a.result, "ball flight (result)")
    L = lock_block(p, cam)
    base = p["golfer"]["base_swing"]
    c = timing(a.duration)
    hook = a.hook or f"Bola selalu {a.problem.lower()}?"
    slug = re.sub(r"[^a-z0-9]+", "-", f"{a.problem}-{a.fault}-{a.camera}-{a.duration:g}s".lower()).strip("-")

    scenes = [
        ("SCENE 1 — BEFORE", c[0],
         f"The golfer hits one full shot with the mid iron. Base swing: {base}. FAULT: {fault['before_motion']}. "
         f"BALL FLIGHT: {before_flight}. The golfer holds the finish and watches the ball curve away.",
         [f"Hook (frame 0): \"{hook}\"", "Small corner tag: \"BEFORE\""]),
        ("SCENE 2 — IDENTIFY", c[1],
         f"Same take as Scene 1 replayed, freezing at {fault['freeze_moment']}. Picture stays completely still during the freeze. "
         f"Nothing in the image changes; the highlight is added in the edit.",
         [f"Freeze marks: {fault['freeze_marks']}", f"Label: \"{fault['cause_text']}\"", "Optional: \"Ni punca slice\""]),
        ("SCENE 3 — ADJUSTMENT", c[2],
         (f"Same golfer, same spot, same light, same clothes. {adj.get('demo_solo', adj['demo'])}. Slow, calm, natural coaching movement; no ball is hit in this scene."
          if p["coach"].get("same_as_golfer") else
          f"Same golfer, same spot, same light. {p['coach']['identity']} wearing {p['coach']['clothing']} enters from camera left. "
          f"{adj['demo']}. Slow, calm, natural coaching movement; no ball is hit in this scene."),
         [f"Feel cue: \"{adj['feel_text']}\"", f"Name tag (first appearance): \"{BRAND}\""] + (["Talking-head option: Coach Iqbal's own voice-over \"Cuba feel lutut kanan masuk ke kiri\" recorded separately"] if p["coach"].get("same_as_golfer") else [])),
        ("SCENE 4 — AFTER", c[3],
         f"The SAME golfer, identical setup, grip, posture, tempo and backswing as Scene 1. The ONLY change: {adj['after_motion']}. "
         f"BALL FLIGHT: {after_flight}. Balanced full finish, golfer watches the ball fly toward the target.",
         ["Small corner tag: \"AFTER\""]),
        ("SCENE 5 — COMPARISON", c[4],
         "Edit-only scene, no new generation: Scene 1 and Scene 4 side by side (or stacked), synced at impact, both at real speed, "
         "then both freeze at the same downswing position as Scene 2.",
         [f"Takeaway: \"{adj['takeaway']}\"", "\"Small adjustment. Big difference.\"", f"End line: \"{BRAND}\""]),
    ]

    out = [f"# {a.problem.title()} · {a.fault} → {a.adjustment} · {a.camera} · {a.duration:g}s",
           "",
           f"**Hook:** {hook}  ",
           f"**Format:** BEFORE → IDENTIFY → ADJUSTMENT → AFTER → COMPARISON · vertical 9:16 · {a.duration:g} s · TikTok / Reels / Shorts  ",
           f"**Branding:** {BRAND}  ",
           f"**Preset:** `{os.path.relpath(a.preset, HERE)}`",
           ""]
    if p.get("consent_note"):
        out += [f"> ⚠️ {p['consent_note']}", ""]
    out += ["## Consistency lock (paste word-for-word into every generation)", "", "```", L, "```", "",
            "## Negative prompt (every generation)", "", "```", NEGATIVE, "```", "",
            "## Scenes", ""]
    for title, (t0, t1), action, overlays in scenes:
        gen = "edit only (HyperFrames)" if "COMPARISON" in title or "IDENTIFY" in title else "generate"
        out += [f"### {title}  ·  {t0:.1f}–{t1:.1f} s  ·  {gen}", "",
                "**Prompt:**", "", "```", (L + " " + action) if gen == "generate" else action, "```", "",
                "**Overlay plan (added in HyperFrames, not in the AI clip):**", ""]
        out += [f"- {o}" for o in overlays] + [""]
    out += ["## Production notes", "",
            "- Generate Scene 1 first and keep its seed / reference frame. Generate Scenes 3 and 4 with that same frame as the image reference, "
            "the same lock and the same seed, so the golfer, clothes, bay and light match.",
            "- Scenes 2 and 5 are made in the edit from Scenes 1 and 4 (freeze, side-by-side): no extra generation, so they cannot drift.",
            "- Keep every text overlay out of the AI generation (models garble text); add it in HyperFrames inside the safe band "
            "(x 60–930, y 168–1330 on 1080×1920), never over a face.",
            "- Reject any take where the swing changes beyond the one adjustment (grip, stance width, backswing length, tempo must match).",
            "- Label the video as an AI-generated demonstration when it is posted, so viewers don't read it as a real result.",
            "- For the best likeness, give the model 2-3 real photos of the golfer (face, full body in this outfit) as image references in every generation.",
            ""]
    return "\n".join(out), slug


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--problem"); ap.add_argument("--fault"); ap.add_argument("--adjustment"); ap.add_argument("--result")
    ap.add_argument("--camera", default="front 3/4"); ap.add_argument("--duration", type=float, default=15)
    ap.add_argument("--hook"); ap.add_argument("--preset", default=os.path.join(HERE, "presets", "iqbal-bay32-night.json"))
    ap.add_argument("--out"); ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        lib = load(os.path.join(HERE, "library.json"))
        for k, v in lib.items(): print(f"{k}: {', '.join(v)}")
        return
    if not all([a.problem, a.fault, a.adjustment, a.result]):
        ap.error("--problem, --fault, --adjustment and --result are required")
    md, slug = build(a)
    out = a.out or os.path.join(HERE, "outputs", f"{slug}.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(md)
    print(out)


if __name__ == "__main__":
    main()
