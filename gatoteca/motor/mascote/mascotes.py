# -*- coding: utf-8 -*-
"""Mascote do Entrelinhas: cinco gatos no estilo da referencia (pincel seco / riso sobre kraft).

Formas chapadas, sem contorno, borda felpuda e falhas de tinta no miolo (filtro 'giz').
uso: py mascotes.py [1..5]   -> gera mascoteN.html e fotografa em ../saida
"""
import os, sys, math, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import montar

AQUI = os.path.dirname(os.path.abspath(__file__))
TINTA = "#1B1517"


def giz(i, wob=7, fel=4.5, furos=".705", absoluto=False):
    """Pincel seco: ondula a borda, desfia em fibras e abre falhas pequenas no miolo."""
    k = float(furos)
    caixa = 'filterUnits="userSpaceOnUse" x="-1500" y="-1500" width="3000" height="3000"' if absoluto else 'x="-8%%" y="-8%%" width="116%%" height="116%%"'
    return ('<filter id="giz%d" ' + caixa + ' color-interpolation-filters="sRGB">'
            '<feTurbulence type="fractalNoise" baseFrequency=".016" numOctaves="2" seed="%d" result="w"/>'
            '<feDisplacementMap in="SourceGraphic" in2="w" scale="%g" xChannelSelector="R" yChannelSelector="G" result="a"/>'
            '<feTurbulence type="fractalNoise" baseFrequency=".6 .45" numOctaves="2" seed="%d" result="f"/>'
            '<feDisplacementMap in="a" in2="f" scale="%g" xChannelSelector="R" yChannelSelector="G" result="b"/>'
            '<feTurbulence type="fractalNoise" baseFrequency=".95 .55" numOctaves="1" seed="%d" result="g"/>'
            '<feColorMatrix in="g" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -12 %g" result="h"/>'
            '<feComposite in="b" in2="h" operator="in"/></filter>') % (i, 10 + i * 7, wob, 30 + i * 11, fel, 50 + i * 13, 12 * k)


DEFS = "".join(giz(i) for i in range(1, 9)) + giz(9, wob=3, fel=3, furos=".74", absoluto=True) + (
    '<filter id="fibra" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".012 .35" numOctaves="3" seed="4"/>'
    '<feColorMatrix type="matrix" values="0 0 0 0 .35 0 0 0 0 .28 0 0 0 0 .2 0 0 0 -2.2 1.25"/></filter>')


def P(d, cor, f=1, extra=""):
    return '<path d="%s" fill="%s" filter="url(#giz%d)" %s/>' % (d, cor, f, extra)


