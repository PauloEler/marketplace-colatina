# RFC - MISSAO 004 OPERACAO CONQUISTAR COLATINA

## Problema

A estrategia de crescimento nao possuia uma fonte operacional para visitas, bairros, embaixadores e prioridade semanal. Planilhas ou memoria informal impediriam medicao consistente e aprendizado.

## Proposta

Criar um painel administrativo isolado com tres estruturas minimas:

- `growth_commercial_companies`: acompanhamento e checklist por empresa;
- `growth_ambassadors`: participacao e indicacoes;
- `growth_weekly_missions`: uma prioridade ativa por semana.

O relatorio semanal sera calculado sob demanda usando essas estruturas e as metricas existentes de usuarios, anuncios, pedidos, afiliados e sugestoes.

## Privacidade

Contato de empresa e embaixador e dado administrativo restrito. O sistema nao publica, envia ou integra esses dados. Nenhum IP, localizacao precisa ou historico de mensagens e coletado.

## Compatibilidade

Nao ha alteracao em Marketplace, pedidos, Analytics, afiliados, Empresas Parceiras, Radar, notificacoes ou Hoje em Colatina.

## Criterios

Acesso administrativo, CSRF, validacao de entrada, uma missao ativa, relatorio reproduzivel, responsividade 1440/768/390/320, console limpo, suite e Ruff aprovados.
