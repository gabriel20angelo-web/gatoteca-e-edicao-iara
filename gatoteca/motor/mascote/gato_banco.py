# -*- coding: utf-8 -*-
"""BANCO DE POSES do mascote do Entrelinhas: o frajola de pelucia de tracos (rodada 3, versao A).

O gato e montado em pecas (cabeca, corpo, bracos, pernas, solas, rabo); cada peca recebe o mesmo
pelo de riscos curtos (felpudo.pelo) e tufos na borda (felpudo.tufos), com regioes brancas
(peito, barriga, focinho, patas, ponta do rabo). A cabeca tem 12 expressoes e orelhas que giram.

uso: py gato_banco.py               -> todas as poses: PNG transparente + SVG + folha de contato
     py gato_banco.py 04 11 21      -> so essas
"""
import os, sys, math, random, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar
import fofos as F
from felpudo import amostrar, pelo, tufos, desenha, caminho, norm
from shapely.geometry import Point, LineString, Polygon, box
from shapely.ops import unary_union
from shapely import affinity

AQUI = os.path.dirname(os.path.abspath(__file__))
TINTA = "#1E1418"
AMEIXA = "#3B2A33"
PRETO = dict(base="#2A2226", escuro="#120D10", medio="#3E3439", claro="#6E6168", borda="#120D10")
BRANCO = dict(base="#F6F0E4", escuro="#C9BCA9", medio="#E6DCCB", claro="#FFFFFF", borda="#B8AA96")
ROSA, FEIJAO = "#E99AA6", "#F0A3B0"
DENS = .036


# ================================================================== geometria
def elipse(cx, cy, rx, ry, rot=0):
    e = affinity.scale(Point(0, 0).buffer(1, resolution=48), rx, ry)
    return affinity.translate(affinity.rotate(e, rot, origin=(0, 0)), cx, cy)


def spline(pts, n=10):
    """Catmull-Rom pelos pontos dados (curva suave para rabos e membros)."""
    if len(pts) < 3:
        return pts
    P = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1])
    return out


def capsula(pts, r0, r1=None, suave=True):
    """Membro/rabo afilado: circulos ao longo da curva, unidos dois a dois."""
    r1 = r0 if r1 is None else r1
    c = spline(pts) if suave and len(pts) > 2 else pts
    n = len(c)
    pecas = []
    for i in range(n - 1):
        ra = r0 + (r1 - r0) * i / (n - 1)
        rb = r0 + (r1 - r0) * (i + 1) / (n - 1)
        pecas.append(unary_union([Point(c[i]).buffer(ra), Point(c[i + 1]).buffer(rb)]).convex_hull)
    return unary_union(pecas)


def fluxo_linha(pts):
    c = spline(pts) if len(pts) > 2 else pts
    segs = [(c[i], c[i + 1]) for i in range(len(c) - 1)]

    def f(x, y):
        best, bd = None, 1e9
        for a, b in segs:
            d = LineString([a, b]).distance(Point(x, y))
            if d < bd:
                bd, best = d, (b[0] - a[0], b[1] - a[1])
        return best
    return f


def tons(pal, cx, cy, alcance=260):
    def f(x, y, r):
        k = (-(x - cx) - 1.2 * (y - cy)) / alcance
        if r < .32 + k * .25:
            return pal["claro"]
        if r > .72 + k * .2:
            return pal["escuro"]
        return pal["medio"]
    return f


