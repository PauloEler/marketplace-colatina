# KPIs da Operação Tração

| Frente | KPI | Fórmula / fonte | Janela | Limite conhecido |
|---|---|---|---|---|
| Aquisição | Novos usuários | contas não administrativas criadas | 7 dias | não mede visitante anônimo |
| Aquisição | Usuários recorrentes | ativos nesta semana ∩ ativos na semana anterior | 7 + 7 dias | inicia na publicação |
| Aquisição | Retorno semanal | recorrentes / ativos na semana anterior | semanal | aguarda base anterior |
| Aquisição | Origem | visitas por categoria agregada | 7 dias | UTM/referrer bruto não é retido |
| Empresas | Cadastradas | contas ativas com nome de loja | atual | não equivale a empresa verificada |
| Empresas | Parceiras | parceiros não-placeholder publicados | atual | placeholders não contam |
| Empresas | Ativas | lojas com anúncio ativo | atual | empresa convidada ainda sem fonte |
| Marketplace | Anúncios ativos | anúncios ativos e não excluídos | atual | — |
| Marketplace | Pedidos | pedidos criados | 7 e 30 dias | — |
| Marketplace | Resposta média | pedido criado → confirmação do vendedor | 30 dias | aguarda evento observado |
| Marketplace | Conversão | pedidos concluídos / pedidos | 30 dias | mede fluxo interno |
| Marketplace | Receita | comissão de pedidos com pagamento aprovado | acumulada | depende do status oficial do pagamento |
| Comunidade | Participação | sugestões criadas | 7 dias | nome é opcional |
| Comunidade | Implementadas | sugestões com status implementada | atual | depende da curadoria administrativa |
| Afiliados | CTR | cliques / impressões | 30 dias | eventos anônimos internos |
| Afiliados | Receita | informação oficial do parceiro | — | indisponível nesta versão |

## Interpretação

Zero é um valor medido. “Aguardando base” e “não mensurado” significam que a fonte ainda não permite uma conclusão. Esses estados não podem ser convertidos artificialmente em zero.
