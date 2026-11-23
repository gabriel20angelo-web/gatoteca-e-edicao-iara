# -*- coding: utf-8 -*-
"""Lilith × TULIPA, v5: a GATA NO ARCO (o layout da arte «02 - Lilith com a TULIPA», com o mascote no lugar da Lilith).

O frajola de pelucia de tracos, gigante e de pe, num vestido longo de noite: rosto de Bastet (olhos amendoados,
meio fechados, delineado), lua crescente flutuando entre as orelhas, a lua clara atras da cabeca, asas de coruja
caidas (Relevo de Burney), a serpente enrolada no vestido com a cabeca junto ao rosto, patas brancas segurando a
cintura, pezinhos sob a barra, rabo saindo do vestido e tres corujinhas no chao. Coluna de texto da arte 02, com
os dados certos (quintas, 13h às 14h15, a cada 15 dias, sala 713, bloco B).
uso: py post_lilith5.py   -> saida/post_lilith5.png + pasta do clube (normal e 2x) + figuras no banco
"""
import os, sys, math, re, base64
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "mascote"))
import montar
from papel import papel
import gato_banco as G
from gato_banco import Pose, elipse, capsula, spline, fluxo_linha, PRETO, BRANCO, TINTA
from felpudo import amostrar, pelo, desenha, caminho
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
from shapely import affinity
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[2]  # raiz do repositório

D = str(_REPO / 'gatoteca/artes')
VINHO, VINHO2, OURO, SALVIA, CREME = "#5C2230", "#3D1820", "#C19E5A", "#6B7E55", "#EDDFC2"
SERP, SERP_C, SERP_E = "#8B9C75", "#B5C29C", "#4A5C36"
ORELHA = "#E99AA6"
CX = 250  # eixo da carta (viewBox 500 x 1300)


def b64(c):
    return "data:image/png;base64," + base64.b64encode(open(c, "rb").read()).decode()


# ================================================================== caminhos
def pontos_caminho(d, n=64):
    """Amostra um caminho de M/C absolutos e reamostra por comprimento em n+1 pontos."""
    toks = re.findall(r"[MC]|-?\d+(?:\.\d+)?", d)
    pts, i, cmd, cur = [], 0, None, (0, 0)
    while i < len(toks):
        t = toks[i]
        if t in "MC":
            cmd = t
            i += 1
            continue
        if cmd == "M":
            cur = (float(toks[i]), float(toks[i + 1]))
            pts.append(cur)
            i += 2
        else:
            x1, y1, x2, y2, x, y = map(float, toks[i:i + 6])
            x0, y0 = cur
            for s in range(1, 41):
                u = s / 40
                a, b, c, e = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u ** 2, u ** 3
                pts.append((a * x0 + b * x1 + c * x2 + e * x, a * y0 + b * y1 + c * y2 + e * y))
            cur = (x, y)
            i += 6
    acc = [0]
    for (a, b), (c, d_) in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.hypot(c - a, d_ - b))
    L, out, j = acc[-1], [], 0
    for k in range(n + 1):
        s = L * k / n
        while j < len(acc) - 2 and acc[j + 1] < s:
            j += 1
        f = (s - acc[j]) / ((acc[j + 1] - acc[j]) or 1)
        out.append((pts[j][0] + (pts[j + 1][0] - pts[j][0]) * f, pts[j][1] + (pts[j + 1][1] - pts[j][1]) * f))
    return out


