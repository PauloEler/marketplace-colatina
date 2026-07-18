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

Publicada e validada em produção.

## Publicação

- PR: `#60`;
- hash do merge: `a50c47f09c97f41f0ce5ff4fff704eafe4bfbe0d`;
- merge realizado em: `18/07/2026 13:09:11` (horário de Brasília);
- CI da `master`: aprovado no workflow `29651391696`;
- deploy automático no Render: detectado em produção entre `13:10` e `13:11` (horário de Brasília);
- produção: `https://mercadocolatina.com.br/`.

## Validação final em produção

| Verificação | Resultado |
| --- | --- |
| Dashboard `/admin?visao=afiliados` | Ativo e acessível ao administrador |
| Estado inicial | Hoje: 0; 7 dias: 0; 30 dias: 0 |
| Clique desktop | `Celulares e acessórios`: 1 clique |
| Clique mobile 390 px | `Fones e áudio`: 1 clique |
| Estado final | Hoje: 2; 7 dias: 2; 30 dias: 2 |
| Ranking final | Celulares: 1; Fones: 1; demais categorias: 0 |
| Responsividade | Desktop e mobile sem overflow horizontal |
| Home | Conteúdo e layout preservados |
| Links oficiais | Seis URLs `meli.la` únicas preservadas |
| Segurança dos links | `target="_blank"` e `rel="sponsored noopener noreferrer"` preservados |
| Console | Sem erros originados pela aplicação |

O console do Chrome apresentou exclusivamente mensagens de uma extensão do navegador (`chrome-extension://`), sem relação com o Mercado Colatina.

## Privacidade

Nenhum dado pessoal é armazenado. Os eventos persistem somente parceiro, identificador da oferta, categoria, tipo do evento, origem, dispositivo e data/hora. Não são coletados nome, e-mail, telefone, IP, cookies de identificação ou identificador pessoal do visitante.

## Conclusão

O dashboard começou a registrar novos cliques em produção. A MX-004.1D está publicada, com CI aprovado, deploy ativo e validação desktop/mobile concluída. A MX-004.2 não foi iniciada.
