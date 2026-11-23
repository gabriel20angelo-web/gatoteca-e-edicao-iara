# -*- coding: utf-8 -*-
"""BANCO DE POSES, parte 2 (27-56): acessorios, objetos, amigos, pensando e brincando.

Acessorios de cabeca sao desenhados em coordenadas locais do rosto (centro 0,0; topo da cabeca ~ -89;
olhos em (+-41, 0); nariz 16-26; boca 26-44; orelhas com ponta em (+-82,-130)).
Objetos ficam em coordenadas da pose (chao em y=0; no gato sentado a cabeca esta em (0,-262)).
uso: py gato_banco2.py [27 28 ...]
"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gato_banco as G
from gato_banco import (pose, Pose, sentado, sentado_barriga, em_pe, membro, rabo, elipse, capsula, contorno, brilho,
                        coracao, livro_fechado, livro_aberto_costas, olho_brilho, texto_simb, gota, AMEIXA, TINTA, BRANCO, PRETO)
from shapely.geometry import box
from shapely.ops import unary_union

OURO, VERM, LARJ, ROXO = "#E3B04B", "#C8324F", "#E8752F", "#4A3468"
LARANJA = dict(base="#EFA25A", escuro="#C9662E", medio="#E08C45", claro="#FFD49A", borda="#A9521F")
CINZA = dict(base="#A29EAE", escuro="#5E5A68", medio="#8A8598", claro="#DAD6E4", borda="#4B4754")

G.DEFS_EXTRA = G.F.DEFS + (
    '<radialGradient id="cristal" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#F3E8FF"/><stop offset=".45" stop-color="#B9A2E0"/><stop offset="1" stop-color="#5B4A9A"/></radialGradient>'
    '<radialGradient id="chama" cx="50%" cy="65%" r="60%"><stop offset="0" stop-color="#FFF6C8"/><stop offset=".5" stop-color="#FFC94A"/><stop offset="1" stop-color="#F07A2A"/></radialGradient>'
    '<radialGradient id="aboboraLuz" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="#FFF3B0"/><stop offset="1" stop-color="#F2A93C"/></radialGradient>'
    '<pattern id="bolasBrancas" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="5" cy="5" r="3.6" fill="#FFF6EC"/><circle cx="16" cy="16" r="3.6" fill="#FFF6EC"/></pattern>'
    '<pattern id="listrasCachecol" width="28" height="28" patternUnits="userSpaceOnUse" patternTransform="rotate(-20)"><rect width="28" height="28" fill="#E8752F"/><rect width="10" height="28" fill="#F2C94C"/></pattern>'
    '<pattern id="xadrezMarrom" width="16" height="16" patternUnits="userSpaceOnUse"><rect width="16" height="16" fill="#9A6A44"/><rect width="8" height="16" fill="#7B4A2E" opacity=".6"/><rect width="16" height="8" fill="#7B4A2E" opacity=".6"/></pattern>'
)


def g(transf, s):
    return '<g transform="%s">%s</g>' % (transf, s)


# ================================================================== acessorios de cabeca (coordenadas do rosto)
def oculos_redondos():
    s = ""
    for x in (-41, 41):
        s += '<circle cx="%g" cy="2" r="25" fill="#FFFFFF" fill-opacity=".14" stroke="%s" stroke-width="4.2"/>' % (x, OURO)
        s += '<path d="M%g,-12 C%g,-18 %g,-18 %g,-14" fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round" opacity=".8"/>' % (x - 12, x - 6, x + 2, x + 6)
    s += '<path d="M-16,0 C-8,-7 8,-7 16,0 M-66,-2 L-104,-12 M66,-2 L104,-12" fill="none" stroke="%s" stroke-width="4" stroke-linecap="round"/>' % OURO
    return s


def oculos_escuros():
    lente = "M-74,-14 C-72,-24 -18,-24 -12,-12 C-10,10 -24,24 -44,24 C-64,24 -76,6 -74,-14Z"
    s = ""
    for k in (1, -1):
        s += '<path transform="scale(%d 1)" d="%s" fill="#1E1418" fill-opacity=".93" stroke="#E0566E" stroke-width="3.4" stroke-linejoin="round"/>' % (k, lente)
        s += '<path transform="scale(%d 1)" d="M-62,-6 L-48,-18 M-58,6 L-36,-14" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" opacity=".7"/>' % k
    s += '<path d="M-12,-8 C-6,-14 6,-14 12,-8" fill="none" stroke="#E0566E" stroke-width="3.4"/>'
    return s


LENCO_TOPO = "M-114,-22 C-118,-74 -70,-106 0,-106 C70,-106 118,-74 114,-22 C80,-44 -80,-44 -114,-22Z"
LENCO_LADO = "M-114,-22 C-120,22 -108,62 -66,92 L-46,78 C-80,52 -92,14 -88,-36Z"


def lenco():
    forma = LENCO_TOPO + " " + LENCO_LADO + " " + LENCO_LADO.replace("M-", "M").replace(" -", " ").replace("C-", "C").replace("L-", "L")
    # o espelho do lado direito
    dir_ = "M114,-22 C120,22 108,62 66,92 L46,78 C80,52 92,14 88,-36Z"
    s = ""
    for d in (LENCO_TOPO, LENCO_LADO, dir_):
        s += contorno(d, "#D9483B", 2.4) + '<path d="%s" fill="url(#bolasBrancas)"/>' % d
    no = ('<ellipse cx="-18" cy="98" rx="20" ry="12" transform="rotate(-18 -18 98)" fill="#D9483B" stroke="%s" stroke-width="2.4"/>'
          '<ellipse cx="18" cy="98" rx="20" ry="12" transform="rotate(18 18 98)" fill="#D9483B" stroke="%s" stroke-width="2.4"/>'
          '<path d="M-6,104 L-30,144 L-10,138Z M6,104 L30,144 L10,138Z" fill="#D9483B" stroke="%s" stroke-width="2.2" stroke-linejoin="round"/>'
          '<circle cx="0" cy="100" r="9" fill="#B8362C" stroke="%s" stroke-width="2.2"/>') % (AMEIXA, AMEIXA, AMEIXA, AMEIXA)
    return s + no


def chapeu(cor="#4A3468", faixa=LARJ, alto=250, ponta=40, estrelas=True, lua=False):
    cone = "M-66,-80 C-50,-150 -20,-%d %g,-%d C30,-%d %g,-%d %g,-%d C50,-%d 34,-%d 30,-%d C40,-160 58,-120 66,-80Z" % (
        alto - 40, 10, alto, alto + 22, ponta + 24, alto + 20, ponta + 36, alto, alto + 2, alto - 14, alto - 40)
    s = contorno("M-130,-74 C-130,-92 130,-92 130,-74 C130,-56 -130,-56 -130,-74Z", cor, 2.8)
    s += contorno(cone, cor, 2.8)
    s += contorno("M-64,-94 C-20,-106 20,-106 64,-94 L66,-80 C20,-92 -20,-92 -66,-80Z", faixa, 2.4)
    s += brilho(0, -93, 1.1, "#F2C94C")
    if estrelas:
        s += brilho(-20, -150, .9, "#F2C94C") + brilho(22, -190, .7, "#F2C94C") + brilho(-4, -214, .5, "#F2C94C")
    if lua:
        s += '<path d="M14,-160 a20,20 0 1 0 0,40 a15,15 0 1 1 0,-40Z" fill="#F2C94C"/>'
    return s


def chapeu_bruxa():
    return chapeu("#4A3468", LARJ, 250, 40)


def chapeu_mago():
    return chapeu("#2F4A8C", "#F2C94C", 270, 10, True, True)


def coroa():
    s = contorno("M-52,-92 L-56,-138 L-28,-112 L0,-150 L28,-112 L56,-138 L52,-92 C20,-100 -20,-100 -52,-92Z", "#F2C94C", 2.6)
    s += '<circle cx="0" cy="-104" r="7" fill="%s" stroke="%s" stroke-width="1.8"/><circle cx="-32" cy="-100" r="5" fill="#4F67C9"/><circle cx="32" cy="-100" r="5" fill="#4F67C9"/>' % (VERM, AMEIXA)
    s += '<circle cx="0" cy="-150" r="5" fill="#FFF3C6" stroke="%s" stroke-width="1.6"/><circle cx="-56" cy="-138" r="4" fill="#FFF3C6"/><circle cx="56" cy="-138" r="4" fill="#FFF3C6"/>' % AMEIXA
    return g("rotate(-8)", s)


def boina():
    s = contorno("M-70,-70 C-90,-110 0,-140 70,-118 C120,-102 124,-76 96,-66 C40,-50 -40,-50 -70,-70Z", VERM, 2.6)
    s += contorno("M18,-128 C16,-140 26,-146 30,-136", "none", 3)
    s += '<path d="M-50,-80 C-10,-70 40,-74 86,-84" fill="none" stroke="#8E2236" stroke-width="2" opacity=".6"/>'
    return s


def fone():
    s = '<path d="M-108,-4 C-114,-128 114,-128 108,-4" fill="none" stroke="%s" stroke-width="13" stroke-linecap="round"/>' % AMEIXA
    s += '<path d="M-108,-4 C-114,-128 114,-128 108,-4" fill="none" stroke="#7A5A88" stroke-width="7" stroke-linecap="round"/>'
    for x in (-110, 110):
        s += contorno("M%g,-30 C%g,-34 %g,-34 %g,-30 L%g,36 C%g,40 %g,40 %g,36Z" % (x - 20, x - 10, x + 10, x + 20, x + 20, x + 10, x - 10, x - 20), LARJ, 2.6)
    return s


def flor(x=-84, y=-78):
    s = '<g transform="translate(%g %g)">' % (x, y)
    s += contorno("M8,10 C30,12 40,26 38,34 C24,34 12,24 8,10Z", "#78B27A", 2)
    for a in range(0, 360, 72):
        s += '<ellipse cx="0" cy="-16" rx="11" ry="15" transform="rotate(%d)" fill="#F49AB0" stroke="%s" stroke-width="2"/>' % (a, AMEIXA)
    s += '<circle r="9" fill="#F2C94C" stroke="%s" stroke-width="2"/>' % AMEIXA
    return s + '</g>'


# ================================================================== acessorios de corpo (coordenadas da pose)
def gravata(x=0, y=-170, k=1.0):
    s = '<g transform="translate(%g %g) scale(%g)">' % (x, y, k)
    s += contorno("M0,0 L-38,-20 L-40,20 Z", VERM, 2.6) + contorno("M0,0 L38,-20 L40,20 Z", VERM, 2.6)
    s += '<path d="M0,0 L-38,-20 L-40,20Z M0,0 L38,-20 L40,20Z" fill="url(#bolasBrancas)" opacity=".8"/>'
    s += contorno("M-9,-11 L9,-11 L9,11 L-9,11Z", "#8E2236", 2.4)
    return s + '</g>'


def cachecol():
    faixa = "M-104,-200 C-40,-172 40,-172 104,-200 L108,-166 C40,-140 -40,-140 -108,-166Z"
    ponta = "M36,-160 L72,-162 L80,-66 L44,-70Z"
    s = ""
    for d in (ponta, faixa):
        s += contorno(d, "#E8752F", 2.6) + '<path d="%s" fill="url(#listrasCachecol)"/>' % d + contorno(d, "none", 2.6)
    s += '<path d="M46,-70 L44,-52 M54,-69 L53,-50 M62,-68 L62,-50 M70,-67 L71,-50 M78,-66 L80,-50" stroke="%s" stroke-width="2.4" stroke-linecap="round"/>' % "#E8752F"
    return s


def capa():
    return contorno("M-120,-196 C-176,-120 -196,-40 -176,0 L176,0 C196,-40 176,-120 120,-196 C60,-176 -60,-176 -120,-196Z", VERM, 2.8)


def gola_arminho():
    s = contorno("M-104,-188 C-60,-160 60,-160 104,-188 L110,-160 C60,-130 -60,-130 -110,-160Z", "#FBF6EC", 2.6)
    for x in (-70, -30, 10, 50, 86):
        s += '<path d="M%g,-160 l-3,8 l3,-2 l3,2Z" fill="%s"/>' % (x, TINTA)
    return s


# ================================================================== objetos
def pilha_livros(cx, base, livros):
    """livros = [(largura, cor), ...] de baixo para cima; devolve (svg, topo)."""
    s, y = "", base
    for i, (w, cor) in enumerate(livros):
        dx = (-1) ** i * 10
        s += livro_fechado(cx + dx, y - 22, w, 44, cor, estrela=False)
        y -= 46
    return s, y


def brigadeiro(x, y, k=1.0):
    s = '<g transform="translate(%g %g) scale(%g)">' % (x, y, k)
    s += contorno("M-22,0 L22,0 L18,18 L-18,18Z", "#E59AA8", 2.2)
    s += '<path d="M-16,2 L-13,16 M-6,2 L-5,17 M4,2 L4,17 M14,2 L12,16" stroke="%s" stroke-width="1.4" opacity=".6"/>' % AMEIXA
    s += '<circle cx="0" cy="-8" r="19" fill="#4A2A1C" stroke="%s" stroke-width="2.2"/>' % AMEIXA
    for (a, b, c) in ((-8, -16, "#F2C94C"), (6, -18, "#E0566E"), (-12, -4, "#78B27A"), (10, -6, "#FFF6EC"), (0, -12, "#4F67C9"), (-2, 0, "#E8752F")):
        s += '<rect x="%g" y="%g" width="5" height="2.4" rx="1.2" fill="%s" transform="rotate(%d %g %g)"/>' % (a, b, c, (a * 7) % 90, a, b)
    return s + '</g>'


def prato_doces(x, y):
    s = '<g transform="translate(%g %g)">' % (x, y)
    s += contorno("M-80,0 C-80,-14 80,-14 80,0 C80,14 -80,14 -80,0Z", "#F4ECDC", 2.6)
    s += brigadeiro(-34, -12, .9) + brigadeiro(10, -14, .9) + brigadeiro(-10, -36, .9)
    s += contorno("M30,-30 L46,-38 L58,-30 L46,-22Z", "#C8324F", 2) + contorno("M30,-30 L22,-38 L22,-22Z M58,-30 L66,-38 L66,-22Z", "#F2C94C", 2)
    return s + '</g>'


def cupcake(x, y, k=1.0):
    s = '<g transform="translate(%g %g) scale(%g)">' % (x, y, k)
    s += contorno("M-34,-10 L34,-10 L26,40 L-26,40Z", "#F2A7B4", 2.6)
    s += '<path d="M-22,-8 L-17,38 M-8,-8 L-6,38 M8,-8 L6,38 M22,-8 L17,38" stroke="%s" stroke-width="1.8" opacity=".5"/>' % AMEIXA
    s += contorno("M-40,-8 C-48,-28 -26,-36 -20,-36 C-24,-56 0,-66 10,-52 C26,-62 44,-44 30,-34 C48,-30 46,-8 36,-8Z", "#FFF3E6", 2.6)
    s += '<circle cx="6" cy="-66" r="9" fill="%s" stroke="%s" stroke-width="2.2"/><path d="M8,-74 C10,-86 18,-90 24,-92" fill="none" stroke="%s" stroke-width="2"/>' % (VERM, AMEIXA, AMEIXA)
    for (a, b, c) in ((-20, -24, "#4F67C9"), (12, -30, "#78B27A"), (-4, -44, "#F2C94C"), (24, -18, "#E0566E")):
        s += '<rect x="%g" y="%g" width="6" height="2.6" rx="1.3" fill="%s"/>' % (a, b, c)
    return s + '</g>'


def bussola(x, y, k=1.0):
    s = '<g transform="translate(%g %g) scale(%g)">' % (x, y, k)
    s += '<circle r="46" fill="%s" stroke="%s" stroke-width="2.8"/><circle r="36" fill="#FBF3E2" stroke="%s" stroke-width="2"/>' % (OURO, AMEIXA, AMEIXA)
    s += contorno("M0,-52 C-6,-60 6,-60 0,-52Z", OURO, 2.2)
    for a in range(0, 360, 45):
        s += '<line x1="0" y1="-30" x2="0" y2="-%d" transform="rotate(%d)" stroke="%s" stroke-width="1.6"/>' % (25 if a % 90 else 22, a, AMEIXA)
    s += '<path d="M0,-26 L7,0 L0,4 L-7,0Z" fill="%s" transform="rotate(20)"/><path d="M0,26 L7,0 L0,-4 L-7,0Z" fill="#4F67C9" transform="rotate(20)"/>' % VERM
    s += '<circle r="4" fill="%s"/><text y="-14" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="11" fill="%s">N</text>' % (AMEIXA, AMEIXA)
    return s + '</g>'


def vela(x, base, alt):
    s = contorno("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (x - 11, base, x + 11, base, x + 11, base - alt, x - 11, base - alt), "#FBF3E2", 2.2)
    s += contorno("M%g,%g C%g,%g %g,%g %g,%g" % (x + 4, base - alt, x + 6, base - alt + 10, x + 8, base - alt + 14, x + 6, base - alt + 22), "#FBF3E2", 1.8)
    s += '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="2"/>' % (x, base - alt, x, base - alt - 6, AMEIXA)
    s += '<path d="M%g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g %g,%g Z" fill="url(#chama)" stroke="%s" stroke-width="1.6"/>' % (
        x, base - alt - 34, x + 12, base - alt - 18, x + 10, base - alt - 4, x, base - alt - 4, x - 10, base - alt - 4, x - 12, base - alt - 18, x, base - alt - 34, AMEIXA)
    return s


def castical(x, y, k=1.0):
    s = '<g transform="translate(%g %g) scale(%g)">' % (x, y, k)
    s += '<circle cx="0" cy="-230" r="130" fill="#FFD267" opacity=".42" filter="url(#brilho)"/>'
    s += contorno("M-52,0 C-52,-14 52,-14 52,0Z", OURO, 2.6)
    s += contorno("M-8,-12 L8,-12 L6,-150 L-6,-150Z", OURO, 2.4)
    s += contorno("M-70,-150 C-70,-110 70,-110 70,-150", "none", 7) + contorno("M-70,-150 C-70,-110 70,-110 70,-150", "none", .1)
    s += '<path d="M-70,-150 C-70,-110 70,-110 70,-150" fill="none" stroke="%s" stroke-width="4"/>' % OURO
    for cx_ in (-70, 0, 70):
        s += contorno("M%g,-150 L%g,-150 L%g,-162 L%g,-162Z" % (cx_ - 18, cx_ + 18, cx_ + 14, cx_ - 14), OURO, 2.2)
    s += vela(-70, -162, 64) + vela(0, -162, 96) + vela(70, -162, 50)
    return s + '</g>'


def bola_cristal(x, y, r=76):
    s = '<circle cx="%g" cy="%g" r="%g" fill="#B9A2E0" opacity=".45" filter="url(#brilho)"/>' % (x, y - r, r * 1.5)
    s += contorno("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (x - r * .8, y, x + r * .8, y, x + r * .55, y - r * .32, x - r * .55, y - r * .32), "#7B4A2E", 2.6)
    s += '<circle cx="%g" cy="%g" r="%g" fill="url(#cristal)" stroke="%s" stroke-width="2.8"/>' % (x, y - r * 1.12, r, AMEIXA)
    s += '<path d="M%g,%g C%g,%g %g,%g %g,%g" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" opacity=".8"/>' % (
        x - r * .55, y - r * 1.4, x - r * .5, y - r * 1.7, x - r * .2, y - r * 1.85, x + r * .05, y - r * 1.88)
    s += brilho(x + r * .2, y - r * 1.0, 1.0, "#FFF6EC") + brilho(x - r * .25, y - r * .8, .6, "#FFF6EC") + brilho(x + r * .4, y - r * 1.4, .5, "#FFF6EC")
    return s


def cartas_tarot(x, y, k=1.0, rot=0):
    s = '<g transform="translate(%g %g) rotate(%g) scale(%g)">' % (x, y, rot, k)
    for a, simb in ((-22, "lua"), (0, "sol"), (22, "estrela")):
        c = '<g transform="rotate(%d 0 60)">' % a
        c += contorno("M-26,-40 L26,-40 L26,40 L-26,40Z", "#FBF3E2", 2.4)
        c += '<rect x="-20" y="-34" width="40" height="68" fill="none" stroke="%s" stroke-width="1.2" opacity=".6"/>' % AMEIXA
        if simb == "sol":
            c += '<circle cx="0" cy="-2" r="10" fill="#F2C94C" stroke="%s" stroke-width="1.6"/>' % AMEIXA
            c += "".join('<line x1="0" y1="-14" x2="0" y2="-20" transform="rotate(%d 0 -2)" stroke="%s" stroke-width="1.6"/>' % (t, AMEIXA) for t in range(0, 360, 45))
        elif simb == "lua":
            c += '<path d="M2,-16 a14,14 0 1 0 0,28 a10,10 0 1 1 0,-28Z" fill="#4F67C9"/>'
        else:
            c += brilho(0, -2, 1.5, VERM)
        s += c + '</g>'
    return s + '</g>'


def novelo(x, y, r=46):
    s = '<path d="M%g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g %g,%g" fill="none" stroke="%s" stroke-width="3.2" stroke-linecap="round"/>' % (
        x + r * .6, y + r * .7, x + r * 2, y + r * 2.2, x - r * 1.6, y + r * 2.6, x - r * .4, y + r * 3.6, x + r * .4, y + r * 4.4, x + r * 2.6, y + r * 3.8, x + r * 3.2, y + r * 4.6, VERM)
    s += '<circle cx="%g" cy="%g" r="%g" fill="%s" stroke="%s" stroke-width="2.8"/>' % (x, y, r, VERM, AMEIXA)
    for a in (-40, 0, 40):
        s += '<path d="M%g,%g C%g,%g %g,%g %g,%g" fill="none" stroke="#8E2236" stroke-width="2.4" transform="rotate(%d %g %g)"/>' % (
            x - r * .85, y - r * .3, x - r * .3, y + r * .5, x + r * .3, y + r * .5, x + r * .85, y - r * .3, a, x, y)
    return s


def papel_pena_tinteiro(pp, pena_x, pena_y, tint_x):
    """pp = (cx, cy, rot) da folha."""
    cx, cy, rot = pp
    s = g("translate(%g %g) rotate(%g)" % (cx, cy, rot),
          contorno("M-80,-56 L80,-56 L80,56 L-80,56Z", "#FBF3E2", 2.6) +
          "".join('<path d="M-60,%d C-30,%d 10,%d %d,%d" fill="none" stroke="%s" stroke-width="2" opacity=".55"/>' % (y, y - 4, y + 4, 40 if y < 30 else 0, y, AMEIXA) for y in (-34, -16, 2, 20, 38)))
    s += contorno("M%g,0 L%g,26 L%g,26 L%g,0Z" % (tint_x - 22, tint_x - 28, tint_x + 28, tint_x + 22), "#2F4A8C", 2.6)
    s += contorno("M%g,-14 L%g,-14 L%g,0 L%g,0Z" % (tint_x - 12, tint_x + 12, tint_x + 14, tint_x - 14), "#1E1418", 2)
    return s


def pena(x, y, rot=-30, k=1.0):
    s = '<g transform="translate(%g %g) rotate(%g) scale(%g)">' % (x, y, rot, k)
    s += contorno("M0,0 C-14,-40 -12,-90 6,-130 C20,-96 22,-50 0,0Z", "#FBF6EC", 2.4)
    s += '<path d="M2,-4 C2,-50 4,-90 6,-128" fill="none" stroke="%s" stroke-width="1.8"/>' % AMEIXA
    s += '<path d="M0,0 L-3,14" stroke="#1E1418" stroke-width="3" stroke-linecap="round"/>'
    s += "".join('<path d="M4,%d L14,%d M2,%d L-8,%d" stroke="%s" stroke-width="1.2" opacity=".5"/>' % (y_, y_ - 10, y_, y_ - 10, AMEIXA) for y_ in range(-110, -20, 16))
    return s + '</g>'


def lupa(x, y, r=36, ang=40, olho=None):
    """Lente centrada em (x,y); o cabo sai na direcao 'ang' (graus, 0 = direita)."""
    t = math.radians(ang)
    ex, ey = x + math.cos(t) * r, y + math.sin(t) * r
    fx, fy = x + math.cos(t) * (r + 70), y + math.sin(t) * (r + 70)
    s = '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="14" stroke-linecap="round"/><path d="M%g,%g L%g,%g" stroke="#7B4A2E" stroke-width="9" stroke-linecap="round"/>' % (ex, ey, fx, fy, AMEIXA, ex, ey, fx, fy)
    s += '<circle cx="%g" cy="%g" r="%g" fill="#DDF0FF" fill-opacity=".35"/>' % (x, y, r)
    if olho:
        s += '<clipPath id="lente"><circle cx="%g" cy="%g" r="%g"/></clipPath><g clip-path="url(#lente)">%s</g>' % (x, y, r - 2, olho)
    s += '<circle cx="%g" cy="%g" r="%g" fill="none" stroke="%s" stroke-width="6"/><circle cx="%g" cy="%g" r="%g" fill="none" stroke="%s" stroke-width="2"/>' % (x, y, r, OURO, x, y, r + 3, AMEIXA)
    s += '<path d="M%g,%g C%g,%g %g,%g %g,%g" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity=".8"/>' % (x - r * .6, y - r * .2, x - r * .6, y - r * .5, x - r * .4, y - r * .65, x - r * .1, y - r * .7)
    return s


def guarda_chuva(cx, cy, rx=200, ry=120, cabo=(100, -300)):
    gomos = 6
    pts_baixo = []
    s = '<path d="M%g,%g L%g,%g C%g,%g %g,%g %g,%g" fill="none" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % (
        cx, cy - ry * .9, cabo[0], cabo[1], cabo[0] + 4, cabo[1] + 24, cabo[0] + 28, cabo[1] + 24, cabo[0] + 30, cabo[1] + 6, AMEIXA)
    copa = "M%g,%g C%g,%g %g,%g %g,%g" % (cx - rx, cy, cx - rx, cy - ry * 1.3, cx + rx, cy - ry * 1.3, cx + rx, cy)
    for i in range(gomos, 0, -1):
        x0 = cx - rx + 2 * rx * i / gomos
        x1 = cx - rx + 2 * rx * (i - 1) / gomos
        copa += " Q%g,%g %g,%g" % ((x0 + x1) / 2, cy - 26, x1, cy)
    s += contorno(copa + "Z", VERM, 2.8)
    for i in range(1, gomos):
        x0 = cx - rx + 2 * rx * i / gomos
        s += '<path d="M%g,%g Q%g,%g %g,%g" fill="none" stroke="%s" stroke-width="2" opacity=".6"/>' % (cx, cy - ry * .98, (cx + x0) / 2, cy - ry * .7, x0, cy, AMEIXA)
    s += '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % (cx, cy - ry * .98, cx, cy - ry * 1.12, AMEIXA)
    return s


def chuva(lista):
    return "".join('<path transform="translate(%g %g)" d="M0,-10 C4,-4 6,0 6,4 C6,9 3,11 0,11 C-3,11 -6,9 -6,4 C-6,0 -4,-4 0,-10Z" fill="#8EC5E8" stroke="%s" stroke-width="1.4"/>' % (x, y, AMEIXA) for x, y in lista)


def abobora_lanterna(cx, cy, rx=190, ry=150, topo=-262):
    corpo = elipse(cx, cy, rx, ry).difference(box(cx - 400, cy - 400, cx + 400, topo))
    from felpudo import caminho
    d = caminho(corpo)
    s = contorno(d, "#E8752F", 3)
    s += '<clipPath id="abob"><path d="%s"/></clipPath><g clip-path="url(#abob)">' % d
    for dx in (-120, -60, 0, 60, 120):
        s += '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="none" stroke="#B8541E" stroke-width="3"/>' % (cx + dx * .55, cy, abs(dx) * .5 + 40, ry * 1.02)
    s += '</g>'
    s += '<path d="M%g,%g L%g,%g L%g,%g Z M%g,%g L%g,%g L%g,%g Z" fill="url(#aboboraLuz)" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % (
        cx - 92, cy - 20, cx - 40, cy - 20, cx - 66, cy - 66, cx + 40, cy - 20, cx + 92, cy - 20, cx + 66, cy - 66, AMEIXA)
    s += '<path d="M%g,%g L%g,%g L%g,%g L%g,%g L%g,%g L%g,%g L%g,%g C%g,%g %g,%g %g,%g Z" fill="url(#aboboraLuz)" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % (
        cx - 110, cy + 20, cx - 80, cy + 40, cx - 50, cy + 22, cx - 18, cy + 44, cx + 18, cy + 22, cx + 50, cy + 44, cx + 110, cy + 20,
        cx + 80, cy + 96, cx - 80, cy + 96, cx - 110, cy + 20, AMEIXA)
    return s


def caixa_papelao(cx, base, w=330, h=230):
    x0, x1, top = cx - w / 2, cx + w / 2, base - h
    frente = contorno("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (x0, top, x1, top, x1, base, x0, base), "#C99A64", 3)
    frente += '<path d="M%g,%g L%g,%g" stroke="#E8D3A8" stroke-width="16" opacity=".8"/>' % (cx, top, cx, top + 70)
    frente += '<text x="%g" y="%g" text-anchor="middle" font-family="Caveat" font-weight="700" font-size="48" fill="%s" transform="rotate(-4 %g %g)">livros</text>' % (cx + 40, base - 56, AMEIXA, cx + 40, base - 56)
    abas = contorno("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (x0, top, x0 - 70, top - 40, x0 - 40, top - 70, x0 + 30, top - 20), "#B4844E", 2.6)
    abas += contorno("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (x1, top, x1 + 70, top - 40, x1 + 40, top - 70, x1 - 30, top - 20), "#B4844E", 2.6)
    fundo = contorno("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (x0, top, x0 + 30, top - 24, x1 - 30, top - 24, x1, top), "#7A5432", 2.4)
    return fundo, abas, frente


def balao_pensamento(x, y, conteudo=""):
    s = ""
    for (a, b, r) in ((-110, 150, 10), (-80, 112, 15)):
        s += '<circle cx="%g" cy="%g" r="%g" fill="#FBF3E2" stroke="%s" stroke-width="2.6"/>' % (x + a, y + b, r, AMEIXA)
    nuvem = ("M%g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g %g,%g Z" % (
        x - 90, y + 40, x - 130, y + 30, x - 120, y - 30, x - 80, y - 40, x - 70, y - 90, x - 10, y - 96, x + 10, y - 70,
        x + 40, y - 100, x + 110, y - 80, x + 100, y - 30, x + 140, y - 10, x + 130, y + 56, x + 80, y + 56,
        x + 50, y + 90, x - 40, y + 86, x - 90, y + 40))
    return s + contorno(nuvem, "#FBF3E2", 2.8) + conteudo


def lampada(x, y):
    s = "".join('<line x1="0" y1="-62" x2="0" y2="-84" transform="translate(%g %g) rotate(%d)" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % (x, y, a, AMEIXA) for a in range(-70, 71, 35))
    s += '<circle cx="%g" cy="%g" r="70" fill="#FFE07A" opacity=".5" filter="url(#brilho)"/>' % (x, y)
    s += contorno("M%g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g %g,%g L%g,%g L%g,%g Z" % (
        x - 16, y + 34, x - 50, y + 6, x - 40, y - 52, x, y - 52, x + 40, y - 52, x + 50, y + 6, x + 16, y + 34, x + 16, y + 34, x - 16, y + 34), "#FFE07A", 2.8)
    s += contorno("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (x - 16, y + 34, x + 16, y + 34, x + 14, y + 52, x - 14, y + 52), "#A29EAE", 2.4)
    s += '<path d="M%g,%g C%g,%g %g,%g %g,%g" fill="none" stroke="#E8752F" stroke-width="2.4"/>' % (x - 10, y + 30, x - 12, y - 6, x + 12, y - 6, x + 10, y + 30)
    return s


def nota(x, y, k=1.0, dupla=False, rot=0):
    s = '<g transform="translate(%g %g) rotate(%g) scale(%g)" fill="%s" stroke="%s">' % (x, y, rot, k, AMEIXA, AMEIXA)
    s += '<ellipse cx="0" cy="0" rx="11" ry="8" transform="rotate(-20)"/><path d="M9,-2 L9,-46" stroke-width="3.4"/>'
    if dupla:
        s += '<ellipse cx="34" cy="-8" rx="11" ry="8" transform="rotate(-20 34 -8)"/><path d="M43,-10 L43,-54" stroke-width="3.4"/><path d="M9,-46 L43,-54 L43,-44 L9,-36Z" stroke="none"/>'
    else:
        s += '<path d="M9,-46 C20,-40 24,-30 20,-20" fill="none" stroke-width="3.4"/>'
    return s + '</g>'


def mariposa(x, y, k=1.0, rot=-12):
    s = '<g transform="translate(%g %g) rotate(%g) scale(%g)">' % (x, y, rot, k)
    for lado in (-1, 1):
        s += contorno("M0,-4 C%g,-44 %g,-40 %g,-8 C%g,4 %g,6 0,0Z" % (lado * 30, lado * 70, lado * 64, lado * 50, lado * 20), "#E8C987", 2.4)
        s += contorno("M0,2 C%g,10 %g,30 %g,36 C%g,40 %g,20 0,6Z" % (lado * 20, lado * 46, lado * 30, lado * 14, lado * 6), "#D9A96A", 2.2)
        s += '<circle cx="%g" cy="-18" r="7" fill="#7B4A2E"/>' % (lado * 40)
    s += contorno("M-5,-14 C-5,-22 5,-22 5,-14 L4,24 C4,30 -4,30 -4,24Z", "#7B4A2E", 2)
    s += '<path d="M-2,-20 C-8,-34 -18,-38 -22,-40 M2,-20 C8,-34 18,-38 22,-40" fill="none" stroke="%s" stroke-width="1.8"/>' % AMEIXA
    return s + '</g>'


def lua_crescente(x, y, r=56):
    ox, oy, ro = x + r * .5, y - r * .22, r * .86
    return ('<mask id="mlua%d"><rect x="%g" y="%g" width="%g" height="%g" fill="#fff"/><circle cx="%g" cy="%g" r="%g" fill="#000"/></mask>'
            '<clipPath id="clua%d"><circle cx="%g" cy="%g" r="%g"/></clipPath>'
            '<g mask="url(#mlua%d)"><circle cx="%g" cy="%g" r="%g" fill="#F7DC8C" stroke="%s" stroke-width="2.8"/></g>'
            '<g clip-path="url(#clua%d)"><circle cx="%g" cy="%g" r="%g" fill="none" stroke="%s" stroke-width="2.8"/></g>') % (
        int(abs(x)), x - r - 4, y - r - 4, 2 * r + 8, 2 * r + 8, ox, oy, ro, int(abs(x)), x, y, r, int(abs(x)), x, y, r, AMEIXA, int(abs(x)), ox, oy, ro, AMEIXA)


def constelacao(pts):
    s = '<path d="M%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="3 5" opacity=".75"/>' % (" L".join("%g,%g" % p for p in pts), AMEIXA)
    return s + "".join(brilho(x, y, .55 + (i % 3) * .2, AMEIXA) for i, (x, y) in enumerate(pts))


def braco(p, lado, pts, pata, rot_pata=0, r=22, sentado_ombro=(84, -150)):
    membro(p, [(lado * sentado_ombro[0], sentado_ombro[1])] + pts, r, r - 3)
    p.pata(pata[0], pata[1], 22, 19, rot_pata, dedos=False)


# ================================================================== POSES 27-56
A, OB, AM, PB = "Acessórios", "Objetos", "Com amigos", "Pensando e brincando"


@pose("27", "De óculos", A, "Óculos redondos dourados de leitor, ao lado de uma pilha de livros. O jeito «professor» do clube: indicação, curiosidade, «você sabia?».")
def p27(p):
    s, topo = pilha_livros(-210, 0, [(150, "#4F67C9"), (130, VERM), (140, "#78B27A")])
    p.svg(s, caixa=(-300, topo - 10, -120, 0))
    sentado(p, cabeca=dict(acess=[oculos_redondos()]))


@pose("28", "Chapéu de bruxa", A, "Chapéu de bruxa roxo com faixa laranja e uma abóbora ao lado. Halloween, edições temáticas, leitura de terror.")
def p28(p):
    sentado(p, cabeca=dict(expr="feliz", acess=[chapeu_bruxa()], topo_acess=-300))
    p.svg(abobora_mini(-200, -34, 1.6), caixa=(-250, -90, -150, 0))


def abobora_mini(x, y, k):
    s = '<g transform="translate(%g %g) scale(%g)">' % (x, y, k)
    for dx, rx in ((-12, 16), (12, 16), (0, 17)):
        s += '<ellipse cx="%g" cy="0" rx="%g" ry="15" fill="#E8752F" stroke="%s" stroke-width="1.6"/>' % (dx, rx, AMEIXA)
    s += '<path d="M0,-14 C0,-22 4,-26 8,-28" fill="none" stroke="#4E6B3A" stroke-width="3" stroke-linecap="round"/>'
    s += '<path d="M-10,-4 L-5,-4 L-7.5,-9Z M5,-4 L10,-4 L7.5,-9Z M-9,4 C-4,9 4,9 9,4" fill="#FFE07A" stroke="%s" stroke-width="1"/>' % AMEIXA
    return s + '</g>'


@pose("29", "De lenço e óculos escuros", A, "Lenço de bolinhas amarrado no queixo e óculos escuros de gatinho: a diva. Para fofoca literária, «spoiler? não sei de nada», looks de evento.")
def p29(p):
    sentado(p, cabeca=dict(acess=[lenco(), oculos_escuros()]))
    p.svg(brilho(-150, -420, 1.3, AMEIXA) + brilho(170, -430, 1.0, AMEIXA), caixa=(-170, -450, 190, -400))


@pose("30", "Coroado", A, "Coroinha dourada, capa vermelha e gola de arminho: o rei (ou rainha) do clube. Para «leitor do mês», vencedor do sorteio, aniversário do clube.")
def p30(p):
    p.svg(capa())
    sentado(p, cabeca=dict(expr="contente", acess=[coroa()]))
    p.svg(gola_arminho())


@pose("31", "Poeta de boina", A, "Boina vermelha e cachecol listrado: o poeta. Para poesia, citações, sarau, leitura em voz alta.")
def p31(p):
    sentado(p, cabeca=dict(expr="contente", acess=[boina()]))
    p.svg(cachecol())


@pose("32", "De gala", A, "Gravata-borboleta de bolinhas e cara de satisfeito. Para eventos especiais, convite formal, encerramento de ciclo.")
def p32(p):
    sentado(p, cabeca=dict(expr="contente"))
    p.svg(gravata(0, -166, 1.0))


@pose("33", "Ouvindo audiolivro", A, "Fone de ouvido e notas musicais em volta. Para audiolivro, podcast, playlist de leitura.")
def p33(p):
    sentado(p, cabeca=dict(expr="contente", acess=[fone()]))
    p.svg(nota(-180, -380, 1.2) + nota(150, -420, 1.1, True, 10) + nota(190, -300, .9), caixa=(-200, -480, 240, -280))


@pose("34", "Com florzinha", A, "Florzinha rosa atrás da orelha e bochechas coradas. Para primavera, carinho, «mês das mulheres», delicadeza.")
def p34(p):
    sentado(p, cabeca=dict(expr="contente", acess=[flor()]))


@pose("35", "No alto da pilha", OB, "Sentado no topo de uma pilha de livros coloridos. Para «metas de leitura», listas, «quantos livros você leu?».")
def p35(p):
    s, topo = pilha_livros(0, 0, [(300, "#4F67C9"), (270, VERM), (290, "#78B27A"), (250, "#7A3E8E")])
    p.svg(s, caixa=(-160, topo, 160, 0))
    p.inicio(0, topo + 6)
    sentado(p, cabeca=dict(expr="feliz"))
    p.fim()


@pose("36", "Comendo docinhos", OB, "Brigadeiro na boca, pratinho de doces do lado. Para o lanche do encontro, «tem docinho!», Dia das Crianças.")
def p36(p):
    sentado_barriga(p, cabeca=dict(expr="feliz"), bracos=None)
    membro(p, [(-80, -182), (-64, -150), (-48, -124)], 23, 20)
    p.pata(-46, -118, 25, 17, 20)
    p.svg(brigadeiro(16, -214, 1.05))
    braco(p, 1, [(70, -196), (40, -206)], (34, -204), 70, sentado_ombro=(84, -182))
    p.svg(prato_doces(-196, -14), caixa=(-280, -70, -110, 0))
    p.svg('<circle cx="-30" cy="-196" r="3" fill="#4A2A1C"/><circle cx="-22" cy="-186" r="2.4" fill="#4A2A1C"/><circle cx="60" cy="-232" r="2.2" fill="#E0566E"/>')


@pose("37", "Com cupcake", OB, "Cupcake de cereja nas duas patinhas. Para aniversário, comemoração, café com bolo do encontro.")
def p37(p):
    sentado_barriga(p, cabeca=dict(expr="contente"), bracos=None)
    p.svg(cupcake(0, -136, 1.2), caixa=(-60, -250, 60, -80))
    for lado in (-1, 1):
        braco(p, lado, [(lado * 70, -150), (lado * 48, -136)], (lado * 44, -134), lado * 90, sentado_ombro=(84, -182))


@pose("38", "Com a bússola", OB, "Bússola dourada nas patas, olhando para ela. Para aventura, «qual o próximo destino de leitura?», roteiros.")
def p38(p):
    sentado(p, cabeca=dict(expr="curioso", olhar=(0, 7)), patas=True)
    p.svg(bussola(0, -128, 1.0))
    for lado in (-1, 1):
        braco(p, lado, [(lado * 70, -136), (lado * 44, -128)], (lado * 42, -126), lado * 90)


@pose("39", "Mago do castiçal", OB, "Chapéu de mago azul de estrelas e um castiçal de três velas acesas. Para mistério, fantasia, encontros à noite.")
def p39(p):
    p.svg(castical(-220, 0, 1.0), caixa=(-300, -330, -140, 0))
    sentado(p, cabeca=dict(expr="neutro", olhar=(-6, -1), acess=[chapeu_mago()], topo_acess=-310))


@pose("40", "Bola de cristal", OB, "As patinhas sobre uma bola de cristal que brilha. Para «previsões do mês», «adivinha o livro», sorteios.")
def p40(p):
    sentado(p, cabeca=dict(expr="curioso", olhar=(0, 8)), patas=False)
    p.svg(bola_cristal(0, -4, 78), caixa=(-120, -200, 120, 0))
    p.pata(-46, -168, 26, 16, -10)
    p.pata(46, -168, 26, 16, 10)


@pose("41", "Tirando cartas", OB, "Leque de três cartas de tarô (lua, sol, estrela) na pata e uma piscadinha. Para enquetes, «escolha uma carta», dinâmicas.")
def p41(p):
    sentado(p, cabeca=dict(expr="piscando"))
    p.svg(cartas_tarot(140, -300, 1.15, 10), caixa=(70, -400, 220, -220))
    braco(p, 1, [(118, -190), (130, -236)], (132, -244), 20)


@pose("42", "Brincando com novelo", OB, "De barriga pra cima segurando um novelo vermelho, o fio solto pela barriga. Para fim de semana, preguiça boa, «modo brincadeira».")
def p42(p):
    rabo(p, [(30, -4), (90, 22), (160, 14), (196, -22)], 18, 13)
    for lado in (-1, 1):
        membro(p, [(lado * 100, -60), (lado * 140, -92), (lado * 160, -118)], 32, 28)
    from shapely.ops import unary_union as U
    p.peca(elipse(0, -150, 150, 160), lambda x, y: (x / 200, (y + 150) / 200), brancos=U([elipse(0, -150, 96, 122), elipse(0, -280, 60, 30)]))
    p.cabeca(0, -330, rot=-6, expr="feliz")
    p.svg(novelo(0, -214, 46), caixa=(-120, -270, 220, 10))
    for lado in (-1, 1):
        membro(p, [(lado * 108, -256), (lado * 96, -238), (lado * 58, -226)], 24, 21)
        p.pata(lado * 52, -226, 24, 20, lado * 80, dedos=False)
        p.sola(lado * 166, -130, .95, lado * 35)


@pose("43", "Escrevendo", OB, "Escrevendo com pena numa folha, tinteiro do lado. Para «escreva com a gente», resenhas, oficinas de escrita.")
def p43(p):
    sentado_barriga(p, cabeca=dict(expr="leitura"), bracos=None, solas=True)
    p.svg(papel_pena_tinteiro((0, -112, -4), 0, 0, 190), caixa=(-90, -180, 220, 30))
    braco(p, -1, [(-80, -150), (-62, -112)], (-60, -108), -60, sentado_ombro=(84, -182))
    membro(p, [(84, -182), (76, -150), (50, -124)], 22, 19)
    p.svg(pena(52, -126, 28, 1.0))
    p.pata(48, -120, 22, 19, 60, dedos=False)


@pose("44", "Detetive de lupa", OB, "Lupa no olho direito, que aparece gigante através da lente. Para «lendo nas entrelinhas», pistas, livro de mistério.")
def p44(p):
    sentado(p, cabeca=dict(expr="neutro"))
    olho = olho_brilho(41, -262, rx=28, ry=32, olhar=(-3, 0))
    p.svg(lupa(41, -262, 40, 52, olho), caixa=(0, -310, 150, -160))
    braco(p, 1, [(110, -180), (104, -196)], (100, -200), 50)


@pose("45", "Na chuva", OB, "Em pé debaixo de um guarda-chuva vermelho, gotas em volta. Para dia de chuva em Recife, «encontro mantido», aconchego.")
def p45(p):
    p.svg(guarda_chuva(40, -500, 200, 120, (104, -300)) + chuva([(-230, -360), (-200, -250), (290, -330), (270, -220), (-180, -140), (250, -110), (-240, -40)]),
          caixa=(-250, -650, 300, -20))
    em_pe(p, bracos=None, cabeca=dict(expr="contente"))
    braco(p, 1, [(96, -250), (104, -290)], (104, -298), 0, sentado_ombro=(66, -206))
    membro(p, [(-66, -206), (-84, -160), (-88, -126)], 22, 19)
    p.pata(-88, -118, 22, 18, -10, dedos=False)


@pose("46", "Dentro da abóbora", OB, "Saindo de dentro de uma abóbora de Halloween entalhada e acesa. Para a edição de Halloween, convite de festa, «doces ou travessuras».")
def p46(p):
    p.svg('<ellipse cx="0" cy="-262" rx="150" ry="26" fill="#5A2A14" stroke="%s" stroke-width="2.6"/>' % AMEIXA)
    p.cabeca(0, -300, expr="feliz", sobre_corpo=False)
    p.svg(abobora_lanterna(0, -120, 200, 150, -262), caixa=(-210, -290, 210, 30))
    p.pata(-80, -258, 26, 16)
    p.pata(80, -258, 26, 16)
    p.svg(brilho(-200, -380, 1.2) + brilho(210, -350, .9))


@pose("47", "Com o filhote", AM, "Ele e um filhotinho laranja que olha pra cima, com um coração entre os dois. Para família, «traga um amigo», cuidado.")
def p47(p):
    p.inicio(-190, 0, .52, pe=LARANJA, iris="#E9A83C")
    sentado(p, cabeca=dict(expr="curioso", olhar=(4, -6), rot=-8))
    p.fim()
    p.inicio(60, 0)
    sentado(p, cabeca=dict(expr="contente", rot=-6))
    p.fim()
    p.svg(coracao(-110, -330, 1.4), caixa=(-140, -360, -80, -300))


@pose("48", "A turma", AM, "Três gatos lado a lado: ele no meio, um cinza contente e um laranja feliz. Para «somos um clube», boas-vindas, fotos de grupo.")
def p48(p):
    p.inicio(-215, 10, .8, pe=CINZA, iris="#8FC3E6")
    sentado(p, rabo_cima=False, cabeca=dict(expr="contente", rot=-6))
    p.fim()
    p.inicio(215, 10, .8, pe=LARANJA, iris="#E9A83C")
    sentado(p, cabeca=dict(expr="feliz", rot=6))
    p.fim()
    sentado(p, rabo_cima=False, cabeca=dict(expr="neutro"))


@pose("49", "Juntinhos", AM, "Dois gatos de bochecha colada, o frajola e um cinza, com um coração em cima. Para amizade, parceria (TULIPA!), «obrigado por virem».")
def p49(p):
    p.inicio(118, 0, .92, pe=CINZA, iris="#8FC3E6")
    sentado(p, cabeca=dict(expr="contente", rot=-14))
    p.fim()
    p.inicio(-118, 0, .92)
    sentado(p, rabo_cima=False, cabeca=dict(expr="contente", rot=14))
    p.fim()
    p.svg(coracao(0, -420, 2.0), caixa=(-40, -460, 40, -390))


@pose("50", "Hora da história", AM, "Lendo em voz alta para dois filhotes que escutam. Para leitura coletiva, clube infantil, «roda de leitura».")
def p50(p):
    sentado_barriga(p, cabeca=dict(rot=-4, expr="leitura"), bracos=None)
    p.svg(livro_aberto_costas(0, -118, 210, 132))
    for lado in (-1, 1):
        membro(p, [(lado * 84, -184), (lado * 100, -150), (lado * 98, -122)], 22, 19)
        p.pata(lado * 98, -116, 22, 18, lado * 70, dedos=False)
    p.inicio(-230, 30, .46, pe=LARANJA, iris="#E9A83C")
    sentado(p, cabeca=dict(expr="curioso", olhar=(5, -6), rot=8))
    p.fim()
    p.inicio(230, 30, .46, pe=CINZA, iris="#8FC3E6")
    sentado(p, rabo_cima=False, cabeca=dict(expr="contente", rot=-8))
    p.fim()


@pose("51", "Pensando", PB, "Patinha no queixo, olhar pro alto e um balão de pensamento com um livro dentro. Para perguntas, reflexões, «o que você achou?».")
def p51(p):
    sentado(p, cabeca=dict(expr="neutro", olhar=(5, -6), rot=6))
    braco(p, 1, [(96, -170), (54, -186)], (48, -186), 80)
    p.svg(balao_pensamento(200, -480, livro_fechado(200, -486, 70, 90, VERM, rot=-8)), caixa=(70, -580, 350, -320))


@pose("52", "Teve uma ideia", PB, "Lâmpada acesa sobre a cabeça e a patinha erguida. Para dicas, «ideia de leitura», sugestões do público.")
def p52(p):
    sentado(p, cabeca=dict(expr="feliz"))
    braco(p, 1, [(130, -200), (144, -256)], (146, -266), 10)
    p.svg(lampada(0, -480), caixa=(-90, -570, 90, -420))


@pose("53", "Olhando as estrelas", PB, "Olhando pra cima, para a lua e uma constelação. Para «boa noite», poesia, sonhos, leitura de fantasia.")
def p53(p):
    p.svg(lua_crescente(-190, -470, 54) + constelacao([(90, -540), (150, -500), (210, -520), (240, -460), (190, -420)]), caixa=(-250, -560, 260, -400))
    sentado(p, cabeca=dict(expr="neutro", olhar=(2, -8), rot=-4))


@pose("54", "Dançando", PB, "Dançando numa perna só, bracinhos abertos, notas no ar. Para festa, sexta-feira, comemoração, «bora!».")
def p54(p):
    p.inicio(0, 0, 1, -7)
    rabo(p, [(-70, -60), (-140, -90), (-170, -150), (-150, -204)], 18, 13)
    membro(p, [(-46, -50), (-52, -10)], 30, 28)
    membro(p, [(46, -56), (96, -76), (120, -44)], 28, 25)
    from shapely.ops import unary_union as U
    p.peca(G.amostrar(G.BEAN_PE).buffer(3), lambda x, y: (x / 200, 1), brancos=U([elipse(0, -122, 58, 84), elipse(0, -222, 42, 30)]))
    p.pata(-54, -8, 34, 16)
    p.pata(126, -40, 30, 15, -40)
    membro(p, [(-66, -206), (-110, -256), (-134, -300)], 22, 19)
    membro(p, [(66, -206), (122, -212), (166, -236)], 22, 19)
    p.cabeca(0, -318, expr="feliz", rot=10)
    p.pata(-138, -308, 22, 20, -30, dedos=False)
    p.pata(174, -240, 22, 20, 60, dedos=False)
    p.fim()
    p.svg(nota(-220, -380, 1.3, True, -10) + nota(220, -420, 1.2, False, 12) + nota(250, -300, .9), caixa=(-240, -480, 300, -260))
    p.svg('<ellipse cx="20" cy="4" rx="140" ry="12" fill="%s" opacity=".18"/>' % AMEIXA)


@pose("55", "Caçando mariposa", PB, "Pulando com os bracinhos pra cima atrás de uma mariposa. Para curiosidade, «corre que acaba», energia.")
def p55(p):
    p.svg('<ellipse cx="0" cy="0" rx="110" ry="12" fill="%s" opacity=".2"/>' % AMEIXA)
    p.inicio(0, -70)
    em_pe(p, "cima", cabeca=dict(expr="curioso", olhar=(2, -8)))
    p.fim()
    p.svg(mariposa(30, -560, 1.2), caixa=(-60, -620, 120, -510))


@pose("56", "Na caixa", PB, "Dentro de uma caixa de papelão escrita «livros», as abas abertas. Para chegada de livros, doações, mudança, «caixa de surpresas».")
def p56(p):
    fundo, abas, frente = caixa_papelao(0, 0, 330, 230)
    p.svg(abas + fundo)
    p.cabeca(0, -262, expr="neutro", sobre_corpo=False)
    p.svg(frente, caixa=(-240, -310, 240, 0))
    p.pata(-74, -228, 26, 16)
    p.pata(74, -228, 26, 16)


if __name__ == "__main__":
    cods = sys.argv[1:] or [c for c, *_ in G.POSES if int(c) >= 27]
    G.construir(cods)
    todos = json.load(open(os.path.join(G.AQUI, "banco", "banco.json"), encoding="utf-8"))
    G.folha([m for m in todos if int(m["cod"]) >= 27], os.path.join(G.AQUI, "banco", "_folha2.png"))
