# RELATÓRIO — OS 009 — DASHBOARD EXECUTIVO v1.0

**Projeto:** Mercado Colatina

**Organização:** Mercado One Tecnologia

**Ordem de Serviço:** Nº 009

**Data:** 13 de julho de 2026

**Status:** implementação concluída, dependência integrada e Pull Request Draft atualizada

---

## 1. Resumo executivo

O Dashboard Executivo v1.0 foi criado como uma visão administrativa, somente leitura, destinada ao fundador e aos administradores do Mercado Colatina. A tela concentra métricas de dimensão, atividade, marketplace e sistema sem criar banco, tabela, coluna, model, API ou regra de negócio.

O Dashboard reutiliza os indicadores de saúde e operação já consolidados pelo Cockpit Executivo e acrescenta três leituras de marketplace calculadas a partir dos registros existentes: categorias mais utilizadas, produtos mais recentes e lojas mais recentes.

A implementação utiliza a rota administrativa existente:

`/admin?visao=dashboard`

Não foi criada uma rota `/dashboard`. O acesso permanece protegido pela autenticação e pela permissão administrativa já existentes.

---

## 2. Objetivo e ação principal

### Objetivo

Permitir que o fundador identifique rapidamente:

- o tamanho atual da base;
- a atividade recente;
- a composição do marketplace;
- a saúde e a versão do sistema.

### Ação principal

**Consultar os indicadores atuais do Mercado Colatina.**

O Dashboard não executa operações. Todos os links presentes são navegações para páginas já existentes ou para o Health Check.

---

## 3. Arquitetura

### 3.1 Visão administrativa existente

O Dashboard foi incorporado como uma nova apresentação da rota `/admin`, selecionada pelo parâmetro `visao=dashboard`.

Essa decisão preserva:

- o controle de acesso administrativo;
- o Painel Administrativo original;
- o Cockpit Executivo;
- as rotas públicas e autenticadas;
- as regras permanentes de autenticação e autorização.

### 3.2 Camada de dados

A função `montar_dashboard_executivo` reutiliza `montar_cockpit_executivo` e executa somente consultas `SELECT` para compor os dados adicionais.

Não existem no Dashboard:

- `INSERT`;
- `UPDATE`;
- `DELETE`;
- `COMMIT`;
- formulário;
- botão de alteração;
- chamada a API operacional.

Um teste específico compara as quantidades de usuários, anúncios e pedidos antes e depois da renderização da tela, confirmando que permanecem inalteradas.

### 3.3 Dependência da Sprint

A OS-009 foi construída sobre o Cockpit Executivo v1.0. A dependência foi integrada à `master` pela PR #35 no commit `5b00494248b990ca7b3570b6ba88a6a4f8ac751a`, após aprovação do CI e validação do deploy em produção. Em seguida, a branch da PR #36 foi reconstruída sobre a nova `master`, mantendo no comparativo exclusivamente os seis arquivos da OS-009.

---

## 4. Painéis implementados

### 4.1 Visão geral

| Indicador | Definição | Fonte existente |
|---|---|---|
| Usuários cadastrados | total de contas registradas | `usuarios` |
| Lojas cadastradas | usuários com `loja_nome` preenchido | `usuarios` |
| Anúncios ativos | anúncios com `ativo=1` | `anuncios` |
| Pedidos | total histórico de pedidos | `pedidos` |
| Solicitações de compra | pedidos no estado `aguardando` | `pedidos` |

### 4.2 Atividade

São exibidos os cinco registros mais recentes de cada conjunto:

- últimos anúncios, incluindo estado ativo ou inativo na consulta operacional já existente;
- últimos usuários;
- últimos pedidos.

Os registros são ordenados por data de criação e identificador, do mais recente para o mais antigo.

### 4.3 Marketplace

#### Categorias mais utilizadas

Ranking das cinco categorias com maior quantidade de anúncios ativos. Categorias legadas sem acento são normalizadas pela função oficial `categoria_label`, evitando duplicidade visual entre nomes equivalentes.

#### Produtos mais recentes

Cinco anúncios ativos mais recentes, com título, categoria, vendedor e preço. Cada item direciona para a Página do Produto existente.

#### Lojas mais recentes

Cinco usuários mais recentes que possuem `loja_nome` preenchido. Como o sistema não possui data independente de criação da loja, a ordenação utiliza `usuarios.criado_em`, sem criar campo novo. Cada item direciona para o Perfil Público da Loja existente.

### 4.4 Sistema

| Indicador | Origem |
|---|---|
| Health Check | endpoint existente `/health` |
| Último deploy | `RENDER_DEPLOY_ID`; na ausência, versão pelo commit |
| Último commit | `RENDER_GIT_COMMIT` ou `GIT_COMMIT` |
| CI | `CI_STATUS` |
| Testes | `CI_TEST_COUNT` ou contagem dos testes existentes |

Na ausência de metadado operacional, a interface informa “Não informado”, sem fabricar estado positivo.

---

## 5. Design e Mercado Design System

O Dashboard foi implementado conforme o Mercado Design System 1.0.

### Estrutura visual

