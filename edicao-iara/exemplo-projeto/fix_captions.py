import json, shutil, sys
from pathlib import Path
d = Path(__file__).resolve().parent.parent
f = d / "captions.json"
bak = d / "captions.before_v3.json"
if not bak.exists():
    shutil.copy(f, bak)
w = json.loads(bak.read_text(encoding="utf-8"))   # sempre parte do backup (idempotente)
def find(text, t, tol=0.06):
    for i, x in enumerate(w):
        if x["text"] == text and abs(x["start"] - t) <= tol:
            return i
    raise SystemExit(f"nao achei {text} @ {t}")
def ent(text, a, b):
    return {"text": text, "start": a, "end": b, "type": "word"}
# trocas e retempos (por indice original, antes de inserir)
i = find("feitos", 19.65); w[i]["text"] = "feito"
i = find("que", 33.18); w[i].update(text="é", start=33.10, end=33.24)
i = find("mesmos?", 30.13); w[i].update(start=30.13, end=30.25)
i = find("Faz", 30.32); w[i].update(start=30.25, end=30.33)
i = find("sentido,", 30.35); w[i].update(text="sentido?", start=30.33, end=30.73)
i = find("comigo?", 32.30); w[i]["text"] = "comigo,"
i = find("clube", 49.37); w[i]["text"] = "Clube"
i = find("do", 49.61); w[i]["text"] = "do"
i = find("livro,", 49.73); w[i]["text"] = "Livro,"
i = find("mês", 52.69); w[i]["text"] = "mês,"
i = find("Frank", 51.37); w[i].update(text="Frankenstein,", start=51.37, end=51.91)
j = find("Frankenstein", 51.55); del w[j]
i = find("que", 46.08); w[i]["end"] = 46.28
# inserir (de tras para frente, por tempo)
ins = [("é", 1.52, 1.66, "gente", 1.34), ("é", 8.28, 8.44, "gente", 8.06), ("é", 46.28, 46.36, "que", 46.08),
       ("de", 51.91, 51.97, "Frankenstein,", 51.37)]
for text, a, b, prev, pt in sorted(ins, key=lambda z: -z[1]):
    k = find(prev, pt) + 1
    w.insert(k, ent(text, a, b))
f.write_text(json.dumps(w, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(w), "palavras")
for x in w:
    if 1.3 < x["start"] < 2.3 or 8 < x["start"] < 8.6 or 29.9 < x["start"] < 30.8 or 32.9 < x["start"] < 33.5 or x["start"] > 46 and x["start"] < 46.6 or x["start"] > 49.3:
        print(x["text"], x["start"], x["end"])
