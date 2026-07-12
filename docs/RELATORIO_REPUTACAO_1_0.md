# Mercado Colatina — Relatório da Reputação 1.0

## Resumo técnico

Foi implementada a primeira versão da reputação automática para vendedor e comprador. Os indicadores são calculados a partir dos usuários, pedidos e eventos já existentes; nenhum contador de reputação pode ser informado ou alterado pelo usuário.

A conta do usuário passou a mostrar os indicadores completos dos dois papéis. O painel do vendedor também exibe a reputação completa de venda. O administrador pode abrir a reputação completa de qualquer usuário a partir da lista administrativa. No anúncio público aparecem apenas membro desde, vendas concluídas, taxa de conclusão e, quando ativado futuramente, o selo de loja verificada.

## Regras de cálculo

- Vendas, compras e pedidos concluídos: pedidos com status `concluido`.
- Cancelamentos: pedidos com status `cancelado` ou `recusado`.
- Em análise: pedidos com status `em_analise`.
- Taxa de conclusão: concluídos divididos pelos pedidos finalizados, considerando concluídos, cancelados e recusados. Pedidos ainda abertos ou em análise não reduzem a taxa.
- Tempo médio do vendedor: intervalo entre a criação e o evento de conclusão; para registros legados sem esse evento, usa-se `atualizado_em` como compatibilidade.
- Tempo médio do comprador: intervalo entre a criação do pedido e `comprador_confirmou_em`.
- Último acesso: atualizado somente após login válido.

## Segurança e permissões

- O usuário acessa sua reputação completa somente dentro de `Minha conta`.
- A rota de reputação de outro usuário é exclusiva do administrador.
- O anúncio público não expõe último acesso, cancelamentos, pedidos em análise ou tempos médios.
- Campos enviados manualmente com tentativas de alterar reputação são ignorados.
- Não foi criado controle público ou do usuário para alterar `loja_verificada`.

## Performance

- O cálculo compartilhado carrega os pedidos necessários em uma única consulta, evitando uma consulta por indicador.
- O painel do vendedor reutiliza a coleção de pedidos que já era carregada para os cartões e estatísticas.
- Os indicadores não são persistidos como contadores, eliminando risco de divergência com os pedidos reais.

## Migração segura

A inicialização existente recebeu uma migração aditiva e idempotente, compatível com SQLite e PostgreSQL:

- `usuarios.ultimo_acesso_em TIMESTAMP`, inicialmente nulo para usuários antigos;
- `usuarios.loja_verificada INTEGER NOT NULL DEFAULT 0`.

Não houve criação de banco, remoção de coluna, alteração de pedido ou reescrita de dados existentes. Usuários antigos permanecem compatíveis e passam a ter último acesso registrado no próximo login válido.

## Arquivos alterados

- `app.py`
- `database.py`
- `static/styles.css`
- `templates/_reputacao_completa.html`
- `templates/admin.html`
- `templates/anuncio.html`
- `templates/minha_conta.html`
- `templates/painel_vendedor.html`
- `templates/reputacao_usuario.html`
- `tests/test_moderacao.py`
- `RELATORIO_REPUTACAO_1_0.md`

## Testes executados

Comando: `python -m unittest discover -s tests -v`

Resultado final: **59 testes aprovados de 59**.

Foram adicionados testes para:

- reputação automática do vendedor;
- reputação automática do comprador;
- taxa de conclusão;
- tempos médios;
- registro de último acesso apenas em login válido;
- visualização completa pelo próprio usuário;
- visualização administrativa;
- bloqueio para usuário comum consultar outro usuário;
- exposição pública limitada;
- impossibilidade de edição da reputação.

Os testes anteriores de pedidos, estoque, reserva, devolução, dupla confirmação e rastreabilidade continuam aprovados.

## Problemas e riscos encontrados

- Usuários antigos não possuem histórico de último acesso anterior à implantação; a interface informa que ele ainda não foi registrado até o próximo login.
- Pedidos legados concluídos sem evento `PEDIDO_CONCLUIDO` usam a data de atualização como aproximação do tempo de conclusão.
- O campo de loja verificada está preparado com valor padrão desativado, mas não possui nesta missão processo administrativo de verificação.

## Preservação dos fluxos existentes

- Nenhuma rota de criação, confirmação, conclusão ou cancelamento de pedido foi alterada.
- Nenhuma regra de estoque, reserva ou devolução foi alterada.
- A dupla confirmação permaneceu intacta.
- A linha do tempo e seus eventos permaneceram intactos.

## Sugestões futuras

- Definir critérios e processo administrativo auditável para ativar loja verificada.
- Criar uma página pública de loja, caso seja desejável reunir anúncios e reputação pública do vendedor.
- Avaliar atualização periódica das métricas em cache somente quando o volume justificar, mantendo os pedidos como fonte oficial.
