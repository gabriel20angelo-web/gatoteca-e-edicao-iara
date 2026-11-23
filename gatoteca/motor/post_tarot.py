# -*- coding: utf-8 -*-
"""TIRAGEM DE TARÔ (não é do clube, mas usa a identidade do Entrelinhas): a fórmula da v5 da Lilith.

Arco de tarô à esquerda com o frajola de rosto de Bastet como taróloga: lua clara atrás da cabeça, crescente
entre as orelhas, xale rosa de franja sobre o vestido ameixa, as patas sobre a carta do meio de uma tiragem de
três (XVII A Estrela, XIX O Sol, XVIII A Lua) numa mesa de toalha jade com festão e franja de ouro, e duas velas.
Coluna de texto limpa à direita: «Tiragem de Tarô» e os dois preços como duas cartinhas em arco.
uso: py post_tarot.py            -> saida/post_tarot.png (+ @2x)
     py post_tarot.py --final    -> também na pasta «Tiragem de tarô - artes» da área de trabalho
"""
import os, sys, math, base64
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "mascote"))
import montar
from papel import papel
import gato_banco as G
from gato_banco import Pose, PRETO
from felpudo import amostrar, caminho
from shapely.geometry import Polygon
from shapely import affinity
from post_lilith5 import cabeca, crescente, espelho
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[2]  # raiz do repositório

D = str(_REPO / 'gatoteca/artes/Tiragem de tarô')
NOITE, NOITE2, NOITE3 = "#262E4A", "#1A2036", "#3A4468"
OURO, OURO_C = "#C9A55E", "#E4C98A"
AMEIXA, AMEIXA2 = "#45293D", "#4A3044"
ROSA, ROSA2 = "#B8828F", "#9A6676"
JADE, JADE2, JADE3 = "#55786F", "#3F5F58", "#7E9F95"
CREME = "#F1E3CF"
CX = 250  # eixo da carta (viewBox 500 x 1300)


def b64(c):
    return "data:image/png;base64," + base64.b64encode(open(c, "rb").read()).decode()


def estrela4(x, y, k=1.0, cor=OURO, op=1):
    return '<path transform="translate(%g %g) scale(%g)" d="M0,-10 Q0,0 10,0 Q0,0 0,10 Q0,0 -10,0 Q0,0 0,-10Z" fill="%s" opacity="%g"/>' % (x, y, k, cor, op)


def estrela8(r, r2, cor, extra=""):
    pts = []
    for i in range(16):
        a = math.pi * i / 8 - math.pi / 2
        rr = r if i % 2 == 0 else r2
        pts.append("%.1f,%.1f" % (math.cos(a) * rr, math.sin(a) * rr))
    return '<path d="M%sZ" fill="%s" %s/>' % (" L".join(pts), cor, extra)


# ================================================================== as três cartas da mesa
def face_estrela(w, h):
    s = '<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (-w / 2, -h / 2, w, h, NOITE)
    s += '<g filter="url(#brilhoP)" opacity=".55">%s</g>' % estrela8(30, 9, OURO_C)
    s += estrela8(28, 8, OURO, 'stroke="%s" stroke-width=".8"' % "#F6E3B0")
    s += "".join(estrela4(x, y, k, "#F3E7DC") for x, y, k in ((-30, -34, .55), (30, -30, .5), (-34, 6, .4), (33, 10, .45), (-14, -44, .32), (16, 38, .3)))
    s += '<path d="M%g,%g C-20,%g -8,%g 0,%g C8,%g 20,%g %g,%g" fill="none" stroke="%s" stroke-width="1.6" opacity=".85"/>' % (
        -w / 2, h / 2 - 12, h / 2 - 17, h / 2 - 9, h / 2 - 14, h / 2 - 19, h / 2 - 11, w / 2, h / 2 - 15, JADE3)
    return s


def face_sol(w, h):
    s = '<rect x="%g" y="%g" width="%g" height="%g" fill="#F4DFA8"/>' % (-w / 2, -h / 2, w, h)
    s += '<circle r="%g" fill="#FFF4D2" opacity=".9" filter="url(#brilhoP)"/>' % (w * .42)
    raios = ""
    for i in range(16):
        a = math.radians(i * 22.5)
        r0, r1 = 27, (44 if i % 2 == 0 else 36)
        raios += "M%.1f,%.1f L%.1f,%.1f " % (math.cos(a) * r0, math.sin(a) * r0, math.cos(a) * r1, math.sin(a) * r1)
    s += '<path d="%s" stroke="%s" stroke-width="2.2" stroke-linecap="round"/>' % (raios, "#C08A3A")
    s += '<circle r="24" fill="%s" stroke="#A9772F" stroke-width="1.4"/>' % "#E8B54E"
    # rostinho sereno do sol
    s += '<path d="M-11,-3 q4,3 8,0 M3,-3 q4,3 8,0 M-5,8 q5,4 10,0" fill="none" stroke="#8A5A22" stroke-width="1.5" stroke-linecap="round"/>'
    s += '<circle cx="-11" cy="5" r="3" fill="#E58A98" opacity=".45"/><circle cx="11" cy="5" r="3" fill="#E58A98" opacity=".45"/>'
    s += '<path d="M%g,%g C-24,%g 24,%g %g,%g L%g,%g L%g,%gZ" fill="%s" opacity=".9"/>' % (
        -w / 2, h / 2 - 18, h / 2 - 26, h / 2 - 26, w / 2, h / 2 - 18, w / 2, h / 2, -w / 2, h / 2, JADE)
    return s


