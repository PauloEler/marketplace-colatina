# Relatório MDS Sprint 002 — Aplicação do Mercado Design System na Home

> **Projeto:** Mercado Colatina
> **Sprint:** MDS Sprint 002
> **Data:** 13 de julho de 2026
> **Design System:** Mercado Design System 1.0
> **Escopo:** apresentação visual e estrutura semântica da página inicial
> **Resultado:** aprovado para revisão, sem publicação automática

## 1. Resumo executivo

A página inicial recebeu a primeira aplicação técnica do Mercado Design System 1.0. A mudança é visualmente perceptível, mas permanece restrita à apresentação e à semântica da Home.

A nova composição reforça, nesta ordem:

1. marca e ação de anunciar;
2. busca local;
3. mensagem de marketplace regional;
4. categorias;
5. ofertas locais;
6. lojas locais;
7. conteúdo explicativo;
8. parceiro externo e planos, com menor prioridade.

O resultado apresenta hierarquia mais clara, controles consistentes, cartões com leitura mais rápida e uma experiência mobile mais eficiente. A redução da quebra vertical das categorias antecipou significativamente a primeira oferta em celulares.

Nenhuma rota, consulta, regra de negócio, autenticação, pedido, estoque, reputação, rastreabilidade, fluxo de anúncio ou estrutura de banco foi alterada.

## 2. Referências obrigatórias consultadas

- `docs/DESIGN_SYSTEM_MERCADO_COLATINA.md`
- `docs/MDS_CHECKLIST.md`
- `MERCADO_COLATINA_MASTER.md`

As decisões respeitaram os princípios de confiança, simplicidade, organização, clareza, rapidez, acessibilidade, prioridade ao conteúdo local e monetização em segundo plano.

## 3. Ação principal da Home

**Ação principal:** anunciar no Mercado Colatina.

O botão **Anunciar** permanece evidente no cabeçalho, e o hero apresenta o CTA correspondente:

- visitante: **Anunciar grátis**;
- usuário autenticado: **Publicar um anúncio**.

A busca é o principal instrumento de descoberta e aparece imediatamente após o cabeçalho. O CTA **Explorar ofertas** permanece como ação secundária.

## 4. Alterações realizadas

### 4.1 Fundação de tokens

Os tokens oficiais do MDS 1.0 foram incorporados ao `:root` sem remover os aliases antigos usados pelas outras telas. A Home consome diretamente os tokens `--mc-*`, permitindo adoção progressiva e reduzindo risco de regressão fora do escopo.

Grupos aplicados:

- marca e cores semânticas;
- superfícies, bordas e textos;
- tipografia e pesos;
- escala de espaçamento;
- dimensões de controles, toque e ícones;
- raios e bordas;
- sombras;
- duração e curvas de movimento;
- camadas de interface.

### 4.2 Cabeçalho

- Marca recebeu proporção, tipografia e contraste alinhados ao MDS.
- Navegação passou a respeitar alvos mínimos de 44 px.
- O botão **Anunciar** usa Secondary com texto escuro, combinação aprovada pelo MDS.
- Ícone de adicionar segue o padrão outline da biblioteca Lucide.
- Menu mobile passa a ser usado também no tablet, evitando quebra da navegação de usuários autenticados.
- O comportamento visual novo é limitado pela classe `mds-home`; outras páginas preservam seu estilo anterior.

### 4.3 Busca

- Labels visíveis foram adicionadas para busca e categoria.
- Input, select e botão possuem 48 px de altura.
- Borda, foco, raio, tipografia e espaçamento usam tokens oficiais.
- Ícone Search do Lucide foi incluído no campo e no botão.
- No mobile, a busca ocupa a primeira linha; categoria e botão compartilham a segunda linha.
- Placeholder continua sendo apoio, não substituto do label.

### 4.4 Hero

- A mensagem principal foi atualizada para **“Compre. Venda. Valorize Colatina.”**.
- O subtítulo foi reduzido e mantém o contexto regional.
- O fundo escuro e decorativo foi substituído por superfície clara com borda de marca e sombra discreta.
- O CTA principal usa Primary e o secundário usa Outline.
- O hero ficou menor no desktop e nos principais celulares.
- Não foram introduzidas imagens genéricas ou elementos decorativos competitivos.

