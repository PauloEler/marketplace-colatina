# Arquitetura da Central de Notificações

## Objetivo

Oferecer uma infraestrutura única para avisos internos do Mercado Colatina. Nenhuma funcionalidade futura deve criar contador, tabela ou painel próprio de notificações.

## Componentes

- `notifications`: tabela independente, vinculada ao destinatário.
- `notification_center.py`: serviço central para criar, listar, contar, ler e arquivar.
- `components/notification_center.html`: sino e painel reutilizados pelo cabeçalho.
- `/notificacoes`: histórico do usuário e visão administrativa agregada.
- `notification-center.js`: comportamento acessível de fechamento do painel.

## Modelo de dados

Cada registro guarda destinatário, tipo, título, descrição curta, URL interna, estado, referência opcional, chave idempotente, metadados JSON e datas de criação, leitura e arquivamento.

Estados oficiais: `nao_lida`, `lida` e `arquivada`.

Tipos preparados: novo pedido, nova mensagem, anúncio aprovado/reprovado/expirando, venda concluída, aviso do sistema, empresa parceira e promoção. Nesta entrega somente `NOVO_PEDIDO` possui regra de geração.

## Fluxo Novo pedido

1. O comprador envia a solicitação.
2. O pedido e a notificação são registrados na mesma transação.
3. Titular, gestores vinculados e administradores ativos recebem registros individuais.
4. A chave `novo-pedido:{pedido}:{destinatario}` impede duplicidade.
5. O sino consulta apenas os registros do usuário autenticado.
6. “Abrir” marca como lida e direciona ao pedido correto.

## Segurança e privacidade

- Toda ação exige autenticação e CSRF.
- Leitura, abertura e arquivamento filtram por `usuario_id`.
- URLs externas ou iniciadas por `//` não são aceitas como destino.
- A visão administrativa apresenta somente métricas agregadas; não expõe o conteúdo privado de outros usuários.
- Nenhum dado pessoal adicional é armazenado.

## Evolução

Novos produtores de eventos devem chamar `criar_notificacao` e usar um tipo oficial. Push, WhatsApp, e-mail, Firebase, OneSignal e WebPush permanecem fora desta camada e desta Sprint.
