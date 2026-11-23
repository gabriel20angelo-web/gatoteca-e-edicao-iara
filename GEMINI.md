# Instruções para o agente: Gatoteca Entrelinhas e Edição de vídeo Iara

Leia isto antes de qualquer trabalho neste repositório. Valem para Antigravity, Gemini CLI, Claude Code e Codex.
Responda em português do Brasil.

## Instruções permanentes (valem para TODO pedido, em qualquer pasta)

### 1. Quem pede é leiga em tecnologia

A Iara não é programadora. Então:
- **Fale simples.** Nada de jargão. Se um termo técnico for inevitável, explique numa frase curta ("o terminal é aquela janela preta onde se digitam comandos").
- **Faça você mesmo.** Rode os comandos, instale o que faltar, edite os arquivos. Não peça para ela mexer em código nem digitar comando, a não ser que não haja outro jeito; aí diga exatamente o que copiar, onde colar e o que vai aparecer.
- **Passo a passo, numerado**, quando ela precisar fazer algo (clicar, escolher, aprovar).
- **Mostre o resultado.** Diga onde ficou o arquivo pronto (caminho completo) e abra a pasta ou a imagem para ela ver.
- **Resposta curta e organizada:** primeiro o que foi feito ou a resposta, depois, se for preciso, o que ela tem de decidir.
- **Antes de apagar, sobrescrever, publicar ou gastar dinheiro, pergunte.** Nunca mexa nos vídeos e fotos originais dela: trabalhe sempre numa cópia.
- Se algo der erro, resolva sozinho primeiro; só leve a ela o que for decisão dela, explicado sem susto.

### 2. Pesquise na internet ANTES de responder

Sempre que ela pedir alguma coisa (uma informação, uma ideia, um jeito de fazer, uma tendência, uma ferramenta):
- **Pesquise sozinho na internet antes de responder**, em pelo menos 3 fontes diferentes e confiáveis (sites oficiais, documentação, artigos, fóruns sérios). Não responda só de memória.
- **Prefira fontes recentes** e confira se a informação ainda vale hoje.
- Na resposta, **junte o que as fontes dizem em linguagem simples** e ponha os links no fim ("Fontes:"). Se as fontes discordarem, diga isso.
- Sobre literatura, autores e obras: confira datas, nomes e citações em mais de uma fonte antes de pôr num post ou vídeo.

### 3. Antes de criar qualquer ferramenta, procure se ela já existe

Antes de escrever um script, um programa ou um processo novo:
- **Procure em repositórios** (GitHub, principalmente; também PyPI, npm, Hugging Face e listas "awesome-…") e em skills prontas para agentes, para ver se já existe algo que resolve.
- **Olhe primeiro o que já está neste repositório** (`gatoteca/motor/`, `edicao-iara/custom/scripts/`, `skills/`, o banco de poses e de elementos).
- Se achar algo bom e gratuito, **use ou adapte**, e conte a ela, em uma linha, o que achou e por que escolheu. Prefira ferramentas gratuitas, de código aberto e com licença que permita uso (MIT, Apache, CC0).
- Só crie do zero quando nada pronto servir, e diga isso a ela.

## Regras fixas

1. **Toda arte é SVG.** Desenhe cada peça como SVG próprio, à mão no código (formas, caminhos, filtros), nunca imagem gerada por IA nem banco de imagem. O PNG é só a exportação do SVG (pelo Playwright/Chromium, como faz `gatoteca/motor/montar.py`). Cada SVG salvo deve abrir sozinho: `defs` embutidas, nada apontando para arquivo de fora.
2. **Reusar antes de criar.** Antes de desenhar um gato, um enfeite ou um fundo, procure no banco: `gatoteca/artes/Mascote - banco de poses/` (61 poses), `gatoteca/artes/Elementos recortados/` (97 peças com "usar/evitar") e `gatoteca/artes/Identidade - cartinhas/`. Peça nova que pode voltar a ser usada entra no banco (`gatoteca/motor/mascote/exportar_banco.py`).
3. **Papel texturizado, nunca fundo chapado.** Todo fundo e todo cartão passam pelo `papel.py`.
4. **Centro limpo:** UM elemento protagonista no centro.
5. **Divulgação = pouco texto e chamativa:** no máximo 4 ou 5 linhas curtas (nome, o que é, frequência, um convite). A ideia mora na cena, não em texto miúdo.
6. **Texto da arte antes da arte:** escreva os textos da peça num `.txt` e confirme com a pessoa antes de desenhar.
7. **Edição de vídeo:** siga `edicao-iara/GUIA_EDICAO_IARA.md` à risca. **Nunca aplique filtro de cor nem color grade** (deixava o vídeo avermelhado). Nunca altere o vídeo original; cada versão numa pasta nova.
8. Imagem real em vídeo = domínio público da Wikimedia Commons (`https://commons.wikimedia.org/wiki/Special:FilePath/<arquivo>?width=1200`).

## Gatoteca Entrelinhas (identidade visual)

Leia `gatoteca/IDENTIDADE_VISUAL.md` (paleta, fontes, mascote, o que foi aprovado e reprovado).

- Motor: `gatoteca/motor/`. Rode os scripts de dentro dessa pasta (`python divulga_post.py`). `montar.py` carrega as fontes e texturas e exporta o PNG.
- Mascote: `gatoteca/motor/mascote/gato_banco.py` (poses 01-26) e `gato_banco2.py` (27-56); figuras de post 57-61 vêm de `post_lilith5.py`. ⛔ Rode `gato_banco.py` SEMPRE com os códigos das poses (`python gato_banco.py 04 11`): sem códigos ele reescreve o `banco.json` só com 01-26.
- Planos do clube: `gatoteca/planos/`.

## Edição de vídeo Iara

- Método: `edicao-iara/GUIA_EDICAO_IARA.md`. Modelo pronto: `edicao-iara/exemplo-projeto/`.
- Editor: cooked em `~/editor-por-referencia` (instalado pelo `instalar.ps1`), com a biblioteca apontada para `edicao-iara/`. As skills do editor ficam em `~/editor-por-referencia/plugins/ai-editor/skills/` (`start`, `cut`, `style-edit`); leia o `SKILL.md` de cada uma ao usá-la.
- Estilo: `edicao-iara/creator-teardowns/iara/style.json` + `style.overrides.json` (sem bloco `grade`).
- Sons: `sons/virais/` (pelo `edicao-iara/custom/scripts/sons_v3.py`), teclas e brilho em `edicao-iara/custom/sounds/`.
- Em resumo: corte híbrido com sobreposição (`sobrepor_video.py`); legenda queimada Quicksand 500 a 3,6%, branca, palavra da vez rosa #FFD1DC, sem faixa preta, com `?` e `!`; destaques de texto animado nas 3 frases-chave (`texto_animado.py`), sem título de abertura; várias imagens ao mesmo tempo quando a fala enumera, entre 46% e 77% da altura; um efeito sonoro a cada 3-4 s, abaixo da voz; brilho viral no "oi, eu sou Iara" (`brilho.py`); zooms desenhados à mão, com zoom out, nunca o automático; sem música por padrão; **sem filtro de cor**.
- No Windows, rode Python com `PYTHONUTF8=1` (acentos) e transcreva em português (`--lang pt`).
- O blooper (trecho em preto e branco) está arquivado: só se a pessoa pedir, e com a voz normal.
