# -*- coding: utf-8 -*-
"""Mascote do Entrelinhas, rodada 3: gatos FELPUDOS com marca propria.

A. Pelucia de tracos: o pelo inteiro feito de riscos curtos seguindo o caimento; tufos na silhueta.
B. Listras de escrita: rajado cujas listras sao linhas de texto escritas a mao.
C. Entre as linhas: gato-pao espremido entre as duas linhas da marca (Entre [gato] linhas).
uso: py felpudo.py [a b c]
"""
import os, sys, math, re, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar
import fofos as F
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

AQUI = os.path.dirname(os.path.abspath(__file__))
TINTA = "#1E1418"


# ------------------------------------------------------------------ caminho -> poligono
def amostrar(d, passos=16, dx=0, dy=0, k=1.0, cy=0):
    toks = re.findall(r"[MLCZ]|-?\d+(?:\.\d+)?", d)
    pts, i, cmd, cur = [], 0, None, (0, 0)
    tf = lambda x, y: (x * k + dx, (y - cy) * k + cy + dy)
    while i < len(toks):
        t = toks[i]
        if t in "MLCZ":
            cmd = t
            i += 1
            continue
        if cmd in ("M", "L"):
            cur = (float(toks[i]), float(toks[i + 1]))
            pts.append(tf(*cur))
            i += 2
        elif cmd == "C":
            x1, y1, x2, y2, x, y = map(float, toks[i:i + 6])
            x0, y0 = cur
            for s in range(1, passos + 1):
                u = s / passos
                a, b, c, e = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u ** 2, u ** 3
                pts.append(tf(a * x0 + b * x1 + c * x2 + e * x, a * y0 + b * y1 + c * y2 + e * y))
            cur = (x, y)
            i += 6
    return Polygon(pts).buffer(0)


def caminho(poly):
    if hasattr(poly, "geoms"):
        return " ".join(caminho(g) for g in poly.geoms if not g.is_empty)
    c = list(poly.exterior.coords)
    return "M" + " L".join("%.1f,%.1f" % p for p in c) + "Z"


def norm(x, y):
    m = math.hypot(x, y) or 1
    return x / m, y / m


# ------------------------------------------------------------------ o pelo
def pelo(poly, n, fluxo, tom, L=(9, 16), larg=(1.3, 2.1), seed=1, curva=.28):
    """Riscos curtos dentro do poligono. tom(x,y,r) -> cor. Devolve {(cor,w): [d]}."""
    random.seed(seed)
    x0, y0, x1, y1 = poly.bounds
    saida = {}
    feitos = 0
    tent = 0
    while feitos < n and tent < n * 8:
        tent += 1
        x, y = x0 + random.random() * (x1 - x0), y0 + random.random() * (y1 - y0)
        if not poly.contains(Point(x, y)):
            continue
        dx, dy = norm(*fluxo(x, y))
        l = L[0] + random.random() * (L[1] - L[0])
        c = (random.random() - .5) * 2 * curva * l
        px, py = -dy, dx
        mx, my = x + dx * l / 2 + px * c, y + dy * l / 2 + py * c
        cor = tom(x, y, random.random())
        w = round(larg[0] + random.random() * (larg[1] - larg[0]), 1)
        saida.setdefault((cor, w), []).append("M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" % (x - dx * l / 2, y - dy * l / 2, mx, my, x + dx * l / 2, y + dy * l / 2))
        feitos += 1
    return saida