def face_lua(w, h):
    s = '<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (-w / 2, -h / 2, w, h, NOITE)
    d = "M-14,-6 A14,14 0 1 0 6,-16 A11,11 0 1 1 -14,-6Z"
    s += '<g transform="translate(2 -8) rotate(-14) scale(2.1)"><path d="%s" fill="#FFF3C6" opacity=".5" filter="url(#brilhoP)"/>' % d
    s += '<path d="%s" fill="%s" stroke="#F6E3B0" stroke-width=".5"/></g>' % (d, OURO)
    s += "".join('<path transform="translate(%g %g)" d="M0,-4 C2,-1 2.4,1.5 0,3 C-2.4,1.5 -2,-1 0,-4Z" fill="%s"/>' % (x, y, OURO_C) for x, y in ((-12, 26), (0, 32), (12, 26)))
    s += "".join(estrela4(x, y, k, "#F3E7DC") for x, y, k in ((-32, -34, .45), (32, -36, .4), (34, 4, .35)))
    for i, yy in enumerate((h / 2 - 16, h / 2 - 8)):
        s += '<path d="M%g,%g q7,-4 14,0 t14,0 t14,0 t14,0 t14,0 t14,0 t14,0 t14,0" fill="none" stroke="%s" stroke-width="1.4" opacity="%g"/>' % (-w / 2 - 4 + i * 6, yy, JADE3, .9 - i * .3)
    return s


def carta_tarot(cx, cy, w, h, rot, num, nome, face, seed):
    tex = b64(papel(int(w), int(h), "#F3E7DC", seed, forca=1.2, fibras=2.0, pintas=.6, borda=.2, relevo=.18))
    uid = "jc%d" % seed
    jx, jy, jw, jh = -w / 2 + 11, -h / 2 + 30, w - 22, h - 62
    s = '<g transform="translate(%g %g) rotate(%g)" filter="url(#sombraC)">' % (cx, cy, rot)
    s += '<clipPath id="%s"><rect x="%g" y="%g" width="%g" height="%g" rx="3"/></clipPath>' % (uid, jx, jy, jw, jh)
    s += '<rect x="%g" y="%g" width="%g" height="%g" rx="7" fill="%s"/>' % (-w / 2, -h / 2, w, h, CREME)
    s += '<image href="%s" x="%g" y="%g" width="%g" height="%g" preserveAspectRatio="none" clip-path="inset(0 round 7px)"/>' % (tex, -w / 2, -h / 2, w, h)
    s += '<g clip-path="url(#%s)"><g transform="translate(0 %g)">%s</g></g>' % (uid, jy + jh / 2, face(jw, jh))
    s += '<rect x="%g" y="%g" width="%g" height="%g" rx="3" fill="none" stroke="%s" stroke-width="1"/>' % (jx, jy, jw, jh, NOITE)
    s += '<rect x="%g" y="%g" width="%g" height="%g" rx="7" fill="none" stroke="%s" stroke-width="1.8"/>' % (-w / 2, -h / 2, w, h, OURO)
    s += '<rect x="%g" y="%g" width="%g" height="%g" rx="4" fill="none" stroke="%s" stroke-width=".7" opacity=".8"/>' % (-w / 2 + 5, -h / 2 + 5, w - 10, h - 10, NOITE)
    s += '<text x="0" y="%g" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="14" letter-spacing="1.5" fill="%s">%s</text>' % (-h / 2 + 22, NOITE, num)
    s += '<text x="0" y="%g" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="%g" letter-spacing="1.2" fill="%s">%s</text>' % (
        h / 2 - 13, 12.5 if len(nome) < 7 else 11.5, NOITE, nome)
    return s + '</g>'


