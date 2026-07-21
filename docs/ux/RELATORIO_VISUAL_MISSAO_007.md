# Relatório visual — Missão 007 Home 2.0

## Resultado

A primeira dobra passou a apresentar um foco por bloco: inspiração, busca e
conexão com empresas. A transição para Cidade Viva permanece no ponto original
da Home compacta.

## Validação por largura

| Largura | Hero | Título | Busca | Serviço | Overflow |
|---|---|---|---|---|---|
| 1440 px | texto e foto lado a lado | 2 linhas | faixa horizontal | CTA à direita | não |
| 1024 px | texto e foto lado a lado | 2 linhas | faixa em duas linhas | CTA à direita | não |
| 768 px | texto sobre foto | 2 linhas | controles compactos | faixa compacta | não |
| 390 px | texto sobre foto | 2 linhas | empilhada | empilhada | não |
| 320 px | texto sobre foto | 2 linhas | empilhada | empilhada | não |

Em todas as larguras a primeira dobra contém somente um logo, a busca não está
dentro do Hero e o compartilhamento não compete com os CTAs.

## Evidências

- Antes: `docs/ux/evidencias/missao_007/antes/`
- Depois: `docs/ux/evidencias/missao_007/depois/`
- Comparativos lado a lado: `docs/ux/evidencias/missao_007/comparativo/`
- Flag desligada: `docs/ux/evidencias/missao_007/reversao/`

Foram registradas as cinco larguras solicitadas. O console ficou sem erros e a
estrutura acessível apresenta regiões, títulos, rótulos e controles nativos.

## Reversão visual

As imagens da Home publicada antes da mudança e depois do desligamento da flag
foram comparadas pixel a pixel. Resultado: `0,0000%` de pixels diferentes nas
cinco larguras.

## Observação

As capturas locais usam os dados disponíveis no banco de desenvolvimento. A
ausência eventual de conteúdo em Cidade Viva é de dados, não de layout; o
componente original e seus testes foram preservados.