### 4.5 Categorias

- Categorias usam o padrão oficial de tags/chips interativos.
- Cada chip possui alvo mínimo de 44 px.
- A categoria atual usa `aria-current="page"`, além de diferenciação visual.
- No mobile, a lista utiliza rolagem horizontal interna com scroll snap.
- A página não recebe rolagem horizontal.
- A faixa deixou de quebrar em várias linhas, reduzindo substancialmente a distância até os produtos.

### 4.6 Ofertas locais

- Cartões usam Surface/Card, Border, Radius LG e Shadow SM.
- Imagens mantêm proporção consistente e `object-fit: cover`.
- O placeholder continua identificando ausência de imagem sem criar dado falso.
- Hierarquia do conteúdo passou a ser: categoria, preço, título, localização, estoque e loja.
- Título do produto passou a ser um `h3` semântico.
- Localização, estoque e loja receberam ícones outline Lucide.
- Condição permanece em badge textual sobre a imagem.
- Estoque continua exibindo o mesmo valor, com flexão corrigida para “disponível/disponíveis”.
- CTA da loja foi padronizado como **Abrir loja**.
- Hover, `focus-within` e estados ativos utilizam movimento curto e tokens oficiais.

### 4.7 Lojas em destaque

- Cards usam o padrão oficial de superfície, borda, raio e sombra.
- Nome e bairro receberam prioridade visual.
- Foi adicionada uma descrição contextual curta sem inventar informações comerciais da loja.
- Selos foram reorganizados em uma linha própria e com menor peso visual.
- O selo Fundador usa ícone Award do Lucide em vez de emoji funcional.
- Métricas foram mantidas para preservar a informação existente, mas receberam menor contraste e hierarquia.
- O CTA foi padronizado como **Abrir loja**.

### 4.8 Comunicado

- Mantém-se compacto, expansível e dispensável.
- Superfície, borda, raio, sombra, cores e áreas de toque foram alinhados ao componente Alert do MDS.
- O botão de fechar mantém nome acessível.
- O comportamento de expansão e persistência de fechamento não foi alterado.

### 4.9 Mercado Livre e planos

- Permanecem abaixo das ofertas e lojas locais.
- O parceiro continua explicitamente identificado antes do CTA.
- O bloco de afiliado usa Info Soft e botão Outline, sem competir com a marca local.
- Planos usam superfícies neutras, sem card destacado ou sombra promocional.
- Nenhuma regra, preço, link ou condição comercial foi alterada.

### 4.10 Rodapé

- Espaçamentos, container e áreas de toque dos links foram alinhados ao MDS.
- O fundo Primary Active foi mantido como base institucional.

## 5. Ícones

Biblioteca aplicada: **Lucide Icons**, padrão outline, `stroke-width="2"`, `currentColor` e cantos arredondados.

Ícones utilizados:

- Search;
- Plus;
- Menu;
- Map Pin;
- Package;
- Store;
- Award.

Todos os ícones adicionados são decorativos ao lado de texto e usam `aria-hidden="true"`.

## 6. Comparação antes e depois

### 6.1 Diferenças visuais principais

| Área | Antes | Depois |
|---|---|---|
| Cabeçalho | navegação compacta, controles com medidas legadas | hierarquia MDS, alvos de 44 px e CTA Secondary |
| Busca | label somente para leitor de tela e botão azul | labels visíveis, ícone Lucide, foco e botão Primary |
| Hero | fundo verde forte e mensagem genérica | superfície clara, mensagem regional e CTAs MDS |
| Categorias mobile | chips quebravam em várias linhas | faixa horizontal organizada e rolável |
| Produto | metadados comprimidos em uma linha | preço, título e informações em hierarquia vertical |
| Loja | métricas visualmente dominantes | identidade, contexto e CTA recebem prioridade |
| Parceiro | bloco neutro legado | Info Soft e menor competição visual |
| Planos | cards ainda disputavam atenção | tratamento neutro e secundário |

