#!/usr/bin/env python3
"""Efeito de BRILHO viral (estrelinhas que cintilam em volta do rosto + clarão suave) e o som de brilhinhos.
Tudo sintetizado aqui (sem licença de terceiros). Feito para a edição Iara (22/11/2026).

    py brilho.py som <saida.wav>
    py brilho.py quadros <pasta_saida> [--fps 29.97] [--dur 1.7] [--cx 50] [--cy 24] [--seed 7]
    py brilho.py aplicar <video.mp4> <pasta_quadros> <t_inicio> <saida.mp4> [--fps 29.97]

som: cerca de 40 pings agudos (escala pentatônica, 2 a 7 kHz), densos no começo e rareando, glissando leve
para cima, com parcial de sino, pan aleatório e um eco curto. 1,4 s.
quadros: PNG RGBA 1080x1920. Estrelinhas de 4 pontas (raios finos, halo rosado e dourado) nascem em volta do
ponto (cx, cy)% (o rosto), crescem, giram, cintilam e somem; brilhinhos miúdos; clarão radial nos 0,6 s iniciais.
aplicar: sobrepõe os quadros ao vídeo a partir de t_inicio (áudio copiado).
"""
import argparse
import math
import random
import subprocess
from pathlib import Path

import numpy as np

W, H = 1080, 1920


def som(out):
    sr = 48000
    dur = 1.4
    n = int(sr * dur)
    L = np.zeros(n)
    R = np.zeros(n)
    rng = np.random.default_rng(11)
    escala = [2093, 2349, 2637, 3136, 3520, 4186, 4699, 5274, 6272, 7040]
    tt = np.arange(n) / sr
    for k in range(42):
        t0 = 0.95 * rng.random() ** 1.7
        f = escala[rng.integers(len(escala))] * (1 + 0.35 * t0)
        tau = rng.uniform(0.05, 0.16)
        amp = rng.uniform(0.35, 1.0) * (1 - 0.55 * t0)
        i0 = int(t0 * sr)
        m = min(n - i0, int(sr * tau * 7))
        x = tt[:m]
        env = np.minimum(1, x / 0.002) * np.exp(-x / tau)
        ping = amp * env * (np.sin(2 * math.pi * f * x) + 0.3 * np.sin(2 * math.pi * f * 2.76 * x) * np.exp(-x / (tau * 0.4)))
        pan = rng.uniform(0.15, 0.85)
        L[i0:i0 + m] += ping * math.cos(pan * math.pi / 2)
        R[i0:i0 + m] += ping * math.sin(pan * math.pi / 2)
    # chiado brilhante (ruído acima de ~5 kHz) que sobe e desce
    noise = rng.standard_normal(n)
    hp = noise - np.convolve(noise, np.ones(6) / 6, mode="same")
    env = np.sin(math.pi * np.clip(tt / 0.9, 0, 1)) ** 2
    L += 0.10 * hp * env
    R += 0.10 * np.roll(hp, 37) * env
    st = np.stack([L, R], 1)
    st /= np.abs(st).max() * 1.12
    raw = Path(out).with_suffix(".raw.wav")
    from scipy.io import wavfile
    wavfile.write(str(raw), sr, (st * 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
                    "aecho=0.8:0.55:45|80|125:0.32|0.22|0.14,afade=t=out:st=1.15:d=0.25", "-ar", str(sr), str(out)], check=True)
    raw.unlink()
    print("som:", out)


def estrela(d, cx, cy, r, ang, cor, raio_fino=0.10):
    """4 pontas: dois losangos finos cruzados (grandes) + dois menores na diagonal."""
    for k, (rr, w) in enumerate(((r, r * raio_fino), (r, r * raio_fino), (r * 0.45, r * 0.07), (r * 0.45, r * 0.07))):
        a = ang + k * math.pi / 2 if k < 2 else ang + math.pi / 4 + (k - 2) * math.pi / 2
        ca, sa = math.cos(a), math.sin(a)
        pts = [(cx + ca * rr, cy + sa * rr), (cx - sa * w, cy + ca * w), (cx - ca * rr, cy - sa * rr), (cx + sa * w, cy - ca * w)]
        d.polygon(pts, fill=cor)
    d.ellipse([cx - r * 0.13, cy - r * 0.13, cx + r * 0.13, cy + r * 0.13], fill=cor)


