# Relatório MDS Sprint 003 — Produto Premium

> **Projeto:** Mercado Colatina
>
> **Sprint:** MDS Sprint 003
>
> **Data:** 14 de julho de 2026
>
> **Mercado Design System:** 1.0
>
> **Status:** concluída, testada e não publicada

## 1. Resumo executivo

A Página do Produto foi reorganizada para tornar a decisão de compra imediata, confiável e previsível, usando integralmente os tokens e componentes do Mercado Design System (MDS).

A mudança visual é claramente perceptível: a fotografia abre o conteúdo; preço, **Solicitar compra** e WhatsApp formam um bloco decisório compacto; resumo, loja, descrição e segurança seguem em ordem progressiva. No celular de 390 px, o CTA principal passou de 988 px para 697 px e o WhatsApp de 1.070 px para 753 px. As duas ações agora aparecem integralmente na primeira tela de 844 px.

Não foram alterados banco de dados, pedidos, estoque, rastreabilidade, autenticação, reputação, regras de negócio, rotas ou lógica da aplicação. A publicação não foi realizada.

## 2. Referências obrigatórias consultadas

- `docs/DESIGN_SYSTEM_MERCADO_COLATINA.md`;
- `docs/MDS_CHECKLIST.md`;
- `MERCADO_COLATINA_MASTER.md`.

Princípios aplicados: confiança antes de persuasão, simplicidade com contexto, uma prioridade por vez, organização visível, clareza operacional, mobile first e acessibilidade desde a origem.

## 3. Diagnóstico anterior

- No mobile de 390 px, o resumo textual aparecia antes da fotografia.
- O CTA começava em 988 px e o WhatsApp em 1.070 px.
- Em 320 px, o CTA começava em 961 px e o WhatsApp em 1.061 px.
- O usuário precisava percorrer conteúdo secundário antes de alcançar as ações.
- A loja e a segurança estavam agrupadas em uma coluna de apoio posterior à descrição, contrariando a hierarquia solicitada.
- A estrutura antiga não protegia em teste a ordem completa imagem → preço → CTA → WhatsApp → resumo → loja → descrição → segurança.

## 4. Solução implementada

### 4.1 Hierarquia

A ordem do DOM e da leitura visual passou a ser:

1. imagem;
2. identificação e preço;
3. ação principal **Solicitar compra**;
4. ação secundária **Conversar no WhatsApp**;
5. resumo do produto;
6. loja e reputação pública;
7. descrição;
8. segurança;
9. produtos relacionados, somente quando a coleção existir;
10. ferramentas secundárias de denúncia ou gerenciamento.

No desktop e notebook, imagem e painel de decisão usam duas colunas, preservando a mesma ordem no DOM. No mobile, os elementos são empilhados sem reordenação por CSS.

### 4.2 Imagem e galeria

- A imagem é a primeira informação do produto.
- Foto única usa `object-fit: contain`, sem corte ou filtro.
- Galeria múltipla mantém a imagem principal e até quatro miniaturas compactas no mobile.
- O placeholder sem foto informa o nome do produto para tecnologias assistivas.
- Todos os links de ampliação possuem nome acessível específico.
- Imagens posteriores usam carregamento adiado.

### 4.3 Ação principal

- Texto preservado conforme requisito: **Solicitar compra**.
- Rota preservada: `/comprar/<id>`.
- Primary Button em largura total, 48 px de altura, Primary, texto White e sombra MDS.
- Estados default, hover, active, focus e disabled implementados.
- Proprietário do anúncio recebe botão nativo desabilitado com motivo associado por `aria-describedby`.
- A microcopy informa que os detalhes serão revisados antes do envio.

### 4.4 WhatsApp

- Rota preservada: `/anuncio/<id>/contato`.
- Mantido imediatamente depois da ação principal.
- Variante Outline reduz competição com o CTA Primary.
- Área de toque de 48 px e foco visível.

### 4.5 Resumo, loja, descrição e segurança

