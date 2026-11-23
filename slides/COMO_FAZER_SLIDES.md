# Como fazer slides de aula

Este é o jeito de fazer os slides das aulas de língua (por exemplo, português para alunos chilenos). Serve para a inteligência artificial e para você entender o que ela está fazendo.

A ideia em uma frase: **cada slide é uma pequena página da internet** (um arquivo `.html`), e um programa tira a foto de todos e monta o PDF, o PowerPoint e uma folha de prévia.

Aula de exemplo, completa: `slides/exemplo-planos-concretos/` (abra o `aula.pdf` para ver como fica).

---

## 1. Antes de tudo: o conteúdo

- **Pesquise na internet antes de escrever**, em mais de uma fonte: a regra de gramática, os exemplos, as diferenças com o espanhol, as curiosidades. Nada inventado: nenhuma estatística, citação ou "regra" sem fonte.
- Escreva para o aluno: frases curtas, português simples, comparando com o espanhol (e com o espanhol do Chile) quando ajuda.
- Português correto, com todos os acentos. Aspas sempre curvas: “assim”. Nunca « » nem "retas" no slide.

## 2. A estrutura da aula (uns 15 a 20 slides)

1. **Capa**: rótulo pequeno ("Português · aula de conversação"), o título grande, uma frase do que a aula ensina, um gato grande.
2. **Tópicos**: o roteiro da aula em 4 a 6 cartões numerados.
3. **O que é / para que serve**: a ideia central, com um exemplo de verdade.
4. **Contraste**: o certo × o parecido (ex.: plano decidido × só uma ideia).
5. **A forma**: a regra numa tabela curta (quem · forma · em espanhol).
6. **Dicas para hispanofalantes**: os erros que eles costumam fazer, com ✗ e ✓.
7. **Marcadores** (de tempo, de lugar…): de preferência numa linha do tempo desenhada.
8. **Vocabulário**: tabela com uns 10 itens (palavra · uso · em espanhol · exemplo), em 1 ou 2 slides.
9. **Pronúncia**: escrita × fala, primeiro devagar, depois rápido; sílabas fortes marcadas.
10. **Charges com os gatos**: três situações curtas com balões de fala.
11. **Frases úteis** para a conversa (perguntar, aceitar, recusar…).
12. **Diálogo modelo**: dois personagens, em balões, em 1 ou 2 slides.
13. **Três atividades individuais**: completar / achar o erro; praticar a pronúncia; uma tarefa final de verdade (o aluno produz e apresenta).

**Notas do professor**: todo slide tem um `<aside>` com o que o professor faz ou fala naquele slide. Nas atividades, o **gabarito** (ou uma resposta possível) vai no `<aside>`, nunca no slide. As notas não aparecem no slide; vão para as notas do PowerPoint.

## 3. O visual

- **Paleta** (já está no `motor/base.css`): fundos areia `#E6D6B4`, creme `#F4ECDD`, papel `#FBF6EC`; escuro `#1E3328`; verde `#3E6A47`; azul `#2E4C7A`; terracota `#C8431F` (o destaque); laranja `#DE7A3C`; cinza `#4A5A50`.
- **Fontes** (já embutidas em `motor/fontes/`): **Fraunces** nos títulos, **Literata** no texto, **Barlow** nos rótulos pequenos em maiúsculas.
- **Tamanhos** (o slide tem 1920 × 1080): título da capa 112, título do slide 72, destaque 44, texto 32 a 34, nota 28, rótulo 26. Nada menor que 24.
- **Rodapé** "Tema · n / total" em todos os slides menos a capa: basta pôr `<p class="rodape"></p>`; o programa escreve sozinho.
- **Um elemento forte por slide** (uma tabela, ou uma linha do tempo, ou uma charge). Muito espaço livre.
- **Variar o layout** de um slide para o outro: fundo areia, creme, papel e, de vez em quando, um escuro; grade de cartões, tabela, balões, linha do tempo.
- O conteúdo termina até a altura 930; embaixo disso fica só o rodapé. O programa avisa se algo passar.

## 4. A arte

