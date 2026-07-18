# Relatório — Sprint MX-004.1D

## Objetivo

Criar a camada interna de Analytics da seção **Ofertas de Parceiros**, com registro anônimo, métricas administrativas e arquitetura preparada para novos programas de afiliados.

## Entregas

- registro de impressões e cliques;
- categoria, parceiro, origem, dispositivo e data/hora derivados ou validados;
- contagem de cliques únicos do DOM e cliques repetidos do usuário;
- dashboard administrativo em `/admin?visao=afiliados`;
- totais de hoje, 7 dias e 30 dias;
- ranking, TOP categoria, menor interesse e CTR por categoria;
- suporte estrutural a Mercado Livre, Amazon, Magalu, Shopee e outros;
- proteção CSRF e ausência de dados pessoais;
- suporte SQLite e PostgreSQL no banco existente.

## Arquivos alterados

- `affiliate_analytics.py`
- `app.py`
- `database.py`
- `partner_offers.py`
- `static/partner-offers-carousel.js`
- `templates/index.html`
- `templates/base.html`
- `templates/analytics_afiliados.html`
- `tests/test_moderacao.py`
- `docs/analytics/*`

## Preservado

- layout, CSS e design da Home;
- posição, rotação e navegação do carrossel;
- seis URLs oficiais de afiliado;
- abertura em nova guia;
- autenticação e regras de negócio existentes;
- arquivos antigos soltos no repositório.

## Testes cobertos

- clique único;
- cliques repetidos;
- desktop e mobile;
- impressão única por card em cada carregamento;
- token CSRF;
- rejeição de evento, oferta e dispositivo inválidos;
- origem e dados comerciais definidos pelo servidor;
- acesso administrativo ao dashboard;
- totais, ranking e CTR;
- estado sem dados;
- regressão da Home e dos links oficiais.

## Resultado das validações

- suíte automatizada: 104 testes aprovados;
- Ruff check: aprovado;
- Ruff format check: aprovado;
- `git diff --check`: aprovado;
- validação desktop: 6 impressões únicas, 2 cliques repetidos no mesmo card e ranking atualizado;
- validação mobile em 390 px: clique registrado como `mobile`, sem overflow horizontal;
- carrossel manual: sexto card entrou em visão e gerou sua impressão;
- dashboard: totais, ranking e CTR renderizados em desktop e mobile;
- console do navegador: sem erros.

## Limitações

- não mede vendas, comissão ou receita confirmada;
- não identifica pessoas ou visitantes únicos;
- bloqueadores de JavaScript podem reduzir a cobertura;
- retenção e agregação histórica serão definidas após observar volume real.

## Status

Implementação pronta para revisão. Sem merge e sem deploy.
