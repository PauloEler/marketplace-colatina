# RELATORIO PATCH MX-004.1B - ATIVACAO COMERCIAL E CARDS COMPACTOS

## Objetivo

Preparar a secao "Ofertas de Parceiros" para receber seis links oficiais individuais do Programa de Afiliados do Mercado Livre e compactar o carrossel sem alterar sua posicao na Home.

## Causa do limite de quatro cards

O CSS definia cada card com `flex-basis: calc((100% - 3rem) / 4)`. Essa regra reservava um quarto da largura util para cada oferta e, por isso, limitava o desktop a quatro cards visiveis simultaneamente.

## Situacao comercial dos links

- Status dos links oficiais: `0/6` fornecidos.
- Os seis links oficiais individuais ainda nao foram fornecidos pelo proprietario do Mercado Colatina.
- Nenhum parametro, identificador ou codigo de afiliado foi criado por este Patch.
- Nenhuma identificacao de afiliado foi inventada.
- A comissao de afiliado nao esta declarada como ativa.
- Os seis destinos diretos atuais do Mercado Livre foram preservados como fallback.
- A ativacao comercial depende do preenchimento das variaveis `OFERTA_PARCEIRO_01_URL` a `OFERTA_PARCEIRO_06_URL` com os links oficiais recebidos.

## Arquitetura escolhida

Foi criado o modulo central `partner_offers.py`, que concentra:

- titulo, preco, imagem e texto alternativo;
- identificador de cada destino;
- nome da variavel de ambiente de cada link oficial;
- URL direta usada como fallback;
- indicador interno de link oficial configurado.

A funcao `build_partner_offers()` usa a URL oficial sem alteracao quando a variavel correspondente esta preenchida. Quando ela esta ausente ou vazia, mantem o fallback direto. O template apenas recebe e renderiza a configuracao pronta.

As seis variaveis tambem foram declaradas em `.env.example` e `render.yaml`, sem valores inventados.

## Breakpoints e cards visiveis

| Largura | Cards visiveis | Regra |
|---|---:|---|
| 1440 px ou desktop largo | 6 | Regra padrao |
| 1280 px e desktop comum | 5 | `max-width: 1399px` |
| 1024 px | 5 | Mantem a regra de desktop comum |
| Tablet ate 1023 px | 3 | `max-width: 1023px` |
| Mobile ate 639 px | 2 | `max-width: 639px` |
| 320 px | 2 | Gap reduzido em `max-width: 359px` |

## Compactacao aplicada

- Gap do carrossel reduzido.
- Cards recalculados por breakpoint.
- Margens internas e badge compactados.
- Titulo e preco ajustados de forma proporcional.
- Botao preservado com altura minima acessivel de 44 px.
- Foco visivel reforcado no link de cada oferta.
- `min-width: 0` e `max-width: 100%` aplicados ao bloco para impedir overflow da pagina.

## Recursos preservados

- Navegacao manual.
- Rotacao automatica.
- Pausa por mouse e foco.
- Respeito a `prefers-reduced-motion`.
- Navegacao por teclado.
- Lazy loading.
- Nova guia com `target="_blank"`.
- `rel="sponsored noopener noreferrer"`.

## Arquivos alterados

- `.env.example`
- `app.py`
- `partner_offers.py`
- `render.yaml`
- `static/partner-offers-carousel.js`
- `static/styles.css`
- `templates/index.html`
- `tests/test_moderacao.py`
- `docs/relatorios/RELATORIO_PATCH_MX004_1B_ATIVACAO_COMERCIAL_CARDS_COMPACTOS.md`
- `docs/evidencias/mx004-1b-cards-desktop-1440.png`
- `docs/evidencias/mx004-1b-cards-mobile-390.png`

## Testes automatizados

- Seis ofertas cadastradas.
- URLs preenchidas e unicas.
- Seis chaves de configuracao unicas.
- Fallbacks diretos unicos.
- Link oficial recebido preservado sem alteracao.
- Ausencia de ativacao comercial quando as variaveis estao vazias.
- Atributos `target` e `rel` corretos.
- Configuracao responsiva 6/5/3/2 declarada e testada.

## Validacao responsiva

| Largura | Resultado | Cards visiveis |
|---|---|---:|
| 1440 px | Aprovado, sem overflow | 6 |
| 1280 px | Aprovado, sem corte | 5 |
| 1024 px | Aprovado, estavel e legivel | 5 |
| Tablet 768 px | Aprovado | 3 |
| 390 px | Aprovado | 2 |
| 320 px | Aprovado, sem overflow da pagina | 2 |

