# -*- coding: utf-8 -*-
"""Mascote do Entrelinhas, rodada 2: gato inteiro, gordinho (pudim), no traco de carta de tarot.

Contorno fino a mao + aguada + textura no pelo (listras, frajola, hachura de gravura).
Sem moldura de carta: o tarot fica nos elementos em volta (raios, astros, faixa com o nome).
uso: py fofos.py [1..5]
"""
import os, sys, math, re, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import montar

AQUI = os.path.dirname(os.path.abspath(__file__))
LINHA = "#2A1E24"

DEFS = r'''
<filter id="mao" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency=".04" numOctaves="2" seed="4" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="2.2" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="maoL" filterUnits="userSpaceOnUse" x="-2000" y="-2000" width="4000" height="4000">
  <feTurbulence type="fractalNoise" baseFrequency=".04" numOctaves="2" seed="4" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="2.2" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="aguada" x="-10%" y="-10%" width="120%" height="120%">
  <feTurbulence type="fractalNoise" baseFrequency=".028" numOctaves="3" seed="9" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="5" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feTurbulence type="fractalNoise" baseFrequency=".02" numOctaves="2" seed="2" result="m"/>
  <feColorMatrix in="m" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1.1 1.28" result="ma"/>
  <feComposite in="d" in2="ma" operator="in"/></filter>
<filter id="borrao" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="esfuma" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="10"/></filter>
<filter id="brilho" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="14"/></filter>
<path id="br0" d="M0,-10 Q0,0 10,0 Q0,0 0,10 Q0,0 -10,0 Q0,0 0,-10Z"/>
'''

# ------------------------------------------------------------------ geometria do gato sentado (chao em y=0, centro x=0)
CORPO = ("M-118,0 C-138,-44 -132,-114 -104,-162 C-86,-192 -60,-206 -40,-212 L40,-212 C60,-206 86,-192 104,-162 "
         "C132,-114 138,-44 118,0 C80,9 -80,9 -118,0 Z")
CABECA = ("M-100,-262 C-102,-314 -60,-344 0,-344 C60,-344 102,-314 100,-262 C99,-234 92,-212 76,-198 "
          "C56,-183 30,-178 0,-178 C-30,-178 -56,-183 -76,-198 C-92,-212 -99,-234 -100,-262 Z")
ORELHA_E = "M-90,-290 C-95,-326 -90,-360 -80,-382 C-77,-386 -73,-385 -70,-382 C-56,-368 -42,-352 -30,-336 Z"
ORELHA_D = "M90,-290 C95,-326 90,-360 80,-382 C77,-386 73,-385 70,-382 C56,-368 42,-352 30,-336 Z"
DENTRO_E = "M-80,-304 C-83,-330 -80,-354 -74,-368 C-62,-356 -52,-344 -44,-334 Z"
DENTRO_D = "M80,-304 C83,-330 80,-354 74,-368 C62,-356 52,-344 44,-334 Z"
PERNAS = "M-36,-150 C-40,-100 -42,-52 -46,-18 M36,-150 C40,-100 42,-52 46,-18"
PATA_E = "M-74,-6 C-76,-24 -56,-30 -44,-28 C-28,-26 -18,-18 -20,-6 C-22,4 -70,6 -74,-6Z"
PATA_D = "M74,-6 C76,-24 56,-30 44,-28 C28,-26 18,-18 20,-6 C22,4 70,6 74,-6Z"
DEDOS = "M-58,-8 L-58,-16 M-44,-6 L-44,-15 M58,-8 L58,-16 M44,-6 L44,-15"
PEITO = ("M-42,-196 C-36,-170 -38,-126 -30,-96 L-20,-104 L-12,-86 L0,-96 L12,-86 L20,-104 L30,-96 "
         "C38,-126 36,-170 42,-196 C20,-186 -20,-186 -42,-196Z")
