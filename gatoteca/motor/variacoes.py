# -*- coding: utf-8 -*-
"""Cinco variacoes da divulgacao de Halloween (Parque da Jaqueira), com as pecas de pecas.py.

uso: py variacoes.py [1 2 3 4 5]   -> gera varN_*.html e fotografa em saida/
"""
import os, sys
from pecas import *
import montar

AQUI = os.path.dirname(os.path.abspath(__file__))

# textos (os mesmos da arte aprovada)
T = dict(
    titulo1="Edição de", titulo2="Halloween",
    sub="Piquenique literário no Parque da Jaqueira",
    data="Sáb, 31 de outubro · 15h",
    preco="R$ 30", vagas="20 vagas",
    inclui="Ecobag, marcador de livro, café, bolo e frutinhas,<br>e sorteio de um livro entre os leitores",
    cta="Comunidade no WhatsApp · link na bio",
)

CABER_JS = '''<script>
document.fonts.ready.then(()=>{document.querySelectorAll('.caber').forEach(e=>{let f=parseFloat(getComputedStyle(e).fontSize);
  while(e.scrollWidth>e.clientWidth+1&&f>10){f-=1;e.style.fontSize=f+'px'}})});
</script>'''

COPA_VIVA = "--copa1:#3F7A5A;--copa2:#78B27A;--copaluz:#D6EBAA;--copabase:#6FA678;--tronco:#7E5244;--jaca:#BFC85E;--lanterna:#F2A03D;--folha:#28503A"


def carta(uid, conteudo, papel="#F2E7D3", linha="#2A1E24", numeral="", nome="", fora="", cor_txt=None, painel=True):
    """Carta de tarot em arco (540x760). 'conteudo' fica dentro da janela; 'fora' transborda."""
    cor_txt = cor_txt or linha
    fundo_janela = 676 if painel else 760
    s = ['<clipPath id="j%s"><path d="M22,%d V270 A248,248 0 0 1 518,270 V%d Z"/></clipPath>' % (uid, fundo_janela, fundo_janela)]
    s.append('<path d="M0,760 V270 A270,270 0 0 1 540,270 V760 Z" fill="%s"/>' % papel)
    s.append('<g clip-path="url(#j%s)">%s</g>' % (uid, conteudo))
    s.append('<g fill="none" stroke="%s" filter="url(#mao)"><path d="M14,746 V270 A256,256 0 0 1 526,270 V746 Z" stroke-width="1.8"/>'
             '<path d="M22,738 V270 A248,248 0 0 1 518,270 V738 Z" stroke-width=".8"/>' % linha)
    if painel:
        s.append('<path d="M22,676 H518" stroke-width="1.6"/><path d="M22,683 H518" stroke-width=".7"/>')
    s.append('</g>')
    if numeral:
        s.append('<use href="#br0" transform="translate(270 30) scale(.55)" fill="%s"/>' % cor_txt)
        s.append('<text x="270" y="72" text-anchor="middle" font-family="Cinzel" font-weight="600" font-size="20" letter-spacing="5" fill="%s">%s</text>' % (cor_txt, numeral))
    if nome and painel:
        s.append('<text x="270" y="721" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="25" letter-spacing="7" fill="%s">%s</text>' % (cor_txt, nome))
        s.append('<use href="#br0" transform="translate(70 712) scale(.45)" fill="%s"/><use href="#br0" transform="translate(470 712) scale(.45)" fill="%s"/>' % (cor_txt, cor_txt))
    s.append(fora)
    return "".join(s)


def chao(cor, y=604, op=.55):
    return ('<path d="M0,%d C120,%d 200,%d 270,%d C350,%d 430,%d 540,%d V760 H0Z" fill="%s" opacity="%g" filter="url(#aguada)"/>'
            '<path d="M0,%d C120,%d 200,%d 270,%d C350,%d 430,%d 540,%d" fill="none" stroke="#2A1E24" stroke-width="1.15" filter="url(#mao)"/>'
            ) % (y, y - 7, y - 4, y - 2, y, y - 6, y, cor, op, y, y - 7, y - 4, y - 2, y, y - 6, y)


