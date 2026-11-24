#!/usr/bin/env bash
# Drive folder 1V5O7fsTQ3tDUyWBKtVEx_orZs4-I7WqR (24 Nov 2026, bunker script) -> .src/   (owner's footage, not committed)
set -euo pipefail
cd "$(dirname "$0")/.."
while read -r id name; do
  [ -f ".src/$name" ] || curl -sSL -o ".src/$name" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
done <<'L'
19eqvw79FdvE0UAmwswLaNNe-uDb8jO99 IMG_0413.MOV
1kyyCcMVHl1MHIRODVtuix6kl29DsHPwo IMG_0414.MOV
1I6I17HlaQMZcZXyCgrZioI7eUDkPLdU0 IMG_0415.MOV
1R14686WkqrcyzRgko6NWarN0VWjRjZU0 IMG_0417.MOV
1rZiNk83YuZyAQhTWQBUgJJ049-sc2vR4 IMG_0418.MOV
1vNo6YaICv1Xvt_AotCBUMhUckJ_Tr_1d IMG_0419.MOV
1kcNPLccOQxI9svZEEH5SALZJ-JImEDzm demo_top_n_skull.MOV
1CVMoqRcJ6nDMSVT0rbGkEtZkhrg6P018 egg_fry.MOV
L
ls -la .src
