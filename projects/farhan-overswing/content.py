# Coach Farhan, common mistake #2: overswing (IMG_0434). Source times = crop transcripts (large-v3, casual-Malay prompt) + energy gaps.
SRC = "IMG_0434.MOV"
PIECES = [
    dict(name="hook", a=12.55, b=24.45),   # "Overswing. You seronok lah tengok John Daly buat macam tu, tapi berapa puluh tahun dia practice. So you tak boleh ikut sebab maybe body and human stability tak sama."
    dict(name="demo", a=59.45, b=79.95),   # "Again, overswing. Macam mana? Daripada tepi, angkat, cukup. Tak perlu nak melampau-lampau belakang ni sebab penatlah. Bila dia panjang-panjang swing ni, dahlah you lambat nak datang. Bola pun tak kena, weight shift tak kena, transfer tak betul, finishing lagilah."
    dict(name="fix", a=82.10, b=97.10),    # "Again, make sure you ada that control of the backswing, maintain..., parallel to the ground kalau boleh, letak sini pun okay, and you ada that control, finish dengan lebih baik."
]
HOLD = 1.6
H1, H2, H3, H4 = 190, 286, 392, 488      # all rows at the top: his head moves between y ~550 and ~1000 as the phone zooms
L1, L2, L3, L4 = H1, H2, H3, H4
ROWS = [
    dict(text="Coach Farhan · common mistake #2", st="", t=12.55, until=24.4, y=H1),
    dict(text="Overswing?", st="badfill big", t=12.55, until=24.4, y=H2 - 8),
    dict(text="Swing pro ≠ swing kita", st="", t=19.2, until=24.4, y=H3),
    dict(text="Dari tepi: angkat… cukup ✓", st="good", t=61.4, until=71.3, y=L1),
    dict(text="Tak perlu melampau", st="bad", t=65.5, until=71.3, y=L2),
    dict(text="Lambat nak datang", st="bad", t=74.4, until=79.95, y=L1, tag="✗"),
    dict(text="Bola & weight shift tak kena", st="bad", t=75.5, until=79.95, y=L2, tag="✗"),
    dict(text="Finishing lagilah", st="bad", t=78.6, until=79.95, y=L3, tag="✗"),
    dict(text="Kawal backswing", st="good big", t=84.7, until="end", y=H1),
    dict(text="Parallel dengan tanah · finish lebih baik", st="", t=88.0, until="end", y=H2 - 4),
    dict(text="Save. Cuba kat range ↓", st="ink", t=95.6, until="end", y=H3 - 4),
]
CAPS = [
    ("Overswing. You seronok tengok John Daly buat macam tu, tapi berapa puluh tahun dia practice.", 12.60, 18.95),
    ("So you tak boleh ikut, sebab maybe body and stability tak sama.", 19.20, 24.45),
    ("Again, overswing. Macam mana? Daripada tepi, angkat… cukup.", 59.50, 63.00),
    ("Tak perlu nak melampau-lampau belakang ni, sebab penatlah.", 65.50, 71.30),
    ("Bila panjang-panjang swing ni, dahlah you lambat nak datang.", 71.90, 75.10),
    ("Bola pun tak kena, weight shift tak kena, transfer tak betul, finishing lagilah.", 75.50, 79.95),
    ("Again, make sure you ada that control of the backswing.", 82.15, 85.50),
    ("Parallel to the ground kalau boleh, letak sini pun okay.", 87.70, 91.10),
    ("And you ada that control, finish dengan lebih baik.", 91.40, "end"),
]
