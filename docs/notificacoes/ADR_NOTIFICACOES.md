# ADR — Infraestrutura única de notificações

## Status

Aceita na MX-006.1.

## Decisão

Centralizar notificações persistentes na tabela `notifications` e no módulo `notification_center.py`.

## Alternativas consideradas

1. Continuar calculando contadores diretamente nas tabelas de pedidos e anúncios. Rejeitada porque mistura domínios, não registra leitura e multiplica soluções isoladas.
2. Criar uma tabela por tipo de aviso. Rejeitada por duplicar interface, permissões e estados.
3. Usar serviço externo. Rejeitada nesta fase por custo, dependência e escopo.

## Consequências

- Positivas: contrato único, estados consistentes, idempotência, isolamento por usuário e evolução previsível.
- Custos: uma consulta resumida por página autenticada e manutenção de uma tabela adicional.
- Regra permanente: funcionalidades futuras devem emitir eventos pela Central; não devem criar sinos ou contadores paralelos.
