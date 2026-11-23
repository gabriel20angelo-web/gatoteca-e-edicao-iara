"""Leva a captions.json corrigida da v3 (tempo do corte v2/v3) para o corte v4 pelo mapa [[t_desde, delta], ...]."""
import json, sys
from pathlib import Path
d = Path(sys.argv[1])
mapa = json.loads((d / "_olho/mapa_v3_v4.json").read_text())
def delta(t):
    k = 0.0
    for t0, dl in mapa:
        if t >= t0: k = dl
    return k
ws = json.loads((d / "_olho/captions.v3fix.json").read_text(encoding="utf-8"))
out = [dict(w, start=round(w["start"] + delta(w["start"]), 3), end=round(w["end"] + delta(w["start"]), 3)) for w in ws]
for a, b in zip(out, out[1:]):
    if a["end"] > b["start"]: a["end"] = max(a["start"] + 0.04, b["start"])
(d / "captions.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(out), "palavras; fim", out[-1]["end"])
