# -*- coding: utf-8 -*-
"""Post Lilith × TULIPA, versao 3 (do zero): O ENVELOPE.

O post inteiro e a frente de um envelope de papel texturizado, com borda de correio aereo (rosa e jade):
remetente impresso «CLUBE DE LITERATURA / Entrelinhas», selo com o mascote e carimbo, a carta de Lilith
(papel escuro, Lilith-gata contra a lua clara) presa com fita, etiqueta de endereco datilografada com as
informacoes e a chamada numa tira de papel rasgado. Tudo com textura de papel (papel.py), nada chapado.
uso: py post_lilith3.py
"""
import os, sys, math, base64
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "mascote"))
import montar
from papel import papel, rasgado
import cartinhas as C
from cartinhas import estrela8, selo_postal, carimbo, imagem, gato, elem, JADE, JADE_E, ROSA, ROSA_C, NOITE, AMEIXA, PEROLA, OURO
import post_lilith2 as L2
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[2]  # raiz do repositório

D = str(_REPO / 'gatoteca/artes')
LOGO = str(_REPO / 'gatoteca/motor/assets/logo_tulipa.png')
W, H = 1080, 1350
ENVELOPE = "#EFE2D4"
TINTA = "#3B2A33"


def b64(c):
    return "data:image/png;base64," + base64.b64encode(open(c, "rb").read()).decode()


def textura(x, y, w, h, cor, seed, **kw):
    return '<image href="%s" x="%g" y="%g" width="%g" height="%g" preserveAspectRatio="none"/>' % (b64(papel(int(w), int(h), cor, seed, **kw)), x, y, w, h)


def folha(uid, d, x, y, w, h, cor, seed, sombra=True, fibra_borda="#FBF6EE", **kw):
    """Pedaco de papel: forma d preenchida com textura, borda clara de rasgo e sombra."""
    s = ''
    if sombra:
        s += '<path d="%s" fill="#2A1A20" opacity=".38" filter="url(#sombraPapel)" transform="translate(4 9)"/>' % d
    s += '<path d="%s" fill="none" stroke="%s" stroke-width="3.2" stroke-linejoin="round" opacity=".9"/>' % (d, fibra_borda)
    s += '<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)">%s</g>' % (uid, d, uid, textura(x, y, w, h, cor, seed, **kw))
    return s


def correio_aereo(larg=30):
    """Borda de envelope de correio aereo: paralelogramos rosa e jade alternados."""
    s = ['<clipPath id="bordaCA"><path d="M0,0 H%d V%d H0Z M%d,%d V%d H%d V%dZ" clip-rule="evenodd"/></clipPath>' % (W, H, larg, larg, H - larg, W - larg, larg)]
    s.append('<g clip-path="url(#bordaCA)" opacity=".92">')
    passo, k = 46, 0
    for t in range(-H, W + H, passo):
        cor = (ROSA, JADE)[k % 2]
        s.append('<path d="M%d,0 L%d,0 L%d,%d L%d,%dZ" fill="%s"/>' % (t, t + 24, t + 24 - H, H, t - H, H, cor))
        k += 1
    s.append('</g>')
    return "".join(s)


def fita(cx, cy, w, h, rot, cor="#E6C4D0", seed=5):
    d = rasgado(-w / 2, -h / 2, w, h, seed, amp=1.2, passo=5, lados="lr")
    return ('<g transform="translate(%g %g) rotate(%g)" opacity=".86">' % (cx, cy, rot) +
            '<clipPath id="fita%d"><path d="%s"/></clipPath><g clip-path="url(#fita%d)">%s</g>' % (seed, d, seed, textura(-w / 2, -h / 2, w, h, cor, seed, relevo=.15, fibras=1.5, borda=0)) +
            '<path d="%s" fill="#FFFFFF" opacity=".18"/></g>' % d)


