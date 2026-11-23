# -*- coding: utf-8 -*-
"""Guia da identidade «cartinhas» + exportacao das pecas de exemplo para a pasta do clube."""
import os, shutil
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[2]  # raiz do repositório

AQUI = os.path.dirname(os.path.abspath(__file__))
D = str(_REPO / 'gatoteca/artes/Identidade - cartinhas')
os.makedirs(D, exist_ok=True)
for n, nome in (("capa", "1 - capa (três cartas)"), ("verso", "2 - verso do postal (o convite)"),
                ("envelope", "3 - envelope (chamada final)"), ("componentes", "0 - componentes e paleta")):
    shutil.copy(os.path.join(AQUI, "saida", "cartinha_%s.png" % n), os.path.join(D, nome + ".png"))

REGRAS = [
    ("A peça é um objeto", "Cada post é uma cartinha fotografada: cartão-postal, verso escrito, envelope, selo. O fundo é o veludo escuro da mesa (#141116), nunca uma cor chapada solta. Pode haver uma, duas ou três cartas sobrepostas e levemente giradas (até 10°)."),
    ("A moldura dupla de cantos recortados", "Toda carta tem a moldura de duas linhas finas em ameixa, com os cantos recortados para dentro. É a assinatura do sistema, como o arco era na versão tarô."),
    ("O emblema no anel de pérolas", "No centro da frente fica um medalhão de pérolas com raios finos saindo. Dentro dele vai o mascote (uma pose do banco) ou o olho de gato. Um emblema por peça."),
    ("O céu de estrelas", "Poucas estrelas grandes de 8 pontas em rosa com contorno ameixa e muitas pequenas de 5 pontas em noite. Nunca estrela dourada de clip-art no lugar delas; as douradas recortadas entram só como 2 ou 3 brilhos extras."),
    ("Duas cores que se alternam", "Jade e rosa-postal são as cores das cartas; quando uma carta é jade, a vizinha é rosa. Noite e ameixa fazem as linhas e o texto; pérola e ouro fazem os enfeites; o vinho é só do lacre."),
    ("O olho de gato", "O símbolo da marca, no lugar do olho com diamante da referência: olho amendoado, íris verde do mascote, pupila em fenda. Aparece no forro arlequim, nos corações de pérola e como marca d'água no verso (opacidade 7%)."),
    ("O forro arlequim", "Losangos rosa e jade com quatro ícones que se revezam: olho de gato, estrela, livro aberto e lua. Serve de forro do envelope, de carta de fundo ou de faixa; nunca atrás de texto."),
    ("Tipografia", "Título em DM Serif Display (serifa gorda), em rosa-claro com contorno ameixa, levemente girado. Rótulos em Cinzel, caixa alta espaçada. Mensagem e informações em Caveat, escritas «à mão» nas linhas do postal. Texto corrido curto em Cormorant itálico."),
    ("Os elementos recortados", "Entram como objetos sobre a mesa ou presos à carta: o lacre fecha (um por peça), a lanterna pendura do alto, a estrela dourada brilha num canto. Até um quarto da largura do post; nunca por cima do mascote ou do texto."),
    ("O mascote", "Sempre uma pose pronta do banco, dentro do medalhão, no selo postal ou espiando por cima de uma carta. Não misturar com o gato vintage da colagem."),
]

PECAS = [
    ("1 - capa (três cartas).png", "Capa", "Envelope arlequim, verso rosa e frente jade empilhados no veludo. A frente leva o título, o emblema com o mascote e o rótulo da edição; o lacre vinho prende o canto."),
    ("2 - verso do postal (o convite).png", "Verso do postal", "O slide de informação: «Cartão-postal», mensagem escrita à mão, quando, onde, quanto e o que inclui nas linhas; selo com o mascote, carimbo de Recife, corações de pérola e o lacre embaixo."),
    ("3 - envelope (chamada final).png", "Envelope", "O último slide: envelope aberto, a cartinha «Garanta sua vaga» saindo, o mascote espiando por cima, lanternas penduradas e a chamada para a comunidade do WhatsApp."),
]