As seis larguras mantiveram cards sem overflow interno e botoes com altura minima computada de 44 px.

## Resultados dos testes

- Suite completa: 99 testes aprovados.
- `ruff check .`: aprovado.
- `ruff format --check .`: aprovado.
- `git diff --check`: aprovado.
- Seis URLs preenchidas e unicas: aprovado.
- Imagem, titulo e botao no mesmo link do card: aprovado.
- `target="_blank"` e `rel="sponsored noopener noreferrer"`: aprovados nos seis cards.
- Navegacao manual: aprovada.
- Teclado: Enter nos controles e setas no carrossel aprovados.
- Foco visivel: aprovado.
- Rotacao automatica: agendamento e deslocamento validados em teste isolado do componente.
- Preferencia de movimento reduzido: pausa automatica confirmada nos navegadores de validacao.
- Console da aplicacao: sem erros.

## Evidencias

- Desktop 1440 px: `docs/evidencias/mx004-1b-cards-desktop-1440.png`.
- Mobile 390 px: `docs/evidencias/mx004-1b-cards-mobile-390.png`.

## Pendencia final

Receber do proprietario e cadastrar os seis links oficiais individuais do Programa de Afiliados do Mercado Livre. Ate isso ocorrer, a secao continua funcional com os links diretos, mas sem confirmacao de comissao ativa.

## Publicacao

- PR: `#55`, removida de Draft, revisada e aprovada.
- Merge na `master`: `c1e9bf0c6fd2068bb090393f74abb9ce46263bce`.
- Horario do merge: 18/07/2026, 10:56:32 (America/Sao_Paulo).
- CI da `master`: aprovado no workflow `29647084832`.
- Deploy automatico no Render: concluido.
- Nova versao detectada em producao: 18/07/2026, 10:59:12 (America/Sao_Paulo).
- URL validada: `https://mercadocolatina.com.br/`.

### Validacao em producao por breakpoint

| Largura | Esperado | Observado | Overflow da pagina | Resultado |
|---|---:|---:|---|---|
| 1440 px | 6 | 6 | Nao | Aprovado |
| 1280 px | 5 | 5 | Nao | Aprovado |
| 1024 px | 5 | 5 | Nao | Aprovado |
| 768 px | 3 | 3 | Nao | Aprovado |
| 390 px | 2 | 2 | Nao | Aprovado |
| 320 px | 2 | 2 | Nao | Aprovado |

Em todas as larguras foram encontrados seis cards cadastrados, sem overflow interno e com altura minima de 44 px nos botoes.

### Matriz dos seis destinos em producao

| Card | Identificador | Destino validado | Origem do link |
|---:|---|---|---|
| 1 | `celulares-acessorios` | `https://lista.mercadolivre.com.br/celulares-acessorios` | Fallback direto |
| 2 | `fones-audio` | `https://lista.mercadolivre.com.br/fones-audio` | Fallback direto |
| 3 | `informatica` | `https://lista.mercadolivre.com.br/informatica` | Fallback direto |
| 4 | `casa-utilidades` | `https://lista.mercadolivre.com.br/casa-utilidades` | Fallback direto |
| 5 | `ferramentas` | `https://lista.mercadolivre.com.br/ferramentas` | Fallback direto |
| 6 | `eletroportateis` | `https://lista.mercadolivre.com.br/eletroportateis` | Fallback direto |

Imagem, titulo e botao de cada card compartilham o mesmo link correspondente. Os seis links possuem `target="_blank"` e `rel="sponsored noopener noreferrer"` e foram confirmados com abertura em nova guia.

### Validacao funcional em producao

- Navegacao manual: aprovada; avancar deslocou o carrossel e voltar restaurou a posicao.
- Teclado: aprovado com Enter nos controles e ArrowRight no carrossel.
- Foco visivel: aprovado, com contorno computado no elemento ativo.
- Rotacao automatica: ativo publicado com intervalo de 5,2 segundos; no navegador de validacao, a pausa por `prefers-reduced-motion` foi corretamente respeitada.
- Console da aplicacao: zero erros.
- Desktop e mobile: aprovados conforme a matriz de breakpoints.

### Situacao comercial apos a publicacao

- Os links atuais continuam sendo fallbacks diretos do Mercado Livre.
- Links oficiais de afiliado fornecidos: `0/6`.
- A comissao ainda nao pode ser considerada ativa.
- Nenhum parametro, codigo ou identificacao de afiliado foi inventado.
- A pendencia comercial permanece ate o recebimento e cadastro dos seis links oficiais individuais.
