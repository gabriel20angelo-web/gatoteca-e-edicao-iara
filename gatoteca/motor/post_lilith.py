# -*- coding: utf-8 -*-
"""Post do Entrelinhas × TULIPA sobre LILITH, na identidade «cartinhas», com a Lilith-gata.

A Lilith-gata (feita no motor do mascote): gata preta de pelucia com luz rosada na silhueta, olhos
dourados, crescente crescente-de-lua no peito, diadema de lua, asas de coruja abertas (Relevo de
Burney), serpente enrolada aos pes, sentada numa lua crescente com duas corujinhas nas pontas.
uso: py post_lilith.py   -> saida/post_lilith.png (+ copia na pasta do clube, normal e 2x)
"""
import os, sys, math
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "mascote"))
import montar
import cartinhas as C
from cartinhas import (cartao, moldura, raios, estrela8, estrela5, ceu, anel_perolas, selo_postal, carimbo, titulo, imagem, gato, elem,
                       JADE, JADE_E, ROSA, ROSA_C, NOITE, AMEIXA, PEROLA, OURO)
import gato_banco as G
from gato_banco import Pose, elipse, capsula, spline, rabo, membro, montar_svg
from shapely.geometry import Point
from shapely.ops import unary_union
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[2]  # raiz do repositório

PELO = dict(base="#211A20", escuro="#0E0A0D", medio="#382C35", claro="#6E5A68", borda="#C796AE")
PEITO = dict(base="#F1E3E6", escuro="#C9B3BC", medio="#E2CFD6", claro="#FFFFFF", borda="#C796AE")
DOURADO_OLHO = "#E3B04B"
LUA_OURO, LUA_OURO_E = "#E8C46A", "#B8893A"


# ================================================================== pecas da Lilith-gata (coordenadas da pose: chao y=0, cabeca em (0,-262))
def pena(x, y, ang, L, w, fill, contorno=OURO):
    return ('<path transform="translate(%.1f %.1f) rotate(%.1f)" d="M0,0 C%.1f,%.1f %.1f,%.1f 0,%.1f C%.1f,%.1f %.1f,%.1f 0,0Z" fill="%s" stroke="%s" stroke-width="1.3"/>'
            '<path transform="translate(%.1f %.1f) rotate(%.1f)" d="M0,%.1f L0,%.1f" stroke="%s" stroke-width=".8" opacity=".6"/>') % (
        x, y, ang, -w, L * .2, -w, L * .8, L, w, L * .8, w, L * .2, fill, contorno, x, y, ang, L * .12, L * .88, contorno)


def asa(lado):
    """Asa de coruja aberta: primarias longas (atras), secundarias, cobertura com escamas rosa (frente)."""
    s = []
    cores = ("#3E2638", "#4E3046")
    for i in range(8):  # primarias
        t = i / 7
        x, y = lado * (318 - 150 * t), -318 + 170 * t
        s.append(pena(x, y, -lado * (34 - 22 * t), 150 - 40 * t, 15, cores[i % 2]))
    for i in range(7):  # secundarias
        t = i / 6
        x, y = lado * (272 - 150 * t), -300 + 150 * t
        s.append(pena(x, y, -lado * (26 - 16 * t), 96 - 24 * t, 14, cores[(i + 1) % 2]))
    cob = ("M%g,-226 C%g,-292 %g,-356 %g,-372 C%g,-384 %g,-360 %g,-322 C%g,-280 %g,-232 %g,-196 C%g,-180 %g,-170 %g,-176 Z" % (
        lado * 64, lado * 104, lado * 190, lado * 266, lado * 304, lado * 334, lado * 328, lado * 318, lado * 292, lado * 248, lado * 200, lado * 140, lado * 90))
    s.append('<path d="%s" fill="#2F1D2B" stroke="%s" stroke-width="1.6" stroke-linejoin="round"/>' % (cob, OURO))
    esc = ""
    for r, (y0, x0, x1) in enumerate(((-330, 170, 300), (-300, 130, 300), (-268, 110, 280), (-236, 100, 240))):
        x = x0
        while x < x1:
            esc += "M%g,%g q%g,10 %g,0 " % (lado * x, y0 + (x - x0) * .18, lado * 9, lado * 18)
            x += 18
    s.append('<clipPath id="cob%d"><path d="%s"/></clipPath><g clip-path="url(#cob%d)"><path d="%s" fill="none" stroke="%s" stroke-width="1.8" opacity=".85"/></g>' % (
        lado + 1, cob, lado + 1, esc, ROSA))
    return "".join(s)


