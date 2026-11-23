# Guia de edição: Iara (atualizado em 22/11/2026, depois da v4 do vídeo Frankenstein)

Este guia substitui o de 20/11. O que caiu está no fim, para ninguém repetir. Os arquivos de controle do último vídeo (Frankenstein, versão final) estão em `exemplo-projeto/` deste repositório; o vídeo em si não vai junto.

Neste repositório, a pasta `edicao-iara/` é a **biblioteca** do editor (onde ficam `custom/`, `creator-teardowns/` e `edits/`) e `$S` é a pasta de scripts do style-edit (`<editor>/plugins/ai-editor/skills/style-edit/scripts`). Os sons virais ficam em `sons/virais/`, na raiz do repositório.

## O que o vídeo é

Cabeça falante em 9:16 (1080x1920). O rosto da Iara fica quase sempre na metade de cima (0 a ~45% da altura), então tudo o que entra na tela vai na faixa do meio para baixo. É um Reel dinâmico, mais perto do viral que da influencer medida: legenda queimada o tempo todo, várias imagens ao mesmo tempo quando a fala enumera, e efeito sonoro com frequência. A delicadeza fica na letra, não no ritmo.

## Cor: sem filtro

O vídeo sai com a cor da gravação. **Nada de color grade nem filtro de cor**: o grade automático do editor (que copiava o brilho e a saturação medidos na influencer) deixava a pele avermelhada e ficou ruim. Por isso o `style.json` da Iara não tem o bloco `grade`; não o recoloque. Se o `plan.json` sair com um bloco `"grade"`, apague-o antes do render.

## Corte

O corte é seco, por jump cut, e as emendas entre frases usam a **sobreposição híbrida** (`custom/scripts/sobrepor_video.py <fonte> <edit_dir>`; o `--so-classificar` mostra as classes antes de montar):
- **Sobreposição**: a frase seguinte entra por cima da cauda da anterior, as duas vozes cheias. O alvo é 400 ms, com teto de 45% da última palavra. Quando sobra uma pausa longa depois da última palavra, a pausa some e a voz nova entra sobre a palavra até o teto.
- **Corte normal (limpo, 110 ms)**:
  - frase curta enfática (C1);
  - número ou termo-chave no fim (C2);
  - **a próxima frase é uma pergunta (C3)**: corte normal para *chegar* na pergunta e, logo **depois** dela, sobreposição para a fala seguinte. Regra dele em 22/11, no "Faz sentido?". Pergunta é dúvida, precisa chegar limpa; depois dela o ritmo segue;
  - pausa longa no cru, acima de 2,5 s (C4);
  - fecho de citação (C5).
- **Respiro**: depois da primeira frase (o gancho), antes do "Aliás, oi" (a virada para a apresentação) e no fim.
- **Imagem com L-cut**: o quadro troca quando a voz nova começa.

Conferir o corte em português (`transcribe.py cut.mp4 --lang pt`); o `verify_cut.py` transcreve em inglês.

## Legenda (queimada, sempre)

Preset `custom/captions/iara-delicada-fina.json`:
- **Quicksand peso 500**, tamanho **3,6%**;
- branca, sombra suave;
- palavra da vez em rosa claro #FFD1DC, 3 palavras por vez, entrada pop leve (1,05).

Duas regras saíram de reprovação:
- **Sem faixa preta.** O editor põe sozinho um "tratamento de contraste" (`treat: band`), que é uma faixa escura atrás da legenda. A preset desliga isso com `"treat": false`.
- **Fina e pequena.** Quicksand 700 a 4,8% foi reprovada: "muito grossa, pouco delicada, muito grande".

A legenda fica em y ~81% (limite do plan.py). Texto em português, corrigido à mão onde o Whisper erra (ex.: "Frank Frankenstein", "é" que some); o script fica em `exemplo-projeto/fix_captions.py`.

**Pontuação:** a legenda mantém `?` e `!` (`"punct": "?!"` na preset). Sem eles a pergunta não lê como pergunta. Vírgula e ponto ficam de fora.

