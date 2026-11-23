#!/usr/bin/env python3
"""Versão COM SOBREPOSIÇÃO de falas de um corte (regra híbrida de 3 níveis, 22/11/2026).

    py sobrepor_video.py <fonte> <edit_dir> [--so-classificar]

<edit_dir> é uma cópia da edição original (decisions.json, report.json, words.raw.json,
words.json, captions.json, beats.json, cues_iara.json). O script:
  1. classifica cada emenda (interior / sobreposicao / corte_limpo / respiro) -> emendas.json
  2. monta cut.mp4 (1080x1920, vídeo reencodado por trecho, áudio somado em numpy, 48 kHz)
  3. regrava words.json, captions.json, beats.json, report.json e cues_iara.json com os tempos
     novos (os originais ficam em *.old.json; o script sempre lê o .old.json).

Regras (feedback_sobreposicao_hibrida_criterios + feedback_sobreposicao_sem_abaixar_nem_cortar):
  - só emenda ENTRE FRASES muda; emenda dentro da frase fica como no corte atual.
  - sobreposição: as duas vozes cheias, somadas; alvo 400 ms, teto = cauda + 0,45 x última palavra;
    folga de 40 ms antes do ataque da próxima frase; < 50 ms vira corte limpo.
  - corte limpo (C1 curta enfática, C2 número/termo-chave, C3 pergunta, C4 pausa > 2,5 s no cru,
    C5 citação): 110 ms entre o fim da voz e o ataque; pausa já longa (>= 0,5 s) é mantida.
  - respiro: depois da 1a frase, antes do "Aliás": pausa de até 1,0 s.
  - imagem: o quadro troca quando a voz seguinte começa; a cauda continua só no áudio (L-cut).
"""
import argparse
import bisect
import concurrent.futures as cf
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d

SR = 48000
HOP = 240          # 5 ms
WIN = 480          # 10 ms
THR = -24.0        # dB: voz
ALVO = 0.40
TETO = 0.45
FOLGA = 0.04
MIN_OV = 0.05
GAP_LIMPO = 0.11
GAP_MANTER = 0.5
RESP_MAX = 1.0
FADE = 0.008
C1_PALAVRAS, C1_DUR, C4_PAUSA = 10, 3.2, 2.5
import os
RENDER = Path(os.environ.get("EDITOR_DIR", str(Path.home() / "editor-por-referencia"))) / "plugins/ai-editor/skills/cut/scripts/render.py"
KEY_TERMS = set()   # C2: termos-chave finais (vazio aqui); números entram pelo regex