# ================================================================== velas
def vela(x, yb, h=74):
    yt = yb - h
    s = '<circle cx="%g" cy="%g" r="70" fill="url(#chamaHalo)"/>' % (x, yt - 14)
    s += '<ellipse cx="%g" cy="%g" rx="20" ry="5.5" fill="%s"/><ellipse cx="%g" cy="%g" rx="13" ry="3" fill="#8E6E36"/>' % (x, yb + 1, OURO, x, yb - 1)
    corpo = "M%g,%g L%g,%g C%g,%g %g,%g %g,%g L%g,%gZ" % (x - 8.5, yb - 1, x - 8.5, yt + 3, x - 4, yt - 1, x + 4, yt + 1, x + 8.5, yt, x + 8.5, yb - 1)
    s += '<path d="%s" fill="%s"/>' % (corpo, CREME)
    s += '<path d="M%g,%g L%g,%g" stroke="#D2BE98" stroke-width="5" opacity=".7"/>' % (x + 5.5, yt + 4, x + 5.5, yb - 2)
    s += '<path d="M%g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g %g,%g" fill="%s"/>' % (x - 8.5, yt + 3, x - 10, yt + 10, x - 9, yt + 20, x - 7, yt + 22, x - 5, yt + 24, x - 6, yt + 8, x - 4, yt + 2, CREME)
    s += '<path d="%s" fill="none" stroke="#B9A47E" stroke-width=".9"/>' % corpo
    s += '<path d="M%g,%g L%g,%g" stroke="#1E1418" stroke-width="1.5" stroke-linecap="round"/>' % (x, yt, x, yt - 6)
    s += '<path d="M%g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g %g,%gZ" fill="url(#chamaG)"/>' % (
        x, yt - 32, x + 8, yt - 20, x + 7, yt - 8, x, yt - 4, x - 7, yt - 8, x - 8, yt - 20, x, yt - 32)
    s += '<ellipse cx="%g" cy="%g" rx="2.4" ry="5" fill="#FFFDF2"/>' % (x, yt - 11)
    return s


# ================================================================== a mesa (toalha jade de franja)
def mesa():
    tex = b64(papel(500, 1300, JADE, 81, forca=1.6, fibras=2.2))
    s = '<clipPath id="toalha"><path d="M0,800 L500,800 L500,1196 L0,1196Z"/></clipPath><g clip-path="url(#toalha)">'
    s += '<image href="%s" x="0" y="0" width="500" height="1300" preserveAspectRatio="none"/>' % tex
    s += '<rect y="800" width="500" height="240" fill="url(#tampo)"/>'
    s += '<rect y="1040" width="500" height="156" fill="%s" opacity=".38"/>' % JADE2
    s += '<rect y="800" width="500" height="396" fill="url(#ceuP)"/>'
    # dobras da frente
    for x in (70, 160, 250, 340, 430):
        s += '<path d="M%g,1044 C%g,1100 %g,1150 %g,1196" stroke="%s" stroke-width="16" opacity=".22" fill="none" filter="url(#borrao)"/>' % (x, x - 3, x + 3, x, "#1F3530")
    s += '</g>'
    s += '<rect y="800" width="500" height="14" fill="url(#sombraTopo)"/>'
    s += ('<g fill="none" stroke="%s" stroke-linecap="round" filter="url(#mao)"><path d="M0,1040 L500,1040" stroke-width="1.6"/>'
          '<path d="M0,1047 L500,1047" stroke-width=".7"/><path d="M0,1162 L500,1162 M0,1192 L500,1192" stroke-width="1.1"/></g>') % OURO
    # festão logo abaixo da borda do tampo e o medalhão de sol e lua no meio da frente
    fest = "".join("M%g,1048 Q%g,1070 %g,1048 " % (x, x + 15.6, x + 31.25) for x in [i * 31.25 for i in range(16)])
    s += '<path d="%s" fill="none" stroke="%s" stroke-width="1.3" filter="url(#mao)"/>' % (fest, OURO)
    s += "".join('<circle cx="%g" cy="1066" r="2" fill="%s"/>' % (i * 31.25 + 15.6, OURO_C) for i in range(16))
    raios = "".join("M%.1f,%.1f L%.1f,%.1f " % (250 + math.cos(math.radians(a)) * 26, 1110 + math.sin(math.radians(a)) * 26,
                                               250 + math.cos(math.radians(a)) * (36 if a % 30 == 0 else 31), 1110 + math.sin(math.radians(a)) * (36 if a % 30 == 0 else 31)) for a in range(0, 360, 15))
    s += '<g filter="url(#mao)"><path d="%s" stroke="%s" stroke-width="1.2"/>' % (raios, OURO)
    s += '<circle cx="250" cy="1110" r="22" fill="%s" stroke="%s" stroke-width="1.4"/></g>' % (JADE2, OURO)
    s += crescente(252, 1112, .78)
    for lado in (-1, 1):
        s += estrela4(250 + lado * 62, 1110, .55, OURO) + estrela4(250 + lado * 92, 1110, .32, OURO_C)
    # barra bordada: luazinhas e pontos
    for i in range(15):
        xb = 12 + i * 34
        s += ('<circle cx="%g" cy="1177" r="2.4" fill="%s"/>' % (xb, OURO) if i % 2 else
              '<path transform="translate(%g 1178) rotate(-14) scale(.42)" d="M-14,-6 A14,14 0 1 0 6,-16 A11,11 0 1 1 -14,-6Z" fill="%s"/>' % (xb, OURO))
    # franja
    fr = "".join("M%.1f,1194 L%.1f,1216 " % (x, x + .6) for x in [8 + i * 6.2 for i in range(80)])
    s += '<path d="%s" stroke="%s" stroke-width="1.6" stroke-linecap="round" filter="url(#mao)"/>' % (fr, OURO)
    s += "".join('<circle cx="%g" cy="1196" r="2.2" fill="%s"/>' % (8 + i * 24.8, OURO_C) for i in range(20))
    return s


