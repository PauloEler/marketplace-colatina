# Relatório de publicação — Afiliado JBL Tune 520BT

Data: 29/07/2026

## Objetivo

Adicionar à seção **Ofertas de Parceiros** uma segunda oferta de produto
específico, mantendo transparência, rastreamento independente e separação do
Marketplace local.

## Configuração oficial

- Produto: Fone de ouvido JBL Tune 520BT, cor azul.
- Catálogo: `MLB52695692`.
- Anúncio observado na geração: `MLB6620112834`.
- Parceiro: Mercado Livre.
- Link oficial: `https://meli.la/2uTaby6`.
- ID de produto compartilhável: `GU4PCP-DG23`.
- Etiqueta: `oferta02jbl520bt`.
- Canal autorizado: `https://mercadocolatina.com.br/`.
- Comissão exibida na geração do link: 5%, sujeita às regras do programa.

## Critérios de seleção

No momento da auditoria, a página informava mais de mil unidades vendidas,
avaliação 4,9 de 5 e 1.746 opiniões. Esses dados serviram apenas para selecionar
o candidato e podem mudar. O card não promete preço, estoque ou desempenho.

## Transparência

O produto ainda não foi testado pelo Mercado Colatina. Essa condição aparece
diretamente no card. O clique abre o site do parceiro em nova guia, com
`rel="sponsored noopener noreferrer"`.

## Imagem

Foi criada uma imagem ilustrativa original de um fone sem fio azul. Ela não
copia a fotografia comercial do anúncio e não usa logotipo, embalagem, preço
ou identidade visual do Mercado Livre.

## Arquitetura

A oferta foi adicionada à configuração centralizada em `partner_offers.py`, com:

- URL oficial individual;
- fallback direto para a página do produto;
- identificador único `fone-jbl-tune-520bt`;
- variável opcional `OFERTA_PARCEIRO_08_URL`;
- imagem, título e aviso próprios.

O card foi posicionado logo após o Ulanzi MA09 para ficar visível no resumo
compacto da Home. O layout, o carrossel, o CSS e as ofertas anteriores foram
preservados.

## Validação prevista

- oito ofertas cadastradas;
- oito URLs oficiais únicas e não vazias;
- imagem, título e botão usando a mesma URL do card;
- abertura em nova guia;
- atributo patrocinado preservado;
- evento de analytics identificado como `fone-jbl-tune-520bt`;
- suíte completa, Ruff e verificação de diferenças aprovados;
- validação final em produção sem clicar no próprio link de afiliado.

## Resultado de publicação

A preencher após CI, merge, deploy e validação em produção.