def bandeirinhas(y0, cores):
    """Varal de bandeirinhas atravessando o arco."""
    s = ['<path d="M30,%d Q270,%d 510,%d" fill="none" stroke="#2A1E24" stroke-width="1.1" filter="url(#mao)"/>' % (y0, y0 + 70, y0)]
    n = 11
    for i in range(n):
        t = (i + .5) / n
        x = (1 - t) ** 2 * 30 + 2 * (1 - t) * t * 270 + t ** 2 * 510
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * (y0 + 70) + t ** 2 * y0
        s.append('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="%s" stroke="#2A1E24" stroke-width="1" filter="url(#mao)"/>' % (x - 15, y - 2, x + 15, y - 1, x, y + 30, cores[i % len(cores)]))
    return "".join(s)


# ============================================================ V1 · tiragem de tres cartas
def v1():
    ceu_lilas = '<rect width="540" height="760" fill="url(#ceuLilas)"/>'
    c_lua = carta("a", ceu_lilas + lua(270, 300, 150) + morcegos([(150, 170, 2.2, -10), (410, 150, 1.6, 12), (440, 240, 1.2, -6), (110, 420, 1.3, 8)]) +
                  brilhos([(80, 120, .8), (470, 340, .6), (130, 520, .5), (420, 470, .5), (300, 520, .4)], "#2A1E24") + chao("#9BC48B", 600) +
                  abobora(120, 640, 1.6) + abobora(170, 650, 1.1, "--abobora:#F2B544") + abobora(420, 642, 1.4, "--abobora:#C8324F"),
                  papel="#E9DDF0", numeral="XVIII", nome="A LUA")
    c_jaq = carta("b", '<rect width="540" height="760" fill="url(#luarCarta)"/>' + lua(270, 196, 104) +
                  morcegos([(420, 182, 1.15, -10), (448, 210, .78, 12), (116, 206, .7, 6)]) +
                  brilhos([(84, 150, .7), (458, 134, .62), (56, 250, .42), (486, 236, .42)], "#2A1E24") + chao("#7DB87A", 604) +
                  arvore(270, 606, 1, COPA_VIVA) + piquenique(44, 600, 1) + gato(406, 646, 1) +
                  abobora(478, 646, 1) + abobora(455, 656, .62, "--abobora:#F2B544"),
                  papel="#F4E9D5", numeral="XXXI", nome="A JAQUEIRA")
    c_piq = carta("c", '<rect width="540" height="760" fill="url(#ceuPessego)"/>' + bandeirinhas(150, ["#E8752F", "#7A3E8E", "#78B27A", "#F2B544", "#C8324F"]) +
                  lua(400, 300, 46, raios=False) + brilhos([(110, 300, .7), (200, 250, .45), (470, 420, .5)], "#2A1E24") + chao("#9BC48B", 560) +
                  piquenique(20, 470, 2.75) + use("ic_ecobag", 380, 380, 130, 130) + abobora(450, 610, 1.4) +
                  use("ic_marcador", 60, 520, 70, 70, "", 'transform="rotate(-20 95 555)"'),
                  papel="#F7E1CB", numeral="VII", nome="O PIQUENIQUE")
    grad = ('<svg width="0" height="0" style="position:absolute"><defs>'
            '<linearGradient id="ceuLilas" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C9B2DD" stop-opacity=".7"/><stop offset=".7" stop-color="#C9B2DD" stop-opacity="0"/></linearGradient>'
            '<linearGradient id="luarCarta" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7E2A4" stop-opacity=".6"/><stop offset=".55" stop-color="#F7E2A4" stop-opacity="0"/></linearGradient>'
            '<linearGradient id="ceuPessego" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4B98E" stop-opacity=".6"/><stop offset=".6" stop-color="#F4B98E" stop-opacity="0"/></linearGradient>'
            '</defs></svg>')
    fundo = ('<svg style="left:0;top:0" width="1080" height="1350">%s<g fill="none" stroke="#F2B544" transform="translate(540 520)">'
             '<circle r="470" stroke-width="1.2" opacity=".22"/><circle r="484" stroke-width=".6" opacity=".16"/><circle r="400" stroke-dasharray="2 9" opacity=".25"/></g></svg>'
             ) % estrelas(120, 1080, 1350, seed=3, evitar=lambda x, y: 150 < x < 930 and 200 < y < 830)
    corpo = grad + fundo + marca_html("#F2B544", "#F4E9D5", "left:0;right:0;top:40px")
    corpo += '<svg class="ct ce" viewBox="0 0 540 760" style="left:110px;top:250px;width:370px;transform:rotate(-14deg)">%s</svg>' % c_lua
    corpo += '<svg class="ct cd" viewBox="0 0 540 760" style="left:600px;top:250px;width:370px;transform:rotate(14deg)">%s</svg>' % c_piq
    corpo += '<svg class="ct cc" viewBox="0 0 540 760" style="left:335px;top:205px;width:410px">%s</svg>' % c_jaq
    corpo += '<svg style="left:0;top:0" width="1080" height="1350">%s</svg>' % selo(952, 262, 82, 12, "#E8752F", "#FFF4DE", T["preco"], T["vagas"])
    corpo += ('<div class="texto"><div class="t1">%s <span>%s</span></div><div class="sub">%s</div><div class="data">%s</div>%s<div class="cta">%s</div></div>'
              % (T["titulo1"], T["titulo2"], T["sub"], T["data"], icones_html("#F4E9D5", 54, 14), T["cta"]))
    css = '''
.peca{background:radial-gradient(ellipse 75% 60% at 50% 42%,#6E4778 0%,#4A2B55 45%,#2A1832 100%)}
.ct{height:auto;transform-origin:50% 100%;filter:drop-shadow(0 18px 26px rgba(15,6,20,.55))}
.cc{filter:drop-shadow(0 26px 36px rgba(15,6,20,.7))}
.texto{left:40px;right:40px;top:868px;display:flex;flex-direction:column;align-items:center;text-align:center;color:#F4E9D5}
.t1{font-family:'Cormorant';font-style:italic;font-weight:600;font-size:66px;line-height:1;color:#F4E9D5}
.t1 span{font-family:'Shrikhand';font-style:normal;font-size:76px;color:#F2B544;letter-spacing:.01em;text-shadow:4px 5px 0 #C8324F}
.sub{margin-top:18px;font-family:'Cormorant';font-weight:600;font-size:36px}
.data{margin-top:14px;font-family:'Cinzel';font-weight:700;font-size:23px;letter-spacing:.12em;color:#F2B544}
.icones{margin-top:26px}
.cta{margin-top:24px;font-family:'Cinzel';font-weight:600;font-size:15px;letter-spacing:.3em;margin-right:-.3em;color:#F2B544}
'''
    return pagina("Halloween · tiragem", css, corpo)