def tufos(poly, fluxo, cor, passo=7.5, L=(7, 13), w=1.8, seed=2, mistura=.62, pular=None):
    """Tufos na borda: pares de riscos curvos que saem para fora, deitados no sentido do pelo.
    cor pode ser texto ou funcao (x,y) -> cor (para a borda mudar de tom sobre o peito branco)."""
    random.seed(seed)
    anel = poly.exterior
    total = anel.length
    grupos = {}
    t = 0.0
    while t < total:
        p = anel.interpolate(t)
        a, b = anel.interpolate(max(0, t - 2)), anel.interpolate(min(total, t + 2))
        tx, ty = norm(b.x - a.x, b.y - a.y)
        nx, ny = -ty, tx
        if poly.contains(Point(p.x + nx * 3, p.y + ny * 3)):
            nx, ny = -nx, -ny
        if pular and pular(p.x, p.y, nx, ny):
            t += passo
            continue
        fx, fy = norm(*fluxo(p.x, p.y))
        base = math.atan2(ny * (1 - mistura) + fy * mistura, nx * (1 - mistura) + fx * mistura)
        c_ = cor(p.x, p.y) if callable(cor) else cor
        for j, (dang, kl) in enumerate(((0, 1), (random.choice((-1, 1)) * .32, .72))):
            ang = base + dang
            dx, dy = math.cos(ang), math.sin(ang)
            l = (L[0] + random.random() * (L[1] - L[0])) * kl
            curv = (random.random() - .5) * .9 * l
            sx, sy = p.x - nx * 6 + tx * j * 2, p.y - ny * 6 + ty * j * 2
            ex, ey = p.x + dx * l, p.y + dy * l
            grupos.setdefault(c_, []).append("M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" % (sx, sy, (sx + ex) / 2 - dy * curv, (sy + ey) / 2 + dx * curv, ex, ey))
        t += passo * (.75 + random.random() * .5)
    return "".join('<path d="%s" fill="none" stroke="%s" stroke-width="%g" stroke-linecap="round"/>' % (" ".join(v), c, w) for c, v in grupos.items())


def desenha(mapa, op=1):
    return "".join('<path d="%s" fill="none" stroke="%s" stroke-width="%g" stroke-linecap="round" opacity="%g"/>' % (" ".join(v), c, w, op) for (c, w), v in mapa.items())


def tons(paleta, luz_x=-1, luz_y=-1.2, cx=0, cy=-150, alcance=260):
    """Escolhe escuro/medio/claro conforme a posicao em relacao a luz (alto a esquerda)."""
    def f(x, y, r):
        k = ((x - cx) * luz_x + (y - cy) * luz_y) / alcance  # >0 = lado da luz
        if r < .32 + k * .25:
            return paleta["claro"]
        if r > .72 + k * .2:
            return paleta["escuro"]
        return paleta["medio"]
    return f


def olhos_brilho(iris, y=-262, dx=38, rx=15.5, ry=17.5, olhar=(0, 0)):
    s = ""
    for x in (-dx, dx):
        s += '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="%s"/>' % (x, y, rx, ry, TINTA)
        s += '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="%s"/>' % (x + olhar[0] * .4, y + 2 + olhar[1] * .4, rx * .78, ry * .8, iris)
        s += '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="%s"/>' % (x + olhar[0], y + 2 + olhar[1], rx * .42, ry * .62, TINTA)
        s += '<circle cx="%g" cy="%g" r="%g" fill="#FFFDF6"/><circle cx="%g" cy="%g" r="%g" fill="#FFFDF6"/>' % (x + 5, y - 6, rx * .36, x - 5, y + 8, rx * .15)
    return s


def rosto_fofo(nariz="#F18E9B", bigode="#FFFDF6", op_bigode=.85):
    s = '<ellipse cx="-64" cy="-232" rx="16" ry="9" fill="#F28C9A" opacity=".55" filter="url(#borrao)"/><ellipse cx="64" cy="-232" rx="16" ry="9" fill="#F28C9A" opacity=".55" filter="url(#borrao)"/>'
    s += '<path d="M-9,-246 L9,-246 C9,-240 3,-237 0,-236 C-3,-237 -9,-240 -9,-246Z" fill="%s" stroke="%s" stroke-width="1.6"/>' % (nariz, TINTA)
    s += '<path d="M0,-236 L0,-230 M-14,-229 C-11,-221 -3,-221 0,-230 C3,-221 11,-221 14,-229" fill="none" stroke="%s" stroke-width="2.6" stroke-linecap="round"/>' % TINTA
    s += '<path d="M-74,-240 L-148,-252 M-74,-232 L-150,-228 M-72,-224 L-140,-208 M74,-240 L148,-252 M74,-232 L150,-228 M72,-224 L140,-208" fill="none" stroke="%s" stroke-width="1.5" stroke-linecap="round" opacity="%g"/>' % (bigode, op_bigode)
    return s


