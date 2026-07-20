# ADR - AGREGACAO DA OPERACAO PRIMEIROS 100

## Status

Aceita para a PR Draft da Missao 003.

## Decisao

Reutilizar a coleta minimizada da Operacao Tracao e criar uma camada somente leitura em `operation_100.py`. Nao criar tabela ou alterar dominios operacionais.

O funil sera uma coorte progressiva de 30 dias. A recorrencia oficial permanece a intersecao de usuarios ativos em duas janelas consecutivas de 7 dias. Indicadores sem fonte exibem indisponibilidade em vez de zero estimado.

## Motivos

- preserva uma definicao unica de recorrencia;
- impede conversoes acima de 100% no funil;
- evita duplicacao e coleta adicional de dados;
- permite testar consultas separadamente da interface;
- mantem protegidos marketplace, pedidos e analytics dos afiliados.

## Consequencias

O painel responde o estado atual e os bloqueios mensuraveis. Convites, campanhas e receita de afiliados ainda nao podem ser confirmados automaticamente. Uma fonte futura exigira RFC e ADR proprias.

## Alternativas rejeitadas

- criar novo banco analitico: desnecessario para o volume atual;
- reconstruir recorrencia anterior a coleta: tecnicamente impossivel sem inventar dados;
- inferir receita por clique: nao possui validade comercial;
- usar um funil de volumes independentes: permitiria interpretacao enganosa.
