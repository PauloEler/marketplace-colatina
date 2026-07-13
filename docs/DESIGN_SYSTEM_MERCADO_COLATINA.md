# Mercado Design System 1.0

> **Sigla oficial:** MDS
> **Versão:** 1.0
> **Instituído em:** 13 de julho de 2026
> **Status:** normativo e obrigatório
> **Abrangência:** todas as telas, fluxos, componentes e comunicações visuais do Mercado Colatina

## 1. Autoridade e uso deste documento

O Mercado Design System é a referência oficial para decisões de interface do Mercado Colatina. Toda tela nova e toda alteração visual futura deve obedecer a este documento e ao [MDS Checklist](MDS_CHECKLIST.md).

O `MERCADO_COLATINA_MASTER.md` continua sendo a autoridade máxima de produto e governança. O MDS traduz esses princípios para a experiência visual. Em caso de conflito, a regra de produto prevalece e o MDS deve ser atualizado antes da implementação.

Este documento define o padrão; ele não autoriza mudanças automáticas na interface existente. A adoção técnica dos tokens e componentes será realizada em Sprints próprias, com revisão, testes e migração controlada.

### Regras de governança

1. Nenhuma tela pode ser criada ou modificada sem revisão pelo MDS.
2. Nenhum valor visual novo deve ser introduzido quando já existir um token equivalente.
3. Nenhum componente pode criar uma variante isolada sem necessidade comprovada.
4. Exceções precisam de justificativa registrada, impacto de acessibilidade avaliado e plano para incorporação ou remoção.
5. Mudanças neste documento exigem versão, data, motivo e revisão do checklist.
6. Componentes novos devem resolver um padrão reutilizável, não apenas uma tela específica.

## 2. Filosofia do Design

### 2.1 Missão do Design

Fazer o comércio local parecer simples, confiável e organizado para qualquer pessoa, especialmente em seu primeiro contato e em um celular.

O design deve aproximar pessoas, produtos e lojas de Colatina sem criar aparência burocrática, impessoal ou excessivamente promocional. A interface existe para orientar decisões e reduzir incertezas.

### 2.2 Objetivos

- Comunicar imediatamente que o Mercado Colatina é um marketplace local.
- Tornar ações importantes compreensíveis sem treinamento prévio.
- Reduzir o tempo entre intenção e conclusão da tarefa.
- Dar previsibilidade a estados, preços, disponibilidade, responsabilidades e próximos passos.
- Tratar vendedores, compradores e administradores com a mesma clareza estrutural.
- Construir confiança por meio de consistência, transparência e acessibilidade.
- Funcionar bem em celulares simples, conexões limitadas e diferentes níveis de familiaridade digital.
- Valorizar o comércio local sem imitar interfaces de grandes marketplaces.

### 2.3 Princípios

#### Confiança antes de persuasão

Informações importantes, limites, publicidade, estados e consequências devem ser explícitos. O design não usa urgência artificial, padrões enganosos ou destaque visual desproporcional.

#### Simplicidade com contexto

Simplificar não significa esconder informações necessárias. A tela mostra primeiro o essencial e oferece detalhes progressivamente quando o usuário precisar.

#### Uma prioridade por vez

Cada tela possui uma ação principal evidente. Ações secundárias apoiam o objetivo; ações destrutivas ficam separadas e nunca recebem destaque promocional.

#### Organização visível

Agrupamento, alinhamento, espaçamento e hierarquia devem permitir que o usuário compreenda a página antes de ler cada palavra.

#### Local sem improviso

A proximidade regional aparece na linguagem, nos produtos e nas lojas. A execução visual permanece profissional, estável e tecnologicamente atual.

#### Clareza operacional

Toda ação deve responder: o que acontecerá, com quais dados, em qual estado e qual será o próximo passo.

#### Mobile first

O menor contexto útil é definido primeiro. A ampliação para tablet e desktop melhora o aproveitamento espacial sem mudar a lógica da tarefa.

#### Acessibilidade desde a origem

Acessibilidade não é acabamento. Cor, contraste, foco, semântica, teclado, texto e movimento são decisões iniciais do componente.

### 2.4 Palavras-chave

| Palavra-chave | Tradução visual e comportamental |
|---|---|
| **Confiança** | estados claros, consistência, transparência e ausência de surpresas |
| **Simplicidade** | poucas decisões simultâneas, linguagem direta e ações previsíveis |
| **Organização** | grid consistente, agrupamento e hierarquia reconhecível |
| **Tecnologia** | interface rápida, responsiva, atual e discreta |
| **Comércio local** | proximidade, pessoas e lojas reais, sem aparência genérica |
| **Clareza** | rótulos objetivos, contraste e feedback imediato |
| **Rapidez** | conteúdo principal cedo, menos cliques e carregamento percebido curto |
| **Acessibilidade** | uso possível por teclado, leitores de tela e diferentes capacidades visuais ou motoras |

### 2.5 Tom visual

O tom visual do Mercado Colatina é **local, confiável, claro, acolhedor e profissional**.