K_CAB = 1.08  # a cabeca dos fofos ja vinha 8% maior


def partes_sentado():
    corpo = amostrar(F.CORPO).buffer(4)
    cab = amostrar(F.CABECA, k=K_CAB, cy=-262).buffer(4)
    oe = amostrar(F.ORELHA_E, k=K_CAB, cy=-262)
    od = amostrar(F.ORELHA_D, k=K_CAB, cy=-262)
    return corpo, cab, oe, od


def fluxo_corpo(x, y):
    return (x / 230, 1)


def fluxo_cab(x, y):
    return (x, y + 236)


def fluxo_orelha(lado):
    return lambda x, y: (lado * .25, -1)


# ================================================================== A · PELUCIA DE TRACOS (frajola no ceu amarelo do tarot)
def gato_pelucia(pal_preto, pal_branco, iris, uid="a"):
    corpo, cab, oe, od = partes_sentado()
    brancos = unary_union([amostrar(F.PEITO).buffer(6), amostrar(F.FOCINHO, k=K_CAB, cy=-262).buffer(8),
                           amostrar("M-9,-306 L9,-306 L24,-246 L-24,-246 Z", k=K_CAB, cy=-262)])
    pata_e, pata_d = amostrar(F.PATA_E).buffer(3), amostrar(F.PATA_D).buffer(3)
    cauda = amostrar(F.CAUDA_CIMA)
    tp, tb = tons(pal_preto), tons(pal_branco)

    def tom_corpo(x, y, r):
        return tb(x, y, r) if brancos.contains(Point(x, y)) else tp(x, y, r)

    s = []
    # rabo (atras), com ponta branca
    s.append('<path d="%s" fill="%s"/>' % (caminho(cauda), pal_preto["base"]))
    s.append(desenha(pelo(cauda, 260, lambda x, y: (.3, -1), lambda x, y, r: tb(x, y, r) if y < -150 else tp(x, y, r), seed=11)))
    s.append(tufos(cauda, lambda x, y: (.3, -1), pal_preto["borda"], seed=12))
    # orelhas
    for o, lado in ((oe, -1), (od, 1)):
        s.append('<path d="%s" fill="%s"/>' % (caminho(o), pal_preto["base"]))
        dentro = amostrar(F.DENTRO_E if lado < 0 else F.DENTRO_D, k=K_CAB, cy=-262)
        s.append('<path d="%s" fill="#E99AA6"/>' % caminho(dentro))
        s.append(desenha(pelo(dentro, 40, fluxo_orelha(lado), lambda x, y, r: "#FFF6F0", L=(6, 11), larg=(1, 1.4), seed=21 + lado)))
        s.append(tufos(o, fluxo_orelha(lado), pal_preto["borda"], seed=23 + lado, passo=6))
    # corpo
    s.append('<path d="%s" fill="%s"/>' % (caminho(corpo), pal_preto["base"]))
    s.append('<clipPath id="cb%s"><path d="%s"/></clipPath>' % (uid, caminho(corpo)))
    s.append('<g clip-path="url(#cb%s)"><path d="%s" fill="%s"/></g>' % (uid, caminho(brancos), pal_branco["base"]))
    s.append(desenha(pelo(corpo, 1500, fluxo_corpo, tom_corpo, seed=31)))
    s.append(tufos(corpo, fluxo_corpo, lambda x, y: pal_branco["borda"] if brancos.buffer(10).contains(Point(x, y)) else pal_preto["borda"], seed=32))
    # linhas das pernas e patas brancas
    s.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round" opacity=".55"/>' % (F.PERNAS, pal_branco["escuro"]))
    for pt, sd in ((pata_e, 41), (pata_d, 42)):
        s.append('<path d="%s" fill="%s"/>' % (caminho(pt), pal_branco["base"]))
        s.append(desenha(pelo(pt, 70, lambda x, y: (0, 1), tb, L=(5, 9), seed=sd)))
        s.append(tufos(pt, lambda x, y: (0, 1), pal_branco["borda"], passo=5, L=(4, 8), w=1.6, seed=sd + 5))
    s.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-linecap="round"/>' % (F.DEDOS, pal_branco["borda"]))
    # cabeca
    s.append('<path d="%s" fill="%s"/>' % (caminho(cab), pal_preto["base"]))
    s.append('<clipPath id="ch%s"><path d="%s"/></clipPath>' % (uid, caminho(cab)))
    s.append('<g clip-path="url(#ch%s)"><path d="%s" fill="%s"/></g>' % (uid, caminho(brancos), pal_branco["base"]))
    s.append(desenha(pelo(cab, 1250, fluxo_cab, tom_corpo, L=(7, 13), seed=51)))
    s.append(tufos(cab, fluxo_cab, lambda x, y: pal_branco["borda"] if brancos.buffer(14).contains(Point(x, y)) or y > -176 * K_CAB else pal_preto["borda"],
                   seed=52, L=(9, 16), mistura=.45, pular=lambda x, y, nx, ny: ny > .45))
    s.append(olhos_brilho(iris))
    s.append(rosto_fofo())
    return "".join(s)


