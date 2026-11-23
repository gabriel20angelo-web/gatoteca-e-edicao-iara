# -*- coding: utf-8 -*-
"""FOTO DO GRUPO DO WHATSAPP do Entrelinhas: o frajola de oculos dourados ao lado de uma pilha de livros.

Quadrado 1080 x 1080 em papel texturizado; tudo o que importa cabe no circulo que o WhatsApp recorta.
Atras do gato, uma lua de papel perola com aro de ouro (a lua da arte 02, em ponto pequeno). Sem texto:
na lista de conversas a foto aparece com ~50 px e so o rosto de oculos precisa ler.

Variantes:  rosa   -> fofo (rosto do banco, olhos de brilho) em papel rosa
            jade   -> o mesmo em papel jade
            bastet -> o rosto «menos fofo» da v5 (olhos amendoados, delineado) de oculos, papel rosa
uso: py perfil_whatsapp.py [rosa jade bastet]   -> saida/perfil_<var>.png + saida/perfil_previa.png
     py perfil_whatsapp.py --final              -> tambem copia para a pasta do clube
"""
import os, sys, math, base64, shutil
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "mascote"))
import montar
from papel import papel
import gato_banco as G
import gato_banco2 as G2
from gato_banco import Pose, sentado, TINTA
from shapely.geometry import box, MultiPoint
from shapely.ops import unary_union
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[2]  # raiz do repositório

D = str(_REPO / 'gatoteca/artes')
DESTINO = os.path.join(D, "WhatsApp - foto do grupo")
W = 1080
JADE, ROSA, NOITE, AMEIXA, PEROLA, OURO, VINHO = "#5F857C", "#C799AA", "#30323C", "#624956", "#F1E3E6", "#D9B36A", "#6E1F2E"
CONTORNO = "#2A1A22"

VARIANTES = {
    # fundo, livros de baixo para cima (largura, cor, tipo), fita, rosto
    "rosa": dict(fundo=ROSA, livros=[(212, VINHO, "lombada"), (186, JADE, "paginas"), (200, AMEIXA, "lombada"), (160, OURO, "lombada")], fita=JADE, rosto="fofo"),
    "jade": dict(fundo=JADE, livros=[(212, VINHO, "lombada"), (186, ROSA, "paginas"), (200, AMEIXA, "lombada"), (160, OURO, "lombada")], fita=VINHO, rosto="fofo"),
    "bastet": dict(fundo=ROSA, livros=[(212, VINHO, "lombada"), (186, JADE, "paginas"), (200, NOITE, "lombada"), (160, OURO, "lombada")], fita=JADE, rosto="bastet"),
}


def b64(c):
    return "data:image/png;base64," + base64.b64encode(open(c, "rb").read()).decode()


def clarear(cor, f):
    r, g, b = (int(cor[i:i + 2], 16) for i in (1, 3, 5))
    m = lambda c: int(c + (255 - c) * f) if f > 0 else int(c * (1 + f))
    return "#%02X%02X%02X" % (m(r), m(g), m(b))


