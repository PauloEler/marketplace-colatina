# Relatório visual — PATCH UX-007A

## Comparativo

As capturas anteriores foram feitas na Home 2.0 em produção. As capturas posteriores foram feitas na aplicação local com as três flags ativas e o mesmo motor Chromium/Edge.

| Largura | Resultado |
| --- | --- |
| 1440 px | painel vertical à direita; conteúdo com 1280 px úteis; sem sobreposição |
| 1024 px | painel vertical à direita; colunas estáveis |
| 768 px | painel horizontal abaixo da Cidade Viva |
| 390 px | card comum de 350 px; sem posição fixa |
| 320 px | card comum de 280 px; sem overflow |

Em todas as larguras, `scrollWidth` foi igual à largura interna. O `position` computado do balão foi `relative`. O botão comunitário permaneceu acessível, mas passou ao fluxo normal para não cobrir o painel.

## Evidências

- Antes: `docs/ux/evidencias/ux_007a/antes/`
- Depois: `docs/ux/evidencias/ux_007a/depois/`

Arquivos: `HOME_1440.png`, `HOME_1024.png`, `HOME_768.png`, `HOME_390.png` e `HOME_320.png`.

## Avaliação

O desktop ganhou uma orientação lateral clara; tablet e mobile preservam leitura linear. Cards resumidos compartilham largura, raio e densidade. O rodapé móvel caiu de aproximadamente uma tela completa para uma composição em duas colunas, mantendo todos os caminhos.
