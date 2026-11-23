# -*- coding: utf-8 -*-
"""Catalogo dos elementos recortados: nome, categoria, onde usar e onde evitar.

Gera na pasta do clube:  Elementos recortados/<categoria>/<slug>.png + catalogo HTML + LEIAME.txt
As rendas saem tambem recoloridas na paleta das cartinhas.
"""
import os, json, shutil, html
import numpy as np
from PIL import Image
from pathlib import Path as _P
_REPO = _P(__file__).resolve().parents[3]  # raiz do repositório

AQUI = os.path.dirname(os.path.abspath(__file__))
BRUTOS = os.path.join(AQUI, "brutos")
DESTINO = str(_REPO / 'gatoteca/artes/Elementos recortados')

# ---------------------------------------------------------------- categorias: o que sao e a regra geral
CATS = {
    "1 Lacres e selos": ("Selos de cera (rosa, lilás, vinho, dourado, escuros).",
                         "Fechar a cartinha ou o envelope; marcar o destaque (preço, data) AO LADO dele; selar o «convite».",
                         "Em cima do mascote ou de texto; mais de dois por peça; misturar rosa, lilás e vinho no mesmo post (escolher uma família)."),
    "2 Astros": ("Sóis e luas com rosto, estrelas douradas, céu pintado.",
                 "Pontuar o campo de estrelas desenhadas; sol ou lua de rosto como emblema secundário em capa de tema místico.",
                 "Ampliar (são pequenos, 736 px na origem); mais de um sol ou lua de rosto por peça."),
    "3 Corações e joias": ("Corações (dourado, anatômico, broche, sagrado), medalhões, anéis, joias de ouro.",
                           "Afeto, depoimentos, «livro favorito», romance; o sagrado coração casa com a moldura de raios.",
                           "Posts de serviço (data, preço, regras); o coração anatômico em post leve."),
    "4 Flores e asas": ("Borboletas, flores (peônia, lírio, hibisco), galho florido, arabescos dourados.",
                        "Cantos e bordas, entrar pela margem; borboleta para transformação, começos, metamorfose.",
                        "Cobrir o rosto do mascote; pôr flor fotografada colada a flor desenhada (os dois estilos brigam)."),
    "5 Molduras e quadros": ("Espelho oval ornamentado, quadros de pintura, flores prensadas, rosa em papel rasgado.",
                             "Retrato do mascote, foto do livro do mês ou de convidado; papel rasgado para citação curta.",
                             "Texto longo dentro do quadro; moldura de pintura em post de aviso rápido."),
    "6 Luz e mistério": ("Lanternas, poste de praça, ampulheta, bola de cristal, cristal, frascos.",
                         "Encontro presencial e à noite (o poste é a cara do Parque da Jaqueira); ampulheta = prazo, últimas vagas; bola = enquete.",
                         "Frasco «Fairy Dust» fora de contexto lúdico (o texto é em inglês)."),
    "7 Arte clássica e mar": ("Cabeça de estátua, anjo, sereia, conchas, pérolas, peixe azul.",
                              "Temas de mito, poesia, filosofia; a sereia (Waterhouse, domínio público) serve para Lilith e mulheres míticas; pérolas casam com o anel de pérolas.",
                              "Post infantil; a estátua rachada em post alegre."),
    "8 Leitura": ("Livro ilustrado aberto, gato vintage com livro.",
                  "Livro aberto como objeto de cena; «Mulherzinhas» quando for esse o livro.",
                  "O gato vintage JUNTO do mascote (dois gatos-personagem confundem); o livro com título visível em indicação de outro livro."),
    "9 Rendas": ("Faixas de renda extraídas como tinta de uma cor só, em versões na paleta.",
                 "Borda de cima ou de baixo do cartão, divisória entre blocos, barra do envelope.",
                 "Ampliar além de 1080 px de largura; para impresso, buscar no Canva «lace borders» (resolução maior)."),
}

