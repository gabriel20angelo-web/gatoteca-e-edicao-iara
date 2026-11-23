# -*- coding: utf-8 -*-
"""FOTO DE PERFIL DO WHATSAPP da Gatoteca Entrelinhas: «Entre 🐈 linhas» (plano de 13/11/2026, peça 2).

Um livro aberto grande, de frente e um pouco de cima. Na página da esquerda está impresso «Entre», na da
direita «linhas», e o frajola está sentado NA DOBRA, entre as duas palavras, com as patinhas nas páginas
e o rabo descendo pela dobra até sair pela borda de baixo do livro. «GATOTECA» em arco no alto.
Quadrado 1080 x 1080; tudo o que importa cabe no círculo do WhatsApp (figura até 510 px do centro,
texto até ~470 px).

Variantes:  jade -> fundo jade (recomendado), capa ameixa
            rosa -> fundo rosa, capa jade
uso: py divulga_perfil.py [jade rosa]   -> saida/perfil_entre_<var>.png + saida/perfil_entre_previa.png
     py divulga_perfil.py --zoom        -> também recortes em 2x (rosto, patinhas, palavras)
     py divulga_perfil.py --final       -> copia para a pasta do plano (a figura no banco, cód. 62, ainda não foi feita)
"""
import os, sys, math, random, shutil
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "mascote"))
import montar
from papel import papel
import gato_banco as G
from gato_banco import Pose, sentado, rabo
import divulga_post as DP
from divulga_post import com_papel, b64, estrela8, clarear
import perfil_whatsapp as PW
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union

DESTINO = DP.DESTINO
SAIDA = os.path.join(AQUI, "saida")
W = 1080
C = W / 2
JADE, JADE_E, ROSA, ROSA_C, NOITE, AMEIXA, PEROLA, OURO, VINHO = (DP.JADE, DP.JADE_E, DP.ROSA, DP.ROSA_C, DP.NOITE,
                                                                  DP.AMEIXA, DP.PEROLA, DP.OURO, DP.VINHO)
CONTORNO = DP.CONTORNO
PAGINA = DP.PAGINA
TINTA_TXT = "#2B2A33"

VARIANTES = {
    "jade": dict(fundo=JADE, borda=JADE_E, capa=AMEIXA, estrela=ROSA, titulo=PEROLA, titulo_borda="#24403A", halo="#FFEFD6"),
    "rosa": dict(fundo=ROSA, borda="#9E6F82", capa=JADE, estrela=PEROLA, titulo="#4A2C3B", titulo_borda=PEROLA, halo="#FFF3EA"),
}

# ------------------------------------------------------------------ geometria (px da foto)
GATO_S = 1.12          # escala do gato
GATO_Y = 662           # chão do gato (base dos pés) na dobra
CAB_ESC = 1.10         # cabeça um pouco maior que a do banco: lê a 49 px
HW = 432               # meia-largura do livro (cada página)
TOPO_G, TOPO_O = 574, 524        # borda de cima da página: na dobra e na ponta de fora
BASE_G, BASE_O = 868, 808        # borda de baixo: na dobra e na ponta de fora
TXT_V = .80           # onde ficam as palavras entre a borda de cima (0) e a de baixo (1)
TXT_TAM = 116
ARCO_R = 410
TXT_VAO = 92           # as palavras começam/terminam a esta distância da dobra (depois das patinhas)
PATA_Y = 9              # a pata passa da base do corpo e pisa na página
PATA_X = 46            # patinhas da frente, na frente das pernas do corpo


# ================================================================== o livro aberto
def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d for a, b, c, d in zip(p0, p1, p2, p3))


def borda(lado, v):
    """Curva horizontal da página (da dobra para fora) a uma altura v (0 = borda de cima, 1 = de baixo).
    As páginas sobem da dobra e se assentam para fora (a «gaivota» do livro aberto visto de cima)."""
    def cp(yg, yo, sobe):
        return [(C, yg), (C + lado * HW * .16, yg - sobe), (C + lado * HW * .55, yo - sobe * .55), (C + lado * HW, yo)]
    a = cp(TOPO_G, TOPO_O, 64)
    b = cp(BASE_G, BASE_O, 54)
    return [tuple(pa[i] + (pb[i] - pa[i]) * v for i in range(2)) for pa, pb in zip(a, b)]