FOCINHO = "M-34,-240 C-34,-256 -14,-260 0,-252 C14,-260 34,-256 34,-240 C34,-218 16,-206 0,-206 C-16,-206 -34,-218 -34,-240Z"
CAUDA_FRENTE = "M116,-26 C132,8 70,26 -6,20 C-44,18 -70,12 -78,2 C-70,-8 -46,-2 -8,1 C52,5 98,-2 100,-30 Z"
CAUDA_CIMA = "M110,-20 C170,-26 200,-96 174,-164 C168,-182 146,-182 150,-164 C172,-104 156,-60 108,-50 Z"
PATA_ERGUIDA = "M58,-232 C52,-252 70,-266 86,-260 C100,-254 102,-236 92,-226 C82,-216 62,-218 58,-232Z"
BRACO_ERGUIDO = "M40,-176 C60,-190 66,-214 66,-230 L90,-226 C92,-206 84,-180 64,-160 Z"


def clarear(h, f):
    h = h.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(int(c + (255 - c) * f) for c in (r, g, b))


def P(d, cor, f="aguada", extra="", op=1, base=True):
    fundo = '<path d="%s" fill="%s" opacity="%g" %s/>' % (d, clarear(cor, .16), op, extra) if base and cor.startswith("#") else ""
    return fundo + '<path d="%s" fill="%s" opacity="%g" filter="url(#%s)" %s/>' % (d, cor, op, f, extra)


