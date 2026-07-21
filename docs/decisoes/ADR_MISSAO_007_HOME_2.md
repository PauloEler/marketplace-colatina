# ADR — Isolamento da Home 2.0 por feature flag

## Contexto

A primeira dobra precisava ser reorganizada sem alterar a versão publicada nem
as seções da Home compacta.

## Decisão

Adicionar `HOME_2_ENABLED`, com valor padrão `false`, e renderizar a variante
somente quando a flag existente da Cidade Viva também estiver ativa. Manter o
markup anterior no ramo alternativo e escopar todo estilo novo em
`.home-2-mission007`.

## Consequências positivas

- Ativação e desligamento sem migração ou mudança de banco.
- Home publicada preservada byte a byte no caminho desligado.
- Comparação visual possível nas mesmas larguras.
- Reversão adicional por um único commit.

## Consequências e limites

- Dois conjuntos de primeira dobra coexistem temporariamente no template.
- A variante não aparece em páginas de resultados, filtros ou visualização de
  todos os itens; isso preserva a experiência vigente nesses contextos.

## Estado

Aceita para a PR Draft da Missão 007. Ativação em produção ainda não autorizada.
