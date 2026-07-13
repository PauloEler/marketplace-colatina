# RELATÓRIO MX-003 — MARKETPLACE EXPERIENCE

## 1. Resumo executivo

A MX-003 refinou transversalmente a experiência do Mercado Colatina sem criar funcionalidades e sem alterar banco de dados, autenticação, pedidos, estoque, reputação, permissões, APIs, rotas ou regras de negócio.

A Sprint criou uma camada única de experiência para todas as telas, padronizando microinterações, foco, alvos de toque, feedback semântico, carregamento perceptível, estados vazios, hierarquia e comportamento responsivo. A implementação usa os tokens do Mercado Design System e preserva as interfaces especializadas já entregues para Home e Página do Produto.

A validação automatizada alcançou 85/85 testes aprovados. A inspeção em navegador cobriu as larguras de 320, 360, 390, 768, 1024 e 1440 px, além das principais jornadas públicas e autenticadas.

## 2. Pré-requisito concluído

Antes da abertura da MX-003, a MX-002 foi integrada oficialmente:

- Pull Request: `#33 — MX-002 — Home Premium`;
- método: rebase, preservando histórico linear;
- hash final na `master`: `ba91cd856d426a2adae4803e283d113ce4a6a76a`;
- CI pós-merge: aprovado;
- deploy automático: concluído;
- Health Check: HTTP 200, `{"status":"ok"}`;
- Home Premium e logo v0.9 confirmadas em produção;
- busca, navegação desktop/mobile e console validados;
- MX-003 criada a partir da `master` efetivamente publicada.

## 3. Diagnóstico inicial

A auditoria encontrou uma base funcional e segura, porém com acabamento desigual entre as telas mais recentes e áreas herdadas:

- transições estavam definidas globalmente, mas componentes especializados usavam tempos e respostas diferentes;
- alguns botões administrativos possuíam área visual inferior ao mínimo de toque;
- o foco não incluía todos os controles expansíveis;
- não existia atalho para pular diretamente ao conteúdo principal;
- o menu não indicava programaticamente a página atual;
- mensagens de sucesso e erro tinham aparência simples e não possuíam ícones consistentes;
- aviso e informação ainda não tinham variantes globais completas;
- formulários não apresentavam loading quando a resposta demorava;
- imagens reservavam espaço, mas não ofereciam skeleton durante espera real;
- alguns estados vazios informavam apenas ausência, sem explicar o próximo passo;
- Login, Cadastro, Criação de anúncio e Painel Administrativo não possuíam H1;
- o Painel Administrativo saltava níveis de títulos;
- imagens equivalentes utilizavam combinações diferentes de `loading` e `decoding`;
- o token de aviso usado como texto sobre a superfície amarela resultava em contraste de 4,35:1, ligeiramente abaixo do mínimo para texto normal.

## 4. Microinterações

### 4.1 Movimento padronizado

- transições comuns usam `--mc-duration-base`, equivalente a 180 ms;
- cores, fundos, bordas, sombras, opacidade e transformações compartilham a curva `--mc-ease-standard`;
- botões usam resposta pressionada discreta, sem deslocamento exagerado;
- cards ganham elevação de 2 px somente em dispositivos que realmente possuem hover;
- a interface continua completamente utilizável sem hover;
- `prefers-reduced-motion: reduce` remove deslocamentos, loops e transições não essenciais.

### 4.2 Botões e controles

- botões e ações equivalentes possuem mínimo de 44 px;
- active, hover, focus, disabled e loading receberam comportamento consistente;
- estado disabled remove elevação e comunica indisponibilidade visualmente;
- loading preserva as dimensões originais do botão;
- botões submetidos ficam protegidos contra novo acionamento enquanto a navegação está em andamento.

### 4.3 Cards, categorias e navegação

- cards de produto, loja, pedido, conta, comunicação e reputação usam a mesma cadência de transição;
- categorias preservam o tratamento Premium da Home e passam a compartilhar as regras globais de foco e movimento;
- a página atual recebe `aria-current="page"` na navegação desktop e mobile;
- quando dois links compartilham destino, somente o link semanticamente principal recebe o estado atual;
- componentes `details/summary` sincronizam `aria-expanded` com o estado aberto ou fechado.

## 5. Feedback visual