# ================================================================== pelagem de uma peca
class Pose:
    def __init__(self, cod, nome, grupo, nota, centro=(0, -200)):
        self.cod, self.nome, self.grupo, self.nota = cod, nome, grupo, nota
        self.cx, self.cy = centro
        self.camadas, self.polis, self.caixas = [], [], []
        self.seed = int(cod) * 100 if cod.isdigit() else 7
        self.pe, self.pb, self.iris = PRETO, BRANCO, "#C9D86A"
        self._pilha = []

    # -------------------------------------------------- grupos: mover/encolher/girar um trecho inteiro
    def inicio(self, dx=0, dy=0, k=1.0, rot=0, pe=None, pb=None, iris=None):
        self._pilha.append((len(self.camadas), len(self.polis), dx, dy, k, rot, self.pe, self.pb, self.iris))
        if pe:
            self.pe = pe
        if pb:
            self.pb = pb
        if iris:
            self.iris = iris

    def fim(self):
        nc, npl, dx, dy, k, rot, pe, pb, iris = self._pilha.pop()
        corpo = "".join(self.camadas[nc:])
        del self.camadas[nc:]
        self.camadas.append('<g transform="translate(%g %g) rotate(%g) scale(%g)">%s</g>' % (dx, dy, rot, k, corpo))
        novos = [affinity.translate(affinity.scale(affinity.rotate(g, rot, origin=(0, 0)), k, k, origin=(0, 0)), dx, dy) for g in self.polis[npl:]]
        del self.polis[npl:]
        self.polis += novos
        self.caixas = self.caixas
        self.pe, self.pb, self.iris = pe, pb, iris

    def svg(self, s, caixa=None):
        self.camadas.append(s)
        if caixa:
            self.caixas.append(caixa)

    def peca(self, poly, fluxo, brancos=None, so_branco=False, dens=DENS, L=(9, 16), larg=(1.3, 2.1),
             tufo=None, eric=False, pular=None, op=1):
        """Desenha uma peca de pelo. brancos = poligono das regioes brancas (recortado pela peca)."""
        self.seed += 7
        self.polis.append(poly)
        tp, tb = tons(self.pe, self.cx, self.cy), tons(self.pb, self.cx, self.cy)
        if so_branco:
            brancos = poly.buffer(30)
        eh_branco = (lambda x, y: brancos.contains(Point(x, y))) if brancos is not None else (lambda x, y: False)
        borda_br = brancos.buffer(10) if brancos is not None else None
        s = ['<path d="%s" fill="%s"/>' % (caminho(poly), self.pb["base"] if so_branco else self.pe["base"])]
        if brancos is not None and not so_branco:
            inter = poly.intersection(brancos)
            if not inter.is_empty:
                s.append('<path d="%s" fill="%s"/>' % (caminho(inter), self.pb["base"]))
        n = max(20, int(poly.area * dens))
        tom = lambda x, y, r: tb(x, y, r) if eh_branco(x, y) else tp(x, y, r)
        s.append(desenha(pelo(poly, n, fluxo, tom, L=L, larg=larg, seed=self.seed), op))
        cfg = dict(passo=7.5, L=(7, 13), w=1.8, mistura=.62)
        if eric:
            cfg = dict(passo=5.2, L=(14, 27), w=1.9, mistura=.08)
        cfg.update(tufo or {})
        cor = lambda x, y: self.pb["borda"] if (borda_br is not None and borda_br.contains(Point(x, y))) else self.pe["borda"]
        s.append(tufos(poly, fluxo, cor, seed=self.seed + 1, pular=pular, **cfg))
        self.camadas.append("".join(s))

    def branco(self, poly, fluxo, **kw):
        self.peca(poly, fluxo, so_branco=True, **kw)

    # -------------------------------------------------- patas
    def pata(self, cx, cy, rx=25, ry=15, rot=0, dedos=True):
        p = elipse(cx, cy, rx, ry, rot)
        self.branco(p, lambda x, y: (0, 1), L=(5, 9), tufo=dict(passo=5, L=(4, 8), w=1.6))
        if dedos:
            t = math.radians(rot)
            d = ""
            for k in (-.3, .3):
                x0, y0 = cx + math.cos(t) * rx * k, cy + math.sin(t) * rx * k
                d += "M%.1f,%.1f L%.1f,%.1f " % (x0 + math.sin(t) * ry * .1, y0 - math.cos(t) * ry * .1 * -1, x0 - math.sin(t) * ry * .7, y0 + math.cos(t) * ry * .7)
            self.svg('<path d="%s" stroke="%s" stroke-width="1.6" stroke-linecap="round" fill="none"/>' % (d, self.pb["borda"]))

    def sola(self, cx, cy, k=1.0, rot=0):
        """Sola virada para quem olha: almofada grande e quatro feijoezinhos."""
        p = elipse(cx, cy, 34 * k, 40 * k, rot)
        self.branco(p, lambda x, y: (x - cx, y - cy), L=(5, 9), tufo=dict(passo=5, L=(4, 9), w=1.6, mistura=.2))
        g = '<g transform="translate(%g %g) rotate(%g) scale(%g)">' % (cx, cy, rot, k)
        g += '<path d="M-17,12 C-19,-2 -8,-6 0,-6 C8,-6 19,-2 17,12 C15,22 -15,22 -17,12Z" fill="%s"/>' % FEIJAO
        for x, y in ((-20, -14), (-7, -24), (7, -24), (20, -14)):
            g += '<ellipse cx="%g" cy="%g" rx="6.2" ry="7.5" fill="%s"/>' % (x, y, FEIJAO)
        self.svg(g + '</g>')

    # -------------------------------------------------- cabeca
    def cabeca(self, x, y, esc=1.0, rot=0, expr="neutro", orelhas="cima", olhar=(0, 0), vira=0, sobre_corpo=True, eric=False, recorte=None, acess=None, acess_tras=None, topo_acess=-160, mancha_testa=True):
        """Cabeca no ponto (x,y) (centro do rosto). Coordenadas locais: rosto centrado em 0,0."""
        k = 1.08
        cab = amostrar(F.CABECA, k=k, cy=-262, dy=262).buffer(4)
        oe = amostrar(F.ORELHA_E, k=k, cy=-262, dy=262)
        od = amostrar(F.ORELHA_D, k=k, cy=-262, dy=262)
        de = amostrar(F.DENTRO_E, k=k, cy=-262, dy=262)
        dd = amostrar(F.DENTRO_D, k=k, cy=-262, dy=262)
        ang = {"cima": (0, 0), "atras": (-42, 42), "baixo": (-68, 68), "lado": (0, 30), "de_lado": (-22, -10)}[orelhas]
        oe, de = affinity.rotate(oe, ang[0], origin=(-64, -55)), affinity.rotate(de, ang[0], origin=(-64, -55))
        od, dd = affinity.rotate(od, ang[1], origin=(64, -55)), affinity.rotate(dd, ang[1], origin=(64, -55))
        focinho = affinity.translate(amostrar(F.FOCINHO, k=k, cy=-262, dy=262).buffer(8), vira * .8, 0)
        mancha = affinity.translate(amostrar("M-9,-306 L9,-306 L24,-246 L-24,-246 Z", k=k, cy=-262, dy=262), vira * .6, 0)
        brancos = unary_union([focinho, mancha]) if mancha_testa else focinho
        # posicao global (para a caixa da imagem)
        tf = lambda g: affinity.translate(affinity.scale(affinity.rotate(g, rot, origin=(0, 0)), esc, esc, origin=(0, 0)), x, y)
        self.polis += [tf(cab), tf(oe), tf(od)]
        if acess:  # chapeus e coroas passam do alto da cabeca: a caixa da imagem tem de incluir
            self.polis.append(tf(box(-140, topo_acess, 140, 150)))
        sub = Pose(self.cod, "", "", "", centro=(0, 0))
        sub.seed = self.seed + 300
        sub.pe, sub.pb, sub.iris = self.pe, self.pb, self.iris
        self.seed += 11
        for a in (acess_tras or []):
            sub.svg(a)
        fluxo_cab = lambda a, b: (a - vira * .5, b + 26)
        for o, d_, lado in ((oe, de, -1), (od, dd, 1)):
            sub.peca(o, lambda a, b, l=lado: (l * .25, -1), tufo=dict(passo=6), eric=eric)
            sub.svg('<path d="%s" fill="%s"/>' % (caminho(d_), ROSA))
            sub.svg(desenha(pelo(d_, 40, lambda a, b, l=lado: (l * .25, -1), lambda a, b, r: "#FFF6F0", L=(6, 11), larg=(1, 1.4), seed=sub.seed + lado)))
        sub.peca(cab, fluxo_cab, brancos=brancos, dens=.04, L=(7, 13), eric=eric,
                 tufo=dict(L=(9, 16), mistura=.45), pular=(lambda a, b, nx, ny: ny > .45) if sobre_corpo else None)
        sub.svg(rosto(expr, olhar, vira, self.iris, self.pe))
        for a in (acess or []):
            sub.svg(a)
        corpo = "".join(sub.camadas)
        if recorte:
            corpo = '<clipPath id="rc%s"><path d="%s"/></clipPath><g clip-path="url(#rc%s)">%s</g>' % (self.cod, recorte, self.cod, corpo)
        self.camadas.append('<g transform="translate(%g %g) rotate(%g) scale(%g)">%s</g>' % (x, y, rot, esc, corpo))


# ================================================================== o rosto (coordenadas locais da cabeca)
def olho_brilho(x, y, rx=16.7, ry=18.9, iris="#C9D86A", olhar=(0, 0), menor=1.0):
    rx, ry = rx * menor, ry * menor
    s = '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="%s"/>' % (x, y, rx, ry, TINTA)
    s += '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="%s"/>' % (x + olhar[0] * .4, y + 2 + olhar[1] * .4, rx * .78, ry * .8, iris)
    s += '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="%s"/>' % (x + olhar[0], y + 2 + olhar[1], rx * .42, ry * .62, TINTA)
    s += '<circle cx="%g" cy="%g" r="%g" fill="#FFFDF6"/><circle cx="%g" cy="%g" r="%g" fill="#FFFDF6"/>' % (x + 5 + olhar[0] * .3, y - 6 + olhar[1] * .3, rx * .36, x - 5, y + 8, rx * .15)
    return s


def L_(d, w=4, cor=TINTA):
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%g" stroke-linecap="round" stroke-linejoin="round"/>' % (d, cor, w)


def coracao(x, y, s=1.0, cor="#E0566E", contorno=AMEIXA):
    return ('<path transform="translate(%g %g) scale(%g)" d="M0,8 C-14,-2 -18,-12 -10,-18 C-5,-22 0,-18 0,-13 C0,-18 5,-22 10,-18 C18,-12 14,-2 0,8Z" '
            'fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round"/>') % (x, y, s, cor, contorno, 2 / s)