def C(d, w=3, cor=LINHA, f="mao", extra=""):
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%g" stroke-linecap="round" stroke-linejoin="round" filter="url(#%s)" %s/>' % (d, cor, w, f, extra)


def hachura(clip_id, x0, y0, x1, y1, passo=7, ang=45, cor=LINHA, op=.3, w=1.1):
    s = []
    n = int((x1 - x0 + y1 - y0) / passo) + 2
    for i in range(n):
        x = x0 - (y1 - y0) + i * passo
        s.append("M%g,%g L%g,%g" % (x, y1, x + (y1 - y0), y0))
    return '<g clip-path="url(#%s)" opacity="%g">%s</g>' % (clip_id, op, C(" ".join(s), w, cor, "maoL"))


def olhos(tipo, cor_iris=LINHA, olhar=(0, 0)):
    dx, dy = olhar
    if tipo == "redondo":
        s = ""
        for x in (-38, 38):
            s += '<ellipse cx="%g" cy="-262" rx="13" ry="15" fill="%s"/>' % (x, cor_iris)
            if cor_iris != LINHA:
                s += '<ellipse cx="%g" cy="%g" rx="7" ry="11" fill="%s"/>' % (x + dx, -262 + dy, LINHA)
            s += '<circle cx="%g" cy="%g" r="5" fill="#FFFBF0"/><circle cx="%g" cy="%g" r="2.2" fill="#FFFBF0"/>' % (x + 4 + dx * .5, -268 + dy * .5, x - 4, -256)
        return s
    if tipo == "feliz":
        return C("M-50,-258 C-44,-270 -32,-270 -26,-258 M26,-258 C32,-270 44,-270 50,-258", 4)
    if tipo == "dormindo":
        return C("M-50,-264 C-44,-254 -32,-254 -26,-264 M26,-264 C32,-254 44,-254 50,-264", 4) + C("M-48,-260 l-6,5 M28,-260 l-4,6 M48,-260 l6,5", 2)
    return ""


def rosto(nariz="#F0919A", boca="normal", bigode=LINHA):
    s = '<ellipse cx="-62" cy="-236" rx="15" ry="8" fill="#F28C9A" opacity=".5" filter="url(#borrao)"/><ellipse cx="62" cy="-236" rx="15" ry="8" fill="#F28C9A" opacity=".5" filter="url(#borrao)"/>'
    s += '<path d="M-8,-246 L8,-246 C8,-241 3,-238 0,-237 C-3,-238 -8,-241 -8,-246Z" fill="%s" stroke="%s" stroke-width="1.4"/>' % (nariz, LINHA)
    if boca == "aberta":
        s += C("M0,-237 L0,-231", 2.4) + '<path d="M-11,-230 C-9,-216 9,-216 11,-230 C4,-226 -4,-226 -11,-230Z" fill="#B8475A" stroke="%s" stroke-width="2"/>' % LINHA
    else:
        s += C("M0,-237 L0,-231 M-13,-230 C-10,-223 -3,-223 0,-231 C3,-223 10,-223 13,-230", 2.4)
    s += C("M-72,-240 L-132,-250 M-72,-232 L-134,-228 M72,-240 L132,-250 M72,-232 L134,-228", 1.6, bigode, "maoL")
    return s


def gato(pal, padrao="", olho="redondo", cauda="frente", pata="chao", olhar=(0, 0), boca="normal", uid="g"):
    """Gato sentado e gordinho. pal: corpo, peito, orelha, listra, iris."""
    corpo, peito = pal["corpo"], pal.get("peito")
    s = ['<clipPath id="c%s"><path d="%s"/><path d="%s"/></clipPath>' % (uid, CORPO, CABECA),
         '<clipPath id="cb%s"><path d="%s"/></clipPath>' % (uid, CORPO)]
    # rabo para cima fica atras do corpo
    if cauda == "cima":
        s.append(P(CAUDA_CIMA, corpo) + C(CAUDA_CIMA, 3))
        if pal.get("ponta"):
            s.append('<clipPath id="ct%s"><path d="%s"/></clipPath><g clip-path="url(#ct%s)">%s</g>' % (uid, CAUDA_CIMA, uid, P("M120,-200 L220,-200 L220,-120 L120,-120Z", pal["ponta"])))
        if pal.get("listra"):
            s.append('<clipPath id="ct2%s"><path d="%s"/></clipPath><g clip-path="url(#ct2%s)">%s</g>' % (uid, CAUDA_CIMA, uid,
                     C("M150,-40 L190,-60 M164,-80 L204,-92 M166,-120 L206,-124 M160,-150 L196,-168", 7, pal["listra"], "maoL")))
    # orelhas
    s.append('<g transform="translate(0 -262) scale(1.08) translate(0 262)">')
    for o, i in ((ORELHA_E, DENTRO_E), (ORELHA_D, DENTRO_D)):
        s.append(P(o, pal.get("orelha_fora", corpo)) + P(i, pal.get("orelha", "#F4A9B0")) + C(o, 3))
    s.append('</g>')
    # corpo
    s.append(P(CORPO, corpo))
    s.append(padrao)  # listras/manchas recortadas pelo corpo e cabeca (vem pronto)
    s.append(hachura("cb" + uid, 20, -210, 140, 10, 8, 45, pal.get("hachura", LINHA), .22))
    if peito:
        s.append(P(PEITO, peito))
    s.append(C(CORPO, 3.2))
    s.append(C(PERNAS, 2.4))
    if peito:
        s.append(C(PEITO, 2, LINHA, "mao", 'opacity=".55"'))
    # patas
    s.append(P(PATA_E, pal.get("patas", corpo)) + C(PATA_E, 2.6))
    if pata == "chao":
        s.append(P(PATA_D, pal.get("patas", corpo)) + C(PATA_D, 2.6) + C(DEDOS, 1.8))
    else:
        s.append(C("M-58,-8 L-58,-16 M-44,-6 L-44,-15", 1.8))
    if cauda == "frente":
        s.append(P(CAUDA_FRENTE, corpo) + C(CAUDA_FRENTE, 3))
        if pal.get("ponta"):
            s.append('<clipPath id="cf%s"><path d="%s"/></clipPath><g clip-path="url(#cf%s)">%s</g>' % (uid, CAUDA_FRENTE, uid, P("M-90,-20 L-30,-20 L-30,30 L-90,30Z", pal["ponta"])))
        if pal.get("listra"):
            s.append('<clipPath id="cf2%s"><path d="%s"/></clipPath><g clip-path="url(#cf2%s)">%s</g>' % (uid, CAUDA_FRENTE, uid,
                     C("M90,-30 L100,20 M50,-10 L56,30 M10,-10 L14,30 M-30,-10 L-28,30", 7, pal["listra"], "maoL")))
    # cabeca
    s.append('<g transform="translate(0 -262) scale(1.08) translate(0 262)">')
    s.append(P(CABECA, corpo))
    if pal.get("mascara"):
        s.append('<clipPath id="ch%s"><path d="%s"/></clipPath><g clip-path="url(#ch%s)">%s</g>' % (uid, CABECA, uid, pal["mascara"]))
    if pal.get("focinho"):
        s.append(P(FOCINHO, pal["focinho"]))
    if pal.get("cabeca_padrao"):
        s.append('<clipPath id="ch2%s"><path d="%s"/></clipPath><g clip-path="url(#ch2%s)">%s</g>' % (uid, CABECA, uid, pal["cabeca_padrao"]))
    s.append(C(CABECA, 3.2))
    s.append(olhos(olho, pal.get("iris", LINHA), olhar))
    s.append(rosto(pal.get("nariz", "#F0919A"), boca, pal.get("bigode", LINHA)))
    s.append('</g>')
    if pata != "chao":
        s.append(P(BRACO_ERGUIDO, corpo) + C("M40,-176 C60,-190 66,-214 66,-230 M90,-226 C92,-206 84,-180 64,-160", 2.8) +
                 P(PATA_ERGUIDA, pal.get("patas", corpo)) + C(PATA_ERGUIDA, 2.6) + C("M66,-246 L72,-240 M78,-254 L84,-246", 1.6))
    return "".join(s)


def listras_tabby(cor, uid):
    """Listrinhas: M na testa, bochechas e arcos no corpo."""
    cab = C("M-16,-338 L-12,-306 M0,-342 L0,-302 M16,-338 L12,-306 M-98,-256 L-74,-252 M-98,-244 L-76,-242 M98,-256 L74,-252 M98,-244 L76,-242", 6, cor, "maoL")
    corpo = C("M-140,-70 C-112,-74 -98,-88 -92,-106 M-140,-118 C-114,-120 -100,-134 -96,-150 M-136,-30 C-110,-30 -96,-42 -92,-56 "
              "M140,-70 C112,-74 98,-88 92,-106 M140,-118 C114,-120 100,-134 96,-150 M136,-30 C110,-30 96,-42 92,-56 "
              "M-60,-206 L-56,-186 M60,-206 L56,-186", 8, cor, "maoL")
    return '<clipPath id="lt%s"><path d="%s"/></clipPath><g clip-path="url(#lt%s)">%s</g>' % (uid, CORPO, uid, corpo), cab


def manchas(cor, uid, seed=3):
    random.seed(seed)
    blobs = []
    for cx, cy, r in [(-90, -60, 46), (70, -140, 40), (110, -30, 30), (-40, -190, 22)]:
        pts = []
        for i in range(10):
            a = i / 10 * 2 * math.pi
            rr = r * (.75 + random.random() * .45)
            pts.append("%.1f,%.1f" % (cx + math.cos(a) * rr, cy + math.sin(a) * rr))
        blobs.append("M" + " L".join(pts) + "Z")
    return '<clipPath id="mc%s"><path d="%s"/></clipPath><g clip-path="url(#mc%s)">%s</g>' % (uid, CORPO, uid, P(" ".join(blobs), cor))


# ------------------------------------------------------------------ ornamentos de tarot (fora do gato)
def raios(cx, cy, r0, r1, passo=6, cor=LINHA, op=.45, longo=1.18):
    s = []
    a = 0.0
    while a < 360:
        t = math.radians(a)
        rr = r1 * (longo if int(round(a / passo)) % 3 == 0 else 1)
        s.append("M%.1f,%.1f L%.1f,%.1f" % (cx + math.cos(t) * r0, cy + math.sin(t) * r0, cx + math.cos(t) * rr, cy + math.sin(t) * rr))
        a += passo
    return '<g opacity="%g">%s</g>' % (op, C(" ".join(s), 1.3, cor, "maoL"))


def brilhos(lista, cor=LINHA):
    return '<g fill="%s">%s</g>' % (cor, "".join('<use href="#br0" transform="translate(%g %g) scale(%g)"/>' % t for t in lista))


def faixa(cx, cy, texto, numeral, cor="#F4E9D5", tinta=LINHA, w=250):
    """Faixa de pergaminho com o nome, como o titulo de uma carta."""
    s = ['<g transform="translate(%g %g)">' % (cx, cy)]
    for lado in (-1, 1):
        x0 = lado * (w - 30)
        s.append('<path d="M%g,-12 L%g,-12 L%g,12 L%g,36 L%g,36 Z" fill="%s" stroke="%s" stroke-width="2.4" stroke-linejoin="round" filter="url(#mao)"/>'
                 % (x0, x0 + lado * 70, x0 + lado * 52, x0 + lado * 70, x0, "#E2CFAE", tinta))
    s.append('<path d="M-%g,-28 C-%g,-34 %g,-34 %g,-28 L%g,28 C%g,22 -%g,22 -%g,28 Z" fill="%s" stroke="%s" stroke-width="2.6" stroke-linejoin="round" filter="url(#mao)"/>'
             % (w, w / 2, w / 2, w, w, w / 2, w / 2, w, cor, tinta))
    s.append('<text y="11" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="30" letter-spacing="6" fill="%s">%s</text>' % (tinta, texto))
    s.append('<text y="-46" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="20" letter-spacing="4" fill="%s" opacity=".75">%s</text>' % (tinta, numeral))
    s.append('</g>')
    return "".join(s)


def pagina(nome, corpo, fundo="#F1E6D2"):
    css = ('*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1080px}'
           '.peca{position:relative;width:1080px;height:1080px;overflow:hidden;background:radial-gradient(ellipse 70%% 60%% at 50%% 42%%,#F8EFDD 0%%,%s 60%%,#E6D6BA 100%%)}'
           '.peca::before,.peca::after{content:"";position:absolute;inset:0;pointer-events:none;background-size:1080px 1440px;z-index:5}'
           '.peca::before{background-image:var(--grao-neg);mix-blend-mode:multiply;opacity:.75}'
           '.peca::after{background-image:var(--grao-pos);mix-blend-mode:plus-lighter;opacity:.5}'
           '.peca>svg{position:absolute;left:0;top:0}') % fundo
    return ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>%s</title>\n<!--ACERVO-->\n<style>%s</style></head><body><div class="peca">'
            '<svg width="1080" height="1080" viewBox="0 0 1080 1080"><defs>%s</defs>%s</svg></div></body></html>') % (nome, css, DEFS, corpo)


