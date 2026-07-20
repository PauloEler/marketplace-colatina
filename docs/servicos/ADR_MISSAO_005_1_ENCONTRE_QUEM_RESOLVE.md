# ADR — Missão 005 / Sprint 5.1

## Decisão

Adotar um domínio e uma tabela próprios para necessidades de serviços, com formulário público progressivo de quatro passos e mural de leitura pública. O contato será aberto exclusivamente a contas com loja cadastrada ou a administradores.

## Motivos

1. O usuário não precisa conhecer categorias para pedir ajuda.
2. A publicação sem cadastro reduz atrito e atende à meta operacional de rapidez.
3. O isolamento evita misturar uma necessidade de serviço com anúncio ou pedido comercial existente.
4. A liberação protegida do WhatsApp equilibra rapidez de resposta e privacidade.
5. JavaScript é uma melhoria progressiva, não uma dependência da publicação.

## Alternativas rejeitadas

- transformar a necessidade em anúncio: mistura intenção de compra com oferta;
- publicar o WhatsApp no mural: expõe dado pessoal;
- exigir cadastro antes da descrição: aumenta abandono;
- usar IA para classificar: amplia custo, dependência e escopo antes de validar utilidade.

## Consequências

O MVP exige nova tabela e duas páginas, mas não altera regras do marketplace. Moderação, encerramento, bloqueios avançados e tempo até resposta deverão ser avaliados com dados reais.