def rosto(expr, olhar=(0, 0), vira=0, iris="#C9D86A", pe=PRETO):
    v = vira
    ex, dx = 41, v
    menor_e, menor_d = (1.0, 1.0) if v == 0 else ((.86, 1.0) if v > 0 else (1.0, .86))
    s = []
    bochecha = .55
    boca = "w"
    if expr in ("neutro", "curioso", "leitura", "pendurado"):
        o = {"neutro": olhar, "curioso": (olhar[0] or 5, olhar[1] or -5), "leitura": (0, 7), "pendurado": (0, -6)}[expr]
        s.append(olho_brilho(-ex + dx, 0, olhar=o, menor=menor_e, iris=iris) + olho_brilho(ex + dx, 0, olhar=o, menor=menor_d, iris=iris))
        if expr == "leitura":
            s.append('<path d="M%g,-18 L%g,-18 L%g,-4 L%g,-4Z M%g,-18 L%g,-18 L%g,-4 L%g,-4Z" fill="%s"/>' % (
                -60 + dx, -22 + dx, -22 + dx, -60 + dx, 22 + dx, 60 + dx, 60 + dx, 22 + dx, pe["base"]))
            s.append(L_("M%g,-4 L%g,-4 M%g,-4 L%g,-4" % (-58 + dx, -24 + dx, 24 + dx, 58 + dx), 3.5))
        if expr in ("curioso", "pendurado"):
            boca = "o"
    elif expr == "feliz":
        s.append(L_("M%g,4 C%g,-10 %g,-10 %g,4 M%g,4 C%g,-10 %g,-10 %g,4" % (-56 + dx, -50 + dx, -32 + dx, -26 + dx, 26 + dx, 32 + dx, 50 + dx, 56 + dx), 5))
        boca, bochecha = "aberta", .75
    elif expr == "contente":
        s.append(L_("M%g,-2 C%g,10 %g,10 %g,-2 M%g,-2 C%g,10 %g,10 %g,-2" % (-56 + dx, -50 + dx, -32 + dx, -26 + dx, 26 + dx, 32 + dx, 50 + dx, 56 + dx), 4.5))
        bochecha = .7
    elif expr == "dormindo":
        s.append(L_("M%g,0 C%g,9 %g,9 %g,0 M%g,0 C%g,9 %g,9 %g,0" % (-56 + dx, -50 + dx, -32 + dx, -26 + dx, 26 + dx, 32 + dx, 50 + dx, 56 + dx), 4.2))
        s.append(L_("M-54,4 l-6,5 M-30,6 l-2,6 M30,6 l2,6 M54,4 l6,5", 2.2))
    elif expr == "piscando":
        s.append(L_("M%g,4 C%g,-10 %g,-10 %g,4" % (-56 + dx, -50 + dx, -32 + dx, -26 + dx), 5) + olho_brilho(ex + dx, 0, olhar=olhar, iris=iris))
    elif expr == "assustado":
        for xx in (-ex + dx, ex + dx):
            s.append('<ellipse cx="%g" cy="0" rx="19" ry="21" fill="#FFFDF6" stroke="%s" stroke-width="3.2"/>' % (xx, TINTA))
            s.append('<circle cx="%g" cy="2" r="5.5" fill="%s"/><circle cx="%g" cy="0" r="1.8" fill="#FFFDF6"/>' % (xx, TINTA, xx + 2))
        s.append(L_("M-58,-32 C-50,-40 -36,-40 -28,-34 M28,-34 C36,-40 50,-40 58,-32", 3.4))
        boca, bochecha = "tremida", .3
    elif expr == "bravo":
        for xx, lado in ((-ex + dx, -1), (ex + dx, 1)):
            s.append(olho_brilho(xx, 2, iris="#E3C24A"))
            # ponta de dentro (perto do nariz) BAIXA, ponta de fora alta: cara de bravo
            s.append('<path d="M%g,%g L%g,%g L%g,-34 L%g,-34Z" fill="%s"/>' % (xx - lado * 24, 6, xx + lado * 22, -16, xx + lado * 22, xx - lado * 24, pe["base"]))
            s.append(L_("M%g,6 L%g,-16" % (xx - lado * 22, xx + lado * 21), 4.6))
            s.append(L_("M%g,-16 L%g,-38" % (xx - lado * 24, xx + lado * 24), 7, "#F6F0E4"))
        boca, bochecha = "chiando", 0
    elif expr == "triste":
        s.append(olho_brilho(-ex + dx, 2, olhar=(0, 3), iris=iris) + olho_brilho(ex + dx, 2, olhar=(0, 3), iris=iris))
        s.append('<path d="M-56,14 C-46,22 -34,22 -26,14 M26,14 C34,22 46,22 56,14" fill="none" stroke="#9FD3F0" stroke-width="3"/>')
        s.append('<path d="M-58,20 C-62,34 -62,46 -56,52 C-50,46 -52,34 -58,20Z" fill="#AEE0F7" stroke="%s" stroke-width="1.6"/>' % AMEIXA)
        s.append(L_("M-58,-22 C-50,-24 -38,-30 -30,-38 M30,-38 C38,-30 50,-24 58,-22", 3.4))
        boca, bochecha = "triste", .35
    elif expr == "bocejo":
        s.append(L_("M-56,-6 L-34,2 L-56,8 M56,-6 L34,2 L56,8", 4.4))
        boca, bochecha = "bocejo", .5
    elif expr == "apaixonado":
        s.append(coracao(-ex + dx, 4, 1.55, "#E0566E", TINTA) + coracao(ex + dx, 4, 1.55, "#E0566E", TINTA))
        bochecha = .85
    # bochechas, nariz, boca, bigodes
    if bochecha:
        s.append('<ellipse cx="%g" cy="32" rx="17" ry="10" fill="#F28C9A" opacity="%g" filter="url(#borrao)"/><ellipse cx="%g" cy="32" rx="17" ry="10" fill="#F28C9A" opacity="%g" filter="url(#borrao)"/>' % (-69 + dx, bochecha, 69 + dx, bochecha))
    s.append('<path d="M%g,16 L%g,16 C%g,22 %g,25 %g,26 C%g,25 %g,22 %g,16Z" fill="#F18E9B" stroke="%s" stroke-width="1.7"/>' % (-10 + dx, 10 + dx, 10 + dx, 3 + dx, dx, -3 + dx, -10 + dx, -10 + dx, TINTA))
    m = dx
    if boca == "w":
        s.append(L_("M%g,26 L%g,33 M%g,33 C%g,42 %g,42 %g,33 C%g,42 %g,42 %g,33" % (m, m, m - 15, m - 12, m - 3, m, m + 3, m + 12, m + 15), 2.8))
    elif boca == "o":
        s.append(L_("M%g,26 L%g,31" % (m, m), 2.6) + '<ellipse cx="%g" cy="38" rx="5" ry="6" fill="#B8475A" stroke="%s" stroke-width="2.4"/>' % (m, TINTA))
    elif boca == "aberta":
        s.append(L_("M%g,26 L%g,31" % (m, m), 2.6) + '<path d="M%g,32 C%g,50 %g,50 %g,32 C%g,36 %g,36 %g,32Z" fill="#B8475A" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % (m - 13, m - 10, m + 10, m + 13, m + 5, m - 5, m - 13, TINTA)
                 + '<path d="M%g,44 C%g,40 %g,40 %g,44 C%g,47 %g,47 %g,44Z" fill="#F07C8C"/>' % (m - 7, m - 3, m + 3, m + 7, m + 3, m - 3, m - 7))
    elif boca == "tremida":
        s.append(L_("M%g,36 l5,-4 l5,4 l5,-4 l5,4 l5,-4" % (m - 15), 2.6))
    elif boca == "chiando":
        s.append('<path d="M%g,30 C%g,52 %g,52 %g,30 C%g,34 %g,34 %g,30Z" fill="#7A2A3C" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (m - 22, m - 16, m + 16, m + 22, m + 8, m - 8, m - 22, TINTA)
                 + '<path d="M%g,32 L%g,32 L%g,42Z M%g,32 L%g,32 L%g,42Z" fill="#FFFDF6"/>' % (m - 16, m - 9, m - 12, m + 9, m + 16, m + 12))
    elif boca == "triste":
        s.append(L_("M%g,26 L%g,32 M%g,40 C%g,32 %g,32 %g,40" % (m, m, m - 10, m - 4, m + 4, m + 10), 2.8))
    elif boca == "bocejo":
        s.append(L_("M%g,26 L%g,29" % (m, m), 2.6) + '<ellipse cx="%g" cy="46" rx="17" ry="20" fill="#7A2A3C" stroke="%s" stroke-width="2.6"/>' % (m, TINTA)
                 + '<path d="M%g,54 C%g,46 %g,46 %g,54 C%g,62 %g,62 %g,54Z" fill="#F07C8C"/>' % (m - 10, m - 4, m + 4, m + 10, m + 6, m - 6, m - 10)
                 + '<path d="M%g,30 L%g,30 L%g,37Z M%g,30 L%g,30 L%g,37Z" fill="#FFFDF6"/>' % (m - 11, m - 6, m - 9, m + 6, m + 11, m + 9))
    s.append('<path d="M%g,22 L%g,10 M%g,30 L%g,30 M%g,38 L%g,52 M%g,22 L%g,10 M%g,30 L%g,30 M%g,38 L%g,52" fill="none" stroke="#FFFDF6" stroke-width="1.5" stroke-linecap="round" opacity=".85"/>' % (
        -80 + m, -160 + m, -82 + m, -162 + m, -78 + m, -152 + m, 80 + m, 160 + m, 82 + m, 162 + m, 78 + m, 152 + m))
    return "".join(s)