Foi criado um componente global para quatro estados:

| Estado | Uso | Região viva | Tratamento |
|---|---|---|---|
| Sucesso | ação realmente concluída | `polite` | verde e ícone de confirmação |
| Erro | falha que exige correção | `assertive` | vermelho e ícone de erro |
| Aviso | atenção sem falha imediata | `polite` | superfície amarela e ícone de alerta |
| Informação | orientação neutra | `polite` | azul e ícone de informação |

Os ícones seguem o padrão outline, `stroke-width: 2`, usam `currentColor` e são ocultados de leitores de tela por serem decorativos. O texto continua sendo a fonte principal da mensagem.

O aviso usado durante a criação assistida de anúncio passou a utilizar o mesmo componente global, eliminando um bloco visual isolado.

## 6. Estados vazios

### Administração

- Fundadores: explica quando os usuários elegíveis aparecerão;
- Comunicados: orienta a criação do primeiro aviso;
- Denúncias: informa que solicitações de análise aparecerão na lista;
- Pagamentos: explica o destino das próximas solicitações;
- Pedidos: informa que estados e históricos serão apresentados quando houver registros.

### Minha Loja

- filtro sem anúncios passou a explicar a situação;
- oferece “Ver todos os anúncios” e “Publicar novo anúncio” como caminhos de recuperação;
- grupos de pedidos vazios mencionam a etapa específica;
- cada grupo explica quando uma negociação passará a aparecer ali.

### Estados já adequados e preservados

- Home com limpeza de filtros e retorno às ofertas;
- perfil público da loja com recuperação de busca;
- Meus Anúncios com publicação inicial;
- Pedidos com caminhos para explorar ofertas e gerenciar anúncios.

## 7. Loading e Skeleton

### Formulários

- formulários POST aguardam 300 ms antes de exibir loading, evitando cintilação em respostas rápidas;
- o formulário recebe `aria-busy="true"` somente quando a espera se torna perceptível;
- o botão mantém largura e altura, recebe spinner e fica indisponível para novo envio;
- o estado é restaurado quando a página retorna do cache do navegador;
- parâmetros, campos enviados, CSRF e destinos permanecem inalterados.

### Imagens

- skeleton é ativado somente quando a imagem ainda não terminou de carregar;
- o container recebe `aria-busy="true"` durante a espera;
- load e error removem imediatamente o skeleton;
- o efeito respeita `prefers-reduced-motion`;
- cards, galeria do produto, pedidos, Minha Loja, Meus Anúncios e confirmação de pedido estão cobertos;
- `loading="lazy"` foi padronizado para imagens abaixo da primeira dobra;
- `decoding="async"` foi aplicado às imagens equivalentes;
- proporções e espaços existentes foram preservados, evitando saltos visuais.

## 8. Acessibilidade

### Foco e teclado

- foco visível de 2 px utiliza `--mc-focus` e `--mc-shadow-focus`;
- links, botões, inputs, selects, textareas e summaries estão cobertos;
- foi adicionado “Pular para o conteúdo principal” como primeiro link da página;
- o `main` possui destino identificável e foco programático;
- controles expansíveis expõem `aria-expanded` real;
- mensagens usam `role="status"` ou `role="alert"` conforme a urgência;
- botões icon-only existentes mantêm nomes acessíveis;
- nenhum fluxo passou a depender somente de cor.

### Hierarquia

- Login passou a possuir H1 “Entrar”;
- Cadastro passou a possuir H1 “Criar conta”;
- Criação de anúncio passou a possuir H1 “Criar anúncio”;
- Painel Administrativo recebeu H1, contexto e subtítulo;
- seções principais do Painel Administrativo passaram a usar H2;
- estados vazios preservam H3 dentro de suas respectivas regiões.

### Contraste medido

| Combinação | Resultado | WCAG AA |
|---|---:|---|
| Primary `#17633D` sobre branco | 7,27:1 | Aprovado |
| Texto principal `#17211B` sobre branco | 16,54:1 | Aprovado |
| Texto secundário `#65716A` sobre branco | 5,09:1 | Aprovado |
| Danger sobre superfície Danger | 5,68:1 | Aprovado |
| Info sobre superfície Info | 5,38:1 | Aprovado |
| Texto principal sobre superfície Warning | 15,01:1 | Aprovado |

