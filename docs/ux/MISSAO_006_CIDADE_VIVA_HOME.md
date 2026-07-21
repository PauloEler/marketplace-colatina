# Missão 006 — Cidade Viva

## Problema real

A Home acumulou blocos importantes ao longo das missões anteriores, mas passou a exigir uma rolagem longa e repetitiva, especialmente no celular. Isso dificulta a descoberta rápida de produtos, empresas e necessidades reais da cidade.

## Objetivo

Testar uma composição vertical mais dinâmica sem apagar anúncios, alterar regras de negócio ou comprometer a Home atual. A primeira dobra, a busca, o Encontre Quem Resolve, as categorias e os principais caminhos comerciais permanecem preservados.

## Solução reversível

A composição é ativada exclusivamente por `HOME_CIDADE_VIVA_ENABLED=true`. O valor padrão é `false`.

- flag desligada: a composição anterior é renderizada integralmente;
- flag ligada: produtos e empresas recebem limites configuráveis, dados reais formam o bloco Cidade em movimento e anúncios seguintes aparecem como novidades;
- `?todos=1`: restaura a composição integral na própria requisição e permite ver todos os produtos e empresas;
- nenhuma tabela, dado, rota, pedido ou dashboard foi alterado.

O limite da vitrine é controlado por `HOME_CIDADE_VIVA_PRODUCT_LIMIT`, com padrão `4` e faixa segura entre `3` e `8`.

## Composição ativa

1. Hero e busca.
2. Encontre Quem Resolve.
3. Categorias.
4. Produtos em destaque, com limite e acesso a “Ver todos”.
5. Cidade em movimento, somente com métricas reais e valores maiores que zero.
6. Lojas em destaque.
7. Anúncios recentes, sem repetir os produtos já exibidos.
8. Ofertas e empresas parceiras.
9. Rodapé.

Blocos institucionais secundários continuam intactos no código e na Home anterior. No protótipo ativo, são substituídos por uma composição direta para evitar repetição. A reversão da flag os reapresenta imediatamente.

## Dados de Cidade em movimento

As métricas são calculadas no momento da requisição:

- anúncios ativos e com estoque;
- empresas ativas que possuem anúncios ativos;
- necessidades com status `aberto`.

Indicadores com valor zero são omitidos. Não existem valores estimados, simulados ou preenchidos manualmente.

## Problema da cidade resolvido

O morador consegue perceber em menos tempo o que está disponível e acontecendo no Mercado Colatina, sem atravessar várias fileiras visualmente semelhantes. Isso melhora a descoberta do comércio local e das necessidades que aguardam atendimento.
