# CHANGELOG MASTER

## 2026-07-21 - PATCH UX-005C Primeira dobra

### Publicado

- PR #84 integrada na `master` por squash merge.
- Hash do merge: `62c2686155153342b75aaf909cc0f1833ba4df80`.
- CI da `master` aprovado no workflow `29821308245`.
- Deploy automático no Render detectado em produção às 07h14min49s, horário de Brasília.

### Melhorado

- Hero mais compacto e orientado às ações principais.
- CTAs **Comprar agora** e **Anunciar grátis** com maior clareza.
- Busca rápida com exemplo e botão **Encontrar agora**.
- Faixa **Encontre Quem Resolve** posicionada antes das categorias.
- Categorias com foco visível e navegação mobile horizontal.
- Fotografia preservada no desktop e omitida até 960 px para priorizar ações.

### Validado em produção

- Desktop 1440 × 900, mobile 390 × 844 e mobile 320 × 720 sem overflow horizontal.
- Hero, busca, primeira dobra, dez categorias e quatro caminhos principais operacionais.
- Destinos de compra, cadastro, busca, categorias e **Encontre Quem Resolve** preservados.
- Console da aplicação sem erros; mensagens observadas pertenciam exclusivamente a uma extensão do Chrome.
- Produtos, pedidos, empresas, dashboards, backend e banco de dados preservados.

## 2026-07-20 - Missao 005 Sprint 5.1 Encontre Quem Resolve

### Adicionado

- Jornada publica mobile-first para descrever uma necessidade local em quatro passos.
- Classificacao interna baseada no problema, sem exigir categoria do morador.
- Mural `/quem-resolve` para empresas acompanharem pedidos locais.
- Resposta por WhatsApp restrita a lojas autenticadas e administradores.
- Tabela `pedidos_servico` e dominio isolado das regras do marketplace.
- Protecao do contato, consentimento explicito, CSRF, limites e bloqueio de telefone na descricao publica.
- RFC, ADR, arquitetura e relatorios da Sprint 5.1.

### Garantias

- WhatsApp nao exibido na listagem publica.
- Fluxo basico preservado sem JavaScript.
- Anuncios, pedidos, afiliados, empresas parceiras, notificacoes e dashboards anteriores preservados.
- Nenhuma integracao externa, pagamento, chat ou IA adicionada.

### Publicacao

- PR #82 integrada na `master` por squash merge.
- Hash do merge: `f511b1a97db2c9e74bbeb473882ca610804d50ef`.
- CI da `master` aprovado no workflow `29781849320`.
- Deploy automatico no Render detectado em producao por volta de 18h54, horario de Brasilia.

### Validado em producao

- Rota publica, fluxo de quatro passos e revisao final carregando corretamente.
- Mural das empresas inicializado com estado vazio real e sem erro de banco.
- Dashboard Executivo autenticado preservado.
- Desktop 1440/1024 px, tablet 768 px e mobile 390/320 px validados.
- Formularios e paineis novos sem overflow horizontal; alvos principais com 48 px.
- Console da aplicacao sem erros.
- Home, Ofertas de Parceiros, Empresas Parceiras, Hoje em Colatina, Afiliados e Central de Notificacoes preservados.
- Nenhum pedido tecnico falso foi persistido em producao; gravacao e resposta autenticada foram confirmadas pelos 138 testes automatizados e pelo CI.

## 2026-07-20 - Missao 004 Operacao Conquistar Colatina

### Adicionado

- Dashboard administrativo Tracao Comercial em `/admin/tracao-comercial`.
- Indicadores de empresas visitadas, interessadas, cadastradas, parceiras, bairros, visitas e conversao.
- Painel de Embaixadores com indicacoes e participacao.
- Missao da Semana com uma unica prioridade ativa e progresso mensuravel.
- Checklist do ciclo da empresa, da visita a recomendacao de outra empresa.
- Relatorio executivo semanal em Markdown, identificado como previa ou fechamento de sexta-feira.
- Operacao, playbooks, calendario, checklist, RFC, ADR e relatorio da Missao 004.

### Garantias

- Escritas administrativas protegidas por autenticacao e CSRF.
- Contatos restritos ao administrador.
- Tabelas comerciais isoladas dos dominios existentes.
- Nenhuma campanha paga, automacao de marketing, CRM completo ou integracao externa.
- Marketplace, pedidos, Analytics, Afiliados, Empresas Parceiras, Radar da Cidade, Central de Notificacoes e Hoje em Colatina preservados.

### Publicacao

- PR #79 integrada na `master` por squash merge.
- Hash do merge: `734f2a55a0e99cb8bb2284c8b37ac973c2985cb9`.
- CI da `master` aprovado no workflow `29769148411`.
- Deploy automatico no Render detectado em producao as 15h51, horario de Brasilia.

### Validado em producao

- Dashboard com 7 indicadores e 4 secoes operacionais.
- Paineis de Empresas, Embaixadores e Missao da Semana disponiveis ao administrador.
- Relatorio semanal autenticado apontando para a rota publicada.
- Desktop 1440 px, notebook 1024 px, tablet 768 px e mobile 390/320 px sem overflow horizontal.
- Console da aplicacao sem erros; mensagens observadas pertenciam a extensoes do Chrome.
- Funcionalidades anteriores preservadas e sem regressao identificada.
- Operacao Conquistar Colatina oficialmente iniciada.