# ============================================================ V2 · a carta que transborda (a mais chamativa)
def v2():
    ceu = ('<linearGradient id="ceuNoite" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#241830"/><stop offset=".75" stop-color="#4C2F57"/><stop offset="1" stop-color="#6A3E5E"/></linearGradient>')
    dentro = ('<defs>%s</defs><rect width="540" height="760" fill="url(#ceuNoite)"/>' % ceu +
              estrelas(60, 540, 600, seed=11, cor="#F4E9D5") + brilhos([(80, 180, .8), (460, 160, .7), (120, 330, .5), (430, 360, .5)], "#F2B544") +
              lua(270, 170, 78, linha="#F2D27E", opac_raios=.5) +
              chao("#4E8A5C", 612, .95) + arvore(262, 622, 1.08, COPA_VIVA) + piquenique(10, 606, 1.0) + abobora(214, 654, .8, "--abobora:#F2B544") +
              morcegos([(120, 150, 1.6, -10), (410, 120, 1.3, 8)], "#120A14"))
    fora = (morcegos([(470, 40, 2.2, 12), (30, 90, 1.8, -14)], "#120A14") +
            abobora(66, 742, 2.3) + abobora(126, 758, 1.5, "--abobora:#F2B544") + abobora(28, 768, 1.2, "--abobora:#C8324F") +
            gato(440, 762, 1.75))
    c = carta("v2", dentro, papel="#2A1C30", linha="#F2B544", nome="A JAQUEIRA", fora=fora, cor_txt="#F2B544")
    fundo = '<svg style="left:0;top:0" width="1080" height="1350">%s</svg>' % lua(540, 560, 330, linha="#3B1E2C", opac_raios=.32)
    bats = '<svg style="left:0;top:0;z-index:6" width="1080" height="1350">%s%s</svg>' % (
        morcegos([(170, 228, 3.2, -14), (930, 196, 2.6, 10), (985, 300, 1.7, -4), (96, 340, 1.8, 12), (840, 120, 1.5, 6)], "#2A1626"),
        selo(292, 478, 86, -12, "#7A2E5A", "#FFF1DB", T["preco"], T["vagas"]))
    corpo = fundo + marca_html("#3B1E2C", "#2A1626", "left:0;right:0;top:36px;z-index:3")
    corpo += '<div class="t1">%s</div><div class="t2">%s</div>' % (T["titulo1"], T["titulo2"])
    corpo += '<svg class="ct" viewBox="0 0 540 760" style="left:300px;top:392px;width:480px;height:676px;transform:rotate(-3deg)">%s</svg>' % c
    corpo += bats
    corpo += ('<div class="texto"><div class="sub">%s</div><div class="data">%s</div>%s<div class="cta">%s</div></div>'
              % (T["sub"], T["data"], icones_html("#2A1626", 52, 10), T["cta"]))
    css = '''
.peca{background:linear-gradient(172deg,#F6A355 0%,#EC7F3D 42%,#D95A2C 100%)}
.t1{left:0;right:0;top:146px;text-align:center;font-family:'Cormorant';font-style:italic;font-weight:700;font-size:54px;color:#2A1626;z-index:2}
.t2{left:0;right:0;top:186px;text-align:center;font-family:'Shrikhand';font-size:178px;line-height:1;color:#2A1626;letter-spacing:-.01em;
  text-shadow:6px 7px 0 #FFF1DB;z-index:2}
.ct{z-index:4;overflow:visible;filter:drop-shadow(0 24px 30px rgba(42,22,38,.55))}
.texto{left:30px;right:30px;top:1094px;display:flex;flex-direction:column;align-items:center;text-align:center;color:#2A1626;z-index:5}
.sub{font-family:'Cormorant';font-weight:700;font-size:38px;line-height:1}
.data{margin-top:8px;font-family:'Cinzel';font-weight:700;font-size:23px;letter-spacing:.12em}
.icones{margin-top:12px}
.ic span{font-weight:700}
.cta{margin-top:10px;font-family:'Cinzel';font-weight:700;font-size:15px;letter-spacing:.3em;margin-right:-.3em}
'''
    return pagina("Halloween · transborda", css, corpo)