# ================================================================== a taróloga
ROBE = ("M204,452 C178,458 146,470 128,500 C112,528 110,590 114,660 C118,720 124,770 128,830 L372,830 C376,770 382,720 386,660 "
        "C390,590 388,528 372,500 C354,470 322,458 296,452 L250,540 Z")
XALE_E = ("M208,449 C178,454 140,466 120,496 C100,524 94,580 96,636 C98,662 100,680 104,696 C142,636 184,560 230,470 Z")
# braço: ombro (sob o xale) -> cotovelo junto do corpo -> antebraço deitado na mesa até a pata; manga sino
BRACO_E = [(142, 560), (124, 650), (126, 736), (150, 788), (178, 806)]


def xale(lado):
    """Metade do xale: papel rosa, estrelinhas, borda de ouro na frente e franja caindo do vies."""
    d = XALE_E if lado < 0 else caminho(affinity.translate(espelho(amostrar(XALE_E)), 500, 0))
    uid = "xale%d" % (lado + 1)
    tex = b64(papel(260, 300, ROSA, 84 + lado, forca=1.5, fibras=2.2))
    s = '<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)">' % (uid, d, uid)
    s += '<image href="%s" x="%g" y="440" width="260" height="300" preserveAspectRatio="none"/>' % (tex, 84 if lado < 0 else 156)
    s += '<rect x="0" y="0" width="500" height="1300" fill="url(#estrelinhas)"/><rect x="0" y="0" width="500" height="1300" fill="url(#sombraXale)"/></g>'
    a, b = ((98, 700), (230, 470)) if lado < 0 else ((402, 700), (270, 470))
    # franja ao longo do vies da frente
    fr = ""
    for i in range(1, 24):
        t = i / 24
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        fr += "M%.1f,%.1f L%.1f,%.1f " % (x, y, x + lado * -1.5, y + 17 - 6 * t)
    s += '<path d="%s" stroke="%s" stroke-width="1.5" stroke-linecap="round" filter="url(#mao)"/>' % (fr, OURO)
    s += '<path d="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-linejoin="round" filter="url(#mao)"/>' % (d, OURO)
    ox = 7 * (1 if lado < 0 else -1)
    s += '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width=".8" opacity=".8" filter="url(#mao)"/>' % (a[0] - ox * .2, a[1] - 11, b[0] - ox, b[1] + 4, OURO)
    return s


