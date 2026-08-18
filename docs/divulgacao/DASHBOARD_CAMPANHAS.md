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

Nesta versão os dados são um retrato manual da conferência realizada em
18/08/2026 na conta Google Ads `333-169-5325`. O painel identifica isso
explicitamente. Não existe sincronização automática e nenhuma métrica ausente é
inventada.

## Arquitetura

`campaign_dashboard.py` centraliza os snapshots e monta os agregados. A rota
administrativa apenas entrega essa estrutura ao template. Essa separação
permite substituir a origem manual por adaptadores oficiais do Google Ads e da
Meta no futuro, preservando o template.

## Limitações

- os números não mudam até uma nova conferência registrada no código;
- conversões ainda não estão mensuradas;
- Facebook e Instagram aparecem somente no roteiro de evolução;
- o painel não cria, edita, pausa ou publica campanhas.

## Próximos passos

1. Observar a entrega das duas campanhas no Google Ads.
2. Registrar a primeira leitura com impressões e cliques.
3. Definir a conversão principal antes de automatizar decisões.
4. Avaliar integração oficial, somente com credenciais e autorização.