# ============================================================ V3 · cartaz panoramico
def v3():
    s = ['<svg style="left:0;top:0" width="1080" height="1350"><defs>'
         '<linearGradient id="morro" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4E8A5C"/><stop offset=".35" stop-color="#2F5A40"/><stop offset="1" stop-color="#14221A"/></linearGradient>'
         '</defs>']
    s.append(estrelas(150, 1080, 900, seed=21, cor="#F4E9D5"))
    s.append(lua(770, 420, 165, linha="#F2D27E", opac_raios=.55))
    s.append(morcegos([(700, 330, 2.6, -10), (860, 300, 1.8, 12), (900, 400, 1.3, -6), (610, 450, 1.2, 8)], "#1B1426"))
    s.append('<path d="M0,1010 Q300,950 620,995 T1080,975 V1350 H0Z" fill="#2C4A3A"/>')
    s.append(arvore(300, 1088, 1.78, COPA_VIVA))
    s.append('<path d="M0,1070 C300,1040 700,1095 1080,1050 V1350 H0Z" fill="url(#morro)"/>')
    s.append('<g filter="url(#mao)" stroke="#14221A" fill="none" stroke-width="1.6"><path d="M0,1070 C300,1040 700,1095 1080,1050"/></g>')
    s.append(piquenique(440, 1036, 1.55))
    s.append(abobora(980, 1100, 2.0) + abobora(1036, 1112, 1.3, "--abobora:#F2B544") + abobora(690, 1094, 1.2, "--abobora:#C8324F"))
    s.append(gato(860, 1112, 2.75))
    # vagalumes
    import random as R
    R.seed(5)
    vg = "".join('<circle cx="%d" cy="%d" r="%.1f"/>' % (R.randint(40, 1040), R.randint(560, 1040), 1.6 + R.random() * 2) for _ in range(26))
    s.append('<g fill="#FFE07A" filter="url(#brilho2)">%s</g><g fill="#FFF6C8">%s</g>' % (vg, vg.replace('r="', 'r="0.')))
    s.append('</svg>')
    corpo = "".join(s)
    corpo += marca_html("#F2D27E", "#F4E9D5", "left:0;right:0;top:38px")
    corpo += '<div class="t1">%s <span>%s</span></div>' % (T["titulo1"], T["titulo2"])
    corpo += ('<div class="texto"><div class="sub">%s</div><div class="info"><span>%s</span><i></i><b>%s</b><i></i><span>%s</span></div><div class="inclui">%s</div><div class="cta">%s</div></div>'
              % (T["sub"], T["data"], T["preco"], T["vagas"], T["inclui"], T["cta"]))
    css = '''
.peca{background:linear-gradient(180deg,#151C38 0%,#253058 38%,#47406E 66%,#7A4F6E 84%,#3A2A3A 100%)}
.t1{left:0;right:0;top:168px;text-align:center;font-family:'Cormorant';font-style:italic;font-weight:700;font-size:60px;color:#F4E9D5;line-height:1}
.t1 span{display:block;font-family:'Shrikhand';font-style:normal;font-size:120px;color:#F2A03D;text-shadow:5px 6px 0 #1B1426}
.texto{left:40px;right:40px;top:1148px;display:flex;flex-direction:column;align-items:center;text-align:center;color:#F4E9D5}
.sub{font-family:'Cormorant';font-weight:700;font-size:38px;line-height:1}
.info{margin-top:12px;display:flex;align-items:center;gap:18px;font-family:'Cinzel';font-weight:700;font-size:21px;letter-spacing:.1em}
.info b{font-size:28px;color:#F2B544}.info i{width:7px;height:7px;background:#F2B544;transform:rotate(45deg)}
.inclui{margin-top:10px;font-family:'Cormorant';font-style:italic;font-weight:600;font-size:24px;line-height:1.2;color:rgba(244,233,213,.9)}
.cta{margin-top:10px;font-family:'Cinzel';font-weight:700;font-size:14px;letter-spacing:.3em;margin-right:-.3em;color:#F2B544}
'''
    return pagina("Halloween · cartaz", css, corpo)


