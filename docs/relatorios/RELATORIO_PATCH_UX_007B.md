# Relatório — PATCH UX-007B Acabamento final da Home

## Objetivo

Finalizar alinhamento, proporção e identidade visual da Home sem criar funcionalidade de negócio.

## Alterações

- cards uniformizados dentro de cada coleção;
- imagens de produtos e ofertas com recorte e alinhamento comuns;
- Balão da Cidade alinhado ao topo de Cidade Viva;
- cinco mensagens rotativas, sem números fictícios;
- “Sugira uma melhoria” removido do fluxo e incorporado ao rodapé institucional;
- rodapé compactado, preservando logo, links e informações;
- feature flag `HOME_FINISH_007B_ENABLED=false` por padrão.

## Preservado

Hero, busca, Encontre Quem Resolve, conteúdo Cidade Viva, produtos, empresas, parceiros, rotas, banco, backend e dashboards.

## Reversão

Definir `HOME_FINISH_007B_ENABLED=false` e reiniciar o serviço, ou reverter o único commit do patch. Nenhuma limpeza de dados é necessária.

## Validação

- 162 testes automatizados aprovados localmente;
- Ruff check e format check aprovados;
- sintaxe JavaScript validada;
- desktop: 1440 px e 1024 px;
- tablet: 768 px;
- mobile: 390 px e 320 px;
- cards de produtos, lojas, ofertas e parceiros com dimensões equivalentes;
- Balão alinhado ao topo de Cidade Viva no desktop e empilhado nas larguras menores;
- rodapé reduzido em aproximadamente 20% a 25%, conforme a largura;
- sem overflow horizontal;
- console sem erros ou avisos.

## Publicação

- PR: `#93`.
- Merge por squash: `95a788a8feec3ccc6c6c0d6a871037dd1a0571cf`.
- CI da `master`: aprovado no workflow `29854578089`.
- Deploy automático do código: `live` no Render às 14h51, horário de Brasília.
- `HOME_FINISH_007B_ENABLED=true` ativada no Render.
- Deploy da configuração: `live` às 14h54, horário de Brasília.

## Validação final em produção

| Largura | Resultado |
| --- | --- |
| Desktop 1440 px | Hero, busca, Encontre Quem Resolve, Cidade Viva, cards e rodapé aprovados; Balão alinhado ao topo de Cidade Viva; sem overflow. |
| Tablet 768 px | Balão empilhado abaixo de Cidade Viva; cards uniformes; rodapé compacto; sem overflow. |
| Mobile 390 px | Conteúdo empilhado, cards uniformes, sugestão no rodapé e sem overflow. |
| Mobile 320 px | Layout íntegro, cards uniformes e sem overflow. |

- console sem erros ou avisos;
- cinco mensagens do Balão publicadas;
- rotação automaticamente pausada quando `prefers-reduced-motion: reduce` está ativa;
- botão flutuante de sugestão removido da Home e link institucional preservado no rodapé;
- Hero, busca, Encontre Quem Resolve, Cidade Viva, produtos, empresas, parceiros, backend, banco, rotas e dashboards preservados;
- produção estável após o deploy.