def poe(svg, x, y, k):
    return '<g transform="translate(%g %g) scale(%g)">%s</g>' % (x, y, k, svg)


# ================================================================== 1 · O LEITOR (frajola)
def f1():
    pal = dict(corpo="#2B2427", peito="#FBF6EC", patas="#FBF6EC", focinho="#FBF6EC", iris="#C9D86A", orelha="#E79AA3", bigode="#8A7F84", ponta="#FBF6EC", hachura="#8A7F84")
    g = gato(pal, olho="redondo", cauda="frente", olhar=(0, 2), uid="a")
    livro = ('<g transform="translate(-186 4)">' +
             P("M-4,-4 L-84,8 L-92,-4 L-4,-16Z M4,-4 L84,8 L92,-4 L4,-16Z", "#E2CFAE") +
             P("M0,-10 C-24,-24 -60,-26 -88,-14 L-80,-48 C-56,-58 -24,-56 0,-44Z", "#FBF6EC") +
             P("M0,-10 C24,-24 60,-26 88,-14 L80,-48 C56,-58 24,-56 0,-44Z", "#FBF6EC") +
             C("M0,-10 C-24,-24 -60,-26 -88,-14 L-80,-48 C-56,-58 -24,-56 0,-44Z M0,-10 C24,-24 60,-26 88,-14 L80,-48 C56,-58 24,-56 0,-44Z M-88,-14 L-92,-4 L-4,-16 M88,-14 L92,-4 L4,-16 M0,-10 L0,-44", 2.4) +
             C("M-70,-26 C-52,-34 -30,-34 -14,-28 M-68,-36 C-50,-44 -30,-43 -14,-38 M14,-28 C30,-34 52,-34 70,-26 M14,-38 C30,-43 50,-44 68,-36", 1.3, LINHA, "maoL", 'opacity=".55"') +
             P("M-3,-12 L3,-12 L3,14 L0,9 L-3,14Z", "#C8324F") + '</g>')
    cena = (raios(540, 494, 196, 250) + C("M540,286 m-190,0 a190,190 0 1,0 380,0 a190,190 0 1,0 -380,0", 1.4, LINHA, "maoL", 'transform="translate(0 208)" opacity=".5"') +
            '<circle cx="540" cy="494" r="180" fill="#F2D27E" opacity=".35" filter="url(#aguada)"/>' +
            brilhos([(250, 230, 1.1), (840, 260, .9), (200, 560, .7), (880, 600, .8), (300, 380, .5), (790, 400, .5)]) +
            '<path d="M150,840 C380,826 700,826 930,840" stroke="%s" stroke-width="2" fill="none" filter="url(#maoL)"/>' % LINHA +
            poe(livro + g, 540, 836, 1.22) + faixa(540, 950, "O LEITOR", "0"))
    return pagina("Mascote · O Leitor", cena)