# ================================================================== livros deitados (vistos de frente)
def livro(cx, cy, w, h, cor, tipo, seed, rot=0):
    """Livro deitado. «lombada»: a lombada para quem olha (frisos de ouro, etiqueta). «paginas»: o miolo creme
    entre as duas capas. Cor em papel texturizado (papel.py) e contorno de tinta."""
    tex = b64(papel(int(w * 2), int(h * 2), cor, seed, forca=1.5, fibras=2.4, pintas=.6, borda=.22, relevo=.25))
    uid = "lv%d" % seed
    x0, y0 = -w / 2, -h / 2
    s = '<g transform="translate(%g %g) rotate(%g)">' % (cx, cy, rot)
    if tipo == "lombada":
        # lombada levemente abaulada nas pontas
        d = ("M%g,%g L%g,%g C%g,%g %g,%g %g,%g L%g,%g C%g,%g %g,%g %g,%gZ"
             % (x0 + 6, y0, -x0 - 6, y0, -x0 + 4, y0 + h * .2, -x0 + 4, -y0 - h * .2, -x0 - 6, -y0,
                x0 + 6, -y0, x0 - 4, -y0 - h * .2, x0 - 4, y0 + h * .2, x0 + 6, y0))
        s += '<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)">' % (uid, d, uid)
        s += '<image href="%s" x="%g" y="%g" width="%g" height="%g" preserveAspectRatio="none"/>' % (tex, x0 - 6, y0, w + 12, h)
        # brilho de volume no alto e sombra embaixo
        s += '<rect x="%g" y="%g" width="%g" height="%g" fill="#FFFFFF" opacity=".16"/>' % (x0 - 6, y0 + h * .12, w + 12, h * .16)
        s += '<rect x="%g" y="%g" width="%g" height="%g" fill="#000000" opacity=".16"/>' % (x0 - 6, -y0 - h * .22, w + 12, h * .22)
        s += '</g>'
        # frisos de ouro perto das pontas
        for xf in (x0 + 26, x0 + 36, -x0 - 36, -x0 - 26):
            s += '<path d="M%g,%g L%g,%g" stroke="%s" stroke-width="3.2" stroke-linecap="round"/>' % (xf, y0 + 4, xf, -y0 - 4, OURO if cor != OURO else VINHO)
        # etiqueta do titulo
        ew, eh = w * .34, h * .46
        s += '<rect x="%g" y="%g" width="%g" height="%g" rx="3" fill="%s" stroke="%s" stroke-width="1.8"/>' % (-ew / 2, -eh / 2, ew, eh, "#F4EAD6", CONTORNO)
        s += '<path d="M%g,%g L%g,%g M%g,%g L%g,%g" stroke="%s" stroke-width="2.4" stroke-linecap="round" opacity=".75"/>' % (
            -ew * .3, -eh * .12, ew * .3, -eh * .12, -ew * .2, eh * .18, ew * .2, eh * .18, AMEIXA)
        s += '<path d="%s" fill="none" stroke="%s" stroke-width="2.8" stroke-linejoin="round"/>' % (d, CONTORNO)
    else:
        # miolo: capa de cima e de baixo (tiras de cor) e paginas creme com riscos
        capa = h * .2
        s += '<clipPath id="%s"><rect x="%g" y="%g" width="%g" height="%g" rx="6"/></clipPath><g clip-path="url(#%s)">' % (uid, x0, y0, w, h, uid)
        s += '<image href="%s" x="%g" y="%g" width="%g" height="%g" preserveAspectRatio="none"/>' % (tex, x0, y0, w, h)
        s += '</g>'
        px0, py0, pw, ph = x0 + 10, y0 + capa, w - 14, h - 2 * capa
        s += '<rect x="%g" y="%g" width="%g" height="%g" fill="#F6EEDD"/>' % (px0, py0, pw, ph)
        riscos = "".join("M%g,%g L%g,%g " % (px0 + 4, py0 + ph * t, px0 + pw - 2, py0 + ph * t) for t in (.22, .42, .62, .8))
        s += '<path d="%s" stroke="#C9B89A" stroke-width="1.4"/>' % riscos
        s += '<rect x="%g" y="%g" width="%g" height="%g" fill="none" stroke="%s" stroke-width="1.6"/>' % (px0, py0, pw, ph, CONTORNO)
        s += '<rect x="%g" y="%g" width="%g" height="%g" rx="6" fill="none" stroke="%s" stroke-width="2.8"/>' % (x0, y0, w, h, CONTORNO)
    return s + '</g>'


def fita(x, y, cor, comp=78):
    """Fitinha de marcador saindo de baixo de um livro, com a ponta em V."""
    d = "M%g,%g L%g,%g L%g,%g L%g,%g L%g,%g Z" % (x - 9, y, x + 9, y, x + 11, y + comp, x, y + comp - 12, x - 7, y + comp + 2)
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="2.2" stroke-linejoin="round"/>' % (d, cor, CONTORNO)


