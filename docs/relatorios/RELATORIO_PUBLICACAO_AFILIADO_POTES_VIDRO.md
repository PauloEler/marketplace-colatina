# Relatório de publicação — Kit de Potes de Vidro

## Produto selecionado

- Produto: Kit com 10 potes herméticos de vidro de 640 ml
- Catálogo Mercado Livre: `MLB53222689`
- Anúncio observado: `MLB5574851656`
- Link oficial de afiliado: `https://meli.la/1VhuyQ1`
- Etiqueta exclusiva: `oferta05potesvidro`

## Critérios observados

- Mais de 250 mil unidades vendidas.
- Avaliação 4,9 de 5.
- 58.992 opiniões.
- Primeiro lugar na categoria de recipientes para armazenamento de alimentos.
- Comissão exibida no catálogo de afiliados: 12%, sujeita às regras do programa.

Os indicadores foram observados no momento da seleção e podem mudar no
Mercado Livre.

## Transparência

- O preço não é fixado no card.
- O visitante consulta preço, estoque, frete e condições diretamente no
  parceiro.
- O link abre em nova guia com identificação de conteúdo patrocinado.
- Nenhuma compra vinculada à própria conta foi realizada.

## Imagem

Foi criada uma imagem ilustrativa original, sem logotipos, marcas, preço ou
fotografia comercial copiada:

`static/oferta-parceiro-11-potes-vidro-premium.webp`

## Arquitetura

- A oferta foi adicionada à configuração centralizada em `partner_offers.py`.
- A chave de substituição é `OFERTA_PARCEIRO_11_URL`.
- O fallback aponta para a página oficial do catálogo.
- O identificador analítico é `kit-potes-vidro-hermeticos`.

## Validação prevista

- Onze ofertas com URLs oficiais únicas e não vazias.
- Imagem, título e botão vinculados ao mesmo destino.
- `target="_blank"`.
- `rel="sponsored noopener noreferrer"`.
- Suíte completa, Ruff e verificação do diff.
- Validação final em produção após o deploy.