def tarologa():
    """Tudo o que fica dentro da janela da carta, de trás para a frente."""
    p = Pose("93", "Taróloga", "", "", centro=(CX, 330))
    p.seed = 9300
    # vestido (o tronco; a mesa corta abaixo de 800)
    tex = b64(papel(500, 1300, AMEIXA, 83, forca=1.5, fibras=2.2))
    p.svg('<clipPath id="robeC"><path d="%s"/></clipPath><g clip-path="url(#robeC)">' % ROBE +
          '<image href="%s" x="0" y="0" width="500" height="1300" preserveAspectRatio="none"/>' % tex +
          '<rect width="500" height="1300" fill="url(#ceu)"/><rect width="500" height="1300" fill="url(#sombraVest)"/></g>'
          '<g fill="none" stroke="%s" stroke-linecap="round" filter="url(#mao)"><path d="M204,452 L250,540 L296,452 M192,458 L250,560 L308,458" stroke-width="1.2"/>'
          '<path d="M250,560 L250,800" stroke-width=".7" opacity=".5"/></g>' % OURO)
    # pescoço e peito branco no decote
    colo = Polygon([(198, 404), (302, 404), (314, 452), (342, 500), (158, 500), (186, 452)]).buffer(6)
    bib = Polygon([(218, 426), (282, 426), (250, 532)]).buffer(6)
    p.peca(colo, lambda a, b: ((a - CX) / 160, 1), brancos=bib)
    # medalhão de lua no peito
    p.svg('<path d="M236,470 Q250,500 264,470" fill="none" stroke="%s" stroke-width="1" opacity=".9"/>' % OURO +
          crescente(250, 512, .62))
    # mesa, mangas por cima do tampo, depois o xale cobrindo o alto das mangas
    p.svg(mesa())
    me = G.capsula(BRACO_E, 27, 31)
    md = affinity.translate(espelho(me), 500, 0)
    # punho: a faixa da manga logo antes da pata (corte perpendicular ao antebraço)
    (ax, ay), (bx, by) = BRACO_E[-2], BRACO_E[-1]
    ang = math.degrees(math.atan2(by - ay, bx - ax))
    faixa = affinity.translate(affinity.rotate(Polygon([(-10, -60), (40, -60), (40, 60), (-10, 60)]), ang, origin=(0, 0)), bx, by)
    pe_ = me.intersection(faixa)
    pd_ = affinity.translate(espelho(pe_), 500, 0)
    tex_m = b64(papel(280, 360, "#7A566F", 79, forca=1.5, fibras=2.2))
    for uid, m, pu in (("mE", me, pe_), ("mD", md, pd_)):
        x0, y0 = m.bounds[0] - 10, m.bounds[1] - 10
        p.svg('<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)"><image href="%s" x="%g" y="%g" width="280" height="360" preserveAspectRatio="none"/>'
              '<rect x="0" y="0" width="500" height="1300" fill="url(#ceu)"/></g>' % (uid, caminho(m), uid, tex_m, x0, y0) +
              '<path d="%s" fill="none" stroke="#8E6A86" stroke-width="3" opacity=".55" clip-path="url(#%s)"/>' % (caminho(m), uid) +
              '<path d="%s" fill="%s"/>' % (caminho(pu), ROSA2) +
              '<path d="%s" fill="none" stroke="%s" stroke-width="1.3" stroke-linejoin="round" filter="url(#mao)"/>' % (caminho(pu), OURO) +
              '<path d="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-linejoin="round" filter="url(#mao)"/>' % (caminho(m), OURO))
    # dobra do cotovelo
    p.svg('<path d="M112,724 C122,736 132,742 146,744 M388,724 C378,736 368,742 354,744" fill="none" stroke="%s" stroke-width="1" opacity=".7" filter="url(#mao)"/>' % OURO)
    p.svg(xale(-1) + xale(1))
    # cabeça de Bastet e a lua entre as orelhas
    cabeca(p, CX, 352, 1.1, 3, olhar=(1, 3))
    p.svg(crescente(CX + 4, 230, 1.55))
    # velas nas pontas da mesa
    p.svg(vela(52, 816, 78) + vela(448, 816, 64))
    # a tiragem: três cartas, a do meio maior e com um brilho atrás
    p.svg('<ellipse cx="250" cy="924" rx="110" ry="128" fill="url(#brilhoCarta)"/>')
    p.svg(carta_tarot(116, 938, 112, 186, -6, "XVII", "A ESTRELA", face_estrela, 501) +
          carta_tarot(384, 938, 112, 186, 6, "XVIII", "A LUA", face_lua, 503) +
          carta_tarot(250, 924, 128, 212, 0, "XIX", "O SOL", face_sol, 502))
    # patas sobre a carta do meio
    p.pata(214, 813, 22, 14, -8)
    p.pata(286, 813, 22, 14, 8)
    p.svg('<path d="M24,1250 C120,1240 200,1248 250,1246 C320,1244 400,1240 476,1250" fill="none" stroke="%s" stroke-width="1.4" opacity=".8" filter="url(#mao)"/>' % OURO)
    return "".join(p.camadas)


