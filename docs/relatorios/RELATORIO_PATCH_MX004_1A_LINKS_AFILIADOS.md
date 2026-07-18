# RELATORIO PATCH MX-004.1A - LINKS AFILIADOS

## Objetivo

Corrigir os links da secao "Ofertas de Parceiros" para que cada card abra o destino correspondente ao seu proprio titulo, imagem e preco.

## Causa raiz

Os 6 cards usavam a mesma constante `MERCADO_LIVRE_AFILIADO_URL` como valor de `url`.

O template estava correto ao renderizar `oferta.url`; o problema estava na fonte de dados, onde todas as ofertas recebiam a mesma URL.

## Diagnostico realizado

- Fonte de dados dos 6 cards inspecionada em `app.py`.
- Confirmado que todos os cards recebiam a mesma URL antes do patch.
- Template inspecionado em `templates/index.html`.
- Confirmado que o template nao reutilizava uma variavel unica global para todos os cards; ele usava `oferta.url`.
- Estrutura HTML inspecionada.
- Confirmado que nao havia link envolvendo todo o carrossel.
- CSS inspecionado.
- Confirmado que nao havia camada invisivel, `z-index` ou elemento absoluto capturando todos os cliques.

## Arquivos alterados

- `app.py`
- `templates/index.html`
- `tests/test_moderacao.py`
- `docs/relatorios/RELATORIO_PATCH_MX004_1A_LINKS_AFILIADOS.md`

## Links cadastrados

| Card | Titulo | Identificador de destino | URL |
|---|---|---|---|
| 1 | Celulares e acessorios | `celulares-acessorios` | `https://lista.mercadolivre.com.br/celulares-acessorios` |
| 2 | Fones e audio | `fones-audio` | `https://lista.mercadolivre.com.br/fones-audio` |
| 3 | Informatica | `informatica` | `https://lista.mercadolivre.com.br/informatica` |
| 4 | Casa e utilidades | `casa-utilidades` | `https://lista.mercadolivre.com.br/casa-utilidades` |
| 5 | Ferramentas | `ferramentas` | `https://lista.mercadolivre.com.br/ferramentas` |
| 6 | Eletroportateis | `eletroportateis` | `https://lista.mercadolivre.com.br/eletroportateis` |

## Preservacao de parametros oficiais

Cada card agora aceita URL individual por variavel de ambiente:

- `OFERTA_PARCEIRO_01_URL`
- `OFERTA_PARCEIRO_02_URL`
- `OFERTA_PARCEIRO_03_URL`
- `OFERTA_PARCEIRO_04_URL`
- `OFERTA_PARCEIRO_05_URL`
- `OFERTA_PARCEIRO_06_URL`

Quando um link oficial de afiliado for cadastrado nessas variaveis, o valor sera renderizado sem alteracao, preservando todos os parametros recebidos.

Na validacao de producao de 18/07/2026, as seis variaveis especificas nao estavam configuradas com links oficiais de afiliado. A aplicacao publicou os valores padrao de categoria, sem query string, identificador ou redirecionador de afiliado:

- `https://lista.mercadolivre.com.br/celulares-acessorios`
- `https://lista.mercadolivre.com.br/fones-audio`
- `https://lista.mercadolivre.com.br/informatica`
- `https://lista.mercadolivre.com.br/casa-utilidades`
- `https://lista.mercadolivre.com.br/ferramentas`
- `https://lista.mercadolivre.com.br/eletroportateis`

Portanto, nao foi possivel confirmar a permanencia dos parametros de afiliado nos links finais. Para concluir a validacao comercial, ainda e necessario cadastrar os seis links oficiais individuais nas variaveis `OFERTA_PARCEIRO_01_URL` a `OFERTA_PARCEIRO_06_URL`.

## Evidencias

- Cada card possui URL propria.
- Imagem, titulo e botao pertencem ao mesmo link do card.
- Links abrem em nova guia.
- Links usam `rel="sponsored noopener noreferrer"`.
- Testes automatizados impedem URLs vazias ou repetidas.

