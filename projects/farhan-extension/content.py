# Coach Farhan: early extension (IMG_0431 talk + demo, IMG_0432 summary). Source times = crop transcripts (large-v3) + energy gaps.
SRC = "IMG_0431.MOV"
PIECES = [
    dict(name="hook", a=4.62, b=10.48),                     # "Bila kita cakap pasal early extension, perkara yang biasa berlaku dalam amateur,"
    dict(name="why", a=15.68, b=32.40),                     # "You punya mindset biasa, bila you nak pukul tu, you swing, suddenly you punya pinggang ataupun lower body tu pergi dulu, so tak ada time untuk tangan ni datang and strike bola ataupun compress untuk bawa balik ke target"
    dict(name="demo", a=128.85, b=151.30),                  # "Kita try to push left hip ke belakang dulu. Bersama-sama, right hip rotate macam tu. Left hip ke dalam, right hip ke kiri. Dia tak nak lutut ni dia tak boleh keluar. Macam you menari, macam tu."
    dict(name="sum", src="IMG_0432.MOV", a=30.38, b=46.15), # "So dua benda yang kita nak kena fokus: backswing normal, left hip you pull back, right hip kena rotate left, and then tangan akan sampai strike bola."
]
HOLD = 1.6
H1, H2, H3 = 190, 286, 392          # rows only in the top band (his head is ~y 600-900 in both set-ups)
B = "IMG_0432.MOV"
ROWS = [
    dict(text="Coach Farhan · early extension", st="", t=4.62, until=15.6, y=H1),
    dict(text="Pinggang lari dulu?", st="badfill big", t=4.62, until=15.6, y=H2 - 8),
    dict(text="Lower body pergi dulu", st="bad", t=23.34, until=32.4, y=H1, tag="01"),
    dict(text="Tangan tak sempat strike bola", st="bad", t=26.64, until=32.4, y=H2 - 6, tag="02"),
    dict(text="Drill:", st="ink big", t=128.9, until=151.3, y=H1),
    dict(text="Push left hip ke belakang", st="good", t=131.78, until=151.3, y=H2 + 12, tag="01"),
    dict(text="Right hip rotate ke kiri", st="good", t=136.12, until=151.3, y=H3 + 6, tag="02"),
    dict(text="2 benda fokus:", st="ink big", src=B, t=30.46, until=35.45, y=H1),
    dict(text="Left hip pull back", st="good big", src=B, t=35.54, until="end", y=H1, tag="01"),
    dict(text="Right hip rotate left", st="good", src=B, t=39.06, until="end", y=H2 + 20, tag="02"),
    dict(text="Save. Cuba kat range ↓", st="ink", src=B, t=44.6, until="end", y=H3 + 14),
]
CAPS = [
    ("Bila kita cakap pasal early extension, perkara yang biasa berlaku dalam amateur…", 4.65, 10.45),
    ("Bila you nak pukul tu, you swing…", 15.70, 21.00),
    ("Suddenly you punya pinggang ataupun lower body tu pergi dulu.", 21.10, 25.90),
    ("So tak ada time untuk tangan ni datang and strike bola, ataupun compress, bawa balik ke target.", 25.96, 32.40),
    ("Kita try to push left hip ke belakang dulu.", 128.90, 134.40),
    ("Bersama-sama, right hip rotate, macam tu.", 135.20, 138.70),
    ("Left hip ke dalam, right hip ke kiri.", 140.60, 144.40),
    ("Lutut ni dia tak boleh keluar. Macam you menari.", 144.50, 151.30),
    ("Dua benda yang kita nak kena fokus.", 30.40, 32.80, B),
    ("Backswing normal, left hip you pull back,", 33.00, 38.80, B),
    ("right hip kena rotate left, and then tangan akan sampai strike bola.", 39.00, "end", B),
]
