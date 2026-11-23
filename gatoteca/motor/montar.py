# -*- coding: utf-8 -*-
"""Clube do Livro Entrelinhas: monta as artes (HTML + SVG desenhado a mao) e fotografa em 1080x1350.

uso: py montar.py [arte1 arte2 ...]   (sem argumento, monta todas as arte*.html da pasta)
Le o grao de papel e os gestos de canetao do acervo do UmRabiscoPsi (slides_html/assets.json).
"""
import base64, glob, json, os, sys
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[2]  # raiz do repositório

AQUI = os.path.dirname(os.path.abspath(__file__))
ACERVO = str(_REPO / 'gatoteca/motor/assets/assets.json')
SAIDA = os.path.join(AQUI, "saida")
os.makedirs(SAIDA, exist_ok=True)

A = json.load(open(ACERVO, encoding="utf-8"))


def b64(caminho, mime):
    return "data:%s;base64,%s" % (mime, base64.b64encode(open(caminho, "rb").read()).decode())


F = os.path.join(AQUI, "fontes")
css = [
    "<style id='acervo'>",
    "@font-face{font-family:'Cormorant';font-weight:300 700;src:url(%s)}" % b64(os.path.join(F, "CormorantGaramond.ttf"), "font/ttf"),
    "@font-face{font-family:'Cormorant';font-style:italic;font-weight:300 700;src:url(%s)}" % b64(os.path.join(F, "CormorantGaramond-Italic.ttf"), "font/ttf"),
    "@font-face{font-family:'Cinzel';font-weight:400 900;src:url(%s)}" % b64(os.path.join(F, "Cinzel.ttf"), "font/ttf"),
    "@font-face{font-family:'Italiana';src:url(%s)}" % b64(os.path.join(F, "Italiana.ttf"), "font/ttf"),
    "@font-face{font-family:'Shrikhand';src:url(%s)}" % b64(os.path.join(F, "Shrikhand.ttf"), "font/ttf"),
    "@font-face{font-family:'DM Serif Display';src:url(%s)}" % b64(os.path.join(F, "DMSerifDisplay.ttf"), "font/ttf"),
    "@font-face{font-family:'DM Serif Display';font-style:italic;src:url(%s)}" % b64(os.path.join(F, "DMSerifDisplay-Italic.ttf"), "font/ttf"),
    "@font-face{font-family:'Special Elite';src:url(%s)}" % b64(os.path.join(F, "SpecialElite.ttf"), "font/ttf"),
    "@font-face{font-family:'Caveat';font-weight:400 700;src:url(%s)}" % b64(os.path.join(F, "Caveat.ttf"), "font/ttf"),
]
raiz = ["--grao-pos:url(%s)" % A["grao_pos"]["uri"], "--grao-neg:url(%s)" % A["grao_neg"]["uri"],
        "--logo-tulipa:url(%s)" % b64(str(_REPO / 'gatoteca/motor/assets/logo_tulipa.png'), "image/png")]
for k, v in A.items():
    if k.startswith("g_"):
        raiz.append("--G-%s:url(%s)" % (k[2:], v["uri"]))
css.append(":root{" + ";".join(raiz) + "}")
css.append("</style>")
ACERVO_CSS = "\n".join(css)


def montar(nome):
    tpl = open(os.path.join(AQUI, nome + ".html"), encoding="utf-8").read()
    html = tpl.replace("<!--ACERVO-->", ACERVO_CSS)
    destino = os.path.join(SAIDA, nome + ".final.html")
    open(destino, "w", encoding="utf-8").write(html)
    return destino


def fotografar(pares):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for nome, html in pares:
            pg.goto("file:///" + html.replace("\\", "/"))
            pg.wait_for_timeout(900)
            png = os.path.join(SAIDA, nome + ".png")
            pg.screenshot(path=png, clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
            print(png)
        b.close()


if __name__ == "__main__":
    nomes = sys.argv[1:] or sorted(os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(AQUI, "arte*.html")))
    fotografar([(n, montar(n)) for n in nomes])