def caminho_curva(pts, inverso=False):
    p = pts[::-1] if inverso else pts
    return "M%.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (p[0] + p[1] + p[2] + p[3])


def contorno_pagina(lado, n=40):
    cima = [bez(*borda(lado, 0), t=i / n) for i in range(n + 1)]
    baixo = [bez(*borda(lado, 1), t=i / n) for i in range(n + 1)]
    return cima + baixo[::-1]


def d_de(pts):
    return "M" + " L".join("%.1f,%.1f" % p for p in pts) + "Z"


def linhas_impressas(lado, seed):
    """As «linhas»: texto impresso como tracinhos, seguindo a curva da página; some onde está a palavra."""
    rnd = random.Random(seed)
    s = []
    vs = [.1, .19, .28, .37, .46, .55, .93]
    for k, v in enumerate(vs):
        pts = borda(lado, v)
        t0, t1 = .14, .9
        if k == len(vs) - 1 or k == 3:
            t1 = .9 - rnd.uniform(.15, .4) if lado < 0 else .9   # fim de parágrafo
        t = t0 + (rnd.uniform(0, .06) if k in (0, 4) else 0)
        while t < t1:
            L = rnd.uniform(.035, .11)
            a, b = bez(*pts, t=t), bez(*pts, t=min(t + L, t1))
            s.append("M%.1f,%.1f L%.1f,%.1f" % (a + b))
            t += L + .022
    return '<path d="%s" stroke="#8C7A80" stroke-width="5" stroke-linecap="round" opacity=".34"/>' % " ".join(s)


def livro(v):
    s = ""
    esq, dir_ = contorno_pagina(-1), contorno_pagina(1)
    folhas = unary_union([Polygon(esq).buffer(0), Polygon(dir_).buffer(0)])
    # capa de pano (aparece em volta e embaixo), com sombra no fundo
    capa = folhas.buffer(15, join_style=2)
    capa = unary_union([capa, Polygon([(C - HW - 6, BASE_O - 30), (C + HW + 6, BASE_O - 30), (C + HW + 10, BASE_O + 30), (C, BASE_G + 34), (C - HW - 10, BASE_O + 30)])])
    from shapely import affinity
    capa = affinity.translate(capa, 0, 16)
    dc = d_de(list(capa.exterior.coords))
    x0, y0, x1, y1 = capa.bounds
    s += '<path d="%s" fill="#0E1A17" opacity=".55" filter="url(#esfuma)" transform="translate(0 16)"/>' % dc
    s += com_papel(dc, v["capa"], 191, (x0, y0, x1, y1), forca=1.8, fibras=3, stroke=CONTORNO, sw=3.2,
                   extra='<rect x="%g" y="%g" width="%g" height="%g" fill="url(#capaLuz)"/>' % (x0, y0, x1 - x0, y1 - y0))
    # cantoneiras de ouro nas quatro pontas de fora da capa
    for lado in (-1, 1):
        for (yy, sy) in ((TOPO_O + 2, -1), (BASE_O + 30, 1)):
            cx = C + lado * (HW + 14)
            pts = [(cx, yy + sy * 22), (cx - lado * 54, yy + sy * 22), (cx, yy - sy * 34)]
            pts = [(cx + lado * 4, yy + sy * 24), (cx - lado * 50, yy + sy * 24), (cx + lado * 4, yy - sy * 30)]
            s += '<path d="M%g,%g L%g,%g L%g,%gZ" fill="%s" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (sum(pts, ()) + (OURO, CONTORNO))
            s += '<circle cx="%g" cy="%g" r="3.4" fill="%s"/>' % (cx - lado * 10, yy + sy * 14, CONTORNO)
    # o miolo: folhas empilhadas (a grossura do livro), mais abertas na base, em leque nas pontas
    for k in range(6, 0, -1):
        e = k * 3.2
        for lado, pts in ((-1, esq), (1, dir_)):
            sh = [(x + lado * e * .55 * ((abs(x - C) / HW) ** 2), y + e * (.35 + .65 * (y - TOPO_O) / (BASE_G - TOPO_O))) for x, y in pts]
            s += '<path d="%s" fill="%s" stroke="#A8968E" stroke-width="1.1"/>' % (d_de(sh), "#E4D5CB" if k % 2 else "#F2E8DF")
    # as duas páginas, papel creme, com sombra da dobra e luz de cima
    for lado, pts, seed in ((-1, esq, 193), (1, dir_, 194)):
        d = d_de(pts)
        bx = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
        grad = "dobraE" if lado < 0 else "dobraD"
        extra = linhas_impressas(lado, seed)
        extra += '<rect x="%g" y="%g" width="%g" height="%g" fill="url(#%s)"/>' % (bx[0], bx[1], bx[2] - bx[0], bx[3] - bx[1], grad)
        extra += '<rect x="%g" y="%g" width="%g" height="%g" fill="url(#paginaLuz)"/>' % (bx[0], bx[1], bx[2] - bx[0], bx[3] - bx[1])
        s += com_papel(d, PAGINA, seed, bx, forca=1.3, fibras=2.0, relevo=.2, extra=extra, stroke=CONTORNO, sw=3)
    # o vinco da dobra
    s += '<path d="M%g,%g C%g,%g %g,%g %g,%g" fill="none" stroke="%s" stroke-width="2.6" opacity=".7"/>' % (
        C, TOPO_G, C - 2, TOPO_G + 100, C - 2, BASE_G - 100, C, BASE_G, CONTORNO)
    return s, folhas


