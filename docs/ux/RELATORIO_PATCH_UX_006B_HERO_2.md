# Relatório — PATCH UX-006B Hero 2.0

Data: 21/07/2026
Branch: `agent/patch-ux-006b-hero-2`
Deploy: não realizado

## Causa observada

O Hero desktop media 594 px em 1440 px. O título estava limitado a `10.5ch`, resultando em seis linhas, enquanto a fotografia permanecia comprimida na mesma área.

## Alterações

- largura útil desktop ajustada para 78%;
- título estruturado em exatamente duas linhas;
- fotografia ampliada no desktop e restaurada em tablet/mobile;
- espaçamentos internos reduzidos;
- `Comprar agora` reforçado como CTA principal;
- `Anunciar grátis` mantido como CTA secundário;
- busca preservada imediatamente após o Hero.

## Matriz visual

| Viewport | Hero antes | Hero depois | Linhas antes | Linhas depois | Overflow |
| --- | ---: | ---: | ---: | ---: | --- |
| 1440 px | 594 px | 1.022 px | 6 | 2 | não |
| 768 px | 594 px | 692 px | 3 | 2 | não |
| 390 px | 343 px | 343 px | 2 | 2 | não |
| 320 px | 273 px | 273 px | 3 | 2 | não |

Em 390 px o Hero completo permanece dentro da primeira viewport. Em 320 px a busca inicia dentro da primeira viewport e continua imediatamente abaixo da fotografia, sem rolagem horizontal.

## Evidências

- `docs/ux/evidencias/patch_ux_006b/antes/`
- `docs/ux/evidencias/patch_ux_006b/depois/`
- `docs/ux/evidencias/patch_ux_006b/comparativo/`

Foram registradas capturas em 1440, 768, 390 e 320 px, além dos quatro comparativos Antes × Depois.

## Validação

- 149 testes aprovados;
- Ruff check aprovado;
- Ruff format check aprovado;
- `git diff --check` aprovado;
- console do navegador sem erros;
- ausência de overflow horizontal entre 320 e 1440 px;
- Home compacta, Cidade Viva, “Ver todos” e busca preservados;
- backend, banco e feature flag sem alterações.

## Reversão

Reversão por um único commit validada em worktree isolada. Após o `git revert`, a árvore restaurada ficou idêntica à `origin/master`.
