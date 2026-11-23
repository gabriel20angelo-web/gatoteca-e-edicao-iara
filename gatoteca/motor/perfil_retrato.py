# -*- coding: utf-8 -*-
"""FOTO DE PERFIL da Gatoteca Entrelinhas: retrato do frajola (rosto + um pouco do peito) diante de uma estante.

Mesmo gato do perfil_whatsapp.py (pose «sentado» do banco), so que enquadrado de perto, como retrato.
Fundo: estante de livros na paleta, em papel texturizado, levemente desfocada, com uma luz quente de
abajur atras da cabeca para o rosto destacar. Sem texto.

Variantes:  oculos -> de oculos redondos de ouro
            sem    -> sem oculos (olhos de brilho a mostra)
uso: py perfil_retrato.py [oculos sem] [--final]
"""
import os, sys, random, shutil
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "mascote"))
import montar
from papel import papel
import gato_banco as G
import gato_banco2 as G2
from gato_banco import Pose, sentado
import perfil_whatsapp as PW
from perfil_whatsapp import b64, clarear, W, JADE, ROSA, NOITE, AMEIXA, OURO, VINHO, CONTORNO

DESTINO = os.path.join(PW.D, "WhatsApp - foto de perfil (retrato)")
ESCALA, CX, CY_CABECA = 2.55, 540, 540     # cabeca do gato (y = -261 na figura) vai para (540, 520)
MADEIRA = "#4A3340"


def gato(var):
    p = Pose("91", "retrato", "", "", centro=(0, -200))
    p.seed = 4200
    if var == "oculos":
        sentado(p, rabo_cima=False, cabeca=dict(acess=[G2.oculos_redondos().replace(G2.OURO, OURO)]))
    else:
        sentado(p, rabo_cima=False, cabeca=dict(acess=[]))
    return p


def estante(seed=7):
    """Tres prateleiras de lombadas em pe (e uma pilha deitada de vez em quando), na paleta do clube."""
    rnd = random.Random(seed)
    cores = [VINHO, JADE, ROSA, AMEIXA, OURO, NOITE, "#7C4A5A", "#3F5E57", "#A9707F", "#8A6E3A", "#E6D2C3"]
    s = ""
    pratos = [(-40, 300), (300, 640), (640, 980), (980, 1320)]   # (topo, base) de cada vao
    for topo, base in pratos:
        x = -20
        while x < W + 20:
            if rnd.random() < .08:   # pilha deitada
                w = rnd.randint(150, 200)
                y = base
                for k in range(rnd.randint(3, 5)):
                    h = rnd.randint(26, 36)
                    c = rnd.choice(cores)
                    dx = rnd.randint(-8, 8)
                    s += '<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s" stroke="%s" stroke-width="3"/>' % (x + dx, y - h, w, h, c, CONTORNO)
                    s += '<path d="M%d,%d V%d M%d,%d V%d" stroke="%s" stroke-width="3"/>' % (x + dx + 18, y - h + 4, y - 4, x + dx + w - 18, y - h + 4, y - 4, OURO)
                    y -= h
                x += w + 10
                continue
            w = rnd.randint(34, 70)
            h = rnd.randint(int((base - topo) * .62), int((base - topo) * .9))
            c = rnd.choice(cores)
            inc = rnd.choice([0] * 8 + [-6, 7])
            g = '<g transform="rotate(%d %d %d)">' % (inc, x + w / 2, base) if inc else "<g>"
            g += '<rect x="%d" y="%d" width="%d" height="%d" rx="3" fill="%s" stroke="%s" stroke-width="3"/>' % (x, base - h, w, h, c, CONTORNO)
            g += '<rect x="%d" y="%d" width="%d" height="%d" fill="#000" opacity=".18"/>' % (x + w * .72, base - h + 2, w * .26, h - 4)
            g += '<rect x="%d" y="%d" width="%d" height="%d" fill="#FFF" opacity=".12"/>' % (x + w * .12, base - h + 2, w * .14, h - 4)
            friso = OURO if c not in (OURO, "#8A6E3A") else VINHO
            for f in (.1, .14, .86, .9):
                g += '<path d="M%d,%d H%d" stroke="%s" stroke-width="3"/>' % (x + 4, base - h + h * f, x + w - 4, friso)
            if rnd.random() < .55:
                eh = rnd.randint(40, 70)
                g += '<rect x="%d" y="%d" width="%d" height="%d" rx="2" fill="#F4EAD6" stroke="%s" stroke-width="2"/>' % (x + w * .2, base - h * .62, w * .6, eh, CONTORNO)
            s += g + "</g>"
            x += w + rnd.choice([0, 0, 2, 4])
        # a prateleira (tabua) na base do vao
        s += '<rect x="-20" y="%d" width="%d" height="34" fill="%s" stroke="%s" stroke-width="3"/>' % (base, W + 40, MADEIRA, CONTORNO)
        s += '<rect x="-20" y="%d" width="%d" height="6" fill="#FFF" opacity=".12"/>' % (base + 3, W + 40)
        s += '<rect x="-20" y="%d" width="%d" height="22" fill="#000" opacity=".25"/>' % (base + 34, W + 40)
    return s


