# SPEC — "Dibina, bukan dibeli siap" (PRGR 02 × KBS TGI 60 × MCC Plus 4)

GOAL:    a golfer scrolling IG sees a set being built from three named parts and DMs MIY Golf to have theirs built.
OUTPUT:  HyperFrames, 1080 x 1920, 30 fps (IG Reels / TikTok; key copy also inside the 3:4 grid crop y 240–1680).
TIME:    22.75 s x 30 = 682 frames. Music 124 BPM → 14.516 frames a beat; the track's drop lands on beat 5 (2.419 s).
         Scene seams on beats 5, 13, 21, 27, 35, 41 (2.419 / 6.290 / 10.161 / 13.065 / 16.935 / 19.839 s).

LOOK:    "Spec Plate" — the photos are the ground, full frame, always. Copy lives on steel badge plates cut like
         the PRGR 02 cavity badge (22 px chamfers top-left and bottom-right, a blank slot beside the tag).
         - plate: brushed steel, vertical gradient #f4f5f6 → #d5d8dc → #b8bcc2 plus 1 px hairlines at 6 %;
           drop shadow 0 14 px 22 px rgba(0,0,0,.5).
         - ink: engraved graphite #222428 with a 2 px white lower lip (engraving), every word that must be read.
         - accent: KBS red #d7191f (taken from the shaft label), only the tag, the cutter line, the measure line,
           one word in the recap and the hanko. One red focus per frame.
         - type: Barlow Condensed 800 (display, 150–190 px, −1 % tracking, caps), 600 (tags, 38 px, +12 %),
           500 (lines, 46 px).
         - end card: the MIY Golf Trading logo on its own black.
OBJECTS: the real heads (PRGR 02), shafts (KBS TGI 60, ruler marks), grips (Golf Pride MCC Plus 4) — all from the
         four photos; the plate (a machined badge), a red hanko seal "MIY · DIBINA".
MOTION:  enter expo.out 0.45 s (plates slot in from the left like a part, seat 3 px in 2 frames);
         engrave = clip reveal left→right 0.3 s power2.inOut led by a 6 px red cutter line;
         camera power2.inOut 2.5–3.5 s, one move per shot; whips power3.in 0.2 s with render motion blur;
         stamp 1.6 → 1 in 0.12 s power4.in, 2-frame 4 px shake. Exits 40 % shorter than entrances.
SHOTS:
  S1 0–2.42    close-up 02 heads, wrap visible. Plate on frame 0: "MIY GOLF · CUSTOM BUILD / DIBINA. / bukan
               dibeli siap." Punch-in on the badge at beat 2.5; whip up into the drop. Riser → drop.
  S2 2.42–6.29 row of heads; camera tracks up the row. Plate "KEPALA / PRGR 02 / Kepala besi dari Jepun."
               Clubs clank on landing. Exit: red iris opens out of the plate's tag.
  S3 6.29–10.16 shaft levelled (photo turned 8.3°), red iris closes onto the KBS label; track KBS → TGI 60.
               Plate "SHAFT / KBS TGI 60 / Graphite tour. Ringan di tangan." Exit: whip right.
  S4 10.16–13.07 ruler marks on the bench; a red measure line runs the marks to a CUT tick.
               Plate "PANJANG / IKUT KAU / Shaft dipotong ikut ukuran kau." Tape measure.
  S5 12.77–16.94 the measure line wipes on the grips; pan from MCC Plus 4 to Golf Pride.
               Plate "GRIP / MCC PLUS 4 / Golf Pride. Saiz ikut tangan kau." Exit: blur swap.
  S6 16.94–19.84 flat lay pulls back to the whole bench. Recap lands on beats: "KEPALA + SHAFT + GRIP / = SET KAU."
               Hanko "DIBINA · CUSTOM / LULUS" slams on beat 39.5. Dip cut.
  S7 19.84–22.75 close-up of a head badge settles; CTA plate "CUSTOM BUILD & FITTING / DM KAMI." engraved in, held 2.1 s.
  v2: no logo, no description lines anywhere (owner's call); plates carry only tag + title.
  v3: NO on-screen text or graphics at all (owner's call): photos, camera moves, transitions, SFX (+ optional music).
      The LOOK, plate and copy lines above are history; REVIEW.md has the v3 cut.
BANNED:  the spec.md defaults; plus: photos shrunk into cards; a slideshow of dissolves; text over the hero head
         badge; anything in the right rail (x > 960) or under y 1330; every plate entering the same way twice in a
         row without the engrave; generic whoosh on every cut (rotate takes).
QA:      0.0 (thumbnail reads), 1.3 (punch-in), 2.5 (drop landing), 4.5, 6.3 (iris seam), 8.5, 11.8 (CUT tick),
         12.9 (wipe), 15.0, 18.9 (recap + stamp), 21.5 (end card).