cards = "".join('<figure><img src="%s" alt="%s"><figcaption><b>%s</b>%s</figcaption></figure>' % (a, t, t, d) for a, t, d in PECAS)
regras = "".join('<div class="regra"><h3>%s</h3><p>%s</p></div>' % r for r in REGRAS)
html = '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Identidade cartinhas</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Cinzel:wght@700&family=Cormorant+Garamond:ital,wght@0,500;0,700;1,500&display=swap" rel="stylesheet">
<style>
:root{--jade:#5F857C;--rosa:#C799AA;--rosac:#E6C4D0;--noite:#30323C;--ameixa:#624956;--perola:#F1E3E6;--veludo:#141116}
*{box-sizing:border-box}body{margin:0;background:var(--veludo);color:var(--perola);font:19px/1.4 'Cormorant Garamond',serif}
header{padding:56px 20px 30px;text-align:center}
header small{font:700 13px Cinzel;letter-spacing:.4em;color:var(--rosa)}
header h1{font:56px 'DM Serif Display',serif;margin:8px 0;color:var(--rosac);-webkit-text-stroke:2px var(--ameixa);paint-order:stroke}
header p{max-width:760px;margin:0 auto;color:#e9dde0}
main{max-width:1180px;margin:0 auto;padding:0 16px 70px}
h2{font:32px 'DM Serif Display',serif;color:var(--rosa);margin:46px 0 14px}
.comp{width:100%;border-radius:10px;display:block}
.pecas{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}
figure{margin:0;background:#1f1a22;border:1px solid #ffffff14;border-radius:12px;overflow:hidden}
figure img{width:100%;display:block}
figcaption{padding:12px 16px 16px;display:flex;flex-direction:column;gap:4px}
figcaption b{font:22px 'DM Serif Display',serif;color:var(--rosac)}
.regras{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
.regra{background:var(--perola);color:var(--noite);border-radius:10px;padding:14px 18px;border:1px solid var(--ameixa);
 box-shadow:inset 0 0 0 6px var(--perola),inset 0 0 0 7px #62495688}
.regra h3{margin:0 0 4px;font:700 14px Cinzel;letter-spacing:.14em;text-transform:uppercase;color:var(--jade)}
.regra p{margin:0}
.ref{color:#cbbcc2;font-style:italic}
</style></head><body>
<header><small>CLUBE DO LIVRO ENTRELINHAS</small><h1>Identidade cartinhas</h1>
<p>Cada post é uma cartinha: cartão-postal, envelope e selo sobre o veludo escuro, com moldura dupla de cantos recortados,
medalhão de pérolas, céu de estrelas e o olho de gato como símbolo. Tirado da referência dos cartões RUKA, com o nosso mascote
e os nossos símbolos no lugar dos deles.</p></header>
<main>
<h2>Componentes e paleta</h2><img class="comp" src="0 - componentes e paleta.png" alt="componentes">
<p class="ref">Paleta medida na foto de referência (jade, rosa-postal, noite, ameixa, pérola) mais o ouro e o vinho dos lacres.</p>
<h2>Peças de exemplo</h2><div class="pecas">''' + cards + '''</div>
<h2>As regras</h2><div class="regras">''' + regras + '''</div>
<h2>Onde mora cada coisa</h2>
<p>Motor: <code>gatoteca/motor/cartinhas.py</code> (componentes: <code>cartao</code>, <code>moldura</code>, <code>anel_perolas</code>,
<code>olho_gato</code>, <code>coracao_perolas</code>, <code>guirlanda</code>, <code>arlequim</code>, <code>ceu</code>, <code>selo_postal</code>, <code>carimbo</code>, <code>titulo</code>).
Elementos recortados: pasta «Elementos recortados» (catálogo HTML com o que usar e o que evitar). Mascote: pasta «Mascote - banco de poses».</p>
</main></body></html>'''
open(os.path.join(D, "Guia da identidade cartinhas.html"), "w", encoding="utf-8").write(html)
print("ok", D)
