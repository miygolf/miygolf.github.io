"""Fill tools/anatomi.template.html with tracked anchors -> compositions/anatomi.html."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
T0, A, B = 9.0, 10.2, 12.8  # scene start; callout window in film time
tr = json.load(open(ROOT / "src/tracks.json"))
def pts(name):
    return [[round(t - T0, 2), x, y] for t, x, y in tr[name] if A <= t <= B]
tail, rotor = pts("tail"), pts("rotor")
s = (ROOT / "tools/anatomi.template.html").read_text()
s = s.replace("__TAIL__", json.dumps(tail)).replace("__ROTOR__", json.dumps(rotor))
s = s.replace("__T0X__", str(tail[0][1])).replace("__T0Y__", str(tail[0][2]))
s = s.replace("__R0X__", str(rotor[0][1])).replace("__R0Y__", str(rotor[0][2]))
(ROOT / "compositions/anatomi.html").write_text(s)
print("anatomi.html", len(tail), len(rotor))
