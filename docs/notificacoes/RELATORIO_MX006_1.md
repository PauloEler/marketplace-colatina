# Relatório MX-006.1 — Central de Notificações

## Objetivo

Criar a infraestrutura oficial de notificações internas do Mercado Colatina sem alterar Marketplace, Analytics, Afiliados, Empresas Parceiras ou Hoje em Colatina.

## Entregas

- Tabela `notifications` para SQLite e PostgreSQL.
- Serviço central com tipos, estados, idempotência e permissões.
- Geração de `NOVO_PEDIDO` para titular, gestores vinculados e administradores.
- Sino com contador e painel responsivo.
- Ações abrir, marcar como lida, marcar todas e arquivar.
- Histórico em `/notificacoes`.
- Visão administrativa agregada.
- Destino direto para o card do pedido.
- Testes automatizados e documentação.

## Decisões e motivação

O contador antigo de pedidos foi substituído para impedir duas fontes de verdade. O registro acontece na mesma transação do pedido, garantindo consistência. O painel usa HTML nativo e permanece funcional sem JavaScript.

## Impacto esperado

Pedidos novos ficam visíveis em qualquer página autenticada. A plataforma ganha uma base reutilizável para os demais eventos previstos.

## Limitações

Somente novos pedidos geram eventos. Não há push, WhatsApp, e-mail, Firebase, OneSignal ou WebPush. A atualização não é em tempo real.

## Validação

- 115 testes automatizados aprovados.
- Ruff check e formatação aprovados.
- Desktop 1280 px: sino, contador, painel e abertura validados sem overflow.
- Mobile 390 px e 320 px: painel contido na viewport e sem rolagem horizontal.
- Abertura marcou a notificação como lida e direcionou ao pedido correto.
- Comportamento progressivo do componente validado por interação real no navegador.
- Nenhum erro de aplicação foi observado durante os fluxos testados.
- Não houve merge nem deploy.

## Próximos passos

Após aprovação, publicar a Central e planejar produtores para moderação, mensagens e conclusão de vendas, um por Sprint e sempre usando esta infraestrutura.