def carta_lilith(cx, cy, w, h, rot):
    """Carta de papel escuro em arco (tarot), lua clara e a Lilith-gata em silhueta nitida."""
    r = w / 2
    arco = "M0,%g V%g A%g,%g 0 0 1 %g,%g V%gZ" % (h, r, r, r, w, r, h)
    d_in = "M18,%g V%g A%g,%g 0 0 1 %g,%g V%gZ" % (h - 18, r, r - 18, r - 18, w - 18, r, h - 18)
    d_in2 = "M27,%g V%g A%g,%g 0 0 1 %g,%g V%gZ" % (h - 27, r, r - 27, r - 27, w - 27, r, h - 27)
    mx, my, mr = w / 2, 268, 168
    defs_g, gata = L2.lilith_limpa(mx, my + mr - 24, .74)
    lua = ('<defs><radialGradient id="luaClara" cx="40%" cy="38%" r="70%"><stop offset="0" stop-color="#FFF5D6"/>'
           '<stop offset=".7" stop-color="#F3DFA6"/><stop offset="1" stop-color="#E2C27A"/></radialGradient></defs>' +
           '<circle cx="%g" cy="%g" r="%g" fill="#F3DFA6" opacity=".38" filter="url(#brilho)"/>' % (mx, my, mr + 18) +
           '<circle cx="%g" cy="%g" r="%g" fill="url(#luaClara)"/>' % (mx, my, mr) +
           ''.join('<circle cx="%g" cy="%g" r="%g" fill="#D9B46A" opacity=".35"/>' % (mx + a, my + b, c) for a, b, c in ((-70, -60, 22), (60, -96, 12), (88, 20, 16), (-96, 40, 10))))
    estrelas = "".join(estrela8(x, y, s_, ROSA, "#1A1720", 1.2) for x, y, s_ in ((70, 150, 13), (w - 70, 120, 11), (60, 400, 9), (w - 56, 380, 12), (w - 110, 60 + r * .3, 7)))
    s = '<g transform="translate(%g %g) rotate(%g) translate(%g %g)">' % (cx, cy, rot, -w / 2, -h / 2)
    s += '<path d="%s" fill="#14101A" opacity=".45" filter="url(#sombraPapel)" transform="translate(6 12)"/>' % arco
    s += '<clipPath id="cartaL"><path d="%s"/></clipPath><g clip-path="url(#cartaL)">' % arco
    s += textura(0, 0, w, h, "#2E2A36", 21, forca=1.6)
    s += lua + estrelas + gata + '</g>'
    s += '<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/><path d="%s" fill="none" stroke="%s" stroke-width="1.1" opacity=".8"/>' % (d_in, OURO, d_in2, OURO)
    s += '<path d="M40,%g H%g" stroke="%s" stroke-width="1.4"/>' % (h - 150, w - 40, OURO)
    s += ('<text x="%g" y="%g" text-anchor="middle" font-family="DM Serif Display" font-size="96" fill="%s">Lilith</text>' % (w / 2, h - 66, ROSA_C))
    s += ('<text x="%g" y="%g" text-anchor="middle" font-family="Cormorant" font-style="italic" font-weight="700" font-size="27" fill="%s">a primeira mulher, a que não se curvou</text>' % (w / 2, h - 32, PEROLA))
    s += '<text x="%g" y="%g" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="15" letter-spacing="6" fill="%s">TEMA DO ENCONTRO</text>' % (w / 2, h - 166, OURO)
    return defs_g, s + '</g>'


def etiqueta(cx, cy, w, h, rot):
    d = rasgado(0, 0, w, h, 31, amp=2.2, passo=6, lados="tblr")
    linhas = [("PARA", "quem lê nas entrelinhas"), ("QUANDO", "quintas, às 13h"), ("", "a cada 15 dias"),
              ("ONDE", "sala 713 · bloco B"), ("", "UNICAP"), ("QUANTO", "gratuito e aberto")]
    s = '<g transform="translate(%g %g) rotate(%g) translate(%g %g)">' % (cx, cy, rot, -w / 2, -h / 2)
    s += folha("etq", d, 0, 0, w, h, "#FAF5EE", 32, forca=1.4)
    y = 76
    for i, (rot_, txt) in enumerate(linhas):
        if rot_:
            s += '<text x="34" y="%g" font-family="Cinzel" font-weight="700" font-size="15" letter-spacing="3" fill="%s">%s</text>' % (y - 33, JADE_E, rot_)
        s += '<text x="34" y="%g" font-family="Special Elite" font-size="29" fill="%s">%s</text>' % (y, TINTA, txt)
        s += '<path d="M30,%g H%g" stroke="%s" stroke-width="1.1" opacity=".35" stroke-dasharray="1 4"/>' % (y + 10, w - 30, TINTA)
        prox = linhas[i + 1][0] if i + 1 < len(linhas) else ""
        y += 78 if prox else 40
    return s + '</g>'


