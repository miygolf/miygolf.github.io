// Build an SVG mini-map of the Malay Peninsula with a pin on Sungai Petani (Natural Earth via world-atlas).
import { readFileSync, writeFileSync } from "node:fs";
import { geoMercator, geoPath } from "d3-geo";
import { feature } from "topojson-client";
const topo = JSON.parse(readFileSync(new URL("../node_modules/world-atlas/countries-10m.json", import.meta.url)));
const countries = feature(topo, topo.objects.countries).features;
const W = 300, H = 380;
const extent = { type: "Feature", geometry: { type: "Polygon", coordinates: [[[98.6, 1.0], [98.6, 7.3], [104.6, 7.3], [104.6, 1.0], [98.6, 1.0]]] } };
const proj = geoMercator().fitExtent([[10, 10], [W - 10, H - 10]], extent).clipExtent([[0, 0], [W, H]]);
const path = geoPath(proj);
const pick = (n) => countries.filter((f) => f.properties.name === n);
const out = {};
out.malaysia = pick("Malaysia").map(path).join(" ");
out.others = ["Thailand", "Indonesia", "Singapore"].flatMap(pick).map(path).join(" ");
const pt = (lon, lat) => proj([lon, lat]).map((v) => +v.toFixed(1));
out.pin = pt(100.4877, 5.647);   // Sungai Petani
out.kl = pt(101.6869, 3.139);    // Kuala Lumpur (reference dot)
out.W = W; out.H = H;
writeFileSync(new URL("../assets/map/map.json", import.meta.url), JSON.stringify(out));
console.log("pin", out.pin, "kl", out.kl, "lens", out.malaysia.length, out.others.length);
