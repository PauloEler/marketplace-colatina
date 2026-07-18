# RFC MX-004.1 - HOME MONETIZACAO

## Objetivo

Propor e registrar a implementacao da secao "Ofertas de Parceiros" na Home do Mercado Colatina.

## Motivacao

O Mercado Colatina precisa iniciar monetizacao sustentavel sem comprometer a experiencia principal de compra e venda local. A abordagem mais segura para esta etapa e exibir ofertas parceiras claramente identificadas, abaixo dos produtos locais.

## Decisoes tomadas

- Implementar apenas a secao "Ofertas de Parceiros".
- Nao implementar noticias, Colatina Agora, patrocinadores reais, APIs externas ou banco novo.
- Exibir 6 cards para permitir grade/carrossel com 4 cards visiveis em desktop e 2 em mobile.
- Cada card contem imagem, titulo, preco e botao "Ver oferta".
- Inserir o aviso: "Algumas ofertas desta seção são exibidas por parceiros comerciais. Ao clicar, você será direcionado ao site do parceiro."
- Usar navegacao manual por botoes e rotacao automatica em JavaScript.
- Respeitar `prefers-reduced-motion` para usuarios que reduzem movimento.

## Impacto esperado

- Receita complementar por afiliados.
- Melhor organizacao da divulgacao de parceiros.
- Maior clareza para visitantes sobre o que e Mercado Colatina e o que e conteudo de parceiro.

## Limitacoes

- Nao ha gestao administrativa dos cards.
- Nao ha relatorio de cliques nesta sprint.
- Nao ha validacao automatica de preco em site parceiro.
- Nao ha integracao com redes de afiliados alem do link configurado.

## Proximos passos

- Definir politica comercial para parceiros.
- Adicionar medicao de cliques com privacidade.
- Criar processo de revisao periodica das ofertas.
- Avaliar variacoes de layout apos dados reais de uso.