def lua_assento():
    d = "M-318,-64 C-306,118 306,118 318,-64 C250,46 -250,46 -318,-64Z"
    s = '<path d="%s" fill="%s" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (d, LUA_OURO, AMEIXA)
    s += '<path d="M-286,-30 C-250,70 250,70 286,-30" fill="none" stroke="#FFF1C4" stroke-width="3" opacity=".6"/>'
    for x, y, r in ((-150, 52, 9), (60, 66, 6), (190, 44, 8), (-40, 70, 5)):
        s += '<circle cx="%g" cy="%g" r="%g" fill="%s" opacity=".55"/>' % (x, y, r, LUA_OURO_E)
    return s


def coruja(cx, base, k=1.0, espelho=1, olhar=0):
    s = '<g transform="translate(%g %g) scale(%g %g)">' % (cx, base, k * espelho, k)
    corpo = "M-34,0 C-46,-40 -40,-86 -26,-104 L-30,-128 L-12,-112 C-4,-115 4,-115 12,-112 L30,-128 L26,-104 C40,-86 46,-40 34,0 C14,8 -14,8 -34,0Z"
    s += '<path d="%s" fill="%s" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % (corpo, ROSA, AMEIXA)
    s += '<path d="M-20,-48 C-20,-20 -10,-4 0,-2 C10,-4 20,-20 20,-48 C10,-56 -10,-56 -20,-48Z" fill="%s"/>' % ROSA_C
    esc = "".join("M%g,%g q4,5 8,0 " % (x, y) for y in (-40, -28, -16) for x in range(-14, 12, 9))
    s += '<path d="%s" fill="none" stroke="%s" stroke-width="1.4" opacity=".7"/>' % (esc, AMEIXA)
    s += '<path d="M-34,-60 C-46,-36 -42,-12 -30,-2 M34,-60 C46,-36 42,-12 30,-2" fill="none" stroke="%s" stroke-width="2" opacity=".7"/>' % AMEIXA
    for x in (-15, 15):
        s += '<circle cx="%g" cy="-80" r="15" fill="%s" stroke="%s" stroke-width="2.2"/>' % (x, ROSA_C, AMEIXA)
        s += '<circle cx="%g" cy="-80" r="9.5" fill="%s" stroke="%s" stroke-width="1.6"/>' % (x, DOURADO_OLHO, AMEIXA)
        s += '<circle cx="%g" cy="-80" r="5" fill="#14100F"/><circle cx="%g" cy="-83" r="1.8" fill="#FFF"/>' % (x + olhar, x + olhar + 2)
    s += '<path d="M-5,-66 L5,-66 L0,-56Z" fill="%s" stroke="%s" stroke-width="1.4" stroke-linejoin="round"/>' % (OURO, AMEIXA)
    s += '<path d="M-14,2 l-4,7 M-10,3 l0,8 M10,3 l0,8 M14,2 l4,7" stroke="%s" stroke-width="2.4" stroke-linecap="round"/>' % LUA_OURO_E
    return s + '</g>'


