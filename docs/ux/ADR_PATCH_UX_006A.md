# ADR — PATCH UX-006A: resumo com expansão para a Home integral

## Status

Aceita para protótipo em PR Draft.

## Contexto

O patch deve compactar a Home sem alterar backend, banco ou funcionalidades. A Missão 006 já oferece uma feature flag e o parâmetro `?todos=1`, que renderiza a composição anterior completa.

## Decisão

Reutilizar `HOME_CIDADE_VIVA_ENABLED` e adicionar a classe visual `home-compact-ux006a` somente quando a flag estiver ativa.

Cada seção apresenta um subconjunto ou resumo compacto. O link “Ver todos” aponta para a mesma Home com `?todos=1` e a âncora correspondente. Assim, nenhum conteúdo é apagado e não surge uma segunda fonte de verdade.

“🌇 Cidade Viva” será movida no DOM para depois de Encontre Quem Resolve. O CSS também define `order: 25`, preservando a mesma ordem visual e de leitura.

## Consequências positivas

- nenhuma alteração de Python, banco ou rota;
- reversão imediata pela flag;
- experiência mais curta no desktop e celular;
- conteúdo integral permanece acessível;
- implementação pequena e auditável.

## Consequências negativas

- “Ver todos” restaura a Home integral, não uma página exclusiva por seção;
- a navegação pode exigir nova rolagem até a âncora;
- limites visuais são definidos no CSS e deverão ser revistos se a estrutura dos cards mudar.

## Reversão

Desativar `HOME_CIDADE_VIVA_ENABLED`, descartar a branch ou reverter o único commit do patch. Nenhuma limpeza de dados é necessária.