- Use os **gatinhos da Gatoteca**: `gatoteca/artes/Mascote - banco de poses/png (fundo transparente)/` (abra `Banco de poses do gato.html` para ver todas as poses e escolher a que combina com a cena) e `gatoteca/artes/Elementos recortados/`.
- Ou **SVG novo desenhado no código, bem bonito** (mala, calendário, linha do tempo, ícones…). Os que já existem estão em `slides/motor/figuras/`: mala, calendário, alfinete (mapa), amigos, prancheta, certo, errado, estrela.
- **Nunca** imagem gerada por IA nem foto de banco de imagens.
- Figura nova que pode voltar em outra aula vai para `slides/motor/figuras/` (ou, se for pose de gato, para o banco da Gatoteca).
- Os caminhos das imagens são sempre **relativos** (começam com `../`), para a pasta funcionar em qualquer computador:
  - gato: `../../../gatoteca/artes/Mascote - banco de poses/png (fundo transparente)/07_de_lado_andando.png`
  - figura: `../../motor/figuras/mala.svg`
- Nada de figura em cima de texto. Gato com cartaz (pose 14) pode receber uma palavra escrita por cima, no lugar do cartaz (ver `dialogo-2.html`).

## 5. Como é um slide por dentro

```html
<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><link rel="stylesheet" href="../../motor/base.css"></head>
<body>
<section class="slide creme" id="forma">
  <p class="rotulo">A forma</p>
  <h2><span class="ir">IR</span> no presente + verbo no infinitivo</h2>
  ... cartões, tabela, balões ...
  <img class="fig" src="../../../gatoteca/artes/Mascote - banco de poses/png (fundo transparente)/27_de_oculos.png" style="right:160px;top:420px;width:300px">
  <p class="rodape"></p>
  <aside>O que o professor faz neste slide. Gabarito, se for atividade.</aside>
</section>
</body></html>
```

Classes prontas do `base.css` (para os slides ficarem curtos):

- fundo do slide: `areia`, `creme`, `claro`, `escuro`; `centro` centraliza na vertical;
- texto: `h1`, `h2`, `h3`, `destaque`, `t32`, `t30`, `nota`, `rotulo`; cores `terra`; `ir` (o verbo em destaque), `es` (o espanhol, em itálico azul), `errado` (riscado), `certo`;
- caixas: `cartao` (com `borda` e `num`), `faixa` (frase importante com barra terracota);
- arrumação: `grade-2`, `grade-3`, `grade-4`, `linha`, `coluna`, `cresce`;
- `table.tabela`; balões `balao` (`dir`, `sem-ponta`, `azul-claro`, `verde-claro`, com `<span class="quem">` para o nome); `pilulas` / `pilula` (`cheia`, `terra`);
- figuras soltas: `fig` (posição com `left/right/top/bottom` e `width`), `elipse` (círculo de fundo).

## 6. Como gerar

Cada aula é uma pasta em `slides/`:

```
slides/minha-aula/
  deck.json          {"titulo": "Título da aula", "rodape": "Tema curto", "ordem": ["capa", "topicos", ...]}
  slides/capa.html   um arquivo por slide, com o nome que está na "ordem"
```

Para começar uma aula nova, **copie a pasta `exemplo-planos-concretos`**, apague os `aula.*` e a `previa.png`, e troque o conteúdo.

Na pasta do repositório, rode:

```
python slides/motor/fazer_slides.py slides/minha-aula
```

Sai na pasta da aula:

- `aula.pdf`: uma página por slide (dá para imprimir e projetar);
- `aula.pptx`: para abrir no PowerPoint ou no Google Slides, com as notas do professor;
- `previa.png`: todas as miniaturas numa folha só.

Atalhos para conferir enquanto faz:

- `--rapido`: só a prévia (mais rápido);
- `--ver capa,dialogo-2`: só esses slides, em tamanho cheio (para olhar de perto).

O programa avisa quando uma imagem não carrega, quando algo passa da área útil ou sai pela lateral, e quando um slide está sem notas do professor.

Precisa do Python com `playwright` (e o Chromium: `python -m playwright install chromium`), `pillow`, `python-pptx` e `pypdf` (todos no `requirements.txt`).

## 7. Antes de entregar

1. O programa terminou com "Tudo certo." (sem avisos).
2. **Olhe a `previa.png`** e, de perto, os slides com figura ou muito texto: nada cortado, nada em cima de outra coisa, nada pequeno demais, nenhum slide vazio demais ou cheio demais.
3. Confira os acentos, as aspas “ ” e os gabaritos nas notas.
4. Mostre a prévia à professora antes de dar por pronto.
