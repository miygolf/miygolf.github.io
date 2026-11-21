# Golf prompt generator — Coach Iqbal · Feel The Motion

Reusable prompt system for AI-generated coaching shorts in the **BEFORE → IDENTIFY → ADJUSTMENT → AFTER → COMPARISON** format.

| file | what |
| --- | --- |
| `SYSTEM_PROMPT.md` | system prompt for any chat LLM (generate new prompts by conversation) |
| `generate.py` | offline generator: `python3 generate.py --problem slice --fault "early extension" --adjustment "feel lutut kanan tuck in ke kiri" --result straighter --camera "front 3/4" --duration 15` |
| `library.json` | camera angles, faults (before motion, freeze moment, marks, cause text), adjustments (demo, after motion, feel cue, takeaway), ball flights — add new entries here |
| `presets/bay32-night.json` | identity + environment lock from the Drive folder 1vAvvjHm1jcRnv-GNmpjir7cBmisdTn-b footage (bay 32, night); coach fields to fill from a reference photo |
| `outputs/` | generated prompts |

How the pieces fit:
1. AI video model: generate **Scenes 1, 3, 4** only, each with the same consistency lock, negative prompt and Scene 1's seed / reference frame.
2. HyperFrames (this repo's pipeline): build **Scenes 2 and 5** from those clips (freeze, side-by-side) and add every text overlay — the
   AI clips stay text-free so nothing gets garbled.
3. Post with an "AI-generated demonstration" label.

Note: HyperFrames itself composes footage and graphics; it does not generate realistic people. The scene prompts are for whichever AI video
model you use (most make 5–10 s clips, which is why scenes are generated separately and assembled in HyperFrames).