## Destaques de texto animado (no lugar do título)

Não há título de abertura: a Dancing Script no início ficou feia e o `texts.json` fica `{"items": []}`. A ênfase vem dos **destaques**. Nas frases-chave, a legenda some e entra a frase grande, animada palavra por palavra no tempo da fala, depois a legenda volta. Exemplos:
- o gancho mostra só **"pedaços"**, com as letras voando de pedaços espalhados e se montando;
- **"E o que, afinal, / faz de alguém / um monstro?"**;
- **"O que é / tão difícil / reconhecer / a monstruosidade / em nós mesmos"**, seguido de **"e tão fácil / reconhecer isso / no outro?"**.

**Escolha das frases:** o gancho, as perguntas centrais e a frase-tese. São 3 por vídeo de ~1 min.

**Tipografia:** Quicksand 600 nas palavras de ligação; **Playfair Display itálico** grande nas palavras-chave, em branco ou rosa #FFC4D6.

**Animação:**
- cada palavra sobe com uma molinha;
- a última palavra da pergunta entra com soco e tremida, junto com o vine boom;
- a página sai subindo e esmaecendo;
- uma frase longa vira 2 páginas.

**Posição:** de 49% a ~80% da altura. A legenda está escondida nessa hora; imagem não entra junto (o Goya saiu por isso).

**Como fazer:** `custom/scripts/texto_animado.py` com o `destaques.json` (as linhas, com o tempo de cada palavra tirado da captions.json):
- `plano` depois do sons_v3 (tira a legenda das janelas);
- `quadros`;
- `aplicar` depois do render, junto com o brilho (`--extra <pasta>:<t>`).

## Imagens

Imagem é real e livre: domínio público da Wikimedia (pinturas, gravuras, retratos, folhas de rosto). Baixar por `Special:FilePath/<arquivo>?width=1200`. Nada de banco de imagem.
- **Mais de uma por vez onde a fala junta coisas**, cada uma em sua faixa (`lane: multi1`, `multi2`…, com `box` próprio no images.json):
  - enumeração de 3 entra em cascata, uma imagem por item (Renoir, Monet, Klimt);
  - obra mais autora entram lado a lado (gravura mais retrato).
- **Faixa**: de ~46% a no máximo **77%** da altura. Assim nunca encostam na legenda (81%) nem no rosto (a cabeça desce a 46% quando há zoom; o check.py acusa).
- Entradas animadas variadas; saída com esmaecer.

## Efeitos sonoros: bastante e misturado

Cerca de 1 a cada 3 a 4 s (18 num vídeo de 53 s), sempre abaixo da voz:
- memes ficam de 8 a 10 dB abaixo;
- whoosh, obturador e página, 12 a 13 dB abaixo;
- nunca dois a menos de 0,3 s um do outro.

O script é `custom/scripts/sons_v3.py <edit> [mapa.json]`. Ele nivela cada som contra a fala e roda **depois** do plan.py. O mapa desloca os tempos quando o corte muda. A biblioteca é `sons/virais/`, na raiz deste repositório.

| Momento | Som |
|---|---|
| Título | ding |
| Imagem entrando | whoosh e chicote, alternados |
| Retrato | obturador |
| Livro | virar de página |
| Pergunta dramática | vine boom, com soco de zoom |
| Quando ela se interrompe ("Aliás, oi") | record scratch |
| Momento fofo ("eu sou Iara") | romance meme |
| Convite | yippee e notificação |
| Textos | tecla |

## Brilho viral na apresentação ("oi, eu sou Iara")

Quando ela se apresenta entram estrelinhas de 4 pontas cintilando em volta da cabeça (nunca em cima do rosto), com halo rosado e dourado e um clarão suave, junto com o **som de brilhinhos**, 8 dB abaixo da voz. Os dois são feitos pelo `custom/scripts/brilho.py`:
- `som custom/sounds/brilho.wav`: o som;
- `quadros <pasta> --cx 45 --cy 25`: as estrelinhas, com o centro no rosto;
- `aplicar <render.mp4> <pasta> <t> <saida.mp4>`: depois do render, porque o editor não tem esse efeito.

