# Gatoteca Entrelinhas + Edição de vídeo Iara

Tudo o que é preciso para reproduzir, em outro computador, duas coisas:

1. **A identidade visual da Gatoteca Entrelinhas** (o clube de leitura): o mascote frajola, o banco de poses, as "cartinhas", o papel texturizado, os elementos recortados, as artes já feitas, o motor em Python que gera tudo e os planos do clube.
2. **A edição de vídeo Iara**: Reels 9:16 de cabeça falante com legenda queimada delicada, várias imagens animadas, destaques de texto animado, zooms desenhados, brilho viral na apresentação e efeitos sonoros virais. É o método da versão final do vídeo do Frankenstein.

O repositório já traz as instruções para o agente de IA (Antigravity, Claude Code, Gemini CLI, Codex) em `AGENTS.md`, com cópias em `GEMINI.md` e `CLAUDE.md`. O instalador também grava essas instruções na memória global do agente.

## Começo rápido (para quem não é da área)

Você não precisa entender de programação. O jeito mais fácil:

1. Abra o **Antigravity**.
2. Cole esta mensagem para o agente e envie:
   > Instale para mim o repositório https://github.com/gabriel20angelo-web/gatoteca-e-edicao-iara seguindo o README dele. Instale o que faltar no computador, rode o instalar.ps1 e me avise, em palavras simples, quando terminar.
3. Ele vai pedir permissão algumas vezes para rodar comandos: pode aceitar. A instalação do editor de vídeo demora (pode levar mais de meia hora).
4. Quando ele disser que terminou, **feche e abra o Antigravity de novo**. A partir daí ele já sabe as regras (estão gravadas na memória dele).
5. Depois é só pedir em português, por exemplo:
   - "Faz um post de divulgação da Gatoteca com o gatinho lendo."
   - "Edita este vídeo no estilo Iara: C:\Users\...\meu-video.mp4"

**O que o agente vai fazer sempre, sem você pedir:**
- falar com você de um jeito simples e fazer o trabalho técnico sozinho;
- pesquisar na internet, em várias fontes, antes de responder, e mostrar os links;
- procurar no GitHub e em outros repositórios se já existe uma ferramenta pronta antes de criar uma nova;
- perguntar antes de apagar, publicar ou gastar dinheiro, e nunca mexer nos seus vídeos originais.

**Para atualizar** quando houver novidade, peça ao agente: "Atualize o repositório gatoteca-e-edicao-iara (git pull) e rode o instalar.ps1 de novo."

## Instalar (Windows), passo a passo técnico

1. Instale o **Git**, o **Python 3.12+**, o **Node 20+** e o **ffmpeg**, se ainda não tiver:
   ```powershell
   winget install -e --id Git.Git
   winget install -e --id Python.Python.3.12
   winget install -e --id OpenJS.NodeJS.LTS
   winget install -e --id Gyan.FFmpeg
   ```
   Feche e abra o terminal depois.
2. Baixe este repositório:
   ```powershell
   git clone https://github.com/gabriel20angelo-web/gatoteca-e-edicao-iara.git
   cd gatoteca-e-edicao-iara
   ```
3. Rode o instalador:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\instalar.ps1
   ```
   Ele faz, nesta ordem:
   - instala as bibliotecas Python (`requirements.txt`) e o Chromium do Playwright, que transforma o SVG/HTML em PNG;
   - baixa o editor de vídeo **cooked** (MIT) em `~\editor-por-referencia`, na versão em que os ajustes foram feitos, e aplica os 9 ajustes de `edicao-iara/editor-patch/`;
   - roda o `setup.py bootstrap` do editor (Whisper, Remotion etc.; demora);
   - aponta a biblioteca do editor para `edicao-iara/` deste repositório;
   - copia as skills de `skills/` para o Antigravity (`~\.gemini\antigravity\skills`) e para o Claude Code (`~\.claude\skills`);
   - acrescenta as regras de `AGENTS.md` à memória global do Antigravity/Gemini (`~\.gemini\GEMINI.md`) e do Claude Code (`~\.claude\CLAUDE.md`).

   Para pular o editor de vídeo (só a identidade visual): `.\instalar.ps1 -SemEditor`.

## Usar

Abra o agente **dentro da pasta do repositório** e peça em português:

- *"Faz um post de divulgação da Gatoteca com o frajola lendo"* → o agente segue `gatoteca/IDENTIDADE_VISUAL.md` e usa o motor (`gatoteca/motor/`).
- *"Edita meu vídeo no estilo Iara: <caminho do vídeo>"* → o agente segue `edicao-iara/GUIA_EDICAO_IARA.md` e a skill `edit-like-iara`.

## O que tem em cada pasta

| Pasta | O que é |
|---|---|
| `AGENTS.md` (`GEMINI.md`, `CLAUDE.md`) | A memória/instruções do agente: regras fixas, onde está cada coisa |
| `gatoteca/IDENTIDADE_VISUAL.md` | Paleta, fontes, mascote, o gosto aprovado e o que foi reprovado |
| `gatoteca/motor/` | Motor em Python: `papel.py` (textura de papel), `cartinhas.py` e `envelope.py` (componentes), `mascote/gato_banco.py` e `gato_banco2.py` (o frajola em 56 poses), `elementos/` (recorte e catálogo), `divulga_post.py`, `divulga_perfil.py`, `post_lilith5.py` etc. |
| `gatoteca/artes/` | As artes prontas: banco de poses do mascote (SVG + PNG), elementos recortados, identidade "cartinhas", posts, fotos de perfil, Reels |
| `gatoteca/planos/` | O plano de ação da Gatoteca e do perfil Iara Entre Linhas (duas versões) |
| `edicao-iara/GUIA_EDICAO_IARA.md` | **O método da edição**, passo a passo |
| `edicao-iara/custom/` | Scripts próprios (`sobrepor_video.py`, `sons_v3.py`, `texto_animado.py`, `brilho.py`…), presets de legenda, fontes, teclas e brilho |
| `edicao-iara/creator-teardowns/iara/` | O estilo da Iara para o editor (sem filtro de cor) |
| `edicao-iara/exemplo-projeto/` | Os arquivos de controle do vídeo final do Frankenstein (deixas de som, zooms, destaques, imagens), para servir de modelo |
| `edicao-iara/editor-patch/` | Os 9 ajustes feitos no editor cooked |
| `sons/virais/` | Efeitos virais de Reels (vine boom, yippee, whoosh, chicote, obturador, página, ding, record scratch, romance meme…) |
| `sons/kenney/` | Pacotes de efeitos CC0 da Kenney (interface, impacto, digital…) |
| `sons/iara/` | Teclas e brilho usados na edição |
| `skills/` | Skills para o agente (`gatoteca-arte`, `edit-like-iara`) |

## Licenças

- Código deste repositório: livre para usar e adaptar.
- Editor cooked: MIT, de nextwork-projects (baixado pelo instalador; os patches são modificações dele).
- Sons Kenney: CC0 (ver `License.txt` em cada pacote). Teclas: CC0 (`edicao-iara/custom/sounds/FONTE_TECLADO.txt`). Sons virais: vêm da biblioteca `@remotion/sfx`; são memes da internet, use com bom senso em conteúdo comercial.
- Fontes: Google Fonts (OFL).
- Imagens nos vídeos: só domínio público da Wikimedia Commons.
