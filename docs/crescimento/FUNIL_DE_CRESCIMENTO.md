# FUNIL DE CRESCIMENTO

## Objetivo

Mostrar onde a ativacao dos usuarios deixa de avancar, sem misturar volumes incompativeis nem transformar visitas anonimas em pessoas identificadas.

## Janela e coorte

O funil usa os ultimos 30 dias. Visitantes sao o total agregado de visitas coletadas por dia. A partir de Cadastro, a leitura e uma coorte progressiva de contas nao administrativas criadas na janela:

1. Visitante: visitas agregadas nos ultimos 30 dias.
2. Cadastro: contas criadas na mesma janela.
3. Primeiro anuncio: contas da coorte com anuncio.
4. Primeiro pedido: contas da etapa anterior envolvidas em pedido como comprador ou vendedor.
5. Primeira venda: contas da etapa anterior que concluiram venda como vendedor.
6. Usuario recorrente: contas da etapa anterior ativas nas duas janelas semanais consecutivas.

## Conversao

Cada percentual usa a etapa imediatamente anterior como denominador. Quando o denominador e zero, o painel mostra `Aguardando base`. Os conjuntos sao progressivos, portanto a conversao nao ultrapassa 100%.

## Limitacoes

- visitas anonimas nao possuem identidade nem historico individual;
- a base de atividade comeca na publicacao da Operacao Tracao;
- o funil mede uma jornada progressiva de ativacao e nao todas as jornadas possiveis de compradores;
- nenhuma identificacao pessoal adicional e coletada.
