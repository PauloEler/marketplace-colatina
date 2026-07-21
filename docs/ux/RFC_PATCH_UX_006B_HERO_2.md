# RFC — PATCH UX-006B Hero 2.0

Data: 21/07/2026
Status: implementado em branch, sem merge e sem deploy

## Problema real

Com a Home compacta ativa, o Hero passou a ocupar apenas 594 px em um viewport de 1440 px. O título ficou limitado a uma coluna estreita e chegou a seis linhas, reduzindo a leitura imediata e o valor visual da fotografia de Colatina.

## Objetivo

Recuperar o impacto da primeira dobra sem alterar a arquitetura compacta, a seção Cidade Viva, os resumos, os links “Ver todos”, o backend, o banco ou a feature flag existente.

## Proposta

- aplicar o Hero 2.0 somente quando a classe `home-compact-ux006a` estiver ativa;
- usar 78% da largura útil no desktop largo;
- fixar semanticamente o título em duas linhas;
- equilibrar texto e fotografia da ponte;
- manter a busca imediatamente após o conteúdo principal;
- diferenciar o CTA primário do secundário;
- preservar o comportamento responsivo entre 320 e 1440 px.

## Limites

Nenhum bloco posterior ao Hero foi alterado. Não houve mudança em rotas, dados, autenticação, scripts ou regras de negócio.

## Reversão

O patch é autocontido e pode ser revertido por um único commit. A feature flag `HOME_CIDADE_VIVA_ENABLED` permanece inalterada e continua controlando a Home compacta.
