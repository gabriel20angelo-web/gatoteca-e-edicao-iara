# -*- coding: utf-8 -*-
"""FOTO DE PERFIL da Gatoteca Entrelinhas, v2 (06/10): o frajola «menos fofo» (rosto de Bastet) de chapeu
de bruxo, ao lado da pilha de livros, sobre papel texturizado de cor lisa (sem estante: a v1 ficou poluida).
uso: py perfil_bruxo.py [jade noite ameixa] [--final]
"""
import os, sys, shutil
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI); sys.path.insert(0, os.path.join(AQUI, "mascote"))
import perfil_whatsapp as PW
import gato_banco2 as G2
from gato_banco import Pose, sentado
from shapely.geometry import box
from perfil_whatsapp import JADE, ROSA, NOITE, AMEIXA, OURO, VINHO

DESTINO = os.path.join(PW.D, "WhatsApp - foto de perfil (bruxo)")
PW.VARIANTES.update({
    "jade": dict(fundo=JADE, livros=[(212, VINHO, "lombada"), (186, ROSA, "paginas"), (200, AMEIXA, "lombada"), (160, OURO, "lombada")], fita=VINHO),
    "ameixa": dict(fundo=AMEIXA, livros=[(212, VINHO, "lombada"), (186, JADE, "paginas"), (200, ROSA, "lombada"), (160, OURO, "lombada")], fita=JADE),
    "noite": dict(fundo=NOITE, livros=[(212, VINHO, "lombada"), (186, JADE, "paginas"), (200, ROSA, "lombada"), (160, OURO, "lombada")], fita=OURO),
})
HAT_Y = float(os.environ.get("HAT_Y", "-20"))


def gato(var):
    import post_lilith5 as L5
    v = PW.VARIANTES[var]
    p = Pose("93", "bruxo", "", "", centro=(0, -200))
    p.seed = 4200
    livros_svg, topo, fita_svg = PW.pilha(v["livros"], -190, 2, v["fita"])
    p.svg(livros_svg + fita_svg, caixa=(-300, topo - 6, -80, 2))
    sentado(p, cabeca=None)
    L5.cabeca(p, 0, -258, 1.12, 0, olhar=(3, 1))
    p.svg('<g transform="translate(0 %g) scale(1.12)">%s</g>' % (-258 + HAT_Y, G2.chapeu_bruxa()))
    p.polis.append(box(-150, -258 - 1.12 * 290, 150, -180))
    return p


def lua(cx, cy, r, var):   # sem lua: so o papel e umas estrelinhas
    return ""


PW.gato, PW.lua = gato, lua
PW.ESCALA, PW.CENTRO_X, PW.CHAO = 1.28, 600, 900

if __name__ == "__main__":
    vars_ = [a for a in sys.argv[1:] if not a.startswith("--")] or ["jade", "ameixa", "noite"]
    saidas = PW.exportar(vars_)
    prev = PW.previa(saidas)
    if "--final" in sys.argv:
        os.makedirs(DESTINO, exist_ok=True)
        for i, (var, png) in enumerate(saidas):
            shutil.copy(png, os.path.join(DESTINO, "%s - bruxo (fundo %s).png" % ("ABC"[i], var)))
        shutil.copy(prev, os.path.join(DESTINO, "0 - prévia no WhatsApp (claro e escuro).png"))
        print("copiado para", DESTINO)
