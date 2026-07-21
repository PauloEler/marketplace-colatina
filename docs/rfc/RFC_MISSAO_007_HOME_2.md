# RFC — Missão 007 Home 2.0

## Estado

Implementada em PR Draft; sem merge e sem deploy.

## Problema da cidade que resolve

Moradores precisam identificar rapidamente se desejam comprar, anunciar,
buscar algo específico ou pedir ajuda a uma empresa local. A primeira dobra
anterior apresentava esses caminhos com funções sobrepostas.

## Proposta

Criar uma variante reversível da primeira dobra, mantendo todas as funções e
separando-as em três blocos antes da Cidade Viva.

## Decisões

- Um único logo permanece no cabeçalho.
- O Hero contém apenas mensagem, panorama e dois CTAs.
- A busca continua sendo um formulário GET para `/`.
- Encontre Quem Resolve conserva sua rota existente.
- A Cidade Viva e todas as seções posteriores não são modificadas.
- A variante é controlada por `HOME_2_ENABLED`, desativada por padrão.
- Estilos são escopados e a reversão também pode ocorrer por um único commit.

## Alternativas consideradas

Editar diretamente a Home publicada foi rejeitado porque impediria comparação
segura e reversão imediata. Criar novas rotas foi descartado por ampliar o
escopo e duplicar navegação.

## Impacto esperado

Leitura imediata, menos competição entre ações e maior interação com os quatro
caminhos principais sem aumentar complexidade operacional.

## Limitações

Esta missão não adiciona instrumentação nova nem define vencedor de teste A/B.
A ativação e a medição dependem de aprovação visual e publicação posterior.
