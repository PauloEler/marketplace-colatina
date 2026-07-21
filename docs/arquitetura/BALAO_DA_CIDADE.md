# Balão da Cidade

## Problema real

A Home 2.0 organiza os caminhos da plataforma, mas a área Cidade Viva não possuía um ponto de orientação curto e permanente dentro do próprio layout. O visitante precisava interpretar blocos separados para decidir onde agir.

## Objetivo

Oferecer uma orientação contextual, não invasiva e acessível, aproximando o visitante de empresas, produtos, necessidades e ofertas locais.

## Arquitetura

O Balão da Cidade é renderizado pelo servidor no template da Home e depende de três condições encadeadas:

1. `HOME_CIDADE_VIVA_ENABLED=true`;
2. `HOME_2_ENABLED=true`;
3. `HOME_CITY_BALLOON_ENABLED=true`.

A nova flag é `false` por padrão. O componente usa `aside`, navegação semântica e links reais já existentes. Não há JavaScript, popup, posição fixa, banco novo ou integração externa.

Quando métricas reais existem, até duas são reutilizadas no painel. Quando não existem, a área Cidade Viva apresenta somente caminhos de ação e informa explicitamente que não usa números estimados.

## Responsividade

- 1440 e 1024 px: Cidade Viva à esquerda e painel vertical à direita.
- 768 px: painel em faixa horizontal abaixo da Cidade Viva.
- 390 e 320 px: painel em card comum de largura total.

Os cards resumidos usam largura máxima comum de 80 rem, raio e espaçamento compartilhados. O rodapé mantém todos os links, mas reduz ponte, margens e espaçamentos; no mobile, a navegação institucional usa duas colunas.

## Limitações

O painel não busca conteúdo externo e não inventa dados. Sua evolução deverá continuar usando apenas informações confirmadas da plataforma.
