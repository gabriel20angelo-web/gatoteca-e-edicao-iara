"""Gera o PDF, o PowerPoint e a prévia de uma aula em slides.

Uso:
    python slides/motor/fazer_slides.py slides/<pasta-da-aula>
    python slides/motor/fazer_slides.py slides/<pasta-da-aula> --rapido   (só a prévia, para conferir)
    python slides/motor/fazer_slides.py slides/<pasta-da-aula> --ver capa,dialogo-2   (só esses slides, em tamanho cheio)

A pasta da aula tem:
    deck.json        {"titulo": "...", "rodape": "Tema curto", "ordem": ["capa", "topicos", ...]}
    slides/<id>.html um arquivo por slide, 1920 x 1080, com <section class="slide"> e as notas do professor num <aside>

Saída na própria pasta da aula:
    aula.pdf    uma página por slide (texto de verdade, dá para imprimir)
    aula.pptx   cada slide como imagem de tela cheia + as notas do <aside> nas notas do PowerPoint
    previa.png  folha com as miniaturas de todos os slides (para olhar antes de entregar)

O script também avisa quando algo passa da área útil do slide, quando uma imagem não carrega
ou quando falta um arquivo da ordem.
"""
import argparse
import html
import io
import json
import re
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

LARG, ALT = 1920, 1080
LIMITE_BAIXO = 930  # o conteúdo deve terminar até aqui (o rodapé fica embaixo disso)
MOTOR = Path(__file__).resolve().parent

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Roda dentro da página: escreve o rodapé e mede o que saiu do lugar.
JS_PREPARAR = """
([texto]) => {
  document.querySelectorAll('.rodape').forEach(el => {
    const extra = el.dataset.extra ? ' · ' + el.dataset.extra : '';
    el.textContent = texto + extra;
  });
  const avisos = [];
  document.querySelectorAll('img').forEach(im => {
    if (!im.complete || im.naturalWidth === 0) avisos.push('imagem não carregou: ' + im.getAttribute('src'));
  });
  const sec = document.querySelector('section');
  if (!sec) { avisos.push('não achei o <section class="slide">'); return avisos; }
  const ignorar = el => el.closest('.fig, .elipse, .rodape, aside, svg, .livre');
  sec.querySelectorAll('*').forEach(el => {
    if (ignorar(el)) return;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return;
    const nome = el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : '');
    const trecho = (el.textContent || '').trim().slice(0, 40);
    if (r.bottom > %d) avisos.push('passa da área útil embaixo (y=' + Math.round(r.bottom) + '): ' + nome + ' "' + trecho + '"');
    if (r.right > %d || r.left < 0) avisos.push('sai pela lateral: ' + nome + ' "' + trecho + '"');
    if (el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflow === 'hidden' && el !== sec)
      avisos.push('texto cortado: ' + nome + ' "' + trecho + '"');
  });
  return [...new Set(avisos)].slice(0, 8);
}
""" % (LIMITE_BAIXO, LARG)