# ================================================================== a carta (janela em arco)
def carta():
    tex = b64(papel(500, 1300, "#232A45", 85, forca=1.8, fibras=2.4))
    raios = ""
    for a in range(0, 360, 6):
        t = math.radians(a)
        l = 232 if a % 18 == 0 else 206
        raios += "M%.1f,%.1f L%.1f,%.1f " % (math.cos(t) * 188, math.sin(t) * 188, math.cos(t) * l, math.sin(t) * l)
    estrelas = "".join('<use href="#br" transform="translate(%g %g) scale(%g)"/>' % e for e in
                       ((70, 170, .8), (436, 160, .65), (110, 92, .42), (400, 86, .42), (470, 320, .4), (30, 340, .45), (44, 560, .4), (462, 600, .45)))
    s = '<path d="M0,1300 V250 A250,250 0 0 1 500,250 V1300 Z" fill="%s"/>' % NOITE2
    s += '<g clip-path="url(#janela)">'
    s += '<image href="%s" x="0" y="0" width="500" height="1300" preserveAspectRatio="none"/>' % tex
    s += '<rect width="500" height="1300" fill="url(#noite)"/><rect width="500" height="1300" fill="url(#ceu)"/>'
    s += '<g transform="translate(250 336)"><circle r="260" fill="url(#halo)"/>'
    s += '<path d="%s" stroke="%s" stroke-width=".8" opacity=".6"/>' % (raios, OURO)
    s += '<circle r="158" fill="url(#luaG)"/><circle r="158" fill="url(#luaG)" filter="url(#aguada)" opacity=".5"/>'
    s += "".join('<circle cx="%g" cy="%g" r="%g" fill="#D9BE84" opacity=".28"/>' % c for c in ((-92, -70, 22), (84, -96, 12), (106, 40, 18), (-110, 54, 11), (-40, 112, 14)))
    s += '<g fill="none" stroke="%s"><circle r="158" stroke-width="1.4"/><circle r="168" stroke-width=".7" opacity=".8"/><circle r="178" stroke-width=".9" stroke-dasharray="1.5 6" opacity=".8"/></g></g>' % OURO
    s += '<g fill="%s">%s</g><g fill="%s"><use href="#br" transform="translate(250 48) scale(.7)"/></g>' % (OURO, estrelas, "#F3E7DC")
    s += tarologa()
    s += '</g>'
    s += ('<g fill="none" stroke="%s" filter="url(#mao)"><path d="M12,1300 V250 A238,238 0 0 1 488,250 V1300" stroke-width="1.6"/>'
          '<path d="M19,1300 V250 A231,231 0 0 1 481,250 V1300" stroke-width=".7"/></g>') % OURO
    return s


DEFS_CARTA = '''
<filter id="mao" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".045" numOctaves="2" seed="11" result="n"/>
 <feDisplacementMap in="SourceGraphic" in2="n" scale="1.6" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="aguada" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".03" numOctaves="3" seed="5" result="n"/>
 <feDisplacementMap in="SourceGraphic" in2="n" scale="5" xChannelSelector="R" yChannelSelector="G" result="d"/>
 <feTurbulence type="fractalNoise" baseFrequency=".02" numOctaves="2" seed="3" result="m"/>
 <feColorMatrix in="m" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1.3 1.3" result="ma"/><feComposite in="d" in2="ma" operator="in"/></filter>
<filter id="brilhoP" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="5"/></filter>
<filter id="borrao" x="-50%" y="-10%" width="200%" height="120%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="sombraC" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="5" stdDeviation="4.5" flood-color="#0E1222" flood-opacity=".55"/></filter>
<linearGradient id="noite" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2E3858" stop-opacity=".5"/><stop offset=".45" stop-color="#232A45" stop-opacity=".3"/><stop offset="1" stop-color="#0F1326" stop-opacity=".75"/></linearGradient>
<linearGradient id="sombraVest" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity=".35"/><stop offset=".35" stop-color="#000" stop-opacity="0"/><stop offset=".7" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".4"/></linearGradient>
<linearGradient id="sombraXale" x1="0" y1="0" x2="0" y2="1"><stop offset=".35" stop-color="#000" stop-opacity="0"/><stop offset=".6" stop-color="#2A1020" stop-opacity=".28"/></linearGradient>
<linearGradient id="tampo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1F3530" stop-opacity=".45"/><stop offset=".25" stop-color="#1F3530" stop-opacity="0"/><stop offset="1" stop-color="#E9F1D8" stop-opacity=".08"/></linearGradient>
<linearGradient id="sombraTopo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0F1326" stop-opacity=".5"/><stop offset="1" stop-color="#0F1326" stop-opacity="0"/></linearGradient>
<linearGradient id="chamaG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F2A640"/><stop offset=".55" stop-color="#FFD978"/><stop offset="1" stop-color="#FFF6D8"/></linearGradient>
<radialGradient id="chamaHalo" r=".5"><stop offset="0" stop-color="#FFD98A" stop-opacity=".5"/><stop offset=".4" stop-color="#F2B860" stop-opacity=".16"/><stop offset="1" stop-color="#F2B860" stop-opacity="0"/></radialGradient>
<radialGradient id="brilhoCarta" r=".5"><stop offset="0" stop-color="#F6DFA0" stop-opacity=".42"/><stop offset=".6" stop-color="#E4C98A" stop-opacity=".12"/><stop offset="1" stop-color="#E4C98A" stop-opacity="0"/></radialGradient>
<radialGradient id="halo" r=".5"><stop offset=".55" stop-color="#C9A55E" stop-opacity=".24"/><stop offset="1" stop-color="#C9A55E" stop-opacity="0"/></radialGradient>
<radialGradient id="luaG" cx="42%" cy="38%" r="68%"><stop offset="0" stop-color="#FBF1D6"/><stop offset=".65" stop-color="#F0DDAE"/><stop offset="1" stop-color="#DDBF80"/></radialGradient>
<radialGradient id="irisG" cx="45%" cy="35%" r="70%"><stop offset="0" stop-color="#EEF3A8"/><stop offset=".55" stop-color="#C9D86A"/><stop offset="1" stop-color="#7E9A3C"/></radialGradient>
<pattern id="ceu" width="46" height="52" patternUnits="userSpaceOnUse"><circle cx="8" cy="10" r="1" fill="#C9A55E" opacity=".55"/><circle cx="31" cy="36" r=".8" fill="#F1E3CF" opacity=".45"/></pattern>
<pattern id="ceuP" width="38" height="34" patternUnits="userSpaceOnUse"><circle cx="6" cy="8" r=".9" fill="#E4C98A" opacity=".45"/><circle cx="25" cy="25" r=".7" fill="#F1E3CF" opacity=".3"/></pattern>
<pattern id="estrelinhas" width="30" height="34" patternUnits="userSpaceOnUse"><path transform="translate(8 9) scale(.32)" d="M0,-10 Q0,0 10,0 Q0,0 0,10 Q0,0 -10,0 Q0,0 0,-10Z" fill="#E4C98A" opacity=".8"/><circle cx="23" cy="26" r=".9" fill="#F6E9D8" opacity=".6"/></pattern>
<clipPath id="janela"><path d="M19,1300 V250 A231,231 0 0 1 481,250 V1300 Z"/></clipPath>
<path id="br" d="M0,-10 Q0,0 10,0 Q0,0 0,10 Q0,0 -10,0 Q0,0 0,-10Z"/>
'''


