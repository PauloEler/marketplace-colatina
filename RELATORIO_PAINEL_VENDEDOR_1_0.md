# Relatório — Painel Profissional do Vendedor 1.0

## Resumo técnico

Foi criada a área `Minha loja`, acessível em `/painel-vendedor`, para transformar os dados já existentes do vendedor em uma visão organizada de gestão.

O painel apresenta:

- resumo de anúncios ativos, pausados, esgotados e com estoque baixo;
- pedidos aguardando ação e pedidos em análise;
- vendas concluídas e quantidade total vendida;
- filtros rápidos para anúncios;
- anúncios mais vistos, sem visualizações e recentes;
- pedidos separados por etapa, com acesso ao histórico completo;
- estatísticas de anúncios, vendas, pedidos, análise, taxa de conclusão e tempo médio;
- indicadores internos de histórico da loja, sem estrelas ou avaliação pública;
- layout baseado em cartões e adaptado para celular.

O painel é somente leitura. Nenhuma ação nova altera pedido, anúncio ou estoque. Os botões existentes apenas encaminham o vendedor para as telas já utilizadas pelo projeto.

## Segurança e isolamento

Todas as consultas utilizam o identificador do usuário autenticado como vendedor. O painel carrega somente:

- anúncios em que `usuario_id` pertence ao usuário atual;
- pedidos em que `vendedor_id` pertence ao usuário atual;
- perfil do próprio usuário.

Usuários sem login são redirecionados para a tela de acesso. Os testes confirmam que um vendedor não visualiza anúncios ou informações comerciais pertencentes a outro vendedor.

## Performance

O painel utiliza três leituras principais:

1. perfil do vendedor;
2. anúncios do vendedor;
3. pedidos recebidos pelo vendedor, já acompanhados do produto, comprador e data de conclusão.

Os totais, grupos, filtros e estatísticas são calculados em memória a partir desses resultados. Não há consultas individuais por cartão ou por indicador.

## Migrações

Nenhuma migração foi necessária.

- Nenhuma tabela foi criada.
- Nenhuma coluna foi adicionada ou removida.
- Nenhum banco de dados novo foi criado.
- Nenhum dado existente foi modificado pelo painel.

## Arquivos alterados

- `app.py` — rota protegida, consultas e cálculos do painel;
- `templates/painel_vendedor.html` — interface completa da loja;
- `templates/base.html` — acesso `Minha loja` nos menus desktop e celular;
- `static/styles.css` — cartões, filtros, grupos de pedidos e responsividade;
- `tests/test_moderacao.py` — testes do painel;
- `RELATORIO_PAINEL_VENDEDOR_1_0.md` — este relatório.

## Testes executados

Antes da implementação:

- comando: `python -m unittest discover -s tests -v`;
- resultado: **41 testes aprovados**.

Depois da implementação:

- compilação de `app.py` e da suíte de testes;
- comando: `python -m unittest discover -s tests -v`;
- resultado: **47 testes aprovados**.

Os novos testes validam:

- carregamento e proteção do dashboard;
- isolamento entre vendedores;
- resumo e estatísticas calculadas;
- agrupamento de pedidos e links de histórico;
- filtros rápidos de anúncios;
- estrutura responsiva sem tabelas no painel.

Todos os testes anteriores de estoque, pedidos, dupla confirmação, rastreabilidade, moderação, e-mail e segurança continuam aprovados.

## Problemas e decisões encontradas

- Cada pedido atual representa a reserva de uma unidade. Por isso, a quantidade total vendida corresponde ao número de pedidos concluídos.
- Para pedidos novos, o tempo de conclusão usa o evento `PEDIDO_CONCLUIDO`. Em pedidos legados sem esse evento, o cálculo utiliza `atualizado_em` como aproximação segura.
- Um pedido confirmado permanece no grupo `Aguardando comprador`; o indicador superior também avisa o vendedor quando ainda falta registrar a venda.
- O limite de estoque baixo foi definido como até duas unidades disponíveis e aparece explicado no próprio cartão.

## Sugestões futuras

Sem fazer parte desta entrega, o painel está preparado para evoluções posteriores como:

- período selecionável para estatísticas;
- gráfico simples de vendas por mês;
- ordenação adicional por estoque;
- paginação quando houver grande volume de anúncios ou pedidos;
- indicadores públicos de vendedor verificado, após definição das regras de moderação.

## Confirmações

- O fluxo de pedidos não foi alterado.
- O fluxo de estoque não foi alterado.
- A dupla confirmação não foi alterada.
- A rastreabilidade não foi alterada.
- Nenhuma avaliação por estrelas foi implementada.
- Nenhuma publicação no GitHub ou Render foi realizada nesta missão.