def notas_do_slide(fonte: str) -> str:
    """Tira o texto do <aside> (notas do professor), mantendo os parágrafos."""
    m = re.search(r"<aside[^>]*>(.*?)</aside>", fonte, re.S | re.I)
    if not m:
        return ""
    t = m.group(1)
    t = re.sub(r"<br\s*/?>", "\n", t, flags=re.I)
    t = re.sub(r"</(p|li|div|h\d)>", "\n", t, flags=re.I)
    t = re.sub(r"<li[^>]*>", "• ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    linhas = [re.sub(r"\s+", " ", l).strip() for l in t.splitlines()]
    return "\n".join(l for l in linhas if l)


def fazer_previa(pngs, ids, destino: Path):
    col, w, h, m, leg = 4, 480, 270, 28, 40
    lin = (len(pngs) + col - 1) // col
    folha = Image.new("RGB", (m + col * (w + m), m + lin * (h + leg + m)), "#E9E0CE")
    d = ImageDraw.Draw(folha)
    fonte = None
    for f in [MOTOR / "fontes" / "Barlow-SemiBold.ttf"]:
        try:
            fonte = ImageFont.truetype(str(f), 24)
        except Exception:
            pass
    fonte = fonte or ImageFont.load_default()
    for i, (png, sid) in enumerate(zip(pngs, ids)):
        x = m + (i % col) * (w + m)
        y = m + (i // col) * (h + leg + m)
        im = Image.open(png).convert("RGB").resize((w, h), Image.LANCZOS)
        folha.paste(im, (x, y))
        d.rectangle([x - 1, y - 1, x + w, y + h], outline="#B9A98A")
        d.text((x, y + h + 8), f"{i + 1} · {sid}", fill="#4A5A50", font=fonte)
    folha.save(destino)


def fazer_pptx(pngs, notas, destino: Path):
    from pptx import Presentation
    from pptx.util import Emu

    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)  # 16:9
    vazio = prs.slide_layouts[6]
    for png, nota in zip(pngs, notas):
        s = prs.slides.add_slide(vazio)
        buf = io.BytesIO()
        Image.open(png).convert("RGB").save(buf, "JPEG", quality=90)
        buf.seek(0)
        s.shapes.add_picture(buf, 0, 0, prs.slide_width, prs.slide_height)
        if nota:
            s.notes_slide.notes_text_frame.text = nota
    prs.save(destino)


def juntar_pdfs(pdfs, destino: Path):
    from pypdf import PdfWriter

    w = PdfWriter()
    for p in pdfs:
        w.append(str(p))
    try:  # fontes e imagens repetidas em cada página viram uma só (PDF bem menor)
        w.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    except Exception:
        pass
    with open(destino, "wb") as f:
        w.write(f)


def main():
    ap = argparse.ArgumentParser(description="Gera aula.pdf, aula.pptx e previa.png de uma pasta de aula.")
    ap.add_argument("pasta", help="pasta da aula (com deck.json e slides/)")
    ap.add_argument("--rapido", action="store_true", help="só a prévia (para conferir rápido)")
    ap.add_argument("--ver", default="", help="ids separados por vírgula: salva só esses slides em PNG de tamanho cheio")
    a = ap.parse_args()

    pasta = Path(a.pasta).resolve()
    deck = json.loads((pasta / "deck.json").read_text(encoding="utf-8"))
    ordem = deck["ordem"]
    tema = deck.get("rodape") or deck["titulo"].split(":")[0].strip()
    total = len(ordem)

    faltam = [i for i in ordem if not (pasta / "slides" / f"{i}.html").exists()]
    if faltam:
        sys.exit("Faltam arquivos em slides/: " + ", ".join(f"{i}.html" for i in faltam))

    tmp = Path(tempfile.mkdtemp(prefix="slides_"))
    ver = [i.strip() for i in a.ver.split(",") if i.strip()]
    if ver:
        a.rapido = True
    pngs, pdfs, notas, problemas = [], [], [], 0
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": LARG, "height": ALT})
        for n, sid in enumerate(ordem, 1):
            if ver and sid not in ver:
                continue
            arq = pasta / "slides" / f"{sid}.html"
            fonte = arq.read_text(encoding="utf-8")
            notas.append(notas_do_slide(fonte))
            pag.goto(arq.as_uri(), wait_until="load")
            pag.evaluate("document.fonts.ready.then(() => true)")
            avisos = pag.evaluate(JS_PREPARAR, [f"{tema} · {n} / {total}"])
            if not notas[-1]:
                avisos.append("sem notas do professor (<aside>)")
            for av in avisos:
                print(f"  [{n:02d} {sid}] {av}")
            problemas += len(avisos)
            png = tmp / f"{n:02d}.png"
            if ver:
                png = tmp / f"{n:02d}_{sid}.png"
                print(f"  {sid}: {png}")
            pag.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": LARG, "height": ALT})
            pngs.append(png)
            if not a.rapido:
                pdf = tmp / f"{n:02d}.pdf"
                pag.pdf(path=str(pdf), width=f"{LARG}px", height=f"{ALT}px", print_background=True,
                        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}, page_ranges="1")
                pdfs.append(pdf)
        nav.close()

    if ver:
        print("Prontos (a prévia não foi refeita).")
        return
    fazer_previa(pngs, ordem, pasta / "previa.png")
    print(f"previa.png: {total} slides")
    if not a.rapido:
        juntar_pdfs(pdfs, pasta / "aula.pdf")
        fazer_pptx(pngs, notas, pasta / "aula.pptx")
        print("aula.pdf e aula.pptx prontos")
    print("Tudo certo." if problemas == 0 else f"{problemas} aviso(s) acima: olhe a prévia e conserte.")


if __name__ == "__main__":
    main()
