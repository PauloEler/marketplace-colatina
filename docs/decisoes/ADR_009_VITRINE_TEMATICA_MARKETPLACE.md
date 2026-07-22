# ADR 009 — Vitrine temática com destino obrigatório no Marketplace

**Status:** proposta, ainda não aprovada
**Data:** 22/07/2026

## Contexto

O Mercado Colatina precisa aumentar a entrada no Marketplace a partir da Home sem perder sua essência, duplicar categorias ou favorecer empresas do laboratório.

## Decisão proposta

Adotar uma vitrine temática na Home, orientada por necessidades cotidianas, com as seguintes invariantes:

1. cada tema aponta exclusivamente para uma listagem agregada do Marketplace;
2. nenhum tema aponta diretamente para empresa ou anúncio individual;
3. elegibilidade depende de termos/categorias objetivos;
4. a ordenação continua pertencendo ao Marketplace;
5. a rotação é editorial e não altera a elegibilidade das empresas;
6. a funcionalidade nasce desligada por feature flag;
7. qualquer implementação ocorrerá em autorização e commit separados.

## Consequências positivas

- linguagem mais próxima do cotidiano;
- descoberta de múltiplos comerciantes;
- novo ponto de entrada sem novo canal de venda;
- teste reversível;
- mensuração clara do tráfego Home → Marketplace.

## Consequências e custos

- exige governança editorial dos temas;
- exige validação de diversidade e estado vazio;
- exige Analytics confiável antes da avaliação;
- temas regulados precisam de revisão específica;
- o componente ocupa espaço adicional na Home.

## Opções rejeitadas

- card de loja específica;
- catálogo paralelo na Home;
- promoção automática baseada em pagamento;
- rotação agressiva ou personalização individual;
- criação imediata sem linha de base.

## Reversibilidade

`HOME_COMPRE_PERTO_ENABLED=false` por padrão. Desligar a flag restaura a Home anterior. O futuro commit funcional deverá ser único e não depender de migração destrutiva.

## Validação da decisão

A ADR somente muda para “aceita” após aprovação formal do documento estratégico. Até lá, não autoriza código, merge, deploy, criação de eventos ou alteração de dados.