# ================================================================== a página
CSS = '''
:root{--papel:#ECDFC5;--noite:#262E4A;--noite2:#1A2036;--ouro:#C9A55E;--ouro-e:#9C7A3C;--jade:#4E7068;--creme:#F4E8E2}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1350px;background:var(--papel)}
.peca{position:relative;width:1080px;height:1350px;overflow:hidden;color:var(--noite);background:var(--papel) var(--fundo) 0 0/1080px 1350px no-repeat}
.peca::before,.peca::after{content:"";position:absolute;inset:0;pointer-events:none;background-size:1080px 1440px;z-index:50}
.peca::before{background-image:var(--grao-neg);mix-blend-mode:multiply;opacity:.7}
.peca::after{background-image:var(--grao-pos);mix-blend-mode:plus-lighter;opacity:.5}
.peca>*{position:absolute}
svg{overflow:visible}
.carta{left:56px;top:56px;width:500px;height:1300px;filter:drop-shadow(0 22px 34px rgba(16,20,40,.38))}
.col{left:600px;width:440px;top:74px;bottom:66px;display:flex;flex-direction:column;justify-content:space-between;align-items:flex-start}
.grupo{display:flex;flex-direction:column;align-items:flex-start}
.selo{display:flex;align-items:center;gap:12px;font-family:'Cinzel';font-weight:700;font-size:21px;letter-spacing:.32em;color:var(--ouro-e)}
.selo svg{flex:none}
.tiragem{margin-top:34px;font-family:'Cormorant';font-style:italic;font-weight:500;font-size:68px;line-height:1;color:var(--noite)}
.taro{margin-top:-6px;margin-left:-10px;font-family:'Italiana';font-size:214px;line-height:.9;color:var(--noite);letter-spacing:.01em}
.sub{margin-top:20px;font-family:'Cormorant';font-style:italic;font-weight:500;font-size:38px;line-height:1.14;color:var(--noite)}
.precos{display:flex;gap:24px;margin-left:2px}
.preco{position:relative;width:208px;height:344px;border-radius:104px 104px 12px 12px;background:var(--noite) var(--tex-preco) 0 0/208px 344px no-repeat;
  box-shadow:0 16px 26px rgba(16,20,40,.34);display:flex;flex-direction:column;align-items:center;color:var(--creme)}
.preco:nth-child(1){transform:rotate(-2.2deg)}
.preco:nth-child(2){transform:rotate(1.8deg) translateY(8px)}
.preco::before{content:"";position:absolute;inset:9px;border:1.6px solid var(--ouro);border-radius:95px 95px 6px 6px}
.preco::after{content:"";position:absolute;inset:15px;border:.8px solid rgba(201,165,94,.65);border-radius:89px 89px 3px 3px}
.preco .est{margin-top:54px;height:22px;display:flex;gap:7px;align-items:center}
.preco .n{margin-top:14px;font-family:'DM Serif Display';font-size:122px;line-height:.86;color:var(--creme)}
.preco .q{margin-top:8px;font-family:'Cinzel';font-weight:700;font-size:21px;letter-spacing:.14em;color:var(--creme)}
.preco .fio2{margin:14px 0 6px;display:flex;align-items:center;gap:8px;color:var(--ouro)}
.preco .fio2 i{display:block;width:44px;height:1px;background:currentColor}
.preco .v{font-family:'DM Serif Display';font-size:60px;line-height:1;color:#E9CC8C;white-space:nowrap}
.preco .v small{font-size:31px;margin-right:9px;vertical-align:.42em}
.fio{margin:0 0 20px;display:flex;align-items:center;gap:14px;color:var(--ouro)}
.fio i{display:block;width:120px;height:1px;background:currentColor}
.cta{font-family:'Cinzel';font-weight:700;font-size:22px;letter-spacing:.15em;color:var(--jade)}
.cta2{margin-top:6px;font-family:'Cormorant';font-style:italic;font-weight:600;font-size:33px;color:var(--noite)}
'''

