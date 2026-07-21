# ADR — PATCH UX-006B Hero 2.0

Data: 21/07/2026
Decisão: aceita na branch de trabalho

## Contexto

O Hero herdava largura automática dentro de um contêiner flexível com margens automáticas. Com a Home compacta ativa, o resultado prático no desktop era uma seção de 594 px, título em seis linhas e baixa presença da fotografia principal.

## Decisão

1. Escopar todos os estilos novos sob `.home-compact-ux006a .ux005c-first-fold`.
2. Definir a largura desktop em 78% da área disponível, dentro do limite institucional de 84 rem.
3. Dividir o título em dois elementos de linha, com `white-space: nowrap`, e ajustar a tipografia por breakpoint.
4. Reexibir a fotografia como faixa visual compacta em tablet e mobile.
5. Manter a busca no mesmo formulário, rota e posição estrutural.
6. Usar reversão por commit único, sem criar nova flag.

## Consequências

- leitura do título em duas linhas nos quatro breakpoints auditados;
- Hero mais largo e fotografia mais presente;
- busca e Home compacta preservadas;
- nenhuma dependência nova e nenhum impacto no banco ou backend.

## Alternativas rejeitadas

- redesenhar toda a primeira dobra: ampliaria o escopo;
- remover a fotografia no mobile: contrariaria o objetivo de valorizá-la;
- criar nova feature flag: seria redundante, pois o patch é isolado e reversível por um único commit.