def peca_a():
    preto = dict(base="#2A2226", escuro="#120D10", medio="#3E3439", claro="#6E6168", borda="#120D10")
    branco = dict(base="#F6F0E4", escuro="#C9BCA9", medio="#E6DCCB", claro="#FFFFFF", borda="#B8AA96")
    gato = gato_pelucia(preto, branco, "#C9D86A")
    lua = ('<mask id="mlua"><rect x="780" y="110" width="200" height="200" fill="#fff"/><circle cx="912" cy="196" r="62" fill="#000"/></mask>'
           '<g mask="url(#mlua)"><circle cx="880" cy="210" r="70" fill="#FBF0CF" stroke="#3B2A33" stroke-width="3"/></g>'
           '<path d="M880,140 A70,70 0 0 0 880,280" fill="none"/>')
    sol = '<circle cx="540" cy="486" r="200" fill="#F7DC8C"/><circle cx="540" cy="486" r="200" fill="none" stroke="#3B2A33" stroke-width="2.4"/>'
    cena = (sol + F.raios(540, 486, 214, 300, 6, "#3B2A33", .7, 1.16) + lua +
            F.brilhos([(170, 200, 1.4), (230, 330, .8), (880, 420, .9), (140, 640, .8), (940, 640, 1.1), (330, 150, .6)], "#3B2A33") +
            '<path d="M120,850 C360,836 720,836 960,850" stroke="#3B2A33" stroke-width="2.6" fill="none"/>' +
            F.poe(gato, 540, 846, 1.3) + F.faixa(540, 958, "O LEITOR", "0", cor="#FBF0CF", tinta="#3B2A33"))
    return pagina("Mascote · pelúcia de traços", cena, "#EDBE4F", "#F6D277")


# ================================================================== B · LISTRAS DE ESCRITA (rajado laranja no petroleo)
FRASE = "entre uma linha e outra mora um gato que lê o que ninguém escreveu · "


def listra_texto(d, tam=17, cor="#9C4A1C", inicio=0, uid="t", faixa="#C8642B", larg=None):
    larg = larg or tam * 1.25
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%g" stroke-linecap="round"/>'
            '<path id="%s" d="%s" fill="none"/><text font-family="Caveat" font-weight="700" font-size="%g" fill="#FFE6BF" letter-spacing=".3" dy="%g">'
            '<textPath href="#%s" startOffset="%g">%s</textPath></text>') % (d, faixa, larg, uid, d, tam, tam * .3, uid, inicio, FRASE * 3)


def listra_lisa(d, larg=12, faixa="#C8642B"):
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%g" stroke-linecap="round"/>' % (d, faixa, larg)