# ============================================================ V4 · ingresso
def v4():
    import random as R
    R.seed(8)
    folhas = []
    cores = ["#E8752F", "#F2B544", "#78B27A", "#C8324F", "#D9734E"]
    for _ in range(44):
        x, y = R.randint(0, 1080), R.randint(0, 1350)
        if (40 < x < 1040 and 230 < y < 900) or (120 < x < 960 and 930 < y < 1150) or (360 < x < 720 and y < 160):
            continue
        k = 1.4 + R.random() * 2.4
        folhas.append('<use href="#folha" x="-6" y="-8" width="12" height="16" transform="translate(%d %d) rotate(%d) scale(%.2f)" style="--cor:%s"/>' % (x, y, R.randint(0, 360), k, R.choice(cores)))
    fundo = '<svg style="left:0;top:0" width="1080" height="1350">%s%s</svg>' % (estrelas(70, 1080, 1350, seed=4, cor="#F4E9D5"), "".join(folhas))
    W, H, X = 960, 560, 744
    ticket = ('M22,0 H{a} A22,22 0 0 0 {b},0 H{c} A22,22 0 0 1 {W},22 V{h2} A22,22 0 0 1 {c},{H} H{b} A22,22 0 0 0 {a},{H} H22 A22,22 0 0 1 0,{h2} V22 A22,22 0 0 1 22,0 Z'
              ).format(a=X - 22, b=X + 22, c=W - 22, W=W, H=H, h2=H - 22)
    # mini cena dentro da janela redonda (coordenadas da carta)
    mini = ('<rect x="0" y="0" width="540" height="760" fill="url(#ceuIngresso)"/>' + estrelas(40, 540, 500, seed=2, cor="#F4E9D5") +
            lua(390, 210, 70, linha="#F2D27E", aneis=False) + morcegos([(150, 200, 1.4, -8), (470, 300, 1, 6)], "#1B1426") +
            chao("#4E8A5C", 606, .95) + arvore(250, 610, 1, COPA_VIVA) + gato(420, 650, 1.1) + abobora(488, 652, 1) + abobora(120, 650, .9, "--abobora:#F2B544"))
    cx, cy, r = 200, H / 2, 172
    svg = ['<svg width="%d" height="%d" viewBox="0 0 %d %d"><defs>' % (W, H, W, H),
           '<linearGradient id="ceuIngresso" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A2048"/><stop offset=".8" stop-color="#5A3C6E"/></linearGradient>',
           '<clipPath id="janela4"><circle cx="%g" cy="%g" r="%g"/></clipPath></defs>' % (cx, cy, r)]
    # o gato espia por tras do ingresso
    svg.append('<g transform="translate(600 12)">'
               '<path d="M-48,14 C-54,-18 -44,-42 -32,-52 L-30,-86 L-8,-58 C-3,-60 3,-60 8,-58 L30,-86 L32,-52 C44,-42 54,-18 48,14 Z" fill="#231820" filter="url(#mao)"/>'
               '<path d="M-26,-70 L-22,-58 L-14,-62 Z M26,-70 L22,-58 L14,-62 Z" fill="#7A3E5A" opacity=".8"/>'
               '<ellipse cx="-17" cy="-24" rx="10" ry="9" fill="#F2B544"/><ellipse cx="17" cy="-24" rx="10" ry="9" fill="#F2B544"/>'
               '<ellipse cx="-16" cy="-24" rx="2.6" ry="7.5" fill="#231820"/><ellipse cx="18" cy="-24" rx="2.6" ry="7.5" fill="#231820"/>'
               '<circle cx="-14" cy="-27" r="1.8" fill="#FFF6DD"/><circle cx="20" cy="-27" r="1.8" fill="#FFF6DD"/>'
               '<path d="M-4,-10 L4,-10 L0,-5 Z" fill="#E59AA8"/>'
               '<g stroke="#F4E9D5" stroke-width=".9" opacity=".75" fill="none"><path d="M-12,-6 L-44,-12 M-12,-3 L-44,0 M12,-6 L44,-12 M12,-3 L44,0"/></g></g>')
    svg.append('<path d="%s" fill="#F5E9CF" filter="url(#sombra)"/>' % ticket)
    svg.append('<g fill="none" stroke="#3B2A33" filter="url(#mao)"><rect x="16" y="16" width="%d" height="%d" rx="10" stroke-width="1.4"/>'
               '<rect x="24" y="24" width="%d" height="%d" rx="6" stroke-width=".7"/>'
               '<rect x="%d" y="16" width="%d" height="%d" rx="10" stroke-width="1.4"/>'
               '<path d="M%d,30 V%d" stroke-width="2" stroke-dasharray="3 9" stroke-linecap="round"/></g>' % (X - 32, H - 32, X - 48, H - 48, X + 16, W - X - 32, H - 32, X, H - 30))
    svg.append('<g clip-path="url(#janela4)"><svg x="%g" y="%g" width="%g" height="%g" viewBox="30 150 510 510" preserveAspectRatio="xMidYMid slice">%s</svg></g>' % (cx - r, cy - r, 2 * r, 2 * r, mini))
    svg.append('<g fill="none" filter="url(#mao)"><circle cx="%g" cy="%g" r="%g" stroke="#3B2A33" stroke-width="2"/><circle cx="%g" cy="%g" r="%g" stroke="#E8752F" stroke-width="1.4" stroke-dasharray="2 6"/></g>' % (cx, cy, r, cx, cy, r + 10))
    # patinhas por cima da borda
    svg.append('<g fill="#231820" filter="url(#mao)"><ellipse cx="572" cy="10" rx="17" ry="11"/><ellipse cx="628" cy="10" rx="17" ry="11"/></g>'
               '<g stroke="#F4E9D5" stroke-width="1" opacity=".55"><path d="M566,13 v6 M574,13 v6 M622,13 v6 M630,13 v6"/></g>')
    svg.append('</svg>')
    t_ing = ('<div class="ingresso"><div class="tk">%s'
             '<div class="miolo"><div class="entrada">Entrada · um leitor</div><div class="t1">%s</div><div class="t2 caber">%s</div>'
             '<div class="sub">%s</div><div class="data">%s</div></div>'
             '<div class="canhoto"><div class="rs">R$</div><div class="n30">30</div><div class="vg">%s</div><div class="num">Nº 01 / 20</div></div>'
             '</div></div>') % ("".join(svg), T["titulo1"], T["titulo2"], T["sub"].replace("no Parque", "<br>no Parque"), T["data"], T["vagas"])
    rodape_abob = '<svg style="left:0;top:0" width="1080" height="1350">%s</svg>' % "".join(
        abobora(x, y, k, "--abobora:%s" % c) for x, y, k, c in [(90, 1310, 3.2, "#E8752F"), (200, 1326, 2.0, "#F2B544"), (980, 1304, 3.4, "#E8752F"), (870, 1328, 2.1, "#C8324F"), (1050, 1340, 1.8, "#F2B544")])
    corpo = fundo + marca_html("#F2B544", "#F4E9D5", "left:0;right:0;top:40px")
    corpo += t_ing + rodape_abob
    corpo += '<div class="texto">%s<div class="cta">%s</div></div>' % (icones_html("#F4E9D5", 56, 14), T["cta"])
    css = '''
.peca{background:radial-gradient(ellipse 80% 65% at 50% 45%,#2C5254 0%,#1E3B3D 50%,#11211F 100%)}
.ingresso{left:60px;top:292px;width:960px;height:560px;transform:rotate(-4deg)}
.tk{position:relative;width:960px;height:560px}
.tk>svg{position:absolute;left:0;top:0}
.miolo{position:absolute;left:396px;top:40px;height:480px;justify-content:center;width:318px;display:flex;flex-direction:column;align-items:flex-start;color:#2A1E24}
.entrada{font-family:'Cinzel';font-weight:700;font-size:15px;letter-spacing:.32em;color:#A8355D}
.t1{margin-top:26px;font-family:'Cormorant';font-style:italic;font-weight:700;font-size:52px;line-height:1}
.t2{width:318px;white-space:nowrap;font-family:'Shrikhand';font-size:76px;line-height:1.15;color:#E8752F;text-shadow:3px 4px 0 #2A1E24}
.sub{margin-top:16px;font-family:'Cormorant';font-weight:600;font-size:33px;line-height:1.1}
.data{margin-top:22px;font-family:'Cinzel';font-weight:700;font-size:19px;letter-spacing:.1em;color:#A8355D}
.canhoto{position:absolute;left:760px;top:40px;width:184px;height:480px;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#2A1E24}
.rs{font-family:'Cinzel';font-weight:700;font-size:26px;letter-spacing:.1em}
.n30{font-family:'Shrikhand';font-size:104px;line-height:1;color:#E8752F;text-shadow:3px 4px 0 #2A1E24}
.vg{margin-top:16px;font-family:'Cinzel';font-weight:700;font-size:19px;letter-spacing:.14em}
.num{margin-top:30px;font-family:'Cormorant';font-style:italic;font-weight:600;font-size:22px;color:#A8355D}
.texto{left:30px;right:30px;top:990px;display:flex;flex-direction:column;align-items:center}
.cta{margin-top:26px;font-family:'Cinzel';font-weight:700;font-size:15px;letter-spacing:.3em;margin-right:-.3em;color:#F2B544}
'''
    return pagina("Halloween · ingresso", css, corpo + CABER_JS)


