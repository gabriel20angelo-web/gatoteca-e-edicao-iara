---
name: slides-aula
description: Faz os slides de uma aula de língua (por exemplo, português para alunos chilenos) com os gatinhos da Gatoteca, e entrega PDF, PowerPoint com as notas do professor e uma prévia. Use quando pedirem "faz slides", "slides da aula", "apresentação", "aula em slides" ou um deck sobre um tema de gramática ou conversa.
---

# Slides de aula

O repositório `gatoteca-e-edicao-iara` tem tudo. Ache a pasta dele (onde está o `AGENTS.md`) e:

1. Leia `slides/COMO_FAZER_SLIDES.md` inteiro (estrutura da aula, visual, arte, como gerar).
2. Combine com a pessoa o tema, o público e o nível, em poucas palavras.
3. **Pesquise o conteúdo na internet antes de escrever**, em mais de uma fonte (regra, exemplos, diferenças com o espanhol). Nada inventado.
4. Copie `slides/exemplo-planos-concretos/` para `slides/<nome-da-aula>/`, apague `aula.pdf`, `aula.pptx` e `previa.png`, e troque o conteúdo: `deck.json` (título, rodapé, ordem) e um `.html` por slide, com as notas do professor no `<aside>` (gabarito das atividades sempre no `<aside>`).
5. Arte: gatos do banco (`gatoteca/artes/Mascote - banco de poses/`, veja `Banco de poses do gato.html`), elementos em `gatoteca/artes/Elementos recortados/`, figuras em `slides/motor/figuras/`, ou SVG novo desenhado no código, bem bonito. Nunca imagem de IA nem de banco de imagens. Caminhos sempre relativos (`../`). Figura nova que pode voltar vai para `slides/motor/figuras/`.
6. Gere: `python slides/motor/fazer_slides.py slides/<nome-da-aula>` (use `--rapido` ou `--ver id1,id2` enquanto ajusta). Conserte todo aviso até sair "Tudo certo.".
7. **Olhe a `previa.png`** (e os slides com figura em tamanho cheio, com `--ver`) e corrija o que estiver cortado, sobreposto ou feio.
8. Mostre a prévia à pessoa e diga onde estão o `aula.pdf` e o `aula.pptx` (este abre no PowerPoint ou no Google Slides, com as notas do professor).
