# Relatório de publicação — Afiliado Air Fryer Oven WAP

Data: 29/07/2026

## Objetivo

Adicionar à seção **Ofertas de Parceiros** uma terceira oferta de produto
específico, com rastreamento independente e apresentação transparente.

## Configuração oficial

- Produto: Fritadeira Elétrica Air Fryer Oven Black Inox WAP WAOD2.
- Catálogo: `MLB43435820`.
- Anúncio observado na seleção: `MLB6253142964`.
- Parceiro: Mercado Livre.
- Link oficial: `https://meli.la/1K1uUf6`.
- Etiqueta: `oferta03airfryerwap`.
- Canal autorizado: `https://mercadocolatina.com.br/`.
- Comissão exibida no catálogo de afiliados: 5%, sujeita às regras do programa.

## Critérios de seleção

No momento da auditoria, a página informava mais de 10 mil unidades vendidas,
avaliação 4,9 de 5 e 8.859 opiniões. Esses dados foram usados somente para
selecionar o candidato e podem mudar. O card não fixa preço ou estoque.

## Transparência

O card orienta o visitante a conferir preço e condições no site parceiro. O
clique abre o parceiro em nova guia com
`rel="sponsored noopener noreferrer"`.

## Imagem

Foi criada uma fotografia ilustrativa original de uma air fryer oven preta em
uma cozinha contemporânea. A imagem não copia a fotografia comercial, não usa
logotipo, embalagem, preço ou identidade do Mercado Livre.

## Arquitetura

A oferta foi adicionada à configuração centralizada em `partner_offers.py`, com:

- URL oficial individual;
- fallback direto para a página do produto;
- identificador único `airfryer-wap-waod2`;
- variável opcional `OFERTA_PARCEIRO_09_URL`;
- imagem, título e orientação próprios.

O card foi posicionado logo após Ulanzi e JBL, ficando entre os três produtos
específicos visíveis no resumo compacto da Home. O layout, o CSS, o carrossel,
o analytics e as ofertas anteriores foram preservados.

## Validação prevista

- nove ofertas cadastradas;
- nove URLs oficiais únicas e não vazias;
- imagem, título e botão usando a mesma URL do card;
- abertura em nova guia;
- atributo patrocinado preservado;
- analytics identificado como `airfryer-wap-waod2`;
- suíte completa, Ruff e verificação de diferenças aprovados;
- validação final em produção sem clicar no próprio link de afiliado.

## Resultado de publicação

A preencher após CI, merge, deploy e validação em produção.
