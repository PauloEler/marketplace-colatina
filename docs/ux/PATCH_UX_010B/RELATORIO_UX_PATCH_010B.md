# PATCH UX-010B — Limpeza da Home

## Diagnóstico

A Home preservava as funções corretas, mas a primeira sequência visual passou a apresentar três focos com peso semelhante: Hero, busca e uma segunda composição promocional de serviços.

O bloco de serviços repetia a mesma decisão em quatro camadas: título longo, explicação, ilustrações, cards explicativos e botões. Essa repetição aumentava o tempo necessário para entender a interface e fazia o bloco parecer uma segunda Home.

Também havia três controles com aparência de CTA no Hero. O compartilhamento continuava útil, mas competia visualmente com as ações centrais de comprar e anunciar.

## Decisão de UX

- Preservar integralmente Hero, busca, rotas e fluxos existentes.
- Transformar o compartilhamento do Hero em uma ação terciária e discreta.
- Reduzir o bloco de serviços a uma introdução curta e duas escolhas.
- Exibir o papel antes da ação: `Cliente` e `Prestador`.
- Usar frases na primeira pessoa para facilitar o reconhecimento imediato da intenção.
- Remover ilustrações, emojis decorativos, gradiente e sombras fortes.
- Preservar contraste, foco por teclado e áreas de toque confortáveis.

## Hierarquia final

1. Hero: inspira e apresenta o Mercado Colatina.
2. Busca: permite encontrar produtos e serviços.
3. Serviços em Colatina: oferece somente duas escolhas inequívocas.
4. Conteúdo e indicadores existentes continuam sem alteração.

## Comparação dimensional

| Largura | Antes | Depois | Redução aproximada |
|---|---:|---:|---:|
| Desktop 1440 px | 305 px | 107 px | 65% |
| Tablet 768 px | 408 px | 198 px | 51% |
| Mobile 390 px | 639 px | 334 px | 48% |
| Mobile 320 px | 697 px | 364 px | 48% |

Nenhuma das quatro larguras apresentou overflow horizontal.

## Capturas

### Antes

- [Desktop 1440](antes/desktop_1440.png)
- [Tablet 768](antes/tablet_768.png)
- [Mobile 390](antes/mobile_390.png)
- [Mobile 320](antes/mobile_320.png)

### Depois

- [Desktop 1440](depois/desktop_1440.png)
- [Tablet 768](depois/tablet_768.png)
- [Mobile 390](depois/mobile_390.png)
- [Mobile 320](depois/mobile_320.png)

## Validação

- 182 testes aprovados.
- 37 subtestes aprovados.
- Ruff check aprovado.
- Ruff format check aprovado.
- Git diff check aprovado.
- Desktop, tablet, 390 px e 320 px sem overflow.
- Os dois destinos existentes foram preservados.
- Nenhuma alteração em banco, backend, rotas ou regras de negócio.
- Erros registrados pelo site: nenhum. A mensagem Sentry observada pertence à extensão do navegador e não à aplicação.

## Reversão

O patch é isolado em um único commit. A reversão pode ser realizada com `git revert <hash-do-commit>`, restaurando o HTML, o CSS, os testes e as evidências anteriores sem migração de dados.

## Conclusão

A proposta reduz ruído sem remover capacidade. O Hero recupera protagonismo, o bloco de serviços passa a complementar a Home e a escolha entre procurar e divulgar pode ser compreendida em poucos segundos.
