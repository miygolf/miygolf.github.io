# Coach Farhan, common mistake #1: backswing terlalu outside (IMG_0433). Source times = crop transcripts (large-v3) + energy gaps.
SRC = "IMG_0433.MOV"
PIECES = [
    dict(name="hook", a=10.80, b=18.95),   # "Technical part yang mana kita nampak sangat obvious is backswing terlalu outside."
    dict(name="demo", a=19.75, b=33.55),   # "kita take our setup normal. So bila dia punya backswing tu dia akan jadi flat dan terkeluar daripada you punya badan."
    dict(name="why", a=40.65, b=53.35),    # "Nampak? Pusing, kayu ni dekat belakang. Bila dekat belakang, then you tak ada ability untuk even pull back guna lower body, kayu tu akan jadi in dan swing tu akan jadi in to out."
    dict(name="check", a=57.70, b=64.00),  # "So, benda yang paling mungkin, benda kita boleh semak adalah macam mana posture kita."
    dict(name="close", a=75.55, b=84.35),  # "bila you angkat tangan kiri tu dan kanan, dia betul-betul dekat dengan you punya badan. Dia tak boleh terkeluar ataupun terlepas."
    dict(name="num1", a=90.95, b=98.62),   # "So, number one, check your posture, angkat, tengok tangan you dengan kaki selari."
]
HOLD = 1.6
H1, H2, H3, H4 = 190, 286, 392, 488      # all rows at the top: his head moves between y ~550 and ~1000 as the phone zooms
L1, L2, L3, L4 = H1, H2, H3, H4
ROWS = [
    dict(text="Coach Farhan · common mistake #1", st="", t=10.80, until=19.6, y=H1),
    dict(text="Backswing terlalu outside?", st="badfill big", t=10.80, until=19.6, y=H2 - 8),
    dict(text="Backswing flat", st="bad", t=27.5, until=33.5, y=L1, tag="01"),
    dict(text="Tangan terkeluar dari badan", st="bad", t=29.6, until=33.5, y=L2, tag="02"),
    dict(text="Kayu kat belakang", st="bad", t=42.6, until=53.3, y=L1, tag="!"),
    dict(text="Swing jadi in to out", st="bad", t=51.6, until=53.3, y=L2, tag="→"),
    dict(text="Semak posture", st="ink big", t=62.9, until=64.0, y=H1),
    dict(text="Tangan kiri & kanan", st="", t=76.3, until=84.3, y=L1),
    dict(text="Rapat dengan badan ✓", st="good big", t=79.8, until=84.3, y=L2),
    dict(text="Jangan terkeluar ✗", st="bad", t=81.9, until=84.3, y=L3 + 10),
    dict(text="Number one: check posture", st="good big", t=92.3, until="end", y=H1),
    dict(text="Tangan selari dengan kaki", st="", t=95.1, until="end", y=H2 + 10),
    dict(text="Save. Cuba kat range ↓", st="ink", t=97.2, until="end", y=H3 + 6),
]
CAPS = [
    ("Technical part yang kita nampak sangat obvious: backswing terlalu outside.", 10.80, 18.90),
    ("Kita take our setup normal…", 19.80, 23.40),
    ("So bila dia punya backswing tu, dia akan jadi flat dan terkeluar daripada you punya badan.", 25.70, 33.50),
    ("Nampak? Pusing, kayu ni dekat belakang.", 40.70, 44.10),
    ("Bila dekat belakang, you tak ada ability untuk pull back guna lower body.", 44.20, 48.80),
    ("Kayu tu akan jadi in, dan swing tu akan jadi in to out.", 49.20, 53.30),
    ("So benda kita boleh semak adalah macam mana posture kita.", 57.75, 64.00),
    ("Bila you angkat tangan kiri dan kanan, dia betul-betul dekat dengan you punya badan.", 75.60, 81.30),
    ("Dia tak boleh terkeluar ataupun terlepas.", 81.40, 84.35),
    ("So number one: check your posture, angkat, tengok tangan you dengan kaki selari.", 91.00, "end"),
]