- Verde comunica confiança, estabilidade e vínculo local.
- Azul regional chama para ações e cria contraste amigável.
- Fundos claros mantêm leveza e leitura.
- Cartões organizam conteúdo, mas não devem transformar cada texto em uma caixa.
- Bordas e sombras são discretas; profundidade deve informar hierarquia, não decorar.
- Cantos arredondados transmitem proximidade sem aparência infantil.
- Fotografias valorizam produtos reais e nunca recebem filtros que alterem sua percepção.
- A identidade é politicamente neutra e não utiliza símbolos partidários.
- Linguagem visual promocional é reservada a oportunidades reais e claramente identificadas.

## 3. Paleta oficial

### 3.1 Cores funcionais obrigatórias

| Papel | Token | HEX | Uso oficial |
|---|---|---:|---|
| Primary | `--mc-primary` | `#17633D` | marca, ação principal, seleção e navegação prioritária |
| Secondary | `--mc-secondary` | `#6FC2E8` | ação complementar, destaque amigável e contraste regional |
| Success | `--mc-success` | `#18794E` | confirmação, conclusão e estado positivo real |
| Warning | `--mc-warning` | `#A56300` | atenção, pendência e risco reversível |
| Danger | `--mc-danger` | `#B4232C` | erro, bloqueio, risco e ação destrutiva |
| Info | `--mc-info` | `#276A8A` | orientação, novidade e informação contextual |
| Background | `--mc-background` | `#F4F7F5` | fundo geral das páginas |
| Surface | `--mc-surface` | `#FFFFFF` | superfícies elevadas, formulários e áreas de conteúdo |
| Card | `--mc-card` | `#FFFFFF` | fundo padrão de cartões |
| Border | `--mc-border` | `#DDE7E1` | separação neutra e contornos |
| Text Primary | `--mc-text-primary` | `#17211B` | títulos e leitura principal |
| Text Secondary | `--mc-text-secondary` | `#65716A` | metadados, explicações e apoio |
| Disabled | `--mc-disabled` | `#6B756F` | ícone ou texto indisponível, sempre com contexto adicional |
| Hover | `--mc-hover` | `#0E4C2E` | hover da ação primária |
| Focus | `--mc-focus` | `#276A8A` | anel de foco e indicação de navegação por teclado |

### 3.2 Extensões da paleta

| Papel | Token | HEX |
|---|---|---:|
| Primary active | `--mc-primary-active` | `#083821` |
| Primary soft | `--mc-primary-soft` | `#E8F5ED` |
| Primary subtle | `--mc-primary-subtle` | `#F2FAF5` |
| Secondary hover | `--mc-secondary-hover` | `#8BD0EE` |
| Secondary active | `--mc-secondary-active` | `#4CAEDB` |
| Success soft | `--mc-success-soft` | `#E8F5ED` |
| Warning soft | `--mc-warning-soft` | `#FFF4CC` |
| Danger soft | `--mc-danger-soft` | `#FDEBEC` |
| Info soft | `--mc-info-soft` | `#E9F5FB` |
| Border strong | `--mc-border-strong` | `#B9C9BF` |
| Disabled background | `--mc-disabled-bg` | `#E7ECE9` |
| Overlay | `--mc-overlay` | `#17211B` a 64% de opacidade |
| White | `--mc-white` | `#FFFFFF` |

### 3.3 Combinações de contraste aprovadas

| Fundo | Conteúdo | Contraste aproximado | Uso |
|---|---|---:|---|
| Primary `#17633D` | White `#FFFFFF` | 7,27:1 | texto normal e botões |
| Secondary `#6FC2E8` | Text Primary `#17211B` | 8,31:1 | texto normal e botões |
| Success `#18794E` | White `#FFFFFF` | 5,41:1 | texto normal |
| Warning `#A56300` | White `#FFFFFF` | 4,79:1 | texto normal |
| Danger `#B4232C` | White `#FFFFFF` | 6,53:1 | texto normal |
| Info `#276A8A` | White `#FFFFFF` | 5,97:1 | texto normal |
| Surface `#FFFFFF` | Text Primary `#17211B` | 16,54:1 | leitura principal |
| Surface `#FFFFFF` | Text Secondary `#65716A` | 5,09:1 | leitura secundária |

#### Regras de cor

- Nunca usar apenas cor para comunicar estado; combinar texto, ícone ou padrão.
- Não usar branco sobre `--mc-secondary`; o contraste é insuficiente. Usar `--mc-text-primary`.
- Success, Warning, Danger e Info são semânticos e não podem ser usados apenas como decoração.
- Danger não pode competir continuamente com Primary. Ele aparece somente quando existe risco real.
- Texto sobre fundos suaves usa a versão base escura do respectivo estado.
- Links em conteúdo devem ser identificáveis também por sublinhado ou outro indicador persistente.
- Toda combinação não listada deve ser verificada segundo WCAG 2.2 AA antes do uso.

## 4. Tipografia

### 4.1 Família oficial

```css
font-family: Inter, "Segoe UI", Arial, sans-serif;
```

**Inter** é a fonte oficial. `Segoe UI` e `Arial` são alternativas seguras quando a fonte principal não estiver disponível. A interface não deve misturar famílias sem aprovação do MDS.