def tubo(d, w0, w1, n=56):
    """Trecho da serpente: tubo afilado com barriga clara, escamas em V e contorno de ouro."""
    P = pontos_caminho(d, n)
    E, Dd, C = [], [], []
    for i, (x, y) in enumerate(P):
        a, b = P[max(0, i - 1)], P[min(n, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        m = math.hypot(tx, ty) or 1
        tx, ty = tx / m, ty / m
        w = (w0 + (w1 - w0) * i / n) / 2
        E.append((x - ty * w, y + tx * w))
        Dd.append((x + ty * w, y - tx * w))
        C.append((x, y, tx, ty, w))
    contorno = "M" + " L".join("%.1f,%.1f" % q for q in E + Dd[::-1]) + "Z"
    s = '<path d="%s" fill="%s"/>' % (contorno, SERP)
    s += '<path d="M%s" fill="none" stroke="%s" stroke-width="3.2" opacity=".75"/>' % (" L".join("%.1f,%.1f" % q for q in E), SERP_C)
    s += '<path d="M%s" fill="none" stroke="%s" stroke-width="2.6" opacity=".35"/>' % (" L".join("%.1f,%.1f" % q for q in Dd), SERP_E)
    esc = ""
    for i in range(2, len(C) - 1, 2):
        x, y, tx, ty, w = C[i]
        k = w * .62
        esc += "M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f " % (x - ty * k - tx * k * .6, y + tx * k - ty * k * .6, x, y, x + ty * k - tx * k * .6, y - tx * k - ty * k * .6)
    s += '<path d="%s" fill="none" stroke="%s" stroke-width="1.1" opacity=".8"/>' % (esc, SERP_E)
    s += '<path d="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-linejoin="round"/>' % (contorno, OURO)
    return s


def cabeca_serpente(x, y, rot, k=1.6):
    s = '<g transform="translate(%g %g) rotate(%g) scale(%g)">' % (x, y, rot, k)
    s += '<path d="M-9,2 C-12,-6 -11,-14 -7,-20 C-4,-26 -2,-29 0,-29 C2,-29 4,-26 7,-20 C11,-14 12,-6 9,2 Z" fill="%s" stroke="%s" stroke-width=".9"/>' % (SERP, OURO)
    s += '<path d="M-4,-6 L0,-10 L4,-6 M-3,-1 L0,-4 L3,-1" fill="none" stroke="%s" stroke-width=".7" opacity=".8"/>' % SERP_E
    s += '<ellipse cx="-5" cy="-15" rx="2" ry="2.3" fill="%s"/><ellipse cx="-4.8" cy="-15" rx=".6" ry="1.8" fill="#14050A"/>' % "#E3C24A"
    s += '<ellipse cx="5" cy="-15" rx="2" ry="2.3" fill="%s"/><ellipse cx="5.2" cy="-15" rx=".6" ry="1.8" fill="#14050A"/>' % "#E3C24A"
    s += '<path d="M0,-29 L0,-38 M0,-38 l-3,-4.5 M0,-38 l3,-4.5" stroke="#D0607F" stroke-width="1" fill="none" stroke-linecap="round"/>'
    return s + '</g>'


# ================================================================== asas de coruja caidas (atras do vestido)
def asa():
    """Asa esquerda (a direita sai espelhada): base, fileiras de penas e o bordo de ouro."""
    s = ['<path d="M178,520 C150,440 92,392 46,408 C32,420 36,460 42,540 L168,640 Z" fill="%s"/>' % VINHO]

    def pena(x, y, a, L, w, cor):
        s.append('<g transform="translate(%.1f %.1f) rotate(%.1f)"><path d="M0,0 C%.1f,%.1f %.1f,%.1f 0,%.1f C%.1f,%.1f %.1f,%.1f 0,0Z" fill="%s" stroke="%s" stroke-width=".9"/>'
                 '<path d="M0,%.1f L0,%.1f" stroke="%s" stroke-width=".55" opacity=".55"/></g>' % (x, y, a, -w, L * .2, -w, L * .8, L, w, L * .8, w, L * .2, cor, OURO, L * .1, L * .9, OURO))

    def fileira(n, x0, y0, x1, y1, L0, L1, a0, a1, w):
        for i in range(n):
            t = i / (n - 1)
            pena(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, a0 + (a1 - a0) * t, L0 + (L1 - L0) * t, w, ("#662A3A", VINHO)[i % 2])
    fileira(7, 168, 620, 60, 540, 300, 370, -4, 3, 13)
    fileira(6, 172, 560, 56, 472, 180, 146, -2, 8, 12.5)
    fileira(7, 176, 532, 50, 432, 92, 80, 0, 12, 10.5)
    fileira(7, 180, 518, 62, 414, 56, 50, 6, 18, 9)
    s.append('<path d="M180,520 C152,444 94,394 48,408 C36,414 34,430 40,444" fill="none" stroke="%s" stroke-width="1.4" stroke-linecap="round" filter="url(#mao)"/>' % OURO)
    return "".join(s)


# ================================================================== corujinhas
def coruja(x, y, k=1.0, olhar=(0, 0), vira=1):
    s = '<g transform="translate(%g %g) scale(%g %g)">' % (x, y, k * vira, k)
    corpo = "M-26,26 C-32,-4 -24,-30 0,-34 C24,-30 32,-4 26,26 C14,36 -14,36 -26,26Z"
    s += '<path d="%s" fill="%s"/>' % (corpo, VINHO)
    s += '<path d="M-17,10 C-17,26 -8,32 0,32 C8,32 17,26 17,10 C10,4 -10,4 -17,10Z" fill="#7A3446" opacity=".9"/>'
    s += '<g fill="none" stroke="%s" stroke-width="1.2" stroke-linecap="round" filter="url(#mao)">' % OURO
    s += '<path d="%s"/>' % corpo
    s += '<path d="M-20,-28 L-24,-42 L-10,-33 M20,-28 L24,-42 L10,-33"/>'
    s += '<path d="M-22,0 C-18,12 -16,20 -14,28 M22,0 C18,12 16,20 14,28" stroke-width=".9"/>'
    s += '<path d="M-6,10 q3,3 6,0 q3,3 6,0 M-9,17 q3,3 6,0 q3,3 6,0 q3,3 6,0" stroke-width=".8"/>'
    s += '<path d="M-6,32 v6 M6,32 v6" stroke-width="1.4"/></g>'
    for ex in (-10, 10):
        s += '<circle cx="%g" cy="-14" r="9" fill="%s" stroke="%s" stroke-width="1.2"/>' % (ex, CREME, OURO)
        s += '<circle cx="%g" cy="%g" r="5.4" fill="#E3B04B"/>' % (ex + olhar[0] * .5, -14 + olhar[1] * .5)
        s += '<circle cx="%g" cy="%g" r="3.1" fill="#14050A"/><circle cx="%g" cy="%g" r="1.1" fill="#FFF"/>' % (ex + olhar[0], -14 + olhar[1], ex + olhar[0] + 1.3, -15.4 + olhar[1])
    s += '<path d="M0,-8 L-3,-3 L0,0 L3,-3Z" fill="%s"/>' % OURO
    return s + '</g>'


# ================================================================== a gata
CAB = ("M-88,-4 C-90,-50 -54,-82 0,-82 C54,-82 90,-50 88,-4 C88,14 98,30 90,40 C78,58 44,72 0,74 "
       "C-44,72 -78,58 -90,40 C-98,30 -88,14 -88,-4 Z")
OR_E = "M-86,-30 C-92,-72 -90,-118 -78,-148 C-75,-153 -70,-152 -66,-148 C-50,-124 -36,-100 -22,-78 Z"
DE_E = "M-76,-46 C-80,-78 -78,-112 -72,-134 C-60,-116 -48,-96 -38,-82 Z"
FOC = "M-36,16 C-36,0 -16,-6 0,2 C16,-6 36,0 36,16 C36,42 18,58 0,58 C-18,58 -36,42 -36,16 Z"
MANCHA = "M-7,-76 L7,-76 L19,-4 L-19,-4 Z"
VESTIDO = ("M204,452 C180,460 152,474 140,500 C128,536 124,600 128,660 C132,720 126,800 116,900 C106,1000 94,1100 86,1186 "
           "C170,1204 330,1204 414,1186 C406,1100 394,1000 384,900 C374,800 368,720 372,660 C376,600 372,536 360,500 "
           "C348,474 320,460 296,452 L250,540 Z")
MANGA_E = ("M154,488 C132,522 124,592 128,646 C132,684 168,708 214,716 L222,678 C196,668 178,646 172,604 "
           "C168,574 170,530 186,500 Z")


def espelho(g):
    return affinity.scale(g, -1, 1, origin=(0, 0))


def olho(x, y, lado, olhar):
    """Olho amendoado de Bastet: iris verde do mascote, pupila em fenda, palpebra pesada e delineado."""
    ix, iy = x - lado * 22, y + 4
    ox, oy = x + lado * 25, y - 5
    topo = "M%g,%g C%g,%g %g,%g %g,%g" % (ix, iy, ix + lado * 9, y - 16, ox - lado * 12, y - 19, ox, oy)
    base = " C%g,%g %g,%g %g,%gZ" % (ox - lado * 9, y + 12, ix + lado * 10, y + 14, ix, iy)
    uid = "ol%d" % (lado + 1)
    s = '<clipPath id="%s"><path d="%s%s"/></clipPath>' % (uid, topo, base)
    s += '<path d="%s%s" fill="#F4EFD8"/>' % (topo, base)
    s += '<g clip-path="url(#%s)">' % uid
    px, py = x + olhar[0], y + 1 + olhar[1]
    s += '<circle cx="%g" cy="%g" r="15" fill="url(#irisG)"/>' % (px, py)
    s += '<ellipse cx="%g" cy="%g" rx="3.4" ry="12" fill="%s"/>' % (px + .5, py, TINTA)
    s += '<circle cx="%g" cy="%g" r="2.6" fill="#FFFDF6"/>' % (px + 4.5, py - 4)
    # palpebra superior pesada (meio fechado): pelo preto cobrindo o alto do olho
    s += '<path d="%s C%g,%g %g,%g %g,%gZ" fill="%s"/>' % (topo, ox - lado * 14, y - 8, ix + lado * 10, y - 6, ix, iy, PRETO["base"])
    s += '</g>'
    s += '<path d="%s" fill="none" stroke="%s" stroke-width="4.2" stroke-linecap="round"/>' % (topo, TINTA)
    s += '<path d="M%g,%g C%g,%g %g,%g %g,%g" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round" opacity=".9"/>' % (ox, oy, ox - lado * 9, y + 12, ix + lado * 10, y + 14, ix, iy, TINTA)
    # rabinho do delineado, para fora
    s += '<path d="M%g,%g C%g,%g %g,%g %g,%g" fill="none" stroke="%s" stroke-width="3.4" stroke-linecap="round"/>' % (ox - lado * 2, oy + 1, ox + lado * 5, oy - 2, ox + lado * 10, oy - 6, ox + lado * 14, oy - 10, TINTA)
    return s


def rosto_lilith(olhar=(4, 1)):
    s = olho(-36, -8, -1, olhar) + olho(36, -8, 1, olhar)
    s += '<path d="M-9,17 L9,17 C9,22 3,26 0,27 C-3,26 -9,22 -9,17Z" fill="#E58A98" stroke="%s" stroke-width="1.6" stroke-linejoin="round"/>' % TINTA
    s += '<path d="M0,27 L0,33 M-11,37 C-6,40 -2,39 0,33 C2,39 6,40 11,37" fill="none" stroke="%s" stroke-width="2.2" stroke-linecap="round"/>' % TINTA
    s += ('<path d="M-40,26 L-122,10 M-42,34 L-126,36 M-40,42 L-116,60 M40,26 L122,10 M42,34 L126,36 M40,42 L116,60" fill="none" '
          'stroke="#FFFDF6" stroke-width="1.4" stroke-linecap="round" opacity=".85"/>')
    return s


def crescente(x, y, k=1.0):
    d = "M-14,-6 A14,14 0 1 0 6,-16 A11,11 0 1 1 -14,-6Z"
    return ('<g transform="translate(%g %g) rotate(-14) scale(%g)">' % (x, y, k) +
            '<path d="%s" fill="#FFF3C6" opacity=".7" filter="url(#brilhoP)"/>' % d +
            '<path d="%s" fill="#B8893A" stroke="%s" stroke-width="%g" stroke-linejoin="round"/>' % (d, VINHO2, 1.6 / k) +
            '<path d="M-10,-2 A10,10 0 0 0 2,10" fill="none" stroke="#F3D88E" stroke-width="%g" stroke-linecap="round" opacity=".8"/>' % (1.4 / k) + '</g>')


def cabeca(p, x, y, esc=1.0, rot=0, olhar=(4, 1)):
    sub = Pose("91", "", "", "", centro=(0, 0))
    sub.seed = 9100
    cab = amostrar(CAB).buffer(2)
    oe, de = amostrar(OR_E), amostrar(DE_E)
    od, dd = espelho(oe), espelho(de)
    brancos = unary_union([amostrar(FOC).buffer(4), amostrar(MANCHA)])
    for o, d_, lado in ((oe, de, -1), (od, dd, 1)):
        sub.peca(o, lambda a, b, l=lado: (l * .25, -1), tufo=dict(passo=6))
        sub.svg('<path d="%s" fill="%s"/>' % (caminho(d_), ORELHA))
        sub.svg(desenha(pelo(d_, 40, lambda a, b, l=lado: (l * .25, -1), lambda a, b, r: "#FFF6F0", L=(6, 11), larg=(1, 1.4), seed=sub.seed + lado)))
    sub.peca(cab, lambda a, b: (a, b + 26), brancos=brancos, dens=.042, L=(7, 13), tufo=dict(L=(9, 16), mistura=.45))
    sub.svg(rosto_lilith(olhar))
    p.svg('<g transform="translate(%g %g) rotate(%g) scale(%g)">%s</g>' % (x, y, rot, esc, "".join(sub.camadas)))


def gata():
    """Tudo o que fica dentro da janela da carta, de tras para a frente."""
    p = Pose("90", "Lilith-gata de vestido", "", "", centro=(CX, 330))
    p.seed = 9000
    s = []
    # asas
    s.append('<g id="asaE">%s</g><use href="#asaE" transform="translate(500 0) scale(-1 1)"/>' % asa())
    p.svg("".join(s))
    # rabo saindo de baixo do vestido (atras da barra)
    # pezinhos sob a barra
    for xp in (226, 274):
        p.pata(xp, 1206, 24, 12)
    # pescoco e colo (o peito branco aparece no decote)
    colo = Polygon([(198, 404), (302, 404), (314, 452), (342, 500), (158, 500), (186, 452)]).buffer(6)
    bib = Polygon([(218, 426), (282, 426), (250, 532)]).buffer(6)
    p.peca(colo, lambda a, b: ((a - CX) / 160, 1), brancos=bib)
    # vestido: papel escuro + ceu de pontinhos + costuras de ouro
    tex = b64(papel(500, 1300, "#4A1B27", 77, forca=1.5, fibras=2.2))
    vest = ('<clipPath id="vestC"><path d="%s"/></clipPath><g clip-path="url(#vestC)">' % VESTIDO +
            '<image href="%s" x="0" y="0" width="500" height="1300" preserveAspectRatio="none"/>' % tex +
            '<rect width="500" height="1300" fill="url(#ceu)"/>'
            '<rect width="500" height="1300" fill="url(#sombraVest)"/></g>')
    vest += ('<g fill="none" stroke="%s" stroke-linecap="round" filter="url(#mao)">' % OURO +
             '<path d="M204,452 C180,460 152,474 140,500 C128,536 124,600 128,660 C132,720 126,800 116,900 C106,1000 94,1100 86,1186" stroke-width="1.2"/>'
             '<path d="M296,452 C320,460 348,474 360,500 C372,536 376,600 372,660 C368,720 374,800 384,900 C394,1000 406,1100 414,1186" stroke-width="1.2"/>'
             '<path d="M86,1186 C170,1204 330,1204 414,1186 M93,1158 C170,1176 330,1176 407,1158" stroke-width="1.1"/>'
             '<path d="M204,452 L250,540 L296,452 M192,458 L250,560 L308,458" stroke-width="1.2"/>'
             '<path d="M226,740 C218,880 206,1040 196,1196 M274,740 C282,880 296,1040 306,1196" stroke-width=".7" opacity=".55"/></g>')
    # barra: fileira de luazinhas e pontos entre as duas linhas de ouro
    for i in range(13):
        t = (i + .5) / 13
        xb = 92 + (408 - 92) * t
        yb = 1172 + 14 * math.sin(math.pi * t)
        vest += ('<circle cx="%.1f" cy="%.1f" r="2.4" fill="%s"/>' % (xb, yb, OURO) if i % 2 else
                 '<path transform="translate(%.1f %.1f) rotate(-14) scale(.42)" d="M-14,-6 A14,14 0 1 0 6,-16 A11,11 0 1 1 -14,-6Z" fill="%s"/>' % (xb, yb, OURO))
    p.svg(vest)
    p.pe = dict(PRETO, borda="#8C6578", claro="#6E5A68")  # luz de borda discreta: preto puro sumia no vinho
    G.rabo(p, [(300, 1200), (342, 1212), (380, 1202), (396, 1172), (386, 1142)], 14, 11)
    p.pe = PRETO
    # mangas e patas segurando a cintura
    me = amostrar(MANGA_E)
    md = affinity.translate(espelho(me), 500, 0)
    tex_m = b64(papel(260, 260, "#6E2C42", 78, forca=1.5, fibras=2.2))
    for uid, m in (("mE", me), ("mD", md)):
        p.svg('<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)"><image href="%s" x="%g" y="%g" width="260" height="260" preserveAspectRatio="none"/>'
              '<rect x="0" y="0" width="500" height="1300" fill="url(#ceu)"/></g>' % (uid, caminho(m), uid, tex_m, m.bounds[0] - 10, m.bounds[1] - 10) +
              '<path d="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-linejoin="round" filter="url(#mao)"/>' % (caminho(m), OURO))
    p.svg('<path d="M214,716 L222,678 M286,716 L278,678 M202,714 L211,674 M298,714 L289,674" stroke="%s" stroke-width="2.6" stroke-linecap="round"/>' % OURO)
    p.pata(272, 698, 17, 25, 90)
    p.pata(228, 700, 17, 25, -90)
    # serpente: tres voltas na frente do vestido; a ponta do rabo enrola para fora
    serp = (tubo("M352,470 C362,494 374,520 370,548 C358,606 224,646 130,636", 10, 16) +
            tubo("M376,722 C330,806 200,846 118,826", 17, 16) +
            tubo("M390,906 C350,986 200,1026 106,1006", 15, 12) +
            tubo("M108,1006 C88,1016 76,1036 78,1058 C80,1074 92,1082 102,1078", 12, 1.6))
    p.svg('<g filter="url(#mao)">%s</g>' % serp)
    # cabeca, lua na testa e a cabeca da serpente sussurrando junto do rosto
    cabeca(p, CX, 352, 1.1, 3, olhar=(5, 1))
    p.svg(crescente(CX + 4, 230, 1.55))
    p.svg(cabeca_serpente(350, 470, -20, 1.55))
    # tres corujinhas no chao
    p.svg(coruja(66, 1180, 1.0, (2, -1)) + coruja(126, 1196, .7, (3, -2)) + coruja(446, 1180, 1.0, (-2, -1), -1))
    p.svg('<path d="M24,1222 C120,1212 200,1220 250,1218 C320,1216 400,1212 476,1222" fill="none" stroke="%s" stroke-width="1.6" filter="url(#mao)"/>' % OURO)
    return "".join(p.camadas)


# ================================================================== a carta (janela em arco)
def carta():
    tex = b64(papel(500, 1300, "#3D1820", 76, forca=1.8, fibras=2.4))
    raios = ""
    for a in range(0, 360, 6):
        t = math.radians(a)
        l = 232 if a % 18 == 0 else 206
        raios += "M%.1f,%.1f L%.1f,%.1f " % (math.cos(t) * 188, math.sin(t) * 188, math.cos(t) * l, math.sin(t) * l)
    estrelas = "".join('<use href="#br" transform="translate(%g %g) scale(%g)"/>' % e for e in
                       ((70, 170, .8), (436, 160, .65), (110, 92, .42), (400, 86, .42), (452, 1080, .5), (40, 1100, .45), (470, 300, .4), (30, 330, .45)))
    s = '<path d="M0,1300 V250 A250,250 0 0 1 500,250 V1300 Z" fill="%s"/>' % VINHO2
    s += '<g clip-path="url(#janela)">'
    s += '<image href="%s" x="0" y="0" width="500" height="1300" preserveAspectRatio="none"/>' % tex
    s += '<rect width="500" height="1300" fill="url(#noite)"/><rect width="500" height="1300" fill="url(#ceu)"/>'
    s += '<g transform="translate(250 336)"><circle r="260" fill="url(#halo)"/>'
    s += '<path d="%s" stroke="%s" stroke-width=".8" opacity=".6"/>' % (raios, OURO)
    s += '<circle r="158" fill="url(#luaG)"/><circle r="158" fill="url(#luaG)" filter="url(#aguada)" opacity=".5"/>'
    s += "".join('<circle cx="%g" cy="%g" r="%g" fill="#D9BE84" opacity=".28"/>' % c for c in ((-92, -70, 22), (84, -96, 12), (106, 40, 18), (-110, 54, 11), (-40, 112, 14)))
    s += '<g fill="none" stroke="%s"><circle r="158" stroke-width="1.4"/><circle r="168" stroke-width=".7" opacity=".8"/><circle r="178" stroke-width=".9" stroke-dasharray="1.5 6" opacity=".8"/></g></g>' % OURO
    s += '<g fill="%s">%s</g><g fill="%s"><use href="#br" transform="translate(250 48) scale(.7)"/></g>' % (OURO, estrelas, CREME)
    s += gata()
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
<linearGradient id="noite" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#47202B" stop-opacity=".55"/><stop offset=".45" stop-color="#3D1820" stop-opacity=".35"/><stop offset="1" stop-color="#1E070C" stop-opacity=".75"/></linearGradient>
<linearGradient id="sombraVest" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity=".35"/><stop offset=".35" stop-color="#000" stop-opacity="0"/><stop offset=".7" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".4"/></linearGradient>
<radialGradient id="halo" r=".5"><stop offset=".55" stop-color="#C19E5A" stop-opacity=".26"/><stop offset="1" stop-color="#C19E5A" stop-opacity="0"/></radialGradient>
<radialGradient id="luaG" cx="42%" cy="38%" r="68%"><stop offset="0" stop-color="#FBF1D6"/><stop offset=".65" stop-color="#F0DDAE"/><stop offset="1" stop-color="#DDBF80"/></radialGradient>
<radialGradient id="irisG" cx="45%" cy="35%" r="70%"><stop offset="0" stop-color="#EEF3A8"/><stop offset=".55" stop-color="#C9D86A"/><stop offset="1" stop-color="#7E9A3C"/></radialGradient>
<pattern id="ceu" width="46" height="52" patternUnits="userSpaceOnUse"><circle cx="8" cy="10" r="1" fill="#C19E5A" opacity=".55"/><circle cx="31" cy="36" r=".8" fill="#EDDFC2" opacity=".45"/></pattern>
<clipPath id="janela"><path d="M19,1300 V250 A231,231 0 0 1 481,250 V1300 Z"/></clipPath>
<path id="br" d="M0,-10 Q0,0 10,0 Q0,0 0,10 Q0,0 -10,0 Q0,0 0,-10Z"/>
'''


# ================================================================== a pagina
CSS = '''
:root{--papel:#ECDFC5;--vinho:#5C2230;--vinho2:#3D1820;--ouro:#C19E5A;--salvia:#6B7E55;--tinta:#2A1418}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1350px;background:var(--papel)}
.peca{position:relative;width:1080px;height:1350px;overflow:hidden;color:var(--vinho2);background:var(--papel) var(--fundo) 0 0/1080px 1350px no-repeat}
.peca::before,.peca::after{content:"";position:absolute;inset:0;pointer-events:none;background-size:1080px 1440px;z-index:50}
.peca::before{background-image:var(--grao-neg);mix-blend-mode:multiply;opacity:.7}
.peca::after{background-image:var(--grao-pos);mix-blend-mode:plus-lighter;opacity:.5}
.peca>*{position:absolute}
svg{overflow:visible}
.carta{left:56px;top:56px;width:500px;height:1300px;filter:drop-shadow(0 22px 34px rgba(42,13,20,.35))}
.col{left:604px;width:430px;top:70px;bottom:62px;display:flex;flex-direction:column;justify-content:space-between;align-items:flex-start}
.grupo{display:flex;flex-direction:column;align-items:flex-start}
.marca{display:flex;flex-direction:column;align-items:flex-start}
.marca .sobre{font-family:'Cinzel';font-weight:700;font-size:24px;letter-spacing:.14em;color:var(--vinho);white-space:nowrap}
.linha{display:flex;align-items:center;gap:16px;margin-top:8px}
.marca .nome{position:relative;padding:5px 2px 8px;font-family:'Cormorant';font-style:italic;font-weight:500;font-size:54px;line-height:1;color:var(--vinho2)}
.marca .nome::before,.marca .nome::after{content:"";position:absolute;left:-6px;right:-14px;height:1px;background:linear-gradient(90deg,var(--vinho2) 0%,var(--vinho2) 82%,transparent);opacity:.7}
.marca .nome::before{top:0}.marca .nome::after{bottom:0}
.vezes{font-family:'Cormorant';font-weight:300;font-size:40px;color:var(--vinho)}
.logo{width:96px;height:96px;background:var(--logo-tulipa) center/contain no-repeat}
.tema{font-family:'Cinzel';font-weight:700;font-size:16px;letter-spacing:.42em;color:var(--salvia)}
.lilith{margin-top:4px;margin-left:-8px;font-family:'Italiana';font-size:184px;line-height:.92;color:var(--vinho);letter-spacing:-.01em}
.sub{margin-top:18px;font-family:'Cormorant';font-style:italic;font-weight:500;font-size:37px;line-height:1.12;color:var(--vinho2)}
.desc{margin-top:18px;font-family:'Cormorant';font-weight:500;font-size:26px;line-height:1.25;color:rgba(61,24,32,.85);max-width:420px}
.fio{margin:0 0 22px;display:flex;align-items:center;gap:14px;color:var(--ouro)}
.fio i{display:block;width:120px;height:1px;background:currentColor}
.livre{font-family:'Cormorant';font-weight:600;font-size:48px;line-height:1.05;color:var(--vinho2)}
.marcada{position:relative;display:inline-block;padding:0 4px;margin-left:12px}
.marcada .gi{position:absolute;left:-8%;top:-26%;width:118%;height:152%;background:var(--salvia);opacity:.9;
  -webkit-mask:var(--G-circulo) center/100% 100% no-repeat;mask:var(--G-circulo) center/100% 100% no-repeat}
.info{margin-top:28px;font-family:'Cinzel';font-weight:700;font-size:24px;letter-spacing:.06em;line-height:1.6;color:var(--vinho2)}
.info span{color:var(--ouro)}
.parceria{font-family:'Cormorant';font-style:italic;font-weight:500;font-size:24px;line-height:1.25;color:var(--vinho2)}
.cta{margin-top:16px;font-family:'Cinzel';font-weight:700;font-size:18px;letter-spacing:.16em;color:var(--salvia)}
.cta2{margin-top:2px;font-family:'Cormorant';font-style:italic;font-weight:600;font-size:25px;color:var(--vinho2)}
'''

COLUNA = '''
<div class="col">
  <div class="marca">
    <div class="sobre">Clube de literatura</div>
    <div class="linha"><div class="nome">Entrelinhas</div><div class="vezes">×</div><div class="logo"></div></div>
  </div>
  <div class="grupo">
    <div class="tema">Tema do encontro</div>
    <div class="lilith">Lilith</div>
    <div class="sub">A primeira mulher,<br>a que não se curvou</div>
    <div class="desc">Uma conversa sobre o mito e o que ele<br>ainda diz sobre desejo, recusa e sombra</div>
  </div>
  <div class="grupo">
    <div class="fio"><i></i><svg width="14" height="14" viewBox="-10 -10 20 20"><path d="M0,-10 Q0,0 10,0 Q0,0 0,10 Q0,0 -10,0 Q0,0 0,-10Z" fill="currentColor"/></svg><i></i></div>
    <div class="livre">Aberto e <span class="marcada">gratuito<i class="gi"></i></span></div>
    <div class="info">Quintas, das 13h às 14h15<br>a cada 15 dias<br>Sala 713 <span>·</span> bloco B <span>·</span> UNICAP</div>
  </div>
  <div class="rodape">
    <div class="parceria">Em parceria com a TULIPA, extensão<br>em psicologia analítica da UNICAP</div>
    <div class="cta">Inscreva-se pelo link abaixo ↓</div>
    <div class="cta2">e entre no grupo do WhatsApp do clube</div>
  </div>
</div>
'''


def aneis_fundo():
    """Aneis da lua saindo da carta para o papel (elemento grande e transparente da arte 02)."""
    r = ""
    for a in range(0, 360, 5):
        t = math.radians(a)
        l = 520 if a % 15 == 0 else 496
        r += "M%.1f,%.1f L%.1f,%.1f " % (math.cos(t) * 476, math.sin(t) * 476, math.cos(t) * l, math.sin(t) * l)
    return ('<svg style="left:0;top:0" width="1080" height="1350" viewBox="0 0 1080 1350"><g fill="none" stroke="#5C2230" transform="translate(306 376)">'
            '<circle r="452" stroke-width="1.1" opacity=".16"/><circle r="466" stroke-width=".6" opacity=".12"/>'
            '<circle r="560" stroke-width="1" stroke-dasharray="2 10" opacity=".16"/><path d="%s" stroke-width="1" opacity=".1"/></g></svg>') % r


def peca():
    fundo = b64(papel(1080, 1350, "#ECDFC5", 75, forca=1.3, fibras=2.0, pintas=.8, borda=.10, relevo=.22))
    return ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Entrelinhas · Lilith (v5, a gata no arco)</title>\n<!--ACERVO-->\n'
            '<style>%s .peca{--fundo:url(%s)}</style></head><body><div class="peca">%s'
            '<svg class="carta" viewBox="0 0 500 1300"><defs>%s</defs>%s</svg>%s</div></body></html>') % (
        CSS, fundo, aneis_fundo(), DEFS_CARTA, carta(), COLUNA)


def exportar(nome, html, arquivo_final, so_local=False):
    from playwright.sync_api import sync_playwright
    html = html.replace("<!--ACERVO-->", montar.ACERVO_CSS)
    arq = os.path.join(AQUI, "saida", nome + ".final.html")
    open(arq, "w", encoding="utf-8").write(html)
    destinos = [(1, os.path.join(AQUI, "saida", nome + ".png")), (2, os.path.join(AQUI, "saida", nome + "@2x.png"))]
    if not so_local:
        destinos += [(1, os.path.join(D, arquivo_final)), (2, os.path.join(D, "alta resolução (2160x2700)", arquivo_final))]
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for esc, destino in destinos:
            pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=esc)
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(1500)
            pg.screenshot(path=destino)
        b.close()


def cabeca_bastet():
    p = Pose("92", "", "", "", centro=(0, 0))
    cabeca(p, 0, 0, 1.1, 3, olhar=(5, 1))
    p.svg(crescente(4, -122, 1.55))
    return "".join(p.camadas)


def asas_par():
    return '<g id="asaE">%s</g><use href="#asaE" transform="translate(500 0) scale(-1 1)"/>' % asa()


# figuras deste post que valem para o banco (mini leitura: relevante e reusavel). Ficou FORA a serpente sozinha:
# as voltas so leem enroladas num corpo; solta, vira quatro pedacos de tubo.
ITENS_BANCO = [
    ("57", "lilith_de_vestido", "Lilith de vestido", (20, 176, 460, 1060), gata,
     "De pé, gigante, num vestido longo de noite com mangas e patas brancas na cintura; rosto de Bastet (olhos amendoados "
     "meio fechados, delineado, sem bochecha rosada: a versão «menos fofa»), lua crescente entre as orelhas, asas de coruja "
     "caídas, serpente enrolada no vestido e três corujinhas no chão. Feita para o post de Lilith (post_lilith5.py), que ele "
     "ADOROU; serve para mito, sombra, temas noturnos e qualquer arte em arco de tarô."),
    ("58", "carta_de_lilith_em_arco", "Carta de Lilith em arco", (0, 0, 500, 1300), carta,
     "A carta inteira, sem o texto: arco vinho com moldura dupla de ouro, céu de pontinhos, lua clara com raios atrás da "
     "cabeça e a Lilith de vestido (57) com as corujinhas. Para stories, capa de destaque, ou para pôr outro texto ao lado no Canva."),
    ("59", "rosto_de_bastet", "Rosto de Bastet", (-160, -192, 320, 300), cabeca_bastet,
     "Só a cabeça da versão «menos fofa»: olhos amendoados meio fechados, pupila em fenda, delineado de Bastet, sem bochecha "
     "rosada, com a lua crescente entre as orelhas. Para mito, mistério, ironia, «leitura de sombra», avatar sério do clube."),
    ("60", "corujinha_de_ouro", "Corujinha de ouro", (-38, -48, 76, 92), lambda: coruja(0, 0, 1.0, (2, -1)),
     "Corujinha no traço de ouro da arte 02 (corpo vinho, olhos creme e âmbar). Enfeite noturno: sabedoria, Lilith, leitura "
     "de madrugada; fica bem em par ou trio no pé de uma moldura."),
    ("61", "asas_de_coruja", "Asas de coruja caídas", (20, 384, 460, 616), asas_par,
     "Par de asas de coruja caídas (Relevo de Burney), penas vinho com contorno de ouro. Vai ATRÁS de qualquer figura "
     "(gato, pessoa, livro) para dar ar de ícone; foi usado atrás da 57."),
]


def svg_autonomo(vb, corpo):
    """SVG que abre sozinho (Canva, Inkscape): defs da carta embutidas e xlink:href nas imagens e nos <use>."""
    x, y, w, h = vb
    s = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="%g %g %g %g" width="%g" height="%g">'
         '<defs>%s</defs>%s</svg>') % (x, y, w, h, w, h, DEFS_CARTA, corpo)
    return s.replace(' href="', ' xlink:href="')


def para_o_banco(cods=None):
    """Figuras 57-61 no banco de poses: SVG autonomo + PNG transparente (lado maior >= 900 px)."""
    import json
    from playwright.sync_api import sync_playwright
    banco = os.path.join(AQUI, "mascote", "banco")
    meta = json.load(open(os.path.join(banco, "banco.json"), encoding="utf-8"))
    arq = os.path.join(AQUI, "saida", "_banco_tmp.html")
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for cod, slug, nome, vb, f, nota in ITENS_BANCO:
            if cods and cod not in cods:
                continue
            base = "%s_%s" % (cod, slug)
            svg = svg_autonomo(vb, f())
            open(os.path.join(banco, base + ".svg"), "w", encoding="utf-8").write(svg)
            open(arq, "w", encoding="utf-8").write('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:transparent}svg{display:block}</style></head><body>%s</body></html>' % svg)
            k = max(2.0, 900 / max(vb[2], vb[3]))
            pg = b.new_page(viewport={"width": int(vb[2]), "height": int(vb[3])}, device_scale_factor=k)
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(800)
            pg.screenshot(path=os.path.join(banco, base + ".png"), omit_background=True)
            pg.close()
            meta = [m for m in meta if m["cod"] != cod] + [dict(cod=cod, nome=nome, grupo="Figuras de post", nota=nota, arquivo=base)]
            print("banco:", base)
        b.close()
    os.remove(arq)
    meta.sort(key=lambda m: m["cod"])
    json.dump(meta, open(os.path.join(banco, "banco.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    final = "--final" in sys.argv
    exportar("post_lilith5", peca(), "Lilith × TULIPA - post v5 (a gata no arco).png", so_local=not final)
    if final:
        para_o_banco()
    print("ok")