# ================================================================== 2 · A LUA (rajado cinza dormindo sentado na lua)
def f2():
    lt_corpo, lt_cab = listras_tabby("#5D5A63", "b")
    pal = dict(corpo="#ABA8B4", peito="#F4F1EA", patas="#F4F1EA", focinho="#F4F1EA", orelha="#EFA2AE", cabeca_padrao=lt_cab, listra="#5D5A63")
    g = gato(pal, padrao=lt_corpo, olho="dormindo", cauda="frente", uid="b")
    LUA = "M206,560 C150,900 930,900 874,560 C840,800 240,800 206,560Z"
    lua = ('<path d="%s" fill="#F2D27E"/><path d="%s" fill="#EFC768" filter="url(#aguada)"/>' % (LUA, LUA) +
           '<path d="%s" fill="none" stroke="%s" stroke-width="3" filter="url(#mao)"/>' % (LUA, LINHA) +
           '<circle cx="470" cy="842" r="9" fill="#D9B46A" opacity=".6"/><circle cx="640" cy="852" r="6" fill="#D9B46A" opacity=".6"/>')
    fios = C("M330,110 L330,250 M760,90 L760,200 M560,80 L560,150", 1.4, LINHA, "maoL", 'opacity=".6"') + brilhos([(330, 262, 1.3), (760, 212, 1.1), (560, 162, .8)], "#E3B04B") + brilhos([(330, 262, 1.3), (760, 212, 1.1), (560, 162, .8)].__class__([(330, 262, .5), (760, 212, .45), (560, 162, .35)]), LINHA)
    cena = (fios + brilhos([(170, 420, .8), (900, 420, .7), (150, 700, .5), (930, 690, .55)]) +
            C("M960,330 l14,0 l-14,18 l14,0 M990,290 l10,0 l-10,13 l10,0", 2.4) +
            lua + poe(g, 540, 788, 1.08) + faixa(540, 960, "A LUA", "XVIII"))
    return pagina("Mascote · A Lua", cena)


