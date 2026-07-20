# ADR — Arquitetura do Ouvir Colatina

**Status:** aceita

**Data:** 20 de julho de 2026

## Contexto

Sugestões comunitárias não pertencem a anúncios, pedidos, denúncias, notificações ou eventos de afiliados. Reutilizar uma dessas estruturas misturaria finalidades, permissões e métricas.

## Decisão

Adotar um domínio isolado:

- tabela `sugestoes_comunidade`;
- módulo `community_suggestions.py`;
- template público `sugerir.html`;
- template administrativo `sugestoes_admin.html`;
- rotas públicas e administrativas específicas;
- CSS com prefixo `community-`.

## Estados

`nova → em_analise → planejada → implementada`

`arquivada` pode ser usado quando a contribuição não avançar. A interface permitirá transições administrativas controladas e preservará a data da primeira análise.

## Privacidade

Nome é opcional. Nenhum dado de contato, IP ou associação automática à conta será gravado. O conteúdo permanece privado para a administração nesta versão.

## Analytics

As métricas serão calculadas diretamente sobre a tabela própria e exibidas apenas no painel de sugestões. Nenhum evento será escrito na estrutura de Analytics existente.

## Votação futura

Não será criada tabela ou endpoint de votos antes da decisão sobre autenticação, unicidade, fraude, moderação e privacidade. O domínio e as rotas são independentes para permitir que uma futura RFC acrescente votação sem modificar Marketplace ou Analytics.

## Consequências

- separação clara de responsabilidades;
- migração compatível com SQLite e PostgreSQL;
- menor risco de exposição e acoplamento;
- nova tabela e novas rotas exigem testes próprios;
- votação permanece conscientemente pendente.

## Alternativas rejeitadas

- usar denúncias: finalidade e tratamento diferentes;
- usar notificações: dados pertencem a usuários destinatários;
- registrar como eventos de Analytics: eventos não substituem conteúdo e workflow;
- publicar sugestões imediatamente: risco de abuso e moderação não resolvido.
