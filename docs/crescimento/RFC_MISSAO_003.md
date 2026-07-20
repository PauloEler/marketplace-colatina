# RFC - MISSAO 003 OPERACAO PRIMEIROS 100

## Problema

Os indicadores da Operacao Tracao existem, mas a Diretoria ainda precisa transformar dados dispersos em uma leitura diaria de progresso, funil, empresas, comunidade e bloqueios para chegar a 100 usuarios recorrentes.

## Objetivo

Criar um painel administrativo unico, somente leitura, e uma camada de agregacao dedicada a Operacao 100, reutilizando tabelas e definicoes existentes.

## Proposta

- modulo `operation_100.py` para consultas e definicoes;
- rota administrativa `/admin/operacao-100`;
- funil de coorte progressiva de 30 dias;
- dashboards de empresas e comunidade;
- marcos automaticos quando houver fonte confiavel;
- bloqueios determinísticos, sem IA e sem estimativas.

## Fontes

`usuarios`, `anuncios`, `pedidos`, `pedido_eventos`, `afiliado_eventos`, `sugestoes_comunidade`, `traction_user_activity_daily`, `traction_access_source_daily` e configuracao institucional de parceiros.

## Privacidade e compatibilidade

Nao ha nova tabela, dado pessoal, cookie, API ou escrita operacional. Marketplace, pedidos, afiliados, Empresas Parceiras, Hoje em Colatina e Central de Notificacoes nao sofrem alteracao de regra.

## Criterios de aceite

Painel restrito ao administrador, metricas com fonte documentada, funil sem conversao artificial, receita indisponivel explicitada, responsividade em desktop/tablet/390/320, console limpo, suite e Ruff aprovados.
