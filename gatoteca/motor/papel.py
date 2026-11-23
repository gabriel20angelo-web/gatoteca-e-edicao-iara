# -*- coding: utf-8 -*-
"""Texturas de PAPEL geradas (numpy): manchas em varias escalas, fibras, poros, pintas de envelhecimento,
borda mais escura. Cada papel sai como PNG colorido pronto para preencher formas (pattern/clip).

papel(w, h, cor, seed, forca, fibras, pintas, borda) -> caminho do PNG (cache em texturas/)
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(AQUI, "texturas")
os.makedirs(CACHE, exist_ok=True)


def _ruido(h, w, escala, rng):
    """Ruido suave: aleatorio pequeno ampliado (bicubico) ate o tamanho."""
    sh, sw = max(2, int(h / escala)), max(2, int(w / escala))
    base = rng.random((sh, sw)).astype(np.float32)
    im = Image.fromarray((base * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(im).astype(np.float32) / 255 - .5


def papel(w, h, cor, seed=1, forca=2.0, fibras=2.6, pintas=1.0, borda=.14, relevo=.32, nome=None):
    nome = nome or "papel3_%dx%d_%s_%d_%g_%g_%g_%g_%g.png" % (w, h, cor.strip("#"), seed, forca, fibras, pintas, borda, relevo)
    caminho = os.path.join(CACHE, nome)
    if os.path.exists(caminho):
        return caminho
    rng = np.random.default_rng(seed)
    rgb = np.array([int(cor[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
    escuro = rgb.mean() < .35
    # manchas em tres escalas + grao fino
    m = (_ruido(h, w, 260, rng) * .09 + _ruido(h, w, 70, rng) * .06 + _ruido(h, w, 14, rng) * .035) * forca
    grao = (rng.random((h, w)).astype(np.float32) - .5) * .045 * forca
    lum = 1 + m + grao
    # relevo: o «dente» do papel iluminado de lado (alto a esquerda)
    alt = _ruido(h, w, 1.6, rng) * .7 + _ruido(h, w, 4, rng) * .3
    alt = np.asarray(Image.fromarray(((alt + .5) * 255).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.6))).astype(np.float32) / 255
    gy, gx = np.gradient(alt)
    lum += (-gx * .9 - gy * .9) * 1.6 * relevo
    # borda mais escura (manuseio)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy)) / max(w, h)
    lum *= 1 - borda * np.exp(-d / .045)
    img = np.clip(rgb[None, None, :] * lum[..., None], 0, 1)
    if escuro:  # papel escuro: as fibras e manchas sobem para o claro
        img = np.clip(img + (m[..., None] * .35 * forca), 0, 1)
    out = Image.fromarray((img * 255).astype(np.uint8), "RGB").convert("RGBA")
    # fibras: tracos curvos finos, claros e escuros, desenhados em 2x
    k = 2
    cam = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    dr = ImageDraw.Draw(cam)
    n = int(w * h / 900 * fibras)
    claro = tuple(int(min(255, c * 255 * 1.18 + 18)) for c in rgb)
    esc = tuple(int(c * 255 * .72) for c in rgb)
    for _ in range(n):
        x, y = rng.random() * w * k, rng.random() * h * k
        L = (8 + rng.random() * 34) * k
        a = rng.random() * math.pi
        cur = (rng.random() - .5) * 1.2
        pts = []
        for t in np.linspace(0, 1, 6):
            aa = a + cur * t
            pts.append((x + math.cos(aa) * L * t, y + math.sin(aa) * L * t))
        c = claro if rng.random() < .6 else esc
        dr.line(pts, fill=c + (int(40 + rng.random() * 50),), width=1)
    # pintas (inclusoes) e manchas de envelhecimento
    for _ in range(int(w * h / 5200 * pintas)):
        x, y = rng.random() * w * k, rng.random() * h * k
        r = (.6 + rng.random() * 1.6) * k
        dr.ellipse((x - r, y - r, x + r, y + r), fill=esc + (int(60 + rng.random() * 90),))
    for _ in range(int(w * h / 160000 * pintas) + 1):
        x, y = rng.random() * w * k, rng.random() * h * k
        r = (10 + rng.random() * 40) * k
        tom = (176, 132, 92) if not escuro else claro
        dr.ellipse((x - r, y - r, x + r, y + r), fill=tom + (int(10 + rng.random() * 14),))
    cam = cam.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(.35))
    out.alpha_composite(cam)
    out.convert("RGB").save(caminho)
    return caminho


def rasgado(x0, y0, w, h, seed=1, amp=3.0, passo=7, lados="tblr", morder=.0):
    """Contorno de papel rasgado (lados listados irregulares); devolve path SVG."""
    rng = np.random.default_rng(seed)

    def lado(p0, p1, irregular):
        (ax, ay), (bx, by) = p0, p1
        n = max(2, int(math.hypot(bx - ax, by - ay) / passo))
        nx, ny = -(by - ay), (bx - ax)
        m = math.hypot(nx, ny) or 1
        nx, ny = nx / m, ny / m
        pts = []
        for i in range(n):
            t = i / n
            o = (rng.normal() * amp + (rng.random() < morder) * rng.random() * amp * 4) if irregular else 0
            pts.append((ax + (bx - ax) * t + nx * o, ay + (by - ay) * t + ny * o))
        return pts
    c = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]
    pts = lado(c[0], c[1], "t" in lados) + lado(c[1], c[2], "r" in lados) + lado(c[2], c[3], "b" in lados) + lado(c[3], c[0], "l" in lados)
    return "M" + " L".join("%.1f,%.1f" % p for p in pts) + "Z"


if __name__ == "__main__":
    for cor in ("#EFE2D4", "#2E2A36", "#5F857C", "#FAF5EE", "#C799AA"):
        p = papel(600, 600, cor, 3)
        print(p)