## 2026-07-20 - Missao 003 Operacao Primeiros 100

### Adicionado

- Dashboard administrativo Operacao Primeiros 100 em `/admin/operacao-100`.
- Onze indicadores diarios de usuarios, empresas, marketplace, afiliados e comunidade.
- Funil progressivo de Visitante, Cadastro, Primeiro anuncio, Primeiro pedido, Primeira venda e Usuario recorrente.
- Dashboard das Empresas com empresas cadastradas, parceiras, ativas e sem anuncio ativo.
- Dashboard da Comunidade integrado ao Radar da Cidade.
- Checklist de oito marcos e leitura deterministica dos bloqueios de crescimento.
- Playbooks de usuarios e empresas, RFC, ADR e documentacao operacional.

### Garantias

- Nenhuma tabela ou regra de negocio foi alterada.
- Recorrencia permanece definida como atividade em duas semanas consecutivas.
- Receita de afiliados e empresas convidadas aparecem como nao mensuradas enquanto nao houver fonte oficial.
- Visitantes permanecem agregados, sem identificacao individual adicional.
- Funcionalidades anteriores preservadas.

### Publicacao

- PR #77 integrada na `master` por squash merge.
- Hash do merge: `a098a604a7c5700c01ada03ed2b3c97f88bef9bf`.
- CI da `master` aprovado no workflow `29765958966`.
- Deploy automatico no Render detectado em producao as 15h03, horario de Brasilia.

### Validado em producao

- Dashboard Operacao 100 com 11 indicadores e 6 secoes executivas.
- Funil de Crescimento com 6 etapas e conversoes progressivas.
- Dashboards das Empresas e da Comunidade carregando dados reais.
- Metricas indisponiveis identificadas como `Nao mensurado` e `Nao informada pelo parceiro`.
- Desktop 1440 px, notebook 1024 px, tablet 768 px e mobile 390/320 px sem overflow horizontal.
- Console da aplicacao sem erros; mensagens observadas pertenciam exclusivamente a extensao do Chrome.
- Home, Operacao Tracao, Afiliados, Radar da Cidade, Empresas Parceiras, Hoje em Colatina e Central de Notificacoes preservados.
- Missao 003 oficialmente encerrada.

## 2026-07-20 - Operacao Tracao 1.0

### Adicionado

- Dashboard Executivo unificado com Usuarios, Empresas, Marketplace, Afiliados, Comunidade e Radar da Cidade.
- Medicao semanal de novos usuarios, atividade autenticada, recorrencia e retorno.
- Origem de acesso armazenada somente por categoria agregada.
- Indicadores de empresas, anuncios, pedidos, conversao, resposta, receita interna, afiliados e sugestoes.
- Relatorio Executivo Semanal em Markdown gerado a partir da mesma fonte do dashboard.
- OKRs, KPIs, Playbook de Crescimento, RFC, ADR e documentacao operacional.

### Garantias

- Nenhum IP, referrer completo, UTM bruto ou identificador anonimo persistente armazenado.
- Receita de afiliados e empresas convidadas declaradas como nao mensuradas enquanto nao houver fonte oficial.
- Funcionalidades anteriores preservadas.
- Operacao prevista para 20 de julho a 18 de agosto de 2026.

### Publicacao

- PR #75 integrada na `master`.
- Hash do merge: `53bc802c015d27b532c50b6f0afef7faa677984d`.
- CI da `master` aprovado no workflow `29763648628`.
- Deploy automatico no Render detectado em producao as 14h28, horario de Brasilia.

### Validado em producao

- Dashboard Executivo com as seis frentes e dados reais.
- Relatorio semanal autenticado disponivel no dashboard.
- OKRs, KPIs e Playbook presentes na versao publicada.
- Desktop 1440 px, tablet 768 px, mobile 390 px e 320 px sem overflow horizontal.
- Console da aplicacao sem erros; mensagem isolada observada pertence a uma extensao do Chrome.
- Dashboard anterior, Central de Notificacoes, Afiliados, Comunidade e Radar preservados.
- Operacao Tracao oficialmente iniciada.

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

- PR #73 integrada na `master`.
- Hash do merge: `ffa7c653c46f608c6ace31316ead0a9594078b52`.
- CI da `master` aprovado no workflow `29754043065`.
- Deploy automático no Render detectado em produção às 12h14, horário de Brasília.

### Validado em produção

- Radar autenticado carregando em `/admin/inteligencia-comunidade`.
- Dashboard Executivo preservado e com acesso ao Radar, Afiliados e Central de Notificações.
- Dados reais exibidos sem nomes ou mensagens completas.
- Amostra de uma sugestão tratada corretamente como insuficiente para apontar uma prioridade da cidade.
- Desktop 1440 px, tablet 768 px, mobile 390 px e 320 px sem overflow horizontal.
- Console do site sem erros ou avisos.
- Banco preservado, sem migração e sem escrita durante a validação.
- Home, Marketplace, Ofertas de Parceiros, Empresas Parceiras, Hoje em Colatina, Analytics e Central de Notificações preservados.

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