def pilha(livros, cx, base, cor_fita):
    s, y, topo = "", base, base
    tipos_y = []
    for i, (w, cor, tipo) in enumerate(livros):
        h = 50 if tipo == "lombada" else 44
        dx = (0, 12, -8, 6)[i % 4]
        rot = (0, -1.2, 1.0, -2.2)[i % 4]
        s += livro(cx + dx, y - h / 2, w, h, cor, tipo, 300 + i, rot)
        tipos_y.append((cx + dx, y - h / 2, w, h))
        y -= h + 1
    topo = y
    # a fita sai do segundo livro, pela frente, caindo por cima do primeiro
    fx, fy, fw, fh = tipos_y[1]
    return s, topo, fita(fx - fw * .3, fy + fh * .3, cor_fita, 64)


# ================================================================== rosto «menos fofo» de oculos
def oculos_bastet():
    """Oculos redondos de ouro no rosto de Bastet (olhos em (+-36,-8), coordenadas da cabeca da v5)."""
    s = ""
    for x in (-37, 37):
        s += '<circle cx="%g" cy="-6" r="27" fill="#FFFFFF" fill-opacity=".12" stroke="%s" stroke-width="4.4"/>' % (x, OURO)
        s += '<path d="M%g,-22 C%g,-28 %g,-28 %g,-24" fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round" opacity=".8"/>' % (x - 13, x - 7, x + 1, x + 5)
    s += '<path d="M-10,-8 C-5,-14 5,-14 10,-8 M-64,-10 L-98,-22 M64,-10 L98,-22" fill="none" stroke="%s" stroke-width="4.2" stroke-linecap="round"/>' % OURO
    return s


def gato(var):
    v = VARIANTES[var]
    p = Pose("90", "perfil", "", "", centro=(0, -200))
    p.seed = 4200
    livros_svg, topo, fita_svg = pilha(v["livros"], -190, 2, v["fita"])
    p.svg(livros_svg + fita_svg, caixa=(-300, topo - 6, -80, 2))
    if v["rosto"] == "fofo":
        sentado(p, cabeca=dict(acess=[G2.oculos_redondos().replace(G2.OURO, OURO)]))
    else:
        import post_lilith5 as L5
        sentado(p, cabeca=None)
        L5.cabeca(p, 0, -258, 1.12, 0, olhar=(3, 1))
        p.svg('<g transform="translate(0 -258) scale(1.12)">%s</g>' % oculos_bastet())
        p.polis.append(box(-110, -258 - 1.12 * 152, 110, -180))
    return p


# ================================================================== enquadramento no circulo
def enquadrar(p, raio=478, centro=(540, 548)):
    """Maior escala em que a figura inteira cabe no circulo (margem para o recorte do WhatsApp)."""
    todos = unary_union([g for g in p.polis if g is not None and not g.is_empty] + [box(*c) for c in p.caixas])
    pts = list(todos.convex_hull.exterior.coords)
    cx0 = (todos.bounds[0] + todos.bounds[2]) / 2
    melhor = None
    for dy in range(-160, 161, 4):
        for ddx in range(-60, 61, 4):
            lo, hi = .3, 3.0
            for _ in range(30):
                s = (lo + hi) / 2
                ok = all(math.hypot((x - cx0) * s + ddx, (y - todos.bounds[3]) * s + dy + raio - 6) <= raio for x, y in pts)
                lo, hi = (s, hi) if ok else (lo, s)
            if melhor is None or lo > melhor[0]:
                melhor = (lo, ddx, dy)
    s, ddx, dy = melhor
    # (x, y) da figura -> pixel: centro + (x - cx0) * s + ddx, centro + (y - chao) * s + dy + raio - 6
    tx = centro[0] - cx0 * s + ddx
    ty = centro[1] - todos.bounds[3] * s + dy + raio - 6
    return s, tx, ty


