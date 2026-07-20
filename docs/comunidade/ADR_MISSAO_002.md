# ADR — Missão 002 — Agregação da Inteligência Comunitária

**Status:** aceita

**Data:** 20 de julho de 2026

## Contexto

O domínio de sugestões já armazena os campos necessários. Criar tabelas agregadas, eventos de Analytics ou uma integração de IA aumentaria complexidade, retenção e risco antes de existir volume que justificasse essa infraestrutura.

## Decisão

Calcular a inteligência sob demanda em um módulo Python puro e isolado:

- leitura exclusiva de `sugestoes_comunidade`;
- nenhuma escrita e nenhuma migração de banco;
- regras lexicais explícitas e testáveis;
- resultado estruturado consumido por um template administrativo;
- dataset futuro com versão de schema e exclusão do nome do autor;
- limiar mínimo para qualquer resposta conclusiva.

## Definições

- **pendente:** Nova, Em análise ou Planejada;
- **recorrente:** palavra relevante presente em pelo menos duas sugestões distintas;
- **categoria em crescimento:** volume na janela atual de 30 dias maior que na janela anterior;
- **problema mais citado:** aproximação lexical pelos termos relevantes, sempre acompanhada da limitação metodológica;
- **amostra suficiente:** pelo menos três sugestões nos últimos 30 dias.

## Consequências

- implementação simples e portátil entre SQLite e PostgreSQL;
- ausência de custo externo e de nova coleta;
- métricas atualizadas a cada acesso;
- adequado ao volume inicial, mas não a milhões de registros;
- análise lexical não une sinônimos nem entende contexto;
- futura escala poderá exigir agregação assíncrona por nova ADR.

## Alternativas rejeitadas

- nova tabela de métricas: duplicaria dados e exigiria sincronização;
- reutilizar Analytics de Afiliados: finalidade, privacidade e eventos incompatíveis;
- SQL específico por banco: reduziria portabilidade;
- IA nesta fase: não autorizada e desproporcional à amostra;
- exibir mensagens completas no Radar: desnecessário para a visão agregada.
