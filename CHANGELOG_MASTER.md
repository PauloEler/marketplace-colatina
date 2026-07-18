# CHANGELOG MASTER

## 2026-07-18 - MX-004.1D Analytics dos Afiliados

### Publicado

- PR #60 integrada na `master`.
- Hash do merge: `a50c47f09c97f41f0ce5ff4fff704eafe4bfbe0d`.
- CI da `master` aprovado no workflow `29651391696`.
- Deploy automatico no Render detectado em producao entre 13h10 e 13h11 (horario de Brasilia).

### Validado em producao

- Dashboard administrativo ativo em `/admin?visao=afiliados`.
- Contadores iniciaram em zero e passaram a registrar 2 cliques controlados.
- Clique desktop registrado em `Celulares e acessorios`.
- Clique mobile em 390 px registrado em `Fones e audio`, sem overflow horizontal.
- Totais de hoje, 7 dias e 30 dias atualizados de 0 para 2.
- Home, layout e seis links oficiais `meli.la` preservados.
- Abertura em nova guia com `rel="sponsored noopener noreferrer"` preservada.
- Console da aplicacao sem erros; aviso externo observado apenas em extensao do navegador.
- Eventos armazenam somente parceiro, oferta, categoria, tipo, origem, dispositivo e data/hora, sem dados pessoais.

### Restricoes preservadas

- Sem inicio da MX-004.2.

## 2026-07-18 - Ativacao comercial dos afiliados

### Publicado

- PR #57 integrada na `master`.
- Hash do merge: `e8224a01e4181f504065c3f034f63a277fbe63e7`.
- CI da `master` aprovado no workflow `29648666503`.
- Deploy automatico no Render detectado em producao as 11h48min34s.

### Ativado

- Conta `PAULO-ELER` ativa no Programa de Afiliados e Criadores do Mercado Livre.
- Seis links oficiais `meli.la` publicados na secao "Ofertas de Parceiros".
- Identificacao oficial `matt_word=paulo-eler`, `matt_tool=87431189` e `ref` preservada nos seis redirecionamentos.
- Monetizacao por afiliados oficialmente ativa.

### Validado

- Seis cards com URLs oficiais, preenchidas e unicas.
- Celulares e acessorios, fones e audio, informatica, casa e utilidades, ferramentas e eletroportateis direcionando para as buscas corretas.
- Abertura em nova guia com `rel="sponsored noopener noreferrer"`.
- Desktop 1440 px com seis cards visiveis e sem overflow.
- Mobile 390 px com dois cards visiveis e sem overflow.
- Console da aplicacao sem erros.

### Restricoes preservadas

- Sem alteracao de layout, CSS ou componentes.
- Sem inicio da MX-004.2.

## 2026-07-18 - MX-004.1 Home Monetizacao

### Publicado

- Release da Sprint MX-004.1 publicada em producao.
- PR #51 integrada na `master`.
- Hash do merge: `f74d8d3485062822ee4cca29bf4401b1e1766ada`.

### Adicionado

- Secao "Ofertas de Parceiros" abaixo de "Produtos em destaque".
- Carrossel responsivo com 6 cards.
- Cards com imagem, titulo, preco e botao "Ver oferta".
- Navegacao manual do carrossel.
- Rotacao automatica com respeito a `prefers-reduced-motion`.
- Aviso de transparencia para conteudo de parceiros.
- Imagens locais leves para ofertas.
- Documentacao de arquitetura, RFC, ADR, relatorio de sprint e evidencias.
- Relatorio de publicacao `docs/relatorios/RELATORIO_RELEASE_MX004_1.md`.

### Validado

- CI da `master` aprovado.
- Deploy automatico no Render validado.
- Producao validada em desktop e mobile.
- Console sem erros.
- Lighthouse em producao: Performance 95, Acessibilidade 97, Boas praticas 96, SEO 100.

### Restricoes preservadas

- Sem alteracao de banco de dados.
- Sem alteracao de autenticacao.
- Sem alteracao de regras de negocio.
- Sem APIs externas.
- Sem noticias.
- Sem patrocinadores reais.