def serpente_corpo():
    pts = [(-176, -40), (-130, 4), (-20, 18), (110, 8), (176, -36), (196, -112), (182, -182), (150, -222)]
    c = spline(pts, 12)
    corpo = capsula(pts, 6, 14)
    from felpudo import caminho
    s = '<path d="%s" fill="%s" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % (caminho(corpo), JADE, AMEIXA)
    barriga = " L".join("%.1f,%.1f" % (x, y + 2.5) for x, y in c[int(len(c) * .15):])
    s += '<path d="M%s" fill="none" stroke="#B0CAC1" stroke-width="5" stroke-linecap="round" opacity=".75"/>' % barriga
    esc = ""
    for i in range(3, len(c) - 1, 3):
        (x0, y0), (x1, y1) = c[i - 1], c[i + 1]
        tx, ty = x1 - x0, y1 - y0
        m = math.hypot(tx, ty) or 1
        tx, ty = tx / m, ty / m
        r = 6 + 8 * i / len(c)
        x, y = c[i]
        esc += "M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f " % (x - ty * r * .7 - tx * r * .5, y + tx * r * .7 - ty * r * .5, x, y, x + ty * r * .7 - tx * r * .5, y - tx * r * .7 - ty * r * .5)
    s += '<path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-linejoin="round" opacity=".9"/>' % (esc, OURO)
    return s


def serpente_cabeca():
    s = '<g transform="translate(146 -228) rotate(-58)">'
    s += '<path d="M-14,4 C-18,-10 -14,-26 -6,-34 C-2,-38 2,-38 6,-34 C14,-26 18,-10 14,4 Z" fill="%s" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % (JADE, AMEIXA)
    s += '<path d="M-6,-6 L0,-12 L6,-6 M-5,0 L0,-5 L5,0" fill="none" stroke="%s" stroke-width="1.4"/>' % OURO
    s += '<ellipse cx="-7" cy="-22" rx="3.6" ry="4.2" fill="%s" stroke="%s" stroke-width="1.2"/><ellipse cx="-7" cy="-22" rx="1" ry="3.2" fill="#14100F"/>' % (DOURADO_OLHO, AMEIXA)
    s += '<path d="M0,-37 L0,-50 M0,-50 l-4,-6 M0,-50 l4,-6" stroke="#E0566E" stroke-width="2" fill="none" stroke-linecap="round"/>'
    return s + '</g>'


def diadema():
    """Coordenadas do rosto: tiara de ouro na testa, gotas de perola e a lua crescente no alto."""
    s = '<path d="M-74,-64 C-40,-92 40,-92 74,-64" fill="none" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % AMEIXA
    s += '<path d="M-74,-64 C-40,-92 40,-92 74,-64" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % OURO
    for x, y in ((-46, -80), (-22, -86), (22, -86), (46, -80)):
        s += '<circle cx="%g" cy="%g" r="4.2" fill="%s" stroke="%s" stroke-width="1.2"/>' % (x, y + 6, PEROLA, AMEIXA)
    s += '<path d="M2,-150 a32,32 0 1 0 0,64 a44,44 0 0 1 0,-64Z" fill="%s" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % (LUA_OURO, AMEIXA)
    s += estrela8(18, -150, 9, PEROLA, AMEIXA, 1.2)
    s += '<path d="M-2,-90 L-2,-84" stroke="%s" stroke-width="3"/>' % OURO
    return s


