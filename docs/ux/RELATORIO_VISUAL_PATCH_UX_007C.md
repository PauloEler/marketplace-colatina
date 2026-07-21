# Comparativo visual — PATCH UX-007C

## Antes

As imagens de referência são as capturas finais do PATCH UX-007B, estado atualmente publicado antes do UX-007C.

- `evidencias/ux_007c/antes/HOME_1440.png`
- `evidencias/ux_007c/antes/HOME_768.png`
- `evidencias/ux_007c/antes/HOME_390.png`
- `evidencias/ux_007c/antes/HOME_320.png`

## Depois

- `evidencias/ux_007c/depois/HOME_1440.png`
- `evidencias/ux_007c/depois/HOME_1024.png`
- `evidencias/ux_007c/depois/HOME_768.png`
- `evidencias/ux_007c/depois/HOME_390.png`
- `evidencias/ux_007c/depois/HOME_320.png`

## Critérios observados

- Busca Rápida, Encontre Quem Resolve e Cidade Viva iniciam e terminam na mesma coluna;
- Cidade Viva ocupa sua largura quando existem dois indicadores;
- Balão alinhado ao topo e compacto como coluna editorial;
- “Ver todos” encerra cada seção no canto inferior direito;
- rodapé preservado e mais próximo do conteúdo;
- nenhum overflow entre 320 px e 1440 px.

## Medições finais

| Largura | Busca Rápida | Encontre Quem Resolve | Cidade Viva | Overflow |
| --- | ---: | ---: | ---: | --- |
| 1440 px | 1278 px | 1278 px | 1278 px | não |
| 1024 px | 895 px | 895 px | 895 px | não |
| 768 px | 660 px | 660 px | 660 px | não |
| 390 px | 335 px | 335 px | 335 px | não |
| 320 px | 265 px | 265 px | 265 px | não |

No desktop e notebook, Cidade Viva e Balão começam na mesma linha. Em tablet e mobile, o Balão desce para uma faixa/card comum, preservando o comportamento responsivo anterior e sem cobrir conteúdo.

O rodapé manteve todos os links e informações; somente seus vazios verticais foram reduzidos. A altura medida no desktop caiu de aproximadamente 338 px para 312 px.