### 4.2 Hierarquia tipográfica

| Estilo | Mobile | Tablet/Desktop | Peso | Altura de linha | Espaçamento entre letras |
|---|---:|---:|---:|---:|---:|
| H1 | 32 px | 48 px | 800 | 1,15 | −0,03 em |
| H2 | 28 px | 32 px | 800 | 1,20 | −0,02 em |
| H3 | 22 px | 24 px | 750 | 1,30 | −0,01 em |
| H4 | 18 px | 20 px | 700 | 1,35 | 0 |
| Body large | 18 px | 18 px | 400 | 1,60 | 0 |
| Body | 16 px | 16 px | 400 | 1,50 | 0 |
| Small | 14 px | 14 px | 400/600 | 1,45 | 0,005 em |
| Caption | 12 px | 12 px | 500/700 | 1,35 | 0,02 em |
| Button | 14 px | 14 px | 700 | 1,20 | 0,005 em |
| Label | 14 px | 14 px | 650 | 1,35 | 0 |

Pesos válidos: **400**, **500**, **600**, **700**, **750** e **800**. Se o ambiente não suportar peso 750, usar 700; não sintetizar variações visuais inconsistentes.

### 4.3 Regras tipográficas

- Cada página deve possuir um único H1.
- A hierarquia deve seguir a ordem sem saltos motivados apenas pelo tamanho visual.
- Títulos descrevem o conteúdo ou a tarefa; não usam frases genéricas como “Bem-vindo” sem contexto.
- Corpo de texto deve ter entre 45 e 75 caracteres por linha sempre que possível.
- Inputs usam no mínimo 16 px no celular para preservar legibilidade e evitar zoom automático.
- Caixa alta é restrita a rótulos curtos, com espaçamento de pelo menos 0,06 em.
- Não justificar parágrafos.
- Não reduzir texto abaixo de 12 px.
- Preços usam peso 750 ou 800, alinhamento consistente e moeda explícita.
- Números tabulares podem usar `font-variant-numeric: tabular-nums` em métricas e tabelas.

### 4.4 Espaçamento do conteúdo textual

- Título → subtítulo: `--mc-space-1` (8 px).
- Título de seção → conteúdo: `--mc-space-3` (24 px).
- Parágrafo → parágrafo: `--mc-space-2` (16 px).
- Label → controle: 6 a 8 px; preferir `--mc-space-1`.
- Controle → ajuda: `--mc-space-1` (8 px).
- Blocos de leitura longa: máximo de 720 px de largura.

## 5. Grid e layout

### 5.1 Container

- Largura máxima oficial: **1180 px**.
- O container é centralizado e ocupa `100%` da largura disponível.
- Gutter mobile: **16 px**.
- Gutter tablet: **24 px**.
- Gutter notebook e desktop: **32 px**.
- Conteúdo nunca pode encostar na borda física da tela.
- Fundos de seção podem ocupar toda a largura; conteúdo permanece alinhado ao container.

### 5.2 Breakpoints oficiais

| Faixa | Largura | Colunas | Gutter | Uso |
|---|---:|---:|---:|---|
| Mobile | 0–639 px | 4 | 16 px | uma coluna principal, ações e formulários empilhados |
| Tablet | 640–839 px | 8 | 24 px | duas colunas quando o conteúdo permitir |
| Notebook | 840–1199 px | 12 | 32 px | navegação completa e composição intermediária |
| Desktop | ≥1200 px | 12 | 32 px | container de até 1180 px e maior respiro |

Os breakpoints são pontos de reorganização, não alvos de dispositivos específicos. Um componente deve responder ao espaço disponível, e não a nomes comerciais de aparelhos.

### 5.3 Escala de espaçamento

| Token | Valor | Uso típico |
|---|---:|---|
| `--mc-space-0` | 0 | remoção explícita de espaço |
| `--mc-space-half` | 4 px | ajuste interno mínimo e excepcional |
| `--mc-space-1` | 8 px | ícone com texto, ajuda e pequenos grupos |
| `--mc-space-2` | 16 px | padding de controles e grupos relacionados |
| `--mc-space-3` | 24 px | padding de cartões e separação de conteúdo |
| `--mc-space-4` | 32 px | blocos e seções compactas |
| `--mc-space-6` | 48 px | seções principais no mobile |
| `--mc-space-8` | 64 px | seções principais no desktop |

Valores arbitrários como 13 px, 19 px ou 37 px não devem ser criados sem justificativa documentada.

### 5.4 Regras de composição

- Formulários usam uma coluna no mobile.
- Layouts de duas colunas precisam manter ordem lógica quando empilhados.
- O fluxo de leitura no DOM deve corresponder ao fluxo visual.
- Não alterar ordem por CSS de modo que teclado e leitor de tela sigam uma sequência diferente.
- A página não pode produzir rolagem horizontal.
- Conteúdo excepcionalmente largo, como tabela analítica, deve usar adaptação responsiva ou região interna controlada e rotulada.
- O alinhamento principal é à esquerda; centralização é reservada a mensagens curtas, estados vazios e ações isoladas.
- Seções relacionadas ficam mais próximas entre si do que de seções diferentes.

