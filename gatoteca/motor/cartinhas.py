# -*- coding: utf-8 -*-
"""IDENTIDADE «CARTINHAS» do Entrelinhas: componentes em SVG + pecas de exemplo.

Gramatica tirada da referencia dos cartoes (cartao-postal sobre veludo): cartao com moldura dupla
de cantos recortados, emblema central num anel de perolas com raios finos, ceu de estrelas de 8
pontas, titulo de serifa gorda com contorno, verso de postal com coracoes de perola e guirlandas,
forro de losangos arlequim. O emblema e NOSSO: o olho de gato (iris do mascote, pupila em fenda).

uso: py cartinhas.py [capa verso envelope componentes]
"""
import os, sys, math, random, base64, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[2]  # raiz do repositório

AQUI = os.path.dirname(os.path.abspath(__file__))
BANCO = os.path.join(AQUI, "mascote", "banco")
ELEM = str(_REPO / 'gatoteca/artes/Elementos recortados')

# ---------------------------------------------------------------- paleta (medida na referencia + ouro e vinho dos lacres)
JADE, JADE_E = "#5F857C", "#3F665E"
ROSA, ROSA_C = "#C799AA", "#E6C4D0"
NOITE, AMEIXA = "#30323C", "#624956"
PEROLA, OURO, VINHO = "#F1E3E6", "#D9B36A", "#6E1F2E"
IRIS = "#C9D86A"
VELUDO = "#141116"


def b64png(caminho):
    return "data:image/png;base64," + base64.b64encode(open(caminho, "rb").read()).decode()


def gato(cod):
    return glob.glob(os.path.join(BANCO, cod + "_*.png"))[0]


def elem(cat, slug):
    return os.path.join(ELEM, cat, slug + ".png")


def imagem(caminho, x, y, w=None, h=None, rot=0, extra=""):
    from PIL import Image
    im = Image.open(caminho)
    if w and not h:
        h = w * im.height / im.width
    if h and not w:
        w = h * im.width / im.height
    return '<image href="%s" x="%g" y="%g" width="%g" height="%g" transform="rotate(%g %g %g)" %s/>' % (
        b64png(caminho), x - w / 2, y - h / 2, w, h, rot, x, y, extra)


# ================================================================== componentes
def moldura(w, h, cor, r=26, i=20, i2=30, larg=(2.2, 1.1)):
    """Moldura dupla com cantos recortados para dentro (a marca do cartao-postal)."""
    def caminho(k, rr):
        return ("M%g,%g H%g A%g,%g 0 0 0 %g,%g V%g A%g,%g 0 0 0 %g,%g H%g A%g,%g 0 0 0 %g,%g V%g A%g,%g 0 0 0 %g,%gZ" % (
            k + rr, k, w - k - rr, rr, rr, w - k, k + rr, h - k - rr, rr, rr, w - k - rr, h - k, k + rr, rr, rr, k, h - k - rr, k + rr, rr, rr, k + rr, k))
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%g"/><path d="%s" fill="none" stroke="%s" stroke-width="%g" opacity=".8"/>'
            % (caminho(i, r), cor, larg[0], caminho(i2, r - 6), cor, larg[1]))


def cartao(cx, cy, w, h, cor, rot=0, linha=AMEIXA, conteudo="", sombra=True):
    s = '<g transform="translate(%g %g) rotate(%g) translate(%g %g)">' % (cx, cy, rot, -w / 2, -h / 2)
    if sombra:
        s += '<rect x="6" y="16" width="%g" height="%g" rx="8" fill="#000" opacity=".55" filter="url(#sombraCarta)"/>' % (w, h)
    s += '<rect width="%g" height="%g" rx="8" fill="%s"/>' % (w, h, cor)
    s += '<rect width="%g" height="%g" rx="8" fill="url(#luzCarta)"/>' % (w, h)
    uid = "cc%d" % abs(int(cx * 13 + cy * 7 + w))
    s += '<clipPath id="%s"><rect width="%g" height="%g" rx="8"/></clipPath><g clip-path="url(#%s)">%s</g>' % (uid, w, h, uid, conteudo)
    s += moldura(w, h, linha)
    return s + '</g>'


