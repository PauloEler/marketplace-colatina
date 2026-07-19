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
- PR #68 revisada e integrada na `master`.
- Hash do merge: `0812b481ee8599bbb4ec6f1d22515aef9be8b9a1`.
- CI da `master` aprovado no workflow `29689617071`.
- Deploy automático no Render iniciado às 10h50 e publicado às 10h51 de 19/07/2026, horário de Brasília.

## Teste real controlado em produção

O teste utilizou um comprador, um vendedor, um anúncio e o pedido temporário #4. O comprador realizou a solicitação e permaneceu com zero notificações do pedido. O vendedor recebeu uma notificação `NOVO_PEDIDO`, com contador igual a um.

Ao abrir a notificação, o sistema direcionou para `/pedidos#pedido-4`, encontrou o card correspondente e alterou o estado para lida. Também foram confirmados o comando “Marcar todas como lidas” e o arquivamento pelo histórico em `/notificacoes`.

O isolamento por usuário foi preservado. A visão administrativa agregada retornou totais e agrupamento por tipo sem expor o conteúdo privado das notificações. Nenhum novo dado pessoal é armazenado pela Central.

## Responsividade e estabilidade em produção

- Desktop 1280 px: sino, contador, painel e destino validados.
- Mobile 390 px: painel contido na viewport, sem overflow horizontal.
- Mobile 320 px: painel contido na viewport, sem overflow horizontal.
- Interações de abertura, leitura, marcação coletiva e arquivamento concluídas sem erro de aplicação.
- Home, Ofertas de Parceiros, Analytics, Empresas Parceiras e Hoje em Colatina permaneceram operacionais.

## Encerramento do teste

- Pedido #4 encerrado como rejeitado.
- Anúncio temporário #17 removido.
- Contas temporárias do comprador e vendedor desativadas.
- Identificações temporárias de fundador removidas e vagas restauradas.
- Cópias administrativas do evento de teste arquivadas.

## Próximos passos

A MX-006.1 está publicada e encerrada. Novos produtores de eventos deverão usar exclusivamente esta infraestrutura e dependerão de autorização específica. A MX-006.2 não foi iniciada.