def lilith_gata():
    p = Pose("90", "Lilith", "", "", centro=(0, -200))
    p.pe, p.pb, p.iris = PELO, PEITO, DOURADO_OLHO
    p.svg(asa(-1) + asa(1), caixa=(-345, -400, 345, -130))
    p.svg(lua_assento(), caixa=(-325, -70, 325, 100))
    rabo(p, [(-100, -12), (-168, -24), (-214, -74), (-206, -130)], 19, 13, ponta=False)
    corpo = G.amostrar(G.F.CORPO).buffer(4)
    lua_peito = Point(0, -150).buffer(40).difference(Point(15, -160).buffer(35))
    p.peca(corpo, lambda x, y: (x / 230, 1), brancos=lua_peito)
    p.svg('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round" opacity=".5"/>' % (G.F.PERNAS, PELO["claro"]))
    p.svg(serpente_corpo())
    for x in (-46, 46):
        p.peca(elipse(x, -12, 27, 15), lambda a, b: (0, 1), tufo=dict(passo=5, L=(4, 8), w=1.6))
    p.svg('<path d="M-56,-10 L-56,-18 M-38,-8 L-38,-17 M56,-10 L56,-18 M38,-8 L38,-17" stroke="%s" stroke-width="1.6" stroke-linecap="round"/>' % PELO["borda"])
    p.cabeca(0, -262, expr="neutro", mancha_testa=False, acess=[diadema()], topo_acess=-170)
    p.svg(serpente_cabeca())
    p.svg(coruja(-292, -66, .82, 1, 2) + coruja(292, -66, .82, -1, 2), caixa=(-330, -180, 330, -60))
    return p


def lilith_svg(cx, cy, k):
    """Devolve o desenho da Lilith-gata centrado em (cx, cy) na escala k."""
    p = lilith_gata()
    svg, w, h = montar_svg(p, pad=10)
    import re
    vb = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"', svg)
    x0, y0, vw, vh = map(float, vb.groups())
    miolo = svg[svg.index('</defs>') + 7: svg.rindex('</svg>')]
    defs = svg[svg.index('<defs>') + 6: svg.index('</defs>')]
    return defs, '<g transform="translate(%g %g) scale(%g) translate(%g %g)">%s</g>' % (cx, cy, k, -(x0 + vw / 2), -(y0 + vh / 2), miolo), (vw * k, vh * k)


