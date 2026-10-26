# Casual IG watermark

Watermark Instagram gaya santai untuk Reels/Story (1080×1920):
pill lutsinar lembut, ikon IG warna gradient, handle huruf kecil,
dan tagline tulisan tangan (optional) yang senget sikit.

## PNG siap guna (`png/`)

| Fail | Guna |
|---|---|
| `iqbal.yusoff.png` | Versi bersih, ikon gradient |
| `iqbal.yusoff_tagline.png` | Ada tagline "ride santai je" |
| `iqbal.yusoff_mono.png` | Ikon putih, lagi minimal |

PNG ni transparent, jadi boleh terus drag masuk CapCut / VN / InShot sebagai overlay.

## Buat PNG baru

```bash
python3 watermark/make_watermark.py --handle iqbal.yusoff --tagline "weekend ride" -o wm.png
```

Pilihan: `--mono` (ikon putih), `--bg-alpha 0.25` (pill lagi telus), `--height 90` (lagi besar).

## Tanam terus dalam video

```bash
watermark/apply.sh input.mp4 output.mp4 iqbal.yusoff "ride santai je"
```

- Letak kiri atas (x=40, y=230), dalam safe zone Reels: tak kena header,
  butang kanan atau caption bawah.
- Fade-in lembut kat awal, lepas tu terapung perlahan ±4px (nampak hidup, tak kaku).
- Output H.264 + AAC, `faststart`, max 8 Mbps, sesuai untuk upload IG.
- Tukar kedudukan: `POS_X=60 POS_Y=400 watermark/apply.sh ...`; matikan float: `BOB=0`.

Perlu: `python3` + Pillow, `ffmpeg`.
Font: Poppins & Caveat (SIL OFL, lesen dalam `fonts/`).