O texto do aviso foi alterado do token Warning para Text Primary porque a combinação anterior media 4,35:1. A borda, o fundo e o ícone continuam comunicando o estado Warning com tokens semânticos.

## 9. Consistência visual

- todos os refinamentos são isolados pela classe `mds-experience` aplicada no template base;
- Home e Página do Produto continuam preservando seus escopos MDS especializados;
- controles usam borda, raio, superfícies e foco oficiais;
- cards compartilham sombra e transição oficiais;
- botões administrativos pequenos agora respeitam a área mínima de toque;
- textos longos recebem quebra segura;
- containers flexíveis recebem `min-width: 0` para evitar overflow acidental;
- checkboxes e radios usam cor oficial e mantêm labels clicáveis com área adequada;
- a experiência de páginas internas permanece visualmente compatível com a Home Premium.

## 10. Validação responsiva

### Larguras obrigatórias

| Largura | Overflow horizontal | Menor controle relevante | Resultado |
|---:|---|---:|---|
| 320 px | Não | 44 px | Aprovado |
| 360 px | Não | 44 px | Aprovado |
| 390 px | Não | 44 px | Aprovado |
| 768 px | Não | 44 px | Aprovado |
| 1024 px | Não | 44 px | Aprovado |
| 1440 px | Não | 44 px | Aprovado |

Checkboxes e radios permanecem visualmente com 20 px, dentro de labels clicáveis com área mínima de 44 px.

### Telas inspecionadas

- Home;
- Login;
- Cadastro;
- Página do Produto;
- Perfil público da loja;
- Ajuda;
- Painel Administrativo;
- Minha Loja;
- Pedidos;
- Meus Anúncios;
- Minha Conta.

Foram confirmados:

- um H1 nas jornadas principais;
- ausência de rolagem horizontal;
- controles com área adequada;
- feedback de login como `role="status"`;
- details com `aria-expanded` sincronizado;
- menu móvel e página atual;
- imagens carregadas sem estado busy residual;
- console do navegador sem erros.

## 11. Testes

### Automatizados

- comando: `python -m unittest discover -s tests -v`;
- resultado: **85/85 testes aprovados**;
- novo teste: contrato global de feedback, foco, loading e estrutura de experiência;
- regressões encontradas: nenhuma.

### Qualidade estática

- Ruff: aprovado;
- formatação Ruff: aprovada;
- sintaxe de `experience.js`: aprovada;
- tokens CSS inexistentes: nenhum;
- `git diff --check`: aprovado.

## 12. Arquivos da Sprint

- `RELATORIO_MX_003_MARKETPLACE_EXPERIENCE.md`;
- `static/experience.js`;
- `static/styles.css`;
- `templates/base.html`;
- `templates/admin.html`;
- `templates/login.html`;
- `templates/cadastro.html`;
- `templates/criar.html`;
- `templates/comprar.html`;
- `templates/editar.html`;
- `templates/loja_publica.html`;
- `templates/meus_anuncios.html`;
- `templates/painel_vendedor.html`;
- `templates/pedidos.html`;
- `tests/test_moderacao.py`.

O arquivo local `RELATORIO_AUDITORIA_UX_MERCADO_COLATINA.md` não pertence à Sprint e permanece fora do versionamento.

## 13. Confirmações de escopo

Confirma-se explicitamente que a MX-003:

- não criou funcionalidade de negócio;
- não alterou banco de dados;
- não alterou migrations;
- não alterou models;
- não alterou autenticação;
- não alterou pedidos;
- não alterou estoque;
- não alterou reputação;
- não alterou permissões;
- não alterou APIs;
- não alterou rotas;
- não alterou regras de negócio;
- não alterou `app.py`;
- não disparou deploy da MX-003.

## 14. Conclusão

O Mercado Colatina passa a possuir uma linguagem de interação única em toda a interface. O usuário recebe resposta visual consistente, encontra próximos passos em estados vazios, percebe carregamentos sem saltos e navega com foco e áreas de toque adequadas.

A Sprint melhora fluidez e acabamento sem ampliar o produto funcionalmente. A MX-003 está preparada para commit único, CI remoto e auditoria em Pull Request Draft, sem merge e sem deploy antes da aprovação.