# ---------------------------------------------------------------- cada recorte: (bruto, slug, nome, categoria, nota)
E = [
    ("selos_rosa_01", "lacre_coracao_lua_sol", "Lacre coração com lua e sol dourados", 1, "Rosa; o mais «cartinha de amor». Bom para convite especial."),
    ("selos_rosa_02", "lacre_laco_rosa", "Lacre de laço", 1, "Rosa-bebê, sem dourado: delicado."),
    ("selos_rosa_03", "lacre_cisnes", "Lacre de cisnes", 1, "Casal, par, parceria."),
    ("selos_rosa_04", "lacre_laco_dourado", "Lacre de laço dourado", 1, "Presente, sorteio, «ganhe»."),
    ("selos_rosa_05", "lacre_coracao_lua", "Lacre coração com lua", 1, "Malva; noite e afeto."),
    ("selos_rosa_06", "lacre_lua_e_sol", "Lacre lua e sol", 1, "Rosa forte; o mais «tarô» dos rosas."),
    ("selos_rosa_07", "lacre_sol_dourado", "Lacre de sol dourado", 1, "Celebração, manhã, «bom dia»."),
    ("selos_rosa_08", "lacre_lua_flores", "Lacre lua com flores", 1, "Malva; poesia, noite calma."),
    ("selos_rosa_09", "lacre_ramo", "Lacre de ramo", 1, "Natureza, Parque, leveza."),
    ("selos_rosa_10", "lacre_lilases", "Lacre de lilases", 1, "Primavera, flores."),
    ("selos_rosa_11", "lacre_estrelas_douradas", "Lacre dourado de estrelas", 1, "Dourado inteiro: festa, edição especial."),
    ("selos_rosa_12", "lacre_tulipa", "Lacre de tulipa", 1, "⭐ Use nos posts com a TULIPA."),
    ("selos_rosa_13", "borboleta_de_ouro", "Borboleta de ouro", 4, "Joia; translúcida, fica bem sobre fundo escuro."),
    ("selos_rosa_14", "sol_joia", "Sol de ouro (joia)", 2, "Sol estilizado com espiral."),
    ("selos_rosa_15", "hibisco_iridescente", "Hibisco iridescente", 4, "Flor perolada; cantos."),
    ("selos_lilas_01a", "lacre_orbitas", "Lacre de órbitas", 1, "Lilás; cosmos, astrologia."),
    ("selos_lilas_01b", "lacre_coroa_de_ramos", "Lacre coroa de ramos", 1, "Lilás; conquista, aniversário do clube."),
    ("selos_lilas_02", "lacre_campo_lavanda_lua", "Lacre campo de lavanda e lua", 1, "Cena pintada; noite tranquila."),
    ("selos_lilas_03", "lacre_mariposa_fases_da_lua", "Lacre mariposa e fases da lua", 1, "⭐ Mariposa + lua: mistério, Lilith, noite."),
    ("selos_lilas_04", "lacre_margarida", "Lacre de margarida", 1, "Leve, alegre."),
    ("selos_lilas_05", "lacre_lavanda_ramo", "Lacre ramo de lavanda", 1, "Calma, descanso."),
    ("selos_lilas_06", "lacre_lavanda_clara", "Lacre lavanda clara", 1, "Lilás muito claro: some em fundo claro."),
    ("selos_lilas_07", "lacre_umbela_magenta", "Lacre de umbela (magenta)", 1, "Magenta vivo; destaque."),
    ("selos_lilas_08", "lacre_lavanda_dourada", "Lacre lavanda com dourado", 1, "Mais nobre dos lilases."),
    ("selos_lilas_09a", "lacre_cogumelos", "Lacre de cogumelos dourados", 1, "Roxo escuro; floresta, fantasia, Halloween."),
    ("selos_lilas_09b", "lacre_arabesco_magenta", "Lacre de arabesco dourado", 1, "Magenta com ouro; edição especial."),
    ("selos_lilas_10", "lacre_flor_oval", "Lacre oval de flor", 1, "Minimalista."),
    ("selos_lilas_11", "lacre_coracoes", "Lacre de corações", 1, "Afeto, «a gente ama vocês»."),
    ("selos_lilas_12", "lacre_cerejas", "Lacre de cerejas", 1, "Roxo escuro; doce, lanche."),
    ("selos_lilas_13", "lacre_rosa_magenta", "Lacre de rosa (magenta)", 1, "Romance."),
    ("lacre_vinho_01", "lacre_vinho_lua", "Lacre vinho com lua dourada", 1, "⭐ O lacre principal para Lilith e encontros à noite; maior resolução da coleção."),
    ("espelho_01", "espelho_oval_jardim", "Espelho oval com jardim, fada e estrelas", 5, "Composição pronta: o oval é transparente, ponha o mascote ou uma foto atrás."),
    ("lanternas_01", "galho_florido", "Galho de árvore com flores brancas", 4, "Dossel para o alto da peça (entra pelo canto); tem borda branca de adesivo."),
    ("lanternas_02", "lanterna_pendurada_1", "Lanterna pendurada", 6, "Pendurar do alto da peça; noite, encontro."),
    ("lanternas_03", "lirios_brancos", "Lírios brancos", 4, "Canto inferior; luto leve, delicadeza."),
    ("lanternas_04", "lanterna_pendurada_2", "Lanterna pendurada (par)", 6, "Use junto da 1 para o par da referência."),
    ("lanternas_05", "poste_de_praca", "Poste de praça com três lanternas", 6, "⭐ Parque da Jaqueira, encontro presencial à noite."),
    ("lanternas_06", "peonias_brancas", "Peônias brancas com folhas douradas", 4, "Canto; casamento, delicadeza."),
    ("colagem_01", "cabeca_estatua", "Cabeça de estátua clássica", 7, "Filosofia, mito, «o que os gregos diriam»."),
    ("colagem_02", "ceu_pintado_lua", "Céu pintado com lua e nuvens", 2, "Canto superior direito (tem recorte em curva); noite."),
    ("colagem_03", "anjo_alado", "Anjo alado (estátua)", 7, "Poesia, sagrado, consolo."),
    ("colagem_04", "brilho_dourado_1", "Brilho dourado de 4 pontas", 2, "Espalhar 2 ou 3 entre as estrelas desenhadas."),
    ("colagem_05", "coracao_anatomico_ouro", "Coração anatômico dourado", 3, "Intensidade, «livro que doeu»."),
    ("colagem_06", "lanterna_pequena", "Lanterna pequena", 6, "Detalhe pendurado."),
    ("colagem_07", "coracao_broche_azul", "Coração broche azul com lua", 3, "Noite e afeto; contrasta com o jade."),
    ("colagem_08", "brilho_dourado_2", "Brilho dourado de 4 pontas (2)", 2, "Idem."),
    ("colagem_09", "flor_folha_dourada", "Flor-folha dourada", 4, "Joia de canto."),
    ("colagem_10", "lua_dourada_rosto", "Lua dourada com rosto", 2, "Emblema secundário; noite, sono, sonho."),
    ("colagem_11", "borboleta_rosa", "Borboleta rosa", 4, "Rosa-postal: casa direto com a paleta."),
    ("colagem_13", "estrela_dourada_pequena", "Estrelinha dourada", 2, "Ponto de brilho."),
    ("colagem_14", "flor_dourada", "Flor dourada", 4, "Joia de canto."),
    ("colagem_15", "estrela_bronze_6", "Estrela de bronze (6 pontas)", 2, "Ponto de brilho."),
    ("colagem_16", "sagrado_coracao_ouro", "Sagrado coração dourado", 3, "Devoção ao livro, «favorito da vida»."),
    ("colagem_17", "rosa_papel_rasgado", "Rosa em papel rasgado", 5, "⭐ Papel para citação curta (escreva ao lado da rosa)."),
    ("colagem_18a", "lacre_escuro_agua_viva", "Lacre escuro de água-viva", 1, "Mar, profundezas."),
    ("colagem_18b", "borboleta_verde_agua", "Borboleta verde-água", 4, "⭐ Casa com o jade da paleta."),
    ("colagem_19", "estrelinha_bronze", "Estrelinha de bronze", 2, "Ponto de brilho."),
    ("colagem_20", "estrela_bronze_8", "Estrela de bronze (8 pontas)", 2, "Ponto de brilho maior."),
    ("colagem_21", "quadro_estreito_paisagem", "Quadro estreito de paisagem", 5, "Lateral da peça, «janela»."),
    ("colagem_22", "quadro_oval_flores_1", "Quadro oval de flores", 5, "Galeria, lembrança."),
    ("colagem_23", "lacre_escuro_navio", "Lacre escuro de navio", 1, "Aventura, viagem, livro de mar."),
    ("colagem_24", "botao_sol_lua", "Medalhão sol e lua", 3, "Pequeno; ponto focal de canto."),
    ("colagem_25", "medalhao_coracao", "Medalhão de coração", 3, "Lembrança, amizade."),
    ("colagem_26", "concha_iridescente", "Concha iridescente", 7, "Mar, sereia."),
    ("colagem_27", "sereia_na_pedra", "Sereia na pedra", 7, "⭐ Lilith, mulheres míticas, mar (pintura de domínio público)."),
    ("colagem_28", "quadro_de_rosas", "Quadro de rosas", 5, "Galeria; romance."),
    ("colagem_29", "brilho_dourado_3", "Brilho dourado de 4 pontas (3)", 2, "Idem."),
    ("colagem_30", "concha_com_perolas", "Concha com pérolas", 7, "Casa com o anel de pérolas."),
    ("colagem_31", "quadro_oval_flores_2", "Quadro oval de flores (2)", 5, "Galeria."),
    ("colagem_32", "ampulheta", "Ampulheta", 6, "⭐ Prazo, últimas vagas, contagem regressiva."),
    ("colagem_33", "peixe_azul_bordado", "Peixe azul (bordado)", 7, "Mar; detalhe exótico."),
    ("colagem_34", "garrafinha_com_rosa", "Garrafinha com rosa", 6, "⭐ «Mensagem na garrafa»: carta, recado, CTA."),
    ("colagem_35", "brilho_dourado_4", "Brilho dourado de 4 pontas (4)", 2, "Idem."),
    ("sol_lua_01", "sol_rosto_1", "Sol com rosto (gravura)", 2, "Emblema de tarô; manhã."),
    ("sol_lua_02", "flor_branca_arabesco", "Flor branca com arabescos", 4, "Canto superior."),
    ("sol_lua_03", "lua_prata_rosto", "Lua prateada com rosto", 2, "Emblema de noite."),
    ("sol_lua_04", "frasco_fairy_dust", "Frasco «Fairy Dust»", 6, "Só em post lúdico (texto em inglês)."),
    ("sol_lua_07", "estrela_dourada_8_longa", "Estrela dourada de 8 pontas", 2, "⭐ Igual às estrelas da referência: estrela-guia."),
    ("sol_lua_08", "arabesco_dourado", "Arabesco dourado", 4, "Moldura de canto, sob título."),
    ("sol_lua_10", "borboleta_rosa_iridescente", "Borboleta rosa iridescente", 4, "Rosa-postal; transformação."),
    ("sol_lua_12", "perola_no_suporte", "Pérola/bola no suporte", 6, "Bola de cristal clara; enquete, previsão."),
    ("sol_lua_13", "sagrado_coracao_vermelho", "Sagrado coração vermelho", 3, "Paixão, favorito."),
    ("sol_lua_14", "concha_gravura", "Concha (gravura)", 7, "Mar, em tom de papel."),
    ("sol_lua_15", "lua_prata_estrela", "Lua prateada com estrela", 2, "Noite, boa noite."),
    ("sol_lua_17", "cristal_quartzo", "Cristal de quartzo", 6, "Mistério, clareza."),
    ("sol_lua_18", "flores_prensadas", "Quatro quadrinhos de flores prensadas", 5, "Rodapé, galeria, herbário."),
    ("sol_lua_19", "livro_mulherzinhas", "Livro aberto «Mulherzinhas»", 8, "Só quando o livro for esse (título visível)."),
    ("sol_lua_20", "gato_vintage_com_livro", "Gato vintage com livro", 8, "⛔ Não usar junto do mascote."),
    ("sol_lua_21", "sol_rosto_2", "Sol com rosto (gravura, 2)", 2, "Par do sol 1."),
    ("sol_lua_22", "anel_sinete", "Anel de sinete dourado", 3, "Detalhe; compromisso."),
    ("sol_lua_23", "aneis_dourados", "Anéis dourados", 3, "Romance, casamento literário."),
]
RENDAS = [("renda_01", "renda_festonada"), ("renda_02", "renda_floral_larga"), ("renda_03", "renda_delicada"),
          ("renda_04", "renda_floral_clara"), ("renda_05", "renda_floral_malva"), ("renda_06", "renda_flores_pequenas")]