def raios(cx, cy, r0, r1, cor, n=28, op=.55, larg=1.4, seed=1):
    random.seed(seed)
    s = []
    for k in range(n):
        a = 2 * math.pi * k / n + random.uniform(-.04, .04)
        rr = r1 * random.uniform(.55, 1.0)
        s.append("M%.1f,%.1f L%.1f,%.1f" % (cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return '<path d="%s" stroke="%s" stroke-width="%g" stroke-linecap="round" opacity="%g"/>' % (" ".join(s), cor, larg, op)


def estrela8(cx, cy, r, fill=ROSA, stroke=AMEIXA, w=1.6, rot=0):
    pts = []
    for k in range(16):
        a = math.radians(rot + k * 22.5 - 90)
        rr = r if k % 4 == 0 else (r * .62 if k % 2 == 0 else r * .2)
        pts.append("%.1f,%.1f" % (cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return '<path d="M%sZ" fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round"/>' % (" L".join(pts), fill, stroke, w)


def estrela5(cx, cy, r, fill=NOITE, rot=0):
    pts = []
    for k in range(10):
        a = math.radians(rot + k * 36 - 90)
        rr = r if k % 2 == 0 else r * .42
        pts.append("%.1f,%.1f" % (cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return '<path d="M%sZ" fill="%s"/>' % (" L".join(pts), fill)


def ceu(x0, y0, x1, y1, n=40, seed=3, rosa=ROSA, escura=NOITE, livre=None):
    """Campo de estrelas da referencia: poucas grandes de 8 pontas, muitas pequenas escuras."""
    random.seed(seed)
    s = []
    tent = 0
    while len(s) < n and tent < n * 30:
        tent += 1
        x, y = random.uniform(x0, x1), random.uniform(y0, y1)
        if livre and livre(x, y):
            continue
        t = random.random()
        if t < .18:
            s.append(estrela8(x, y, random.uniform(13, 22), rosa, AMEIXA, 1.6, random.uniform(-10, 10)))
        elif t < .75:
            s.append(estrela5(x, y, random.uniform(5, 10), escura, random.uniform(0, 72)))
        else:
            s.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (x, y, random.uniform(1.4, 2.6), escura))
    return "".join(s)


def perola(x, y, r):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#F4E6E8" stroke="%s" stroke-width="1.5"/>'
            '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1" opacity=".55"/>'
            '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#FFFFFF"/>') % (x, y, r, AMEIXA, x + r * .08, y + r * .08, r * .55, AMEIXA, x - r * .35, y - r * .38, r * .22)


def anel_perolas(cx, cy, rx, ry, r=15):
    per = math.pi * (3 * (rx + ry) - math.sqrt((3 * rx + ry) * (rx + 3 * ry)))
    n = int(per / (2 * r * 1.02))
    s = '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="none" stroke="%s" stroke-width="%g"/>' % (cx, cy, rx, ry, OURO, r * 1.2)
    # amostra o contorno por comprimento de arco
    pts, acc, prev = [], [], None
    for k in range(2000):
        t = 2 * math.pi * k / 2000
        p = (cx + rx * math.cos(t), cy + ry * math.sin(t))
        acc.append(0 if prev is None else acc[-1] + math.dist(p, prev))
        pts.append(p)
        prev = p
    total = acc[-1]
    j = 0
    for i in range(n):
        alvo = total * i / n
        while acc[j] < alvo:
            j += 1
        s += perola(pts[j][0], pts[j][1], r)
    return s


def olho_gato(cx, cy, w, iris=IRIS, pele=ROSA_C, cilios=True, rot=0, mono=None):
    """O emblema: olho de gato amendoado, iris verde do mascote, pupila em fenda."""
    h = w * .52
    olho = "M-1,0 C-.55,-.78 .55,-.78 1,0 C.55,.78 -.55,.78 -1,0Z"
    pal = "M-1.18,0 C-.62,-1.08 .62,-1.08 1.18,0 C.62,1.0 -.62,1.0 -1.18,0Z"
    s = '<g transform="translate(%g %g) rotate(%g) scale(%g %g)">' % (cx, cy, rot, w / 2, h / 2 / .78 * .78)
    s += '<path d="%s" fill="%s" stroke="%s" stroke-width="%g"/>' % (pal, pele, AMEIXA, 4 / w)
    s += '<path d="M-1.05,-.1 C-.6,-.86 .6,-.86 1.05,-.1" fill="none" stroke="%s" stroke-width="%g" opacity=".7"/>' % (AMEIXA, 2.4 / w)
    s += '<clipPath id="olho%d"><path d="%s"/></clipPath>' % (int(cx * 7 + cy), olho)
    s += '<g clip-path="url(#olho%d)"><rect x="-1.1" y="-1" width="2.2" height="2" fill="#FBF6EC"/>' % int(cx * 7 + cy)
    s += '<circle cx="0" cy="0" r=".74" fill="%s" stroke="%s" stroke-width="%g"/>' % (mono or "url(#iris)", AMEIXA, 3 / w)
    s += '<ellipse cx="0" cy="0" rx=".13" ry=".66" fill="#14100F"/>'
    s += '<circle cx=".28" cy="-.32" r=".13" fill="#FFFFFF"/><circle cx="-.25" cy=".3" r=".06" fill="#FFFFFF"/></g>'
    s += '<path d="%s" fill="none" stroke="%s" stroke-width="%g"/>' % (olho, AMEIXA, 5 / w)
    if cilios:
        for k in range(9):
            t = -.8 + k * .2
            x0, y0 = t, -.78 * (1 - t * t) * 1.0 - .04
            s += '<path d="M%.3f,%.3f L%.3f,%.3f" stroke="%s" stroke-width="%g" stroke-linecap="round"/>' % (x0 * 1.05, y0 - .05, x0 * 1.25, y0 - .32, AMEIXA, 2.6 / w)
    return s + '</g>'


CORACAO = "M0,.95 C-.6,.5 -1.05,.05 -1.0,-.38 C-.95,-.82 -.42,-.98 0,-.55 C.42,-.98 .95,-.82 1.0,-.38 C1.05,.05 .6,.5 0,.95Z"


def coracao_perolas(cx, cy, s_, rot=0, cor="#8A5068"):
    g = '<g transform="translate(%g %g) rotate(%g)">' % (cx, cy, rot)
    g += '<path d="%s" transform="scale(%g)" fill="%s" stroke="%s" stroke-width="%g"/>' % (CORACAO, s_, cor, AMEIXA, 3 / s_)
    # perolas no contorno
    pts = []
    for k in range(400):
        t = k / 400
        pts.append(t)
    import re
    nums = [float(v) for v in re.findall(r"-?\d*\.?\d+", CORACAO)]
    # amostra pela curva: usa a forma parametrica aproximada do coracao
    for k in range(26):
        t = 2 * math.pi * k / 26
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        g += perola(x / 17 * s_ * 1.04, y / 17 * s_ * 1.04 - s_ * .1, s_ * .085)
    g += olho_gato(0, -s_ * .08, s_ * 1.1, cilios=False)
    return g + '</g>'


def gema(cx, cy, s_, cor=ROSA, rot=0):
    d = "M-1,-.3 L-.55,-.75 L.55,-.75 L1,-.3 L0,1Z"
    g = '<g transform="translate(%g %g) rotate(%g) scale(%g)">' % (cx, cy, rot, s_)
    g += '<path d="%s" fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round"/>' % (d, cor, AMEIXA, 2 / s_)
    g += '<path d="M-1,-.3 L1,-.3 M-.55,-.75 L-.3,-.3 L0,1 L.3,-.3 L.55,-.75 M-.3,-.3 L0,-.75 L.3,-.3" fill="none" stroke="%s" stroke-width="%g" opacity=".75"/>' % (AMEIXA, 1.2 / s_)
    g += '<path d="M-.7,-.4 L-.45,-.62" stroke="#FFFFFF" stroke-width="%g" stroke-linecap="round"/>' % (2.4 / s_)
    return g + '</g>'


def guirlanda(x0, y0, x1, y1, n=4):
    s = '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="1.2" stroke-dasharray="2 4"/>' % (x0, y0, x1, y1, AMEIXA)
    for k in range(n):
        t = (k + .5) / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        s += gema(x, y, 13, ROSA if k % 2 == 0 else JADE, math.degrees(math.atan2(y1 - y0, x1 - x0)) - 90)
        s += perola(x + (x1 - x0) / n * .5, y + (y1 - y0) / n * .5, 4.2) if k < n - 1 else ""
    return s


def livro_icone(cx, cy, s_):
    return ('<g transform="translate(%g %g) scale(%g)" stroke="%s" stroke-width="%g" stroke-linejoin="round">'
            '<path d="M0,-.55 C-.35,-.75 -.75,-.75 -1,-.6 L-1,.55 C-.75,.4 -.35,.4 0,.6Z" fill="#FBF6EC"/>'
            '<path d="M0,-.55 C.35,-.75 .75,-.75 1,-.6 L1,.55 C.75,.4 .35,.4 0,.6Z" fill="#FBF6EC"/>'
            '<path d="M-.8,-.3 C-.55,-.42 -.3,-.42 -.15,-.34 M-.8,-.05 C-.55,-.17 -.3,-.17 -.15,-.09 M.15,-.34 C.3,-.42 .55,-.42 .8,-.3 M.15,-.09 C.3,-.17 .55,-.17 .8,-.05" fill="none" stroke-width="%g" opacity=".6"/></g>'
            ) % (cx, cy, s_, AMEIXA, 2 / s_, 1.2 / s_)


def lua_icone(cx, cy, r, cor=PEROLA):
    return '<path d="M%g,%g a%g,%g 0 1 0 0,%g a%g,%g 0 0 1 0,%gZ" fill="%s" stroke="%s" stroke-width="1.8"/>' % (
        cx + r * .2, cy - r, r, r, 2 * r, r * 1.35, r * 1.35, -2 * r, cor, AMEIXA)


def arlequim(x0, y0, x1, y1, lado=120, uid="arl"):
    """Losangos rosa e jade com icones: olho de gato, estrela de 8 pontas, livro aberto, lua."""
    s = ['<clipPath id="%s"><rect x="%g" y="%g" width="%g" height="%g"/></clipPath><g clip-path="url(#%s)">' % (uid, x0, y0, x1 - x0, y1 - y0, uid)]
    s.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (x0, y0, x1 - x0, y1 - y0, JADE))
    hx, hy = lado * .5, lado * .62
    linha = 0
    y = y0 - hy
    k = 0
    while y < y1 + hy:
        x = x0 - hx + (hx if linha % 2 else 0)
        while x < x1 + hx:
            cor = ROSA if (linha % 2 == 0) else JADE
            if (linha % 2 == 0):
                s.append('<path d="M%g,%g L%g,%g L%g,%g L%g,%gZ" fill="%s" stroke="%s" stroke-width="1"/>' % (x, y - hy, x + hx, y, x, y + hy, x - hx, y, ROSA, JADE_E))
            ic = k % 4
            if ic == 0:
                s.append(olho_gato(x, y, hx * .95, cilios=False))
            elif ic == 1:
                s.append(estrela8(x, y, hx * .42, ROSA if linha % 2 else NOITE, AMEIXA, 1.2))
            elif ic == 2:
                s.append(livro_icone(x, y, hx * .38))
            else:
                s.append(lua_icone(x, y, hx * .3))
            k += 1
            x += lado
        y += hy
        linha += 1
    s.append('</g>')
    return "".join(s)


def carimbo(cx, cy, r=78, rot=-12, topo="RECIFE · JAQUEIRA", dia="31 OUT", ano="2026", cor=AMEIXA):
    uid = "car%d" % int(cx + cy)
    s = '<g transform="translate(%g %g) rotate(%g)" opacity=".86" filter="url(#tinta)">' % (cx, cy, rot)
    s += '<circle r="%g" fill="none" stroke="%s" stroke-width="3"/><circle r="%g" fill="none" stroke="%s" stroke-width="1.6"/>' % (r, cor, r * .64, cor)
    s += '<path id="%s" d="M%g,0 A%g,%g 0 1 1 %g,0" fill="none"/>' % (uid, -r * .8, r * .8, r * .8, r * .8)
    s += '<text font-family="Cinzel" font-weight="700" font-size="%g" letter-spacing="1" fill="%s"><textPath href="#%s" startOffset="50%%" text-anchor="middle">%s</textPath></text>' % (r * .145, cor, uid, topo)
    s += '<text y="%g" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="%g" fill="%s">%s</text>' % (r * .12, r * .3, cor, dia)
    s += '<text y="%g" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="%g" fill="%s">%s</text>' % (r * .42, r * .17, cor, ano)
    for k in range(5):
        y = -r * .5 + k * r * .25
        s += '<path d="M%g,%g q22,-10 44,0 t44,0 t44,0 t44,0" fill="none" stroke="%s" stroke-width="2.6"/>' % (r * 1.08, y, cor)
    return s + '</g>'


def selo_postal(cx, cy, w, h, conteudo, valor="R$ 30", rot=6, fundo=JADE):
    uid = "sp%d" % int(cx + cy)
    s = '<g transform="translate(%g %g) rotate(%g)">' % (cx, cy, rot)
    m = '<mask id="%s"><rect x="%g" y="%g" width="%g" height="%g" fill="#fff"/>' % (uid, -w / 2, -h / 2, w, h)
    passo = 13
    for x in range(int(-w / 2), int(w / 2) + 1, passo):
        m += '<circle cx="%g" cy="%g" r="4.6" fill="#000"/><circle cx="%g" cy="%g" r="4.6" fill="#000"/>' % (x, -h / 2, x, h / 2)
    for y in range(int(-h / 2), int(h / 2) + 1, passo):
        m += '<circle cx="%g" cy="%g" r="4.6" fill="#000"/><circle cx="%g" cy="%g" r="4.6" fill="#000"/>' % (-w / 2, y, w / 2, y)
    s += m + '</mask>'
    s += '<g mask="url(#%s)"><rect x="%g" y="%g" width="%g" height="%g" fill="#FBF3E8"/>' % (uid, -w / 2, -h / 2, w, h)
    s += '<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (-w / 2 + 12, -h / 2 + 12, w - 24, h - 24, fundo)
    s += raios(0, -h * .05, 0, w * .7, ROSA_C, 22, .4, 1.1)
    s += conteudo
    s += '<text x="%g" y="%g" font-family="DM Serif Display" font-size="24" fill="%s" stroke="%s" stroke-width="3" paint-order="stroke">%s</text>' % (
        -w / 2 + 18, h / 2 - 20, ROSA_C, AMEIXA, valor)
    s += '<text x="%g" y="%g" text-anchor="end" font-family="Cinzel" font-weight="700" font-size="10" letter-spacing="1.5" fill="%s">ENTRELINHAS</text>' % (w / 2 - 18, -h / 2 + 28, PEROLA)
    return s + '</g></g>'


def titulo(x, y, txt, tam, fill=ROSA_C, stroke=AMEIXA, sw=None, rot=0, anchor="middle", fonte="DM Serif Display", ls=0):
    sw = sw or tam * .075
    return ('<text x="%g" y="%g" transform="rotate(%g %g %g)" text-anchor="%s" font-family="%s" font-size="%g" letter-spacing="%g" '
            'fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round" paint-order="stroke">%s</text>') % (x, y, rot, x, y, anchor, fonte, tam, ls, fill, stroke, sw, txt)


DEFS = '''
<filter id="sombraCarta" x="-10%" y="-10%" width="120%" height="130%"><feGaussianBlur stdDeviation="14"/></filter>
<filter id="tinta" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="1" seed="3" result="n"/>
 <feColorMatrix in="n" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -3 2.1" result="m"/><feComposite in="SourceGraphic" in2="m" operator="in"/></filter>
<filter id="brilho" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="16"/></filter>
<filter id="veludo" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".75" numOctaves="2" seed="8"/>
 <feColorMatrix type="matrix" values="0 0 0 0 .5 0 0 0 0 .45 0 0 0 0 .5 0 0 0 .22 0"/></filter>
<linearGradient id="luzCarta" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".12"/></linearGradient>
<radialGradient id="iris" cx="45%" cy="40%" r="65%"><stop offset="0" stop-color="#EEF3A8"/><stop offset=".55" stop-color="#C9D86A"/><stop offset="1" stop-color="#7E9A3C"/></radialGradient>
<radialGradient id="mesa" cx="50%" cy="45%" r="75%"><stop offset="0" stop-color="#26202A"/><stop offset="1" stop-color="#0E0C10"/></radialGradient>
'''


def pagina(nome, corpo, w=1080, h=1350):
    css = ('*{margin:0;padding:0}html,body{width:%dpx;height:%dpx;background:%s}.peca{position:relative;width:%dpx;height:%dpx;overflow:hidden}'
           '.peca::after{content:"";position:absolute;inset:0;pointer-events:none;background-image:var(--grao-pos);background-size:1080px 1440px;mix-blend-mode:plus-lighter;opacity:.35}'
           '.peca>svg{position:absolute;left:0;top:0}') % (w, h, VELUDO, w, h)
    return ('<!doctype html><html><head><meta charset="utf-8"><title>%s</title>\n<!--ACERVO-->\n<style>%s</style></head><body><div class="peca">'
            '<svg width="%d" height="%d" viewBox="0 0 %d %d"><defs>%s</defs>%s</svg></div></body></html>') % (nome, css, w, h, w, h, DEFS, corpo)


def mesa(w=1080, h=1350):
    return '<rect width="%d" height="%d" fill="url(#mesa)"/><rect width="%d" height="%d" filter="url(#veludo)"/>' % (w, h, w, h)


# ================================================================== PECAS DE EXEMPLO
def capa():
    """Capa: tres peças sobre o veludo (envelope arlequim, verso rosa, frente jade com o emblema)."""
    env = cartao(430, 330, 760, 500, JADE, -9, AMEIXA, arlequim(0, 0, 760, 500, 118, "arlCapa") + moldura(760, 500, AMEIXA))
    verso_c = ('<text x="70" y="104" font-family="DM Serif Display" font-size="50" fill="%s">Cartão-postal</text>' % JADE_E +
               estrela8(46, 88, 13, JADE, AMEIXA) + estrela8(372, 78, 11, JADE, AMEIXA) +
               '<g opacity=".14">' + olho_gato(350, 300, 360, iris=AMEIXA, pele=AMEIXA, cilios=True) + '</g>' +
               coracao_perolas(612, 112, 56, 8) + guirlanda(612, 160, 650, 330, 4) +
               coracao_perolas(96, 380, 52, -8) + guirlanda(110, 330, 70, 180, 3))
    verso = cartao(650, 470, 700, 460, ROSA, 7, AMEIXA, verso_c)
    # frente jade com o emblema: anel de perolas e o mascote dentro
    W, H = 880, 620
    cx, cy = W / 2, H / 2 + 26
    livre = lambda x, y: ((x - cx) / 250) ** 2 + ((y - cy) / 205) ** 2 < 1
    frente_c = (raios(cx, cy, 200, 420, ROSA_C, 30, .5, 1.5, 4) + ceu(40, 40, W - 40, H - 40, 46, 6, ROSA, NOITE, livre) +
                '<ellipse cx="%g" cy="%g" rx="182" ry="150" fill="%s"/>' % (cx, cy, ROSA_C) +
                raios(cx, cy, 0, 150, "#FFFFFF", 26, .35, 1.2, 9) +
                anel_perolas(cx, cy, 196, 164, 16) +
                imagem(gato("28"), cx, cy + 8, h=300) +
                titulo(W - 250, 112, "Entrelinhas", 70, ROSA_C, AMEIXA, 5.5, -8) +
                '<text x="%g" y="%g" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="17" letter-spacing="7" fill="%s" transform="rotate(-2 %g %g)">CLUBE DO LIVRO · EDIÇÃO DE HALLOWEEN</text>' % (
                    cx, H - 50, PEROLA, cx, H - 50))
    frente = cartao(536, 840, W, H, JADE, -5, AMEIXA, frente_c)
    rodape = ('<text x="540" y="1238" text-anchor="middle" font-family="Cormorant" font-style="italic" font-weight="600" font-size="38" fill="%s">Piquenique literário no Parque da Jaqueira</text>' % PEROLA +
              '<text x="540" y="1290" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="17" letter-spacing="6" fill="%s">SÁB, 31 DE OUTUBRO · ABRA A CARTA →</text>' % OURO)
    lacre = imagem(elem("1 Lacres e selos", "lacre_vinho_lua"), 118, 560, 140, rot=-12)
    return pagina("Cartinhas · capa", mesa() + env + verso + frente + lacre + rodape)


def verso():
    """O convite: verso do postal, com a mensagem a mao e as informacoes nas linhas."""
    W, H = 960, 1230
    lin = AMEIXA
    linhas = ""
    info = [("QUANDO", "Sábado, 31 de outubro, às 15h"), ("ONDE", "Parque da Jaqueira, Recife"), ("QUANTO", "R$ 30 · só 20 vagas"),
            ("INCLUI", "ecobag, marcador, café, bolo e frutinhas"), ("", "e um livro sorteado entre os leitores")]
    y0 = 760
    for k, (rot_, txt) in enumerate(info):
        y = y0 + k * 80
        linhas += '<path d="M90,%g L870,%g" stroke="%s" stroke-width="1.4" opacity=".55"/>' % (y, y, lin)
        if rot_:
            linhas += '<text x="92" y="%g" font-family="Cinzel" font-weight="700" font-size="15" letter-spacing="4" fill="%s">%s</text>' % (y - 46, JADE_E, rot_)
        linhas += '<text x="250" y="%g" font-family="Caveat" font-weight="600" font-size="44" fill="%s">%s</text>' % (y - 12, AMEIXA, txt)
    mensagem = ('<text font-family="Caveat" font-weight="600" font-size="48" fill="%s">' % AMEIXA +
                '<tspan x="92" y="420">Querido leitor, querida leitora,</tspan>'
                '<tspan x="92" y="480">no fim de outubro a gente vai ler</tspan>'
                '<tspan x="92" y="540">debaixo da jaqueira, com café, bolo</tspan>'
                '<tspan x="92" y="600">e histórias de arrepiar. Vem?</tspan>'
                '<tspan x="868" y="668" text-anchor="end">Com carinho, Entrelinhas</tspan></text>')
    conteudo = ('<g opacity=".07">' + olho_gato(W / 2, 640, 640, pele=AMEIXA, mono=AMEIXA) + '</g>' +
                '<text x="88" y="190" font-family="DM Serif Display" font-size="96" fill="%s">Cartão-postal</text>' % JADE_E +
                estrela8(130, 248, 16, JADE, AMEIXA) + estrela8(430, 236, 12, JADE, AMEIXA) + estrela8(560, 120, 10, JADE, AMEIXA) +
                '<path d="M90,300 L620,300" stroke="%s" stroke-width="1.6" opacity=".55"/>' % lin +
                mensagem + linhas +
                selo_postal(800, 205, 190, 236, imagem(gato("28"), 0, 6, h=170), "R$ 30", 6) +
                carimbo(622, 296, 70, -14) +
                coracao_perolas(112, 1150, 58, -8) + guirlanda(160, 1130, 330, 1185, 3) +
                coracao_perolas(848, 1150, 58, 8) + guirlanda(800, 1130, 630, 1185, 3))
    corpo = mesa() + cartao(540, 675, W, H, ROSA, -2, AMEIXA, conteudo)
    corpo += imagem(elem("1 Lacres e selos", "lacre_vinho_lua"), 540, 1238, 170, rot=-8)
    corpo += imagem(elem("2 Astros", "estrela_dourada_8_longa"), 120, 80, 90, rot=8)
    return pagina("Cartinhas · verso", corpo)


def envelope():
    """Chamada final: envelope aberto com o forro arlequim, cartinha saindo e o mascote espiando."""
    W, H = 900, 560
    ex, ey = 540, 900
    x0, y0 = ex - W / 2, ey - H / 2
    corpo = mesa()
    corpo += imagem(elem("6 Luz e mistério", "lanterna_pendurada_1"), 170, 150, 120)
    corpo += '<path d="M170,0 L170,70" stroke="#8A7A5A" stroke-width="2"/>'
    corpo += imagem(elem("6 Luz e mistério", "lanterna_pendurada_2"), 930, 210, 110)
    corpo += '<path d="M930,0 L930,140" stroke="#8A7A5A" stroke-width="2"/>'
    corpo += ceu(40, 40, 1040, 560, 34, 11, ROSA, "#5B4E5E", lambda x, y: 280 < x < 800 and y > 200)
    # aba aberta (forro arlequim) atras
    aba = "M%g,%g L%g,%g L%g,%g Z" % (x0, y0, ex, y0 - 330, x0 + W, y0)
    corpo += '<path d="%s" fill="%s" stroke="%s" stroke-width="2.4"/>' % (aba, JADE_E, AMEIXA)
    corpo += '<clipPath id="forro"><path d="M%g,%g L%g,%g L%g,%g Z"/></clipPath><g clip-path="url(#forro)">%s</g>' % (
        x0 + 30, y0, ex, y0 - 296, x0 + W - 30, y0, arlequim(x0, y0 - 330, x0 + W, y0, 104, "arlEnv"))
    # cartinha saindo
    c = cartao(540, 520, 700, 560, PEROLA, -3, AMEIXA,
               ceu(40, 40, 660, 520, 24, 5, ROSA, AMEIXA, lambda x, y: 70 < x < 630 and 90 < y < 330) +
               titulo(350, 190, "Garanta", 96, ROSA, AMEIXA, 6) + titulo(350, 290, "sua vaga", 96, ROSA, AMEIXA, 6) +
               '<text x="350" y="360" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="20" letter-spacing="5" fill="%s">SÓ 20 LEITORES</text>' % JADE_E, sombra=True)
    corpo += c
    # bolso do envelope (frente) com as dobras
    bolso = "M%g,%g L%g,%g L%g,%g L%g,%g L%g,%g Z" % (x0, y0, ex, y0 + 250, x0 + W, y0, x0 + W, y0 + H, x0, y0 + H)
    corpo += '<path d="%s" fill="%s" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (bolso, JADE, AMEIXA)
    corpo += '<path d="M%g,%g L%g,%g L%g,%g" fill="none" stroke="%s" stroke-width="1.6" opacity=".6"/>' % (x0, y0 + H, ex, y0 + 300, x0 + W, y0 + H, AMEIXA)
    corpo += '<path d="%s" fill="url(#luzCarta)"/>' % bolso
    corpo += moldura_parcial(x0, y0, W, H)
    corpo += '<text x="540" y="%g" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="20" letter-spacing="6" fill="%s">COMUNIDADE NO WHATSAPP</text>' % (y0 + H - 92, PEROLA)
    corpo += '<text x="540" y="%g" text-anchor="middle" font-family="Cormorant" font-style="italic" font-weight="600" font-size="34" fill="%s">link na bio · clube do livro Entrelinhas</text>' % (y0 + H - 46, PEROLA)
    # o mascote espiando pela borda do bolso
    corpo += espiando(760, 232, 300, -3)
    corpo += imagem(elem("1 Lacres e selos", "lacre_vinho_lua"), ex, y0 + 252, 130)
    return pagina("Cartinhas · envelope", corpo)


def espiando(x_borda, y_borda, w, rot):
    """Pose 19 com a linha de baixo dela encostada na borda (x_borda, y_borda)."""
    import numpy as np
    from PIL import Image
    im = Image.open(gato("19"))
    a = np.asarray(im)[..., 3]
    ys = np.where(a.max(axis=1) > 40)[0]
    base = ys.max() - 6
    h = w * im.height / im.width
    k = w / im.width
    cy = y_borda - (base * k - h / 2)
    return '<g transform="rotate(%g %g %g)">%s</g>' % (rot, x_borda, y_borda, imagem(gato("19"), x_borda, cy, w))


def moldura_parcial(x0, y0, W, H):
    return '<path d="M%g,%g L%g,%g L%g,%g L%g,%g" fill="none" stroke="%s" stroke-width="1.4" opacity=".8"/>' % (
        x0 + 20, y0 + 40, x0 + 20, y0 + H - 20, x0 + W - 20, y0 + H - 20, x0 + W - 20, y0 + 40, AMEIXA)


def componentes():
    """Prancha dos componentes, para o guia."""
    W, H = 1600, 900
    s = '<rect width="%d" height="%d" fill="%s"/>' % (W, H, PEROLA)
    s += cartao(230, 230, 380, 260, JADE, 0, AMEIXA, raios(190, 130, 40, 230, ROSA_C, 24, .5, 1.3) + ceu(30, 30, 350, 230, 18, 2, ROSA, NOITE), sombra=False)
    s += '<g transform="translate(560 230)">' + anel_perolas(0, 0, 120, 100, 13) + olho_gato(0, 0, 170) + '</g>'
    s += coracao_perolas(840, 230, 80, -6) + guirlanda(900, 300, 960, 420, 3)
    s += selo_postal(1090, 230, 170, 210, imagem(gato("01"), 0, 4, h=150), "R$ 30", 4)
    s += carimbo(1380, 240, 80, -10)
    s += cartao(270, 640, 440, 300, JADE, 0, AMEIXA, arlequim(0, 0, 440, 300, 104, "arlComp"), sombra=False)
    s += "".join(estrela8(560 + k * 70, 560, 22 - k * 2, ROSA, AMEIXA) for k in range(4))
    s += "".join(estrela5(560 + k * 50, 640, 9, NOITE, k * 12) for k in range(5))
    s += "".join(gema(580 + k * 60, 720, 20, ROSA if k % 2 else JADE) for k in range(4))
    s += titulo(1100, 620, "Entrelinhas", 96, ROSA_C, AMEIXA, 7)
    s += '<text x="1100" y="690" text-anchor="middle" font-family="Caveat" font-weight="600" font-size="46" fill="%s">escrito à mão nas linhas do postal</text>' % AMEIXA
    s += '<text x="1100" y="745" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="20" letter-spacing="7" fill="%s">RÓTULOS EM CAIXA ALTA ESPAÇADA</text>' % JADE_E
    for k, (n, c) in enumerate((("jade", JADE), ("jade escuro", JADE_E), ("rosa-postal", ROSA), ("rosa claro", ROSA_C), ("noite", NOITE),
                                ("ameixa", AMEIXA), ("pérola", PEROLA), ("ouro", OURO), ("vinho-lacre", VINHO), ("veludo", VELUDO))):
        x = 60 + k * 152
        s += '<rect x="%d" y="800" width="130" height="60" rx="6" fill="%s" stroke="%s" stroke-width="1.4"/>' % (x, c, AMEIXA)
        s += '<text x="%d" y="884" font-family="Cormorant" font-weight="700" font-size="17" fill="%s">%s %s</text>' % (x, AMEIXA, n, c)
    return pagina("Cartinhas · componentes", s, W, H)


PECAS = {"capa": capa, "verso": verso, "envelope": envelope, "componentes": componentes}

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    qual = sys.argv[1:] or list(PECAS)
    saida = os.path.join(AQUI, "saida")
    with sync_playwright() as p:
        b = p.chromium.launch()
        for k in qual:
            html = PECAS[k]().replace("<!--ACERVO-->", montar.ACERVO_CSS)
            w, h = (1600, 900) if k == "componentes" else (1080, 1350)
            pg = b.new_page(viewport={"width": w, "height": h})
            arq = os.path.join(saida, "cartinha_%s.final.html" % k)
            open(arq, "w", encoding="utf-8").write(html)
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(1200)
            pg.screenshot(path=os.path.join(saida, "cartinha_%s.png" % k))
            print(k)
        b.close()