- Resumo reúne disponibilidade, localização, visualizações e ausência de cobrança automática.
- Loja recebeu superfície própria, identificação, link de perfil e indicadores públicos preservados.
- Descrição usa largura de leitura de até 65 caracteres aproximados e `line-height` de leitura.
- Segurança usa alerta Info com ícone Lucide, texto e link específico.
- Denúncia e gerenciamento permanecem depois do fluxo principal, visualmente separados da conversão.

### 4.6 Produtos relacionados

Foi criada a apresentação condicional `produtos_relacionados`, depois de Segurança. A seção não é renderizada quando a coleção não existe ou está vazia. Nenhuma consulta, rota ou regra de recomendação foi adicionada nesta Sprint.

## 5. Componentes MDS aplicados

- Navbar responsiva;
- breadcrumb semântico;
- galeria/card de produto;
- tags de condição e categoria;
- Primary Button;
- Outline Button;
- Disabled Button;
- resumo de produto;
- card de loja;
- badge de loja verificada;
- card de conteúdo;
- alerta Info de segurança;
- formulário de denúncia com select e textarea;
- estado vazio de imagem;
- cards condicionais de produtos relacionados;
- footer;
- ícones Lucide outline com `stroke-width="2"`.

## 6. Tokens utilizados

### Cores

- `--mc-primary`, `--mc-primary-hover`, `--mc-primary-active`;
- `--mc-primary-soft`, `--mc-primary-subtle`;
- `--mc-secondary`, `--mc-secondary-hover`, `--mc-secondary-active`;
- `--mc-success`, `--mc-success-soft`;
- `--mc-info`, `--mc-info-soft`;
- `--mc-danger`;
- `--mc-background`, `--mc-surface`, `--mc-card`;
- `--mc-border`, `--mc-border-strong`;
- `--mc-text-primary`, `--mc-text-secondary`;
- `--mc-disabled`, `--mc-disabled-bg`;
- `--mc-focus`, `--mc-white`.

### Tipografia, espaçamento e dimensão

- `--mc-font-family`;
- escala `--mc-font-size-*`, `--mc-font-weight-*` e `--mc-line-height-*`;
- escala `--mc-space-*`;
- `--mc-container-max` e gutters oficiais;
- `--mc-control-sm`, `--mc-control-md`, `--mc-control-lg`;
- `--mc-touch-target`;
- `--mc-icon-sm`, `--mc-icon-md`;
- `--mc-border-width`, `--mc-border-width-strong`;
- `--mc-radius-md`, `--mc-radius-lg`, `--mc-radius-xl`, `--mc-radius-pill`;
- `--mc-shadow-none`, `--mc-shadow-sm`, `--mc-shadow-md`, `--mc-shadow-focus`;
- `--mc-duration-fast`, `--mc-duration-base`, `--mc-ease-standard`.

## 7. Comparação antes e depois

As posições abaixo são coordenadas verticais em CSS pixels, medidas no navegador a partir do topo do documento com o mesmo produto e uma foto.

| Viewport | CTA antes | CTA depois | Ganho | WhatsApp antes | WhatsApp depois | Rolagem horizontal |
|---|---:|---:|---:|---:|---:|---|
| 320 × 568 | 961 px | 626 px | 335 px | 1.061 px | 682 px | não |
| 360 × 800 | 938 px | 674 px | 264 px | 1.038 px | 730 px | não |
| 390 × 844 | 988 px | 697 px | 291 px | 1.070 px | 753 px | não |
| 768 × 1024 | 723 px | 595 px | 128 px | 823 px | 651 px | não |
| 1024 × 768 | 572 px | 470 px | 102 px | 672 px | 526 px | não |
| 1280 × 720 | 572 px | 566 px | 6 px | 654 px | 622 px | não |
| 1440 × 900 | 572 px | 566 px | 6 px | 654 px | 622 px | não |

### 7.1 Posição do CTA

- Em 390 × 844, CTA e WhatsApp ficaram integralmente na primeira tela.
- Em 360 × 800, CTA e WhatsApp ficaram integralmente na primeira tela.
- Em 320 × 568, ambos aparecem antes de completar duas telas; o CTA foi antecipado em 335 px.
- Em 1280 × 720, imagem, preço, CTA e WhatsApp permanecem simultaneamente visíveis.

