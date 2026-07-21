# RFC — PATCH UX-007A Balão da Cidade

## Problema real da cidade

Moradores precisam reconhecer rapidamente qual caminho digital atende à necessidade do momento, sem enfrentar publicidade invasiva ou informações não verificadas.

## Proposta

Adicionar à Cidade Viva um painel editorial com quatro atalhos e dois CTAs, dimensionar uniformemente os cards resumidos e compactar o rodapé. Toda a mudança fica isolada por feature flag e por seletores CSS escopados.

## Decisões

- painel integrado ao grid, nunca fixo ou sobreposto;
- `aside` com título e navegação identificáveis por tecnologia assistiva;
- dados exibidos somente a partir de `metricas_cidade`;
- estado sem métricas composto apenas por chamadas reais;
- largura útil dos resumos ampliada de 73,75 rem para 80 rem;
- botão comunitário mantido no fluxo para não cobrir o novo painel;
- nenhum JavaScript adicional.

## Impacto esperado

Redução do tempo de decisão na Home, maior visibilidade dos caminhos locais e melhor aproveitamento horizontal no desktop, sem afetar Marketplace, banco, rotas ou dashboards.

## Alternativas rejeitadas

- popup: interromperia a navegação;
- painel fixo: cobriria conteúdo em telas menores;
- números de exemplo: violariam a transparência;
- coluna lateral em toda a Home: reduziria excessivamente a vitrine principal.

## Aceite

O patch é aceito quando a flag desligada preserva a Home 2.0, a flag ligada ativa apenas o escopo descrito, não há overflow entre 320 e 1440 px, a navegação por teclado funciona e a suíte permanece verde.
