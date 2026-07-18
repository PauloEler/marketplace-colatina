# Relatório da Sprint MX-005.1 — Hoje em Colatina

## Objetivo

Criar o primeiro Painel Diário do Mercado Colatina, com cinco categorias reconhecíveis e leitura rápida.

## Implementado

- seção “Hoje em Colatina”;
- cards Tempo, Eventos, Empregos, Farmácia de Plantão e Avisos;
- estado “Em preparação” em todos os cards;
- configuração centralizada e reutilizável;
- SVGs locais e discretos;
- layout responsivo;
- testes automatizados de conteúdo, quantidade, transparência e ordem da Home.

## Arquitetura

`daily_city.py` concentra os cinco registros. O `app.py` apenas entrega os dados ao template, e a Home renderiza a mesma estrutura para cada categoria. Não existe API, banco, JavaScript ou conteúdo diário real.

## Impacto esperado

O visitante identifica as futuras informações locais em menos de dez segundos. O painel adiciona utilidade percebida sem competir com o marketplace ou transmitir dados não verificados.

## Arquivos da sprint

- `daily_city.py`;
- `app.py`;
- `templates/index.html`;
- `static/styles.css`;
- `tests/test_moderacao.py`;
- `docs/arquitetura/HOJE_EM_COLATINA.md`;
- `docs/rfc/RFC_MX005_1_HOJE_EM_COLATINA.md`;
- `docs/decisoes/ADR_002_PAINEL_DIARIO_COLATINA.md`;
- este relatório.

## Restrições preservadas

- sem APIs;
- sem banco novo ou alteração do banco existente;
- sem alteração de autenticação, pedidos ou anúncios;
- sem alteração de afiliados ou empresas parceiras;
- sem merge;
- sem deploy.

## Testes e evidências

- suíte completa: 107 testes aprovados;
- `ruff check`: aprovado;
- `ruff format --check`: aprovado;
- `git diff --check`: aprovado;
- console do navegador: sem erros ou avisos;
- cinco placeholders presentes e identificados;
- nenhuma API, imagem externa ou requisição adicional adicionada;
- ordem da Home preservada.

### Matriz responsiva

| Largura | Cards por linha | Placeholders | Overflow horizontal |
| --- | ---: | ---: | --- |
| 1280 px | 5 | 5 | Não |
| 1024 px | 5 | 5 | Não |
| 768 px | 3 | 5 | Não |
| 390 px | 2 | 5 | Não |
| 320 px | 1 | 5 | Não |

### Lighthouse local

- Performance: 84;
- Acessibilidade: 97;
- Boas práticas: 96;
- SEO: 100;
- nenhuma regressão crítica identificada.

### Evidências visuais

- desktop 1280 px: `docs/evidencias/mx005-1-local-desktop-1280.png`;
- mobile 390 px: `docs/evidencias/mx005-1-local-mobile-390.png`.

## Estado da entrega

Preparada para PR Draft e revisão. Publicação não autorizada.
