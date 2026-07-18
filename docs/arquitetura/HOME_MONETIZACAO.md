# HOME MONETIZACAO

## Objetivo

Descrever a arquitetura da primeira evolucao de monetizacao da Home do Mercado Colatina, mantendo o marketplace como protagonista absoluto.

## Motivacao

A Home ja concentra busca, categorias e produtos locais. A secao "Ofertas de Parceiros" cria um ponto de receita complementar com afiliados sem disputar prioridade com os anuncios do Mercado Colatina.

## Decisoes tomadas

- A secao foi posicionada logo abaixo de "Produtos em destaque".
- Os produtos locais continuam aparecendo antes de qualquer oferta de parceiro.
- As ofertas de parceiros ficam em constantes no `app.py`, sem novo banco de dados.
- As imagens sao SVGs locais e leves, servidas pelo proprio projeto.
- O carrossel usa CSS com scroll snap e JavaScript pequeno para navegacao manual e rotacao automatica.
- Todos os links de parceiro usam `rel="sponsored nofollow"` e abrem em nova aba.
- As imagens usam `loading="lazy"` e `decoding="async"`.

## Impacto esperado

- Criar uma area inicial de receita por afiliados.
- Aumentar o tempo de permanencia na Home.
- Preservar a confianca do usuario por meio de transparencia clara.
- Manter performance alta por nao depender de API externa.

## Limitacoes

- As ofertas sao estaticas nesta sprint.
- Nao ha captura automatica de ofertas.
- Nao ha integracao com API de afiliados.
- Os precos exibidos sao chamadas comerciais de referencia e devem ser revisados antes de campanhas reais.

## Proximos passos

- Substituir ofertas estaticas por ofertas aprovadas comercialmente.
- Medir cliques em ofertas parceiras.
- Avaliar novos parceiros sem afetar a vitrine local.
- Criar rotina editorial para revisao dos cards.