BR = '<svg width="%d" height="%d" viewBox="-10 -10 20 20"><path d="M0,-10 Q0,0 10,0 Q0,0 0,10 Q0,0 -10,0 Q0,0 0,-10Z" fill="%s"/></svg>'


def preco(n, palavra, valor):
    est = "".join(BR % (18, 18, "#E9CC8C") for _ in range(n))
    return ('<div class="preco"><div class="est">%s</div><div class="n">%d</div><div class="q">%s</div>'
            '<div class="fio2"><i></i>%s<i></i></div><div class="v"><small>R$</small>%d</div></div>') % (est, n, palavra, BR % (10, 10, "currentColor"), valor)


COLUNA = '''
<div class="col">
  <div class="grupo">
    <div class="selo">%s<span>Agenda aberta</span>%s</div>
    <div class="tiragem">Tiragem de</div>
    <div class="taro">Tarô</div>
    <div class="sub">Traga a sua pergunta:<br>as cartas respondem</div>
  </div>
  <div class="precos">%s%s</div>
  <div class="grupo">
    <div class="fio"><i></i>%s<i></i></div>
    <div class="cta">Agende a sua tiragem</div>
    <div class="cta2">é só chamar no direct</div>
  </div>
</div>
''' % (BR % (14, 14, "currentColor"), BR % (14, 14, "currentColor"), preco(1, "pergunta", 10), preco(4, "perguntas", 35), BR % (14, 14, "currentColor"))


def aneis_fundo():
    """Anéis da lua saindo da carta para o papel (o elemento grande e transparente da arte 02)."""
    r = ""
    for a in range(0, 360, 5):
        t = math.radians(a)
        l = 520 if a % 15 == 0 else 496
        r += "M%.1f,%.1f L%.1f,%.1f " % (math.cos(t) * 476, math.sin(t) * 476, math.cos(t) * l, math.sin(t) * l)
    return ('<svg style="left:0;top:0" width="1080" height="1350" viewBox="0 0 1080 1350"><g fill="none" stroke="%s" transform="translate(306 392)">'
            '<circle r="452" stroke-width="1.1" opacity=".16"/><circle r="466" stroke-width=".6" opacity=".12"/>'
            '<circle r="560" stroke-width="1" stroke-dasharray="2 10" opacity=".16"/><path d="%s" stroke-width="1" opacity=".1"/></g></svg>') % (NOITE, r)


def peca():
    fundo = b64(papel(1080, 1350, "#ECDFC5", 75, forca=1.3, fibras=2.0, pintas=.8, borda=.10, relevo=.22))
    tex_preco = b64(papel(208, 344, NOITE, 86, forca=1.6, fibras=2.2, borda=.18))
    return ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Tiragem de tarô</title>\n<!--ACERVO-->\n'
            '<style>%s .peca{--fundo:url(%s);--tex-preco:url(%s)}</style></head><body><div class="peca">%s'
            '<svg class="carta" viewBox="0 0 500 1300"><defs>%s</defs>%s</svg>%s</div></body></html>') % (
        CSS, fundo, tex_preco, aneis_fundo(), DEFS_CARTA, carta(), COLUNA)


def exportar(nome, html, arquivo_final, final=False):
    from playwright.sync_api import sync_playwright
    html = html.replace("<!--ACERVO-->", montar.ACERVO_CSS)
    arq = os.path.join(AQUI, "saida", nome + ".final.html")
    open(arq, "w", encoding="utf-8").write(html)
    destinos = [(1, os.path.join(AQUI, "saida", nome + ".png")), (2, os.path.join(AQUI, "saida", nome + "@2x.png"))]
    if final:
        os.makedirs(D, exist_ok=True)
        destinos += [(1, os.path.join(D, arquivo_final + ".png")), (2, os.path.join(D, arquivo_final + " (alta, 2160x2700).png"))]
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for esc, destino in destinos:
            pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=esc)
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(1500)
            pg.screenshot(path=destino)
        b.close()


if __name__ == "__main__":
    exportar("post_tarot", peca(), "Tiragem de tarô - post", final="--final" in sys.argv)
    print("ok")
