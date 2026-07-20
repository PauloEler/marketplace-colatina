# RFC — Missão 002 — Inteligência da Comunidade

**Status:** aprovada para implementação pela Missão 002

**Data:** 20 de julho de 2026

## Problema

As sugestões já possuem fluxo de entrada e análise, mas a administração ainda precisa ler registros individualmente para perceber volume, recorrência e mudança de interesse.

## Objetivo

Criar um Radar da Cidade somente administrativo que agregue sugestões existentes e revele sinais mensuráveis sem IA, integração externa ou nova coleta de dados.

## Proposta

- rota administrativa `/admin/inteligencia-comunidade`;
- módulo `community_intelligence.py`, somente de leitura;
- template `inteligencia_comunidade.html`;
- métricas de volume, estado, categoria, período e tempo até análise;
- ranking automático por categoria;
- extração lexical determinística de palavras frequentes;
- comparação dos últimos 30 dias com os 30 dias anteriores;
- identificação de termos recorrentes presentes em duas ou mais sugestões;
- resposta-síntese com limiar mínimo de três sugestões nos últimos 30 dias;
- dataset interno versionado para uma eventual camada futura de IA.

## Fonte e períodos

A única fonte será `sugestoes_comunidade`. Os períodos serão Hoje, 7, 30 e 90 dias. Crescimento compara janelas consecutivas de 30 dias. Estados pendentes são `nova`, `em_analise` e `planejada`.

## Limites

- frequência de palavras não equivale a compreensão semântica;
- crescimento com amostra pequena é sinal preliminar, não tendência consolidada;
- sugestões arquivadas permanecem no histórico e nas contagens, identificadas separadamente;
- empate de ranking é resolvido alfabeticamente para manter resultado determinístico;
- o painel não publica mensagens nem nomes.

## Fora do escopo

- IA, classificação automática, embeddings ou geração de texto;
- APIs externas;
- alteração da tabela ou criação de tabela agregada;
- votação, moderação automática ou decisão automática;
- alteração de Marketplace, Afiliados, Empresas Parceiras, Central de Notificações ou Hoje em Colatina.

## Critérios de aceite

- somente administrador acessa o Radar;
- todas as métricas refletem a tabela existente;
- palavras ignoram termos comuns e contam sugestões distintas;
- períodos e crescimento são verificáveis;
- amostra insuficiente é declarada;
- desktop, tablet, 390 px e 320 px não apresentam overflow;
- suíte, Ruff e CI aprovados.