def load_render():
    spec = importlib.util.spec_from_file_location("cut_render", RENDER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def env_db(x):
    n = (len(x) - WIN) // HOP + 1
    out = np.empty(n, np.float32)
    for a in range(0, n, 4000):
        b = min(n, a + 4000)
        idx = np.arange(a, b)[:, None] * HOP + np.arange(WIN)[None, :]
        out[a:b] = np.sqrt((x[idx] ** 2).mean(1))
    return 20 * np.log10(out + 1e-7)


def last_voiced(db, t, back=4.0):
    k = int((t * SR - WIN) // HOP)
    lo = max(0, k - int(back / (HOP / SR)))
    for q in range(min(k, len(db) - 1), lo - 1, -1):
        if db[q] > THR:
            return q * HOP / SR + WIN / SR
    return None


def first_voiced(db, t, fwd=1.5):
    k = int(np.ceil(t * SR / HOP))
    hi = min(len(db), k + int(fwd / (HOP / SR)))
    for q in range(k, hi):
        if db[q] > THR:
            return q * HOP / SR + 0.005
    return None


def quiet(db, t0, t1):
    a, b = max(0, int(t0 * SR / HOP)), max(1, int(np.ceil(t1 * SR / HOP)))
    return b > a and float(np.max(db[a:b + 1])) < THR - 2


def backup_read(d, name):
    f, old = d / name, d / (Path(name).stem + ".old.json")
    if not old.exists():
        shutil.copy2(f, old)
    return json.loads(old.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("edit_dir")
    ap.add_argument("--so-classificar", action="store_true", help="grava emendas.json e para")
    a = ap.parse_args()
    d = Path(a.edit_dir)
    R = load_render()
    rep = backup_read(d, "report.json")
    fps, frames = rep["fps"], [tuple(f) for f in rep["frames"]]
    n = len(frames)
    total_src = R.packets(a.source)
    vstart, fstart = R.starts(a.source)
    off = vstart - fstart

    # ---- áudio da fonte (estéreo float) ----
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.source, "-vn", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True).stdout
    src = np.frombuffer(raw, np.float32).reshape(-1, 2)
    src_mono = src.mean(1)
    db_src = env_db(src_mono)

    def sl(t0, t1):   # fonte, segundos do arquivo
        i0, i1 = int(round(t0 * SR)), int(round(t1 * SR))
        seg = src[max(0, i0):max(0, i1)]
        if i0 < 0:
            seg = np.vstack([np.zeros((-i0, 2), np.float32), seg])
        need = i1 - i0
        if len(seg) < need:
            seg = np.vstack([seg, np.zeros((need - len(seg), 2), np.float32)])
        return seg

    # ---- corte antigo (só para medir voz/ataque) ----
    plen = [e - s for s, e in frames]
    cum_f = [0]
    for L in plen:
        cum_f.append(cum_f[-1] + L)
    old_audio = np.concatenate([src_mono[int(round((off + s / fps) * SR)):int(round((off + s / fps) * SR)) + int(round((e - s) / fps * SR))]
                                for s, e in frames])
    cum_s = [0]
    for s, e in frames:
        cum_s.append(cum_s[-1] + int(round((e - s) / fps * SR)))
    T = [c / SR for c in cum_s]   # T[j+1] = fim da peça j no corte antigo
    db_old = env_db(old_audio)

    # ---- palavras da fonte -> tempo do corte antigo ----
    wraw = [w for w in json.loads((d / "words.raw.json").read_text(encoding="utf-8")) if w.get("type") == "word"]
    words = []
    for w in wraw:
        mid = (w["start"] + w["end"]) / 2
        for k, (s, e) in enumerate(frames):
            if s / fps <= mid < e / fps:
                t0 = T[k] + max(0.0, w["start"] - s / fps)
                t1 = min(T[k + 1], T[k] + (w["end"] - s / fps))
                words.append({"text": w["text"], "start": t0, "end": max(t0, t1), "k": k})
                break
    words.sort(key=lambda w: w["start"])
    sent = []
    sid = 0
    for w in words:
        sent.append(sid)
        if re.search(r"[.?!…]['\")]*$", w["text"]):
            sid += 1
    wstarts = [w["start"] for w in words]

    cuts = rep.get("cuts", [])
    emendas = []
    x = [0] * n                 # frames acrescentados (+) ou tirados (-) ao fim da peça i
    delta = [0.0] * n           # pré-rolo extra de áudio no começo da peça i
    audio_full = [False] * n    # True: o áudio da peça i vai até o fim original (sobreposição)
    for j in range(n - 1):
        Tj = T[j + 1]
        P = last_voiced(db_old, Tj)
        o = first_voiced(db_old, Tj)
        em = {"i": j, "t_corte_antigo": round(Tj, 3), "classe": "interior", "motivo": "dentro da frase"}
        emendas.append(em)
        if P is None or o is None or o - Tj > 0.6 or P > Tj + 0.02:
            em["motivo"] = "sem ataque de voz na peça seguinte (pausa mantida)"
            continue
        ix = max(0, bisect.bisect_right(wstarts, P) - 1)
        wp = words[ix]
        if not re.search(r"[.?!…]['\")]*$", wp["text"]) or ix + 1 >= len(words):
            continue
        s_prev = sent[ix]
        sw = [q for q in range(len(words)) if sent[q] == s_prev]
        sentence_start = max(0.0, words[sw[0]]["start"])
        n_w, dur_s = len(sw), P - sentence_start
        next_word = words[ix + 1]["text"]
        ext = Tj - P
        pre = o - Tj
        gap_old = ext + pre
        L = float(np.clip(P - wp["start"], 0.12, 0.9))
        kcut = next((c for c in cuts if abs(c["start"] - frames[j][1] / fps) < 0.15
                     and abs(c["end"] - frames[j + 1][0] / fps) < 0.15), None)
        raw_pause = ((kcut["end"] - kcut["start"]) + gap_old) if kcut and kcut["kind"] == "silence" else None
        em.update({"ult_palavra": wp["text"], "prox_palavra": next_word, "P": round(P, 3), "ataque": round(o, 3),
                   "cauda": round(ext, 3), "preroll": round(pre, 3), "gap_antigo": round(gap_old, 3),
                   "dur_ult_palavra": round(L, 3), "frase_palavras": n_w, "frase_dur": round(dur_s, 2),
                   "pausa_no_cru": None if raw_pause is None else round(raw_pause, 2)})
        crit = []
        if s_prev == 0:
            tipo, motivo = "respiro", "respiro depois da 1a frase (gancho)"
        elif re.match(r"ali[aá]s", next_word.lower()):
            tipo, motivo = "respiro", "respiro antes do 'Aliás' (virada para a apresentação)"
        else:
            # C3 (Gabriel, 22/11): a PERGUNTA pede corte normal PARA CHEGAR nela (a próxima frase é a pergunta);
            # DEPOIS da pergunta a fala seguinte entra sobreposta (salvo pausa longa no cru, C4).
            s_next = sent[ix + 1]
            last_next = max(q for q in range(len(words)) if sent[q] == s_next)
            prox_pergunta = words[last_next]["text"].rstrip("'\")").endswith("?")
            depois_pergunta = wp["text"].rstrip("'\")").endswith("?")
            if prox_pergunta:
                crit.append("C3 a próxima frase é pergunta (corte normal para chegar nela)")
            if re.search(r"\d", wp["text"]) or re.sub(r"\W", "", wp["text"].lower()) in KEY_TERMS:
                crit.append("C2 número/termo-chave final")
            if n_w <= C1_PALAVRAS and dur_s <= C1_DUR and not depois_pergunta:
                crit.append("C1 frase curta enfática")
            if raw_pause is not None and raw_pause > C4_PAUSA:
                crit.append("C4 pausa longa no cru")
            tipo, motivo = ("limpo", "; ".join(crit)) if crit else ("sobreposicao", "")
        nxt_fs = frames[j + 1][0]
        fe = frames[j][1]

        def max_ext(want):   # quadros de silêncio da fonte depois do fim da peça
            k = 0
            while k < want and fe + k + 1 < nxt_fs and fe + k + 1 <= total_src and \
                    quiet(db_src, off + (fe + k) / fps, off + (fe + k + 1) / fps):
                k += 1
            return k

        if tipo == "sobreposicao":
            # cauda de silêncio maior que o alvo (pausa depois da pergunta): come a pausa e põe a voz
            # sobre a última palavra até o teto, senão nunca haveria sobreposição real
            O = min(ALVO, ext + TETO * L) if ext < ALVO - MIN_OV else ext + min(ALVO, TETO * L)
            v = O - ext
            if O < MIN_OV or v < 0.03:
                tipo, motivo = "limpo", "fallback: cauda curta para sobrepor >= 50 ms"
            else:
                xx = -int(round((O + pre) * fps))
                xx = min(xx, -1)
                vv = lambda q: -q / fps - ext - pre
                while vv(xx) > TETO * L + 1e-6 and xx < 0:
                    xx += 1
                if xx >= 0 or vv(xx) + ext < MIN_OV or -xx >= plen[j] - 3:
                    tipo, motivo = "limpo", "fallback: quantização de quadros impede sobrepor >= 50 ms"
                else:
                    x[j] = xx
                    audio_full[j] = True
                    em.update({"sobreposicao_voz_s": round(vv(xx), 3), "sobreposicao_total_s": round(vv(xx) + ext, 3),
                               "teto_voz_s": round(TETO * L, 3), "quadros": xx})
                    motivo = f"sobreposição de {vv(xx) + ext:.2f} s (voz sobre a última palavra {vv(xx):.2f} s, teto {TETO * L:.2f} s)"
        if tipo == "limpo":
            if gap_old >= GAP_MANTER:
                x[j] = 0
                motivo += f" | pausa de {gap_old:.2f} s já existente mantida"
            else:
                xx = int(round((GAP_LIMPO - gap_old) * fps))
                if xx < 0:
                    lim = int(np.floor((ext - 0.03) * fps))
                    xx = 0 if lim <= 0 else max(xx, -lim)
                elif xx > 0:
                    xx = max_ext(xx)
                x[j] = xx
            em["gap_novo"] = round(gap_old + x[j] / fps, 3)
            em["quadros"] = x[j]
        elif tipo == "respiro":
            alvo = RESP_MAX if raw_pause is None else min(RESP_MAX, raw_pause)
            xx = max(0, int(round((alvo - gap_old) * fps)))
            x[j] = max_ext(xx)
            em["gap_novo"] = round(gap_old + x[j] / fps, 3)
            em["quadros"] = x[j]
        # pré-rolo de 40 ms antes do ataque
        if tipo in ("sobreposicao", "limpo", "respiro") and pre < FOLGA:
            dl = FOLGA - pre
            if quiet(db_src, off + frames[j + 1][0] / fps - dl, off + frames[j + 1][0] / fps):
                delta[j + 1] = dl
        em["classe"] = {"limpo": "corte_limpo"}.get(tipo, tipo)
        em["motivo"] = motivo
    (d / "emendas.json").write_text(json.dumps(emendas, ensure_ascii=False, indent=1), encoding="utf-8")
    cont = {}
    for em in emendas:
        cont[em["classe"]] = cont.get(em["classe"], 0) + 1
    print("emendas:", cont, flush=True)
    if a.so_classificar:
        return

    # ---- linha do tempo nova ----
    newf = [e + x[i] - s for i, (s, e) in enumerate(frames)]   # quadros de vídeo da peça i
    V = [0]
    for L in newf:
        V.append(V[-1] + L)
    total_f = V[-1]
    out_len = int(round(total_f / fps * SR))
    y = np.zeros((out_len + SR * 2, 2), np.float32)
    for i, (s, e) in enumerate(frames):
        t0 = s / fps - delta[i]
        t1 = (e if audio_full[i] else e + x[i]) / fps
        seg = sl(off + t0, off + t1).copy()
        f = min(int(FADE * SR), len(seg) // 2)
        ramp = np.linspace(0, 1, f, endpoint=False, dtype=np.float32)
        seg[:f] *= ramp[:, None]
        seg[len(seg) - f:] *= ramp[::-1][:, None]
        o0 = int(round((V[i] / fps - delta[i]) * SR))
        y[o0:o0 + len(seg)] += seg
    y = y[:out_len]
    pk = np.abs(y).max(1)
    if pk.max() > 0.97:
        g = np.minimum(1.0, 0.97 / np.maximum(maximum_filter1d(pk, 241), 1e-9))
        g = uniform_filter1d(minimum_filter1d(g, 481), 481)
        y *= g[:, None]
        print(f"limitador atuou (pico {pk.max():.3f})", flush=True)
    tmp = Path(tempfile.mkdtemp(prefix="sobrepor_"))
    try:
        wavfile.write(str(tmp / "a.wav"), SR, y.astype(np.float32))
        # ---- vídeo por trecho ----
        crf = ["-c:v", "libx264", "-crf", "18", "-preset", "veryfast"]
        size = ",scale='trunc(iw*min(1,1080/min(iw,ih))/2)*2':'trunc(ih*min(1,1080/min(iw,ih))/2)*2':flags=lanczos"
        segdir = d / ".segments_sob"
        segdir.mkdir(exist_ok=True)
        segs = []

        def enc(i):
            s, e = frames[i][0], frames[i][1] + x[i]
            out = segdir / f"{s}-{e}.mp4"
            segs.append(out) if False else None
            if out.exists():
                return None
            t0 = R.video_window(s, e, fps, vstart)[0]
            part = out.with_name(out.stem + f".{os.getpid()}.part.mp4")
            cmd = ["ffmpeg", "-v", "error", "-y", "-copyts", "-ss", f"{max(0.0, t0 - fstart - R.LEAD_S):.6f}", "-i", a.source,
                   "-an", "-vf", R.trim_filter(s, e, fps, vstart, total_src) + size, "-r", str(fps), *crf,
                   "-pix_fmt", "yuv420p", "-g", "15", str(part)]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode:
                return f"peça {i}: {r.stderr[-300:]}"
            part.replace(out)
            return None

        with cf.ThreadPoolExecutor(max(2, (os.cpu_count() or 8) // 4)) as ex:
            for err in ex.map(enc, range(n)):
                if err:
                    sys.exit("ERRO " + err)
        lst = tmp / "list.txt"
        lst.write_text("".join(f"file '{(segdir / f'{frames[i][0]}-{frames[i][1] + x[i]}.mp4').resolve().as_posix()}'\n"
                               for i in range(n)), encoding="utf-8")
        allv = tmp / "all.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(allv)], check=True)
        out = d / "cut.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(allv), "-i", str(tmp / "a.wav"), "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out)], check=True)
        got = R.count_frames(out)
        print(f"cut.mp4: {got} quadros de {total_f} = {total_f / fps:.2f} s", flush=True)
        if got != total_f:
            sys.exit("ERRO: contagem de quadros")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- tempos novos nos arquivos da edição ----
    old_start = [c / fps for c in cum_f]
    new_start = [v / fps for v in V]

    def tmap(t):
        k = min(max(bisect.bisect_right(old_start, t) - 1, 0), n - 1)
        return new_start[k] + (t - old_start[k])

    def remap_words(lst):
        res = []
        for w in lst:
            q = dict(w)
            q["start"], q["end"] = round(tmap(w["start"]), 3), round(tmap(w["end"]), 3)
            res.append(q)
        for q, nx in zip(res, res[1:]):
            if nx["start"] < q["start"]:
                nx["start"] = q["start"]
            q["end"] = max(q["start"], min(q["end"], nx["start"]))
        return res

    for name in ("words.json", "captions.json"):
        old = backup_read(d, name)
        (d / name).write_text(json.dumps(remap_words(old), ensure_ascii=False, indent=1), encoding="utf-8")
    bj = backup_read(d, "beats.json")
    for b in bj:
        b["start"], b["end"] = round(tmap(b["start"]), 3), round(tmap(b["end"]), 3)
    (d / "beats.json").write_text(json.dumps(bj, ensure_ascii=False, indent=1), encoding="utf-8")
    cj = backup_read(d, "cues_iara.json")
    for z in cj.get("zooms_add", []):
        z["start"], z["end"] = round(tmap(z["start"]), 3), round(tmap(z["end"]), 3)
    for c in cj.get("cues", []):
        c["t"] = round(tmap(c["t"]), 3)
    (d / "cues_iara.json").write_text(json.dumps(cj, ensure_ascii=False, indent=1), encoding="utf-8")
    rep2 = dict(rep)
    rep2["frames"] = [[s, e + x[i]] for i, (s, e) in enumerate(frames)]
    rep2["final_s"] = total_f / fps
    rep2["sobreposicao"] = True
    (d / "report.json").write_text(json.dumps(rep2, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"pronto: {total_f / fps:.2f} s (antes {rep['final_s']:.2f} s)", flush=True)


if __name__ == "__main__":
    main()
