# -*- coding: utf-8 -*-
"""Edicao de Halloween no Parque da Jaqueira, v4 (serie envelope): borda laranja e roxa, cartao-postal
com a cena da jaqueira (a arvore, a jaca-lanterna, o gatinho e o piquenique), morcegos saindo do cartao
para o envelope, ingresso destacavel, mascote de chapeu de bruxa no selo.
uso: py post_halloween4.py
"""
import os, sys, random
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import envelope as E
from envelope import *
import pecas as P
from variacoes import COPA_VIVA

LARANJA, ROXO, ABOBORA_E = "#E8752F", "#4A3468", "#B8501C"


def postal(cx, cy, w, h, rot, base=82, borda=22):
    iw, ih = w - 2 * borda, h - borda - base
    random.seed(4)
    est = "".join('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="#F4E9D5" opacity="%.2f"/>' % (random.random() * iw, random.random() * ih * .6, .8 + random.random() * 1.4, .4 + random.random() * .5) for _ in range(46))
    vg = "".join('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="#FFE07A"/>' % (30 + random.random() * (iw - 60), ih * .55 + random.random() * ih * .3, 1.6 + random.random() * 1.6) for _ in range(14))
    chao = 'M0,%g C140,%g 300,%g %g,%g V%g H0Z' % (ih - 72, ih - 86, ih - 64, iw, ih - 80, ih)
    cena = (textura(0, 0, iw, ih, "#26304E", 61, forca=1.4) +
            '<rect width="%g" height="%g" fill="url(#ceuHalloween)"/>' % (iw, ih) + est +
            P.lua(iw - 120, 106, 58, linha="#F2D27E", opac_raios=.45) +
            P.morcegos([(118, 92, 1.5, -8), (176, 58, 1.0, 10), (iw - 70, 238, .8, 6)], "#1B1426") +
            '<path d="%s" fill="#3F7A5A"/><path d="%s" fill="#4E8A5C" filter="url(#aguada)"/>' % (chao, chao) +
            P.arvore(250, ih - 66, .76, COPA_VIVA) +
            P.piquenique(14, ih - 104, 1.06) +
            P.gato(iw - 96, ih - 40, 1.0) +
            P.abobora(iw - 34, ih - 44, 1.05) + P.abobora(iw - 58, ih - 32, .64, "--abobora:#F2B544") +
            '<g filter="url(#brilho2)">%s</g>%s' % (vg, vg.replace('fill="#FFE07A"', 'fill="#FFF6C8" opacity=".9"')))
    s = '<g transform="translate(%g %g) rotate(%g) translate(%g %g)">' % (cx, cy, rot, -w / 2, -h / 2)
    d = rasgado(0, 0, w, h, 71, amp=.9, passo=5)
    s += folha("postal", d, 0, 0, w, h, "#FBF6EE", 72, forca=1.3)
    s += '<clipPath id="cena"><rect x="%g" y="%g" width="%g" height="%g"/></clipPath>' % (borda, borda, iw, ih)
    s += '<g clip-path="url(#cena)"><g transform="translate(%g %g)">%s</g></g>' % (borda, borda, cena)
    s += '<rect x="%g" y="%g" width="%g" height="%g" fill="none" stroke="%s" stroke-width="1.2" opacity=".4"/>' % (borda, borda, iw, ih, TINTA)
    s += '<text x="%g" y="%g" font-family="Special Elite" font-size="25" fill="%s">Parque da Jaqueira · Recife</text>' % (borda + 6, h - 32, TINTA)
    s += '<text x="%g" y="%g" text-anchor="end" font-family="Caveat" font-weight="700" font-size="40" fill="%s" transform="rotate(-4 %g %g)">31.10</text>' % (w - borda - 6, h - 28, ABOBORA_E, w - borda - 6, h - 28)
    return s + '</g>'


def ingresso(cx, cy, rot):
    w, h = 320, 128
    d = rasgado(0, 0, w, h, 81, amp=.8, passo=5, lados="tbr")
    s = '<g transform="translate(%g %g) rotate(%g) translate(%g %g)">' % (cx, cy, rot, -w / 2, -h / 2)
    s += folha("ingr", d, 0, 0, w, h, "#E9B9C9", 82, forca=1.3)
    s += '<path d="M232,8 V%g" stroke="%s" stroke-width="2" stroke-dasharray="2 7" opacity=".55"/>' % (h - 8, TINTA)
    s += '<text x="22" y="40" font-family="Cinzel" font-weight="700" font-size="15" letter-spacing="5" fill="%s">ENTRADA</text>' % TINTA
    s += '<text x="20" y="98" font-family="DM Serif Display" font-size="58" fill="%s">R$ 30</text>' % ROXO
    s += '<text x="276" y="%g" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="15" letter-spacing="2" fill="%s" transform="rotate(-90 276 %g)">20 VAGAS</text>' % (h / 2 + 4, TINTA, h / 2 + 4)
    return s + '</g>'


def peca():
    corpo = textura(0, 0, W, H, ENVELOPE, 13, forca=2.0)
    corpo += correio_aereo(LARANJA, ROXO)
    corpo += lockup(("edição de Halloween", ABOBORA_E)[::-1], "Caveat")
    corpo += C.carimbo(790, 208, 66, -14, "RECIFE · JAQUEIRA", "31 OUT", "2026")
    corpo += C.selo_postal(944, 176, 168, 208, imagem(gato("28"), 0, 2, h=150), "R$ 30", 6, ROXO)
    corpo += cancelamento(840, 1010, 176, 4, 22)
    corpo += postal(326, 712, 526, 556, -4)
    corpo += P.morcegos([(626, 392, 2.6, -14), (712, 336, 1.9, 8), (590, 330, 1.3, -6), (560, 300, .9, 10)], "#2A1626")
    corpo += para_mao(612, 612, rot=-3)
    etq, h = etiqueta(814, 878, 432, [("QUANDO", "sábado, 31 de outubro"), ("", "às 15h"), ("ONDE", "Parque da Jaqueira"),
                                       ("INCLUI", "ecobag, marcador,"), ("", "café, bolo e frutinhas"), ("E MAIS", "sorteio de um livro")], 3, tam=29)
    corpo += etq + clipe(984, 690, 8)
    corpo += imagem(elem("1 Lacres e selos", "lacre_cogumelos"), 984, 1100, 120, rot=-12)
    corpo += ingresso(252, 1098, 5)
    corpo += bilhete(730, 1160, "vem ler com a gente? ♡", rot=-4)
    corpo += tira_cta(1214, ROXO, "GARANTA SUA VAGA PELO LINK ABAIXO ↓", "e entre no grupo do WhatsApp do clube", tinta2="#F2D9E3")
    extra = (P.DEFS + P.SIMBOLOS +
             '<linearGradient id="ceuHalloween" x1="0" y1="0" x2="0" y2="1"><stop offset=".3" stop-color="#5A3C6E" stop-opacity="0"/>'
             '<stop offset="1" stop-color="#7A4A72" stop-opacity=".75"/></linearGradient>')
    return pagina("Entrelinhas · Halloween (v4)", corpo, extra)


if __name__ == "__main__":
    exportar("post_halloween4", peca(), "Halloween na Jaqueira - post v4 (envelope).png")
    print("ok")
