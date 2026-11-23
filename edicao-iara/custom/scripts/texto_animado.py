#!/usr/bin/env python3
"""DESTAQUES de texto animado (tipografia cinética) para a edição Iara (22/11/2026).

Nos momentos de destaque a legenda some, entra a frase grande e animada, palavra por palavra, e depois a legenda
volta. O texto é desenhado aqui (PIL) e sobreposto ao render com ffmpeg, como o brilho.py.

    py texto_animado.py plano   <edit> <destaques.json>     # tira da legenda (plan.json) as palavras das janelas
    py texto_animado.py quadros <edit> <destaques.json>     # PNG RGBA de cada bloco em <edit>/_olho/destaque_<nome>/
    py texto_animado.py aplicar <edit> <destaques.json> <entrada.mp4> <saida.mp4> [--extra pasta:t0 ...]

destaques.json: {"fps": 29.97, "blocos": [...]}. Bloco "linhas": páginas de linhas empilhadas a partir de y_top (%);
cada linha tem t (ou ts, um tempo por palavra), texto, fonte (arquivo em custom/fonts), peso, tam (px), cor e
"soco" (a última palavra entra com soco e tremida). A página sai (sobe e esmaece) no seu "ate". Bloco "pecas":
uma palavra grande cujas letras voam de pedaços espalhados e se montam no lugar (y em %).
"""
import argparse
import json
import math
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FONTS = Path(__file__).resolve().parent.parent / "fonts"
MARGEM = 70


def fonte(nome, tam, peso=None):
    f = ImageFont.truetype(str(FONTS / nome), tam)
    if peso:
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
    return f


def cor(hexa):
    hexa = hexa.lstrip("#")
    return tuple(int(hexa[i:i + 2], 16) for i in (0, 2, 4))