def fracao_em_x(pts, x_alvo, n=400):
    """Fração do comprimento da curva em que ela passa por x_alvo (para o startOffset do textPath)."""
    amos = [bez(*pts, t=i / n) for i in range(n + 1)]
    comp, tot = [0], 0
    for a, b in zip(amos, amos[1:]):
        tot += math.hypot(b[0] - a[0], b[1] - a[1])
        comp.append(tot)
    for (a, b), L in zip(zip(amos, amos[1:]), comp):
        if (a[0] - x_alvo) * (b[0] - x_alvo) <= 0:
            return L / tot
    return .5


def curva_texto(lado, achata=.45):
    """A linha de base das palavras: a curva da página, mas com a gaivota amaciada (letras menos tortas perto da dobra)."""
    pts = borda(lado, TXT_V)
    (x0, y0), (x3, y3) = pts[0], pts[3]
    reta = lambda x: y0 + (y3 - y0) * (x - x0) / (x3 - x0)
    return [(x, y + (reta(x) - y) * achata) for x, y in pts]


def palavras():
    """«Entre» na página da esquerda, «linhas» na da direita, em DM Serif Display, seguindo a curva da página."""
    s = ""
    for lado, txt, seed in ((-1, "Entre", 1), (1, "linhas", 2)):
        pts = curva_texto(lado)
        d = caminho_curva(pts, inverso=(lado < 0))
        i = "pal%d" % seed
        s += '<path id="%s" d="%s" fill="none"/>' % (i, d)
        # «Entre» termina antes da dobra e «linhas» começa depois dela: o vão do meio é do rabo
        alvo = C - TXT_VAO if lado < 0 else C + TXT_VAO
        off = "%.1f%%" % (100 * fracao_em_x(pts if lado > 0 else pts[::-1], alvo))
        ancora = "end" if lado < 0 else "start"
        s += ('<text font-family="DM Serif Display" font-size="%d" fill="%s" text-anchor="%s">'
              '<textPath href="#%s" startOffset="%s">%s</textPath></text>') % (TXT_TAM, TINTA_TXT, ancora, i, off, txt)
    return s


