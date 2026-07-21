# RFC — PATCH UX-007B Acabamento final da Home

## Problema real

A Home 2.0 já reúne os conteúdos corretos, mas algumas coleções apresentam diferenças de altura e recorte. O Balão da Cidade ainda precisa parecer parte da seção Cidade Viva, o convite de sugestões não deve interromper o fluxo e o rodapé mantém mais altura que o necessário.

## Objetivo

Aplicar apenas acabamento visual: geometria uniforme dentro de cada coleção, recortes consistentes, Balão alinhado à Cidade Viva, frases editoriais rotativas, sugestão no rodapé institucional e rodapé aproximadamente 25% mais compacto.

## Escopo

- CSS isolado por `.home-finish-ux007b`;
- rotação de cinco frases reais, sem números ou estimativas;
- pausa quando a página perde visibilidade;
- conteúdo estático quando `prefers-reduced-motion: reduce` estiver ativo;
- nenhuma mudança em Hero, busca, rotas, banco ou backend de negócio.

## Aceite

Desktop, tablet, 390 px e 320 px sem overflow; cards de cada coleção com a mesma geometria; console limpo; Home anterior idêntica com a flag desligada.
