# -*- coding: utf-8 -*-
"""Lilith × TULIPA, v4 (serie envelope): a carta de Lilith e a protagonista; TULIPA como carimbo postal
sob o selo; etiqueta so com quando/onde/quanto; «Para» escrito a mao no envelope. Encontros as 14h.
uso: py post_lilith4.py
"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import envelope as E
from envelope import *
import post_lilith2 as L2


def carta_lilith(cx, cy, w, h, rot):
    r = w / 2
    arco = "M0,%g V%g A%g,%g 0 0 1 %g,%g V%gZ" % (h, r, r, r, w, r, h)
    d_in = "M18,%g V%g A%g,%g 0 0 1 %g,%g V%gZ" % (h - 18, r, r - 18, r - 18, w - 18, r, h - 18)
    d_in2 = "M27,%g V%g A%g,%g 0 0 1 %g,%g V%gZ" % (h - 27, r, r - 27, r - 27, w - 27, r, h - 27)
    mx, my, mr = w / 2, 300, 186
    defs_g, gata = L2.lilith_limpa(mx, my + mr - 26, .84)
    lua = ('<defs><radialGradient id="luaClara" cx="40%" cy="38%" r="70%"><stop offset="0" stop-color="#FFF5D6"/>'
           '<stop offset=".7" stop-color="#F3DFA6"/><stop offset="1" stop-color="#E2C27A"/></radialGradient></defs>' +
           '<circle cx="%g" cy="%g" r="%g" fill="#F3DFA6" opacity=".38" filter="url(#brilho)"/>' % (mx, my, mr + 20) +
           '<circle cx="%g" cy="%g" r="%g" fill="url(#luaClara)"/>' % (mx, my, mr) +
           "".join('<circle cx="%g" cy="%g" r="%g" fill="#D9B46A" opacity=".35"/>' % (mx + a, my + b, c) for a, b, c in ((-78, -66, 24), (66, -106, 13), (98, 22, 18), (-104, 46, 11))))
    estrelas = "".join(estrela8(x, y, s_, ROSA, "#1A1720", 1.2) for x, y, s_ in ((64, 170, 13), (w - 64, 140, 11), (54, 430, 9), (w - 50, 420, 12), (w - 120, 84, 7), (120, 70, 6)))
    s = '<g transform="translate(%g %g) rotate(%g) translate(%g %g)">' % (cx, cy, rot, -w / 2, -h / 2)
    s += '<path d="%s" fill="#14101A" opacity=".45" filter="url(#sombraPapel)" transform="translate(7 14)"/>' % arco
    s += '<clipPath id="cartaL"><path d="%s"/></clipPath><g clip-path="url(#cartaL)">' % arco
    s += textura(0, 0, w, h, "#2E2A36", 21, forca=1.6) + lua + estrelas + gata + '</g>'
    s += '<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/><path d="%s" fill="none" stroke="%s" stroke-width="1.1" opacity=".8"/>' % (d_in, OURO, d_in2, OURO)
    s += '<text x="%g" y="%g" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="16" letter-spacing="6" fill="%s">TEMA DO ENCONTRO</text>' % (w / 2, h - 182, OURO)
    s += '<path d="M44,%g H%g" stroke="%s" stroke-width="1.4"/>' % (h - 166, w - 44, OURO)
    s += '<text x="%g" y="%g" text-anchor="middle" font-family="DM Serif Display" font-size="112" fill="%s">Lilith</text>' % (w / 2, h - 72, ROSA_C)
    s += '<text x="%g" y="%g" text-anchor="middle" font-family="Cormorant" font-style="italic" font-weight="700" font-size="30" fill="%s">a primeira mulher, a que não se curvou</text>' % (w / 2, h - 36, PEROLA)
    return defs_g, s + '</g>'


def peca():
    corpo = textura(0, 0, W, H, ENVELOPE, 11, forca=2.0)
    corpo += correio_aereo(ROSA, JADE)
    corpo += lockup((AMEIXA, "em parceria com a TULIPA · UNICAP"))
    # correio: a TULIPA vira o carimbo postal sob o selo, com o cancelamento passando pelos dois
    corpo += imagem(LOGO, 772, 206, 142, rot=-10)
    corpo += C.selo_postal(944, 176, 168, 208, imagem(gato("01"), 0, -6, h=140), "grátis", 6)
    corpo += cancelamento(806, 1010, 176, 4, 22)
    # a carta (protagonista) e as informacoes
    defs_g, carta = carta_lilith(330, 812, 524, 770, -4)
    corpo += '<defs>%s</defs>' % defs_g + carta
    corpo += fita(318, 432, 210, 58, -8, seed=51)
    corpo += para_mao(588, 556, rot=-3)
    etq, h = etiqueta(806, 790, 420, [("QUANDO", "quintas, às 14h"), ("", "a cada 15 dias"), ("ONDE", "sala 713 · bloco B"), ("", "UNICAP"),
                                       ("QUANTO", "gratuito e aberto")], 3, tam=33)
    corpo += etq + clipe(968, 640, 8)
    corpo += imagem(elem("1 Lacres e selos", "lacre_vinho_lua"), 972, 990, 128, rot=-14)
    corpo += bilhete(842, 1128)
    corpo += tira_cta(1214, JADE, "INSCREVA-SE PELO LINK ABAIXO ↓", "e entre no grupo do WhatsApp do clube")
    return pagina("Entrelinhas · Lilith (v4)", corpo)


if __name__ == "__main__":
    exportar("post_lilith4", peca(), "Lilith × TULIPA - post v4 (envelope, 14h).png")
    print("ok")