# ================================================================== o gato
def gato():
    p = Pose("62", "entre", "", "", centro=(0, -200))
    p.seed = 6200
    # o rabo: sai de trás do corpo, desce pela dobra e passa da borda de baixo do livro
    yb = (BASE_G - GATO_Y) / GATO_S
    rabo(p, [(40, -40), (14, 4), (2, 50), (-2, yb * .55), (-14, yb * .8), (4, yb + 36)], 20, 16)
    sentado(p, rabo_cima=False, patas=False,
            cabeca=dict(esc=CAB_ESC, acess=[]))
    # patinhas da frente apoiadas nas páginas, uma de cada lado da dobra, os dedinhos à mostra
    for lado in (-1, 1):
        cx, cy = lado * PATA_X, PATA_Y
        # a mão: palma e três dedinhos fundidos num contorno só (a borda de baixo fica em gomos), e dois vincos curtos
        mao = unary_union([G.elipse(cx, cy - 5, 22, 17)] + [G.elipse(cx + dx, cy + dy, r, r * .92) for dx, dy, r in ((-13, 8, 9.5), (0, 11, 10), (13, 8, 9.5))])
        mao = mao.buffer(1.5).buffer(-1)
        p.branco(mao, lambda x, y: (0, 1), L=(4, 7), tufo=dict(passo=9, L=(2, 3.5), w=1.3, mistura=.25))
        p.svg('<path d="%s" fill="none" stroke="#9C8F88" stroke-width="1.8" stroke-linejoin="round"/>' % G.caminho(mao))
        d = ""
        for k in (-6.6, 6.6):
            d += "M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f " % (cx + k, cy + 18, cx + k * 1.1, cy + 12, cx + k, cy + 6)
        p.svg('<path d="%s" stroke="#7D716B" stroke-width="2.3" stroke-linecap="round" fill="none"/>' % d)
    return p


def colocar(p):
    return '<g transform="translate(%g %g) scale(%g)">%s</g>' % (C, GATO_Y, GATO_S, "".join(p.camadas))


# ================================================================== a peça
DEFS = '''
<radialGradient id="fundoV" cx="50%" cy="44%" r="62%"><stop offset=".45" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#0B1412" stop-opacity=".5"/></radialGradient>
<radialGradient id="haloG" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="HALO" stop-opacity=".95"/><stop offset=".38" stop-color="HALO" stop-opacity=".55"/><stop offset=".7" stop-color="#F3D08E" stop-opacity=".16"/><stop offset="1" stop-color="#F3D08E" stop-opacity="0"/></radialGradient>
<linearGradient id="dobraE" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#5A3A44" stop-opacity=".5"/><stop offset=".12" stop-color="#5A3A44" stop-opacity=".12"/><stop offset=".3" stop-color="#5A3A44" stop-opacity="0"/><stop offset=".9" stop-color="#5A3A44" stop-opacity="0"/><stop offset="1" stop-color="#5A3A44" stop-opacity=".16"/></linearGradient>
<linearGradient id="dobraD" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5A3A44" stop-opacity=".5"/><stop offset=".12" stop-color="#5A3A44" stop-opacity=".12"/><stop offset=".3" stop-color="#5A3A44" stop-opacity="0"/><stop offset=".9" stop-color="#5A3A44" stop-opacity="0"/><stop offset="1" stop-color="#5A3A44" stop-opacity=".16"/></linearGradient>
<linearGradient id="paginaLuz" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF8EC" stop-opacity=".35"/><stop offset=".5" stop-color="#FFF8EC" stop-opacity="0"/><stop offset="1" stop-color="#5A3A44" stop-opacity=".12"/></linearGradient>
<linearGradient id="capaLuz" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".1"/><stop offset="1" stop-color="#000000" stop-opacity=".25"/></linearGradient>
<filter id="sombraPata" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="3.5"/></filter>
<filter id="sombraGato" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="8"/></filter>
'''


