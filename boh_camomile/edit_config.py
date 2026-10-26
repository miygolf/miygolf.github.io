"""Copy + timing for the BOH Camomile TikTok review. Edit here, re-render.

Times are seconds on the source clip (28.4s). The source has no voice-over,
so the price tag timing is a placeholder: set PRICE start/end to the moment
the price is spoken once it's recorded.
"""
W, H, FPS = 1080, 1920, 30

# TikTok safe zone (x0, y0, x1, y1): clear of the top tabs, right-side
# buttons, and the bottom caption / sound / product-anchor strip.
SAFE = (60, 160, 940, 1440)

HOOK = {
    "start": 0.0, "end": 2.0,
    "line1": "SUSAH NAK",
    "line2": "TIDUR MALAM?",
    "sub": "Fikiran serabut, badan tak rehat...",
}

PRODUCT = {
    "start": 2.0, "end": 4.6,
    "name": "BOH CAMOMILE",
    "tagline": "Harmony · Botanical Beverage",
}

BENEFITS = [
    {"start": 4.7, "end": 9.2,
     "title": ["BEBAS", "KAFEIN"], "sub": "Selamat minum waktu malam"},
    {"start": 9.4, "end": 14.2,
     "title": ["CELUP", "& SIAP"], "sub": "Uncang teh, tak perlu tapis"},
    {"start": 14.4, "end": 20.0,
     "title": ["RASA", "LEMBUT"], "sub": "Aroma camomile yang menenangkan"},
]

PRICE = {
    "start": 20.2, "end": 24.2,
    "label": "HARGA",
    "text": "RM XX.XX",  # TODO: real price
    "note": "",
}

CTA = {
    "start": 24.3, "end": 99.0,
    "lines": ["KLIK", "BEG KUNING"],
    "sub": "Tekan beg kuning & checkout sekarang!",
}