def peca(var):
    p = gato(var)
    s = ESCALA
    tx, ty = CX, CY_CABECA + 261 * s
    textura = b64(papel(W, W, "#C9B2A8", 93, forca=1.6, fibras=2.4, pintas=.7, borda=.0, relevo=.24))
    defs = PW.DEFS + '''
<filter id="desfoque"><feGaussianBlur stdDeviation="2.6"/></filter>
<radialGradient id="abajur" cx="50%" cy="46%" r="50%"><stop offset="0" stop-color="#FFE9C2" stop-opacity="1"/>
 <stop offset=".45" stop-color="#F6CFA0" stop-opacity=".7"/><stop offset="1" stop-color="#F6CFA0" stop-opacity="0"/></radialGradient>
<radialGradient id="vinheta" cx="50%" cy="45%" r="72%"><stop offset=".55" stop-color="#1E1520" stop-opacity="0"/>
 <stop offset="1" stop-color="#1E1520" stop-opacity=".62"/></radialGradient>'''
    svg = ('<svg class="arte" viewBox="0 0 %d %d" width="%d" height="%d"><defs>%s%s</defs>' % (W, W, W, W, G.DEFS_EXTRA, defs) +
           '<rect width="%d" height="%d" fill="%s"/>' % (W, W, NOITE) +
           '<g filter="url(#desfoque)">%s</g>' % estante() +
           # papel por cima da estante: a estante tambem e impressa em papel
           '<image href="%s" x="0" y="0" width="%d" height="%d" style="mix-blend-mode:multiply" opacity=".85"/>' % (textura, W, W) +
           '<rect width="%d" height="%d" fill="%s" opacity=".28"/>' % (W, W, NOITE) +
           '<circle cx="%d" cy="%d" r="470" fill="url(#abajur)" style="mix-blend-mode:screen"/>' % (CX, CY_CABECA - 10) +
           '<rect width="%d" height="%d" fill="url(#vinheta)"/>' % (W, W) +
           '<g transform="translate(%g %g) scale(%g)">%s</g></svg>' % (tx, ty, s, "".join(p.camadas)))
    css = ('*{margin:0;padding:0;box-sizing:border-box}html,body{width:%dpx;height:%dpx;background:%s}'
           '.peca{position:relative;width:%dpx;height:%dpx;overflow:hidden}'
           '.peca::before,.peca::after{content:"";position:absolute;inset:0;pointer-events:none;background-size:%dpx %dpx;z-index:5}'
           '.peca::before{background-image:var(--grao-neg);mix-blend-mode:multiply;opacity:.5}'
           '.peca::after{background-image:var(--grao-pos);mix-blend-mode:plus-lighter;opacity:.4}'
           '.arte{position:absolute;left:0;top:0;overflow:hidden}') % (W, W, NOITE, W, W, W, int(W * 4 / 3))
    return '<!doctype html><html><head><meta charset="utf-8"><title>Gatoteca · retrato (%s)</title>\n<!--ACERVO-->\n<style>%s</style></head><body><div class="peca">%s</div></body></html>' % (var, css, svg)


if __name__ == "__main__":
    PW.peca = peca   # reaproveita exportar() e previa() do perfil do grupo
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    vars_ = args or ["oculos", "sem"]
    from playwright.sync_api import sync_playwright
    saidas = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for var in vars_:
            html = peca(var).replace("<!--ACERVO-->", montar.ACERVO_CSS)
            arq = os.path.join(AQUI, "saida", "retrato_%s.final.html" % var)
            open(arq, "w", encoding="utf-8").write(html)
            pg = b.new_page(viewport={"width": W, "height": W})
            pg.goto("file:///" + arq.replace("\\", "/"))
            pg.wait_for_timeout(1200)
            png = os.path.join(AQUI, "saida", "retrato_%s.png" % var)
            pg.screenshot(path=png)
            pg.close()
            saidas.append((var, png))
            print(png)
        b.close()
    prev = PW.previa(saidas)
    if "--final" in sys.argv:
        os.makedirs(DESTINO, exist_ok=True)
        nomes = {"oculos": "A - retrato de óculos.png", "sem": "B - retrato sem óculos.png"}
        for var, png in saidas:
            shutil.copy(png, os.path.join(DESTINO, nomes[var]))
        shutil.copy(prev, os.path.join(DESTINO, "0 - prévia no WhatsApp (claro e escuro).png"))
        print("copiado para", DESTINO)