### 6.2 Posição da primeira oferta

Medição: distância vertical, em CSS pixels, entre o topo da página e o primeiro card de produto.

| Viewport | Antes | Depois | Variação | Posição relativa depois |
|---|---:|---:|---:|---:|
| 1280 × 720 | 620 px | 645 px | +25 px | 0,90 tela |
| 1440 × 900 | 620 px | 645 px | +25 px | 0,72 tela |
| 768 × 1024 | 614 px | 739 px | +125 px | 0,72 tela |
| 390 × 844 | 945 px | 760 px | **−185 px** | 0,90 tela |
| 360 × 800 | 945 px | 784 px | **−161 px** | 0,98 tela |
| 320 × 568 | 1114 px | 877 px | **−237 px** | 1,54 tela |

No desktop, o label visível da busca acrescentou altura, mas o primeiro produto continua dentro da primeira tela. No tablet, a tipografia H1 oficial aumenta a altura do hero, mas a oferta permanece a 0,72 tela. Nos três celulares, a faixa horizontal de categorias produz ganho expressivo.

### 6.3 Altura dos blocos principais

| Viewport | Busca antes/depois | Hero antes/depois | Categorias antes/depois |
|---|---:|---:|---:|
| 1280 × 720 | 78 / 103 px | 221 / 206 px | 114 / 115 px |
| 390 × 844 | 188 / 173 px | 290 / 228 px | 278 / 141 px |
| 360 × 800 | 188 / 173 px | 290 / 252 px | 278 / 141 px |
| 320 × 568 | 188 / 173 px | 374 / 344 px | 329 / 141 px |

O aumento da busca desktop é intencional para cumprir a obrigatoriedade de labels visíveis. A redução móvel das categorias compensa essa decisão e melhora a descoberta de ofertas.

### 6.4 Capturas e inspeção

Foram inspecionadas capturas da área visível em:

- desktop 1280 × 720;
- tablet 768 × 1024;
- mobile 390 × 844;
- largura mínima 320 × 568;
- área de cards de produto e início de lojas em desktop.

As capturas foram utilizadas durante a validação e não foram adicionadas ao repositório para manter a Sprint restrita aos artefatos necessários.

## 7. Validação responsiva

| Viewport | Rolagem horizontal da página | Busca | Anunciar | Primeiro produto | Resultado |
|---|---|---|---|---|---|
| 1280 × 720 | não | evidente | evidente | dentro da primeira tela | aprovado |
| 1440 × 900 | não | evidente | evidente | dentro da primeira tela | aprovado |
| 768 × 1024 | não | evidente | evidente no menu e hero | dentro da primeira tela | aprovado |
| 390 × 844 | não | evidente | evidente | inicia dentro da primeira tela | aprovado |
| 360 × 800 | não | evidente | evidente | inicia no limite da primeira tela | aprovado |
| 320 × 568 | não | evidente | evidente | 1,54 tela | aprovado |

Em todos os tamanhos:

- `scrollWidth` da página é igual ao `clientWidth`;
- existe um único H1;
- busca e ação de anunciar estão presentes;
- o menor controle principal medido possui 44 px;
- categorias possuem rolagem interna controlada quando necessário.

## 8. Acessibilidade

Itens implementados e verificados:

- HTML semântico com `header`, `nav`, `main`, `section`, `article`, headings e `footer`;
- um único H1;
- hierarquia H1, H2 e H3 coerente;
- labels visíveis para busca e categoria;
- foco visível com `--mc-focus` e `--mc-shadow-focus`;
- alvos mínimos de 44 × 44 px;
- categoria atual indicada por texto, contraste e `aria-current`;
- ícones decorativos ocultos da árvore acessível;
- imagens de produto com texto alternativo;
- botões e links com rótulos descritivos;
- conteúdo de afiliado identificado;
- suporte a `prefers-reduced-motion: reduce`;
- menu mobile baseado em elementos nativos `details` e `summary`;
- ordem do DOM preservada em todos os breakpoints;
- ausência de rolagem horizontal da página.

