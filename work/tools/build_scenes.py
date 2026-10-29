"""Injects the shared card styles into each scene and writes compositions/."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
css = (ROOT / "tools/card.css").read_text()
for src in sorted((ROOT / "tools/scenes").glob("*.html")):
    (ROOT / "compositions" / src.name).write_text(src.read_text().replace("/*CARD_CSS*/", css.rstrip("\n")))
    print("wrote", src.name)