# ================================================================== efeitos e objetos (traco de tarot: contorno ameixa)
def brilho(x, y, s=1.0, cor=AMEIXA):
    return '<path transform="translate(%g %g) scale(%g)" d="M0,-10 Q0,0 10,0 Q0,0 0,10 Q0,0 -10,0 Q0,0 0,-10Z" fill="%s"/>' % (x, y, s, cor)


def texto_simb(x, y, t, tam=70, cor=AMEIXA, rot=0):
    return '<text x="%g" y="%g" transform="rotate(%g %g %g)" text-anchor="middle" font-family="Cormorant" font-weight="700" font-style="italic" font-size="%g" fill="%s">%s</text>' % (x, y, rot, x, y, tam, cor, t)


def zzz(x, y):
    return ('<text x="%g" y="%g" font-family="Caveat" font-weight="700" font-size="64" fill="%s">z</text>'
            '<text x="%g" y="%g" font-family="Caveat" font-weight="700" font-size="46" fill="%s">z</text>'
            '<text x="%g" y="%g" font-family="Caveat" font-weight="700" font-size="32" fill="%s">z</text>') % (x, y, AMEIXA, x + 38, y - 40, AMEIXA, x + 66, y - 70, AMEIXA)


def gota(x, y, s=1.0):
    return '<path transform="translate(%g %g) scale(%g)" d="M0,-16 C6,-6 10,0 10,6 C10,13 5,17 0,17 C-5,17 -10,13 -10,6 C-10,0 -6,-6 0,-16Z" fill="#AEE0F7" stroke="%s" stroke-width="2"/>' % (x, y, s, AMEIXA)


def raiva(x, y, s=1.0):
    d = "M-14,-4 C-8,-6 -6,-8 -4,-14 M4,-14 C6,-8 8,-6 14,-4 M14,4 C8,6 6,8 4,14 M-4,14 C-6,8 -8,6 -14,4"
    return '<path transform="translate(%g %g) scale(%g)" d="%s" fill="none" stroke="#C8324F" stroke-width="%g" stroke-linecap="round"/>' % (x, y, s, d, 4.5 / s)


def nuvem_chuva(x, y):
    n = ('<path transform="translate(%g %g)" d="M-60,10 C-74,10 -78,-12 -60,-16 C-58,-34 -30,-38 -20,-24 C-12,-44 22,-42 26,-20 C44,-26 58,-10 50,4 C62,8 58,22 44,22 L-52,22 C-66,22 -70,10 -60,10Z" '
         'fill="#DCE6EE" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>') % (x, y, AMEIXA)
    for dx_, dy_ in ((-36, 40), (-6, 52), (24, 40), (-20, 74), (12, 80)):
        n += '<path transform="translate(%g %g)" d="M0,-8 C3,-3 5,0 5,3 C5,7 2,9 0,9 C-2,9 -5,7 -5,3 C-5,0 -3,-3 0,-8Z" fill="#8EC5E8"/>' % (x + dx_, y + dy_)
    return n


def contorno(d, fill, w=2.6):
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round" stroke-linecap="round"/>' % (d, fill, AMEIXA, w)