Duas armadilhas:
- O halo se desenha sobre fundo transparente CLARO. Sobre fundo preto, o borrão faz manchas cinzas.
- O som entra pela deixa `brilho` do `sons_v3.py`, que procura o arquivo em `custom/sounds/`.

## Zooms: dinâmicos, desenhados à mão (nunca o automático)

O zoom automático fica desligado (`zoom.per_min = 0`): o longo empurrava o rosto e derrubava imagens. No lugar dele vai um desenho por fala, em `zooms_final.json`, passado com `sons_v3.py --zooms`. Uns 14 num vídeo de 53 s, todos com origem no rosto [50,20]:
- **zoom out** (`kind: "out"`, tipo novo no editor): começa aproximado (1,14 a 1,20) e abre devagar. Vai na abertura do gancho, antes de uma pergunta dramática, na virada "mas do que fizeram de nós" e no "oi, eu sou Iara", junto com o brilho;
- **soco rápido** (punch com `travel_s` de ~0,1 s): nas viradas curtas ("Mas, talvez", "pensa comigo", "Aliás" com o record scratch, "monstro?" com o vine boom);
- **empurrão lento** (punch com `travel_s` longo e `ease: "sine.inOut"`, ou push): sobe até a pergunta e solta seco na emenda seguinte ("…realmente somos?", "…no outro?").

Zoom só onde não há imagem na tela (o check.py acusa cabeça sobre cartão), e o push termina antes de a imagem entrar. O check avisa "zoom-every-line" como tique de IA: aqui é escolha dele, pode ignorar.

## Passo a passo (pasta nova por versão; nunca mexer nas anteriores)

1. Copiar a pasta da versão anterior sem render nem stills.
2. Se o corte mudar:
   - rodar `sobrepor_video.py`;
   - levar a legenda corrigida para os tempos novos (`exemplo-projeto/remap_captions.py`);
   - rodar `face.py`.
3. `PYTHONUTF8=1 py $S/plan.py <edit>/style.json <edit>/captions.json --aspect 9:16`.
4. `py custom/scripts/sons_v3.py <edit> --cues cues_final.json --zooms zooms_final.json`. As deixas e os zooms ficam no tempo do corte atual. O mapa só entra quando o corte mudou e se reaproveita a tabela antiga.
5. `check.py plan`, com 0 FAIL.
6. `edit.py stills`: olhar a folha (rosto livre, legenda sem tocar imagem).
7. `texto_animado.py plano` e `quadros` (antes dos stills).
8. `edit.py render`.
9. `texto_animado.py aplicar <edit> destaques.json render.mp4 final.mp4 --extra _olho/brilho_quadros:<t do "oi">`.
10. Conferir quadros e entregar.

O modelo completo é a pasta `exemplo-projeto/`, com `cues_final.json`, `zooms_final.json`, `destaques.json` e `images.json`.

Editor: o cooked (github.com/nextwork-projects/ai-video-editor-cooked) com os 9 patches de `editor-patch/` aplicados (o `instalar.ps1` faz isso): imagens simultâneas `multi*`, sombra no título, `treat` na preset de legenda, zoom `out`, pontuação `?!` na legenda e tecla em toda entrada.

## O que caiu (não repetir)

- Cormorant Garamond em caixa creme ("tá feio").
- Vídeo sem legenda.
- Uma imagem por vez no topo.
- Só tecla de efeito.
- Quicksand 700 grande com faixa escura.
- Blooper com voz distorcida (arquivado; só com escolha dele, voz normal).
- Corte limpo DEPOIS de pergunta: agora o limpo vem ANTES dela.
- Filtro de cor / color grade (saturação 1,56 e brilho 0,72): deixou o vídeo avermelhado.

**Nunca:** filtro de cor, música por padrão, nem alterar o arquivo fonte.