PALETA = {"jade": "#5F857C", "rosa": "#C799AA", "ardosia": "#30323C", "ameixa": "#624956", "perola": "#F1E3E6", "ouro": "#D9B36A"}


def nome_cat(i):
    return list(CATS)[i - 1]


def gerar():
    if os.path.exists(DESTINO):
        shutil.rmtree(DESTINO)
    for c in CATS:
        os.makedirs(os.path.join(DESTINO, c), exist_ok=True)
    itens = []
    for bruto, slug, nome, cat, nota in E:
        src = os.path.join(BRUTOS, bruto + ".png")
        im = Image.open(src)
        dst = os.path.join(DESTINO, nome_cat(cat), slug + ".png")
        im.save(dst)
        itens.append(dict(slug=slug, nome=nome, cat=nome_cat(cat), nota=nota, w=im.width, h=im.height, rel=nome_cat(cat) + "/" + slug + ".png"))
    for bruto, slug in RENDAS:
        im = Image.open(os.path.join(BRUTOS, bruto + ".png"))
        a = np.asarray(im)[..., 3]
        for cor, hx in PALETA.items():
            rgb = tuple(int(hx[i:i + 2], 16) for i in (1, 3, 5))
            out = np.zeros(a.shape + (4,), np.uint8)
            out[..., :3] = rgb
            out[..., 3] = a
            dst = os.path.join(DESTINO, "9 Rendas", "%s_%s.png" % (slug, cor))
            Image.fromarray(out, "RGBA").save(dst)
        itens.append(dict(slug=slug, nome="Renda " + slug.split("_", 1)[1].replace("_", " "), cat="9 Rendas", nota="Seis cores: " + ", ".join(PALETA),
                          w=im.width, h=im.height, rel="9 Rendas/%s_jade.png" % slug))
    json.dump(itens, open(os.path.join(AQUI, "catalogo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return itens


def pagina(itens):
    blocos = ""
    for c, (oque, usar, evitar) in CATS.items():
        cards = "".join(
            '<figure><div class="img"><img src="%s" alt="%s"></div><figcaption><b>%s</b><span>%s</span><code>%s · %d×%d px</code></figcaption></figure>'
            % (html.escape(i["rel"]), html.escape(i["nome"]), html.escape(i["nome"]), html.escape(i["nota"]), html.escape(i["slug"]), i["w"], i["h"])
            for i in itens if i["cat"] == c)
        blocos += ('<section><h2>%s</h2><p class="oque">%s</p><div class="regras"><div><i>Usar</i>%s</div><div><i>Evitar</i>%s</div></div>'
                   '<div class="grade">%s</div></section>') % (html.escape(c[2:]), html.escape(oque), html.escape(usar), html.escape(evitar), cards)
    return '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Elementos recortados</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Cormorant+Garamond:ital,wght@0,500;0,700;1,500&display=swap" rel="stylesheet">
<style>
:root{--jade:#5F857C;--rosa:#C799AA;--noite:#30323C;--ameixa:#624956;--perola:#F1E3E6}
*{box-sizing:border-box}body{margin:0;background:var(--perola);color:var(--noite);font:19px/1.35 'Cormorant Garamond',serif}
header{background:var(--jade);color:var(--perola);padding:44px 20px 34px;text-align:center}
header h1{font:44px 'DM Serif Display',serif;margin:0 0 8px;color:var(--rosa);-webkit-text-stroke:1.5px var(--ameixa)}
header p{max-width:780px;margin:0 auto}
main{max-width:1240px;margin:0 auto;padding:10px 16px 60px}
h2{font:30px 'DM Serif Display',serif;margin:44px 0 6px;color:var(--ameixa)}
.oque{margin:0 0 10px;font-style:italic}
.regras{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px}
.regras div{background:#fff8;border:1px solid #6249563a;border-radius:8px;padding:10px 14px}
.regras i{display:block;font-weight:700;font-style:normal;letter-spacing:.12em;text-transform:uppercase;font-size:14px;color:var(--jade)}
.regras div+div i{color:#9E3D52}
.grade{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:14px}
figure{margin:0;background:#fff;border:1px solid #62495622;border-radius:10px;overflow:hidden}
.img{aspect-ratio:1;display:flex;align-items:center;justify-content:center;padding:12px;
 background:repeating-conic-gradient(#e9e2e4 0% 25%,#f6f1f2 0% 50%) 50%/22px 22px}
.img img{max-width:100%;max-height:100%}
figcaption{padding:8px 12px 12px;display:flex;flex-direction:column;gap:4px}
figcaption b{font-size:19px;line-height:1.15}figcaption code{font-size:11px;opacity:.55}
@media(max-width:640px){.regras{grid-template-columns:1fr}}
</style></head><body>
<header><h1>Elementos recortados</h1><p>Os recortes das folhas de referência, com fundo transparente, em nove categorias.
Cada categoria diz o que é, onde usar e onde evitar; cada peça tem uma nota. São pequenos (as folhas tinham 736 px de largura):
usar como enfeite, até um quarto da largura do post.</p></header><main>''' + blocos + '</main></body></html>'


if __name__ == "__main__":
    itens = gerar()
    open(os.path.join(DESTINO, "Catálogo de elementos.html"), "w", encoding="utf-8").write(pagina(itens))
    linhas = ["ELEMENTOS RECORTADOS · Clube do Livro Entrelinhas", "",
              "Recortes com fundo transparente das folhas de referência. Pequenos: usar como enfeite (até 1/4 da largura do post).",
              "Direitos: as folhas vieram do Pinterest/Canva. Para peça paga ou impressa, preferir o equivalente do Canva Pro ou de domínio público.", ""]
    for c, (oque, usar, evitar) in CATS.items():
        linhas += [c.upper(), "  O que é: " + oque, "  Usar: " + usar, "  Evitar: " + evitar]
        linhas += ["    %-34s %s" % (i["slug"], i["nota"]) for i in itens if i["cat"] == c]
        linhas.append("")
    open(os.path.join(DESTINO, "LEIAME.txt"), "w", encoding="utf-8").write("\n".join(linhas))
    print(len(itens), "elementos catalogados")