## 6. Design Tokens

Tokens são o contrato visual do MDS. Implementações futuras devem consumir estes nomes, sem duplicar valores em componentes.

```css
:root {
  /* Marca e semântica */
  --mc-primary: #17633D;
  --mc-primary-hover: #0E4C2E;
  --mc-primary-active: #083821;
  --mc-primary-soft: #E8F5ED;
  --mc-primary-subtle: #F2FAF5;
  --mc-secondary: #6FC2E8;
  --mc-secondary-hover: #8BD0EE;
  --mc-secondary-active: #4CAEDB;
  --mc-success: #18794E;
  --mc-success-soft: #E8F5ED;
  --mc-warning: #A56300;
  --mc-warning-soft: #FFF4CC;
  --mc-danger: #B4232C;
  --mc-danger-soft: #FDEBEC;
  --mc-info: #276A8A;
  --mc-info-soft: #E9F5FB;

  /* Superfícies e conteúdo */
  --mc-background: #F4F7F5;
  --mc-surface: #FFFFFF;
  --mc-card: #FFFFFF;
  --mc-border: #DDE7E1;
  --mc-border-strong: #B9C9BF;
  --mc-text-primary: #17211B;
  --mc-text-secondary: #65716A;
  --mc-disabled: #6B756F;
  --mc-disabled-bg: #E7ECE9;
  --mc-hover: #0E4C2E;
  --mc-focus: #276A8A;
  --mc-white: #FFFFFF;
  --mc-overlay: rgba(23, 33, 27, 0.64);

  /* Tipografia */
  --mc-font-family: Inter, "Segoe UI", Arial, sans-serif;
  --mc-font-size-caption: 0.75rem;
  --mc-font-size-small: 0.875rem;
  --mc-font-size-body: 1rem;
  --mc-font-size-body-lg: 1.125rem;
  --mc-font-size-h4: 1.125rem;
  --mc-font-size-h4-lg: 1.25rem;
  --mc-font-size-h3: 1.375rem;
  --mc-font-size-h3-lg: 1.5rem;
  --mc-font-size-h2: 1.75rem;
  --mc-font-size-h2-lg: 2rem;
  --mc-font-size-h1: 2rem;
  --mc-font-size-h1-lg: 3rem;
  --mc-font-weight-regular: 400;
  --mc-font-weight-medium: 500;
  --mc-font-weight-semibold: 600;
  --mc-font-weight-bold: 700;
  --mc-font-weight-strong: 750;
  --mc-font-weight-extrabold: 800;
  --mc-line-height-tight: 1.2;
  --mc-line-height-title: 1.3;
  --mc-line-height-body: 1.5;
  --mc-line-height-reading: 1.6;

  /* Espaçamento */
  --mc-space-0: 0;
  --mc-space-half: 0.25rem;
  --mc-space-1: 0.5rem;
  --mc-space-2: 1rem;
  --mc-space-3: 1.5rem;
  --mc-space-4: 2rem;
  --mc-space-6: 3rem;
  --mc-space-8: 4rem;

  /* Dimensões */
  --mc-container-max: 73.75rem;
  --mc-gutter-mobile: 1rem;
  --mc-gutter-tablet: 1.5rem;
  --mc-gutter-desktop: 2rem;
  --mc-breakpoint-tablet: 40rem;
  --mc-breakpoint-notebook: 52.5rem;
  --mc-breakpoint-desktop: 75rem;
  --mc-control-sm: 2.5rem;
  --mc-control-md: 2.75rem;
  --mc-control-lg: 3rem;
  --mc-touch-target: 2.75rem;
  --mc-icon-sm: 1rem;
  --mc-icon-md: 1.25rem;
  --mc-icon-lg: 1.5rem;

  /* Bordas */
  --mc-border-width: 1px;
  --mc-border-width-strong: 2px;
  --mc-radius-xs: 0.375rem;
  --mc-radius-sm: 0.5rem;
  --mc-radius-md: 0.75rem;
  --mc-radius-lg: 1rem;
  --mc-radius-xl: 1.5rem;
  --mc-radius-pill: 999px;

  /* Elevação */
  --mc-shadow-none: none;
  --mc-shadow-sm: 0 2px 8px rgba(14, 76, 46, 0.08);
  --mc-shadow-md: 0 8px 24px rgba(14, 76, 46, 0.10);
  --mc-shadow-lg: 0 16px 40px rgba(14, 76, 46, 0.16);
  --mc-shadow-focus: 0 0 0 3px rgba(39, 106, 138, 0.30);

  /* Movimento */
  --mc-duration-fast: 120ms;
  --mc-duration-base: 180ms;
  --mc-duration-slow: 280ms;
  --mc-ease-standard: cubic-bezier(0.2, 0, 0, 1);
  --mc-ease-enter: cubic-bezier(0, 0, 0.2, 1);
  --mc-ease-exit: cubic-bezier(0.4, 0, 1, 1);

  /* Camadas */
  --mc-z-base: 0;
  --mc-z-sticky: 100;
  --mc-z-dropdown: 200;
  --mc-z-drawer: 300;
  --mc-z-modal: 400;
  --mc-z-toast: 500;
}
```