def tira_cta(y, h=118):
    d = rasgado(-20, y, W + 40, h, 41, amp=3, passo=6, lados="tb", morder=.04)
    s = folha("cta", d, -20, y - 6, W + 40, h + 12, JADE, 42, forca=1.6)
    s += '<text x="540" y="%g" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="31" letter-spacing="4" fill="%s">INSCREVA-SE PELO LINK ABAIXO ↓</text>' % (y + 52, PEROLA)
    s += '<text x="540" y="%g" text-anchor="middle" font-family="Cormorant" font-style="italic" font-weight="700" font-size="33" fill="%s">e entre no grupo do WhatsApp do clube</text>' % (y + 94, "#F6E4EA")
    return s


def peca():
    corpo = textura(0, 0, W, H, ENVELOPE, 11, forca=2.0)
    corpo += correio_aereo(30)
    # remetente
    corpo += '<text x="78" y="104" font-family="Special Elite" font-size="19" fill="%s" opacity=".8">REMETENTE</text>' % TINTA
    corpo += '<text x="76" y="166" font-family="Cinzel" font-weight="700" font-size="47" letter-spacing="3" fill="%s">CLUBE DE LITERATURA</text>' % AMEIXA
    corpo += '<text x="70" y="278" font-family="DM Serif Display" font-size="122" fill="%s">Entrelinhas</text>' % JADE_E
    corpo += '<text x="78" y="326" font-family="Cormorant" font-style="italic" font-weight="700" font-size="33" fill="%s">em parceria com a TULIPA · UNICAP</text>' % AMEIXA
    corpo += '<path d="M78,350 H560" stroke="%s" stroke-width="1.4" opacity=".45"/>' % AMEIXA
    # correio: selo, carimbo de ondas e o selo da TULIPA como segundo carimbo
    corpo += selo_postal(912, 168, 172, 212, imagem(gato("01"), 0, -6, h=142), "grátis", 6)
    corpo += carimbo(806, 210, 66, -16, "RECIFE · UNICAP", "QUI", "13H")
    corpo += imagem(LOGO, 946, 372, 150, rot=-8)
    # a carta de Lilith presa com fita, e a etiqueta
    defs_g, carta = carta_lilith(318, 820, 452, 690, -4.5)
    corpo += '<defs>%s</defs>' % defs_g
    corpo += imagem(elem("2 Astros", "estrela_dourada_8_longa"), 96, 470, 120, rot=-12)
    corpo += carta
    corpo += fita(300, 486, 200, 56, -9, seed=51)
    corpo += etiqueta(806, 790, 436, 452, 2.5)
    corpo += fita(800, 566, 150, 48, 6, "#B9D3CB", seed=52)
    corpo += imagem(elem("1 Lacres e selos", "lacre_vinho_lua"), 944, 1046, 128, rot=-14)
    corpo += tira_cta(1196)
    defs = ('<filter id="sombraPapel" x="-10%" y="-10%" width="120%" height="130%"><feGaussianBlur stdDeviation="10"/></filter>' + C.DEFS)
    css = ('*{margin:0;padding:0}html,body{width:1080px;height:1350px;background:%s}.peca{position:relative;width:1080px;height:1350px;overflow:hidden}'
           '.peca>svg{position:absolute;left:0;top:0}') % ENVELOPE
    return ('<!doctype html><html><head><meta charset="utf-8"><title>Entrelinhas · Lilith (envelope)</title>\n<!--ACERVO-->\n<style>%s</style></head>'
            '<body><div class="peca"><svg width="1080" height="1350" viewBox="0 0 1080 1350"><defs>%s</defs>%s</svg></div></body></html>') % (css, defs, corpo)


if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    html = peca().replace("<!--ACERVO-->", montar.ACERVO_CSS)
    arq = os.path.join(AQUI, "saida", "post_lilith3.final.html")
    open(arq, "w", encoding="utf-8").write(html)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for esc, destino in ((1, os.path.join(AQUI, "saida", "post_lilith3.png")),
                             (1, os.path.join(D, "Lilith × TULIPA - post v3 (envelope).png")),
                             (2, os.path.join(D, "alta resolução (2160x2700)", "Lilith × TULIPA - post v3 (envelope).png"))):
            pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=esc)
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(1500)
            pg.screenshot(path=destino)
        b.close()
    print("ok")