def gato_escrito(uid="b"):
    corpo, cab, oe, od = partes_sentado()
    cauda = amostrar(F.CAUDA_CIMA)
    LAR = dict(base="#F2A55A", escuro="#D27F3A", medio="#E89348", claro="#FFD49A", borda="#B4561F")
    CRE = dict(base="#FCF1E1", escuro="#E5D2B8", medio="#F3E5D0", claro="#FFFFFF", borda="#D7BFA0")
    brancos = unary_union([amostrar(F.PEITO).buffer(6), amostrar(F.FOCINHO, k=K_CAB, cy=-262).buffer(8)])
    tl, tc = tons(LAR), tons(CRE)
    tom = lambda x, y, r: tc(x, y, r) if brancos.contains(Point(x, y)) else tl(x, y, r)
    s = []
    s.append('<path d="%s" fill="%s"/>' % (caminho(cauda), LAR["base"]))
    s.append('<clipPath id="cc%s"><path d="%s"/></clipPath>' % (uid, caminho(cauda)))
    s.append('<g clip-path="url(#cc%s)">' % uid + "".join(listra_lisa("M110,%d L240,%d" % (y, y - 18), 12) for y in range(-160, -20, 30)) + '</g>')
    s.append(tufos(cauda, lambda x, y: (.3, -1), LAR["borda"], seed=12))
    for o, lado in ((oe, -1), (od, 1)):
        s.append('<path d="%s" fill="%s"/>' % (caminho(o), LAR["base"]))
        s.append('<path d="%s" fill="#F2A3AE"/>' % caminho(amostrar(F.DENTRO_E if lado < 0 else F.DENTRO_D, k=K_CAB, cy=-262)))
        s.append(tufos(o, fluxo_orelha(lado), LAR["borda"], seed=23 + lado, passo=6))
    # corpo com listras de texto em arco
    s.append('<path d="%s" fill="%s"/>' % (caminho(corpo), LAR["base"]))
    s.append('<clipPath id="cb%s"><path d="%s"/></clipPath>' % (uid, caminho(corpo)))
    listras = ""
    for i, (y, curva) in enumerate([(-150, 22), (-108, 24), (-66, 26), (-24, 26)]):
        listras += listra_texto("M-170,%d Q0,%d 170,%d" % (y, y + curva * 2, y), 17, "#9C4A1C", -i * 41 % 130, "tb%d" % i)
    s.append('<g clip-path="url(#cb%s)">%s<path d="%s" fill="%s"/></g>' % (uid, listras, caminho(brancos), CRE["base"]))
    s.append(desenha(pelo(corpo, 650, fluxo_corpo, tom, seed=31), .55))
    s.append(tufos(corpo, fluxo_corpo, LAR["borda"], seed=32))
    s.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round" opacity=".6"/>' % (F.PERNAS, LAR["borda"]))
    for pt, sd in ((amostrar(F.PATA_E).buffer(3), 41), (amostrar(F.PATA_D).buffer(3), 42)):
        s.append('<path d="%s" fill="%s"/>' % (caminho(pt), CRE["base"]))
        s.append(tufos(pt, lambda x, y: (0, 1), CRE["borda"], passo=5, L=(4, 8), w=1.6, seed=sd + 5))
    s.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-linecap="round"/>' % (F.DEDOS, CRE["borda"]))
    # cabeca: o "M" da testa e as bochechas escritos
    s.append('<path d="%s" fill="%s"/>' % (caminho(cab), LAR["base"]))
    s.append('<clipPath id="ch%s"><path d="%s"/></clipPath>' % (uid, caminho(cab)))
    testa = (listra_lisa("M-18,-346 L-14,-312") + listra_lisa("M0,-350 L0,-306") + listra_lisa("M18,-346 L14,-312") +
             "".join(listra_lisa("M%d,%d L%d,%d" % (lado * 112, y, lado * 80, y + 4), 10) for lado in (-1, 1) for y in (-266, -246)))
    s.append('<g clip-path="url(#ch%s)">%s<path d="%s" fill="%s"/></g>' % (uid, testa, caminho(brancos), CRE["base"]))
    s.append(desenha(pelo(cab, 520, fluxo_cab, tom, L=(7, 12), seed=51), .55))
    s.append(tufos(cab, fluxo_cab, LAR["borda"], seed=52, L=(9, 16), mistura=.45, pular=lambda x, y, nx, ny: ny > .45))
    s.append(olhos_brilho("#E9A83C"))
    s.append(rosto_fofo(bigode="#FFFDF6"))
    return "".join(s)