def L(d, cor=TINTA, w=4, f=9, extra=""):
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%g" stroke-linecap="round" stroke-linejoin="round" filter="url(#giz%d)" %s/>' % (d, cor, w, f, extra)


# ------------------------------------------------------------------ geometria do gato (origem = centro do rosto)
CABECA = ("M-148,-80 C-144,-140 -80,-168 0,-168 C80,-168 144,-140 148,-80 C154,-20 176,40 164,100 "
          "C150,170 80,210 0,210 C-80,210 -150,170 -164,100 C-176,40 -154,-20 -148,-80 Z")
ORELHA_E = "M-150,-56 C-158,-150 -158,-226 -146,-292 C-102,-256 -62,-212 -28,-164 Z"
ORELHA_D = "M150,-56 C158,-150 158,-226 146,-292 C102,-256 62,-212 28,-164 Z"
DENTRO_E = "M-132,-112 C-138,-172 -138,-216 -132,-254 C-106,-228 -82,-200 -60,-172 Z"
DENTRO_D = "M132,-112 C138,-172 138,-216 132,-254 C106,-228 82,-200 60,-172 Z"
NARIZ = "M-17,40 C-17,32 17,32 17,40 C15,49 6,57 0,59 C-6,57 -15,49 -17,40Z"
BOCA = "M0,58 L0,70 M-26,73 C-16,84 -5,81 0,70 C5,81 16,84 26,73"
BIGODE = "M-92,66 L-232,46 M-94,82 L-236,94 M-90,96 L-214,128 M92,66 L232,46 M94,82 L236,94 M90,96 L214,128"
FOCINHO = "M-84,40 C-84,0 -40,-8 0,-6 C40,-8 84,0 84,40 C90,96 54,150 0,154 C-54,150 -90,96 -84,40Z"


def esc(d, sx, sy=None):
    sy = sx if sy is None else sy
    return re.sub(r"(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)", lambda m: "%.1f,%.1f" % (float(m.group(1)) * sx, float(m.group(2)) * sy), d)


def rot(svg, ang, cx, cy):
    return '<g transform="rotate(%g %g %g)">%s</g>' % (ang, cx, cy, svg)


def orelhas(pelo, dentro, ang_e=0, ang_d=0, f=2, k=1.0, ky=None):
    ky = k if ky is None else ky
    def uma(o, i, ang, cx):
        return '<g transform="rotate(%g %g -110) translate(%g -110) scale(%g %g) translate(%g 110)">%s</g>' % (ang, cx, cx, k, ky, -cx, P(o, pelo, f) + P(i, dentro, f + 1))
    return uma(ORELHA_E, DENTRO_E, ang_e, -90) + uma(ORELHA_D, DENTRO_D, ang_d, 90)


def olho_meio(cx, cy, iris, dx=0, tampa=0.45, pelo="#000", incl=0, pupila=TINTA, rx=30, ry=27, f=5):
    """Olho amendoado com a palpebra baixando (tampa = fracao coberta) e pupila em fenda deslocada."""
    topo = cy - ry + 2 * ry * tampa
    return ('<g><clipPath id="o%d%d"><ellipse cx="%g" cy="%g" rx="%g" ry="%g"/></clipPath>' % (cx, cy, cx, cy, rx, ry) +
            '<g clip-path="url(#o%d%d)">' % (cx, cy) +
            '<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (cx - rx, cy - ry, 2 * rx, 2 * ry, iris) +
            '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="%s"/>' % (cx + dx, cy + 3, rx * .24, ry * .78, pupila) +
            '<circle cx="%g" cy="%g" r="%g" fill="#FFF8EE"/>' % (cx + dx + rx * .22, cy - ry * .05, rx * .12) +
            '<path d="M%g,%g L%g,%g L%g,%g L%g,%g Z" fill="%s"/>' % (cx - rx - 4, cy - ry - 4, cx + rx + 4, cy - ry - 4, cx + rx + 4, topo - incl, cx - rx - 4, topo + incl, pelo) +
            '</g></g>' +
            L("M%g,%g L%g,%g" % (cx - rx + 2, topo + incl * .93, cx + rx - 2, topo - incl * .93), TINTA, 5))


def olho_redondo(cx, cy, r, iris=TINTA):
    return ('<circle cx="%g" cy="%g" r="%g" fill="%s" filter="url(#giz6)"/>' % (cx, cy, r, iris) +
            '<circle cx="%g" cy="%g" r="%g" fill="#FFF8EE"/><circle cx="%g" cy="%g" r="%g" fill="#FFF8EE"/>' % (cx + r * .32, cy - r * .34, r * .3, cx - r * .3, cy + r * .32, r * .13))


def olho_fechado(cx, cy, w=30, feliz=True, esp=6):
    d = ("M%g,%g C%g,%g %g,%g %g,%g" % (cx - w, cy - 2, cx - w * .4, cy + 14, cx + w * .4, cy + 14, cx + w, cy - 2)) if feliz else \
        ("M%g,%g L%g,%g L%g,%g" % (cx - w, cy + 8, cx, cy - 10, cx + w, cy + 8))
    return L(d, TINTA, esp)


def estrela(cx, cy, r, cor, pontas=4, f=9, ang=0):
    pts = []
    for i in range(pontas * 2):
        a = math.radians(ang + i * 180 / pontas - 90)
        rr = r if i % 2 == 0 else r * (.38 if pontas == 4 else .45)
        pts.append("%.1f,%.1f" % (cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return P("M" + " L".join(pts) + "Z", cor, f)


def bolinhas(cor, r, passo, x0, y0, x1, y1, f=9, desloca=True):
    s = []
    lin = 0
    y = y0
    while y < y1:
        x = x0 + (passo / 2 if desloca and lin % 2 else 0)
        while x < x1:
            s.append('<circle cx="%g" cy="%g" r="%g"/>' % (x, y, r))
            x += passo
        y += passo * .87
        lin += 1
    return '<g fill="%s" filter="url(#giz%d)">%s</g>' % (cor, f, "".join(s))


def gato(pos, esc, camadas):
    return '<g transform="translate(%g %g) scale(%g)">%s</g>' % (pos[0], pos[1], esc, "".join(camadas))


def pagina(nome, corpo, rotulo, fundo="#D9CAB5"):
    css = ('*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1080px}'
           '.peca{position:relative;width:1080px;height:1080px;overflow:hidden;background:%s}'
           '.peca::before,.peca::after{content:"";position:absolute;inset:0;pointer-events:none;background-size:1080px 1440px;z-index:5}'
           '.peca::before{background-image:var(--grao-neg);mix-blend-mode:multiply;opacity:.7}'
           '.peca::after{background-image:var(--grao-pos);mix-blend-mode:plus-lighter;opacity:.45}'
           '.peca>svg{position:absolute;left:0;top:0}'
           '.rot{position:absolute;left:46px;bottom:38px;font-family:Cinzel;font-weight:700;font-size:17px;letter-spacing:.32em;color:#3B2A33;opacity:.75;z-index:6}'
           '.rot i{font-family:Cormorant;font-style:italic;font-weight:600;letter-spacing:0;font-size:22px;text-transform:none}') % fundo
    return ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>%s</title>\n<!--ACERVO-->\n<style>%s</style></head><body><div class="peca">'
            '<svg width="1080" height="1080" viewBox="0 0 1080 1080"><defs>%s</defs>'
            '<rect width="1080" height="1080" filter="url(#fibra)" opacity=".2"/>%s</svg>'
            '<div class="rot">%s</div></div></body></html>') % (nome, css, DEFS, corpo, rotulo)


# ================================================================== 1 · MARCADOR (frajola espiando por cima do livro)
def m1():
    PRETO, BRANCO, ROSA = "#151012", "#F7F1EA", "#F08C7E"
    fundo = P("M240,150 L640,96 L870,230 L890,560 L720,690 L290,690 L180,420 Z", "#F2C94C", 7)
    gat = gato((540, 452), 1.18, [
        orelhas(PRETO, ROSA, -6, 10),
        P(CABECA, PRETO, 1),
        P("M0,-120 C14,-80 30,-40 70,-6 C92,30 92,110 50,150 C26,170 -26,170 -50,150 C-92,110 -92,30 -70,-6 C-30,-40 -14,-80 0,-120Z", BRANCO, 4),
        olho_meio(-66, -12, "#C8D96A", dx=-11, tampa=.5, pelo=PRETO, incl=-3),
        olho_meio(66, -12, "#C8D96A", dx=-11, tampa=.42, pelo=BRANCO, incl=5),
        P(NARIZ, ROSA, 6), L(BOCA, TINTA, 4.5), L(BIGODE, TINTA, 3),
    ])
    # o livro na frente, a fita vermelha e as patinhas por cima da borda
    livro = (P("M250,712 L830,682 L860,1100 L230,1100 Z", "#4F67C9", 2) +
             P("M262,690 L826,662 L834,700 L256,728 Z", "#F4ECDD", 3) +
             L("M300,700 L800,676 M300,710 L806,686", "#C9B79A", 2.2) +
             P("M600,682 L640,680 L650,930 L628,910 L606,932 Z", "#D9483B", 5) +
             L("M300,820 L560,808 M300,850 L500,844", "#8EA0E6", 6) +
             estrela(740, 820, 34, "#F2C94C", 4, 8))
    patas = (P("M408,718 C404,680 470,668 486,702 C492,722 470,734 440,734 C420,734 410,730 408,718Z", BRANCO, 6) +
             P("M594,710 C590,672 656,662 672,696 C678,716 656,728 626,728 C606,728 596,722 594,710Z", BRANCO, 6) +
             L("M432,708 L434,728 M454,706 L456,728 M618,700 L620,722 M640,698 L642,720", "#B9AEA4", 3))
    return pagina("Mascote 1 · Marcador", fundo + gat + livro + patas, "1 · <i>Marcador</i>")


# ================================================================== 2 · PAUTA (gato de caderno pautado)
def m2():
    BRANCO, AZUL, VERM = "#F7F2EA", "#6F8EDB", "#E0605A"
    argolas = "".join(L("M%d,214 C%d,170 %d,170 %d,214" % (x, x - 2, x + 26, x + 24), "#3B2A33", 6) for x in range(268, 820, 52))
    furos = "".join('<circle cx="%d" cy="230" r="9" fill="#D9CAB5" filter="url(#giz9)"/>' % (x + 12) for x in range(268, 820, 52))
    fundo = '<g transform="rotate(-4 540 520)">' + P("M230,200 L850,200 L850,880 L230,880 Z", "#9ED0B4", 7) + furos + argolas + '</g>'
    sil = CABECA + " " + ORELHA_E + " " + ORELHA_D
    linhas = "".join("M-260,%d L260,%d " % (y, y) for y in range(-262, 230, 30))
    camadas = [
        '<clipPath id="silpauta"><path d="%s"/><path d="%s" transform="rotate(14 -90 -110)"/><path d="%s" transform="rotate(-4 90 -110)"/></clipPath>' % (CABECA, ORELHA_E, ORELHA_D),
        rot(P(ORELHA_E, BRANCO, 2) + P(DENTRO_E, "#F5A3A6", 3), 14, -90, -110),
        rot(P(ORELHA_D, BRANCO, 2) + P(DENTRO_D, "#F5A3A6", 3), -4, 90, -110),
        P(CABECA, BRANCO, 1),
        '<g clip-path="url(#silpauta)">' + L(linhas, AZUL, 3.2) + L("M-104,-300 L-104,260", VERM, 4) + '</g>',
        P("M110,40 C126,24 156,30 158,54 C160,76 134,84 118,72 C108,64 104,52 110,40Z", "#3F5CC4", 6),
        olho_redondo(-64, -10, 31), olho_redondo(64, -10, 31),
        P("M-46,-66 C-60,-74 -84,-74 -96,-62", "none", 9) + L("M-44,-62 C-58,-74 -84,-76 -98,-62 M44,-66 C58,-78 84,-80 98,-68", TINTA, 6),
        P(NARIZ, "#F08C7E", 6),
        P("M-46,72 C-30,70 30,70 46,72 C42,118 20,136 0,136 C-20,136 -42,118 -46,72Z", "#2A1B22", 5),
        P("M-22,112 C-14,100 14,100 22,112 C16,128 -16,128 -22,112Z", "#F07C86", 6),
        P("M18,74 L30,74 L24,92 Z", "#FFF8EE", 9),
        L(BIGODE, TINTA, 3),
        P("M-40,190 L0,214 L40,190 L44,240 L0,222 L-44,240 Z", VERM, 4),
        P("M-12,200 L12,200 L12,226 L-12,226Z", "#B8403C", 5),
    ]
    # lapis atras da orelha
    lapis = ('<g transform="translate(-126 -150) rotate(-38)">' + P("M-14,-120 L14,-120 L14,90 L-14,90 Z", "#F2C94C", 3) +
             P("M-14,-150 L14,-150 L14,-120 L-14,-120Z", "#F08C9E", 4) + P("M-14,-126 L14,-126 L14,-116 L-14,-116Z", "#B8B2A8", 5) +
             P("M-14,90 L14,90 L0,128 Z", "#E8C9A0", 6) + P("M-5,114 L5,114 L0,128Z", TINTA, 9) + '</g>')
    corpo = fundo + gato((540, 520), 1.18, [camadas[0], lapis] + camadas[1:])
    return pagina("Mascote 2 · Pauta", corpo, "2 · <i>Pauta</i>")


# ================================================================== 3 · JACA (laranja sonolento, folha de jaqueira na cabeca)
def m3():
    LAR, LISTRA, CREME, VERDE = "#E9893C", "#B6561F", "#FBEBD6", "#4F8A4A"
    OVAL = "M540,110 C760,110 900,270 900,510 C900,770 740,930 540,930 C340,930 180,770 180,510 C180,270 320,110 540,110Z"
    jaca = (P("M530,120 C524,90 530,66 548,50 L560,58 C548,72 544,94 552,120Z", "#6B4A2A", 5) +
            P(OVAL, "#C9C65C", 7) + '<clipPath id="ovjaca"><path d="%s"/></clipPath><g clip-path="url(#ovjaca)">' % OVAL +
            bolinhas("#8C9A3E", 8, 40, 160, 100, 920, 950, 8) + '</g>' +
            P("M556,66 C590,40 640,44 660,62 C630,78 590,80 556,66Z", "#4F8A4A", 6))
    listras = ('<clipPath id="cabjaca"><path d="%s"/></clipPath><g clip-path="url(#cabjaca)">' % CABECA +
               P("M-34,-172 L-20,-172 L-24,-104 Z M-8,-176 L8,-176 L0,-94 Z M20,-172 L34,-172 L24,-104 Z", LISTRA, 3) +
               P("M-180,10 L-112,22 L-180,34 Z M-184,54 L-120,58 L-180,76 Z M180,10 L112,22 L180,34 Z M184,54 L120,58 L180,76 Z", LISTRA, 4) + '</g>')
    lenco = (P("M-170,170 C-90,226 90,226 170,170 L150,250 C80,300 -80,300 -150,250 Z", "#E8D05A", 2) +
             '<clipPath id="lenjaca"><path d="M-170,170 C-90,226 90,226 170,170 L150,250 C80,300 -80,300 -150,250 Z"/></clipPath>' +
             '<g clip-path="url(#lenjaca)">' + bolinhas("#7E9440", 6, 26, -180, 170, 180, 310, 8) + '</g>' +
             P("M-30,236 L30,236 L60,330 L0,300 L-60,330 Z", "#E8D05A", 3))
    folha = ('<g transform="translate(46 -178) rotate(-22)">' +
             P("M0,0 C60,-40 170,-40 230,0 C170,40 60,40 0,0Z", VERDE, 5) + L("M8,0 C80,-6 160,-6 222,0", "#2F5E32", 4) +
             L("M60,-4 L84,-24 M110,-4 L134,-26 M160,-3 L182,-20 M60,4 L84,22 M110,4 L134,24", "#2F5E32", 2.5) +
             L("M0,0 C-14,6 -24,18 -26,32", "#5C3A22", 5) + '</g>')
    CAB = esc(CABECA, 1.12, .96)
    corpo = jaca + gato((540, 520), 1.2, [
        orelhas(LAR, "#F5A3A6", -16, 14, k=.78, ky=.72),
        P(CAB, LAR, 1), listras.replace(CABECA, CAB),
        P(esc(FOCINHO, 1.1, 1), CREME, 4),
        olho_fechado(-64, -4, 30, True, 7), olho_fechado(64, -4, 30, True, 7),
        '<ellipse cx="-98" cy="44" rx="26" ry="15" fill="#F07C86" opacity=".7" filter="url(#giz8)"/><ellipse cx="98" cy="44" rx="26" ry="15" fill="#F07C86" opacity=".7" filter="url(#giz8)"/>',
        P(NARIZ, "#F08C7E", 6), L(BOCA, TINTA, 4.5), L(BIGODE, TINTA, 3),
        lenco, folha,
        L("M120,-60 C130,-80 150,-84 160,-70", "#FFF8EE", 3),
    ])
    corpo += P("M790,250 C800,232 822,232 830,250", "none", 9) + L("M780,250 L812,250 L780,284 L812,284 M836,206 L856,206 L836,228 L856,228", "#3B2A33", 5)
    return pagina("Mascote 3 · Jaca", corpo, "3 · <i>Jaca</i>")


# ================================================================== 4 · LUA (azul-noite, olhos de duas cores, lua na testa)
def m4():
    AZ, AZC, AMARELO = "#2E3B78", "#4E5FA6", "#F3DF9A"
    lua = P("M540,110 A390,390 0 1 1 539.9,110Z", "#F1DC98", 7) + P("M540,170 A330,330 0 1 1 539.9,170Z", "#F6E7B4", 8)
    estrelas = "".join(estrela(x, y, r, "#2E3B78", 4, 9) for x, y, r in [(150, 220, 26), (910, 300, 20), (870, 840, 30), (190, 820, 18), (960, 560, 14), (110, 520, 12)])
    capa = (P("M-230,330 C-210,220 -120,180 0,180 C120,180 210,220 230,330 L240,400 L-240,400 Z", "#6E4E9E", 2) +
            "".join(estrela(x, y, 9, "#F3DF9A", 4, 9) for x, y in [(-150, 260), (-60, 300), (40, 250), (130, 300), (-190, 350), (190, 350), (-10, 360)]) +
            P("M-70,196 C-40,236 40,236 70,196 L54,226 C20,250 -20,250 -54,226 Z", "#F3DF9A", 3))
    corpo = lua + estrelas + gato((540, 470), 1.2, [
        capa,
        orelhas(AZ, "#9AA6E8", -4, 4, k=.92, ky=1.14),
        P(CABECA, AZ, 1),
        P(FOCINHO, AZC, 4),
        P("M-34,-150 A40,40 0 1 0 34,-150 A32,32 0 1 1 -34,-150Z", AMARELO, 6),
        olho_meio(-66, -6, "#F2C14E", dx=0, tampa=.38, pelo=AZ, incl=4),
        olho_meio(66, -6, "#9FD8EE", dx=0, tampa=.38, pelo=AZ, incl=-4),
        P(NARIZ, "#E895B7", 6), L(BOCA, "#141A3A", 4.5), L(BIGODE, "#F3DF9A", 3),
        '<g transform="translate(0 246)">' + P("M-24,-26 L24,-26 L24,26 L-24,26Z", "#F7F1EA", 5) + estrela(0, 0, 16, "#6E4E9E", 4, 9) + '</g>',
    ])
    return pagina("Mascote 4 · Lua", corpo, "4 · <i>Lua</i>")


# ================================================================== 5 · CORDEL (rajado canela, chapeu de couro, piscando)
def m5():
    CAN, LISTRA, CREME, COURO = "#C27B4C", "#7C4426", "#F6E6D0", "#6B3B20"
    fundo = P("M300,160 L780,140 L930,420 L820,830 L330,870 L160,520 Z", "#E3B04B", 7)
    listras = ('<clipPath id="cabcordel"><path d="%s"/></clipPath><g clip-path="url(#cabcordel)">' % CABECA +
               P("M-180,0 L-110,16 L-180,30 Z M-184,46 L-118,52 L-180,70 Z M180,0 L110,16 L180,30 Z M184,46 L118,52 L180,70 Z", LISTRA, 4) + '</g>')
    # meia-lua de couro com as pontas para os lados; borda clara com ilhoses, estrela de Salomao no meio
    MEIA = "M-250,6 C-200,-150 -90,-196 0,-196 C90,-196 200,-150 250,6 C170,-34 90,-48 0,-48 C-90,-48 -170,-34 -250,6Z"
    MIOLO = "M-208,-18 C-168,-128 -82,-166 0,-166 C82,-166 168,-128 208,-18 C150,-46 80,-60 0,-60 C-80,-60 -150,-46 -208,-18Z"
    ilhos = "".join('<circle cx="%.1f" cy="%.1f" r="7.5" fill="#F1DDAE" filter="url(#giz9)"/>' % (math.cos(math.radians(t)) * 228, -40 - math.sin(math.radians(t)) * 140) for t in range(20, 170, 19))
    chapeu = ('<g transform="translate(0 -128) rotate(-6)">' +
              P("M-130,-40 C-120,-110 -60,-140 0,-140 C60,-140 120,-110 130,-40Z", "#4A2814", 2) +
              P(MEIA, "#9A5E34", 3) + P(MIOLO, COURO, 4) + ilhos +
              estrela(0, -112, 46, "#E8B84E", 8, 5, 22.5) + P("M0,-136 A24,24 0 1 1 -0.1,-136Z", COURO, 9) + estrela(0, -112, 16, "#E8B84E", 8, 9) +
              estrela(-112, -88, 15, "#E8B84E", 4, 9) + estrela(112, -88, 15, "#E8B84E", 4, 9) + '</g>')
    lenco = (P("M-160,176 C-90,232 90,232 160,176 L140,250 C70,296 -70,296 -140,250 Z", "#D9483B", 2) +
             '<clipPath id="lencord"><path d="M-160,176 C-90,232 90,232 160,176 L140,250 C70,296 -70,296 -140,250 Z"/><path d="M-36,236 L36,236 L84,330 L0,296 L-84,330Z"/></clipPath>' +
             P("M-36,236 L36,236 L84,330 L0,296 L-84,330Z", "#D9483B", 3) +
             '<g clip-path="url(#lencord)">' + bolinhas("#F7F1EA", 7, 32, -170, 176, 170, 340, 9) + '</g>' +
             P("M-26,226 C-26,206 26,206 26,226 C26,250 -26,250 -26,226Z", "#B8362C", 4))
    corpo = fundo + gato((540, 540), 1.15, [
        orelhas(CAN, "#F5A3A6", -8, 22, k=.95),
        P(esc(CABECA, 1.05, 1), CAN, 1), listras,
        P(FOCINHO, CREME, 4),
        olho_fechado(-64, -8, 30, False, 7),
        olho_meio(66, -8, "#E8C24A", dx=4, tampa=.3, pelo=CAN, incl=-6),
        P(NARIZ, "#F08C7E", 6), L("M0,58 L0,70 M-22,74 C-14,80 -6,78 0,70 C8,80 22,78 34,62", TINTA, 4.5), L(BIGODE, TINTA, 3),
        lenco, chapeu,
    ])
    return pagina("Mascote 5 · Cordel", corpo, "5 · <i>Cordel</i>")


MASC = {1: ("mascote1_marcador", m1), 2: ("mascote2_pauta", m2), 3: ("mascote3_jaca", m3), 4: ("mascote4_lua", m4), 5: ("mascote5_cordel", m5)}

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    qual = [int(a) for a in sys.argv[1:]] or list(MASC)
    saida = os.path.join(os.path.dirname(AQUI), "saida")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1080})
        for k in qual:
            nome, f = MASC[k]
            html = f().replace("<!--ACERVO-->", montar.ACERVO_CSS)
            arq = os.path.join(saida, nome + ".final.html")
            open(arq, "w", encoding="utf-8").write(html)
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(900)
            pg.screenshot(path=os.path.join(saida, nome + ".png"))
            print(nome)
        b.close()
