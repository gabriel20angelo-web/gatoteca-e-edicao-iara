---
name: edit-like-iara
description: Edita um vídeo de cabeça falante no estilo "edição de vídeo Iara" (Reel 9:16 com legenda queimada delicada, várias imagens animadas, destaques de texto animado, zooms desenhados, brilho viral e efeitos sonoros virais). Use quando pedirem "edita meu vídeo no estilo Iara", "edição Iara", "/edit-like-iara", "edit my video like @iara".
---

# Edição de vídeo Iara

Tudo está no repositório `gatoteca-e-edicao-iara` (ache a pasta onde está o `AGENTS.md`; abaixo, `<REPO>`).
O editor é o cooked em `~/editor-por-referencia` (o `instalar.ps1` instala e aplica os patches); a biblioteca dele é `<REPO>/edicao-iara`.

1. **Leia `<REPO>/edicao-iara/GUIA_EDICAO_IARA.md` inteiro antes de editar.** Ele é o método e vale acima de qualquer padrão do editor.
2. Rode a skill `start` do editor (`~/editor-por-referencia/plugins/ai-editor/skills/start/SKILL.md`) no vídeo. No passo "Blend the style", use o estilo da Iara em vez dos criadores do perfil (`$P` = `~/editor-por-referencia/plugins/ai-editor/lib/ai_editor/profile.py`):
   `python "$P" style edits/<nome> --from "<REPO>/edicao-iara/creator-teardowns/iara/style.json"`
3. Corte (skill `cut`) e espere a aprovação da pessoa; depois aplique a sobreposição híbrida (`custom/scripts/sobrepor_video.py`) e siga o passo a passo do guia: plan.py → `sons_v3.py` com deixas e zooms → `check.py plan` → stills → `texto_animado.py` → render → `texto_animado.py aplicar` com o brilho.
4. Use `<REPO>/edicao-iara/exemplo-projeto/` como modelo de `cues_final.json`, `zooms_final.json`, `destaques.json` e `images.json`.

Regras que não mudam:
- **Sem filtro de cor / color grade.** Se o `plan.json` sair com bloco `"grade"`, apague-o antes do render.
- Sem título de abertura; sem música por padrão; zoom automático desligado (`zoom.per_min = 0`).
- Legenda preset `iara-delicada-fina` (Quicksand 500, 3,6%, sem faixa, `?!`).
- Imagens só de domínio público (Wikimedia Commons), entre 46% e 77% da altura.
- Transcrever em português (`--lang pt`) e rodar Python com `PYTHONUTF8=1`.
- Nunca alterar o vídeo original; cada versão em pasta nova.
