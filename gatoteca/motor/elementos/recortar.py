# -*- coding: utf-8 -*-
"""Recorta os elementos das folhas de referencia (fundo liso) em PNG transparente.

Fundo liso: distancia de cor ao fundo -> mascara -> fechar, preencher buracos pequenos, separar
componentes. Cada recorte vai para brutos/<folha>_NN.png + uma folha de contato numerada para eu
nomear e classificar (o nome e a categoria vem de catalogo.py).
"""
import os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as ndi
from skimage import morphology, measure, segmentation
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[3]  # raiz do repositório

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIG = str(_REPO / 'gatoteca/motor/elementos/brutos')
BRUTOS = os.path.join(AQUI, "brutos")
os.makedirs(BRUTOS, exist_ok=True)

FOLHAS = {
    # nome curto: (arquivo, tolerancia, buraco_max, fechar, area_min)
    # nome curto: (arquivo, tolerancia, buraco_max, fechar, area_min, separar)
    "selos_rosa": ("download (7).jpg", 16, 6000, 3, 900, 3),
    "selos_lilas": ("download (6).jpg", 14, 6000, 3, 900, 12),
    "espelho": ("mentally i am here.jpg", 14, 4000, 2, 600, 0),
    "lanternas": ("download (5).jpg", 10, 8000, 2, 900, 6),
    "colagem": ("download (4).jpg", 14, 5000, 3, 250, 6),
    "sol_lua": ("download (3).jpg", 14, 5000, 3, 250, 3),
    "lacre_vinho": ("download (2).jpg", 14, 3000, 3, 900, 0),
}


def recorta(nome, arq, tol, buraco, fechar, area_min, separar=0):
    im = Image.open(os.path.join(ORIG, arq)).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    h, w, _ = a.shape
    cantos = np.array([a[2, 2], a[2, w - 3], a[h - 3, 2], a[h - 3, w - 3]])
    fundo = np.median(cantos, axis=0)
    dist = np.abs(a - fundo).max(axis=2)
    fg = dist > tol
    fg = morphology.binary_closing(fg, morphology.disk(fechar))
    fg = morphology.remove_small_holes(fg, area_threshold=buraco)
    fg = morphology.remove_small_objects(fg, max_size=area_min)
    if separar:
        # pecas que se encostam: encolhe ate soltarem, rotula, e devolve a borda a cada uma
        miolo = ndi.binary_erosion(fg, structure=morphology.disk(separar))
        marcas = measure.label(miolo, connectivity=2)
        rot = segmentation.expand_labels(marcas, distance=separar + 3) * fg
    else:
        rot = measure.label(fg, connectivity=2)
    saida = []
    for r in measure.regionprops(rot):
        if r.area < area_min:
            continue
        y0, x0, y1, x1 = r.bbox
        pad = 3
        y0, x0, y1, x1 = max(0, y0 - pad), max(0, x0 - pad), min(h, y1 + pad), min(w, x1 + pad)
        m = (rot[y0:y1, x0:x1] == r.label)
        m = ndi.binary_erosion(m, structure=morphology.disk(1))  # tira a franja do fundo
        if m.sum() < area_min * .6:
            continue
        alfa = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.7))
        rgba = im.crop((x0, y0, x1, y1)).convert("RGBA")
        rgba.putalpha(alfa)
        i = len(saida) + 1
        p = os.path.join(BRUTOS, "%s_%02d.png" % (nome, i))
        rgba.save(p)
        saida.append(dict(folha=nome, n=i, arquivo=os.path.basename(p), w=x1 - x0, h=y1 - y0, x=x0, y=y0))
    return saida


def y0_ok(ys, h):
    return ys.max() < h - 30  # a ultima renda vem cortada pela borda


def renda():
    """Rendas: cada faixa vira uma tinta de cor unica com alfa pela distancia ao papel (recoloriveis)."""
    im = Image.open(os.path.join(ORIG, "Canva Elements_ Lace Borders.jpg")).convert("RGB")
    a = np.asarray(im).astype(np.float32)
    h, w, _ = a.shape
    # papel: mediana por linha nas bordas esquerda/direita estreitas nao serve (renda vai de ponta a ponta);
    # usamos o papel das faixas vazias entre as rendas, interpolado por linha
    lum = a.mean(axis=2)
    escuro = (np.abs(a - a.reshape(-1, 3).mean(0)).max(axis=2))
    # linhas "vazias" = pouca variacao horizontal
    var = a.std(axis=1).mean(axis=1)
    vazia = var < 6
    papel = np.zeros((h, 3), np.float32)
    idx = np.where(vazia)[0]
    for c in range(3):
        papel[:, c] = np.interp(np.arange(h), idx, a[idx, :, c].mean(axis=1))
    dist = np.abs(a - papel[:, None, :]).max(axis=2)
    ocupada = ~vazia
    ocupada[:150] = False  # titulo "Canva Elements / keyword"
    rot, n = ndi.label(ndi.binary_closing(ocupada, iterations=4))
    saida = []
    for k in range(1, n + 1):
        ys = np.where(rot == k)[0]
        if len(ys) < 25 or y0_ok(ys, h) is False:
            continue
        y0, y1 = ys.min(), ys.max() + 1
        faixa = a[y0:y1]
        d = dist[y0:y1]
        forte = d > np.percentile(d, 90)
        cor = np.median(faixa[forte], axis=0)
        alfa = np.clip((d - 10) / 42.0, 0, 1)
        rgba = np.zeros((y1 - y0, w, 4), np.uint8)
        rgba[..., :3] = cor.astype(np.uint8)
        rgba[..., 3] = (alfa * 255).astype(np.uint8)
        i = len(saida) + 1
        p = os.path.join(BRUTOS, "renda_%02d.png" % i)
        Image.fromarray(rgba, "RGBA").save(p)
        saida.append(dict(folha="renda", n=i, arquivo=os.path.basename(p), w=w, h=int(y1 - y0), cor="#%02X%02X%02X" % tuple(int(c) for c in cor)))
    return saida


def contato(itens, destino, cel=180):
    fonte = ImageFont.truetype(os.path.join(os.path.dirname(AQUI), "fontes", "CormorantGaramond.ttf"), 20)
    cols = 8
    linhas = (len(itens) + cols - 1) // cols
    im = Image.new("RGB", (cols * cel, linhas * (cel + 24)), (205, 200, 196))
    d = ImageDraw.Draw(im)
    for i, it in enumerate(itens):
        g = Image.open(os.path.join(BRUTOS, it["arquivo"]))
        g.thumbnail((cel - 16, cel - 16))
        x, y = (i % cols) * cel, (i // cols) * (cel + 24)
        im.paste(g, (x + (cel - g.width) // 2, y + (cel - g.height) // 2), g)
        d.text((x + 6, y + cel), it["arquivo"].replace(".png", ""), fill=(40, 30, 40), font=fonte)
    im.save(destino)


if __name__ == "__main__":
    todos = []
    for nome, cfg in FOLHAS.items():
        r = recorta(nome, *cfg)
        print(nome, len(r))
        todos += r
    r = renda()
    print("renda", len(r))
    todos += r
    json.dump(todos, open(os.path.join(AQUI, "brutos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    contato(todos, os.path.join(AQUI, "_contato_brutos.png"))
