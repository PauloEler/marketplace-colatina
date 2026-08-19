# Dashboard de Campanhas

## Objetivo

Concentrar, em uma tela administrativa, o acompanhamento das campanhas de
divulgação do Mercado Colatina e do Topa Tudo Colatinense.

## Problema real

As campanhas estavam sendo conferidas diretamente nas plataformas, sem uma
visão única que separasse configuração, resultado e próxima ação. Isso torna a
comparação mais lenta e aumenta o risco de interpretar ausência de dados como
desempenho.

## Primeira versão

O painel está disponível para administradores em `/admin?visao=campanhas` e
apresenta:

- campanhas acompanhadas e seus estados;
- impressões, cliques, custo e CTR;
- saldo pré-pago conhecido da conta;
- localidade, orçamento, aprovação e qualidade;
- palavras adicionadas à campanha do Topa Tudo;
- próxima ação recomendada por campanha;
- data e origem de cada conferência.

## Origem e confiabilidade

Com as credenciais oficiais configuradas, os dados de desempenho são
sincronizados pela Google Ads API e armazenados em cache por 15 minutos. Sem as
credenciais ou durante uma indisponibilidade, o painel preserva o retrato manual
da conferência de 18/08/2026 e identifica claramente o fallback. Nenhuma métrica
ausente é inventada.

## Arquitetura

`google_ads_service.py` autentica, consulta, normaliza e mantém o cache da API.
`campaign_dashboard.py` combina a resposta oficial com os snapshots de
segurança e monta os agregados. A rota administrativa entrega essa estrutura ao
template sem acessar ou exibir segredos.

## Limitações

- a sincronização depende do token de desenvolvedor e das credenciais OAuth;
- o saldo pré-pago permanece como conferência manual;
- Facebook e Instagram aparecem somente no roteiro de evolução;
- o painel não cria, edita, pausa ou publica campanhas.

## Próximos passos

1. Concluir a autorização oficial da API.
2. Cadastrar as credenciais secretas no Render.
3. Validar a primeira sincronização automática.
4. Definir a conversão principal antes de automatizar decisões.
