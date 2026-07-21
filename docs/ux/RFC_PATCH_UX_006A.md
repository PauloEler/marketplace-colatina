# RFC — PATCH UX-006A: Home compacta

## Problema real

Mesmo após o protótipo Cidade Viva, a Home ainda exige que o morador percorra listas completas antes de conhecer todas as frentes da plataforma. Isso aumenta o tempo de descoberta e torna seções diferentes visualmente parecidas.

## Objetivo

Transformar cada lista da composição Cidade Viva em um resumo curto, sempre acompanhado por “Ver todos”, sem remover conteúdo, alterar backend ou criar estado novo.

## Público afetado

Moradores que acessam a Home, principalmente pelo celular, e precisam compreender rapidamente produtos, empresas, necessidades e parceiros disponíveis.

## Proposta

- posicionar “🌇 Cidade Viva” imediatamente após Encontre Quem Resolve;
- manter somente um resumo visual por seção;
- limitar visualmente categorias e parceiros no protótipo;
- reduzir altura de imagens, cards e espaços internos;
- oferecer “Ver todos” em Cidade Viva, Categorias, Produtos, Lojas, Anúncios recentes, Ofertas de Parceiros e Empresas Parceiras;
- usar `?todos=1` como retorno à composição integral;
- aplicar tudo somente quando `HOME_CIDADE_VIVA_ENABLED=true`.

## Alternativas consideradas

### Criar novas rotas de listagem

Rejeitada nesta fase porque exigiria backend e ampliaria o escopo.

### Remover blocos da Home

Rejeitada porque eliminaria caminhos já aprovados.

### Accordion com JavaScript

Rejeitada porque adicionaria comportamento e estado desnecessários. A navegação para a composição integral é mais simples e reversível.

## Indicadores

- altura total antes/depois por breakpoint;
- ausência de overflow horizontal da página;
- sete links “Ver todos” na composição com dados completos;
- posição de Cidade Viva imediatamente após Encontre Quem Resolve;
- Home integral preservada com a flag desligada ou `?todos=1`.

## Riscos

- conteúdo importante ficar pouco evidente no resumo;
- listas horizontais perderem legibilidade em telas estreitas;
- CSS compacto afetar a Home anterior.

Os riscos são controlados pelo escopo `.home-compact-ux006a`, alvos de toque mínimos, testes de flag e capturas em cinco larguras.
