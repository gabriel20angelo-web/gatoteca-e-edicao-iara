# -*- coding: utf-8 -*-
"""SERIE ENVELOPE do Clube de Literatura Entrelinhas: pecas comuns aos posts de divulgacao.

O post e a frente de um envelope de papel texturizado; cada edicao troca a cor da borda de correio
aereo, a carta-heroi e o lacre. Tudo em papel (papel.py), nada chapado.
"""
import os, sys, math, base64
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from papel import papel, rasgado
import cartinhas as C
from cartinhas import estrela8, imagem, gato, elem, JADE, JADE_E, ROSA, ROSA_C, NOITE, AMEIXA, PEROLA, OURO
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[2]  # raiz do repositório

W, H = 1080, 1350
ENVELOPE = "#EFE2D4"
TINTA = "#3B2A33"
LOGO = str(_REPO / 'gatoteca/motor/assets/logo_tulipa.png')
D = str(_REPO / 'gatoteca/artes')


def b64(c):
    return "data:image/png;base64," + base64.b64encode(open(c, "rb").read()).decode()


def textura(x, y, w, h, cor, seed, **kw):
    return '<image href="%s" x="%g" y="%g" width="%g" height="%g" preserveAspectRatio="none"/>' % (b64(papel(int(w), int(h), cor, seed, **kw)), x, y, w, h)


def folha(uid, d, x, y, w, h, cor, seed, sombra=True, fibra_borda="#FBF6EE", **kw):
    s = ''
    if sombra:
        s += '<path d="%s" fill="#2A1A20" opacity=".36" filter="url(#sombraPapel)" transform="translate(5 10)"/>' % d
    s += '<path d="%s" fill="none" stroke="%s" stroke-width="3.2" stroke-linejoin="round" opacity=".9"/>' % (d, fibra_borda)
    s += '<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)">%s</g>' % (uid, d, uid, textura(x, y, w, h, cor, seed, **kw))
    return s


def correio_aereo(c1, c2, larg=24):
    s = ['<clipPath id="bordaCA"><path d="M0,0 H%d V%d H0Z M%d,%d V%d H%d V%dZ" clip-rule="evenodd"/></clipPath>' % (W, H, larg, larg, H - larg, W - larg, larg)]
    s.append('<g clip-path="url(#bordaCA)" opacity=".9">')
    k = 0
    for t in range(-H, W + H, 44):
        s.append('<path d="M%d,0 L%d,0 L%d,%d L%d,%dZ" fill="%s"/>' % (t, t + 22, t + 22 - H, H, t - H, H, (c1, c2)[k % 2]))
        k += 1
    s.append('</g><path d="M%d,%d H%d V%d H%dZ" fill="none" stroke="%s" stroke-width="1.2" opacity=".35"/>' % (larg + 8, larg + 8, W - larg - 8, H - larg - 8, larg + 8, TINTA))
    return "".join(s)


def fita(cx, cy, w, h, rot, cor="#E6C4D0", seed=5):
    d = rasgado(-w / 2, -h / 2, w, h, seed, amp=1.2, passo=5, lados="lr")
    return ('<g transform="translate(%g %g) rotate(%g)" opacity=".86">' % (cx, cy, rot) +
            '<clipPath id="fita%d"><path d="%s"/></clipPath><g clip-path="url(#fita%d)">%s</g>' % (seed, d, seed, textura(-w / 2, -h / 2, w, h, cor, seed, relevo=.15, fibras=1.5, borda=0)) +
            '<path d="%s" fill="#FFFFFF" opacity=".18"/></g>' % d)


def clipe(x, y, rot=0, k=1.0):
    d = "M0,0 L0,-62 A13,13 0 0 1 26,-62 L26,38 A19,19 0 0 1 -12,38 L-12,-44"
    return ('<g transform="translate(%g %g) rotate(%g) scale(%g)" fill="none" stroke-linecap="round">' % (x, y, rot, k) +
            '<path d="%s" stroke="%s" stroke-width="6.5"/><path d="%s" stroke="%s" stroke-width="3.6"/>' % (d, TINTA, d, OURO) +
            '<path d="%s" stroke="#FFF3C6" stroke-width="1.2" opacity=".7" transform="translate(-.8 -.8)"/></g>' % d)


def cancelamento(x0, x1, y0, n=5, passo=20):
    s = ""
    for i in range(n):
        y = y0 + i * passo
        d = "M%g,%g" % (x0, y)
        x = x0
        while x < x1:
            d += " q%g,-9 %g,0 t%g,0" % (13, 26, 26)
            x += 52
        s += '<path d="%s" fill="none" stroke="%s" stroke-width="2.6" opacity=".62"/>' % (d, TINTA)
    return '<g filter="url(#tinta)">%s</g>' % s


