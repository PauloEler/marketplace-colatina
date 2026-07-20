# ADR 003 — Operação Cidade Viva como camada estratégica

**Status:** aceita

**Data:** 20 de julho de 2026

## Contexto

O Mercado Colatina já possui um Documento Mestre criado na fase em que o marketplace era o centro exclusivo da estratégia. O Macro Projeto 001 amplia oficialmente o produto para a solução de problemas cotidianos da cidade.

## Decisão

Adotar `00_CORE/` como camada estratégica vigente da Operação Cidade Viva. Preservar `MERCADO_COLATINA_MASTER.md` como referência histórica e operacional do marketplace onde não houver conflito.

A documentação será modular:

- `00_CORE/`: identidade, Constituição, programa, direção e governança;
- `docs/estrategia/`: aplicação da estratégia;
- `docs/empresa/`: atas e memória decisória;
- `BACKLOG/`: ideias por problema local;
- `docs/metricas/`: definições, fontes e rituais de medição;
- `LIVRO_DE_BORDO.md`: registro semanal oficial.

## Consequências positivas

- direção única sem apagar a história do produto;
- ideias deixam de depender de memória de conversa;
- decisão, execução e resultado tornam-se rastreáveis;
- novas Sprints precisam demonstrar problema local e indicador.

## Consequências e custos

- documentação requer manutenção regular;
- documentos antigos precisam ser interpretados pela hierarquia;
- métricas ainda sem linha de base não podem orientar metas de crescimento imediatamente.

## Alternativas rejeitadas

- substituir o Documento Mestre anterior;
- manter toda estratégia em um único arquivo;
- tratar o novo programa apenas como roadmap sem governança.

## Regra de reversão

Uma futura mudança de camada estratégica exige autorização executiva, nova versão da Constituição, ata e ADR substitutiva. Arquivos históricos não serão apagados.
