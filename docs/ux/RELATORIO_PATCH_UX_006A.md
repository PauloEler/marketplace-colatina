# Relatório — PATCH UX-006A

## Status

Implementado em branch isolada. Sem merge e sem deploy.

## Entrega

- seção “🌇 Cidade Viva” imediatamente após Encontre Quem Resolve;
- sete acessos “Ver todos” quando todos os resumos estão disponíveis;
- categorias resumidas em cinco itens no desktop e quatro no mobile;
- três ofertas comerciais e três empresas parceiras no resumo;
- produtos, lojas, métricas e anúncios recentes compactados;
- composição integral preservada por `?todos=1`;
- comportamento isolado pela feature flag existente.

## Escopo técnico

Arquivos funcionais alterados:

- `templates/index.html`;
- `static/styles.css`;
- `tests/test_moderacao.py`.

`app.py`, banco, rotas e regras de negócio não foram alterados pelo patch.

## Evidências

Capturas antes/depois em 1440, 1024, 768, 390 e 320 px estão em `docs/ux/evidencias/patch_ux_006a/`.

## Resultados

| Referência | Antes do patch | Depois do patch | Redução | Telas depois | Overflow |
| --- | ---: | ---: | ---: | ---: | --- |
| 1440 × 900 | 7.232 px | 4.930 px | 31,8% | 5,48 | não |
| 1024 × 768 | 6.905 px | 4.427 px | 35,9% | 5,76 | não |
| 768 × 1024 | 7.193 px | 5.077 px | 29,4% | 4,96 | não |
| 390 × 844 | 5.694 px | 5.217 px | 8,4% | 6,18 | não |
| 320 × 720 | 6.274 px | 5.758 px | 8,2% | 8,00 | não |

No mobile, a Missão 006 já usava listas horizontais compactas; por isso o ganho adicional é menor. O patch preservou alvos de toque de 44 px e reduziu cards sem sacrificar leitura.

Validações visuais e funcionais:

- Cidade Viva começa entre Encontre Quem Resolve e Categorias no DOM e no visual;
- sete links “Ver todos” quando os sete resumos estão disponíveis;
- resumo com cinco categorias no desktop e quatro no mobile;
- três ofertas e três empresas parceiras no resumo;
- “Ver todos” restaurou dez categorias, seis ofertas, seis parceiros locais e Hoje em Colatina;
- um `h1`, nenhum `id` duplicado e console da aplicação sem erros;
- navegação por teclado alcança CTA principal, busca, Encontre Quem Resolve, métricas e “Ver todos”.
- suíte completa: 147 testes aprovados;
- `ruff check .`, `ruff format --check .` e `git diff --check`: aprovados;
- diff funcional confirmado somente em template, CSS e testes, sem alteração de backend.

## Reversibilidade

Com `HOME_CIDADE_VIVA_ENABLED=false`, a classe `home-compact-ux006a` não existe e a Home anterior permanece integral. Com `?todos=1`, a própria requisição retorna à composição completa.

## Validação final após o rebase

- Missão 006 integrada à `master` pelo commit `ecac8b6`;
- branch do patch rebaseada sobre a `master` sem conflitos;
- `HOME_CIDADE_VIVA_ENABLED=false` confirmado como valor padrão;
- flag desligada: Home anterior íntegra, com 10 categorias, 6 ofertas afiliadas e 6 empresas parceiras;
- flag ligada: sete links “Ver todos” funcionais e Cidade Viva imediatamente após Encontre Quem Resolve;
- ausência de overflow confirmada em 1440, 768, 390 e 320 px;
- novas capturas armazenadas em `docs/ux/evidencias/patch_ux_006a/final/`;
- teste de reversão: o revert do patch restaurou exatamente a árvore da `master` e os 143 testes da versão revertida foram aprovados;
- backend e banco permaneceram fora do diff do patch.
