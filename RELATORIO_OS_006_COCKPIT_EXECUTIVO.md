# RELATÓRIO — OS 006 — COCKPIT EXECUTIVO v1.0

**Produto:** Mercado Colatina

**Empresa:** Mercado One Tecnologia

**Data:** 13 de julho de 2026

**Missão:** Cockpit Executivo v1.0

**Design System:** Mercado Design System 1.0

**Status da entrega:** pronta para auditoria em Pull Request Draft

## 1. Resumo executivo

O Cockpit Executivo v1.0 foi criado como uma visão administrativa, somente leitura e orientada ao fundador. A tela reúne saúde do produto, dimensão do marketplace, operação recente, alertas e atalhos para fluxos existentes.

A composição foi desenhada para responder, na primeira tela e em menos de 30 segundos:

1. o sistema está saudável;
2. o marketplace está operando;
3. existe algum problema importante;
4. qual indicador merece atenção hoje.

O Cockpit não contém formulários, não executa comandos e não substitui o painel administrativo. Ele apresenta informações e direciona o administrador aos fluxos já existentes quando necessário.

## 2. Diagnóstico inicial

Antes desta missão, as informações necessárias estavam distribuídas entre:

- painel administrativo;
- área de pedidos;
- área do vendedor;
- endpoint de Health Check;
- metadados do ambiente de execução;
- suíte automatizada do projeto.

O fundador precisava abrir múltiplas áreas e interpretar informações operacionais para formar uma visão geral. O painel administrativo também concentra formulários e ações, o que reduz a velocidade de leitura executiva.

Não existia uma camada exclusivamente consultiva, com hierarquia orientada a decisão e sem risco de operação acidental.

## 3. Arquitetura da solução

### 3.1 Acesso

O Cockpit utiliza a rota administrativa existente:

`/admin?visao=cockpit`

Essa decisão preserva a restrição de não criar ou alterar rotas:

- nenhuma rota nova foi registrada;
- `/admin` continua abrindo o painel administrativo existente;
- o parâmetro `visao=cockpit` seleciona apenas a apresentação consultiva;
- visitantes e usuários comuns continuam redirecionados para a Home;
- somente sessões com perfil administrativo acessam a tela.

### 3.2 Separação de responsabilidades

| Camada | Responsabilidade |
|---|---|
| `app.py` | consultas de leitura, composição dos indicadores e metadados operacionais |
| `templates/cockpit.html` | estrutura semântica e apresentação dos cinco painéis |
| `static/styles.css` | aplicação visual do MDS e responsividade |
| `templates/base.html` | acesso ao Cockpit para administradores |
| `templates/admin.html` | destino identificável para o atalho de usuários |
| `tests/test_moderacao.py` | acesso, isolamento, indicadores, semântica e regressão |

### 3.3 Preservação da operação

Todas as consultas do Cockpit são `SELECT`. A renderização não executa `INSERT`, `UPDATE` ou `DELETE`.

O Cockpit não possui:

- formulários;
- botões de alteração;
- endpoints de escrita;
- comandos administrativos;
- automações operacionais;
- alteração de estado.

## 4. Painéis implementados

### 4.1 Painel 1 — Saúde do produto

Exibe sete cartões:

- status da aplicação;
- Health Check;
- último deploy;
- último commit;
- status do CI;
- quantidade de testes;
- ambiente atual.

O status da aplicação é apresentado como operacional quando a própria tela e suas consultas foram renderizadas com sucesso. O Health Check continua disponível no endpoint existente `/health` e é acessível diretamente pelo cartão.

Metadados de commit e ambiente utilizam variáveis já fornecidas pelo processo de execução, incluindo `RENDER_GIT_COMMIT`, `RENDER_SERVICE_ID` e `RENDER_EXTERNAL_HOSTNAME` quando disponíveis.

O identificador de deploy usa `RENDER_DEPLOY_ID` quando configurado. Na ausência dele, a versão ativa é identificada pelo commit. O CI utiliza `CI_STATUS` quando o ambiente o fornece.

Nenhum estado externo é inventado. Quando o ambiente não fornece uma informação, o cartão mostra **“Não informado”**.

A quantidade de testes usa `CI_TEST_COUNT` quando declarada pelo pipeline. Como alternativa local, conta os testes existentes nos arquivos `test_*.py`, sem executar a suíte durante a abertura da página.

### 4.2 Painel 2 — Marketplace

Os indicadores usam exclusivamente tabelas e colunas existentes:

| Indicador | Definição |
|---|---|
| Anúncios ativos | anúncios com `ativo=1` |
| Usuários cadastrados | total de contas registradas |
| Lojas cadastradas | usuários com nome de loja preenchido |
| Pedidos | total histórico de pedidos |
| Solicitações de compra | pedidos no estado inicial `aguardando` |

Nenhum indicador é persistido ou duplicado. Todos são calculados no momento da consulta.

### 4.3 Painel 3 — Operação

Apresenta os cinco registros mais recentes de cada grupo:

- últimos anúncios, com vendedor e data;
- últimos cadastros, com usuário e data;
- últimos pedidos, com produto, estado e data.

Cada item direciona para uma página de consulta já existente. Nenhuma ação é executada dentro do Cockpit.

Estados vazios foram tratados com mensagens específicas e humanas.

### 4.4 Painel 4 — Alertas

Os alertas aparecem somente quando existe uma condição objetiva já reconhecida pelo produto:

- denúncias pendentes;
- pedidos em análise;
- alertas administrativos por e-mail indisponíveis.

Na ausência dessas condições, a tela apresenta exatamente:

> Nenhum problema importante encontrado.

Alertas possuem texto, ícone e tratamento semântico. Nenhuma informação depende somente de cor.

