# -*- coding: utf-8 -*-
"""DIVULGACAO da Gatoteca Entrelinhas: post «A roda dos gatos» (plano de 13/11/2026).

A cena: o encontro do clube acontecendo. O chao e um LIVRO ABERTO GIGANTE (paginas creme com linhas
impressas, sem texto legivel), a lombada correndo de lado a lado la no fundo; os gatos sentados em roda
em cima da pagina, cada um um tipo de leitor (o frajola le em voz alta, o laranja discorda, o cinza de
oculos anota, a tricolor abraca o livro emocionada, o pequeno dorme em cima de uma pilha). Na frente,
virada para quem olha, a ALMOFADA VAZIA com um cafe esperando. Atras, a Gatoteca: estante na paleta,
placa com o nome, lustre com cone de luz. Papel de papel.py em tudo.

uso: py divulga_post.py            -> saida/divulga_post.png (1080x1350) + saida/divulga_status.png
     py divulga_post.py --zoom     -> tambem recortes em 2x para conferir rostos, maos, texto e seta
     py divulga_post.py --final    -> alta 2160x2700 + copia para a pasta do plano + SVGs das figuras novas
"""
import os, sys, math, random, base64, shutil
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "mascote"))
import montar
from papel import papel
import gato_banco as G
import gato_banco2 as G2
from gato_banco import Pose, sentado, sentado_barriga, membro, rabo, elipse, amostrar, olho_brilho, L_, coracao, TINTA, PRETO, BRANCO
from gato_banco2 import LARANJA, CINZA, braco, papel_pena_tinteiro, pena
from felpudo import pelo, desenha, caminho
from shapely.geometry import box, Point
from shapely.ops import unary_union
from shapely import affinity
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[2]  # raiz do repositório

D = str(_REPO / 'gatoteca/artes')
DESTINO = os.path.join(D, "Divulgação do clube - post e foto de perfil")
SVG_CANVA = os.path.join(D, "Mascote - banco de poses", "svg (para o Canva)")
SAIDA = os.path.join(AQUI, "saida")

W = 1080
JADE, JADE_E, ROSA, ROSA_C, NOITE, AMEIXA, PEROLA, OURO, VINHO = (
    "#5F857C", "#3F665E", "#C799AA", "#E6C4D0", "#30323C", "#624956", "#F1E3E6", "#D9B36A", "#6E1F2E")
CONTORNO = "#2A1A22"
MADEIRA, MADEIRA_C, FUNDO_EST = "#4A3340", "#6A4A58", "#22171E"
PAGINA = "#F1E6DC"          # creme rosado (nunca amarelo)
TINTA_LINHA = "#8C7A80"
CARAMELO = dict(base="#C89A6A", escuro="#8E6440", medio="#B48456", claro="#EBCDA6", borda="#6E4A2C")
K = 1                        # resolucao das texturas (2 na versao alta)


def b64(c):
    return "data:image/png;base64," + base64.b64encode(open(c, "rb").read()).decode()


def tex(w, h, cor, seed, **kw):
    kw.setdefault("borda", .0)
    return b64(papel(int(w * K), int(h * K), cor, seed, **kw))


_uid = [0]


def uid(p="u"):
    _uid[0] += 1
    return "%s%d" % (p, _uid[0])


def com_papel(d, cor, seed, bbox, forca=1.6, fibras=2.4, pintas=.6, relevo=.26, borda=.0, stroke=None, sw=3, extra=""):
    """Forma (path d) preenchida com papel texturizado da cor dada (+ contorno opcional)."""
    x0, y0, x1, y1 = bbox
    i = uid("cp")
    s = '<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)">' % (i, d, i)
    s += '<image href="%s" x="%g" y="%g" width="%g" height="%g" preserveAspectRatio="none"/>' % (
        tex(x1 - x0, y1 - y0, cor, seed, forca=forca, fibras=fibras, pintas=pintas, relevo=relevo, borda=borda), x0, y0, x1 - x0, y1 - y0)
    s += extra + '</g>'
    if stroke:
        s += '<path d="%s" fill="none" stroke="%s" stroke-width="%g" stroke-linejoin="round"/>' % (d, stroke, sw)
    return s


def clarear(cor, f):
    r, g, b = (int(cor[i:i + 2], 16) for i in (1, 3, 5))
    m = lambda c: int(c + (255 - c) * f) if f > 0 else int(c * (1 + f))
    return "#%02X%02X%02X" % (m(r), m(g), m(b))


# ================================================================== rostos novos (tipos de leitor)
_rosto_orig = G.rosto