# ================================================================== 3 · O SOL (laranja feliz acenando)
def f3():
    lt_corpo, lt_cab = listras_tabby("#C9662E", "c")
    pal = dict(corpo="#EFA25A", peito="#FCF3E4", patas="#FCF3E4", focinho="#FCF3E4", orelha="#F3A2A8", cabeca_padrao=lt_cab, listra="#C9662E")
    g = gato(pal, padrao=lt_corpo, olho="feliz", cauda="cima", pata="erguida", boca="aberta", uid="c")
    sol = ('<circle cx="540" cy="470" r="200" fill="#F6C65B" filter="url(#aguada)"/>' + C("M340,470 a200,200 0 1,0 400,0 a200,200 0 1,0 -400,0", 3) +
           raios(540, 470, 214, 270, 7.5, "#D98E2E", .9, 1.15))
    girassois = ""
    for x, y, k in ((190, 740, 1), (890, 720, 1.1)):
        petalas = "".join('<ellipse cx="0" cy="-34" rx="11" ry="24" transform="rotate(%d)" fill="#F2B544" stroke="%s" stroke-width="2"/>' % (a, LINHA) for a in range(0, 360, 30))
        girassois += ('<g transform="translate(%g %g) scale(%g)">' % (x, y, k) + C("M0,30 C6,70 -4,110 2,140", 4, "#4E7A3E") +
                      '<path d="M2,96 C30,72 64,76 70,88 C50,106 24,108 2,96Z" fill="#78B27A" stroke="%s" stroke-width="2"/>' % LINHA +
                      '<g filter="url(#mao)">' + petalas + '<circle r="22" fill="#7A4E32" stroke="%s" stroke-width="2.4"/></g></g>' % LINHA)
    cena = sol + girassois + brilhos([(220, 280, .9), (870, 300, .8), (140, 520, .6)]) + poe(g, 540, 846, 1.2) + faixa(540, 958, "O SOL", "XIX")
    return pagina("Mascote · O Sol", cena)