# ============================================================ V5 · livro pop-up
def v5():
    s = ['<svg style="left:0;top:0" width="1080" height="1350"><defs>'
         '<linearGradient id="ceuPop" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A2048"/><stop offset="1" stop-color="#6A3E6E"/></linearGradient>'
         '<clipPath id="arcoPop"><path d="M0,520 V200 A200,200 0 0 1 400,200 V520 Z"/></clipPath></defs>']
    s.append(estrelas(90, 1080, 1350, seed=31, cor="#F4E9D5", evitar=lambda x, y: y > 720))
    # o livro aberto
    s.append('<path d="M54,800 C250,770 430,780 540,812 C650,780 830,770 1026,800 L1052,1262 C840,1236 650,1240 540,1268 C430,1240 240,1236 28,1262 Z" fill="#3D1820" stroke="#F2B544" stroke-width="2"/>')
    for k in range(5, 0, -1):
        d = k * 4
        s.append('<path d="M%d,%d C250,%d 430,%d 540,%d L540,%d C430,%d 250,%d %d,%d Z" fill="#E9DCC2" stroke="#B9A88A" stroke-width=".8"/>'
                 % (84 - d, 786 + d, 760 + d, 768 + d, 800 + d, 1236 + d, 1208 + d, 1206 + d, 66 - d, 1232 + d))
        s.append('<path d="M%d,%d C830,%d 650,%d 540,%d L540,%d C650,%d 830,%d %d,%d Z" fill="#E9DCC2" stroke="#B9A88A" stroke-width=".8"/>'
                 % (996 + d, 786 + d, 760 + d, 768 + d, 800 + d, 1236 + d, 1208 + d, 1206 + d, 1014 + d, 1232 + d))
    s.append('<path d="M84,786 C250,760 430,768 540,800 L540,1236 C430,1208 250,1206 66,1232 Z" fill="#F7EEDB"/>')
    s.append('<path d="M996,786 C830,760 650,768 540,800 L540,1236 C650,1208 830,1206 1014,1232 Z" fill="#F7EEDB"/>')
    s.append('<path d="M540,800 L540,1236" stroke="#B9A88A" stroke-width="2"/><path d="M520,804 C530,806 536,808 540,812 C544,808 550,806 560,804 L560,1236 L520,1236Z" fill="#000" opacity=".06"/>')
    # o arco de papel que salta do livro (fundo)
    arco = ('<g transform="translate(340 300)" filter="url(#papelrecortado)"><g clip-path="url(#arcoPop)">'
            '<rect width="400" height="520" fill="url(#ceuPop)"/>%s%s%s</g>'
            '<path d="M10,520 V200 A190,190 0 0 1 390,200 V520" fill="none" stroke="#F2B544" stroke-width="1.4"/></g>'
            ) % (estrelas(40, 400, 400, seed=6, cor="#F4E9D5"), lua(200, 128, 80, linha="#F2D27E", opac_raios=.5), morcegos([(70, 150, 1.6, -8), (330, 120, 1.2, 8), (350, 220, .9, -4)], "#1B1426"))
    s.append(arco)
    s.append('<g filter="url(#papelrecortado)">%s</g>' % arvore(540, 850, 1.0, COPA_VIVA + ';--vagalume:0'))
    s.append('<g filter="url(#papelrecortado)">%s</g>' % piquenique(96, 872, 1.95))
    s.append('<g filter="url(#papelrecortado)">%s%s%s</g>' % (gato(790, 1016, 2.2), abobora(910, 1004, 1.9), abobora(866, 1020, 1.15, "--abobora:#F2B544")))
    s.append(selo(960, 830, 78, 14, "#E8752F", "#FFF4DE", T["preco"], T["vagas"]))
    s.append('</svg>')
    corpo = "".join(s)
    corpo += marca_html("#F2B544", "#F4E9D5", "left:0;right:0;top:36px")
    corpo += '<div class="topo"><div class="t1">%s <span>%s</span></div><div class="sub">%s</div></div>' % (T["titulo1"], T["titulo2"], T["sub"])
    corpo += '<div class="pg pe"><div class="data">Sáb, 31 de outubro</div><div class="hora">15h · Parque da Jaqueira</div></div>'
    corpo += '<div class="pg pd"><div class="inc">Ecobag, marcador de livro, café,<br>bolo, frutinhas e sorteio de livro</div></div>'
    corpo += '<div class="cta">%s</div>' % T["cta"]
    css = '''
.peca{background:radial-gradient(ellipse 85% 70% at 50% 40%,#8A3349 0%,#5A2238 50%,#2E1220 100%)}
.topo{left:0;right:0;top:150px;display:flex;flex-direction:column;align-items:center;text-align:center;color:#F4E9D5}
.t1{font-family:'Cormorant';font-style:italic;font-weight:700;font-size:56px;line-height:1}
.t1 span{font-family:'Shrikhand';font-style:normal;font-size:74px;color:#F2B544;text-shadow:4px 5px 0 #2E1220}
.sub{margin-top:12px;font-family:'Cormorant';font-weight:600;font-size:34px}
.pg{top:1086px;display:flex;flex-direction:column;align-items:center;text-align:center;color:#2A1E24}
.pe{left:110px;width:400px;transform:rotate(1.2deg)}
.pd{left:570px;width:420px;transform:rotate(-1.2deg)}
.data{font-family:'Cinzel';font-weight:700;font-size:24px;letter-spacing:.08em;color:#A8355D}
.hora{margin-top:6px;font-family:'Cormorant';font-style:italic;font-weight:600;font-size:27px}
.inc{font-family:'Cormorant';font-style:italic;font-weight:600;font-size:24px;line-height:1.2}
.cta{left:0;right:0;top:1290px;text-align:center;font-family:'Cinzel';font-weight:700;font-size:15px;letter-spacing:.3em;margin-right:-.3em;color:#F2B544}
'''
    return pagina("Halloween · livro pop-up", css, corpo)


VARS = {1: ("var1_tiragem", v1), 2: ("var2_transborda", v2), 3: ("var3_cartaz", v3), 4: ("var4_ingresso", v4), 5: ("var5_popup", v5)}

if __name__ == "__main__":
    qual = [int(a) for a in sys.argv[1:]] or list(VARS)
    pares = []
    for k in qual:
        nome, f = VARS[k]
        open(os.path.join(AQUI, nome + ".html"), "w", encoding="utf-8").write(f())
        pares.append((nome, montar.montar(nome)))
    montar.fotografar(pares)