### 4.5 Painel 5 — Ações rápidas

Foram adicionados atalhos consultivos para fluxos existentes:

- Novo anúncio;
- Minha Loja;
- Pedidos;
- Administração;
- Usuários.

Os atalhos não contornam permissões, não criam ações paralelas e não alteram os destinos existentes.

## 5. Indicador para hoje

A faixa imediatamente abaixo do cabeçalho prioriza uma única informação:

1. primeiro alerta importante existente;
2. solicitações aguardando vendedor, quando não há alertas;
3. confirmação de operação sem alertas importantes.

Essa hierarquia permite que o fundador saiba onde concentrar atenção antes de percorrer os demais painéis.

## 6. Mercado Design System

### 6.1 Fundamentos aplicados

- container oficial de 1180 px;
- gutters de 16, 24 e 32 px;
- escala de espaçamento do MDS;
- cartões com borda, raio e sombras oficiais;
- Inter com fallbacks oficiais;
- verde institucional como base de confiança;
- azul regional para informação e orientação;
- cores semânticas para sucesso, aviso, perigo e informação;
- Lucide Icons em SVG outline, `stroke-width: 2`;
- movimento de 180 ms apenas em atalhos interativos;
- suporte a `prefers-reduced-motion`.

### 6.2 Hierarquia

- um único H1: “Cockpit Executivo”;
- cinco seções numeradas e identificadas por H2;
- cartões e listas identificados por H3;
- ordem visual igual à ordem do DOM;
- informação prioritária antes dos detalhes;
- ausência de gráficos decorativos.

### 6.3 Acessibilidade

- acesso exclusivo preservado;
- landmarks e seções com nomes acessíveis;
- SVGs decorativos ocultos com `aria-hidden`;
- foco visível de 2 px com cor `--mc-focus`;
- offset de foco de 4 px e sombra oficial;
- todos os links internos do Cockpit com alvo mínimo de 44 px;
- um único H1;
- leitura completa disponível sem depender de hover;
- movimento reduzido respeitado;
- alertas comunicados por texto e ícone, além da cor.

## 7. Validação responsiva

Validação realizada no navegador real com sessão administrativa:

| Largura | Resultado |
|---:|---|
| 320 px | aprovado, uma coluna, sem rolagem horizontal |
| 360 px | aprovado, uma coluna, sem rolagem horizontal |
| 390 px | aprovado, uma coluna, sem rolagem horizontal |
| 768 px | aprovado, cartões de saúde em duas colunas |
| 1024 px | aprovado, cartões de saúde em quatro colunas |
| 1440 px | aprovado, container centralizado e leitura executiva ampla |

Em todas as larguras, `scrollWidth` permaneceu igual à largura útil do documento. Não foi encontrada rolagem horizontal.

Também foram verificados:

- títulos longos em 320 px;
- quebra de metadados;
- cartões com valor ausente;
- menu mobile;
- hierarquia na primeira tela;
- alvos de toque;
- foco por teclado;
- console do navegador.

O console permaneceu sem erros.

## 8. Testes

### 8.1 Testes específicos adicionados

1. acesso bloqueado para visitante e usuário comum;
2. acesso permitido para administrador;
3. preservação do painel `/admin` original;
4. confirmação de que nenhuma rota `/cockpit` foi criada;
5. ausência de formulários dentro do Cockpit;
6. cálculo dos cinco indicadores do marketplace;
7. exibição dos metadados de saúde;
8. renderização dos últimos registros;
9. exibição de alertas reais;
10. estrutura semântica e presença dos padrões responsivos.

### 8.2 Resultado

- **86/86 testes aprovados**;
- Ruff aprovado;
- formatação aprovada;
- verificação de diferenças aprovada;
- console do navegador sem erros.

## 9. Arquivos da missão

| Arquivo | Alteração |
|---|---|
| `app.py` | composição somente leitura dos indicadores e seleção da visão Cockpit |
| `templates/cockpit.html` | nova tela executiva |
| `static/styles.css` | camada visual MDS e responsividade |
| `templates/base.html` | atalho administrativo para o Cockpit |
| `templates/admin.html` | âncora do destino Usuários |
| `tests/test_moderacao.py` | testes específicos e de regressão |
| `RELATORIO_OS_006_COCKPIT_EXECUTIVO.md` | relatório oficial da missão |

## 10. Preservação das regras de negócio

Confirmações explícitas:

- banco de dados não alterado;
- nenhuma tabela criada;
- migrations não alteradas;
- models não alterados;
- autenticação não alterada;
- pedidos não alterados;
- estoque não alterado;
- permissões não alteradas;
- reputação não alterada;
- APIs não alteradas;
- nenhuma rota nova criada;
- rotas existentes preservadas;
- regras de negócio preservadas;
- nenhum comportamento operacional alterado;
- nenhuma funcionalidade de escrita criada.

## 11. Critério de aceite

O Cockpit permite responder rapidamente:

- **O sistema está saudável?** Sim, pela faixa de status e pelos cartões de aplicação e Health Check.
- **O Marketplace está operando normalmente?** Sim, pelos cinco indicadores e pela operação recente.
- **Existe algum problema importante?** Sim ou não, pelo Painel de Alertas e pela mensagem de estado limpo.
- **Qual indicador merece atenção hoje?** Pela faixa prioritária imediatamente após o cabeçalho.

## 12. Conclusão

O Cockpit Executivo v1.0 estabelece um centro de leitura para o fundador sem transformar a tela em um painel operacional. A solução reduz a dispersão de informações, preserva integralmente os fluxos existentes e aplica o Mercado Design System em uma experiência premium, clara e responsiva.

A missão está pronta para auditoria em Pull Request Draft. Nenhum merge ou deploy faz parte desta entrega.
