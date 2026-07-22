# Relatório documental — Missão 009

## Resultado

A estratégia “Compre Perto de Você” foi documentada sem implementação. A proposta mantém o Mercado Colatina como Marketplace e define a Home apenas como entrada temática.

## Entregue

- documento estratégico;
- RFC proposta;
- ADR proposta;
- regras de neutralidade;
- governança de temas e sazonalidade;
- funil de medição;
- critérios de sucesso;
- plano de reversão;
- capturas da Home atual;
- protótipos não executáveis desktop e mobile.

## Decisões principais propostas

1. seção após Cidade Viva e antes de Produtos em destaque;
2. nenhum link direto para empresa;
3. resultados agregados pelo Marketplace;
4. laboratório sem privilégio comercial;
5. tema “remédio” condicionado a revisão;
6. feature flag `HOME_COMPRE_PERTO_ENABLED=false`;
7. implementação somente em nova autorização.

## Arquivos de aplicação

Nenhum arquivo de aplicação foi alterado. Não houve mudança em backend, banco, Home, UX, Marketplace, produtos, pedidos, empresas, Cidade Viva ou Encontre Quem Resolve.

## Situação

- documentação: concluída;
- protótipo: concluído;
- implementação: não iniciada;
- merge: não realizado;
- deploy: não realizado;
- decisão pendente: aprovação estratégica e visual da Diretoria.

## Atualização de 22/07/2026

A Diretoria aprovou formalmente a documentação e autorizou a implementação
reversível da Fase 1 com quatro temas: Mercadinhos, Bares, Conveniências e
Padarias. O código permanece em PR Draft, sem merge e sem deploy, aguardando
auditoria visual.