# ================================================================== a peca
DEFS = '''
<radialGradient id="irisG" cx="45%" cy="35%" r="70%"><stop offset="0" stop-color="#EEF3A8"/><stop offset=".55" stop-color="#C9D86A"/><stop offset="1" stop-color="#7E9A3C"/></radialGradient>
<radialGradient id="halo" r=".5"><stop offset=".6" stop-color="#FFF6E2" stop-opacity=".55"/><stop offset="1" stop-color="#FFF6E2" stop-opacity="0"/></radialGradient>
<radialGradient id="luzLua" cx="42%" cy="36%" r="70%"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".35"/><stop offset=".7" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>
<filter id="sombraChao" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="9"/></filter>
<path id="br" d="M0,-10 Q0,0 10,0 Q0,0 0,10 Q0,0 -10,0 Q0,0 0,-10Z"/>
'''


def lua(cx, cy, r, var):
    tex = b64(papel(2 * r, 2 * r, "#F3E7DC", 91, forca=1.4, fibras=2.2, pintas=.7, borda=.0, relevo=.22))
    raios = ""
    for a in range(0, 360, 6):
        t = math.radians(a)
        l = r + (46 if a % 18 == 0 else 30)
        raios += "M%.1f,%.1f L%.1f,%.1f " % (math.cos(t) * (r + 16), math.sin(t) * (r + 16), math.cos(t) * l, math.sin(t) * l)
    tom = "#FFF4E6"
    s = '<g transform="translate(%g %g)">' % (cx, cy)
    s += '<circle r="%g" fill="url(#halo)"/>' % (r + 90)
    s += '<path d="%s" stroke="%s" stroke-width="2.2" stroke-linecap="round" opacity=".55"/>' % (raios, tom)
    s += '<clipPath id="luaC"><circle r="%g"/></clipPath>' % r
    s += '<image href="%s" x="%g" y="%g" width="%g" height="%g" clip-path="url(#luaC)"/>' % (tex, -r, -r, 2 * r, 2 * r)
    s += '<circle r="%g" fill="url(#luzLua)"/>' % r
    s += "".join('<circle cx="%g" cy="%g" r="%g" fill="#D9C2A8" opacity=".22"/>' % (c[0] * r, c[1] * r, c[2] * r) for c in
                 ((-.55, -.42, .13), (.5, -.58, .07), (.62, .2, .1), (-.66, .32, .06), (-.22, .66, .08)))
    s += '<g fill="none" stroke="%s"><circle r="%g" stroke-width="4"/><circle r="%g" stroke-width="1.6" opacity=".85"/></g>' % (OURO, r, r + 9)
    s += '</g>'
    return s


ESCALA, CENTRO_X, CHAO = 1.54, 594, 822


def conferir_circulo(p, s, tx, ty, raio=510):
    """Distancia maxima da figura ao centro da foto: precisa caber no circulo do WhatsApp (540) com folga."""
    todos = unary_union([g for g in p.polis if g is not None and not g.is_empty] + [box(*c) for c in p.caixas])
    d = max(math.hypot(x * s + tx - W / 2, y * s + ty - W / 2) for x, y in todos.convex_hull.exterior.coords)
    print("  figura ate %.0f px do centro (limite %d)" % (d, raio), "ok" if d <= raio else "PASSA DO CIRCULO")
    return d


