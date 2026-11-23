# -*- coding: utf-8 -*-
"""Post Lilith × TULIPA, versao 2 (limpa): uma cartinha clara, «CLUBE DE LITERATURA» grande,
so a Lilith-gata sobre a lua negra no centro, informacoes em tres colunas legiveis.
Elementos das folhas dele: selo da TULIPA como lacre no canto, estrela dourada, lacre vinho de lua.
uso: py post_lilith2.py
"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "mascote"))
import montar
import cartinhas as C
from cartinhas import cartao, raios, estrela8, titulo, imagem, elem, JADE, JADE_E, ROSA, ROSA_C, NOITE, AMEIXA, PEROLA, OURO
import post_lilith as PL
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[2]  # raiz do repositório

CREME = "#F6EDE6"
LOGO = str(_REPO / 'gatoteca/motor/assets/logo_tulipa.png')
D = str(_REPO / 'gatoteca/artes')


def gata_simples(cx, base, k):
    p = PL.lilith_gata()
    return p


def lilith_limpa(cx, base, k):
    """A Lilith-gata sem asas, corujas, serpente e lua-assento: so a gata com diadema e a lua no peito."""
    import gato_banco as G
    from gato_banco import Pose, elipse, rabo, montar_svg
    from shapely.geometry import Point
    p = Pose("91", "Lilith", "", "", centro=(0, -200))
    p.pe, p.pb, p.iris = PL.PELO, PL.PEITO, PL.DOURADO_OLHO
    rabo(p, [(100, -12), (168, -30), (204, -86), (190, -146)], 19, 13, ponta=False)
    corpo = G.amostrar(G.F.CORPO).buffer(4)
    lua_peito = Point(0, -150).buffer(40).difference(Point(15, -160).buffer(35))
    p.peca(corpo, lambda x, y: (x / 230, 1), brancos=lua_peito)
    p.svg('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round" opacity=".5"/>' % (G.F.PERNAS, PL.PELO["claro"]))
    for x in (-46, 46):
        p.peca(elipse(x, -12, 27, 15), lambda a, b: (0, 1), tufo=dict(passo=5, L=(4, 8), w=1.6))
    p.svg('<path d="M-56,-10 L-56,-18 M-38,-8 L-38,-17 M56,-10 L56,-18 M38,-8 L38,-17" stroke="%s" stroke-width="1.6" stroke-linecap="round"/>' % PL.PELO["borda"])
    p.cabeca(0, -262, expr="neutro", mancha_testa=False, acess=[PL.diadema()], topo_acess=-170)
    svg, w, h = montar_svg(p, pad=10)
    miolo = svg[svg.index("</defs>") + 7: svg.rindex("</svg>")]
    defs = svg[svg.index("<defs>") + 6: svg.index("</defs>")]
    return defs, '<g transform="translate(%g %g) scale(%g)">%s</g>' % (cx, base, k, miolo)


def peca():
    W, H = 930, 1010
    mx, my, r = W / 2, 560, 190
    defs_gata, gata = lilith_limpa(mx, my + r - 36, .86)
    lua_negra = ('<defs><radialGradient id="luaNegra" cx="42%" cy="38%" r="70%"><stop offset="0" stop-color="#3A3446"/>'
                 '<stop offset=".7" stop-color="#262330"/><stop offset="1" stop-color="#1A1820"/></radialGradient></defs>'
                 + '<circle cx="%g" cy="%g" r="%g" fill="%s" opacity=".5"/>' % (mx, my, r + 44, ROSA_C)
                 + raios(mx, my, r + 16, r + 78, ROSA, 40, .75, 2, 5)
                 + '<circle cx="%g" cy="%g" r="%g" fill="url(#luaNegra)" stroke="%s" stroke-width="5"/>' % (mx, my, r, OURO)
                 + '<circle cx="%g" cy="%g" r="%g" fill="none" stroke="%s" stroke-width="1.6" opacity=".7"/>' % (mx, my, r - 12, OURO))
    brilhos = "".join(estrela8(x, y, rr, OURO, AMEIXA, 1.4) for x, y, rr in ((mx - 122, my - 96, 13), (mx + 134, my - 70, 10), (mx + 104, my - 140, 7)))
    col = ""
    for k, (rot_, l1, l2) in enumerate((("QUANDO", "Quintas, 13h", "a cada 15 dias"), ("ONDE", "Sala 713", "bloco B · UNICAP"),
                                         ("QUANTO", "Gratuito", "e aberto a todos"))):
        cx = 160 + k * 305
        col += '<text x="%g" y="900" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="18" letter-spacing="5" fill="%s">%s</text>' % (cx, JADE_E, rot_)
        col += '<text x="%g" y="944" text-anchor="middle" font-family="DM Serif Display" font-size="40" fill="%s">%s</text>' % (cx, NOITE, l1)
        col += '<text x="%g" y="976" text-anchor="middle" font-family="Cormorant" font-style="italic" font-weight="700" font-size="29" fill="%s">%s</text>' % (cx, AMEIXA, l2)
        if k:
            col += '<path d="M%g,880 L%g,978" stroke="%s" stroke-width="1.4" opacity=".4"/>' % (cx - 152, cx - 152, AMEIXA)
    conteudo = (
        '<text x="%g" y="100" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="44" letter-spacing="8" fill="%s">CLUBE DE LITERATURA</text>' % (W / 2, AMEIXA)
        + '<text x="%g" y="192" text-anchor="middle" font-family="DM Serif Display" font-size="92" fill="%s">Entrelinhas</text>' % (W / 2, JADE_E)
        + '<text x="%g" y="236" text-anchor="middle" font-family="Cormorant" font-style="italic" font-weight="700" font-size="31" fill="%s">em parceria com a TULIPA · UNICAP</text>' % (W / 2, AMEIXA)
        + '<path d="M150,272 L%g,272 M%g,272 L780,272" stroke="%s" stroke-width="1.6" opacity=".55"/>' % (W / 2 - 28, W / 2 + 28, AMEIXA)
        + estrela8(W / 2, 272, 12, ROSA, AMEIXA)
        + '<text x="%g" y="318" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="18" letter-spacing="7" fill="%s">TEMA DO ENCONTRO</text>' % (W / 2, JADE_E)
        + lua_negra + brilhos + gata
        + titulo(W / 2 + 5, 846, "Lilith", 120, JADE, JADE, 1, 0)
        + titulo(W / 2, 840, "Lilith", 120, ROSA_C, AMEIXA, 7, 0)
        + '<text x="160" y="440" text-anchor="middle" font-family="Caveat" font-weight="700" font-size="34" fill="%s" transform="rotate(-4 160 440)">a primeira mulher,</text>' % AMEIXA
        + '<text x="164" y="478" text-anchor="middle" font-family="Caveat" font-weight="700" font-size="34" fill="%s" transform="rotate(-4 164 478)">a que não se curvou</text>' % AMEIXA
        + '<path d="M60,866 L%g,866" stroke="%s" stroke-width="1.4" opacity=".3"/>' % (W - 60, AMEIXA)
        + col)
    atras = cartao(566, 640, W - 40, H - 50, JADE, 4.5, AMEIXA, "")
    frente = cartao(540, 632, W, H, CREME, -1.5, AMEIXA, conteudo)
    selo_tulipa = imagem(LOGO, 968, 150, 150, rot=10)
    estrela = imagem(elem("2 Astros", "estrela_dourada_8_longa"), 112, 160, 128, rot=-8)
    lacre = imagem(elem("1 Lacres e selos", "lacre_vinho_lua"), 1028, 1152, 128, rot=-10)
    cta = ('<text x="580" y="1252" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="28" letter-spacing="5" fill="%s">INSCREVA-SE PELO LINK ABAIXO ↓</text>' % OURO
           + '<text x="580" y="1302" text-anchor="middle" font-family="Cormorant" font-style="italic" font-weight="600" font-size="35" fill="%s">e entre no grupo do WhatsApp do clube</text>' % PEROLA)
    corpo = C.mesa() + '<defs>%s</defs>' % defs_gata + atras + frente + selo_tulipa + estrela + lacre + cta
    return C.pagina("Entrelinhas · Lilith (v2)", corpo)


if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    html = peca().replace("<!--ACERVO-->", montar.ACERVO_CSS)
    arq = os.path.join(AQUI, "saida", "post_lilith2.final.html")
    open(arq, "w", encoding="utf-8").write(html)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for esc, destino in ((1, os.path.join(AQUI, "saida", "post_lilith2.png")),
                             (1, os.path.join(D, "Lilith × TULIPA - post v2 (limpo).png")),
                             (2, os.path.join(D, "alta resolução (2160x2700)", "Lilith × TULIPA - post v2 (limpo).png"))):
            pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=esc)
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(1300)
            pg.screenshot(path=destino)
        b.close()
    print("ok")
