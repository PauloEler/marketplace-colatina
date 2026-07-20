# RFC — Macro Projeto 001: Operação Cidade Viva

**Status:** implementada para revisão documental

**Versão:** 1.0

**Data:** 20 de julho de 2026

## Problema

O Mercado Colatina evoluiu rapidamente como marketplace e portal local, mas estratégia, ideias, decisões e métricas ficaram distribuídas entre documentos de diferentes fases e conversas operacionais. Isso aumenta o risco de perda de contexto, expansão de escopo e decisões sem evidência.

## Pergunta da Sprint

**Qual problema da cidade estamos resolvendo?**

Nesta Sprint, o problema é institucional: sem uma direção única e um processo de decisão rastreável, a plataforma reduz sua capacidade de resolver continuamente problemas de Colatina.

## Proposta

Instituir a Operação Cidade Viva e criar:

- núcleo estratégico em `00_CORE/`;
- guias de estratégia e empresa;
- atas históricas das grandes decisões;
- backlogs temáticos por jornada local;
- contrato de métricas e OKRs;
- Livro de Bordo e Painel da Missão;
- hierarquia que preserve o Documento Mestre anterior como base histórica e operacional.

## Escopo

Somente arquivos Markdown, organização documental, governança, arquitetura de decisão e referências cruzadas.

## Fora do escopo

Código, banco, templates, CSS, Home, Marketplace, Analytics, autenticação, integrações, merge e deploy.

## Alternativas consideradas

### Manter apenas o Documento Mestre existente

Rejeitada porque ele documenta principalmente a fase marketplace e não organiza backlogs, métricas, atas e aprendizado da estratégia Cidade Viva.

### Substituir ou apagar a documentação anterior

Rejeitada porque eliminaria contexto histórico e regras operacionais ainda válidas.

### Criar um único arquivo extenso

Rejeitada porque dificultaria atualização por responsabilidade e jornada.

## Critérios de aceite

- todos os arquivos requeridos existem;
- missão, visão, valores e manifesto reproduzem as decisões aprovadas;
- processo oficial e pergunta obrigatória aparecem na governança;
- ideias possuem destino temático e não são tratadas como autorização;
- métricas distinguem fato, linha de base e hipótese;
- RFC, ADR e relatório registram a Sprint;
- somente documentação é alterada;
- PR permanece Draft, sem merge ou deploy.

## Riscos e mitigação

- **duplicidade de autoridade:** hierarquia explícita na Constituição e nos READMEs;
- **documentação sem uso:** Painel da Missão, Livro de Bordo e ritual mensal;
- **backlog virar autorização:** aviso em todos os arquivos e processo de decisão obrigatório;
- **métricas inventadas:** linhas de base pendentes identificadas como tal.