def peca(var):
    v = VARIANTES[var]
    p = gato(var)
    s, tx, ty = ESCALA, CENTRO_X, CHAO
    conferir_circulo(p, s, tx, ty)
    fundo = b64(papel(W, W, v["fundo"], 92, forca=1.5, fibras=2.2, pintas=.7, borda=.10, relevo=.24))
    # a lua fica atras da cabeca e do peito do gato
    lx, ly = tx + 0 * s, ty - 250 * s
    corpo = "".join(p.camadas)
    chao = ty + 2 * s
    estrelas = "".join('<use href="#br" transform="translate(%g %g) scale(%g)"/>' % e for e in
                       ((lx + 330, ly - 150, 1.5), (lx + 380, ly - 60, .8), (lx - 360, ly - 170, 1.0), (lx + 300, ly + 90, .7)))
    svg = ('<svg class="arte" viewBox="0 0 %d %d" width="%d" height="%d"><defs>%s%s</defs>' % (W, W, W, W, G.DEFS_EXTRA, DEFS) +
           lua(lx, ly, int(232 * s / 1.4), var) +
           '<g fill="%s">%s</g>' % ("#FFF4E6", estrelas) +
           '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="%s" opacity=".32" filter="url(#sombraChao)"/>' % (tx - 70 * s, chao, 300 * s, 18 * s, AMEIXA) +
           '<g transform="translate(%g %g) scale(%g)">%s</g></svg>' % (tx, ty, s, corpo))
    css = ('*{margin:0;padding:0;box-sizing:border-box}html,body{width:%dpx;height:%dpx;background:%s}'
           '.peca{position:relative;width:%dpx;height:%dpx;overflow:hidden;background:%s url(%s) 0 0/%dpx %dpx no-repeat}'
           '.peca::before,.peca::after{content:"";position:absolute;inset:0;pointer-events:none;background-size:%dpx %dpx;z-index:5}'
           '.peca::before{background-image:var(--grao-neg);mix-blend-mode:multiply;opacity:.6}'
           '.peca::after{background-image:var(--grao-pos);mix-blend-mode:plus-lighter;opacity:.45}'
           '.arte{position:absolute;left:0;top:0;overflow:visible}') % (W, W, v["fundo"], W, W, v["fundo"], fundo, W, W, W, int(W * 4 / 3))
    return '<!doctype html><html><head><meta charset="utf-8"><title>Entrelinhas · foto do grupo (%s)</title>\n<!--ACERVO-->\n<style>%s</style></head><body><div class="peca">%s</div></body></html>' % (var, css, svg)


def exportar(vars_):
    from playwright.sync_api import sync_playwright
    saidas = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for var in vars_:
            html = peca(var).replace("<!--ACERVO-->", montar.ACERVO_CSS)
            arq = os.path.join(AQUI, "saida", "perfil_%s.final.html" % var)
            open(arq, "w", encoding="utf-8").write(html)
            pg = b.new_page(viewport={"width": W, "height": W}, device_scale_factor=1)
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(1200)
            png = os.path.join(AQUI, "saida", "perfil_%s.png" % var)
            pg.screenshot(path=png)
            pg.close()
            saidas.append((var, png))
            print(png)
        b.close()
    return saidas


def previa(saidas):
    """Como fica no WhatsApp: circulo grande (info do grupo), medio e o da lista de conversas (~50 px),
    no tema claro e no escuro."""
    from PIL import Image, ImageDraw
    tam = (360, 150, 49)
    lin = 410
    passo = sum(tam) + 3 * 18 + 40
    folha = Image.new("RGB", (40 + len(saidas) * passo, 2 * lin + 40), "#FFFFFF")
    dr = ImageDraw.Draw(folha)
    dr.rectangle((0, lin + 20, folha.width, folha.height), fill="#111B21")
    for i, (var, png) in enumerate(saidas):
        im = Image.open(png).convert("RGB")
        for faixa in (0, 1):
            x, y = 40 + i * passo, 30 + faixa * (lin + 10)
            for t in tam:
                k = 3
                big = im.resize((t * k, t * k), Image.LANCZOS)
                m = Image.new("L", (t * k, t * k), 0)
                ImageDraw.Draw(m).ellipse((0, 0, t * k - 1, t * k - 1), fill=255)
                big = big.resize((t, t), Image.LANCZOS)
                m = m.resize((t, t), Image.LANCZOS)
                folha.paste(big, (x, y), m)
                x += t + 18
    destino = os.path.join(AQUI, "saida", "perfil_previa.png")
    folha.save(destino)
    print(destino)
    return destino


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    vars_ = args or list(VARIANTES)
    saidas = exportar(vars_)
    previa(saidas)
    if "--final" in sys.argv:
        os.makedirs(DESTINO, exist_ok=True)
        nomes = {"rosa": "A - frajola de óculos (rosa).png", "jade": "B - frajola de óculos (jade).png", "bastet": "C - frajola de Bastet de óculos (rosa).png"}
        for var, png in saidas:
            shutil.copy(png, os.path.join(DESTINO, nomes[var]))
        print("copiado para", DESTINO)