def arco_titulo(v):
    a = math.radians(64)
    x0, y0 = C - ARCO_R * math.sin(a), C - ARCO_R * math.cos(a)
    x1 = C + ARCO_R * math.sin(a)
    d = "M%.1f,%.1f A%d,%d 0 0 1 %.1f,%.1f" % (x0, y0, ARCO_R, ARCO_R, x1, y0)
    s = '<path id="arcoT" d="%s" fill="none"/>' % d
    estilo = 'font-family="Cinzel" font-weight="800" font-size="80" letter-spacing="12" text-anchor="middle"'
    s += '<text %s fill="#000" opacity=".35" filter="url(#borrao)" transform="translate(3 5)"><textPath href="#arcoT" startOffset="50%%">GATOTECA</textPath></text>' % estilo
    s += ('<text %s fill="%s" stroke="%s" stroke-width="6" paint-order="stroke" stroke-linejoin="round">'
          '<textPath href="#arcoT" startOffset="50%%">GATOTECA</textPath></text>') % (estilo, v["titulo"], v["titulo_borda"])
    # dois losangos de ouro nas pontas do arco
    for sx in (-1, 1):
        ang = math.radians(sx * 52)
        x, y = C + (ARCO_R + 26) * math.sin(ang), C - (ARCO_R + 26) * math.cos(ang)
        s += estrela8(x, y, 15, OURO)
    return s


def peca(var):
    v = VARIANTES[var]
    DP._uid[0] = 0
    p = gato()
    fundo = b64(papel(W, W, v["fundo"], 192, forca=1.6, fibras=2.2, pintas=.7, borda=.10, relevo=.24))
    liv, folhas = livro(v)
    cab_y = GATO_Y - 262 * GATO_S
    s = '<rect width="%d" height="%d" fill="url(#fundoV)"/>' % (W, W)
    # halo de luz pérola/ouro atrás da cabeça
    s += '<circle cx="%g" cy="%g" r="330" fill="url(#haloG)"/>' % (C, cab_y + 30)
    for x, y, r in ((C - 330, 300, 22), (C + 338, 360, 17), (C + 282, 236, 11), (C - 272, 420, 10)):
        s += estrela8(x, y, r, v["estrela"])
    s += arco_titulo(v)
    s += liv
    s += palavras()
    # sombra do gato na página
    s += '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="#3B2030" opacity=".38" filter="url(#sombraGato)"/>' % (C + 8, GATO_Y + 4, 150 * GATO_S, 18 * GATO_S)
    # sombra de contato embaixo de cada patinha: assenta a pata na página
    for lado in (-1, 1):
        s += '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="#2E1826" opacity=".62" filter="url(#sombraPata)"/>' % (
            C + lado * PATA_X * GATO_S + 3, GATO_Y + (PATA_Y + 19) * GATO_S, 26 * GATO_S, 5.5 * GATO_S)
    s += colocar(p)
    defs = G.DEFS_EXTRA + DEFS.replace("HALO", v["halo"])
    svg = '<svg class="arte" viewBox="0 0 %d %d" width="%d" height="%d"><defs>%s</defs>%s</svg>' % (W, W, W, W, defs, s)
    css = ('*{margin:0;padding:0;box-sizing:border-box}html,body{width:%dpx;height:%dpx;background:%s}'
           '.peca{position:relative;width:%dpx;height:%dpx;overflow:hidden;background:%s url(%s) 0 0/%dpx %dpx no-repeat}'
           '.peca::before,.peca::after{content:"";position:absolute;inset:0;pointer-events:none;background-size:%dpx %dpx;z-index:5}'
           '.peca::before{background-image:var(--grao-neg);mix-blend-mode:multiply;opacity:.5}'
           '.peca::after{background-image:var(--grao-pos);mix-blend-mode:plus-lighter;opacity:.4}'
           '.arte{position:absolute;left:0;top:0;overflow:hidden}') % (W, W, v["fundo"], W, W, v["fundo"], fundo, W, W, W, int(W * 4 / 3))
    html = ('<!doctype html><html><head><meta charset="utf-8"><title>Gatoteca · perfil Entre linhas (%s)</title>\n<!--ACERVO-->\n'
            '<style>%s</style></head><body><div class="peca">%s</div></body></html>') % (var, css, svg)
    return html, p, folhas


