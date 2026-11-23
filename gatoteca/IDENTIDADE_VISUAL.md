# Identidade visual da Gatoteca Entrelinhas

Clube de leitura no Recife, gratuito, a cada quinze dias. Nome em uso: **Gatoteca Entrelinhas** (também "Clube de Literatura Entrelinhas"; nunca "clube de psicologia").

## Regra de ouro

Toda arte é **SVG desenhado no código** (ver `AGENTS.md`). O motor em `motor/` monta o SVG/HTML e exporta o PNG. Reusar o banco antes de desenhar de novo.

## Paleta

| Nome | Cor | Uso |
|---|---|---|
| Jade | `#5F857C` | cor principal, bordas, fitas |
| Rosa | `#C799AA` | títulos, detalhes, carinho |
| Noite | `#30323C` | fundos escuros, texto |
| Ameixa | `#624956` | contorno de título, sombras |
| Pérola | `#F1E3E6` | papel claro, lua |
| Ouro | `#D9B36A` | óculos, aros, estrelas, frisos |
| Vinho-lacre | `#6E1F2E` | lacre, um por peça |

## Fontes (em `motor/fontes/`)

- **DM Serif Display**: título ("Entrelinhas").
- **Cinzel**: rótulos ("CLUBE DE LITERATURA").
- **Cormorant Garamond**: texto corrido.
- **Caveat**: escrito à mão (só enfeite, nunca dado importante).
- **Special Elite**: etiqueta datilografada.
- **Italiana**: nome de tema em destaque (ex.: "Lilith").

## O mascote: o frajola de "pelúcia de traços"

Gato frajola preto e branco, de barriguinha, olhos verdes com brilho. O pelo é feito de riscos curtos seguindo o caimento, com tufos na silhueta no lugar do contorno.
- **Banco de poses**: `artes/Mascote - banco de poses/` (SVG, PNG transparente, folha e página HTML com a nota de uso de cada pose). Grupos: descanso, movimento, segurando, escondido, humores, acessórios (óculos dourados, chapéu de bruxa, boina, coroa…), objetos (livros, xícara, bola de cristal, tarô, lupa…), com amigos, pensando/brincando, e as figuras de post (57 Lilith de vestido, 58 carta em arco, 59 rosto de Bastet, 60 corujinha de ouro, 61 asas de coruja).
- **Duas caras**: a fofa (bochecha, olhos redondos) e a **"menos fofa" / rosto de Bastet** (cabeça menor, olhos amendoados meio fechados, pupila em fenda, delineado egípcio), que funciona como figura-ícone séria.
- Pose nova = função `@pose` no fim de `motor/mascote/gato_banco2.py`, depois `python gato_banco2.py <código>` e `python exportar_banco.py`.

## A linguagem das peças

- **Cartinhas** (`motor/cartinhas.py`, guia em `artes/Identidade - cartinhas/`): cartão-postal com moldura dupla de cantos recortados, medalhão de pérolas, céu de estrelas, forro arlequim rosa/jade, olho de gato verde.
- **Envelope** (`motor/envelope.py`): o post é a frente de um envelope de papel com borda de correio aéreo, remetente "CLUBE DE LITERATURA / Entrelinhas", selo com o mascote, carimbo, fita, clipe, etiqueta datilografada, lacre e tira rasgada com a chamada. Cada edição nova muda a cor da borda e a carta-herói.
- **Arco de tarô** (`motor/post_lilith5.py`): carta em arco + o frajola "menos fofo" como figura-ícone + coluna de texto limpa. ⭐ Foi a mais elogiada.
- **Divulgação** (`motor/divulga_post.py`, `motor/divulga_perfil.py`): "A roda dos gatos" (5 gatos-leitores em roda sobre um livro gigante, almofada vazia e "Tem lugar pra você. Vem!") e a foto de perfil "Entre 🐈 linhas" (livro aberto, o frajola na dobra, "GATOTECA" em arco), em jade ou rosa.
- **Elementos recortados** (`artes/Elementos recortados/`, catálogo HTML): 97 peças em 9 categorias (rendas, selos, lacres, estrelas, flores…). São pequenas: enfeite de até 1/4 do post; um lacre por peça; gato vintage nunca junto do mascote.

## O gosto (aprovado × reprovado)

- ⭐ Elementos um por cima do outro (colagem de papéis, fita, selo, lacre), cor, e o mascote/gatinhos.
- ⭐ O frajola gigante "menos fofo" no arco de tarô.
- ⛔ Fundo chapado: tudo em papel texturizado (`papel.py`: manchas, fibras e dente em relevo leve; relevo forte vira reboco).
- ⛔ Centro poluído: um elemento no centro.
- ⛔ Detalhe fino em fundo escuro: não lê. Informação em letra limpa e grande.
- ⛔ Texto miúdo que só se lê com zoom em peça de divulgação: "péssima ideia".
- ⛔ Busto de gato com cabeça enorme e traços humanos: "esquisito, feio".
- ⛔ Reciclar a fórmula de uma arte em outra de tema diferente ("usou a ideia da Lilith"): cada arte nova pede ideia nova.

## Armadilhas técnicas do SVG (já custaram tempo)

- Lua crescente com dois arcos: o arco de volta precisa de raio MAIOR e flags `0 0 1`, senão a área colapsa. Caminho que funciona: `M-14,-6 A14,14 0 1 0 6,-16 A11,11 0 1 1 -14,-6Z`.
- Linha reta com filtro em `objectBoundingBox` some: use `userSpaceOnUse`.
- Pálpebra preta sobre pelo preto não aparece: use sobrancelha clara.
- Rabo preto some sobre vinho: luz de borda `#8C6578`.
- Patas giradas ±70° viram pompom: deitadas a ±90°.
- `cabeca=dict()` vazio é falso em Python: teste `is not None`. `sentado(p)` sem `cabeca` não desenha a cabeça: passe `cabeca=dict(acess=[])`.
- Foto de perfil do WhatsApp: a figura tem de caber no círculo (510 px do centro numa arte de 1080); `perfil_whatsapp.conferir_circulo()` mede.