def quadros(pasta, fps, dur, cx, cy, seed):
    from PIL import Image, ImageDraw, ImageFilter
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(seed)
    X, Y = cx / 100 * W, cy / 100 * H
    stars = []
    for i in range(40):   # estrelas médias e grandes em volta do rosto (anel), algumas mais longe
        ang = rnd.uniform(0, 2 * math.pi)
        dist = rnd.uniform(0.24, 0.44) * W if i < 30 else rnd.uniform(0.44, 0.6) * W
        x = X + math.cos(ang) * dist
        y = Y + math.sin(ang) * dist * 1.25
        if not (40 < x < W - 40 and 40 < y < H * 0.78):
            continue
        if ((x - X) / (0.19 * W)) ** 2 + ((y - Y) / (0.15 * H)) ** 2 < 1:   # nunca em cima do rosto
            continue
        stars.append(dict(x=x, y=y, t0=rnd.uniform(0, dur * 0.55), life=rnd.uniform(0.5, 0.85),
                          r=rnd.uniform(45, 95) if i % 4 else rnd.uniform(120, 170), a0=rnd.uniform(0, 0.6),
                          spin=rnd.uniform(-0.9, 0.9), tint=rnd.choice([(255, 214, 230), (255, 236, 200), (255, 245, 250)])))
    glints = [dict(x=rnd.uniform(60, W - 60), y=rnd.uniform(80, H * 0.75), t0=rnd.uniform(0, dur * 0.7),
                   life=rnd.uniform(0.25, 0.5), r=rnd.uniform(7, 16)) for _ in range(46)]
    nf = int(round(dur * fps))
    yy, xx = np.mgrid[0:H // 4, 0:W // 4]
    dist = np.sqrt(((xx * 4 - X) / W) ** 2 + ((yy * 4 - Y) / W * 0.8) ** 2)
    radial = np.clip(1 - dist / 0.75, 0, 1) ** 2
    for f in range(nf):
        t = f / fps
        base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        # clarão radial: sobe em 0,12 s, some até 0,7 s
        fl = 0.22 * (min(1, t / 0.12) if t < 0.12 else max(0, 1 - (t - 0.12) / 0.58))
        if fl > 0.003:
            a = (radial * fl * 255).astype(np.uint8)
            lay = np.dstack([np.full_like(a, 255), np.full_like(a, 238), np.full_like(a, 244), a])
            base.alpha_composite(Image.fromarray(lay, "RGBA").resize((W, H), Image.BILINEAR))
        glow = Image.new("RGBA", (W // 2, H // 2), (255, 228, 238, 0))   # fundo claro: o borrão não puxa preto
        core = Image.new("RGBA", (W, H), (255, 255, 255, 0))
        dg, dc = ImageDraw.Draw(glow), ImageDraw.Draw(core)
        for s in stars:
            u = (t - s["t0"]) / s["life"]
            if not 0 <= u <= 1:
                continue
            k = math.sin(math.pi * u) ** 0.8 * (0.85 + 0.15 * math.sin(u * 22))   # cresce, cintila, some
            r = s["r"] * k
            ang = s["a0"] + s["spin"] * u
            al = int(255 * min(1, 1.6 * math.sin(math.pi * u)))
            estrela(dg, s["x"] / 2, s["y"] / 2, r * 0.75, ang, s["tint"] + (int(al * 0.85),), 0.22)
            estrela(dc, s["x"], s["y"], r, ang, (255, 255, 255, al))
        for g in glints:
            u = (t - g["t0"]) / g["life"]
            if 0 <= u <= 1:
                k = math.sin(math.pi * u)
                al = int(255 * k)
                estrela(dc, g["x"], g["y"], g["r"] * (0.6 + 0.4 * k), 0, (255, 255, 255, al), 0.16)
                dg.ellipse([g["x"] / 2 - 6 * k, g["y"] / 2 - 6 * k, g["x"] / 2 + 6 * k, g["y"] / 2 + 6 * k], fill=(255, 225, 238, int(al * 0.6)))
        glow = glow.filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR)
        base.alpha_composite(glow)
        base.alpha_composite(glow)
        base.alpha_composite(core.filter(ImageFilter.GaussianBlur(0.8)))
        base.save(pasta / f"{f:04d}.png")
    print(f"quadros: {nf} em {pasta}")


def aplicar(video, pasta, t0, out, fps):
    fc = (f"[1:v]format=rgba,setpts=PTS-STARTPTS+{t0}/TB[s];"
          f"[0:v][s]overlay=eof_action=pass:format=auto,format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-framerate", str(fps), "-i", str(Path(pasta) / "%04d.png"),
                    "-filter_complex", fc, "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "16", "-preset", "slow",
                    "-c:a", "copy", "-movflags", "+faststart", str(out)], check=True)
    print("aplicado:", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["som", "quadros", "aplicar"])
    ap.add_argument("args", nargs="+")
    ap.add_argument("--fps", type=float, default=29.97)
    ap.add_argument("--dur", type=float, default=1.7)
    ap.add_argument("--cx", type=float, default=50)
    ap.add_argument("--cy", type=float, default=24)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    if a.modo == "som":
        som(a.args[0])
    elif a.modo == "quadros":
        quadros(a.args[0], a.fps, a.dur, a.cx, a.cy, a.seed)
    else:
        aplicar(a.args[0], a.args[1], float(a.args[2]), a.args[3], a.fps)


if __name__ == "__main__":
    main()