# ================================================================== 4 · A ESTRELA (malhado alcancando a estrela)
def f4():
    pal = dict(corpo="#FBF6EC", patas="#FBF6EC", orelha="#F3A2A8", iris="#7FB7D8",
               cabeca_padrao='<path d="M-110,-360 C-60,-350 -20,-320 -10,-290 C-30,-276 -60,-280 -110,-300Z" fill="#2B2427" filter="url(#aguada)"/>'
                             '<path d="M40,-200 C60,-214 96,-214 110,-196 L110,-170 L40,-170Z" fill="#E59A54" filter="url(#aguada)"/>')
    g = gato(pal, padrao=manchas("#2B2427", "d") + manchas("#E59A54", "d2", seed=9), olho="redondo", cauda="cima", pata="erguida", olhar=(4, -6), uid="d")
    estrela = ('<g transform="translate(650 360)">' + C("M0,-380 L0,-40", 1.6) +
               '<path d="M0,-44 L12,-12 L46,-12 L18,8 L28,40 L0,20 L-28,40 L-18,8 L-46,-12 L-12,-12Z" fill="#F2C94C" stroke="%s" stroke-width="2.6" stroke-linejoin="round" filter="url(#mao)"/>' % LINHA +
               '<circle r="70" fill="#F2D27E" opacity=".4" filter="url(#brilho)"/></g>')
    cena = (raios(650, 360, 60, 104, 10, LINHA, .4) + estrela + brilhos([(240, 260, 1.0), (180, 420, .6), (900, 480, .7), (860, 160, .5), (330, 140, .5)]) +
            '<path d="M170,846 C380,832 700,832 910,846" stroke="%s" stroke-width="2" fill="none" filter="url(#maoL)"/>' % LINHA +
            poe(g, 520, 842, 1.22) + faixa(540, 956, "A ESTRELA", "XVII"))
    return pagina("Mascote · A Estrela", cena)