### 6.1 Regras dos tokens

- Tokens semânticos são preferidos a tokens base no código de componentes.
- Opacidade não deve ser aplicada a texto para criar cor secundária; usar `--mc-text-secondary`.
- Um token só pode mudar de valor semântico em uma nova versão do MDS.
- Breakpoints são documentados como contrato, mas não devem ser simulados por variáveis CSS dentro de media queries.
- Tokens de componente podem ser criados como alias, por exemplo `--mc-button-primary-bg: var(--mc-primary)`.

## 7. Componentes

### 7.1 Regras comuns

Todo componente possui:

- nome e finalidade inequívocos;
- anatomia documentada;
- variantes limitadas;
- estados default, hover, active, focus, disabled, loading, erro e sucesso quando aplicáveis;
- comportamento mobile;
- rótulo acessível;
- contraste aprovado;
- conteúdo realista em validação, incluindo textos longos e vazios.

### 7.2 Botões

#### Variantes

- **Primary:** uma ação principal por região ou formulário.
- **Secondary:** alternativa importante sem competir com Primary.
- **Outline:** ação complementar em superfície clara.
- **Ghost:** ação de baixo peso visual.
- **Danger:** ação destrutiva confirmada.
- **Link:** navegação textual; não substituir botão de ação.

#### Especificação

- Altura padrão: 44 px; grande: 48 px; pequeno: 40 px apenas em contextos densos.
- Área de toque mínima: 44 × 44 px.
- Padding horizontal: 16 px; grande: 24 px.
- Raio: `--mc-radius-sm` ou `--mc-radius-md`.
- Texto: 14 px, peso 700.
- Ícone: 16 ou 20 px, sempre alinhado e com 8 px de distância.
- Loading preserva a largura do botão e comunica `aria-busy="true"`.
- Disabled precisa ser visual e semanticamente indisponível; explicar o motivo quando ele não for evidente.
- Botões usam verbos específicos: “Publicar anúncio”, “Salvar alterações”, “Cancelar pedido”. Evitar “OK”, “Enviar” e “Continuar” sem contexto.
- Botão destrutivo não ocupa a posição mais fácil por padrão e requer confirmação proporcional ao risco.

### 7.3 Cards

#### Variantes

- **Produto:** imagem, condição, categoria, título, preço, localização e origem.
- **Conteúdo:** título, texto e ação opcional.
- **Métrica:** rótulo, valor e contexto temporal.
- **Interativo:** todo o card pode ser acionável quando existir um único destino.

#### Regras

- Fundo `--mc-card`, borda `--mc-border`, raio `--mc-radius-lg` e sombra `--mc-shadow-sm`.
- Padding interno padrão: 24 px; compacto: 16 px.
- Cards no mesmo grupo mantêm anatomia e alinhamento equivalentes.
- Não aninhar cards apenas para criar decoração.
- Se o card inteiro for um link, ações internas adicionais exigem semântica e foco independentes.
- Imagem de produto usa proporção consistente, `object-fit: cover`, texto alternativo e placeholder oficial.
- Hover não pode ser o único sinal de interatividade.

### 7.4 Inputs e áreas de texto

- Ordem: label, controle, texto de apoio e mensagem de erro.
- Label visível é obrigatório; placeholder não substitui label.
- Altura mínima: 44 px; textarea inicia com pelo menos 96 px.
- Fonte do campo no mobile: 16 px.
- Padding: 12 px vertical e 16 px horizontal.
- Borda default `--mc-border-strong`; foco de 2 px `--mc-focus` mais anel externo.
- Erro usa borda Danger, mensagem específica e associação por `aria-describedby`.
- Campos obrigatórios devem ser indicados em texto; não depender apenas de asterisco.
- Formatação automática não pode impedir colar, editar ou usar tecnologias assistivas.
- Agrupar campos relacionados com `fieldset` e `legend`.

### 7.5 Checkbox

- Controle visual de 20 × 20 px dentro de alvo mínimo de 44 × 44 px.
- Usado para escolhas independentes ou múltiplas.
- Label inteira é clicável.
- Estados: desmarcado, marcado, indeterminado, foco, erro e disabled.
- Não substituir por switch quando a mudança não for imediata.

### 7.6 Radio

- Controle visual de 20 × 20 px dentro de alvo mínimo de 44 × 44 px.
- Usado para escolher exatamente uma opção em um conjunto.
- Grupo possui `fieldset` e `legend` ou nome acessível equivalente.
- Nenhuma opção pré-selecionada quando isso puder induzir uma decisão relevante.

### 7.7 Select

- Compartilha altura, tipografia, borda, label e estados dos inputs.
- Preferir select nativo para listas curtas e conhecidas.
- Autocomplete pesquisável é componente distinto e exige comportamento completo de teclado.
- Opção inicial deve indicar a expectativa: “Todas as categorias” ou “Selecione uma categoria”.
- Não esconder escolhas essenciais em menus excessivamente longos.

### 7.8 Modal