def peca_b():
    gato = gato_escrito()
    lua = '<circle cx="540" cy="470" r="215" fill="#21585A"/>' + F.raios(540, 470, 228, 300, 5, "#F2D27E", .75, 1.14)
    linhas = "".join('<path d="M60,%d L1020,%d" stroke="#F2D27E" stroke-width="1" opacity=".14"/>' % (y, y) for y in range(80, 1080, 38))
    cena = (linhas + lua + F.brilhos([(180, 220, 1.3), (900, 210, 1.0), (160, 620, .8), (930, 600, .9), (300, 120, .6), (780, 120, .6)], "#F2D27E") +
            '<path d="M120,850 C360,836 720,836 960,850" stroke="#F2D27E" stroke-width="2.4" fill="none"/>' +
            F.poe(gato, 540, 846, 1.3) +
            '<text x="540" y="968" text-anchor="middle" font-family="Caveat" font-weight="700" font-size="40" fill="#F2D27E">entre uma linha e outra mora um gato</text>')
    return pagina("Mascote · listras de escrita", cena, "#173E41", "#1F4F52")


# ================================================================== C · ENTRE AS LINHAS (gato-pao na marca)
PAO = "M-232,0 C-266,-10 -270,-124 -212,-170 C-160,-210 -60,-216 0,-216 C60,-216 160,-210 212,-170 C270,-124 266,-10 232,0 Z"


