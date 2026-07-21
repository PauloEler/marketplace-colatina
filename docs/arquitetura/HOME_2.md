# Home 2.0 — arquitetura reversível

## Problema real

A primeira dobra publicada reunia inspiração, busca, solicitação de serviço e
compartilhamento dentro do mesmo conjunto visual. Essa sobreposição tornava
menos evidente qual caminho o visitante deveria usar.

## Objetivo

Separar a primeira dobra em quatro responsabilidades: o Hero inspira, a busca
encontra, o Encontre Quem Resolve conecta e a Cidade Viva informa.

## Composição

1. `home2-hero`: mensagem institucional, dois CTAs e panorama de Colatina.
2. `home2-search-band`: formulário GET que preserva a busca e as categorias.
3. `home2-solver`: acesso isolado à rota Encontre Quem Resolve.
4. `home-city-movement`: componente existente, sem alteração.

O template anterior permanece no mesmo arquivo e é selecionado pelo contexto
`home_2_enabled`. Todo CSS novo é limitado pela classe de `body`
`.home-2-mission007`, impedindo impacto quando a experiência está desligada.

## Ativação

`HOME_2_ENABLED=false` é o padrão em desenvolvimento e no Render. A Home 2.0
só pode aparecer quando a Home compacta/Cidade Viva também estiver ativa:

```text
home_2_enabled = HOME_2_ENABLED and home_cidade_viva_enabled
```

Filtros, resultados de busca e `?todos=1` continuam usando a Home publicada.

## Preservação

Não houve mudança em banco, rotas, backend de busca, produtos, empresas,
parceiros, dashboards ou seções posteriores. A imagem e os destinos existentes
foram reutilizados.

## Evolução futura

Após aprovação visual, ativar a flag em janela controlada e medir os cliques em
Comprar agora, Anunciar grátis, Encontrar agora e Descrever minha necessidade.