# ================================================================== conferir o círculo
def conferir(p, folhas):
    """Distância ao centro: gato e livro até 510 px; texto (arco e palavras) até ~470 px."""
    from shapely import affinity
    todos = unary_union([g for g in p.polis if g is not None and not g.is_empty] + [box(*c) for c in p.caixas])
    gato_px = affinity.translate(affinity.scale(todos, GATO_S, GATO_S, origin=(0, 0)), C, GATO_Y)
    dg = max(math.hypot(x - C, y - C) for x, y in gato_px.convex_hull.exterior.coords)
    dl = max(math.hypot(x - C, y - C) for x, y in folhas.exterior.coords)
    # palavras: caixa aproximada em volta do trecho da curva que elas ocupam
    dt = 0
    for lado, larg in ((-1, 293 * TXT_TAM / 120), (1, 321 * TXT_TAM / 120)):
        pts = curva_texto(lado)
        meio = .46 if lado < 0 else .46
        for t in (meio - larg / HW / 2.1, meio + larg / HW / 2.1):
            x, y = bez(*pts, t=max(0, min(1, t)))
            for yy in (y, y - TXT_TAM * .72):
                dt = max(dt, math.hypot(x - C, yy - C))
    dtit = ARCO_R + 76 * .72
    print("  gato ate %.0f px | paginas ate %.0f px (limite 510) | palavras ate ~%.0f, GATOTECA ate ~%.0f px (limite ~470)" % (dg, dl, dt, dtit))
    return dg, dl, dt


def exportar(vars_, escala=1, sufixo=""):
    from playwright.sync_api import sync_playwright
    saidas = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for var in vars_:
            html, p, folhas = peca(var)
            conferir(p, folhas)
            html = html.replace("<!--ACERVO-->", montar.ACERVO_CSS)
            arq = os.path.join(SAIDA, "perfil_entre_%s%s.final.html" % (var, sufixo))
            open(arq, "w", encoding="utf-8").write(html)
            pg = b.new_page(viewport={"width": W, "height": W}, device_scale_factor=escala)
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(1500)
            png = os.path.join(SAIDA, "perfil_entre_%s%s.png" % (var, sufixo))
            pg.screenshot(path=png)
            pg.close()
            saidas.append((var, png))
            print(png)
        b.close()
    return saidas


def zoom(png):
    from PIL import Image
    im = Image.open(png)
    k = im.width // W
    for nome, (a, b_, c, d) in dict(rosto=(380, 120, 700, 470), patas=(400, 580, 680, 740), palavras=(90, 560, 990, 880)).items():
        im.crop((a * k, b_ * k, c * k, d * k)).save(os.path.join(SAIDA, "zoom_perfil_%s.png" % nome))


def previa(saidas):
    """A prévia de perfil_whatsapp.py (360, 150 e 49 px, tema claro e escuro), sem apagar a prévia antiga."""
    destino = os.path.join(SAIDA, "perfil_entre_previa.png")
    antiga = os.path.join(SAIDA, "perfil_previa.png")
    guarda = antiga + ".guarda"
    if os.path.exists(antiga):
        shutil.copy(antiga, guarda)
    feito = PW.previa(saidas)
    shutil.move(feito, destino)
    if os.path.exists(guarda):
        shutil.move(guarda, antiga)
    print(destino)
    return destino


if __name__ == "__main__":
    os.makedirs(SAIDA, exist_ok=True)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    vars_ = args or list(VARIANTES)
    saidas = exportar(vars_)
    prev = previa(saidas)
    if "--zoom" in sys.argv:
        DP.K = 2
        alta = exportar(vars_[:1], escala=2, sufixo="_2x")
        zoom(alta[0][1])
    if "--final" in sys.argv:
        nomes = {"jade": "Foto de perfil A - jade.png", "rosa": "Foto de perfil B - rosa.png"}
        for var, png in saidas:
            shutil.copy(png, os.path.join(DESTINO, nomes[var]))
        shutil.copy(prev, os.path.join(DESTINO, "0 - prévia no WhatsApp (claro e escuro).png"))
        print("copiado para", DESTINO)
