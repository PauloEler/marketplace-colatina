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

O CI oficial será registrado pela PR Draft.
