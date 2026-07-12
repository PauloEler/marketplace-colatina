# Relatório de rastreabilidade dos pedidos — Mercado Colatina

## Resumo técnico

Foi implementado um histórico permanente de eventos por pedido, visível somente ao comprador, ao vendedor e ao administrador. A atualização preserva a dupla confirmação já existente e registra, conforme cada ação ocorre:

- `PEDIDO_CRIADO`;
- `VENDEDOR_CONFIRMOU`;
- `ESTOQUE_RESERVADO`;
- `VENDA_MARCADA_COMO_REALIZADA`;
- `COMPRADOR_CONFIRMOU_RECEBIMENTO`;
- `PEDIDO_CONCLUIDO`;
- `PROBLEMA_RELATADO`;
- `PEDIDO_EM_ANALISE`;
- `PEDIDO_CANCELADO`;
- `ESTOQUE_DEVOLVIDO`.

Cada registro contém pedido, tipo, data e hora, usuário responsável quando houver, papel do responsável, descrição legível, dados adicionais, estado anterior e estado posterior. Eventos automáticos são identificados como ações do sistema.

O relato de problema agora exige um motivo estruturado. A descrição permanece opcional, exceto quando o motivo escolhido é `OUTRO`. O administrador vê o motivo e a descrição; comprador e vendedor veem que o pedido está em análise e o motivo, sem exposição automática do texto livre na listagem compartilhada.

## Migração segura

O projeto não utiliza uma ferramenta externa de migrações. Por isso, a migração foi incorporada ao inicializador idempotente existente em `database.py`, mantendo compatibilidade com SQLite e PostgreSQL.

A migração:

- cria a tabela `pedido_eventos` somente se ela ainda não existir;
- cria índice por pedido e data;
- adiciona as colunas de problema ao cadastro de pedidos somente se estiverem ausentes;
- não remove nem renomeia tabelas ou colunas existentes;
- não altera o status, estoque, pagamento ou confirmações de pedidos existentes;
- cria um único evento inicial `PEDIDO_CRIADO` para pedidos legados sem histórico;
- usa restrição única por pedido e tipo de evento para impedir duplicações.

O marco inicial de um pedido legado é identificado como ação do sistema e informa que o pedido existente foi incorporado ao histórico. Não são inventados eventos passados cuja data ou autoria não possam ser comprovadas.

## Integridade e concorrência

As mudanças de status, estoque e eventos são confirmadas juntas na mesma transação. Em caso de exceção, a operação executa rollback.

A confirmação do vendedor passou a usar atualização condicional do estado do pedido e reserva condicional de estoque. Isso reduz o risco de dois cliques ou requisições concorrentes reservarem mais de uma unidade. Cliques repetidos também são protegidos pela validação de status e pela unicidade dos eventos.

Relatar um problema apenas muda o pedido para `em_analise` e registra os dados do relato. Essa ação não baixa, devolve, pausa ou reativa estoque.

O cancelamento de um pedido que já tinha unidade reservada continua devolvendo exatamente uma unidade e agora registra `PEDIDO_CANCELADO` e `ESTOQUE_DEVOLVIDO`.

## Permissões e privacidade

A rota individual do histórico autoriza somente:

- o comprador do pedido;
- o vendedor do pedido;
- um administrador autenticado.

Usuários alheios recebem resposta de acesso proibido. As listagens de compras e vendas continuam filtradas pelo usuário autenticado. O texto livre do problema é exibido ao administrador, enquanto a interface compartilhada com comprador e vendedor mostra o motivo estruturado e o estado de análise.

## Testes executados

Antes da implementação:

- `python -m unittest discover -s tests -v`;
- resultado: **33 testes aprovados**.

Depois da implementação:

- compilação de `app.py`, `database.py` e dos testes;
- `python -m unittest discover -s tests -v`;
- resultado: **41 testes aprovados**.

Foram validados criação do evento inicial, confirmação do vendedor, reserva de estoque, confirmação do comprador, confirmação da venda, conclusão, obrigatoriedade do motivo, regra de `OUTRO`, eventos de problema, permissões, idempotência, pedido legado, integridade do estoque, cancelamento e devolução de unidade.

## Arquivos alterados

- `app.py` — regras, eventos, permissões, problema estruturado e transações;
- `database.py` — migração idempotente para SQLite e PostgreSQL;
- `templates/pedidos.html` — linha do tempo e formulário de problema;
- `templates/admin.html` — acesso ao histórico e detalhes para mediação;
- `templates/_pedido_timeline.html` — componente visual reutilizável;
- `templates/historico_pedido.html` — página protegida do histórico;
- `static/styles.css` — apresentação da linha do tempo e do formulário;
- `tests/test_moderacao.py` — testes de rastreabilidade, permissões e integridade;
- `RELATORIO_RASTREABILIDADE_PEDIDOS_MERCADO_COLATINA.md` — este relatório.

## Riscos encontrados e tratamento

- **Pedidos antigos sem eventos:** recebem somente um marco inicial verificável, sem simular acontecimentos passados.
- **Cliques repetidos:** validação do estado e unicidade no banco impedem repetição de eventos e nova baixa de estoque.
- **Concorrência na reserva:** atualizações condicionais impedem que a mesma solicitação seja confirmada duas vezes e que estoque zerado seja reservado.
- **Texto livre com dados pessoais:** a interface orienta a não informar senhas ou dados bancários e restringe a descrição detalhada ao painel administrativo.
- **Ambientes diferentes:** a migração foi escrita para os dois bancos já suportados pelo projeto. Os testes automatizados usam banco isolado e nunca acessam produção.

## Confirmações finais

- Nenhum banco novo foi criado para a aplicação.
- Nenhum pedido ou anúncio existente foi apagado.
- A migração é aditiva e idempotente.
- O fluxo atual de dupla confirmação foi preservado.
- A reserva, pausa, devolução e reativação segura do estoque foram preservadas.
- Avaliações, estrelas, comprovantes e integrações de WhatsApp não fazem parte desta entrega.