Combinações de cor principais utilizam pares aprovados pelo MDS:

- Primary sobre White: 7,27:1;
- Text Primary sobre Surface: 16,54:1;
- Text Secondary sobre Surface: 5,09:1;
- Text Primary sobre Secondary: 8,31:1.

## 9. Checklist MDS

### 9.1 Itens aprovados

- [x] ação principal evidente;
- [x] conteúdo local antes de parceiro e planos;
- [x] componentes oficiais aplicados;
- [x] tokens oficiais de cor, tipografia, espaçamento, raio, sombra, dimensão e movimento;
- [x] container máximo de 1180 px;
- [x] gutters mobile, tablet e desktop;
- [x] validação em 320, 360, 390, 768, 1280 e 1440 px;
- [x] nenhuma rolagem horizontal da página;
- [x] ordem visual e ordem do DOM coerentes;
- [x] Inter com fallbacks oficiais;
- [x] único H1;
- [x] inputs com 16 px no mobile;
- [x] botões com verbos específicos;
- [x] labels não substituídas por placeholder;
- [x] paleta e contrastes aprovados;
- [x] controles e alvos de toque com pelo menos 44 px;
- [x] ícones Lucide outline;
- [x] foco visível;
- [x] estados atuais indicados semanticamente;
- [x] publicidade e afiliação identificadas;
- [x] tempos e curvas do MDS;
- [x] preferência por redução de movimento respeitada;
- [x] testes automatizados atualizados;
- [x] nenhuma exceção bloqueadora identificada.

### 9.2 Itens pendentes ou com ressalva

- [ ] Teste manual completo com leitor de tela dedicado. A árvore de acessibilidade foi inspecionada, mas não substitui uma sessão completa com NVDA ou equivalente.
- [ ] Validação manual de zoom a 200%. Reflow foi validado em 320 CSS px, que cobre a principal reorganização responsiva.
- [ ] Exibir a descrição comercial real em cada card de loja. O view model atual da Home não disponibiliza essa informação, e o backend foi preservado conforme o escopo. Foi usada uma descrição contextual neutra.
- [ ] Auditoria automatizada integral de WCAG. Contrastes principais, semântica, foco, toque e reflow foram verificados nesta Sprint.

Nenhuma ressalva acima representa bloqueador visual ou regressão funcional da entrega atual.

## 10. Testes executados

### 10.1 Qualidade de código

- `git diff --check`: aprovado;
- `python -m ruff check .`: aprovado;
- `python -m ruff format --check .`: aprovado.

### 10.2 Testes automatizados

- Comando: `python -m unittest discover -s tests -p 'test_*.py' -v`
- Total: **81 testes**
- Aprovados: **81**
- Falhas: **0**
- Erros: **0**

Foi adicionado um teste específico para preservar:

- classe de escopo da Home;
- mensagem principal;
- labels visíveis;
- estado atual das categorias;
- heading semântico dos produtos;
- nome acessível do grupo de informações do anúncio.

## 11. Arquivos da Sprint

- `static/styles.css`
- `templates/base.html`
- `templates/index.html`
- `tests/test_moderacao.py`
- `RELATORIO_MDS_SPRINT_002_HOME.md`

## 12. Confirmação de preservação

Esta Sprint não alterou:

- `app.py`;
- `database.py`;
- arquivos de banco;
- rotas;
- consultas;
- pedidos;
- estoque;
- autenticação;
- reputação;
- rastreabilidade;
- regras de planos;
- regras ou fluxo de anúncios;
- dados exibidos dos anúncios, além da correção textual de pluralização da disponibilidade.

O arquivo local não rastreado `RELATORIO_AUDITORIA_UX_MERCADO_COLATINA.md` foi preservado e permanece fora do escopo desta Sprint.

## 13. Conclusão

A Home agora expressa visualmente o Mercado Design System 1.0: mais clara, local, organizada, profissional e consistente. A busca e o anúncio permanecem evidentes, os produtos continuam aparecendo cedo e a experiência mobile recebeu o maior ganho de eficiência.

A entrega está pronta para revisão do responsável. Nenhuma publicação foi realizada.