def livro_fechado(cx, cy, w, h, cor="#C8324F", rot=0, estrela=True):
    s = '<g transform="translate(%g %g) rotate(%g)">' % (cx, cy, rot)
    s += contorno("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (-w / 2 + 8, -h / 2 + 6, w / 2 + 6, -h / 2 + 6, w / 2 + 6, h / 2 + 6, -w / 2 + 8, h / 2 + 6), "#F4ECDC")
    s += contorno("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (-w / 2, -h / 2, w / 2, -h / 2, w / 2, h / 2, -w / 2, h / 2), cor)
    s += '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="2" opacity=".5"/>' % (-w / 2 + 14, -h / 2, -w / 2 + 14, h / 2, AMEIXA)
    if estrela:
        s += brilho(6, -h * .12, min(w, h) / 50, "#F2C94C")
        s += '<path d="M%g,%g L%g,%g M%g,%g L%g,%g" stroke="#F2C94C" stroke-width="2.4" stroke-linecap="round"/>' % (-w * .2, h * .18, w * .3, h * .18, -w * .1, h * .28, w * .22, h * .28)
    return s + '</g>'


def livro_aberto_costas(cx, cy, w=200, h=130, cor="#C8324F"):
    """Livro aberto visto por tras (capas para quem olha), como quando o gato le."""
    s = '<g transform="translate(%g %g)">' % (cx, cy)
    s += contorno("M0,%g L%g,%g L%g,%g L0,%g Z" % (-h / 2 + 4, -w / 2, -h / 2 - 8, -w / 2, h / 2 - 8, h / 2 + 4), cor)
    s += contorno("M0,%g L%g,%g L%g,%g L0,%g Z" % (-h / 2 + 4, w / 2, -h / 2 - 8, w / 2, h / 2 - 8, h / 2 + 4), "#B02A46")
    s += contorno("M%g,%g L0,%g L%g,%g" % (-w / 2 + 4, -h / 2 - 14, -h / 2 - 2, w / 2 - 4, -h / 2 - 14), "#F4ECDC", 2)
    s += brilho(w * .25, -6, 1.3, "#F2C94C") + brilho(-w * .25, 10, .7, "#F2C94C")
    return s + '</g>'


def caneca(cx, cy, k=1.0):
    s = '<g transform="translate(%g %g) scale(%g)">' % (cx, cy, k)
    s += '<path d="M-26,-60 C-32,-72 -20,-80 -26,-94 M0,-60 C-6,-72 6,-80 0,-96 M24,-60 C18,-72 30,-80 24,-94" fill="none" stroke="%s" stroke-width="2.4" stroke-linecap="round" opacity=".7"/>' % AMEIXA
    s += contorno("M38,-34 C66,-34 66,6 36,6", "none", 7)
    s += contorno("M38,-34 C66,-34 66,6 36,6", "none", 0.1)
    s += contorno("M-42,-50 L42,-50 L38,22 C36,34 -36,34 -38,22 Z", "#F4ECDC")
    s += contorno("M-42,-50 C-42,-58 42,-58 42,-50 C42,-42 -42,-42 -42,-50Z", "#7B4A2E")
    s += brilho(0, -6, 1.6, "#C8324F")
    return s + '</g>'


def placa(cx, cy, w=360, h=180):
    s = contorno("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2, cx + w / 2, cy + h / 2, cx - w / 2, cy + h / 2), "#FBF3E2", 3)
    s += '<rect x="%g" y="%g" width="%g" height="%g" rx="6" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="3 7" opacity=".6"/>' % (cx - w / 2 + 14, cy - h / 2 + 14, w - 28, h - 28, AMEIXA)
    return s


def lanterna(cx, cy, k=1.0):
    s = '<g transform="translate(%g %g) scale(%g)">' % (cx, cy, k)
    s += '<circle cx="0" cy="40" r="80" fill="#FFD267" opacity=".5" filter="url(#brilho)"/>'
    s += contorno("M-14,0 C-14,-24 14,-24 14,0", "none", 2.6)
    s += contorno("M-26,6 L26,6 L32,96 L-32,96Z", "#F6D27A")
    s += '<path d="M0,6 L0,96 M-29,50 L29,50" stroke="%s" stroke-width="2"/>' % AMEIXA
    s += '<path d="M0,30 L6,44 L22,44 L9,54 L14,70 L0,60 L-14,70 L-9,54 L-22,44 L-6,44Z" fill="#FFF3C6"/>'
    s += contorno("M-36,96 L36,96 L36,108 L-36,108Z", "#7B4A2E")
    return s + '</g>'


def ecobag(cx, cy, w=320, h=250):
    x0, y0 = cx - w / 2, cy - h
    s = contorno("M%g,%g C%g,%g %g,%g %g,%g" % (cx - 150, y0 + 8, cx - 160, y0 - 120, cx - 100, y0 - 130, cx - 96, y0 + 8), "none", 7)
    s += contorno("M%g,%g C%g,%g %g,%g %g,%g" % (cx + 96, y0 + 8, cx + 100, y0 - 130, cx + 160, y0 - 120, cx + 150, y0 + 8), "none", 7)
    return s


def ecobag_frente(cx, cy, w=320, h=250):
    x0, y0 = cx - w / 2, cy - h
    s = contorno("M%g,%g L%g,%g L%g,%g L%g,%g Z" % (x0, y0, x0 + w, y0, x0 + w - 12, cy, x0 + 12, cy), "#EAD9B8", 3)
    s += '<g transform="translate(%g %g)"><path d="M-22,-8 a26,26 0 1 0 26,-26 a20,20 0 1 1 -26,26Z" fill="#E8752F" stroke="%s" stroke-width="2.2"/></g>' % (cx, cy - h * .52, AMEIXA)
    s += '<text x="%g" y="%g" text-anchor="middle" font-family="Cormorant" font-style="italic" font-weight="700" font-size="42" fill="%s">Entrelinhas</text>' % (cx, cy - h * .2, AMEIXA)
    return s


# ================================================================== CORPOS-BASE
CORPO_B = ("M-122,0 C-150,-40 -144,-122 -110,-168 C-92,-196 -62,-210 -40,-214 L40,-214 C62,-210 92,-196 110,-168 "
           "C144,-122 150,-40 122,0 C80,10 -80,10 -122,0 Z")
PAO = "M-232,0 C-266,-10 -270,-124 -212,-170 C-160,-210 -60,-216 0,-216 C60,-216 160,-210 212,-170 C270,-124 266,-10 232,0 Z"
BEAN_PE = ("M-86,-40 C-104,-100 -100,-190 -70,-238 C-50,-266 50,-266 70,-238 C100,-190 104,-100 86,-40 C70,-8 -70,-8 -86,-40Z")


def rabo(p, pts, r0=18, r1=13, ponta=True, eric=False):
    t = capsula(pts, r0, r1)
    if eric:
        t = t.buffer(10)
    br = Point(pts[-1]).buffer(r1 * 2.4) if ponta else None
    p.peca(t, fluxo_linha(pts), brancos=br, eric=eric, tufo=dict(passo=6.5))
    return t


def membro(p, pts, r0, r1, branco_ponta=None, fluxo=None):
    m = capsula(pts, r0, r1)
    p.peca(m, fluxo or fluxo_linha(pts), brancos=branco_ponta, tufo=dict(passo=7))
    return m


def sentado(p, rabo_cima=True, cabeca=None, patas=True, eric=False, peito=True):
    """A pose-base: sentado de pudim (corpo e rabo); cabeca opcional por parametro."""
    if rabo_cima:
        rabo(p, [(108, -30), (168, -70), (184, -130), (166, -172)], 20, 16, eric=eric)
    corpo = amostrar(F.CORPO).buffer(4)
    p.peca(corpo, lambda x, y: (x / 230, 1), brancos=amostrar(F.PEITO).buffer(6) if peito else None, eric=eric)
    p.svg('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round" opacity=".55"/>' % (F.PERNAS, p.pb["escuro"]))
    if patas:
        p.pata(-46, -12, 27, 15)
        p.pata(46, -12, 27, 15)
    if cabeca is not None:
        p.cabeca(0, -262, **cabeca)


def sentado_barriga(p, cabeca=None, bracos="barriga", solas=True):
    """Sentado largado: barriga redonda, pernas para frente e solas a mostra."""
    rabo(p, [(-100, -12), (-160, -2), (-206, -26), (-214, -72)], 18, 14)
    corpo = amostrar(CORPO_B).buffer(4)
    barriga = unary_union([elipse(0, -92, 82, 94), amostrar(F.PEITO).buffer(8)])
    p.peca(corpo, lambda x, y: (x / 230, 1), brancos=barriga)
    for lado in (-1, 1):
        coxa = elipse(lado * 100, -44, 50, 48)
        p.peca(coxa, lambda x, y, l=lado: (l * .6, 1))
    if bracos == "barriga":
        for lado in (-1, 1):
            membro(p, [(lado * 80, -182), (lado * 64, -150), (lado * 48, -124)], 23, 20)
            p.pata(lado * 46, -118, 25, 17, lado * -20)
    if cabeca is not None:
        p.cabeca(0, -262, **cabeca)
    if solas:
        p.sola(-82, 2, 1.0, 12)
        p.sola(82, 2, 1.0, -12)


def em_pe(p, bracos="cima", cabeca=None, rabo_lado=1):
    rabo(p, [(rabo_lado * 70, -60), (rabo_lado * 140, -80), (rabo_lado * 172, -150), (rabo_lado * 150, -204)], 18, 13)
    for lado in (-1, 1):
        membro(p, [(lado * 46, -50), (lado * 50, -10)], 30, 28)
    corpo = amostrar(BEAN_PE).buffer(3)
    p.peca(corpo, lambda x, y: (x / 200, 1), brancos=unary_union([elipse(0, -122, 58, 84), elipse(0, -222, 42, 30)]))
    for lado in (-1, 1):
        p.pata(lado * 52, -8, 34, 16)
    if bracos == "cima":
        for lado in (-1, 1):
            membro(p, [(lado * 66, -206), (lado * 100, -248), (lado * 128, -284)], 22, 19)
    if cabeca is not None:
        p.cabeca(0, -318, **cabeca)
    if bracos == "cima":
        for lado in (-1, 1):
            p.pata(lado * 134, -294, 22, 20, lado * 30, dedos=False)


# ================================================================== AS POSES
POSES = []


def pose(cod, nome, grupo, nota):
    def deco(f):
        POSES.append((cod, nome, grupo, nota, f))
        return f
    return deco


@pose("01", "Sentado", "Descanso", "A pose-base, de pudim, olhando para quem lê. Serve para assinatura, perfil e quando o post só precisa da presença dele.")
def p01(p):
    sentado(p, cabeca=dict())


@pose("02", "Pão", "Descanso", "Deitado de pão, patinhas escondidas, olhos de contentamento. Bom para «aconchego», leitura calma, aviso de pausa.")
def p02(p):
    rabo(p, [(200, -30), (228, -2), (180, 14), (100, 14), (66, 6)], 17, 14)
    corpo = amostrar(PAO).buffer(3)
    p.peca(corpo, lambda x, y: (x / 160, .45), brancos=elipse(0, -50, 78, 48), dens=.034)
    p.pata(-40, -8, 26, 12, dedos=True)
    p.pata(40, -8, 26, 12, dedos=True)
    p.cabeca(0, -128, expr="contente")


@pose("03", "Bolinha dormindo", "Descanso", "Enrolado como uma bolinha, o rabo cobrindo o queixo. Para «boa noite», «até o próximo encontro», textos de descanso.")
def p03(p):
    corpo = amostrar("M-170,-130 C-170,-250 -60,-310 40,-300 C150,-290 200,-210 190,-120 C180,-30 100,0 0,0 C-100,0 -170,-40 -170,-130Z").buffer(3)
    p.peca(corpo, lambda x, y: (x - 10, y + 150), dens=.033)
    p.pata(-104, -44, 24, 14, -10)
    p.cabeca(-46, -118, esc=.92, rot=-12, expr="dormindo")
    rabo(p, [(176, -120), (176, -40), (110, -8), (0, -6), (-100, -16), (-158, -40)], 22, 16)
    p.svg(zzz(60, -300), caixa=(50, -400, 170, -280))


@pose("04", "Barriga pra cima", "Descanso", "De barriga pra cima, patinhas no ar e os feijõezinhos à mostra. O post de carinho, de alegria boba, de «chegou o livro».")
def p04(p):
    rabo(p, [(30, -4), (90, 22), (160, 14), (196, -22)], 18, 13)
    for lado in (-1, 1):
        membro(p, [(lado * 100, -60), (lado * 140, -92), (lado * 160, -118)], 32, 28)
    corpo = elipse(0, -150, 150, 160)
    p.peca(corpo, lambda x, y: (x / 200, (y + 150) / 200), brancos=unary_union([elipse(0, -150, 96, 122), elipse(0, -280, 60, 30)]))
    p.cabeca(0, -330, rot=-6, expr="feliz")
    for lado in (-1, 1):
        membro(p, [(lado * 108, -256), (lado * 128, -298), (lado * 132, -330)], 24, 21)
        p.pata(lado * 132, -340, 24, 20, lado * 20, dedos=False)
        p.sola(lado * 166, -130, .95, lado * 35)
    p.svg(coracao(-190, -420, 1.4) + coracao(200, -380, 1.0) + brilho(230, -470, 1.2), caixa=(-220, -470, 240, -360))


@pose("05", "Sentado largado", "Descanso", "Sentado «de gente», barriguinha redonda e solas viradas pra frente. A pose mais dele: para «chegou sexta», «terminei o livro», conversa.")
def p05(p):
    sentado_barriga(p, cabeca=dict())


@pose("06", "Em pé comemorando", "Movimento", "Em pé nas patas de trás, bracinhos pra cima, barriguinha à mostra. Anúncio, conquista, «inscrições abertas».")
def p06(p):
    em_pe(p, "cima", cabeca=dict(expr="feliz"))
    p.svg(brilho(-170, -420, 1.4) + brilho(180, -440, 1.1) + brilho(210, -330, .8), caixa=(-190, -460, 230, -320))


@pose("07", "De lado andando", "Movimento", "De perfil, andando com o rabo em gancho e o rosto virado pra quem lê. Para «a caminho do encontro», transições, setas de «arraste».")
def p07(p):
    membro(p, [(78, -110), (64, -10)], 21, 20)
    membro(p, [(-86, -110), (-74, -10)], 24, 22)
    rabo(p, [(-182, -160), (-226, -212), (-232, -282), (-200, -322)], 17, 13)
    corpo = unary_union([elipse(-20, -140, 160, 64), elipse(-112, -136, 82, 74), elipse(92, -150, 72, 68)])
    p.peca(corpo, lambda x, y: (1, .35), brancos=unary_union([elipse(122, -108, 50, 48), elipse(0, -82, 120, 14)]))
    membro(p, [(108, -110), (124, -10)], 22, 21)
    membro(p, [(-126, -110), (-146, -10)], 26, 23)
    for x in (64, 124):
        p.pata(x + 8, -8, 26, 12)
    for x in (-74, -146):
        p.pata(x + 6, -8, 28, 12)
    p.cabeca(150, -236, esc=.92, rot=5)


@pose("08", "Olhando pra trás", "Movimento", "De costas, virando a cabeça por cima do ombro. Para «e você, já leu?», chamadas de continuação, «deixa eu te contar».")
def p08(p):
    rabo(p, [(-96, -10), (-160, 0), (-202, -30), (-208, -74)], 18, 14)
    corpo = amostrar(F.CORPO).buffer(4)
    p.peca(corpo, lambda x, y: (x / 230, 1))
    p.svg('<path d="M10,-200 C0,-150 4,-90 -4,-20" fill="none" stroke="%s" stroke-width="2.2" opacity=".55"/>' % PRETO["claro"])
    p.cabeca(34, -266, rot=12, vira=28, expr="curioso", olhar=(8, 0), orelhas="de_lado")


@pose("09", "Espreguiçando", "Movimento", "Bumbum pra cima, patas da frente esticadas, bocejo. Para «bom dia», «segunda-feira», começo de leitura.")
def p09(p):
    membro(p, [(-100, -150), (-94, -10)], 24, 22)
    membro(p, [(60, -64), (214, -28)], 19, 18)
    rabo(p, [(-186, -200), (-214, -268), (-198, -340), (-162, -370)], 17, 13)
    corpo = unary_union([elipse(-120, -170, 78, 74), capsula([(-110, -160), (60, -80)], 60, 52), elipse(70, -70, 62, 54)])
    p.peca(corpo, lambda x, y: (1, .45), brancos=elipse(96, -58, 42, 38))
    membro(p, [(-152, -150), (-162, -10)], 26, 24)
    membro(p, [(74, -50), (232, -16)], 20, 19)
    p.pata(-162, -8, 28, 12)
    p.pata(-90, -8, 26, 12)
    p.pata(244, -14, 26, 13)
    p.pata(226, -26, 24, 12)
    p.cabeca(120, -132, esc=.88, rot=-6, expr="bocejo")


@pose("10", "Deitado esticado", "Movimento", "Deitado de lado, comprido, a cabeça apoiada nas patinhas. Para «domingo», «tempo de ler», textos longos.")
def p10(p):
    rabo(p, [(-196, -50), (-256, -26), (-300, -14), (-334, -14)], 17, 12)
    membro(p, [(-160, -50), (-196, -16)], 30, 26)
    corpo = capsula([(-150, -64), (110, -64)], 62)
    p.peca(corpo, lambda x, y: (1, .25), brancos=elipse(-10, -16, 140, 22))
    membro(p, [(100, -30), (200, -10)], 17, 16)
    p.pata(-204, -12, 30, 12)
    membro(p, [(120, -44), (230, -16)], 18, 17)
    p.pata(212, -10, 26, 11)
    p.pata(242, -14, 27, 12)
    p.cabeca(176, -100, esc=.9, rot=10, expr="contente")


@pose("11", "Lendo", "Segurando", "Sentado largado lendo um livro de capa vermelha, olhos nas páginas e as solas aparecendo. O mascote em serviço: indicação de leitura, «livro do mês».")
def p11(p):
    sentado_barriga(p, cabeca=dict(rot=-4, expr="leitura"), bracos=None)
    p.svg(livro_aberto_costas(0, -118, 210, 132))
    for lado in (-1, 1):
        membro(p, [(lado * 84, -184), (lado * 100, -150), (lado * 98, -122)], 22, 19)
        p.pata(lado * 98, -116, 22, 18, lado * 70, dedos=False)


@pose("12", "Abraçando o livro", "Segurando", "Em pé, abraçado num livro, olhos fechados de quem ama a história. Para «livro favorito», resenha, «a gente amou».")
def p12(p):
    em_pe(p, bracos=None, cabeca=dict(expr="contente"))
    p.svg(livro_fechado(0, -136, 116, 156, "#3F6E8C", rot=-8))
    for lado in (-1, 1):
        membro(p, [(lado * 70, -204), (lado * 40, -160), (lado * -6, -138)], 22, 19)
        p.pata(lado * -12, -136, 22, 18, lado * -30, dedos=False)
    p.svg(coracao(-150, -420, 1.3) + coracao(160, -380, .9), caixa=(-180, -440, 180, -360))


@pose("13", "Xícara de café", "Segurando", "Sentado largado com a xícara quentinha nas duas patas. Para os encontros, o café do clube, «bora conversar».")
def p13(p):
    sentado_barriga(p, cabeca=dict(expr="contente"), bracos=None)
    p.svg(caneca(0, -140, 1.0), caixa=(-60, -250, 70, -100))
    for lado in (-1, 1):
        membro(p, [(lado * 84, -184), (lado * 70, -150), (lado * 50, -146)], 22, 19)
        p.pata(lado * 46, -146, 22, 18, lado * 90, dedos=False)


@pose("14", "Cartaz em branco", "Segurando", "Em pé segurando um cartaz vazio por cima da cabeça: é o espaço para escrever o recado do post (data, livro, aviso).")
def p14(p):
    em_pe(p, bracos=None, cabeca=dict(expr="feliz"))
    for lado in (-1, 1):
        membro(p, [(lado * 66, -206), (lado * 104, -300), (lado * 116, -400)], 21, 18)
    p.svg(placa(0, -486, 340, 170), caixa=(-180, -580, 180, -390))
    for lado in (-1, 1):
        p.pata(lado * 116, -408, 22, 20, dedos=False)


@pose("15", "Com a lanterna", "Segurando", "Em pé com a lanterna acesa numa pata e acenando com a outra. Para «vem que o encontro é hoje à noite», Halloween, guia de leitura.")
def p15(p):
    em_pe(p, bracos=None, cabeca=dict(expr="neutro", olhar=(4, 0)))
    membro(p, [(-66, -206), (-104, -250), (-130, -290)], 22, 19)
    p.pata(-134, -300, 22, 20, -30, dedos=False)
    membro(p, [(66, -200), (110, -170), (128, -140)], 22, 19)
    p.svg(lanterna(132, -132, .9), caixa=(60, -150, 210, 0))
    p.pata(130, -134, 22, 18, 90, dedos=False)


@pose("16", "Espiando atrás do livro", "Escondido", "Só olhos, orelhas e patinhas aparecendo por cima de um livro em pé. Para spoiler, mistério, «adivinha o próximo livro».")
def p16(p):
    p.cabeca(0, -334, expr="curioso", olhar=(6, -2), sobre_corpo=False)
    p.svg(livro_fechado(0, -150, 340, 300, "#3F6E8C"), caixa=(-180, -310, 190, 0))
    p.pata(-70, -300, 26, 16)
    p.pata(70, -300, 26, 16)


@pose("17", "Pendurado na borda", "Escondido", "Pendurado pelas patinhas na borda de um livro deitado, barriguinha e solas no ar. Para «quase acabando», «segura aí», suspense.")
def p17(p):
    for lado in (-1, 1):
        membro(p, [(lado * 66, -250), (lado * 72, -330), (lado * 70, -398)], 22, 20)
    rabo(p, [(40, -92), (86, -48), (80, 6), (44, 28)], 17, 13)
    corpo = elipse(0, -170, 92, 122)
    p.peca(corpo, lambda x, y: (x / 200, 1), brancos=elipse(0, -160, 58, 90))
    for lado in (-1, 1):
        membro(p, [(lado * 44, -76), (lado * 50, -24)], 28, 26)
    p.cabeca(0, -322, expr="pendurado")
    p.svg(livro_fechado(0, -420, 520, 44, "#7A3E8E", estrela=False), caixa=(-262, -446, 266, -394))
    p.pata(-70, -428, 26, 16)
    p.pata(70, -428, 26, 16)
    p.sola(-52, -16, .9, 8)
    p.sola(52, -16, .9, -8)
    p.svg(gota(110, -380, 1.1))


@pose("18", "Na ecobag", "Escondido", "Saindo de dentro da ecobag do clube. Para divulgar o kit (ecobag, marcador), sorteio, «vem com a gente».")
def p18(p):
    p.svg(ecobag(0, 0, 320, 250), caixa=(-170, -400, 170, 0))
    p.cabeca(0, -270, expr="feliz", sobre_corpo=False)
    p.svg(ecobag_frente(0, 0, 320, 250), caixa=(-170, -370, 170, 0))
    p.pata(-70, -252, 26, 16)
    p.pata(70, -252, 26, 16)


@pose("19", "Espiando de baixo", "Escondido", "Só orelhas, olhos e patinhas subindo pela borda de baixo. Sticker de canto, fim de carrossel, «tô de olho».")
def p19(p):
    p.cabeca(0, -14, expr="neutro", olhar=(0, -5), sobre_corpo=False, recorte="M-300,-400 L300,-400 L300,%g L-300,%g Z" % (14, 14))
    p.svg('<path d="M-230,0 L230,0" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % AMEIXA, caixa=(-230, -10, 230, 4))
    p.pata(-96, -6, 28, 15)
    p.pata(96, -6, 28, 15)


@pose("20", "Feliz", "Humores", "Olhinhos fechados de alegria, boquinha aberta, rabo pra cima. Comemorações, boas notícias, «obrigado».")
def p20(p):
    sentado(p, cabeca=dict(expr="feliz"))
    p.svg(brilho(-170, -420, 1.3) + brilho(190, -400, 1.0) + brilho(-200, -300, .7), caixa=(-220, -440, 210, -290))


@pose("21", "Assustado", "Humores", "Pelo todo arrepiado (o pelo de risquinhos eriça de verdade), olhos arregalados, orelhas baixas, gota de suor. Para «prazo acabando», «últimas vagas», susto.")
def p21(p):
    sentado(p, eric=True, cabeca=dict(expr="assustado", orelhas="atras", eric=True))
    p.svg(gota(120, -350, 1.3) + texto_simb(-170, -330, "!", 90, AMEIXA, -10), caixa=(-200, -420, 150, -300))


@pose("22", "Bravo", "Humores", "Orelhas pra trás, chiando de dentinhos, marca de raiva. Para «spoiler não!», regras do clube, humor.")
def p22(p):
    sentado(p, eric=True, cabeca=dict(expr="bravo", orelhas="atras"))
    p.svg(raiva(110, -380, 1.6), caixa=(80, -410, 140, -350))


@pose("23", "Triste", "Humores", "Orelhas caídas, lágrima e nuvenzinha de chuva. Para «acabou o livro», «encontro adiado», fim de série.")
def p23(p):
    sentado(p, rabo_cima=False, cabeca=dict(expr="triste", orelhas="baixo", rot=-4))
    rabo(p, [(110, -20), (170, -6), (200, 10), (176, 20)], 18, 14)
    p.svg(nuvem_chuva(0, -460), caixa=(-80, -510, 80, -370))


@pose("24", "Curioso", "Humores", "Cabeça inclinada, olhar de lado e um ponto de interrogação. Para perguntas, enquetes, «qual livro vocês querem?».")
def p24(p):
    sentado(p, cabeca=dict(expr="curioso", rot=14, orelhas="lado", olhar=(6, -4)))
    p.svg(texto_simb(160, -360, "?", 110, AMEIXA, 12), caixa=(120, -450, 200, -330))


@pose("25", "Sonolento", "Humores", "Bocejo enorme de olhos espremidos. Para «leitura até tarde», «modo sono», posts da noite.")
def p25(p):
    sentado(p, cabeca=dict(expr="bocejo"))
    p.svg(zzz(110, -390), caixa=(100, -480, 210, -370))


@pose("26", "Apaixonado", "Humores", "Olhos de coração, bochechas vermelhas e coraçõezinhos flutuando. Para livro favorito, depoimentos, «a gente ama vocês».")
def p26(p):
    sentado(p, cabeca=dict(expr="apaixonado"))
    p.svg(coracao(-160, -400, 1.5) + coracao(170, -420, 1.1) + coracao(200, -330, .8), caixa=(-190, -440, 220, -320))


# ================================================================== render
DEFS_EXTRA = F.DEFS


def montar_svg(p, pad=40):
    todos = unary_union([g for g in p.polis if g is not None and not g.is_empty])
    x0, y0, x1, y1 = todos.bounds
    for a, b, c, d in p.caixas:
        x0, y0, x1, y1 = min(x0, a), min(y0, b), max(x1, c), max(y1, d)
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    w, h = x1 - x0, y1 - y0
    corpo = "".join(p.camadas)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.0f %.0f %.0f %.0f" width="%.0f" height="%.0f"><defs>%s</defs>%s</svg>'
           % (x0, y0, w, h, w, h, DEFS_EXTRA, corpo))
    return svg, w, h


def fontes_css():
    return montar.ACERVO_CSS


def construir(cods=None):
    from playwright.sync_api import sync_playwright
    banco = os.path.join(AQUI, "banco")
    os.makedirs(banco, exist_ok=True)
    meta = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1000, "height": 1000})
        for cod, nome, grupo, nota, f in POSES:
            if cods and cod not in cods:
                continue
            p = Pose(cod, nome, grupo, nota, centro=(0, -200))
            f(p)
            svg, w, h = montar_svg(p)
            base = "%s_%s" % (cod, nome.lower().replace(" ", "_").replace("ç", "c").replace("ã", "a").replace("é", "e").replace("á", "a").replace("í", "i").replace("ó", "o"))
            open(os.path.join(banco, base + ".svg"), "w", encoding="utf-8").write(svg)
            k = 900 / max(w, h)
            W, H = int(w * k), int(h * k)
            html = ('<!doctype html><html><head><meta charset="utf-8">%s<style>html,body{margin:0;background:transparent}svg{display:block}</style></head><body>%s</body></html>'
                    % (fontes_css(), svg.replace('width="%.0f" height="%.0f"' % (w, h), 'width="%d" height="%d"' % (W, H), 1)))
            arq = os.path.join(banco, "_tmp.html")
            open(arq, "w", encoding="utf-8").write(html)
            pg.set_viewport_size({"width": W, "height": H})
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(500)
            pg.screenshot(path=os.path.join(banco, base + ".png"), omit_background=True)
            meta.append(dict(cod=cod, nome=nome, grupo=grupo, nota=nota, arquivo=base))
            print(cod, nome, W, H)
        b.close()
    if os.path.exists(os.path.join(banco, "_tmp.html")):
        os.remove(os.path.join(banco, "_tmp.html"))
    velho = os.path.join(banco, "banco.json")
    if cods and os.path.exists(velho):
        antigos = {m["cod"]: m for m in json.load(open(velho, encoding="utf-8"))}
        for m in meta:
            antigos[m["cod"]] = m
        meta = [antigos[k] for k in sorted(antigos)]
    json.dump(meta, open(velho, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return meta


def folha(meta, destino, cols=6, cel=300, fundo=(237, 190, 79)):
    from PIL import Image, ImageDraw, ImageFont
    fonte = ImageFont.truetype(os.path.join(os.path.dirname(AQUI), "fontes", "CormorantGaramond.ttf"), 22)
    banco = os.path.join(AQUI, "banco")
    linhas = (len(meta) + cols - 1) // cols
    im = Image.new("RGB", (cols * cel, linhas * (cel + 34)), fundo)
    d = ImageDraw.Draw(im)
    for i, m in enumerate(meta):
        g = Image.open(os.path.join(banco, m["arquivo"] + ".png")).convert("RGBA")
        g.thumbnail((cel - 30, cel - 30))
        x, y = (i % cols) * cel, (i // cols) * (cel + 34)
        im.paste(g, (x + (cel - g.width) // 2, y + (cel - g.height) // 2), g)
        d.text((x + 12, y + cel + 2), "%s · %s" % (m["cod"], m["nome"]), fill=(59, 42, 51), font=fonte)
    im.save(destino)


if __name__ == "__main__":
    cods = sys.argv[1:] or None
    meta = construir(cods)
    todos = json.load(open(os.path.join(AQUI, "banco", "banco.json"), encoding="utf-8"))
    folha(todos, os.path.join(AQUI, "banco", "_folha.png"))