def sprite(texto, f, rgb, pad=40):
    """Palavra com sombra suave, recortada com folga. Devolve (imagem, deslocamento do ponto de origem)."""
    l, t, r, b = f.getbbox(texto)
    w, h = r - l + 2 * pad, b - t + 2 * pad
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((pad - l + 2, pad - t + 5), texto, font=f, fill=(20, 10, 15, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    tx = Image.new("RGBA", (w, h), (*rgb, 0))
    ImageDraw.Draw(tx).text((pad - l, pad - t), texto, font=f, fill=(*rgb, 255))
    sh.alpha_composite(tx)
    return sh, (l - pad, t - pad)


def ease_out_back(p, s=1.4):
    p -= 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2


def ease_out_cubic(p):
    return 1 - (1 - p) ** 3


def colar(base, img, cx, cy, escala=1.0, alfa=1.0, rot=0.0):
    if alfa <= 0.01 or escala <= 0.01:
        return
    if abs(escala - 1) > 0.002 or rot:
        nw, nh = max(1, int(img.width * escala)), max(1, int(img.height * escala))
        img = img.resize((nw, nh), Image.LANCZOS)
        if rot:
            img = img.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alfa < 0.999:
        a = img.getchannel("A").point(lambda v: int(v * alfa))
        img = img.copy()
        img.putalpha(a)
    base.alpha_composite(img, (int(round(cx - img.width / 2)), int(round(cy - img.height / 2))))


def montar_linhas(bloco):
    """Pré-desenha as palavras e calcula onde cada uma fica (centro x, y) em cada página."""
    paginas = []
    for pg in bloco["paginas"]:
        y = bloco["y_top"] / 100 * H
        linhas = []
        for ln in pg["linhas"]:
            tam = ln["tam"]
            palavras = ln["texto"].split()
            while True:   # encolhe a linha até caber na largura
                f = fonte(ln["fonte"], tam, ln.get("peso"))
                esp = f.getlength(" ")
                larg = sum(f.getlength(p) for p in palavras) + esp * (len(palavras) - 1)
                if larg <= W - 2 * MARGEM or tam < 30:
                    break
                tam = int(tam * 0.94)
            asc, desc = f.getmetrics()
            lh = asc + desc
            x = (W - larg) / 2
            ts = ln.get("ts") or [ln["t"] + 0.08 * i for i in range(len(palavras))]
            itens = []
            for i, p in enumerate(palavras):
                img, (ox, oy) = sprite(p, f, cor(ln.get("cor", "#FFFFFF")))
                # centro do sprite na tela: a origem do texto fica em (x, y)
                cx = x + ox + img.width / 2
                cy = y + oy + img.height / 2
                itens.append(dict(img=img, cx=cx, cy=cy, t=ts[i], soco=ln.get("soco") and i == len(palavras) - 1))
                x += f.getlength(p) + esp
            linhas.append(itens)
            y += lh * 1.02 + ln.get("depois", 10)
        paginas.append(dict(ate=pg["ate"], linhas=linhas))
    return paginas


def quadro_linhas(paginas, t, saida_s):
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for pg in paginas:
        sai = (t - (pg["ate"] - saida_s)) / saida_s
        if sai >= 1:
            continue
        sai = max(0.0, sai)
        for ln in pg["linhas"]:
            for it in ln:
                u = (t - it["t"]) / (0.42 if it["soco"] else 0.34)
                if u < 0:
                    continue
                u = min(1.0, u)
                alfa = min(1.0, u / 0.55) * (1 - ease_out_cubic(sai))
                dy = (1 - ease_out_back(u)) * 38 - ease_out_cubic(sai) * 34
                esc = 0.86 + 0.14 * ease_out_back(u)
                dx = 0.0
                if it["soco"]:
                    esc = 1.32 - 0.32 * ease_out_back(u, 2.2)
                    k = max(0.0, 1 - (t - it["t"]) / 0.35)
                    dx = math.sin((t - it["t"]) * 70) * 7 * k
                colar(base, it["img"], it["cx"] + dx, it["cy"] + dy, esc, alfa)
    return base


def montar_pecas(bloco, seed=5):
    f = fonte(bloco["fonte"], bloco["tam"], bloco.get("peso"))
    texto = bloco["texto"]
    larg = f.getlength(texto)
    x = (W - larg) / 2
    y = bloco["y"] / 100 * H
    rnd = random.Random(seed)
    letras = []
    for i, ch in enumerate(texto):
        img, (ox, oy) = sprite(ch, f, cor(bloco.get("cor", "#FFFFFF")), pad=36)
        letras.append(dict(img=img, cx=x + ox + img.width / 2, cy=y + oy + img.height / 2,
                           dx=rnd.uniform(-320, 320), dy=rnd.uniform(-260, 220), rot=rnd.uniform(-55, 55),
                           t=bloco["t0"] + 0.03 + 0.045 * i))
        x += f.getlength(ch)
    return letras


def quadro_pecas(letras, t, t1):
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sai = max(0.0, (t - (t1 - 0.3)) / 0.3)
    for L in letras:
        u = (t - L["t"]) / 0.55
        if u < 0:
            continue
        u = min(1.0, u)
        e = ease_out_cubic(u)
        alfa = min(1.0, u / 0.4) * (1 - sai)
        drift = math.sin((t - L["t"]) * 2.2) * 2   # respira de leve depois de montado
        colar(base, L["img"], L["cx"] + L["dx"] * (1 - e), L["cy"] + L["dy"] * (1 - e) + drift * e,
              (0.6 + 0.4 * e) * (1 + 0.05 * sai), alfa, L["rot"] * (1 - e))
    return base


def quadros(edit, spec):
    fps = spec["fps"]
    for b in spec["blocos"]:
        pasta = edit / "_olho" / f"destaque_{b['nome']}"
        pasta.mkdir(parents=True, exist_ok=True)
        for old in pasta.glob("*.png"):
            old.unlink()
        n = int(round((b["t1"] - b["t0"]) * fps))
        if b["tipo"] == "pecas":
            letras = montar_pecas(b)
            fn = lambda t: quadro_pecas(letras, t, b["t1"])   # noqa: E731
        else:
            paginas = montar_linhas(b)
            fn = lambda t: quadro_linhas(paginas, t, b.get("saida", 0.26))   # noqa: E731
        for k in range(n):
            fn(b["t0"] + k / fps).save(pasta / f"{k:04d}.png", compress_level=1)
        print(f"{b['nome']}: {n} quadros em {pasta}")


def plano(edit, spec):
    """Tira da legenda as palavras que caem nas janelas dos destaques; o resto do bloco fica, aparado."""
    p = edit / "plan.json"
    plan = json.loads(p.read_text(encoding="utf-8"))
    jan = [(b["t0"], b["t1"]) for b in spec["blocos"]]
    dentro = lambda w: any(a - 0.02 <= w["start"] < z for a, z in jan)   # noqa: E731
    novos = []
    for c in plan["captions"]["chunks"]:
        ws = [w for w in c["words"] if not dentro(w)]
        if not ws:
            continue
        if len(ws) < len(c["words"]):
            c = dict(c, words=ws, text=" ".join(w["text"] for w in ws))
            corte = min((a for a, z in jan if a >= ws[0]["start"]), default=None)
            if corte is not None:
                c["end"] = min(c["end"], corte)
        novos.append(c)
    tirados = len(plan["captions"]["chunks"]) - len(novos)
    plan["captions"]["chunks"] = novos
    p.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"legenda: {len(novos)} blocos ({tirados} tirados) fora das janelas {jan}")


def aplicar(edit, spec, entrada, saida, extras):
    fps = spec["fps"]
    camadas = [(edit / "_olho" / f"destaque_{b['nome']}", b["t0"]) for b in spec["blocos"]]
    for e in extras:
        pasta, t0 = e.rsplit(":", 1)
        camadas.append((Path(pasta), float(t0)))
    args = ["ffmpeg", "-v", "error", "-y", "-i", str(entrada)]
    fc, ant = [], "0:v"
    for i, (pasta, t0) in enumerate(camadas, 1):
        args += ["-framerate", str(fps), "-i", str(pasta / "%04d.png")]
        fc.append(f"[{i}:v]format=rgba,setpts=PTS-STARTPTS+{t0}/TB[s{i}]")
        fc.append(f"[{ant}][s{i}]overlay=eof_action=pass:format=auto[v{i}]")
        ant = f"v{i}"
    fc.append(f"[{ant}]format=yuv420p[v]")
    args += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "16",
             "-preset", "slow", "-c:a", "copy", "-movflags", "+faststart", str(saida)]
    subprocess.run(args, check=True)
    print("aplicado:", saida)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["plano", "quadros", "aplicar"])
    ap.add_argument("edit")
    ap.add_argument("spec")
    ap.add_argument("io", nargs="*")
    ap.add_argument("--extra", nargs="*", default=[])
    a = ap.parse_args()
    edit = Path(a.edit)
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    if a.modo == "plano":
        plano(edit, spec)
    elif a.modo == "quadros":
        quadros(edit, spec)
    else:
        aplicar(edit, spec, a.io[0], a.io[1], a.extra)


if __name__ == "__main__":
    main()