### 7.2 Tempo para encontrar a ação principal

Não foi realizado estudo cronometrado com participantes; portanto, segundos de busca não foram inventados. O indicador objetivo adotado foi **tempo até disponibilidade visual do CTA após o carregamento**:

- antes, em 360 e 390 px, a ação exigia rolagem para entrar no viewport;
- depois, a ação está disponível no viewport inicial, sem tempo adicional de rolagem;
- o Primary Button é o único controle preenchido da região e precede imediatamente o WhatsApp Outline.

Assim, o tempo operacional adicional para revelar a ação caiu de uma interação de rolagem para zero interações.

### 7.3 Hierarquia visual

| Critério | Antes | Depois |
|---|---|---|
| Primeiro conteúdo do produto | resumo textual | imagem |
| Prioridade das ações | CTA abaixo de conteúdo secundário | CTA após preço |
| WhatsApp | posterior e competitivo | secundário imediato em Outline |
| Loja | coluna de apoio após descrição | seção própria antes da descrição |
| Segurança | misturada à coluna de apoio | seção própria depois da descrição |
| Relacionados | não previstos na interface | seção condicional na posição definida |

## 8. Responsividade validada

| Largura | Imagem | CTA | WhatsApp | Excesso horizontal | Resultado |
|---:|---:|---:|---:|---:|---|
| 320 px | 133–338 px | 626–674 px | 682–730 px | 0 px | aprovado |
| 360 px | 133–368 px | 674–722 px | 730–778 px | 0 px | aprovado |
| 390 px | 133–390 px | 697–745 px | 753–801 px | 0 px | aprovado |
| 768 px | 157–637 px | 595–643 px | 651–699 px | 0 px | aprovado |
| 1024 px | 157–765 px | 470–518 px | 526–574 px | 0 px | aprovado |
| 1280 px | 157–765 px | 566–614 px | 622–670 px | 0 px | aprovado |
| 1440 px | 157–765 px | 566–614 px | 622–670 px | 0 px | aprovado |

Também foram validados:

- produto sem imagem em 320 px: placeholder de 203 px, zero imagem quebrada e CTA a 562 px;
- produto com cinco imagens em 390 px: cinco links acessíveis, CTA a 697 px e WhatsApp a 753 px;
- título longo real;
- preço com separadores brasileiros;
- ausência de rolagem horizontal em todos os intervalos medidos.

## 9. Acessibilidade — WCAG 2.2 AA

### Semântica e leitores de tela

- idioma `pt-BR` preservado;
- um único H1;
- sequência H1 → H2 sem saltos na página;
- landmarks de banner, navegação, main, article, aside e footer;
- breadcrumb em lista ordenada com `aria-current="page"`;
- regiões nomeadas para galeria, compra, resumo, loja, descrição e segurança;
- imagens com texto alternativo útil;
- ícones decorativos ocultos com `aria-hidden="true"`;
- nenhum ID duplicado;
- nenhuma referência `aria-labelledby` ou `aria-describedby` quebrada.

### Foco, teclado e toque

- links, botões, details, select e textarea são controles HTML nativos;
- ordem do foco acompanha a ordem do DOM e da tarefa;
- `:focus-visible` usa `--mc-focus`, contorno de 2 px, offset de 2 px e `--mc-shadow-focus`;
- botões possuem 48 px de altura;
- demais alvos essenciais respeitam o mínimo de 44 × 44 px;
- há 8 px entre as ações principais;
- a interface não depende de hover;
- o CTA desabilitado possui motivo textual associado.

### Contraste e conteúdo

- Primary/White: aproximadamente 7,27:1;
- Surface/Text Primary: aproximadamente 16,54:1;
- Surface/Text Secondary: aproximadamente 5,09:1;
- estados semânticos sempre usam texto ou ícone além da cor;
- links em conteúdo permanecem sublinhados;
- português brasileiro direto e sem urgência artificial.

### Movimento

- transições usam 120 ms e 180 ms;
- `prefers-reduced-motion: reduce` remove deslocamentos e reduz transições;
- nenhum movimento essencial, flash ou loop foi introduzido.

