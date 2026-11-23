#!/usr/bin/env python3
"""Sons delicados da «edição de vídeo Iara», além da tecla do editor.

    py sons_iara.py <edits/NOME> <cues.json>

cues.json: {"zooms_add": [{"start": s, "end": e, "scale": 1.15, "origin": [x, y]}],
            "cues": [{"som": "pagina|sino|grave|sopro", "t": segundos_do_evento}]}
Gera <edit>/sfx_iara/<som>.wav (sintetizado pelo ffmpeg, sem licença), nivela cada um
contra a fala do cut (kit.json speech_db, janela de 50 ms) e acrescenta as deixas ao plan.json
(o render toca qualquer arquivo dentro da pasta do edit). Rodar DEPOIS do último plan.py.
"""
import array
import json
import math
import subprocess
import sys
import wave
from pathlib import Path

SR = 48000
# som: (grafo ffmpeg sem entrada, dB abaixo da fala na janela mais alta de 50 ms)
SONS = {
    # virar de página: ruído com tremulação rápida (as folhas), banda de papel
    "pagina": ("anoisesrc=d=0.42:c=pink:a=1:r=48000:seed=4242,"
               "aeval='val(0)*pow(sin(PI*min(t\\,0.42)/0.42)\\,2)*(0.55+0.45*sin(2*PI*31*t))',"
               "highpass=f=900,lowpass=f=6500,afade=t=out:st=0.30:d=0.12", 14),
    # sininho: três parciais agudas, ataque curto, cauda de ~1,2 s
    "sino": ("aevalsrc='(0.6*sin(2*PI*1318.5*t)+0.35*sin(2*PI*1975.5*t)+0.18*sin(2*PI*2637*t))"
             "*(1-exp(-t*600))*exp(-t*3.2)':d=1.3:s=48000,afade=t=out:st=1.0:d=0.3", 16),
    # grave suave: queda de 70 para 42 Hz, sem estalo
    "grave": ("aevalsrc='sin(2*PI*(70*t-14*t*t))*(1-exp(-t*120))*exp(-t*3.5)':d=1.0:s=48000,"
              "afade=t=out:st=0.8:d=0.2", 8),
    # sopro leve do zoom: ar que sobe e some
    "sopro": ("anoisesrc=d=0.5:c=pink:a=1:r=48000:seed=77,highpass=f=500,lowpass=f=3500,"
              "afade=t=in:st=0:d=0.22:curve=exp,afade=t=out:st=0.24:d=0.26:curve=log", 15),
}


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


def gerar(edit, nome, speech_db):
    out = edit / "sfx_iara" / f"{nome}.wav"
    out.parent.mkdir(exist_ok=True)
    graph, under = SONS[nome]
    raw = out.with_suffix(".raw.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", graph, "-ac", "1", "-ar", str(SR),
                    "-c:a", "pcm_s16le", str(raw)], check=True)
    db, att = loudest50(pcm(raw))
    gain = (speech_db - under) - db
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"volume={gain:.2f}dB,alimiter=limit=0.9",
                    "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", str(out)], check=True)
    raw.unlink()
    return f"sfx_iara/{nome}.wav", att


def main():
    edit, cues = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    speech = json.loads((edit / ".sfx" / "kit.json").read_text(encoding="utf-8"))["speech_db"]
    plan_p = edit / "plan.json"
    plan = json.loads(plan_p.read_text(encoding="utf-8"))
    fps = plan["fps"]
    plan["sfx"] = [s for s in plan["sfx"] if not s["src"].startswith("sfx_iara/")]
    feitos = {}
    for c in cues.get("cues", []):
        if c["som"] not in feitos:
            feitos[c["som"]] = gerar(edit, c["som"], speech)
        src, att = feitos[c["som"]]
        t = round(round(max(0.0, c["t"] - att) * fps) / fps, 4)
        plan["sfx"].append({"t": t, "src": src, "event": round(c["t"], 3)})
    plan["sfx"].sort(key=lambda s: s["t"])
    for z in cues.get("zooms_add", []):
        plan["zooms"].append({"start": z["start"], "end": z["end"], "scale": z.get("scale", 1.15), "kind": "punch",
                              "ease_s": 0.0, "travel_s": 0.1, "origin": z.get("origin", [50, 20])})
    plan["zooms"].sort(key=lambda z: z["start"])
    plan_p.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(cues.get('cues', []))} deixas ({', '.join(sorted(feitos))}), fala {speech} dB; "
          f"{len(cues.get('zooms_add', []))} zoom(s) a mais -> {plan_p}")


if __name__ == "__main__":
    main()
