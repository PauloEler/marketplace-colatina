# CHANGELOG MASTER

## 2026-07-20 - Missão 002 Inteligência da Comunidade

### Adicionado

- Dashboard administrativo **Radar da Cidade** em `/admin/inteligencia-comunidade`.
- Indicadores de volume, estados, períodos e tempo médio até análise.
- Ranking automático de categorias, palavras frequentes, recorrências e categorias em crescimento.
- Resposta baseada em amostra recente para a pergunta **O que Colatina mais precisa neste momento?**.
- Schema interno `comunidade.v1`, sem autoria, preparado para uma avaliação futura de IA.

### Garantias

- Agregação determinística e somente de leitura.
- Nenhuma migração ou alteração de banco.
- Nenhum nome ou mensagem completa exibido no Radar.
- Nenhuma IA, API externa ou decisão automática implementada.
- Marketplace, Analytics de Afiliados, Empresas Parceiras, Central de Notificações e Hoje em Colatina preservados.

### Publicação

- PR #73 aprovada para integração na `master`.
- Resultado final do merge, CI, deploy e validação será registrado após a publicação.

## 2026-07-20 - Missão 001 Ouvir Colatina

### Publicado

- PR #71 integrada na `master`.
- Hash do merge: `5baec757ccf16c16020859f8697fc0d472e2a3cf`.
- CI da `master` aprovado no workflow `29739307446`.
- Deploy automático no Render detectado em produção às 08h42, horário de Brasília.

### Adicionado

- Botão global e discreto **Sugira uma melhoria**.
- Formulário público em `/sugerir`, com nome opcional, categoria e mensagem.
- Tabela isolada `sugestoes_comunidade` e estados Nova, Em análise, Planejada, Implementada e Arquivada.
- Painel administrativo em `/admin/sugestoes`, com filtros e métricas próprias.
- Fundação documental da Operação Cidade Viva e processo permanente orientado por problemas reais da cidade.

### Validado em produção

- Botão e formulário carregando corretamente.
- Sugestão controlada cadastrada com confirmação visual.
- Painel administrativo exibindo a sugestão, filtros, estados e métricas corretamente.
- Alteração da sugestão controlada de Nova para Arquivada confirmada em produção.
- Tempo médio até análise calculado após a mudança de estado.
- Desktop 1440 px, tablet 768 px e mobile 390/320 px sem overflow horizontal.
- Botão responsivo preservado, inclusive em tela estreita de 320 px.
- Console público e do painel sem erros originados pelo site.

### Restrições preservadas

- Marketplace, Analytics, Afiliados, Empresas Parceiras, Hoje em Colatina e Central de Notificações não foram alterados.
- Votação comunitária não implementada; permanece condicionada a RFC própria.
- Missão 002 não iniciada.

## 2026-07-19 - MX-006.1 Central de Notificações

### Publicado

- PR #68 integrada na `master`.
- Hash do merge: `0812b481ee8599bbb4ec6f1d22515aef9be8b9a1`.
- CI da `master` aprovado no workflow `29689617071`.
- Deploy automático no Render concluído às 10h51, horário de Brasília.

### Adicionado

- Infraestrutura central e reutilizável de notificações.
- Tabela própria `notifications`, com estados não lida, lida e arquivada.
- Sino, contador automático, painel responsivo e histórico em `/notificacoes`.
- Ações para abrir, marcar como lida, marcar todas como lidas e arquivar.
- Notificação `NOVO_PEDIDO` para vendedores e visão administrativa agregada.
- Isolamento por usuário, sem armazenamento de novos dados pessoais.

### Validado em produção

- Teste real controlado com solicitação de compra e entrega da notificação ao vendedor.
- Contador alterado de zero para um e abertura direcionada ao pedido correto.
- Mudança de estado para lida, marcação de todas e arquivamento confirmados.
- Comprador sem acesso à notificação do vendedor.
- Visão administrativa agregada confirmada sem exposição do conteúdo de outros usuários.
- Desktop, 390 px e 320 px validados sem overflow horizontal.
- Home e funcionalidades anteriores preservadas, sem erros de aplicação observados.

### Limpeza do teste

- Pedido controlado encerrado como rejeitado.
- Anúncio temporário removido.
- Contas temporárias desativadas e vagas de fundador restauradas.

### Restrições preservadas

- Sem push, WhatsApp, e-mail, Firebase, OneSignal ou WebPush.
- Sem início da MX-006.2.

## 2026-07-18 - MX-005.1 Hoje em Colatina

### Publicado

- PR #64 integrada na `master`.
- Hash do merge: `a708f0e5bcb53d20e153ebc643255c0567ade030`.
- CI da `master` aprovado no workflow `29658007584`.
- Deploy automatico no Render detectado em producao as 16h35min33s, horario de Brasilia.

### Adicionado

- Secao "Hoje em Colatina" com cinco cards reutilizaveis.
- Placeholders transparentes para Tempo, Eventos, Empregos, Farmacia de Plantao e Avisos.
- Arquitetura preparada para evolucao futura, sem APIs ou alteracoes de banco nesta sprint.

### Validado em producao

- Home e painel diario carregando normalmente.
- Cinco cards em 5 colunas no desktop, 3 no tablet e 2 no mobile.
- Sem overflow horizontal nos tres formatos.
- Analytics, Empresas Parceiras e Ofertas de Parceiros preservados.
- Console sem erros ou avisos.
- Lighthouse: Performance 92, Acessibilidade 97, Boas praticas 96, SEO 100.
- Sem regressao critica.

### Backlog

- `PERF-001`: investigar a medicao local de Performance 84 registrada durante a sprint.

### Restricoes preservadas

- Sem inicio da MX-005.2.

## 2026-07-18 - MX-004.2 Empresas Parceiras e Confiança

### Publicado

- PR #62 integrada na `master`.
- Hash do merge: `472281189f4eeefdfdd588cec69e1d228b3bd07f`.
- CI da `master` aprovado no workflow `29653561010`.
- Deploy automático no Render detectado em produção às 14h18min07s, horário de Brasília.

### Adicionado

- Seção “Por que confiar no Mercado Colatina?” com cinco compromissos institucionais.
- Seção “Empresas Parceiras” com seis espaços reservados e transparentes.
- Arquitetura preparada para Parceiro Local, Parceiro Destaque e Parceiro Premium.
- Páginas institucionais Quem Somos e Seja Parceiro.
- Rodapé reforçado e novas rotas adicionadas ao sitemap.

### Validado em produção

- Home carregando normalmente.
- Seis cards de empresas parceiras em 3 colunas no desktop, 2 no tablet e 1 no mobile.
- Sem overflow horizontal nos três formatos.
- Seis ofertas oficiais de afiliados e analytics preservados.
- Console sem erros ou avisos.
- Lighthouse: Performance 96, Acessibilidade 97, Boas práticas 96, SEO 100.
- Sem regressão crítica.

### Restrições preservadas

- Sem alteração de banco, pedidos, anúncios, autenticação ou regras comerciais.
- Sem empresas ou patrocinadores reais.
- Sem início da MX-004.3.

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