def lockup(sub, sub_fonte="Cormorant"):
    s = '<text x="74" y="98" font-family="Special Elite" font-size="19" fill="%s" opacity=".8">REMETENTE</text>' % TINTA
    s += '<text x="72" y="160" font-family="Cinzel" font-weight="700" font-size="48" letter-spacing="3" fill="%s">CLUBE DE LITERATURA</text>' % AMEIXA
    s += '<text x="66" y="272" font-family="DM Serif Display" font-size="124" fill="%s">Entrelinhas</text>' % JADE_E
    if sub_fonte == "Caveat":
        s += '<text x="78" y="326" font-family="Caveat" font-weight="700" font-size="50" fill="%s" transform="rotate(-2 78 326)">%s</text>' % sub
    else:
        s += '<text x="74" y="322" font-family="Cormorant" font-style="italic" font-weight="700" font-size="34" fill="%s">%s</text>' % sub
    return s


def para_mao(x, y, txt="Para: quem lê nas entrelinhas", rot=-3, cor=AMEIXA):
    return ('<text x="%g" y="%g" font-family="Caveat" font-weight="700" font-size="42" fill="%s" transform="rotate(%g %g %g)">%s</text>' % (x, y, cor, rot, x, y, txt) +
            '<path d="M%g,%g q60,10 120,2 t120,0" fill="none" stroke="%s" stroke-width="2" opacity=".55" transform="rotate(%g %g %g)"/>' % (x + 70, y + 12, cor, rot, x, y))


def etiqueta(cx, cy, w, linhas, rot, seed=31, cor="#FAF5EE", tam=30):
    """linhas = [(rotulo, valor), ...]; rotulo vazio = continua a linha de cima."""
    y, alturas = 74, []
    for i, (r, _) in enumerate(linhas):
        alturas.append(y)
        prox = linhas[i + 1][0] if i + 1 < len(linhas) else None
        y += 76 if prox else 40
    h = alturas[-1] + 44
    d = rasgado(0, 0, w, h, seed, amp=2.2, passo=6, lados="tblr")
    s = '<g transform="translate(%g %g) rotate(%g) translate(%g %g)">' % (cx, cy, rot, -w / 2, -h / 2)
    s += folha("etq%d" % seed, d, 0, 0, w, h, cor, seed + 1, forca=1.4)
    for (r, txt), y in zip(linhas, alturas):
        if r:
            s += '<text x="34" y="%g" font-family="Cinzel" font-weight="700" font-size="15" letter-spacing="3" fill="%s">%s</text>' % (y - 33, JADE_E, r)
        s += '<text x="34" y="%g" font-family="Special Elite" font-size="%g" fill="%s">%s</text>' % (y, tam, TINTA, txt)
        s += '<path d="M30,%g H%g" stroke="%s" stroke-width="1.1" opacity=".35" stroke-dasharray="1 4"/>' % (y + 10, w - 30, TINTA)
    return s + '</g>', h


def tira_cta(y, cor, l1, l2, h=112, tinta1=PEROLA, tinta2="#F6E4EA"):
    d = rasgado(-20, y, W + 40, h, 41, amp=3, passo=6, lados="tb", morder=.04)
    s = folha("cta", d, -20, y - 6, W + 40, h + 12, cor, 42, forca=1.6)
    s += '<text x="540" y="%g" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="30" letter-spacing="4" fill="%s">%s</text>' % (y + 50, tinta1, l1)
    s += '<text x="540" y="%g" text-anchor="middle" font-family="Cormorant" font-style="italic" font-weight="700" font-size="33" fill="%s">%s</text>' % (y + 90, tinta2, l2)
    return s


def pagina(titulo, corpo, defs_extra=""):
    defs = '<filter id="sombraPapel" x="-10%" y="-10%" width="120%" height="130%"><feGaussianBlur stdDeviation="10"/></filter>' + C.DEFS + defs_extra
    css = ('*{margin:0;padding:0}html,body{width:1080px;height:1350px;background:%s}.peca{position:relative;width:1080px;height:1350px;overflow:hidden}'
           '.peca>svg{position:absolute;left:0;top:0}') % ENVELOPE
    return ('<!doctype html><html><head><meta charset="utf-8"><title>%s</title>\n<!--ACERVO-->\n<style>%s</style></head>'
            '<body><div class="peca"><svg width="1080" height="1350" viewBox="0 0 1080 1350"><defs>%s</defs>%s</svg></div></body></html>') % (titulo, css, defs, corpo)


def exportar(nome, html, arquivo_final):
    import montar
    from playwright.sync_api import sync_playwright
    html = html.replace("<!--ACERVO-->", montar.ACERVO_CSS)
    arq = os.path.join(AQUI, "saida", nome + ".final.html")
    open(arq, "w", encoding="utf-8").write(html)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for esc, destino in ((1, os.path.join(AQUI, "saida", nome + ".png")), (1, os.path.join(D, arquivo_final)),
                             (2, os.path.join(D, "alta resolução (2160x2700)", arquivo_final))):
            pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=esc)
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(1500)
            pg.screenshot(path=destino)
        b.close()


def bilhete(x, y, txt="vem com a gente? ♡", rot=-4, cor=AMEIXA, tam=44):
    return '<text x="%g" y="%g" text-anchor="middle" font-family="Caveat" font-weight="700" font-size="%g" fill="%s" transform="rotate(%g %g %g)">%s</text>' % (x, y, tam, cor, rot, x, y, txt)
