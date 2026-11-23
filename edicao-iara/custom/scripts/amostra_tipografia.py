"""Folha com 4 opções de tipografia (título + legenda) sobre um quadro do vídeo.
py amostra_tipografia.py <quadro.png> <saida.png>"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

F = Path(__file__).resolve().parent.parent / "fonts"


def font(name, size, wght=None):
    f = ImageFont.truetype(str(F / name), size)
    if wght:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    return f


def stroke_text(d, xy, text, f, fill, stroke=0, sc="#000", anchor="mm"):
    d.text(xy, text, font=f, fill=fill, stroke_width=stroke, stroke_fill=sc, anchor=anchor)


def shadow(img, xy, text, f, fill, anchor="mm", blur=6, alpha=170):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((xy[0] + 3, xy[1] + 4), text, font=f, fill=(0, 0, 0, alpha), anchor=anchor)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(img).text(xy, text, font=f, fill=fill, anchor=anchor)


def caption_words(img, y, words, hi, f, base, hicol, stroke=0, sc="#000", upper=False, shadowed=False, bg=None):
    d = ImageDraw.Draw(img)
    words = [w.upper() if upper else w for w in words]
    sp = f.getlength(" ")
    total = sum(f.getlength(w) for w in words) + sp * (len(words) - 1)
    x = (img.width - total) / 2
    if bg:
        pad = 22
        asc, desc = f.getmetrics()
        d.rounded_rectangle([x - pad, y - asc / 2 - pad, x + total + pad, y + asc / 2 + desc / 2 + pad], 18, fill=bg)
    for i, w in enumerate(words):
        col = hicol if i == hi else base
        if shadowed:
            shadow(img, (x, y), w, f, col, anchor="lm")
        else:
            d.text((x, y), w, font=f, fill=col, stroke_width=stroke, stroke_fill=sc, anchor="lm")
        x += f.getlength(w) + sp


def opt(base, label, draw):
    img = base.copy().convert("RGBA")
    draw(img)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, img.width, 90], fill=(20, 20, 20, 210))
    d.text((img.width / 2, 45), label, font=font("PoppinsBold.ttf", 48), fill="#fff", anchor="mm")
    return img


def main():
    base = Image.open(sys.argv[1]).convert("RGB").resize((1080, 1920))
    W = 1080
    cap = ["a", "gente", "é", "feito", "de", "pedaços"]

    def a(img):   # Moderna: título Playfair itálico, legenda Montserrat extra-negrito com contorno
        shadow(img, (W / 2, 330), "A gente é feito", font("PlayfairItalic.ttf", 108, 700), "#ffffff")
        shadow(img, (W / 2, 450), "de pedaços", font("PlayfairItalic.ttf", 108, 700), "#F4B6C2")
        caption_words(img, 1380, cap, 5, font("Montserrat.ttf", 78, 800), "#ffffff", "#FF8FB1", stroke=7, sc="#1a1a1a")

    def b(img):   # Delicada: título manuscrito Dancing Script, legenda Quicksand negrito
        shadow(img, (W / 2, 360), "A gente é feito de pedaços", font("DancingScript.ttf", 96, 700), "#ffffff")
        caption_words(img, 1380, cap, 5, font("Quicksand.ttf", 76, 700), "#ffffff", "#FFD1DC", shadowed=True)

    def c(img):   # Editorial: DM Serif nos dois, legenda com caixa rosé suave
        shadow(img, (W / 2, 330), "A gente é feito", font("DMSerif.ttf", 112), "#ffffff")
        shadow(img, (W / 2, 450), "de pedaços", font("DMSerifItalic.ttf", 112), "#ffffff")
        caption_words(img, 1380, cap, 5, font("DMSerif.ttf", 80), "#2B2427", "#B0476A", bg=(255, 240, 243, 235))

    def d(img):   # Viral: Poppins Black caixa alta, palavra da vez em rosa
        shadow(img, (W / 2, 330), "A GENTE É FEITO", font("PoppinsBlack.ttf", 96), "#ffffff")
        shadow(img, (W / 2, 445), "DE PEDAÇOS", font("PoppinsBlack.ttf", 96), "#FF6FA3")
        caption_words(img, 1380, cap, 5, font("PoppinsBlack.ttf", 74), "#ffffff", "#FF6FA3", stroke=8, sc="#000", upper=True)

    tiles = [opt(base, "A · Moderna", a), opt(base, "B · Delicada", b), opt(base, "C · Editorial", c), opt(base, "D · Viral", d)]
    sheet = Image.new("RGB", (W * 4 + 60, 1920), "#ffffff")
    for i, t in enumerate(tiles):
        sheet.paste(t.convert("RGB"), (i * (W + 20), 0))
    sheet.resize((sheet.width // 2, sheet.height // 2)).save(sys.argv[2])


if __name__ == "__main__":
    main()
