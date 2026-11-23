---
name: gatoteca-arte
description: Faz arte da Gatoteca Entrelinhas (clube de leitura) na identidade visual dela - post, divulgação, foto de perfil, convite, pose nova do mascote frajola. Use quando pedirem arte, post, card, convite ou figura da Gatoteca / Clube Entrelinhas / do gatinho frajola.
---

# Arte da Gatoteca Entrelinhas

O repositório `gatoteca-e-edicao-iara` tem tudo. Ache a pasta dele (onde está o `AGENTS.md`) e:

1. Leia `AGENTS.md` e `gatoteca/IDENTIDADE_VISUAL.md`.
2. Escreva os textos da peça num `.txt` (divulgação: no máximo 4-5 linhas curtas) e confirme com a pessoa.
3. Procure no banco antes de desenhar: `gatoteca/artes/Mascote - banco de poses/` (página HTML com a nota de cada pose) e `gatoteca/artes/Elementos recortados/`.
4. Monte a peça como **SVG desenhado no código**, partindo do script mais próximo em `gatoteca/motor/` (`divulga_post.py`, `divulga_perfil.py`, `post_lilith5.py`, `envelope.py`, `cartinhas.py`). Fundo em papel texturizado (`papel.py`), um elemento no centro, paleta e fontes da identidade.
5. Exporte o PNG pelo `montar.py` (Playwright/Chromium), olhe o resultado e entregue o SVG e o PNG.
6. Figura nova que pode voltar: salve no banco (`gatoteca/motor/mascote/exportar_banco.py`).
