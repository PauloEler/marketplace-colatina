# Relatório de publicação — Parafusadeira WAP

## Produto selecionado

- Produto: Parafusadeira e Furadeira a Bateria WAP BPF 12K3.2 com maleta
- Catálogo Mercado Livre: `MLB47815092`
- Anúncio observado: `MLB5665826874`
- Link oficial de afiliado: `https://meli.la/2oKG2qM`
- Etiqueta exclusiva: `oferta04parafusadeirawap`

## Critérios observados

- Mais de 10 mil unidades vendidas.
- Avaliação 4,8 de 5.
- Mais de 11 mil opiniões.
- Produto de categoria diferente das três ofertas específicas anteriores.

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

`static/oferta-parceiro-10-parafusadeira-wap-premium.webp`

## Arquitetura

- A oferta foi adicionada à configuração centralizada em `partner_offers.py`.
- A chave de substituição é `OFERTA_PARCEIRO_10_URL`.
- O fallback aponta para a página oficial do catálogo.
- O identificador analítico é `parafusadeira-wap-12k32`.

## Validação prevista

- URL oficial única e não vazia.
- Imagem, título e botão vinculados ao mesmo destino.
- `target="_blank"`.
- `rel="sponsored noopener noreferrer"`.
- Suíte completa, Ruff e verificação do diff.
- Validação final em produção após o deploy.