def rosto_x(expr, olhar=(0, 0), vira=0, iris="#C9D86A", pe=PRETO):
    """Expressoes da roda: lendo_alto, discorda, emocionada, anotando. O resto cai no rosto do banco."""
    if expr not in ("lendo_alto", "discorda", "emocionada", "anotando"):
        return _rosto_orig(expr, olhar, vira, iris, pe)
    dx = vira
    ex = 41
    s, boca, bochecha = [], "w", .55
    if expr in ("lendo_alto", "anotando"):
        o = (0, 7)
        s.append(olho_brilho(-ex + dx, 0, olhar=o, iris=iris) + olho_brilho(ex + dx, 0, olhar=o, iris=iris))
        s.append('<path d="M%g,-18 L%g,-18 L%g,-4 L%g,-4Z M%g,-18 L%g,-18 L%g,-4 L%g,-4Z" fill="%s"/>' % (
            -60 + dx, -22 + dx, -22 + dx, -60 + dx, 22 + dx, 60 + dx, 60 + dx, 22 + dx, pe["base"]))
        s.append(L_("M%g,-4 L%g,-4 M%g,-4 L%g,-4" % (-58 + dx, -24 + dx, 24 + dx, 58 + dx), 3.5))
        boca = "aberta" if expr == "lendo_alto" else "w"
    elif expr == "discorda":
        o = olhar
        s.append(olho_brilho(-ex + dx, 2, olhar=o, iris=iris) + olho_brilho(ex + dx, 2, olhar=o, iris=iris))
        # palpebra de cima reta (olhar de «peraí»): metade de cima do olho tapada pela cor do pelo
        for xx in (-ex + dx, ex + dx):
            s.append('<path d="M%g,-22 L%g,-22 L%g,-6 L%g,-8Z" fill="%s"/>' % (xx - 22, xx + 22, xx + 22, xx - 22, pe["base"]))
            s.append(L_("M%g,-8 L%g,-6" % (xx - 20, xx + 20), 3.6))
        # sobrancelhas de quem discorda: uma erguida, outra baixa (cetica)
        s.append(L_("M%g,-30 C%g,-42 %g,-44 %g,-38" % (-60 + dx, -50 + dx, -34 + dx, -24 + dx), 5.5, "#5A2A12"))
        s.append(L_("M%g,-24 L%g,-30" % (22 + dx, 60 + dx), 5.5, "#5A2A12"))
        boca, bochecha = "falando", .4
    elif expr == "emocionada":
        s.append(L_("M%g,-2 C%g,10 %g,10 %g,-2 M%g,-2 C%g,10 %g,10 %g,-2" % (-56 + dx, -50 + dx, -32 + dx, -26 + dx, 26 + dx, 32 + dx, 50 + dx, 56 + dx), 4.5))
        # lagrima de emocao, brilhando, no canto de um olho
        s.append('<path d="M%g,8 C%g,18 %g,26 %g,30 C%g,34 %g,34 %g,30 C%g,26 %g,18 %g,8Z" fill="#BFE6F7" stroke="%s" stroke-width="1.8"/>' % (
            -58 + dx, -60 + dx, -66 + dx, -66 + dx, -66 + dx, -56 + dx, -56 + dx, -56 + dx, -56 + dx, -58 + dx, TINTA))
        s.append('<circle cx="%g" cy="24" r="2.4" fill="#FFFFFF"/>' % (-63 + dx))
        boca, bochecha = "sorriso", .95
    if bochecha:
        s.append('<ellipse cx="%g" cy="32" rx="17" ry="10" fill="#F28C9A" opacity="%g" filter="url(#borrao)"/><ellipse cx="%g" cy="32" rx="17" ry="10" fill="#F28C9A" opacity="%g" filter="url(#borrao)"/>' % (-69 + dx, bochecha, 69 + dx, bochecha))
    s.append('<path d="M%g,16 L%g,16 C%g,22 %g,25 %g,26 C%g,25 %g,22 %g,16Z" fill="#F18E9B" stroke="%s" stroke-width="1.7"/>' % (-10 + dx, 10 + dx, 10 + dx, 3 + dx, dx, -3 + dx, -10 + dx, -10 + dx, TINTA))
    m = dx
    if boca == "w":
        s.append(L_("M%g,26 L%g,33 M%g,33 C%g,42 %g,42 %g,33 C%g,42 %g,42 %g,33" % (m, m, m - 15, m - 12, m - 3, m, m + 3, m + 12, m + 15), 2.8))
    elif boca == "aberta":
        s.append(L_("M%g,26 L%g,31" % (m, m), 2.6) + '<path d="M%g,32 C%g,50 %g,50 %g,32 C%g,36 %g,36 %g,32Z" fill="#B8475A" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % (m - 13, m - 10, m + 10, m + 13, m + 5, m - 5, m - 13, TINTA)
                 + '<path d="M%g,44 C%g,40 %g,40 %g,44 C%g,47 %g,47 %g,44Z" fill="#F07C8C"/>' % (m - 7, m - 3, m + 3, m + 7, m + 3, m - 3, m - 7))
    elif boca == "falando":   # boca aberta de lado, no meio de uma frase
        s.append(L_("M%g,26 L%g,31" % (m, m), 2.6) + '<path d="M%g,33 C%g,52 %g,54 %g,36 C%g,34 %g,32 %g,33Z" fill="#B8475A" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % (m - 12, m - 8, m + 14, m + 17, m + 8, m - 4, m - 12, TINTA))
    elif boca == "sorriso":
        s.append(L_("M%g,26 L%g,31 M%g,31 C%g,44 %g,44 %g,31" % (m, m, m - 14, m - 8, m + 8, m + 14), 2.8))
    s.append('<path d="M%g,22 L%g,10 M%g,30 L%g,30 M%g,38 L%g,52 M%g,22 L%g,10 M%g,30 L%g,30 M%g,38 L%g,52" fill="none" stroke="#FFFDF6" stroke-width="1.5" stroke-linecap="round" opacity=".85"/>' % (
        -80 + m, -160 + m, -82 + m, -162 + m, -78 + m, -152 + m, 80 + m, 160 + m, 82 + m, 162 + m, 78 + m, 152 + m))
    return "".join(s)


G.rosto = rosto_x


class PoseX(Pose):
    """Pose com cabeca de manchas (tricolor): manchas = [(poligono local, paleta)], orelhas_pal = (esq, dir)."""

    def cabeca(self, x, y, esc=1.0, rot=0, expr="neutro", orelhas="cima", olhar=(0, 0), vira=0, sobre_corpo=True,
               eric=False, recorte=None, acess=None, acess_tras=None, topo_acess=-160, mancha_testa=True, manchas=None, orelhas_pal=None):
        F = G.F
        k = 1.08
        cab = amostrar(F.CABECA, k=k, cy=-262, dy=262).buffer(4)
        oe = amostrar(F.ORELHA_E, k=k, cy=-262, dy=262)
        od = amostrar(F.ORELHA_D, k=k, cy=-262, dy=262)
        de = amostrar(F.DENTRO_E, k=k, cy=-262, dy=262)
        dd = amostrar(F.DENTRO_D, k=k, cy=-262, dy=262)
        ang = {"cima": (0, 0), "atras": (-42, 42), "lado": (0, 30)}[orelhas]
        oe, de = affinity.rotate(oe, ang[0], origin=(-64, -55)), affinity.rotate(de, ang[0], origin=(-64, -55))
        od, dd = affinity.rotate(od, ang[1], origin=(64, -55)), affinity.rotate(dd, ang[1], origin=(64, -55))
        focinho = affinity.translate(amostrar(F.FOCINHO, k=k, cy=-262, dy=262).buffer(8), vira * .8, 0)
        mancha = affinity.translate(amostrar("M-9,-306 L9,-306 L24,-246 L-24,-246 Z", k=k, cy=-262, dy=262), vira * .6, 0)
        brancos = unary_union([focinho, mancha]) if mancha_testa else focinho
        tf = lambda g: affinity.translate(affinity.scale(affinity.rotate(g, rot, origin=(0, 0)), esc, esc, origin=(0, 0)), x, y)
        self.polis += [tf(cab), tf(oe), tf(od)]
        sub = Pose(self.cod, "", "", "", centro=(0, 0))
        sub.seed = self.seed + 300
        sub.pe, sub.pb, sub.iris = self.pe, self.pb, self.iris
        self.seed += 11
        for a in (acess_tras or []):
            sub.svg(a)
        fluxo_cab = lambda a, b: (a - vira * .5, b + 26)
        pals = orelhas_pal or (self.pe, self.pe)
        for (o, d_, lado), pal in zip(((oe, de, -1), (od, dd, 1)), pals):
            sub.pe = pal
            sub.peca(o, lambda a, b, l=lado: (l * .25, -1), tufo=dict(passo=6), eric=eric)
            sub.svg('<path d="%s" fill="%s"/>' % (caminho(d_), G.ROSA))
            sub.svg(desenha(pelo(d_, 40, lambda a, b, l=lado: (l * .25, -1), lambda a, b, r: "#FFF6F0", L=(6, 11), larg=(1, 1.4), seed=sub.seed + lado)))
        sub.pe = self.pe
        sub.peca(cab, fluxo_cab, brancos=brancos, dens=.04, L=(7, 13), eric=eric,
                 tufo=dict(L=(9, 16), mistura=.45), pular=(lambda a, b, nx, ny: ny > .45) if sobre_corpo else None)
        for poly, pal in (manchas or []):
            m = poly.intersection(cab.buffer(-3)).difference(brancos.buffer(6))
            if not m.is_empty:
                sub.pe = pal
                sub.peca(m, fluxo_cab, dens=.045, L=(7, 12), tufo=dict(passo=6, L=(5, 9), mistura=.5))
        sub.pe = self.pe
        sub.svg(G.rosto(expr, olhar, vira, self.iris, self.pe))
        for a in (acess or []):
            sub.svg(a)
        self.camadas.append('<g transform="translate(%g %g) rotate(%g) scale(%g)">%s</g>' % (x, y, rot, esc, "".join(sub.camadas)))


# ================================================================== objetos
def livro_costas_vinho(cx, cy, w=210, h=132):
    """Livro aberto visto por tras (capa vinho para quem olha), friso e estrela de ouro."""
    c = lambda d, f, sw=2.6: '<path d="%s" fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round"/>' % (d, f, CONTORNO, sw)
    s = '<g transform="translate(%g %g)">' % (cx, cy)
    s += c("M%g,%g L0,%g L%g,%g" % (-w / 2 + 4, -h / 2 - 16, -h / 2 - 4, w / 2 - 4, -h / 2 - 16), "#F6EEE6", 2)
    s += c("M0,%g L%g,%g L%g,%g L0,%g Z" % (-h / 2 + 4, -w / 2, -h / 2 - 8, -w / 2, h / 2 - 8, h / 2 + 4), VINHO)
    s += c("M0,%g L%g,%g L%g,%g L0,%g Z" % (-h / 2 + 4, w / 2, -h / 2 - 8, w / 2, h / 2 - 8, h / 2 + 4), "#5A1826")
    for sx in (-1, 1):
        s += '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="3" opacity=".9"/>' % (sx * (w / 2 - 14), -h / 2 + 2, sx * (w / 2 - 14), h / 2 - 14, OURO)
    s += G.brilho(-w * .25, 6, 1.3, OURO) + G.brilho(w * .25, -4, .8, OURO)
    s += '<path d="M%g,%g L%g,%g" stroke="#FFFFFF" stroke-width="5" opacity=".14" stroke-linecap="round"/>' % (-w / 2 + 12, -h / 2 + 4, -w / 2 + 12, h / 2 - 20)
    return s + '</g>'


def livro_capa(cx, cy, w, h, cor, rot=0, seed=1):
    """Livro fechado de frente (capa), com frisos e um medalhao de ouro: o que a tricolor abraca."""
    s = '<g transform="translate(%g %g) rotate(%g)">' % (cx, cy, rot)
    s += '<path d="M%g,%g L%g,%g L%g,%g L%g,%g Z" fill="#F6EEE6" stroke="%s" stroke-width="2.6"/>' % (-w / 2 + 8, -h / 2 + 6, w / 2 + 6, -h / 2 + 6, w / 2 + 6, h / 2 + 6, -w / 2 + 8, h / 2 + 6, CONTORNO)
    d = "M%g,%g L%g,%g L%g,%g L%g,%g Z" % (-w / 2, -h / 2, w / 2, -h / 2, w / 2, h / 2, -w / 2, h / 2)
    s += com_papel(d, cor, seed, (-w / 2, -h / 2, w / 2, h / 2), stroke=CONTORNO, sw=2.8)
    s += '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="2.4" opacity=".7"/>' % (-w / 2 + 14, -h / 2, -w / 2 + 14, h / 2, CONTORNO)
    s += '<rect x="%g" y="%g" width="%g" height="%g" rx="4" fill="none" stroke="%s" stroke-width="2.4"/>' % (-w / 2 + 22, -h / 2 + 10, w - 32, h - 20, OURO)
    s += G.brilho(5, -h * .1, min(w, h) / 46, OURO)
    s += '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="2.6" stroke-linecap="round"/>' % (-w * .2, h * .2, w * .28, h * .2, OURO)
    return s + '</g>'


def livro_deitado(cx, base, w, h, cor, seed, dx=0, rot=0):
    """Livro deitado visto de frente (lombada para quem olha), em papel texturizado."""
    x0, y0 = cx - w / 2 + dx, base - h
    d = "M%g,%g L%g,%g C%g,%g %g,%g %g,%g L%g,%g C%g,%g %g,%g %g,%gZ" % (
        x0 + 6, y0, x0 + w - 6, y0, x0 + w + 3, y0 + h * .2, x0 + w + 3, y0 + h * .8, x0 + w - 6, y0 + h,
        x0 + 6, y0 + h, x0 - 3, y0 + h * .8, x0 - 3, y0 + h * .2, x0 + 6, y0)
    ex = ('<rect x="%g" y="%g" width="%g" height="%g" fill="#FFFFFF" opacity=".16"/>' % (x0 - 4, y0 + h * .12, w + 8, h * .18) +
          '<rect x="%g" y="%g" width="%g" height="%g" fill="#000000" opacity=".2"/>' % (x0 - 4, y0 + h * .74, w + 8, h * .3))
    s = '<g transform="rotate(%g %g %g)">' % (rot, cx, base - h / 2)
    s += com_papel(d, cor, seed, (x0 - 4, y0, x0 + w + 4, y0 + h), extra=ex, stroke=CONTORNO, sw=2.6)
    f = OURO if cor != OURO else VINHO
    for xf in (x0 + 18, x0 + 26, x0 + w - 26, x0 + w - 18):
        s += '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="2.6"/>' % (xf, y0 + 4, xf, y0 + h - 4, f)
    ew, eh = w * .32, h * .44
    s += '<rect x="%g" y="%g" width="%g" height="%g" rx="2" fill="#F4EAE0" stroke="%s" stroke-width="1.6"/>' % (x0 + w / 2 - ew / 2, y0 + h / 2 - eh / 2, ew, eh, CONTORNO)
    return s + '</g>'


def xicara(cx, cy, k=1.0, cor=VINHO, vapor=True):
    """Xicara de cafe no pires, um pouco de cima."""
    s = '<g transform="translate(%g %g) scale(%g)">' % (cx, cy, k)
    s += '<ellipse cx="0" cy="4" rx="40" ry="12" fill="%s" stroke="%s" stroke-width="2.6"/>' % (PEROLA, CONTORNO)
    s += '<ellipse cx="0" cy="2" rx="24" ry="6" fill="#D9C6CC"/>'
    s += '<path d="M22,-26 C40,-28 40,-6 20,-6" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round"/>' % CONTORNO
    s += '<path d="M22,-26 C40,-28 40,-6 20,-6" fill="none" stroke="%s" stroke-width="3.4" stroke-linecap="round"/>' % PEROLA
    s += '<path d="M-26,-34 L26,-34 C26,-8 18,2 0,2 C-18,2 -26,-8 -26,-34Z" fill="%s" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (PEROLA, CONTORNO)
    s += '<path d="M-25,-22 L25,-22 L24,-15 L-24,-15Z" fill="%s"/>' % cor
    s += '<ellipse cx="0" cy="-34" rx="26" ry="7" fill="#5A3324" stroke="%s" stroke-width="2.4"/>' % CONTORNO
    s += '<ellipse cx="-6" cy="-35" rx="9" ry="2.4" fill="#8A5A40"/>'
    s += '<path d="M-18,-30 L-18,-6" stroke="#FFFFFF" stroke-width="4" opacity=".55" stroke-linecap="round"/>'
    if vapor:
        s += '<path d="M-8,-48 C-16,-60 0,-68 -8,-82 M8,-46 C0,-60 16,-70 8,-88" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" opacity=".55"/>' % "#FFF6EE"
        s += '<path d="M-8,-48 C-16,-60 0,-68 -8,-82 M8,-46 C0,-60 16,-70 8,-88" fill="none" stroke="%s" stroke-width="1.4" stroke-linecap="round" opacity=".35"/>' % AMEIXA
    return s + '</g>'


def bolo(cx, cy, k=1.0):
    """Fatia de bolo no pratinho (pao de lo, recheio vinho, cobertura rosa, cereja)."""
    s = '<g transform="translate(%g %g) scale(%g)">' % (cx, cy, k)
    s += '<ellipse cx="0" cy="4" rx="58" ry="16" fill="%s" stroke="%s" stroke-width="2.6"/>' % (PEROLA, CONTORNO)
    s += '<ellipse cx="0" cy="3" rx="44" ry="10" fill="none" stroke="%s" stroke-width="1.6" opacity=".8"/>' % OURO
    # lado (as camadas) e topo
    s += '<path d="M-40,-2 L30,6 L30,-40 L-40,-50Z" fill="#E9CBA6" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % CONTORNO
    s += '<path d="M-40,-24 L30,-15 L30,-22 L-40,-31Z" fill="%s"/>' % VINHO
    s += '<path d="M-40,-36 L30,-28 L30,-31 L-40,-40Z" fill="#FFF4F0"/>'
    s += '<path d="M30,6 L52,-8 L52,-52 L30,-40Z" fill="#D8B48C" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % CONTORNO
    s += '<path d="M-40,-50 L30,-40 L52,-52 L-12,-64Z" fill="%s" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % (ROSA_C, CONTORNO)
    s += '<path d="M-40,-50 C-36,-42 -30,-46 -26,-40 C-20,-34 -14,-44 -8,-38" fill="none" stroke="%s" stroke-width="2"/>' % CONTORNO
    s += '<circle cx="14" cy="-62" r="9" fill="#B8243C" stroke="%s" stroke-width="2.2"/><path d="M14,-70 C16,-80 22,-84 28,-86" fill="none" stroke="%s" stroke-width="2.2"/>' % (CONTORNO, CONTORNO)
    s += '<circle cx="11" cy="-65" r="2.6" fill="#FFFFFF" opacity=".8"/>'
    return s + '</g>'


def almofada(cx, cy, k=1.0, seed=71):
    """A ALMOFADA VAZIA: rosa, estofada, cantos franzidos com borlas de ouro, capitone no meio, vivo de ouro."""
    s = '<g transform="translate(%g %g) scale(%g)">' % (cx, cy, k)
    # cantos (franzidos): tras (+-118,-46), frente (+-142,20); lados bojudos
    topo = ("M-118,-46 C-70,-66 70,-66 118,-46 C140,-28 150,-6 142,20 C80,40 -80,40 -142,20 C-150,-6 -140,-28 -118,-46Z")
    frente = ("M-142,20 C-80,40 80,40 142,20 C146,34 140,48 130,56 C70,74 -70,74 -130,56 C-140,48 -146,34 -142,20Z")
    s += com_papel(frente, clarear(ROSA, -.2), seed + 1, (-150, 10, 150, 78), stroke=CONTORNO, sw=3,
                   extra='<path d="M-150,50 C-60,72 60,72 150,50 L150,80 L-150,80Z" fill="#000" opacity=".2"/>')
    luz = ('<ellipse cx="-24" cy="-24" rx="96" ry="30" fill="#FFFFFF" opacity=".3" filter="url(#borrao)"/>'
           '<ellipse cx="0" cy="-8" rx="130" ry="40" fill="none" stroke="#FFFFFF" stroke-width="10" opacity=".08"/>'
           '<path d="M-150,14 C-80,36 80,36 150,14 L150,40 L-150,40Z" fill="#5A2A3C" opacity=".16"/>')
    s += com_papel(topo, ROSA, seed, (-152, -68, 152, 40), extra=luz, stroke=CONTORNO, sw=3)
    # vincos do capitone: do botao para os cantos franzidos
    for (x, y) in ((-118, -46), (118, -46), (-142, 20), (142, 20)):
        s += '<path d="M0,-12 Q%g,%g %g,%g" fill="none" stroke="%s" stroke-width="2.2" opacity=".42" stroke-linecap="round"/>' % (x * .5, y * .5 - 12 + (8 if y > 0 else -6), x * .9, y * .9 - 1, AMEIXA)
        s += '<path d="M%g,%g l%g,%g M%g,%g l%g,%g" stroke="%s" stroke-width="1.8" opacity=".5" stroke-linecap="round"/>' % (
            x, y, -x * .12, -6, x, y, -x * .1, 7, AMEIXA)
    s += '<ellipse cx="0" cy="-12" rx="10" ry="6.5" fill="%s" stroke="%s" stroke-width="2"/>' % (OURO, CONTORNO)
    s += '<ellipse cx="-3" cy="-14" rx="3" ry="1.6" fill="#FFF3C6"/>'
    # vivo de ouro na quina da frente
    s += '<path d="M-142,20 C-80,40 80,40 142,20" fill="none" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % OURO
    s += '<path d="M-142,20 C-80,40 80,40 142,20" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3 6" opacity=".6"/>' % CONTORNO
    # borlas nos quatro cantos
    for x, y, sc in ((-118, -46, .72), (118, -46, .72), (-142, 22, 1.0), (142, 22, 1.0)):
        b = '<g transform="translate(%g %g) scale(%g)">' % (x, y, sc)
        b += '<circle cx="0" cy="0" r="7.5" fill="%s" stroke="%s" stroke-width="2"/>' % (OURO, CONTORNO)
        b += '<path d="M-7,6 C-10,18 -13,30 -12,40 L12,40 C13,30 10,18 7,6Z" fill="%s" stroke="%s" stroke-width="2" stroke-linejoin="round"/>' % (OURO, CONTORNO)
        b += '<path d="M-7,16 L-9,38 M-3,16 L-3.5,39 M1,16 L1,39 M5,16 L6,38" stroke="#9C7A2E" stroke-width="1.4"/>'
        b += '<path d="M-8,12 L8,12" stroke="%s" stroke-width="3.2"/>' % VINHO
        s += b + '</g>'
    return s + '</g>'


def destaque_almofada(cx, cy):
    """Brilho quente embaixo e em volta da almofada vazia + estrelinhas: «este lugar e seu»."""
    s = '<ellipse cx="%g" cy="%g" rx="230" ry="80" fill="url(#poçaRosa)" style="mix-blend-mode:screen"/>' % (cx, cy + 4)
    for x, y, r, cor in ((cx - 182, cy - 62, 15, ROSA), (cx + 176, cy - 74, 11, OURO), (cx + 204, cy - 22, 8, ROSA), (cx - 206, cy - 10, 8, OURO)):
        s += estrela8(x, y, r + 3, CONTORNO) + estrela8(x, y, r, cor)
    return s


def balao(x, y, w, h, cauda, conteudo, seed=3):
    """Balao de fala de papel perola, contorno de tinta; cauda apontando para (cx, cy) relativo ao centro."""
    tx, ty = cauda
    rx, ry = w / 2, h / 2
    ang = math.atan2(ty, tx)
    a0, a1 = ang - .32, ang + .32
    p0 = (math.cos(a0) * rx * .92, math.sin(a0) * ry * .92)
    p1 = (math.cos(a1) * rx * .92, math.sin(a1) * ry * .92)
    d_ell = "M%g,0 A%g,%g 0 1 0 %g,0 A%g,%g 0 1 0 %g,0Z" % (-rx, rx, ry, rx, rx, ry, -rx)
    d_cauda = "M%g,%g Q%g,%g %g,%g Q%g,%g %g,%gZ" % (p0[0], p0[1], tx * .7, ty * .7 - 4, tx, ty, tx * .55, ty * .55 + 6, p1[0], p1[1])
    s = '<g transform="translate(%g %g)">' % (x, y)
    s += '<path d="%s" fill="%s" stroke="%s" stroke-width="7" stroke-linejoin="round"/>' % (d_ell + d_cauda, CONTORNO, CONTORNO)
    s += com_papel(d_ell + " " + d_cauda, "#F7EEF0", seed, (-rx - 4, -ry - 4, max(rx, tx) + 4, max(ry, ty) + 4), forca=1.1, relevo=.2)
    s += conteudo + '</g>'
    return s


def exclamacao(k=1.0):
    return ('<g transform="scale(%g)"><path d="M-9,-30 L9,-30 L5,10 L-5,10Z" fill="%s" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>'
            '<circle cx="0" cy="24" r="7.5" fill="%s" stroke="%s" stroke-width="2.4"/></g>') % (k, VINHO, CONTORNO, VINHO, CONTORNO)


def interrogacao(k=1.0):
    return ('<g transform="scale(%g)"><path d="M-16,-14 C-16,-34 16,-36 16,-16 C16,-4 4,0 2,8 L2,12" fill="none" stroke="%s" stroke-width="13" stroke-linecap="round"/>'
            '<path d="M-16,-14 C-16,-34 16,-36 16,-16 C16,-4 4,0 2,8 L2,12" fill="none" stroke="%s" stroke-width="7.5" stroke-linecap="round"/>'
            '<circle cx="2" cy="28" r="7.5" fill="%s" stroke="%s" stroke-width="2.4"/></g>') % (k, CONTORNO, JADE_E, JADE_E, CONTORNO)


def zs(x, y, k=1.0):
    """Tres Z maiusculos subindo (sono), em DM Serif."""
    s = ""
    for i, (dx, dy, t) in enumerate(((0, 0, 46), (32, -38, 36), (58, -70, 28))):
        s += '<text x="%g" y="%g" font-family="DM Serif Display" font-size="%g" fill="%s" stroke="%s" stroke-width="5" paint-order="stroke" stroke-linejoin="round" transform="rotate(-10 %g %g)">Z</text>' % (
            x + dx * k, y + dy * k, t * k, PEROLA, CONTORNO, x + dx * k, y + dy * k)
    return s


def lustre(cx, cy, k=1.0):
    """Lustre de latao: haste, dois bracos de cada lado com velas acesas e pingentes de cristal."""
    s = '<g transform="translate(%g %g) scale(%g)">' % (cx, cy, k)
    c = lambda d, f="none", w=3: '<path d="%s" fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round" stroke-linecap="round"/>' % (d, f, CONTORNO, w)
    # bracos (por tras do corpo)
    for sx in (-1, 1):
        for (ax, ay, alt) in ((118, -6, 0), (64, 10, 1)):
            d = "M0,22 C%g,%g %g,%g %g,%g" % (sx * 30, 52 + alt * 10, sx * (ax - 10), 46, sx * ax, ay + 4)
            s += '<path d="%s" fill="none" stroke="%s" stroke-width="10" stroke-linecap="round"/>' % (d, CONTORNO)
            s += '<path d="%s" fill="none" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % (d, OURO)
    s += c("M-4,-60 L-4,0 M4,-60 L4,0", "none", 2)
    s += '<rect x="-4" y="-60" width="8" height="64" fill="%s"/>' % OURO
    s += c("M-26,0 C-26,-14 26,-14 26,0 C26,22 12,38 0,44 C-12,38 -26,22 -26,0Z", OURO)
    s += '<path d="M-14,-4 C-12,10 -8,22 -2,32" fill="none" stroke="#FFF3C6" stroke-width="3" opacity=".7" stroke-linecap="round"/>'
    s += c("M-8,44 L8,44 L4,58 L-4,58Z", OURO, 2.4)
    # velas, chamas e o halo de cada uma
    for sx in (-1, 1):
        for (ax, ay) in ((118, -6), (64, 10)):
            x = sx * ax
            s += c("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (x - 14, ay, x + 14, ay, x + 9, ay + 12, x - 9, ay + 12), OURO, 2.4)
            s += c("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (x - 7, ay, x + 7, ay, x + 7, ay - 34, x - 7, ay - 34), "#FBF4EC", 2.2)
            s += '<circle cx="%g" cy="%g" r="26" fill="#FFD98A" opacity=".55" filter="url(#brilho)"/>' % (x, ay - 46)
            s += '<path d="M%g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g %g,%gZ" fill="url(#chama)" stroke="%s" stroke-width="1.6"/>' % (
                x, ay - 36, x - 9, ay - 42, x - 4, ay - 54, x, ay - 62, x + 4, ay - 54, x + 9, ay - 42, x, ay - 36, "#B8541E")
    # pingentes de cristal
    for x, y, L in ((-90, 30, 22), (-40, 44, 28), (40, 44, 28), (90, 30, 22), (0, 64, 30)):
        s += '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="1.4"/>' % (x, y, x, y + L * .5, OURO)
        s += c("M%g,%g L%g,%g L%g,%g L%g,%gZ" % (x, y + L * .5, x + 6, y + L * .5 + 9, x, y + L * .5 + 22, x - 6, y + L * .5 + 9), "#F4F1FA", 1.6)
        s += '<path d="M%g,%g L%g,%g" stroke="#FFFFFF" stroke-width="1.6" opacity=".9"/>' % (x - 2, y + L * .5 + 6, x - 2, y + L * .5 + 14)
    return s + '</g>'


def estrela8(x, y, r, cor, op=1):
    pts = []
    for i in range(16):
        a = math.pi * i / 8 - math.pi / 2
        rr = r if i % 2 == 0 else r * (.42 if i % 4 == 1 or i % 4 == 3 else .42)
        if i % 4 == 2:
            rr = r * .62
        pts.append("%g,%g" % (x + math.cos(a) * rr, y + math.sin(a) * rr))
    return '<path d="M%sZ" fill="%s" opacity="%g"/>' % (" L".join(pts), cor, op)


# ================================================================== a estante
CORES_LIVRO = [VINHO, JADE, ROSA, AMEIXA, OURO, NOITE, "#7C4A5A", JADE_E, "#A9707F", "#8A6E3A", "#E6D2C3", "#4B3A5E"]


def fileira(x0, x1, topo, base, seed, objetos=()):
    """Uma fileira de lombadas em pe, com pilhas deitadas e objetos (vaso, castical, ampulheta) nos vaos dados."""
    rnd = random.Random(seed)
    s, x = "", x0
    altura = base - topo
    obj = dict(objetos)
    while x < x1:
        o = next((k for k in obj if abs(k - x) < 40), None)
        if o is not None:
            tipo = obj.pop(o)
            larg, svg = objeto(tipo, x, base, altura, rnd)
            s += svg
            x += larg
            continue
        if rnd.random() < .09:   # pilha deitada
            w = rnd.randint(90, 130)
            y = base
            for k in range(rnd.randint(2, 4)):
                h = rnd.randint(16, 24)
                c = rnd.choice(CORES_LIVRO)
                ddx = rnd.randint(-6, 6)
                s += '<rect x="%d" y="%d" width="%d" height="%d" rx="3" fill="%s" stroke="%s" stroke-width="2.4"/>' % (x + ddx, y - h, w, h, c, CONTORNO)
                s += '<path d="M%d,%d V%d M%d,%d V%d" stroke="%s" stroke-width="2.4"/>' % (x + ddx + 12, y - h + 3, y - 3, x + ddx + w - 12, y - h + 3, y - 3, OURO if c != OURO else VINHO)
                s += '<rect x="%d" y="%d" width="%d" height="%d" fill="#000" opacity=".18"/>' % (x + ddx + 2, y - h * .35, w - 4, h * .3)
                y -= h
            x += w + 8
            continue
        w = rnd.randint(22, 44)
        h = rnd.randint(int(altura * .6), int(altura * .92))
        c = rnd.choice(CORES_LIVRO)
        inc = rnd.choice([0] * 9 + [-7, 8])
        g = '<g transform="rotate(%d %d %d)">' % (inc, x + (w if inc > 0 else 0), base) if inc else "<g>"
        g += '<rect x="%d" y="%d" width="%d" height="%d" rx="2.5" fill="%s" stroke="%s" stroke-width="2.4"/>' % (x, base - h, w, h, c, CONTORNO)
        g += '<rect x="%g" y="%d" width="%g" height="%d" fill="#000" opacity=".22"/>' % (x + w * .7, base - h + 2, w * .28, h - 4)
        g += '<rect x="%g" y="%d" width="%g" height="%d" fill="#FFF" opacity=".13"/>' % (x + w * .12, base - h + 2, w * .14, h - 4)
        friso = OURO if c not in (OURO, "#8A6E3A") else VINHO
        for f in rnd.choice([(.08, .12, .88, .92), (.1, .9), (.06, .1, .14, .86)]):
            g += '<path d="M%d,%g H%d" stroke="%s" stroke-width="2.2"/>' % (x + 3, base - h + h * f, x + w - 3, friso)
        if rnd.random() < .5:
            eh = rnd.randint(int(h * .18), int(h * .3))
            g += '<rect x="%g" y="%g" width="%g" height="%d" rx="1.5" fill="#F2E8E2" stroke="%s" stroke-width="1.6"/>' % (x + w * .2, base - h * .62, w * .6, eh, CONTORNO)
        s += g + "</g>"
        x += w + rnd.choice([0, 0, 1, 3])
    return s


def objeto(tipo, x, base, altura, rnd):
    c = lambda d, f, w=2.6: '<path d="%s" fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round" stroke-linecap="round"/>' % (d, f, CONTORNO, w)
    if tipo == "vaso":
        cx = x + 44
        s = ""
        for a, L, cor in ((-40, 70, JADE), (-12, 86, JADE_E), (18, 80, JADE), (44, 64, JADE_E), (-62, 50, "#7FA398")):
            t = math.radians(a - 90)
            ex, ey = cx + math.cos(t) * L, base - 56 + math.sin(t) * L
            s += c("M%g,%g Q%g,%g %g,%g Q%g,%g %g,%gZ" % (cx, base - 56, (cx + ex) / 2 - 14, (base - 56 + ey) / 2, ex, ey, (cx + ex) / 2 + 14, (base - 56 + ey) / 2, cx, base - 56), cor, 2)
        s += c("M%g,%g C%g,%g %g,%g %g,%g L%g,%g C%g,%g %g,%g %g,%gZ" % (cx - 22, base - 58, cx - 34, base - 30, cx - 26, base - 4, cx - 14, base, cx + 14, base,
                                                                      cx + 26, base - 4, cx + 34, base - 30, cx + 22, base - 58), ROSA)
        s += '<path d="M%g,%g C%g,%g %g,%g %g,%g" fill="none" stroke="%s" stroke-width="3"/>' % (cx - 28, base - 34, cx - 10, base - 28, cx + 10, base - 28, cx + 28, base - 34, OURO)
        s += estrela8(cx, base - 18, 7, OURO)
        return 92, s
    if tipo == "castical":
        cx = x + 34
        s = '<circle cx="%g" cy="%g" r="40" fill="#FFD98A" opacity=".5" filter="url(#brilho)"/>' % (cx, base - 108)
        s += c("M%g,%g L%g,%g L%g,%g L%g,%gZ" % (cx - 26, base, cx + 26, base, cx + 16, base - 10, cx - 16, base - 10), OURO)
        s += c("M%g,%g L%g,%g" % (cx, base - 10, cx, base - 52), "none", 6)
        s += '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="3"/>' % (cx, base - 10, cx, base - 52, OURO)
        s += c("M%g,%g C%g,%g %g,%g %g,%g" % (cx - 20, base - 52, cx - 16, base - 62, cx + 16, base - 62, cx + 20, base - 52), OURO)
        s += c("M%g,%g L%g,%g L%g,%g L%g,%gZ" % (cx - 7, base - 58, cx + 7, base - 58, cx + 7, base - 96, cx - 7, base - 96), "#FBF4EC", 2.2)
        s += '<path d="M%g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g %g,%gZ" fill="url(#chama)" stroke="#B8541E" stroke-width="1.4"/>' % (
            cx, base - 98, cx - 8, base - 104, cx - 4, base - 116, cx, base - 124, cx + 4, base - 116, cx + 8, base - 104, cx, base - 98)
        return 70, s
    if tipo == "ampulheta":
        cx = x + 30
        s = c("M%g,%g L%g,%g" % (cx - 24, base - 4, cx + 24, base - 4), "none", 7)
        s += c("M%g,%g L%g,%g" % (cx - 24, base - 84, cx + 24, base - 84), "none", 7)
        s += '<path d="M%g,%g L%g,%g M%g,%g L%g,%g" stroke="%s" stroke-width="4"/>' % (cx - 24, base - 4, cx + 24, base - 4, cx - 24, base - 84, cx + 24, base - 84, OURO)
        s += c("M%g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g %g,%g Z" % (cx - 16, base - 80, cx - 16, base - 54, cx + 16, base - 34, cx + 16, base - 8,
                                                              cx - 16, base - 8, cx - 16, base - 34, cx + 16, base - 54), "#EEF2F6", 2)
        s += '<path d="M%g,%g C%g,%g %g,%g %g,%g Z" fill="#E3B886"/>' % (cx - 12, base - 9, cx - 6, base - 22, cx + 6, base - 22, cx + 12, base - 9)
        return 62, s
    if tipo == "gatinho":   # estatueta de gato sentado, de ouro
        cx = x + 30
        s = c("M%g,%g C%g,%g %g,%g %g,%g L%g,%g L%g,%g L%g,%g L%g,%g C%g,%g %g,%g %g,%gZ" % (
            cx - 22, base, cx - 26, base - 30, cx - 14, base - 46, cx - 14, base - 58, cx - 16, base - 76, cx - 4, base - 66, cx + 4, base - 66,
            cx + 16, base - 76, cx + 14, base - 58, cx + 14, base - 46, cx + 26, base - 30), OURO, 2.2)
        s += '<path d="M%g,%g C%g,%g %g,%g %g,%g" fill="none" stroke="%s" stroke-width="2.4"/>' % (cx + 20, base - 4, cx + 40, base - 6, cx + 40, base - 30, cx + 30, base - 40, CONTORNO)
        s += '<path d="M%g,%g L%g,%g" stroke="#FFF3C6" stroke-width="3" opacity=".7" stroke-linecap="round"/>' % (cx - 12, base - 40, cx - 14, base - 12)
        return 66, s
    return 40, ""


def estante(H, dy, placa_y0, placa_y1, rodape):
    """Parede de estante embutida inteira: fundo escuro, montantes, prateleiras, fileiras e objetos."""
    s = '<rect x="0" y="0" width="%d" height="%d" fill="%s"/>' % (W, rodape, FUNDO_EST)
    s += '<image href="%s" x="0" y="0" width="%d" height="%d" preserveAspectRatio="none" opacity=".9"/>' % (
        tex(W, rodape, "#2C1F28", 51, forca=2.0, fibras=2.2, pintas=.4, relevo=.2), W, rodape)
    # vaos: (topo, base) de cada fileira; acima da placa, fileiras ate o alto
    fileiras = []
    y = placa_y0 - 12
    while y > -40:
        fileiras.append((y - 168, y))
        y -= 168 + 24
    fileiras += [(placa_y1 + 10, placa_y1 + 162), (placa_y1 + 186, rodape - 26)]
    objs = {0: [(150, "castical"), (820, "ampulheta")], 1: [(60, "vaso"), (930, "gatinho")], 2: [(400, "ampulheta")], 3: [(690, "vaso")]}
    n_cima = len(fileiras) - 2
    for i, (t, b) in enumerate(fileiras):
        k = i - n_cima if i >= n_cima else 2 + i
        s += fileira(-10, W + 10, t, b, 300 + i * 17, objetos=objs.get(k, ()))
        # sombra no fundo do vao (a prateleira de cima faz sombra)
        s += '<rect x="0" y="%d" width="%d" height="26" fill="#000" opacity=".35"/>' % (t, W)
        # a prateleira
        s += '<rect x="-10" y="%d" width="%d" height="24" fill="%s" stroke="%s" stroke-width="3"/>' % (b, W + 20, MADEIRA, CONTORNO)
        s += '<rect x="-10" y="%d" width="%d" height="5" fill="%s" opacity=".8"/>' % (b + 3, W + 20, MADEIRA_C)
        s += '<rect x="-10" y="%d" width="%d" height="18" fill="#000" opacity=".3"/>' % (b + 24, W + 20)
    # montantes verticais (tres vaos)
    for x in (-16, 352, 712, 1070):
        s += '<rect x="%d" y="-10" width="26" height="%d" fill="%s" stroke="%s" stroke-width="3"/>' % (x, rodape + 10, MADEIRA, CONTORNO)
        s += '<rect x="%d" y="-10" width="5" height="%d" fill="%s" opacity=".8"/>' % (x + 4, rodape + 10, MADEIRA_C)
        s += '<rect x="%d" y="-10" width="16" height="%d" fill="#000" opacity=".28"/>' % (x + 26, rodape + 10)
    # rodape
    s += '<rect x="-10" y="%d" width="%d" height="30" fill="%s" stroke="%s" stroke-width="3"/>' % (rodape - 26, W + 20, MADEIRA, CONTORNO)
    return s


def placa(y0, y1):
    """A placa da Gatoteca: jade-escuro em papel, moldura dupla de ouro, orelhinhas de gato no alto."""
    x0, x1 = 64, W - 64
    s = ""
    # orelhinhas de gato (atras da placa): lados curvos, ponta um pouco para fora, dentro rosa
    for sx in (-1, 1):
        bx = W / 2 + sx * (W / 2 - 64 - 92)
        d = "M%g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g %g,%gZ" % (
            bx - sx * 70, y0 + 16, bx - sx * 58, y0 - 40, bx + sx * 4, y0 - 84, bx + sx * 26, y0 - 92,
            bx + sx * 40, y0 - 60, bx + sx * 62, y0 - 20, bx + sx * 72, y0 + 16)
        s += com_papel(d, JADE_E, 81 + sx, (bx - 80, y0 - 96, bx + 80, y0 + 18), stroke=CONTORNO, sw=3.4)
        di = "M%g,%g C%g,%g %g,%g %g,%g C%g,%g %g,%g %g,%gZ" % (
            bx - sx * 38, y0 + 10, bx - sx * 30, y0 - 24, bx + sx * 6, y0 - 58, bx + sx * 20, y0 - 64,
            bx + sx * 28, y0 - 40, bx + sx * 36, y0 - 14, bx + sx * 42, y0 + 10)
        s += '<path d="%s" fill="%s" stroke="%s" stroke-width="2"/>' % (di, ROSA, CONTORNO)
        s += '<path d="M%g,%g l%g,-16 M%g,%g l%g,-20 M%g,%g l%g,-14" stroke="%s" stroke-width="2.2" stroke-linecap="round"/>' % (
            bx - sx * 14, y0 + 6, sx * 4, bx, y0 + 6, sx * 2, bx + sx * 14, y0 + 6, -sx * 2, PEROLA)
    d = "M%g,%g L%g,%g Q%g,%g %g,%g L%g,%g Q%g,%g %g,%g L%g,%g Q%g,%g %g,%g L%g,%g Q%g,%g %g,%gZ" % (
        x0 + 20, y0, x1 - 20, y0, x1, y0, x1, y0 + 20, x1, y1 - 20, x1, y1, x1 - 20, y1, x0 + 20, y1, x0, y1, x0, y1 - 20, x0, y0 + 20, x0, y0, x0 + 20, y0)
    luz = '<rect x="%g" y="%g" width="%g" height="%g" fill="url(#luzPlaca)"/>' % (x0, y0, x1 - x0, y1 - y0)
    s += '<rect x="%g" y="%g" width="%g" height="%g" rx="20" fill="#000" opacity=".4" filter="url(#esfuma)"/>' % (x0 + 6, y0 + 14, x1 - x0, y1 - y0)
    s += com_papel(d, JADE_E, 77, (x0, y0, x1, y1), forca=1.8, fibras=2.6, relevo=.3, extra=luz, stroke=CONTORNO, sw=4)
    s += '<rect x="%g" y="%g" width="%g" height="%g" rx="12" fill="none" stroke="%s" stroke-width="3.2"/>' % (x0 + 14, y0 + 14, x1 - x0 - 28, y1 - y0 - 28, OURO)
    s += '<rect x="%g" y="%g" width="%g" height="%g" rx="8" fill="none" stroke="%s" stroke-width="1.4" opacity=".8"/>' % (x0 + 24, y0 + 24, x1 - x0 - 48, y1 - y0 - 48, OURO)
    for x, y in ((x0 + 24, y0 + 24), (x1 - 24, y0 + 24), (x0 + 24, y1 - 24), (x1 - 24, y1 - 24)):
        s += estrela8(x, y, 13, ROSA)
    return s


# ================================================================== o livro gigante (o chao)
class Livro:
    def __init__(self, dy, H):
        self.dy, self.H = dy, H
        self.vpy = -250 + dy           # ponto de fuga
        self.yg = 805 + dy             # a dobra (lombada, de lado a lado)
        self.yf = 748 + dy             # borda de longe da pagina de tras
        self.meia = 470                # meia-largura da pagina na dobra

    def x(self, y, lado):
        f = (y - self.vpy) / (self.yg - self.vpy)
        return W / 2 + lado * self.meia * f

    def svg(self, chao_y):
        dy, H = self.dy, self.H
        yb = H + 40
        s = ""
        # chao de tacos (dos lados do livro, la atras)
        s += '<rect x="0" y="%d" width="%d" height="%d" fill="#3A2830"/>' % (chao_y, W, H - chao_y)
        s += '<image href="%s" x="0" y="%d" width="%d" height="%d" preserveAspectRatio="none" opacity=".85"/>' % (tex(W, H - chao_y, "#4A3238", 61, forca=1.8, relevo=.25), chao_y, W, H - chao_y)
        for i in range(-12, 13):
            xa = W / 2 + i * 60
            xb = W / 2 + i * 60 * (yb - self.vpy) / (chao_y - self.vpy)
            s += '<path d="M%g,%d L%g,%d" stroke="#1E1418" stroke-width="2" opacity=".45"/>' % (xa, chao_y, xb, yb)
        # capa (borda de pano ameixa, um pouco maior que as paginas) + sombra do livro no chao
        cf = self.yf - 13
        pts_capa = [(self.x(cf, -1) - 20, cf), (self.x(cf, 1) + 20, cf), (self.x(yb, 1) + 40, yb), (self.x(yb, -1) - 40, yb)]
        dc = "M" + " L".join("%g,%g" % p for p in pts_capa) + "Z"
        s += '<path d="%s" fill="#000" opacity=".5" filter="url(#esfuma)" transform="translate(0 8)"/>' % dc
        s += com_papel(dc, AMEIXA, 91, (min(p[0] for p in pts_capa), cf, max(p[0] for p in pts_capa), yb), forca=1.8, fibras=3, stroke=CONTORNO, sw=3)
        # cantoneiras de ouro nos cantos de longe
        for sx in (-1, 1):
            cx = self.x(cf, sx) + sx * 20
            s += '<path d="M%g,%g L%g,%g L%g,%gZ" fill="%s" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % (
                cx, cf, cx - sx * 46, cf, cx + sx * 6, cf + 34, OURO, CONTORNO)
        # paginas: a de tras (curta, em fuga) e a da frente (o chao da roda)
        d_tras = "M%g,%g L%g,%g L%g,%g L%g,%gZ" % (self.x(self.yf, -1), self.yf, self.x(self.yf, 1), self.yf, self.x(self.yg, 1), self.yg, self.x(self.yg, -1), self.yg)
        d_frente = "M%g,%g C%g,%g %g,%g %g,%g L%g,%g L%g,%g C%g,%g %g,%g %g,%gZ" % (
            self.x(self.yg, -1), self.yg, W * .3, self.yg + 14, W * .7, self.yg + 14, self.x(self.yg, 1), self.yg,
            self.x(yb, 1), yb, self.x(yb, -1), yb, W * .7, self.yg + 14, W * .3, self.yg + 14, self.x(self.yg, -1), self.yg)
        d_frente = "M%g,%g L%g,%g L%g,%g L%g,%gZ" % (self.x(self.yg, -1), self.yg, self.x(self.yg, 1), self.yg, self.x(yb, 1), yb, self.x(yb, -1), yb)
        # bordas de folhas (o miolo aparecendo nas laterais)
        for k in range(5, 0, -1):
            e = k * 3
            d = "M%g,%g L%g,%g L%g,%g L%g,%gZ" % (self.x(self.yf, -1) - e, self.yf + e * .3, self.x(self.yf, 1) + e, self.yf + e * .3, self.x(yb, 1) + e * 1.6, yb, self.x(yb, -1) - e * 1.6, yb)
            s += '<path d="%s" fill="%s" stroke="#B8A49C" stroke-width="1"/>' % (d, "#E6D8CE" if k % 2 else "#F3E9E0")
        lin_tras = self.linhas(self.yf + 10, self.yg - 8, 5, 2)
        s += com_papel(d_tras, PAGINA, 93, (self.x(self.yf, -1), self.yf, self.x(self.yf, 1), self.yg), forca=1.4, fibras=2.2, relevo=.22,
                       extra=lin_tras + '<rect x="0" y="%g" width="%d" height="%g" fill="url(#dobraTras)"/>' % (self.yf, W, self.yg - self.yf))
        self.fim_linhas = 1140 + dy
        lin = self.linhas(self.yg + 16, self.fim_linhas, 13, 3)
        s += com_papel(d_frente, PAGINA, 94, (self.x(yb, -1), self.yg, self.x(yb, 1), yb), forca=1.4, fibras=2.2, relevo=.22,
                       extra=lin + '<rect x="0" y="%g" width="%d" height="60" fill="url(#dobraFrente)"/>' % (self.yg, W))
        s += '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="2.4" opacity=".55"/>' % (self.x(self.yg, -1), self.yg, self.x(self.yg, 1), self.yg, CONTORNO)
        s += '<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d_tras, CONTORNO)
        s += '<path d="M%g,%g L%g,%g M%g,%g L%g,%g" stroke="%s" stroke-width="2.6"/>' % (self.x(self.yg, -1), self.yg, self.x(yb, -1), yb, self.x(self.yg, 1), self.yg, self.x(yb, 1), yb, CONTORNO)
        # no Status (alto) aparece a borda da frente do livro: o miolo de folhas, a capa e o chao
        if H > 1500:
            yn = H - 104
            s += '<rect x="-10" y="%g" width="%d" height="%g" fill="#2A1C24"/>' % (yn + 40, W + 20, H - yn)
            s += '<image href="%s" x="0" y="%g" width="%d" height="%g" preserveAspectRatio="none" opacity=".8"/>' % (tex(W, H - yn - 40, "#3A2830", 63, forca=1.8), yn + 40, W, H - yn - 40)
            for i in range(-14, 15):
                s += '<path d="M%g,%g L%g,%g" stroke="#120B10" stroke-width="2" opacity=".5"/>' % (W / 2 + i * 80, yn + 40, W / 2 + i * 104, H)
            dcapa = "M-10,%g C300,%g 780,%g 1090,%g L1090,%g C780,%g 300,%g -10,%gZ" % (yn + 20, yn + 30, yn + 30, yn + 20, yn + 56, yn + 66, yn + 66, yn + 56)
            s += com_papel(dcapa, AMEIXA, 95, (-10, yn + 14, 1090, yn + 70), forca=1.8, stroke=CONTORNO, sw=3)
            s += '<path d="M-10,%g C300,%g 780,%g 1090,%g" fill="none" stroke="#000" stroke-width="16" opacity=".35" filter="url(#borrao)"/>' % (yn + 74, yn + 84, yn + 84, yn + 74)
            dmiolo = "M-10,%g C300,%g 780,%g 1090,%g L1090,%g C780,%g 300,%g -10,%gZ" % (yn - 4, yn + 2, yn + 2, yn - 4, yn + 24, yn + 34, yn + 34, yn + 24)
            fol = "".join('<path d="M-10,%g C300,%g 780,%g 1090,%g" fill="none" stroke="#B9A79E" stroke-width="1.3"/>' % (yn + k, yn + 6 + k, yn + 6 + k, yn + k) for k in range(2, 26, 4))
            s += com_papel(dmiolo, "#EADDD2", 96, (-10, yn - 6, 1090, yn + 36), forca=1.2, extra=fol + '<rect x="-10" y="%g" width="1100" height="40" fill="url(#dobraTras)"/>' % (yn - 6), stroke=CONTORNO, sw=2.6)
            s += '<path d="M-10,%g C300,%g 780,%g 1090,%g" fill="none" stroke="%s" stroke-width="3"/>' % (yn - 4, yn + 2, yn + 2, yn - 4, CONTORNO)
        # fita marcadora vinho saindo da dobra, deitada na pagina
        fx = 140
        d = "M%g,%g C%g,%g %g,%g %g,%g L%g,%g C%g,%g %g,%g %g,%gZ" % (
            fx, self.yg - 2, fx - 10, self.yg + 120, fx + 30, self.yg + 260, fx - 30, yb,
            fx - 70, yb, fx - 10, self.yg + 250, fx - 34, self.yg + 120, fx - 20, self.yg - 2)
        s += '<path d="%s" fill="#000" opacity=".22" transform="translate(6 5)" filter="url(#borrao)"/>' % d
        s += com_papel(d, VINHO, 97, (fx - 80, self.yg - 4, fx + 40, yb), forca=1.5, stroke=CONTORNO, sw=2.4)
        return s

    def linhas(self, y0, y1, n, seed):
        """Linhas impressas (palavras como tracinhos), em perspectiva: mais juntas e finas perto da dobra."""
        rnd = random.Random(seed)
        s = []
        for i in range(n):
            t = (i + .5) / n
            y = y0 + (y1 - y0) * (t ** 1.25)
            f = (y - self.vpy) / (self.yg - self.vpy)
            xa, xb = self.x(y, -1) + 70 * f, self.x(y, 1) - 70 * f
            esp = 3.4 * f
            x = xa + (rnd.random() * 40 * f if i % 6 == 0 else 0)
            ultima = (i % 6 == 5)
            fim = xb - (rnd.random() * (xb - xa) * .5 if ultima else 0)
            while x < fim:
                L = rnd.uniform(18, 70) * f
                L = min(L, fim - x)
                s.append("M%.1f,%.1f h%.1f" % (x, y, L))
                x += L + 11 * f
            s.append(None if False else "")
            s_w = esp
        return '<path d="%s" stroke="%s" stroke-width="%g" stroke-linecap="round" opacity=".42"/>' % (" ".join(s), TINTA_LINHA, 3.2)


# ================================================================== os gatos da roda
def gato_frajola():
    """O FRAJOLA (o mascote): le em voz alta, livro de capa vinho, ondinhas de voz."""
    p = Pose("11", "lendo", "", "")
    p.seed = 5100
    sentado_barriga(p, cabeca=dict(rot=-4, expr="lendo_alto"), bracos=None)
    p.svg(livro_costas_vinho(0, -118, 214, 134))
    for lado in (-1, 1):
        membro(p, [(lado * 84, -184), (lado * 100, -150), (lado * 98, -122)], 22, 19)
        p.pata(lado * 98, -116, 22, 18, lado * 70, dedos=False)
    # ondinhas de voz saindo dos dois lados da boca
    for sx in (-1, 1):
        for i, r in enumerate((26, 44)):
            p.svg('<path d="M%g,%g A%g,%g 0 0 %d %g,%g" fill="none" stroke="%s" stroke-width="%g" stroke-linecap="round"/>' % (
                sx * (128 + i * 14), -232 - r * .6, r, r * 1.1, 1 if sx > 0 else 0, sx * (128 + i * 14), -232 + r * .6, VINHO, 6.5 - i * 1.5))
    return p


def gato_laranja():
    """O LARANJA: discorda, patinha erguida."""
    p = Pose("52", "discorda", "", "")
    p.seed = 5200
    p.pe, p.iris = LARANJA, "#C9D86A"
    sentado(p, cabeca=dict(expr="discorda", vira=8, olhar=(5, 0), rot=4))
    braco(p, 1, [(130, -200), (148, -262)], (150, -272), 14)
    return p


def gato_cinza():
    """O CINZA de oculos de ouro: anota com pena e tinteiro."""
    p = Pose("43", "anota", "", "")
    p.seed = 5300
    p.pe, p.iris = CINZA, "#8FC3E6"
    oculos = G2.oculos_redondos().replace(G2.OURO, OURO)
    sentado_barriga(p, cabeca=dict(expr="anotando", acess=[oculos], vira=-6), bracos=None, solas=True)
    p.svg(papel_pena_tinteiro((0, -112, -4), 0, 0, -190).replace("#2F4A8C", JADE_E))
    braco(p, 1, [(80, -150), (62, -112)], (60, -108), 60, sentado_ombro=(84, -182))
    membro(p, [(-84, -182), (-76, -150), (-50, -124)], 22, 19)
    p.svg(pena(-52, -126, -28, 1.0))
    p.pata(-48, -120, 22, 19, -60, dedos=False)
    return p


def gato_tricolor():
    """A TRICOLOR: abraca o livro, emocionada (olhos fechados, lagrima, bochechas)."""
    p = PoseX("12", "tricolor", "", "")
    p.seed = 5400
    p.pe, p.iris = LARANJA, "#C9D86A"
    sentado(p, rabo_cima=True, cabeca=None, patas=True)
    # manchas pretas no corpo (por cima do laranja, fora do peito)
    corpo = amostrar(G.F.CORPO).buffer(4)
    peito = amostrar(G.F.PEITO).buffer(10)
    pe_ant = p.pe
    p.pe = PRETO
    for bl in (elipse(-92, -120, 62, 96, 20), elipse(96, -40, 52, 40)):
        m = bl.intersection(corpo.buffer(-2)).difference(peito)
        if not m.is_empty:
            p.peca(m, lambda x, y: (x / 230, 1), tufo=dict(passo=6, L=(5, 9), mistura=.5))
    p.pe = pe_ant
    p.cabeca(0, -262, expr="emocionada", rot=-6, manchas=[(elipse(58, -40, 66, 60), PRETO)], orelhas_pal=(LARANJA, PRETO))
    p.svg(livro_capa(4, -128, 118, 150, JADE, rot=-8, seed=41))
    for lado in (-1, 1):
        membro(p, [(lado * 82, -184), (lado * 54, -150), (lado * 10, -132)], 22, 19)
        p.pata(lado * 4, -130, 22, 18, lado * -30, dedos=False)
    return p


def gato_dorminhoco():
    """O PEQUENO que nao leu: caramelo, enrolado dormindo."""
    p = Pose("03", "dorme", "", "")
    p.seed = 5500
    p.pe = CARAMELO
    corpo = amostrar("M-170,-130 C-170,-250 -60,-310 40,-300 C150,-290 200,-210 190,-120 C180,-30 100,0 0,0 C-100,0 -170,-40 -170,-130Z").buffer(3)
    p.peca(corpo, lambda x, y: (x - 10, y + 150), dens=.033)
    p.pata(-104, -44, 24, 14, -10)
    p.cabeca(-46, -118, esc=.92, rot=-12, expr="dormindo")
    rabo(p, [(176, -120), (176, -40), (110, -8), (0, -6), (-100, -16), (-158, -40)], 22, 16)
    return p


def colocar(p, x, y, s, espelho=False):
    sx = -s if espelho else s
    return '<g transform="translate(%g %g) scale(%g %g)">%s</g>' % (x, y, sx, s, "".join(p.camadas))


def sombra(x, y, rx, ry, cx_luz, forca=.42):
    """Sombra de contato + sombra projetada para fora da roda (a luz esta em cima do centro)."""
    dx = (x - cx_luz) * .18
    s = '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="#3B2030" opacity="%g" filter="url(#esfuma)"/>' % (x + dx, y + 6, rx * 1.15, ry * 1.2, forca * .55)
    s += '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="#2A1520" opacity="%g" filter="url(#borrao)"/>' % (x, y + 2, rx * .8, ry * .55, forca)
    return s


# ================================================================== a cena inteira
DEFS = '''
<radialGradient id="poça" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#FFE6CC" stop-opacity=".55"/><stop offset=".6" stop-color="#FFD9B8" stop-opacity=".2"/><stop offset="1" stop-color="#FFD9B8" stop-opacity="0"/></radialGradient>
<radialGradient id="halo" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#FFE7B8" stop-opacity=".9"/><stop offset=".35" stop-color="#F8C98E" stop-opacity=".38"/><stop offset="1" stop-color="#F8C98E" stop-opacity="0"/></radialGradient>
<radialGradient id="poçaRosa" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#FFD6E2" stop-opacity=".7"/><stop offset="1" stop-color="#FFD6E2" stop-opacity="0"/></radialGradient>
<linearGradient id="cone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE3B4" stop-opacity=".34"/><stop offset="1" stop-color="#FFE3B4" stop-opacity="0"/></linearGradient>
<linearGradient id="dobraFrente" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5A3A44" stop-opacity=".45"/><stop offset="1" stop-color="#5A3A44" stop-opacity="0"/></linearGradient>
<linearGradient id="dobraTras" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5A3A44" stop-opacity="0"/><stop offset=".6" stop-color="#5A3A44" stop-opacity=".1"/><stop offset="1" stop-color="#5A3A44" stop-opacity=".5"/></linearGradient>
<linearGradient id="luzPlaca" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".25"/><stop offset=".7" stop-color="#FFE3B4" stop-opacity=".0"/><stop offset="1" stop-color="#FFE3B4" stop-opacity=".22"/></linearGradient>
<filter id="coneBorrao" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="22"/></filter>
<radialGradient id="vinheta" cx="50%" cy="58%" r="75%"><stop offset=".5" stop-color="#1E1218" stop-opacity="0"/><stop offset="1" stop-color="#1E1218" stop-opacity=".62"/></radialGradient>
<linearGradient id="escuroAlto" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#140C11" stop-opacity=".55"/><stop offset="1" stop-color="#140C11" stop-opacity="0"/></linearGradient>
'''

TXT_SUB = "Clube de leitura gratuito no Recife"
TXT_RODA = ("A cada quinze dias, a gente senta em roda", "para conversar sobre a leitura.")
TXT_VEM = "Tem lugar pra você. Vem!"


def cena(H, dy):
    _uid[0] = 0
    placa_y0, placa_y1 = 96 + dy, 404 + dy
    rodape = 732 + dy
    lv = Livro(dy, H)
    cxr = W / 2
    s = estante(H, dy, placa_y0, placa_y1, rodape)
    s += '<rect x="0" y="0" width="%d" height="%d" fill="url(#escuroAlto)"/>' % (W, rodape)
    s += placa(placa_y0, placa_y1)
    s += lv.svg(rodape)
    # poca de luz na pagina, embaixo do lustre
    s += '<ellipse cx="%g" cy="%g" rx="560" ry="250" fill="url(#poça)" style="mix-blend-mode:screen"/>' % (cxr, 960 + dy)
    # --- posicoes da roda (base dos pes)
    pos = dict(frajola=(cxr, 898 + dy, .62), laranja=(326, 922 + dy, .62), cinza=(770, 918 + dy, .58),
               tricolor=(164, 1106 + dy, .70), dorme=(918, 1050 + dy, .40), almofada=(cxr, 1098 + dy, 1.0))
    # sombras
    s += sombra(*pos["frajola"][:2], 140, 26, cxr)
    s += sombra(*pos["laranja"][:2], 96, 22, cxr)
    s += sombra(*pos["cinza"][:2], 116, 24, cxr)
    s += sombra(*pos["tricolor"][:2], 104, 26, cxr)
    s += sombra(918, 1072 + dy, 120, 24, cxr)
    s += sombra(cxr, 1112 + dy, 150, 26, cxr, .38)
    s += sombra(540, 1004 + dy, 56, 14, cxr, .3)
    # fundo da roda: frajola, laranja, cinza (+ xicaras)
    s += xicara(196, 930 + dy, .6, JADE)
    s += xicara(912, 924 + dy, .58, ROSA)
    s += colocar(gato_frajola(), *pos["frajola"])
    s += colocar(gato_laranja(), *pos["laranja"])
    s += colocar(gato_cinza(), *pos["cinza"])
    s += bolo(540, 1000 + dy, .9)
    # frente da roda: tricolor, a pilha com o dorminhoco, a almofada vazia e o cafe dela
    s += colocar(gato_tricolor(), *pos["tricolor"])
    s += livro_deitado(918, 1072 + dy, 200, 40, JADE, 11, dx=0, rot=0)
    s += livro_deitado(918, 1034 + dy, 176, 36, VINHO, 12, dx=6, rot=-1.5)
    s += colocar(gato_dorminhoco(), 922, 1002 + dy, .40)
    s += destaque_almofada(cxr, 1080 + dy)
    s += almofada(cxr, 1078 + dy, 1.0)
    s += xicara(354, 1104 + dy, .74, VINHO)
    # baloes (so icone)
    s += balao(196, 640 + dy, 92, 82, (44, 50), exclamacao(1.0), 31)
    s += balao(80, 830 + dy, 84, 76, (40, 54), coracao(0, 4, 1.9, "#D9506A", CONTORNO), 32)
    s += zs(958, 920 + dy, 1.0)
    # cone de luz do lustre e halo
    ly = placa_y1 + 74
    s += '<path d="M%g,%g L%g,%g L%g,%g L%g,%gZ" fill="url(#cone)" filter="url(#coneBorrao)" style="mix-blend-mode:screen"/>' % (cxr - 60, ly + 40, cxr + 60, ly + 40, cxr + 470, 1060 + dy, cxr - 470, 1060 + dy)
    s += '<ellipse cx="%g" cy="%g" rx="330" ry="250" fill="url(#halo)" style="mix-blend-mode:screen"/>' % (cxr, ly - 10)
    # lustre pendurado num gancho embaixo da placa
    s += '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="6" stroke-dasharray="7 4"/>' % (cxr, placa_y1, cxr, ly - 60, CONTORNO)
    s += '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="3" stroke-dasharray="7 4"/>' % (cxr, placa_y1, cxr, ly - 60, OURO)
    s += '<circle cx="%g" cy="%g" r="9" fill="none" stroke="%s" stroke-width="4"/>' % (cxr, placa_y1 + 4, OURO)
    s += lustre(cxr, ly, .95)
    # vinheta (por baixo do texto)
    s += '<rect width="%d" height="%d" fill="url(#vinheta)"/>' % (W, H)
    # textos da placa
    s += ('<text x="%g" y="%g" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="40" letter-spacing="16" fill="%s">GATOTECA</text>' % (cxr + 8, placa_y0 + 82, OURO))
    s += ('<text x="%g" y="%g" text-anchor="middle" font-family="DM Serif Display" font-size="148" fill="#1A1016" opacity=".55" filter="url(#borrao)">Entrelinhas</text>' % (cxr + 4, placa_y0 + 222))
    s += ('<text x="%g" y="%g" text-anchor="middle" font-family="DM Serif Display" font-size="148" fill="%s" stroke="%s" stroke-width="7" paint-order="stroke" stroke-linejoin="round">Entrelinhas</text>' % (cxr, placa_y0 + 214, ROSA, AMEIXA))
    s += ('<text x="%g" y="%g" text-anchor="middle" font-family="Cormorant" font-weight="700" font-size="44" fill="%s">%s</text>' % (cxr, placa_y0 + 271, PEROLA, TXT_SUB))
    # o pe: frase da roda + convite + seta ate a almofada
    yt = 1192 + dy
    for i, t in enumerate(TXT_RODA):
        s += '<text x="%g" y="%g" text-anchor="middle" font-family="Cormorant" font-weight="700" font-size="40" fill="%s">%s</text>' % (cxr, yt + i * 44, NOITE, t)
    s += '<text x="%g" y="%g" text-anchor="middle" font-family="DM Serif Display" font-size="66" fill="%s">%s</text>' % (cxr - 22, yt + 124, VINHO, TXT_VEM)
    s += seta(908, yt + 104, 690, 1088 + dy)
    return s


def seta(x0, y0, x1, y1):
    """Seta de canetao vinho, a mao, do «Vem!» ate a almofada."""
    d = "M%g,%g C%g,%g %g,%g %g,%g" % (x0, y0, x0 + 110, y0 - 70, x1 + 170, y1 + 20, x1 + 8, y1 + 4)
    s = '<g filter="url(#maoL)">'
    s += '<path d="%s" fill="none" stroke="%s" stroke-width="8" stroke-linecap="round"/>' % (d, VINHO)
    # ponta (duas pernas), alinhada com a chegada da curva
    ang = math.atan2((y1 + 4) - (y1 + 20), (x1 + 8) - (x1 + 170))
    for da in (-.55, .55):
        a = ang + math.pi + da
        s += '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="8" stroke-linecap="round"/>' % (x1 + 8, y1 + 4, x1 + 8 + math.cos(a) * 34, y1 + 4 + math.sin(a) * 34, VINHO)
    return s + '</g>'


def pagina(H, dy):
    defs = G.DEFS_EXTRA + DEFS
    svg = '<svg class="arte" viewBox="0 0 %d %d" width="%d" height="%d"><defs>%s</defs>%s</svg>' % (W, H, W, H, defs, cena(H, dy))
    css = ('*{margin:0;padding:0;box-sizing:border-box}html,body{width:%dpx;height:%dpx;background:%s}'
           '.peca{position:relative;width:%dpx;height:%dpx;overflow:hidden}'
           '.peca::before,.peca::after{content:"";position:absolute;inset:0;pointer-events:none;background-size:%dpx %dpx;z-index:5}'
           '.peca::before{background-image:var(--grao-neg);mix-blend-mode:multiply;opacity:.45}'
           '.peca::after{background-image:var(--grao-pos);mix-blend-mode:plus-lighter;opacity:.35}'
           '.arte{position:absolute;left:0;top:0;overflow:hidden}') % (W, H, NOITE, W, H, W, int(W * 4 / 3))
    return ('<!doctype html><html><head><meta charset="utf-8"><title>Gatoteca · a roda dos gatos</title>\n<!--ACERVO-->\n'
            '<style>%s</style></head><body><div class="peca">%s</div></body></html>') % (css, svg)


def fotografar(itens, escala=1):
    from playwright.sync_api import sync_playwright
    out = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for nome, H, dy in itens:
            html = pagina(H, dy).replace("<!--ACERVO-->", montar.ACERVO_CSS)
            arq = os.path.join(SAIDA, nome + ".final.html")
            open(arq, "w", encoding="utf-8").write(html)
            pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=escala)
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(1500)
            png = os.path.join(SAIDA, nome + ".png")
            pg.screenshot(path=png, clip={"x": 0, "y": 0, "width": W, "height": H})
            pg.close()
            out.append(png)
            print(png)
        b.close()
    return out


def zoom(png, escala):
    """Recortes para conferir: rostos, balao, almofada + seta, textos; e o post a 300 px."""
    from PIL import Image
    im = Image.open(png)
    k = escala
    cortes = dict(fundo=(60, 560, 1020, 1010), frente=(60, 820, 1020, 1200), texto=(60, 1120, 1020, 1350), placa=(40, 60, 1040, 430))
    for nome, (a, b, c, d) in cortes.items():
        im.crop((a * k, b * k, c * k, d * k)).save(os.path.join(SAIDA, "zoom_%s.png" % nome))
    im.resize((300, int(300 * im.height / im.width)), Image.LANCZOS).save(os.path.join(SAIDA, "zoom_300px.png"))


# ================================================================== figuras novas para o Canva
def exportar_svgs():
    from shapely.ops import unary_union as U
    os.makedirs(SVG_CANVA, exist_ok=True)

    def autonomo(vb, corpo, nome):
        x, y, w, h = vb
        s = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="%g %g %g %g" width="%g" height="%g">'
             '<defs>%s%s</defs>%s</svg>') % (x, y, w, h, w, h, G.DEFS_EXTRA, DEFS, corpo)
        open(os.path.join(SVG_CANVA, nome), "w", encoding="utf-8").write(s.replace(' href="', ' xlink:href="'))
        print("svg:", nome)

    for f, nome in ((gato_frajola, "roda - frajola lendo em voz alta.svg"), (gato_laranja, "roda - gato laranja discordando.svg"),
                    (gato_cinza, "roda - gato cinza de óculos anotando.svg"), (gato_tricolor, "roda - gata tricolor abraçando o livro.svg"),
                    (gato_dorminhoco, "roda - gatinho caramelo dormindo.svg")):
        p = f()
        todos = U([g for g in p.polis if g is not None and not g.is_empty])
        x0, y0, x1, y1 = todos.bounds
        for a, b_, c, d in p.caixas:
            x0, y0, x1, y1 = min(x0, a), min(y0, b_), max(x1, c), max(y1, d)
        x0, y0, x1, y1 = x0 - 60, y0 - 60, x1 + 60, y1 + 40
        autonomo((x0, y0, x1 - x0, y1 - y0), "".join(p.camadas), nome)
    autonomo((-160, -80, 320, 170), almofada(0, 0, 1.0), "roda - almofada vazia rosa.svg")
    autonomo((-150, -110, 300, 220), lustre(0, 0, 1.0), "roda - lustre de latão.svg")
    autonomo((-70, -100, 140, 130), xicara(0, 0, 1.0), "roda - xícara de café.svg")
    autonomo((-70, -100, 140, 130), bolo(0, 0, 1.0), "roda - fatia de bolo.svg")


if __name__ == "__main__":
    os.makedirs(SAIDA, exist_ok=True)
    final = "--final" in sys.argv
    pngs = fotografar([("divulga_post", 1350, 0), ("divulga_status", 1920, 300)])
    if "--zoom" in sys.argv:
        K = 2
        alta = fotografar([("divulga_post_2x", 1350, 0)], escala=2)
        zoom(alta[0], 2)
    if final:
        K = 2
        alta = fotografar([("divulga_post_alta", 1350, 0)], escala=2)
        shutil.copy(pngs[0], os.path.join(DESTINO, "Post - a roda dos gatos.png"))
        shutil.copy(alta[0], os.path.join(DESTINO, "Post (alta, 2160x2700).png"))
        shutil.copy(pngs[1], os.path.join(DESTINO, "Status (1080x1920).png"))
        exportar_svgs()
        print("copiado para", DESTINO)
