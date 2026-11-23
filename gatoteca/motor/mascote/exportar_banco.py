# -*- coding: utf-8 -*-
"""Copia o banco de poses para a pasta do clube: PNG transparente, SVG, folha de contato, pagina e LEIAME."""
import json, os, shutil, html
from gato_banco import folha
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[3]  # raiz do repositório

B = str(_REPO / 'gatoteca/motor/mascote/banco')
D = str(_REPO / 'gatoteca/artes/Mascote - banco de poses')
PNG, SVG = "png (fundo transparente)", "svg (para o Canva)"

os.makedirs(os.path.join(D, PNG), exist_ok=True)
os.makedirs(os.path.join(D, SVG), exist_ok=True)
meta = json.load(open(os.path.join(B, "banco.json"), encoding="utf-8"))
for m in meta:
    shutil.copy(os.path.join(B, m["arquivo"] + ".png"), os.path.join(D, PNG, m["arquivo"] + ".png"))
    shutil.copy(os.path.join(B, m["arquivo"] + ".svg"), os.path.join(D, SVG, m["arquivo"] + ".svg"))
folha(meta, os.path.join(D, "0 - folha de contato.png"))

grupos = []
for m in meta:
    if m["grupo"] not in grupos:
        grupos.append(m["grupo"])

cards = ""
for g in grupos:
    cards += '<h2>%s</h2><div class="grade">' % g
    for m in [x for x in meta if x["grupo"] == g]:
        cards += ('<figure><div class="img"><img src="%s/%s.png" alt="%s"></div>'
                  '<figcaption><b>%s · %s</b><span>%s</span><code>%s</code></figcaption></figure>') % (
            PNG, m["arquivo"], html.escape(m["nome"]), m["cod"], html.escape(m["nome"]), html.escape(m["nota"]), m["arquivo"])
    cards += '</div>'

pagina = '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Banco de poses do gato</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Cormorant+Garamond:ital,wght@0,500;0,700;1,500&display=swap" rel="stylesheet">
<style>
:root{--papel:#F4E9D5;--tinta:#3B2A33;--ouro:#EDBE4F}
*{box-sizing:border-box}body{margin:0;background:var(--papel);color:var(--tinta);font-family:'Cormorant Garamond',serif;font-size:19px}
header{background:var(--ouro);padding:48px 24px 36px;text-align:center}
header small{font-family:Cinzel;letter-spacing:.35em;font-size:13px}
header h1{font-style:italic;font-weight:700;font-size:52px;margin:6px 0 8px}
header p{max-width:760px;margin:0 auto;line-height:1.35}
main{max-width:1240px;margin:0 auto;padding:16px 16px 60px}
h2{font-family:Cinzel;letter-spacing:.2em;font-size:20px;margin:42px 0 14px;border-bottom:1px solid #3B2A3355;padding-bottom:8px}
.grade{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:18px}
figure{margin:0;background:#fffaf0;border:1px solid #3B2A3322;border-radius:10px;overflow:hidden}
.img{background:var(--ouro);aspect-ratio:1;display:flex;align-items:center;justify-content:center;padding:14px}
.img img{max-width:100%;max-height:100%}
figcaption{padding:10px 14px 14px;display:flex;flex-direction:column;gap:6px;line-height:1.25}
figcaption b{font-size:21px}figcaption code{font-size:12px;opacity:.6}
</style></head><body>
<header><small>CLUBE DO LIVRO ENTRELINHAS</small><h1>Banco de poses do gato</h1>
<p>O mascote é o frajola de pelúcia de traços: o pelo inteiro feito de risquinhos, tufos na silhueta, olhos verdes de brilho,
focinho e peito brancos. Cada pose tem PNG com fundo transparente e SVG, e a nota diz para que tipo de post ela serve.</p></header>
<main>{CARDS}</main></body></html>'''.replace("{CARDS}", cards)
open(os.path.join(D, "Banco de poses do gato.html"), "w", encoding="utf-8").write(pagina)

linhas = ["BANCO DE POSES DO GATO · Clube do Livro Entrelinhas", "",
          "Mascote: o frajola de pelúcia de traços (rodada 3, versão A).",
          "Cores: preto #2A2226, branco #F6F0E4, olhos #C9D86A, orelha #E99AA6, feijõezinhos #F0A3B0.",
          r"Motor: gatoteca/motor/mascote/gato_banco.py  (py gato_banco.py [códigos]); cada pose é uma função @pose.",
          "Pastas: «%s» para colar em qualquer arte; «%s» para ampliar sem perder." % (PNG, SVG), ""]
for g in grupos:
    linhas.append(g.upper())
    for m in [x for x in meta if x["grupo"] == g]:
        linhas.append("  %s  %-26s %s" % (m["cod"], m["nome"], m["nota"]))
    linhas.append("")
open(os.path.join(D, "LEIAME.txt"), "w", encoding="utf-8").write("\n".join(linhas))
print(len(meta), "poses copiadas para", D)