# ================================================================== 5 · A LANTERNA (siames cor de pudim sobre os livros)
def f5():
    CARAMELO = "#7B4A2E"
    pal = dict(corpo="#F4E4C4", patas=CARAMELO, orelha_fora=CARAMELO, orelha="#C98A6A", iris="#79B4E0", ponta=CARAMELO,
               mascara='<g filter="url(#borrao)"><path d="M0,-284 C32,-284 54,-262 56,-238 C58,-214 32,-198 0,-198 C-32,-198 -58,-214 -56,-238 C-54,-262 -32,-284 0,-284Z" fill="#A87A58" opacity=".85"/></g>', bigode="#F4E4C4", nariz="#4A2A1A")
    g = gato(pal, olho="redondo", cauda="frente", uid="e")
    livros = ""
    for i, (w, cor, dx) in enumerate([(300, "#4F67C9", 0), (270, "#C8324F", 14), (240, "#78B27A", -10)]):
        y = -i * 46
        livros += (P("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (-w / 2 + dx, y, w / 2 + dx, y, w / 2 + dx, y - 44, -w / 2 + dx, y - 44), cor) +
                   P("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (w / 2 + dx - 26, y - 6, w / 2 + dx - 4, y - 6, w / 2 + dx - 4, y - 38, w / 2 + dx - 26, y - 38), "#FBF6EC") +
                   C("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (-w / 2 + dx, y, w / 2 + dx, y, w / 2 + dx, y - 44, -w / 2 + dx, y - 44), 2.6) +
                   C("M%g,%g L%g,%g M%g,%g L%g,%g" % (-w / 2 + dx + 24, y - 10, -w / 2 + dx + 24, y - 34, -w / 2 + dx + 34, y - 10, -w / 2 + dx + 34, y - 34), 2, "#F2C94C"))
    lanterna = ('<g transform="translate(300 820)">' + '<circle r="90" fill="#FFD267" opacity=".45" filter="url(#brilho)"/>' +
                C("M-16,-70 C-16,-100 16,-100 16,-70 M-24,-70 L24,-70", 2.4) + P("M-26,-70 L26,-70 L32,30 L-32,30Z", "#F6D27A") +
                C("M-26,-70 L26,-70 L32,30 L-32,30Z M0,-70 L0,30 M-29,-20 L29,-20", 2.4) +
                '<path d="M0,-44 L6,-28 L22,-28 L9,-18 L14,-2 L0,-12 L-14,-2 L-9,-18 L-22,-28 L-6,-28Z" fill="#FFF3C6"/>' +
                P("M-36,30 L36,30 L36,42 L-36,42Z", "#7B4A2E") + C("M-36,30 L36,30 L36,42 L-36,42Z", 2.4) + '</g>')
    cena = ('<path d="M170,864 C380,850 700,850 910,864" stroke="%s" stroke-width="2" fill="none" filter="url(#maoL)"/>' % LINHA +
            lanterna + raios(540, 420, 170, 220, 7.5, LINHA, .35) + brilhos([(820, 240, 1.0), (880, 420, .6), (200, 300, .6), (760, 150, .45)]) +
            poe(livros, 540, 862, 1.15) + poe(g, 540, 862 - 138 * 1.15, 1.08) + faixa(540, 962, "A LANTERNA", "IX"))
    return pagina("Mascote · A Lanterna", cena)


FOF = {1: ("fofo1_leitor", f1), 2: ("fofo2_lua", f2), 3: ("fofo3_sol", f3), 4: ("fofo4_estrela", f4), 5: ("fofo5_lanterna", f5)}

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    qual = [int(a) for a in sys.argv[1:]] or list(FOF)
    saida = os.path.join(os.path.dirname(AQUI), "saida")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1080})
        for k in qual:
            nome, f = FOF[k]
            html = f().replace("<!--ACERVO-->", montar.ACERVO_CSS)
            arq = os.path.join(saida, nome + ".final.html")
            open(arq, "w", encoding="utf-8").write(html)
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(900)
            pg.screenshot(path=os.path.join(saida, nome + ".png"))
            print(nome)
        b.close()