## 10. Checklist MDS

- [x] ação principal inequívoca;
- [x] uma ação Primary por região;
- [x] ordem visual compatível com a tarefa;
- [x] tokens oficiais de cor, tipografia, espaçamento, raio, sombra, dimensão e movimento;
- [x] container máximo de 1180 px e gutters oficiais;
- [x] mobile first;
- [x] 320, 360, 390, 768, 1024, 1280 e 1440 px;
- [x] sem rolagem horizontal;
- [x] um único H1 e headings sem salto;
- [x] corpo e campos com pelo menos 16 px;
- [x] alvos essenciais com pelo menos 44 × 44 px;
- [x] ícones Lucide outline;
- [x] foco visível;
- [x] HTML semântico antes de ARIA;
- [x] estado sem imagem;
- [x] estado disabled com motivo;
- [x] conteúdo longo e galeria múltipla;
- [x] redução de movimento;
- [x] testes automatizados proporcionais ao risco;
- [x] console sem erros.

Bloqueadores do MDS encontrados: **nenhum**.

Recomendação de auditoria complementar, sem regressão conhecida: sessão com leitor de tela real e conferência em dispositivos físicos Android e iOS antes de publicação.

## 11. Testes executados

### Automatizados

- `python -m ruff check .` — aprovado;
- `python -m ruff format --check .` — aprovado;
- `python -m unittest discover -s tests -v` — aprovado;
- `git diff --check` — aprovado.

Resultado da suíte:

- **84 testes executados**;
- **84 testes aprovados**;
- **0 falhas**;
- **0 erros**;
- tempo da suíte completa: aproximadamente 10,4 segundos.

O teste da Página do Produto foi ampliado para verificar:

- presença do MDS;
- CTA e rotas preservadas;
- ordem imagem → preço → CTA → WhatsApp → resumo → loja → descrição → segurança;
- estados hover, active, focus e disabled;
- adaptação de imagem mobile;
- seção condicional de produtos relacionados;
- estado desabilitado para o proprietário.

### Visuais e estruturais

- sete viewports obrigatórios medidos no navegador;
- estados com uma foto, cinco fotos e sem imagem;
- largura do documento comparada à largura útil em cada viewport;
- árvore semântica inspecionada;
- IDs e referências ARIA auditados;
- console do navegador sem erros ou avisos.

## 12. Arquivos alterados

- `templates/anuncio.html`;
- `static/styles.css`;
- `tests/test_moderacao.py`;
- `RELATORIO_MDS_SPRINT_003_PRODUTO.md`.

Os relatórios não rastreados preexistentes `RELATORIO_AUDITORIA_EDICAO_FUNDADORA.md` e `RELATORIO_AUDITORIA_UX_MERCADO_COLATINA.md` não fazem parte desta Sprint e não foram alterados nem incluídos no commit.

## 13. Escopo protegido

Não houve alteração em:

- `app.py`;
- `database.py`;
- banco de dados versionado;
- pedidos;
- estoque;
- timeline/rastreabilidade;
- autenticação;
- reputação;
- permissões;
- consultas da página;
- rotas;
- regras de negócio.

Rotas preservadas:

- compra: `/comprar/<id>`;
- WhatsApp: `/anuncio/<id>/contato`;
- denúncia: `/anuncio/<id>/denunciar`;
- edição e status: rotas preexistentes.

## 14. Commit e publicação

Mensagem definida: `Aplica Mercado Design System na Página do Produto`.

A publicação, o push, o merge e o deploy não fazem parte desta Sprint e não foram executados. O hash do commit é informado no resumo de entrega após sua criação.

## 15. Conclusão

A Página do Produto agora apresenta o produto antes de pedir uma decisão, concentra preço e ações no primeiro bloco útil e reduz substancialmente a distância até o CTA no celular. A fotografia ganhou protagonismo, o botão **Solicitar compra** tornou-se inequivocamente principal, o WhatsApp permaneceu acessível como ação secundária e as informações de confiança seguem uma progressão clara.

A implementação está pronta para revisão, sem publicação automática e sem regressão conhecida.
