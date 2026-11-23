#!/usr/bin/env python3
"""Sons da versao 3 da «edicao de video Iara»: memes e whooshes (biblioteca do motion-studio, sem musica).

    py sons_v3.py <edits/NOME> [mapa.json] [--cues cues.json] [--zooms zooms.json]

--cues: lista [[t, som, dB abaixo], ...] no tempo do corte atual, no lugar da tabela CUES. Som procurado na biblioteca
do motion-studio e depois em custom/sounds/ (ex.: brilho.wav, de brilho.py).
--zooms: lista de zooms do plan.json (kind punch | push | out) que SUBSTITUI todos os zooms do plano.

mapa.json (opcional): [[t_desde, delta], ...] desloca os eventos quando o corte mudou (ex.: v3 -> v4).

Cada arquivo e nivelado contra a fala do cut (kit.json speech_db, janela de 50 ms): ganho = (speech_db - abaixo) - pico.
Grava em <edit>/sfx_v3/ e soma as deixas ao plan.json (t = evento - ataque, arredondado ao frame). Remove deixas antigas
(sfx_iara/, sfx_v3/) e as teclas automaticas .sfx/key* que caem em entrada de imagem (fica so a do titulo, t < 0.5).
Rodar DEPOIS do ultimo plan.py. Nada da pasta jp, koto ou musica.
"""
import array, json, math, subprocess, sys, wave
from pathlib import Path

SR = 48000
LIB = Path(__file__).resolve().parents[3] / "sons" / "virais"  # sons/virais do repositório
# (evento s, som, dB abaixo da fala)
CUES = [
    (0.10, "ding", 12), (4.12, "whoosh", 13), (5.64, "whip", 13), (7.00, "whoosh", 13), (10.83, "switch", 13),
    (15.30, "vine-boom", 8), (16.93, "whoosh", 13), (17.71, "shutter-old", 13), (21.19, "mouse-click", 13),
    (28.81, "whoosh", 13), (30.33, "ding", 12), (39.70, "record-scratch", 8), (40.76, "romance-meme", 10),
    (43.50, "page-turn", 13), (49.27, "page-turn", 13), (49.80, "yippee", 9), (51.87, "shutter-modern", 13),
    (53.70, "snapchat-notification", 9),
]
CUSTOM = Path(__file__).resolve().parent.parent / "sounds"
MAX_S = {"romance-meme": 1.2, "yippee": 1.4}      # sons longos: aparados com fade


def pcm(path):
    with wave.open(str(path)) as w:
        return array.array("h", w.readframes(w.getnframes()))


def loudest50(x):
    n, best, at = SR // 20, -120.0, 0
    for i in range(0, max(1, len(x) - n), n // 4):
        seg = x[i:i + n]
        r = math.sqrt(sum(v * v for v in seg) / max(1, len(seg))) / 32768
        db = 20 * math.log10(r) if r > 0 else -120.0
        if db > best:
            best, at = db, i + n // 2
    return best, at / SR


def gerar(edit, nome, under, speech_db):
    out = edit / "sfx_v3" / f"{nome}.wav"
    out.parent.mkdir(exist_ok=True)
    raw = out.with_suffix(".raw.wav")
    cut = []
    if nome in MAX_S:
        cut = ["-t", str(MAX_S[nome])]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(LIB / f"{nome}.wav" if (LIB / f"{nome}.wav").exists() else CUSTOM / f"{nome}.wav"), *cut, "-ac", "1", "-ar", str(SR),
                    "-c:a", "pcm_s16le", str(raw)], check=True)
    db, att = loudest50(pcm(raw))
    gain = (speech_db - under) - db
    fade = f",afade=t=out:st={MAX_S[nome] - 0.15:.2f}:d=0.15" if nome in MAX_S else ""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"volume={gain:.2f}dB{fade},alimiter=limit=0.9",
                    "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", str(out)], check=True)
    raw.unlink()
    return f"sfx_v3/{nome}.wav", att, db + gain


def main():
    edit = Path(sys.argv[1])
    speech = json.loads((edit / ".sfx" / "kit.json").read_text(encoding="utf-8"))["speech_db"]
    plan_p = edit / "plan.json"
    plan = json.loads(plan_p.read_text(encoding="utf-8"))
    fps = plan["fps"]
    plan["sfx"] = [s for s in plan["sfx"] if not s["src"].startswith(("sfx_iara/", "sfx_v3/"))
                   and not (s["src"].startswith(".sfx/key") and s["t"] >= 0.5)]
    feitos = {}
    evs = []
    args = sys.argv[2:]
    opt = {}
    while "--cues" in args or "--zooms" in args:
        k = next(i for i, a in enumerate(args) if a in ("--cues", "--zooms"))
        opt[args[k]] = json.loads(Path(args[k + 1]).read_text(encoding="utf-8"))
        del args[k:k + 2]
    mapa = json.loads(Path(args[0]).read_text()) if args else []
    cues = [tuple(c) for c in opt["--cues"]] if "--cues" in opt else CUES
    def mv(t):
        k = 0.0
        for t0, dl in mapa:
            if t >= t0:
                k = dl
        return round(t + k, 3)
    for ev, nome, under in cues:
        ev = mv(ev)
        k = (nome, under)
        if k not in feitos:
            feitos[k] = gerar(edit, nome, under, speech)
        src, att, _ = feitos[k]
        t = round(round(max(0.0, ev - att) * fps) / fps, 4)
        plan["sfx"].append({"t": t, "src": src, "event": ev})
        evs.append(ev)
    gaps = [round(b - a, 2) for a, b in zip(evs, evs[1:]) if b - a < 0.3]
    assert not gaps, f"deixas a menos de 0,3 s: {gaps}"
    plan["sfx"].sort(key=lambda s: s["t"])
    # zoom do vine-boom (15,3 a 16,7 s), refeito a cada rodada
    plan["zooms"] = [z for z in plan["zooms"] if abs(z["start"] - 15.3) > 0.01]
    plan["zooms"].append({"start": 15.3, "end": 16.7, "scale": 1.12, "kind": "punch", "ease_s": 0.0, "travel_s": 0.1, "origin": [50, 20]})
    if "--zooms" in opt:
        plan["zooms"] = opt["--zooms"]
    plan["zooms"].sort(key=lambda z: z["start"])
    plan_p.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(cues)} deixas, fala {speech} dB; pico de cada som (dB): " +
          ", ".join(f"{n}/{u}:{v[2]:.1f}" for (n, u), v in feitos.items()))


if __name__ == "__main__":
    main()