- Usado para decisão curta que interrompe temporariamente o contexto.
- Não usar como página, formulário longo ou fluxo de várias etapas.
- Larguras: 400 px pequena, 600 px média e 800 px grande; mobile ocupa largura disponível com gutter de 16 px.
- Possui título, descrição opcional, conteúdo, ações e fechar claramente identificável.
- Usa `role="dialog"`, `aria-modal="true"` e nome acessível.
- Ao abrir, foco vai para o primeiro elemento útil; Tab fica contido; Escape fecha quando seguro; ao fechar, foco retorna ao acionador.
- Conteúdo de fundo fica inerte e a rolagem da página é bloqueada.
- A ação principal fica à direita no desktop e em largura total no mobile quando necessário.

### 7.9 Drawer

- Usado para navegação, filtros ou tarefa complementar que precisa preservar contexto.
- Largura desktop: 320 a 400 px; mobile: largura total ou quase total.
- Drawer de navegação entra pelo lado inicial da leitura; painel contextual pode entrar pelo lado final.
- Segue as mesmas regras de foco, Escape, overlay e retorno de foco do modal.
- Não usar drawer para esconder a ação principal da página.

### 7.10 Navbar

- Mantém marca, navegação principal e acesso à ação de anunciar.
- Altura de referência: 64 px no mobile e 72 px no desktop.
- Marca sempre retorna à página inicial.
- Item atual usa `aria-current="page"` e diferenciação além de cor.
- No mobile, o botão de menu possui nome acessível, estado expandido e alvo de 44 × 44 px.
- Busca pode ocupar uma faixa própria quando isso melhora a descoberta.
- Evitar mais de cinco destinos primários visíveis.

### 7.11 Footer

- Contém marca, descrição curta, navegação institucional, ajuda, termos e privacidade.
- Links são agrupados por assunto e permanecem legíveis em uma coluna no mobile.
- Não repetir ações principais de forma competitiva.
- Texto sobre fundo profundo usa branco ou branco com opacidade somente quando o contraste permanecer AA.
- Informações legais e de contato precisam ser reais e atualizadas.

### 7.12 Sidebar

- Largura padrão: 256 a 280 px.
- Usada em áreas administrativas ou de gestão com múltiplos destinos persistentes.
- Item ativo combina fundo, peso e indicador visual.
- No mobile, converte-se em drawer; não reduz o conteúdo principal a uma coluna impraticável.
- Grupos possuem rótulos e ordem estável.
- Ícones nunca substituem rótulos em navegação essencial.

### 7.13 Badges

- Comunicam estado curto: “Novo”, “Pendente”, “Concluído”, “Fundador”.
- Tamanho compacto, texto de 12 px e peso 700.
- Usam raio pill e combinação semântica de fundo suave com texto escuro.
- Não são clicáveis.
- Estado não depende apenas de cor; texto é obrigatório.

### 7.14 Tags

- Classificam ou filtram conteúdo: categoria, tema ou atributo.
- Podem ser removíveis ou selecionáveis, desde que o estado seja acessível.
- Tag interativa deve ser botão real, ter alvo mínimo de 44 px e estado `aria-pressed` quando aplicável.
- Não usar badge como tag nem tag como botão genérico.

### 7.15 Alertas

#### Tipos

- Success, Warning, Danger e Info.

#### Regras

- Anatomia: ícone, título opcional, mensagem, ação opcional e fechar quando permitido.
- Alertas críticos persistem até resolução; confirmações simples podem desaparecer após tempo suficiente.
- Mensagens dinâmicas usam `role="status"` para informação ou `role="alert"` apenas quando imediatas e críticas.
- Não empilhar alertas repetidos.
- Escrever causa e próximo passo: “Não foi possível salvar. Verifique sua conexão e tente novamente.”

### 7.16 Tabelas

- Usadas somente quando a comparação entre linhas e colunas é essencial.
- Possuem caption, cabeçalhos semânticos e escopo definido.
- Números são alinhados à direita; texto, à esquerda.
- Ordenação comunica estado e nome acessível.
- No mobile, priorizar cartões ou linhas empilhadas. Quando a tabela precisar manter sua estrutura, usar região interna rolável, rotulada e com indicação visual; nunca causar rolagem horizontal da página.
- Ações por linha são limitadas e possuem rótulo específico.
- Cabeçalho fixo é permitido somente quando não encobrir foco ou conteúdo.

### 7.17 Paginação

- Exibe anterior, próxima, página atual e páginas próximas.
- Usa navegação com `aria-label="Paginação"` e `aria-current="page"`.
- Alvos mínimos de 44 × 44 px.
- No mobile, pode reduzir páginas numéricas, preservando anterior, estado atual e próxima.
- Filtros e posição de rolagem devem permanecer previsíveis após mudança de página.
- Não misturar paginação e carregamento infinito no mesmo conjunto.

### 7.18 Breadcrumb

- Indica localização hierárquica, não histórico de navegação.
- Usa `nav` com nome acessível e lista ordenada.
- Página atual não é link e usa `aria-current="page"`.
- No mobile, preservar pelo menos o nível anterior e o atual; truncar visualmente sem apagar o nome acessível.
- Não usar em hierarquias com apenas um nível.