def gato_pao(uid="c"):
    CIN = dict(base="#B7B2C4", escuro="#7D7790", medio="#9A95AB", claro="#E9E6F2", borda="#4E4A5C")
    BR = dict(base="#F7F3EE", escuro="#D6CFC8", medio="#ECE6DF", claro="#FFFFFF", borda="#B7AEA6")
    dy = 137  # a cabeca dos fofos (centro -262) desce para -125
    corpo = amostrar(PAO).buffer(3)
    cab = amostrar(F.CABECA, k=K_CAB, cy=-262, dy=dy).buffer(4)
    oe = amostrar(F.ORELHA_E, k=K_CAB, cy=-262, dy=dy)
    od = amostrar(F.ORELHA_D, k=K_CAB, cy=-262, dy=dy)
    focinho = amostrar(F.FOCINHO, k=K_CAB, cy=-262, dy=dy).buffer(8)
    tcin, tbr = tons(CIN, cy=-110, alcance=300), tons(BR, cy=-110)
    # listras escuras: faixas em arco nos flancos, M na testa
    curvas = []
    for lado in (-1, 1):
        for x0 in (110, 150, 190):
            curvas.append(LineString([(lado * x0, -196 + (x0 - 110) * .35), (lado * (x0 + 12), -130), (lado * (x0 + 8), -70), (lado * (x0 - 6), -12)]))
    for x0 in (-16, 0, 16):
        curvas.append(LineString([(x0 * 1.2, -212), (x0, -182)]))
    for lado in (-1, 1):
        for y0 in (-136, -118):
            curvas.append(LineString([(lado * 100, y0), (lado * 74, y0 + 4)]))
    faixas = unary_union([c.buffer(8) for c in curvas])
    def listrado(x, y):
        return faixas.contains(Point(x, y))
    tom = lambda x, y, r: tbr(x, y, r) if focinho.contains(Point(x, y)) else (("#5F5A70" if r < .75 else CIN["medio"]) if listrado(x, y) else tcin(x, y, r))
    s = []
    cauda = amostrar("M206,-30 C250,-10 262,40 248,96 C240,128 214,140 200,124 C222,112 230,80 226,50 C222,20 210,4 190,-4 Z")
    s.append('<path d="%s" fill="%s"/>' % (caminho(cauda), CIN["base"]))
    s.append(desenha(pelo(cauda, 120, lambda x, y: (0, 1), tcin, L=(7, 12), seed=61)))
    s.append(tufos(cauda, lambda x, y: (0, 1), CIN["borda"], seed=62))
    s.append('<path d="%s" fill="%s"/>' % (caminho(corpo), CIN["base"]))
    s.append('<clipPath id="cp%s"><path d="%s"/></clipPath><g clip-path="url(#cp%s)"><ellipse cx="0" cy="-10" rx="250" ry="70" fill="#7D7790" opacity=".45" filter="url(#brilho)"/>'
             '<ellipse cx="0" cy="-40" rx="120" ry="60" fill="#5F5A70" opacity=".35" filter="url(#brilho)"/></g>' % (uid, caminho(corpo), uid))
    s.append('<g clip-path="url(#cp%s)"><path d="%s" fill="#6A6480" opacity=".85"/></g>' % (uid, caminho(faixas)))
    s.append(desenha(pelo(corpo, 1800, lambda x, y: (x / 160, .45), tom, seed=71), .92))
    s.append(tufos(corpo, lambda x, y: (x / 160, .45), CIN["borda"], seed=72, pular=lambda x, y, nx, ny: ny > .6))
    for o, lado in ((oe, -1), (od, 1)):
        s.append('<path d="%s" fill="%s"/>' % (caminho(o), CIN["base"]))
        s.append('<path d="%s" fill="#EFA0AE"/>' % caminho(amostrar(F.DENTRO_E if lado < 0 else F.DENTRO_D, k=K_CAB, cy=-262, dy=dy)))
        s.append(tufos(o, fluxo_orelha(lado), CIN["borda"], seed=23 + lado, passo=6))
    s.append('<g clip-path="url(#cp%s)"><ellipse cx="0" cy="-26" rx="118" ry="30" fill="#3F3A4D" opacity=".5" filter="url(#brilho)"/></g>' % uid)
    s.append('<path d="%s" fill="%s"/>' % (caminho(cab), CIN["base"]))
    cab_faixas = unary_union([c.buffer(7) for c in curvas[-7:]]).intersection(cab)
    s.append('<clipPath id="ch%s"><path d="%s"/></clipPath><g clip-path="url(#ch%s)"><path d="%s" fill="%s"/>%s</g>' % (uid, caminho(cab), uid, caminho(focinho), BR["base"],
             "".join('<path d="%s" fill="#6A6480" opacity=".85"/>' % caminho(g) for g in getattr(cab_faixas, "geoms", [cab_faixas]) if not g.is_empty)))
    s.append(desenha(pelo(cab, 1150, lambda x, y: (x, y + 99), tom, L=(7, 13), seed=81)))
    s.append(tufos(cab, lambda x, y: (x, y + 99), CIN["borda"], seed=82, L=(9, 16), mistura=.45, pular=lambda x, y, nx, ny: ny > .55))
    s.append('<g transform="translate(0 %d)">' % dy + olhos_brilho("#8FC3E6") + rosto_fofo(bigode="#FFFDF6") + '</g>')
    return "".join(s)


def patinhas_c():
    BR = dict(base="#F7F3EE", borda="#8D8578")
    s = ""
    for x in (-52, 52):
        d = "M%g,-10 C%g,-14 %g,-14 %g,-10 L%g,18 C%g,30 %g,30 %g,18 Z" % (x - 24, x - 12, x + 12, x + 24, x + 22, x + 12, x - 12, x - 22)
        s += '<path d="%s" fill="#B7B2C4"/>' % d
        s += '<path d="M%g,6 C%g,0 %g,0 %g,6 C%g,24 %g,30 %g,30 C%g,30 %g,24 %g,6Z" fill="%s" stroke="%s" stroke-width="1.8"/>' % (x - 22, x - 10, x + 10, x + 22, x + 22, x + 12, x, x - 12, x - 22, x - 22, BR["base"], BR["borda"])
        s += '<path d="M%g,20 L%g,28 M%g,20 L%g,29" stroke="%s" stroke-width="1.6" stroke-linecap="round"/>' % (x - 7, x - 7, x + 7, x + 7, BR["borda"])
    return s