## Testes executados

- `ruff check .` - aprovado.
- `ruff format --check .` - aprovado.
- `python -m unittest tests.test_moderacao` - 96 testes aprovados.
- `git diff --check` - aprovado.
- Validacao especifica da matriz dos cards renderizados - aprovada.

## Matriz de teste

| Card | Resultado |
|---|---|
| Card 1 -> produto 1 | `celulares-acessorios` confirmado |
| Card 2 -> produto 2 | `fones-audio` confirmado |
| Card 3 -> produto 3 | `informatica` confirmado |
| Card 4 -> produto 4 | `casa-utilidades` confirmado |
| Card 5 -> produto 5 | `ferramentas` confirmado |
| Card 6 -> produto 6 | `eletroportateis` confirmado |

## Validacao de areas clicaveis

- Clique na imagem: validado por `data-click-area="imagem"` dentro do link do card.
- Clique no titulo: validado por `data-click-area="titulo"` dentro do link do card.
- Clique no botao "Ver oferta": validado por `data-click-area="botao"` dentro do link do card.
- Todas as areas compartilham a mesma URL do card correspondente.

## Validacao em producao

### Publicacao

- PR: `#53`.
- Hash do merge: `5109853e783735bd39f84b42a10f7fabdac35a78`.
- Merge realizado em: 18/07/2026 as 09:44:01 BRT (`12:44:01Z`).
- CI da `master`: aprovado no run `29644860852`.
- CI concluido em: 18/07/2026 as 09:44:32 BRT (`12:44:32Z`).
- Deploy automatico no Render: confirmado em producao durante a validacao iniciada apos a conclusao do CI. O painel do Render nao foi consultado, portanto o horario tecnico exato de conclusao do deploy nao esta disponivel; a nova versao estava ativa antes das evidencias registradas as 09:54 BRT.
- URL validada: `https://mercadocolatina.com.br/`.

### Matriz dos seis destinos em producao

| Card | Destino esperado | Destino publicado | Resultado |
|---|---|---|---|
| 1 | `celulares-acessorios` | `https://lista.mercadolivre.com.br/celulares-acessorios` | Aprovado |
| 2 | `fones-audio` | `https://lista.mercadolivre.com.br/fones-audio` | Aprovado |
| 3 | `informatica` | `https://lista.mercadolivre.com.br/informatica` | Aprovado |
| 4 | `casa-utilidades` | `https://lista.mercadolivre.com.br/casa-utilidades` | Aprovado |
| 5 | `ferramentas` | `https://lista.mercadolivre.com.br/ferramentas` | Aprovado |
| 6 | `eletroportateis` | `https://lista.mercadolivre.com.br/eletroportateis` | Aprovado |

### Desktop

- Resolucao validada: `1280 x 720`.
- 6 cards renderizados e 4 visiveis por vez.
- 18 cliques aprovados: imagem, titulo e botao dos 6 cards.
- Todas as aberturas ocorreram em nova guia.
- Todos os destinos corresponderam ao card clicado.
- Navegacao manual e volta continua do carrossel aprovadas.
- Console sem erros.

### Mobile

- Layout mobile validado com 2 cards visiveis por vez.
- 18 cliques aprovados: imagem, titulo e botao dos 6 cards.
- Todas as aberturas ocorreram em nova guia.
- Todos os destinos corresponderam ao card clicado.
- Navegacao manual e volta continua do carrossel aprovadas.
- Console sem erros.

### Evidencias de producao

- `docs/evidencias/mx004-1a-producao-desktop.png`
- `docs/evidencias/mx004-1a-producao-mobile.png`

### Resultado final

- Correcao funcional dos seis destinos: aprovada.
- Abertura por imagem, titulo e botao: aprovada em desktop e mobile.
- Parametros oficiais de afiliado: nao confirmados, pois estao ausentes nos seis links publicados.
- Status comercial do Patch: pendente de configuracao dos seis links oficiais individuais de afiliado.