# ================================================================== a peca
def peca():
    defs_gata, gata, (gw, gh) = lilith_svg(450, 528, .76)
    W, H = 900, 800
    mx, my, rx, ry = 450, 520, 262, 226
    livre = lambda x, y: ((x - mx) / (rx + 40)) ** 2 + ((y - my) / (ry + 40)) ** 2 < 1 or (y < 300 and 120 < x < 780)
    ceu_ = ceu(36, 36, W - 36, H - 36, 52, 21, ROSA, "#7FB3A6", livre)
    eclipse = ('<defs><radialGradient id="eclipse" r=".5"><stop offset="0" stop-color="#1B1720"/><stop offset=".8" stop-color="#1B1720"/>'
               '<stop offset=".93" stop-color="#5A3448"/><stop offset="1" stop-color="#C796AE"/></radialGradient></defs>')
    conteudo = (eclipse + raios(mx, my, rx + 24, rx + 230, ROSA_C, 34, .45, 1.4, 7) + ceu_ +
                '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="url(#eclipse)"/>' % (mx, my, rx - 8, ry - 8) +
                anel_perolas(mx, my, rx, ry, 15) + gata +
                '<text x="%g" y="78" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="17" letter-spacing="8" fill="%s">TEMA DO ENCONTRO</text>' % (W / 2, OURO) +
                titulo(W / 2 + 6, 214, "Lilith", 158, JADE, JADE, 1, -3) +
                titulo(W / 2, 208, "Lilith", 158, ROSA_C, "#14111A", 9, -3) +
                '<text x="%g" y="268" text-anchor="middle" font-family="Caveat" font-weight="600" font-size="42" fill="%s" transform="rotate(-2 %g 268)">a primeira mulher, a que não se curvou</text>' % (W / 2, PEROLA, W / 2))
    principal = cartao(540, 556, W, H, NOITE, -2.5, "#C796AE", conteudo)

    # cartao das informacoes (rosa-postal)
    IW, IH = 780, 336
    linhas = ""
    for k, (rot_, txt) in enumerate((("QUANDO", "quintas, às 13h · a cada 15 dias"), ("ONDE", "sala 713, bloco B · UNICAP"), ("QUANTO", "gratuito e aberto a todos"))):
        y = 150 + k * 66
        linhas += '<path d="M48,%g L%g,%g" stroke="%s" stroke-width="1.3" opacity=".5"/>' % (y + 12, IW - 48, y + 12, AMEIXA)
        linhas += '<text x="52" y="%g" font-family="Cinzel" font-weight="700" font-size="14" letter-spacing="3.5" fill="%s">%s</text>' % (y - 4, JADE_E, rot_)
        linhas += '<text x="186" y="%g" font-family="Caveat" font-weight="700" font-size="40" fill="%s">%s</text>' % (y + 2, AMEIXA, txt)
    info_c = ('<g opacity=".08">' + C.olho_gato(IW / 2, IH / 2 + 10, 520, pele=AMEIXA, mono=AMEIXA, cilios=False) + '</g>' +
              '<text x="48" y="84" font-family="DM Serif Display" font-size="44" fill="%s">Vem ler com a gente</text>' % JADE_E +
              estrela8(640, 52, 12, JADE, AMEIXA) + linhas +
              carimbo(560, 62, 50, -12, "UNICAP · BLOCO B", "QUI", "13H"))
    info = cartao(560, 1080, IW, IH, ROSA, 2.5, AMEIXA, info_c)
    selo = selo_postal(905, 905, 150, 184, imagem(gato("01"), 0, -4, h=122), "grátis", 7)
    lacre = imagem(elem("1 Lacres e selos", "lacre_tulipa"), 132, 948, 132, rot=-12)

    # lockup no alto
    lock = ('<text x="80" y="66" font-family="Cinzel" font-weight="700" font-size="15" letter-spacing="6" fill="%s">CLUBE DE PSICOLOGIA</text>' % OURO +
            titulo(80, 128, "Entrelinhas", 58, ROSA_C, AMEIXA, 4.5, 0, "start") +
            '<text x="452" y="122" font-family="Cormorant" font-weight="500" font-size="44" fill="%s">×</text>' % PEROLA +
            imagem(str(_REPO / 'gatoteca/motor/assets/logo_tulipa.png'), 556, 92, 104) +
            '<text x="622" y="86" font-family="Cormorant" font-style="italic" font-weight="600" font-size="25" fill="%s">em parceria com a</text>' % PEROLA +
            '<text x="622" y="118" font-family="Cinzel" font-weight="700" font-size="22" letter-spacing="3" fill="%s">TULIPA · UNICAP</text>' % ROSA_C)
    cta = ('<text x="540" y="1292" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="22" letter-spacing="5" fill="%s">INSCREVA-SE PELO LINK ABAIXO ↓</text>' % OURO +
           '<text x="540" y="1330" text-anchor="middle" font-family="Cormorant" font-style="italic" font-weight="600" font-size="29" fill="%s">e entre no grupo do WhatsApp do clube</text>' % PEROLA)
    estrelas_mesa = ceu(20, 160, 1060, 1250, 26, 40, ROSA, "#5B4E5E", lambda x, y: 70 < x < 1010 and 150 < y < 1240)
    corpo = C.mesa() + '<defs>%s</defs>' % defs_gata + estrelas_mesa + lock + principal + info + selo + lacre + cta
    return C.pagina("Entrelinhas · Lilith", corpo)


if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    html = peca().replace("<!--ACERVO-->", montar.ACERVO_CSS)
    arq = os.path.join(AQUI, "saida", "post_lilith.final.html")
    open(arq, "w", encoding="utf-8").write(html)
    D = str(_REPO / 'gatoteca/artes')
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for esc, destino in ((1, os.path.join(AQUI, "saida", "post_lilith.png")),
                             (1, os.path.join(D, "Lilith × TULIPA - post (cartinha com a Lilith-gata).png")),
                             (2, os.path.join(D, "alta resolução (2160x2700)", "Lilith × TULIPA - post (cartinha com a Lilith-gata).png"))):
            pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=esc)
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(1300)
            pg.screenshot(path=destino)
        b.close()
    print("ok")
