# Relatório de publicação — Afiliado Ulanzi MA09

Data: 29/07/2026

## Objetivo

Publicar na seção **Ofertas de Parceiros** o primeiro produto específico do
piloto de afiliados, sem confundir a oferta externa com anúncio do Marketplace.

## Configuração oficial

- Produto: Tripé para celular Ulanzi MA09 com controle remoto.
- Catálogo: `MLB36175790`.
- Anúncio selecionado: `MLB6191329464`.
- Parceiro: Mercado Livre.
- Link oficial: `https://meli.la/2gSYwQb`.
- Etiqueta: `neo01mercadocolatina`.
- Canal autorizado: `https://mercadocolatina.com.br/`.
- Comissão exibida na geração do link: 5%, sujeita às regras do programa.

## Transparência

O produto ainda não foi testado pelo Mercado Colatina. Essa condição aparece
diretamente no card. A publicação não promete preço, estoque, desempenho ou
resultado. O clique abre o site do parceiro em nova guia.

## Imagem

Foi criada uma imagem ilustrativa original, sem copiar fotografia comercial do
anúncio e sem usar logotipos, marcas gráficas ou identidade do Mercado Livre.

## Arquitetura

A oferta foi adicionada à configuração centralizada em `partner_offers.py`, com:

- URL oficial individual;
- fallback direto para a página do produto;
- identificador único `tripe-ulanzi-ma09`;
- variável opcional `OFERTA_PARCEIRO_07_URL`;
- imagem, título e aviso próprios.

O carrossel, o layout, o CSS e as seis ofertas anteriores foram preservados.

## Validação prevista

- sete ofertas cadastradas;
- sete URLs oficiais únicas e não vazias;
- imagem, título e botão usando a mesma URL do card;
- `target="_blank"`;
- `rel="sponsored noopener noreferrer"`;
- evento de analytics identificado como `tripe-ulanzi-ma09`;
- suíte completa, Ruff e verificação de diferenças aprovados;
- validação final em produção sem clicar no próprio link de afiliado.

## Resultado de publicação

A preencher após CI, merge, deploy e validação em produção.