- hero executivo claro e objetivo;
- cartões grandes para métricas;
- quatro seções numeradas;
- amplo espaço entre seções;
- fundo neutro e superfícies brancas;
- sombras discretas;
- números com alinhamento e leitura tabular;
- hierarquia H1 → H2 → H3;
- ícones Lucide no padrão outline e `stroke-width: 2`;
- estados positivos acompanhados de texto, não apenas cor.

### Tokens

Todos os valores visuais utilizam tokens existentes do MDS para:

- cores;
- tipografia;
- espaçamento;
- raios;
- bordas;
- sombras;
- dimensões;
- foco.

Nenhum token novo foi criado.

### Estados vazios

Os painéis apresentam mensagens humanas e específicas quando não há anúncios, pedidos, produtos, lojas ou categorias. A ausência de dados não é tratada como erro.

---

## 6. Acessibilidade

Validações realizadas:

- um único H1;
- quatro regiões semânticas nomeadas com `aria-labelledby`;
- hierarquia de títulos sem salto;
- ícones decorativos ocultos com `aria-hidden`;
- links com texto que identifica o destino;
- foco visível definido com `--mc-focus` e `--mc-shadow-focus`;
- área mínima de 44 px nos links internos do Dashboard;
- navegação não dependente de hover;
- estado atual “Dashboard” identificado com `aria-current="page"`;
- ordem do DOM igual à ordem visual;
- ausência de formulários e controles sem função consultiva.

---

## 7. Responsividade

Validação realizada em navegador real:

| Largura | Resultado | Rolagem horizontal |
|---:|---|---|
| 320 px | aprovado | não |
| 360 px | aprovado | não |
| 390 px | aprovado | não |
| 768 px | aprovado | não |
| 1024 px | aprovado | não |
| 1440 px | aprovado | não |

No mobile, métricas e sistema passam para uma coluna. As listas mantêm título, contexto e data legíveis, sem alterar a ordem de leitura. No tablet e desktop, o grid aumenta progressivamente o aproveitamento horizontal.

---

## 8. Testes

### Testes específicos adicionados

1. acesso exclusivo para administrador;
2. preservação do Painel Administrativo e das rotas existentes;
3. presença de um único H1 e ausência de formulários;
4. métricas da Visão Geral;
5. atividade recente;
6. normalização e ranking de categorias;
7. produtos e lojas recentes;
8. indicadores do sistema;
9. seções semânticas;
10. presença dos estilos responsivos;
11. confirmação de que a renderização não grava usuários, anúncios ou pedidos.

### Resultado local

- **88/88 testes aprovados**;
- Ruff aprovado;
- formatação aprovada;
- `git diff --check` aprovado;
- Dashboard renderizado com HTTP 200;
- Health Check local com HTTP 200;
- nenhuma regressão encontrada na suíte existente.

O CI remoto será executado novamente após a publicação da branch atualizada. Seu resultado final deve ser confirmado na entrega da missão. O merge e o deploy da PR #36 permanecem fora deste escopo.

---

## 9. Arquivos da OS-009

| Arquivo | Alteração |
|---|---|
| `app.py` | composição somente leitura e seleção da visão Dashboard |
| `templates/dashboard_executivo.html` | nova tela executiva |
| `templates/base.html` | acesso administrativo ao Dashboard |
| `static/styles.css` | layout MDS e responsividade |
| `tests/test_moderacao.py` | testes específicos e proteção contra escrita |
| `RELATORIO_OS_009_DASHBOARD_EXECUTIVO.md` | documentação da missão |

Os relatórios de auditoria não pertencem ao escopo da OS-009 e permanecem fora do commit e da Pull Request.

---

## 10. Confirmações obrigatórias

- **Banco preservado:** confirmado. Nenhuma tabela, coluna, migration ou arquivo de banco foi alterado.
- **Models preservados:** confirmado. Nenhum model foi criado ou modificado.
- **Regras preservadas:** confirmado. Nenhuma regra de negócio foi alterada.
- **Autenticação preservada:** confirmado. O Dashboard utiliza a verificação administrativa existente.
- **Pedidos preservados:** confirmado. Pedidos são apenas consultados.
- **Estoque preservado:** confirmado. Nenhuma consulta ou alteração de estoque foi adicionada.
- **APIs preservadas:** confirmado. Nenhuma API foi criada ou modificada.
- **Dados apenas de leitura:** confirmado por arquitetura e teste automatizado.
- **Merge:** não realizado.
- **Deploy:** não realizado.

---

## 11. Conclusão

O Dashboard Executivo v1.0 entrega uma leitura clara do crescimento, da atividade, da composição do marketplace e da saúde técnica do Mercado Colatina. A solução respeita o MDS, funciona de 320 a 1440 px, utiliza exclusivamente dados existentes e não cria capacidade operacional nova.

A dependência do Cockpit Executivo foi integrada e validada em produção. A OS-009 está isolada na PR #36 e pronta para auditoria em Pull Request Draft, condicionada apenas à confirmação do novo CI remoto. Nenhum merge ou deploy da PR #36 foi realizado.