### 7.19 Loading

- Mostrar após aproximadamente 300 ms para evitar cintilação em respostas rápidas.
- Loading de ação fica no próprio componente e preserva dimensões.
- Loading de página informa “Carregando” a tecnologias assistivas com região viva moderada.
- Bloquear somente a região realmente indisponível.
- Nunca deixar spinner sem limite, mensagem de erro ou possibilidade de nova tentativa.

### 7.20 Skeleton

- Replica a estrutura aproximada do conteúdo, sem simular dados falsos.
- Usado quando o layout é conhecido e a espera é perceptível.
- Animação é sutil e desativada com `prefers-reduced-motion`.
- Não usar em ações instantâneas ou por menos de 300 ms.
- Ao carregar, evitar saltos de layout.

### 7.21 Empty States

- Explicam o que está vazio, por que isso pode ter ocorrido e o que fazer em seguida.
- Anatomia: ícone opcional, título, descrição curta e uma ação principal quando existir solução.
- Exemplos: “Nenhum anúncio publicado” + “Publicar primeiro anúncio”; “Nenhum resultado” + “Limpar filtros”.
- Não culpar o usuário e não transformar ausência de conteúdo em erro.
- Ilustrações são opcionais e nunca substituem texto.

## 8. Ícones

### 8.1 Biblioteca oficial

**Lucide Icons** é a biblioteca oficial do Mercado Colatina.

#### Padrão

- Estilo outline.
- `stroke-width: 2`.
- Cantos e terminações arredondados conforme a biblioteca.
- Tamanhos oficiais: 16, 20 e 24 px.
- Cor herdada do contexto por `currentColor`.
- SVG preferencialmente inline ou por componente centralizado.

#### Regras

- Não misturar Lucide com bibliotecas preenchidas, emojis ou ícones de pesos diferentes.
- Emoji não pode ser usado como controle funcional.
- Ícone decorativo usa `aria-hidden="true"`.
- Ícone sem texto precisa de nome acessível e alvo mínimo de 44 × 44 px.
- Ícone não substitui rótulo em ações críticas ou pouco familiares.
- Logos de parceiros são ativos de marca e não fazem parte da biblioteca de interface.
- Um mesmo conceito usa sempre o mesmo ícone.

## 9. Mobile First

### 9.1 Larguras de referência

- Largura mínima de validação: **320 px**.
- Mobile principal: **360 e 390 px**.
- Tablet: **768 px**.
- Notebook: **1024 px**.
- Desktop: **1280 e 1440 px**.

Validar somente larguras fixas não é suficiente; a interface precisa se adaptar nos intervalos.

### 9.2 Controles e toque

- Altura mínima de botões, inputs, selects e alvos: **44 px**.
- Área de toque mínima: **44 × 44 px**.
- Distância recomendada entre alvos independentes: **8 px**.
- Ações principais podem ocupar largura total no mobile.
- Ícones pequenos devem permanecer dentro de uma área de toque adequada.
- Não depender de hover.

### 9.3 Tipografia e leitura

- Corpo: 16 px.
- Input: 16 px.
- H1: 32 px, com quebra natural e sem cortar palavras importantes.
- Linhas de leitura usam largura disponível com gutter de 16 px.
- Conteúdo não deve exigir zoom para ser entendido ou acionado.

### 9.4 Espaçamento e composição

- Gutter de página: 16 px.
- Espaço entre campos: 16 px.
- Espaço entre grupos: 24 ou 32 px.
- Espaço entre seções principais: 48 px.
- Cards podem reduzir padding de 24 para 16 px, nunca abaixo de 16 px sem contexto denso aprovado.
- Formulários e ações são empilhados por padrão.
- Elementos fixos não podem encobrir conteúdo, foco ou mensagens.
- A primeira informação útil deve aparecer cedo; cabeçalhos promocionais não podem dominar várias telas.

## 10. Acessibilidade

O objetivo mínimo é conformidade com **WCAG 2.2 nível AA**.

### 10.1 Contraste

- Texto normal: mínimo 4,5:1.
- Texto grande: mínimo 3:1.
- Componentes, bordas essenciais e indicadores de foco: mínimo 3:1 contra cores adjacentes.
- Placeholder não pode conter a única instrução necessária.
- Estados disabled continuam legíveis, embora controles inativos tenham exceções normativas de contraste.
- Contraste deve ser medido, não estimado visualmente.

### 10.2 Foco

- Todo elemento interativo exibe foco visível com `:focus-visible`.
- Padrão: contorno de 2 px `--mc-focus`, offset de 2 px e/ou `--mc-shadow-focus`.
- O foco não pode ser removido sem substituto equivalente.
- Cabeçalhos sticky, modais e barras fixas não podem encobrir o elemento focado.
- A ordem de foco segue a ordem lógica da tarefa.

### 10.3 Teclado

- Toda ação é operável por teclado.
- Enter ativa links e botões; Space ativa botões, checkbox e controles compatíveis.
- Escape fecha camadas temporárias quando isso não causar perda de dados.
- Modais e drawers contêm foco; menus seguem padrão reconhecido.
- Não criar atalhos de teclado que conflitem com navegador ou tecnologia assistiva.

