# Relatório — Missão 002 — Inteligência da Comunidade

## Problema real

Sugestões isoladas não permitem reconhecer rapidamente necessidades recorrentes, mudança de interesse e tempo de resposta. A cidade precisa ser compreendida por evidências agregadas, sem transformar sinais pequenos em certezas.

## Objetivo

Entregar o primeiro Radar da Cidade, exclusivamente administrativo, usando os dados já existentes do Ouvir Colatina.

## Decisões

- nenhuma alteração de banco;
- nenhuma IA ou integração externa;
- agregação determinística e somente de leitura;
- privacidade por apresentação exclusivamente agregada;
- amostra mínima antes de responder conclusivamente o que Colatina mais precisa.

## Entrega implementada

- rota administrativa `/admin/inteligencia-comunidade`;
- módulo `community_intelligence.py` somente de leitura;
- Radar da Cidade com métricas de volume, estados e períodos;
- ranking automático de categorias;
- palavras frequentes por sugestões distintas;
- termos recorrentes e aproximação lexical dos problemas citados;
- comparação de categorias entre janelas consecutivas de 30 dias;
- resposta principal com amostra mínima recente;
- schema interno `comunidade.v1`, sem autoria, preparado para decisão futura sobre IA;
- navegação administrativa e layout responsivo próprios.

## Banco e privacidade

Nenhuma tabela, coluna ou índice foi criado. O Radar lê a estrutura da Missão 001 e apresenta somente agregados. Nomes e mensagens completas não são renderizados no dashboard.

## Estado

Publicada em produção. PR #73 integrada na `master`, CI aprovado e validação final concluída.

## Testes e evidências

- 123 testes automatizados aprovados, incluindo quatro cenários específicos da Missão 002;
- `ruff check` aprovado;
- `ruff format --check` aprovado;
- `git diff --check` aprovado;
- desktop (1440 px): cinco indicadores e duas colunas de conteúdo, sem overflow;
- tablet (768 px): três indicadores por linha e conteúdo em uma coluna, sem overflow;
- mobile (390 px): dois indicadores por linha, sem overflow;
- mobile estreito (320 px): uma coluna, sem overflow;
- console do navegador sem erros ou avisos;
- rota administrativa, isolamento de acesso e ausência de mensagens completas no painel validados;
- Marketplace, Analytics de Afiliados, Empresas Parceiras, Central de Notificações e Hoje em Colatina preservados pela suíte de regressão.
- PR Draft #73 criada contra `master` e CI do GitHub aprovado.

O cenário visual controlado possuía seis sugestões e retornou **Saúde** como prioridade recente. Esse resultado é apenas evidência funcional: em produção, a resposta será calculada exclusivamente com os dados reais e será apresentada como inconclusiva quando os últimos 30 dias tiverem menos de três sugestões.

## Limitações e próximos passos

- a frequência é lexical e não interpreta sinônimos, contexto ou intenção;
- crescimento compara duas janelas consecutivas de 30 dias e deve ser lido como sinal preliminar;
- nenhuma receita, decisão ou ação automática é produzida;
- qualquer IA futura exigirá nova RFC, ADR, avaliação de privacidade e amostra útil.

## Publicação

- PR: #73;
- hash do merge: `ffa7c653c46f608c6ace31316ead0a9594078b52`;
- CI da `master`: aprovado no workflow `29754043065`;
- deploy automático: detectado em produção às 12h14 de 20 de julho de 2026, horário de Brasília;
- URL validada: `https://mercadocolatina.com.br/admin/inteligencia-comunidade`.

## Validação final em produção

- Radar autenticado carregado com título, resposta principal, indicadores, períodos, ranking, palavras frequentes, crescimento, recorrências e preparação futura para IA;
- dados reais: uma sugestão, já arquivada, sem exposição de nome ou mensagem completa;
- resposta apresentada: **Ainda não há dados suficientes**, coerente com o mínimo de três sugestões nos últimos 30 dias;
- Dashboard Executivo carregado, com Radar, Analytics de Afiliados e Central de Notificações acessíveis;
- desktop 1440 px: cinco indicadores e duas colunas de conteúdo, sem overflow;
- tablet 768 px: três indicadores por linha e conteúdo em uma coluna, sem overflow;
- mobile 390 px: dois indicadores por linha, sem overflow;
- mobile 320 px: uma coluna, sem overflow;
- console do site limpo;
- nenhuma escrita foi realizada no banco durante a validação;
- funcionalidades anteriores preservadas.

## Encerramento

A Missão 002 está oficialmente publicada e encerrada. A Missão 003 não foi iniciada.