def peca_c():
    gato = gato_pao()
    TOPO, BASE, K, X = 480, 700, .9, 540
    y_chao = BASE
    linha = lambda y: '<path d="M56,%d L1024,%d" stroke="#F3E7CF" stroke-width="3" stroke-linecap="round"/>' % (y, y)
    cena = (F.brilhos([(150, 240, 1.2), (920, 220, 1.0), (240, 860, .8), (860, 900, .9), (540, 150, .7)], "#E9C46A") +
            '<text x="540" y="380" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="20" letter-spacing="9" fill="#E9C46A">CLUBE DO LIVRO</text>' +
            linha(BASE) +
            F.poe(gato, X, y_chao, K) +
            linha(TOPO) +
            F.poe(gato_orelhas_por_cima(), X, y_chao, K) +
            F.poe(patinhas_c(), X, y_chao, K) +
            '<text x="300" y="%d" text-anchor="end" font-family="Cormorant" font-style="italic" font-weight="600" font-size="112" fill="#F3E7CF">Entre</text>' % (BASE - 48) +
            '<text x="780" y="%d" text-anchor="start" font-family="Cormorant" font-style="italic" font-weight="600" font-size="112" fill="#F3E7CF">linhas</text>' % (BASE - 48) +
            '<text x="540" y="840" text-anchor="middle" font-family="Caveat" font-weight="700" font-size="38" fill="#E9C46A">o gato que lê o que ninguém escreveu</text>')
    return pagina("Mascote · entre as linhas", cena, "#3B2A33", "#4C3741")


def gato_orelhas_por_cima():
    """Redesenha as orelhas e o alto da cabeca por cima da linha de cima (elas escapam da linha)."""
    full = gato_pao("c2")
    return '<clipPath id="acima"><rect x="-400" y="-400" width="800" height="%g"/></clipPath><g clip-path="url(#acima)">%s</g>' % (400 - 222, full)


def pagina(nome, corpo, fundo, centro):
    css = ('*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1080px}'
           '.peca{position:relative;width:1080px;height:1080px;overflow:hidden;background:radial-gradient(ellipse 70%% 62%% at 50%% 44%%,%s 0%%,%s 70%%)}'
           '.peca::before,.peca::after{content:"";position:absolute;inset:0;pointer-events:none;background-size:1080px 1440px;z-index:5}'
           '.peca::before{background-image:var(--grao-neg);mix-blend-mode:multiply;opacity:.7}'
           '.peca::after{background-image:var(--grao-pos);mix-blend-mode:plus-lighter;opacity:.45}'
           '.peca>svg{position:absolute;left:0;top:0}') % (centro, fundo)
    return ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>%s</title>\n<!--ACERVO-->\n<style>%s</style></head><body><div class="peca">'
            '<svg width="1080" height="1080" viewBox="0 0 1080 1080"><defs>%s</defs>%s</svg></div></body></html>') % (nome, css, F.DEFS, corpo)


PECAS = {"a": ("felpudo_a_pelucia", peca_a), "b": ("felpudo_b_escrito", peca_b), "c": ("felpudo_c_entrelinhas", peca_c)}

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    qual = sys.argv[1:] or list(PECAS)
    saida = os.path.join(os.path.dirname(AQUI), "saida")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1080})
        for k in qual:
            nome, f = PECAS[k]
            html = f().replace("<!--ACERVO-->", montar.ACERVO_CSS)
            arq = os.path.join(saida, nome + ".final.html")
            open(arq, "w", encoding="utf-8").write(html)
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(1200)
            pg.screenshot(path=os.path.join(saida, nome + ".png"))
            print(nome)
        b.close()