### 10.4 Leitores de tela e semântica

- Usar HTML semântico antes de ARIA.
- Manter landmarks: header, nav, main, aside e footer quando aplicáveis.
- Imagens informativas possuem texto alternativo; imagens decorativas usam alt vazio.
- Campos possuem label programaticamente associado.
- Mensagens de erro identificam o campo e explicam a correção.
- Mudanças assíncronas importantes são anunciadas com regiões vivas adequadas.
- Títulos, listas e tabelas refletem a estrutura real.
- Links descrevem o destino; evitar vários “Clique aqui”.

### 10.5 ARIA

- ARIA complementa semântica; não corrige elemento inadequado.
- Estados como `aria-expanded`, `aria-current`, `aria-selected`, `aria-pressed`, `aria-busy` e `aria-invalid` devem refletir o estado visual real.
- Todo `aria-describedby` e `aria-labelledby` aponta para um ID existente.
- `role="alert"` é reservado a mensagens urgentes.
- Componentes compostos seguem padrões reconhecidos do WAI-ARIA Authoring Practices.

### 10.6 Conteúdo inclusivo

- Linguagem simples, respeitosa e sem culpa.
- Instruções não dependem de posição, forma ou cor: evitar “clique no botão verde à direita”.
- Datas, preços e números seguem o contexto brasileiro.
- Mensagens de erro orientam recuperação.
- Siglas incomuns são explicadas na primeira ocorrência.

## 11. Animações e movimento

### 11.1 Tempos oficiais

| Token | Tempo | Uso |
|---|---:|---|
| `--mc-duration-fast` | 120 ms | feedback de botão, cor e foco |
| `--mc-duration-base` | 180 ms | hover, expansão curta e troca de estado |
| `--mc-duration-slow` | 280 ms | modal, drawer e reorganização perceptível |

### 11.2 Curvas

- Padrão: `cubic-bezier(0.2, 0, 0, 1)`.
- Entrada: `cubic-bezier(0, 0, 0.2, 1)`.
- Saída: `cubic-bezier(0.4, 0, 1, 1)`.

### 11.3 Quando usar

- Confirmar relação entre ação e resultado.
- Ajudar a compreender entrada, saída ou mudança de camada.
- Suavizar mudanças de estado sem atrasar a tarefa.
- Indicar carregamento quando a espera for real.

### 11.4 Quando não usar

- Como decoração contínua.
- Para atrasar navegação, confirmação ou conteúdo.
- Em alertas críticos que precisam de leitura imediata.
- Em grandes movimentos de parallax, flashes ou animações que possam causar desconforto.
- Quando `prefers-reduced-motion: reduce` estiver ativo; nesse caso remover deslocamentos, pulsações e loops não essenciais.

Movimentos comuns não devem ultrapassar 300 ms. Exceções precisam demonstrar valor de compreensão, não apenas efeito visual.

## 12. Conteúdo e microcopy

- Usar português brasileiro claro e direto.
- Começar botões com verbo.
- Títulos de página descrevem a tarefa ou o conteúdo.
- Mensagens de confirmação informam o resultado: “Anúncio publicado”.
- Mensagens de erro informam causa conhecida e recuperação.
- Evitar jargão técnico, ironia, excesso de exclamações e caixa alta.
- Não prometer segurança, gratuidade, disponibilidade ou resultado além do que o sistema garante.
- Publicidade, parceria e afiliação são identificadas antes da ação.
- Rótulos iguais mantêm o mesmo significado em todo o produto.

## 13. Regras permanentes

Antes de aprovar qualquer tela, responder:

> **Qual é a ação principal desta tela?**

Toda tela deve possuir:

- hierarquia visual inequívoca;
- contraste aprovado;
- consistência com tokens e componentes;
- título e contexto suficientes;
- estados de carregamento, vazio, erro, sucesso e indisponibilidade quando aplicáveis;
- navegação por teclado e foco visível;
- comportamento mobile first;
- linguagem clara;
- feedback para toda ação;
- próximo passo compreensível.

Nenhum componente pode fugir do padrão apenas por preferência estética. Uma necessidade não atendida deve gerar proposta de evolução do MDS, revisão de acessibilidade e documentação antes da implementação.

## 14. Critério de aprovação de uma interface

Uma interface está pronta para implementação somente quando:

1. a ação principal está identificada;
2. o fluxo e os estados estão documentados;
3. todos os valores usam tokens oficiais;
4. todos os elementos usam componentes existentes ou proposta aprovada;
5. o layout foi pensado desde 320 px;
6. contraste e foco foram verificados;
7. ordem de leitura e teclado são coerentes;
8. textos reais e extremos foram testados;
9. o [MDS Checklist](MDS_CHECKLIST.md) foi preenchido;
10. não existe exceção silenciosa ao Design System.

## 15. Controle de versão

| Versão | Data | Alteração |
|---|---|---|
| 1.0 | 13/07/2026 | Fundação oficial: filosofia, paleta, tipografia, grid, tokens, componentes, ícones, mobile, acessibilidade, movimento e governança |
