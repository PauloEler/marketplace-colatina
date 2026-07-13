# Relatório MDS Sprint 003 — Página do Produto Premium

> **Projeto:** Mercado Colatina
> **Sprint:** MDS Sprint 003
> **Data:** 13 de julho de 2026
> **Mercado Design System:** 1.0
> **Status:** implementação local concluída e pronta para auditoria
> **Publicação:** não realizada

## 1. Resumo executivo

A Página do Produto foi reconstruída visualmente para representar a nova identidade do Mercado Colatina, sem alterar rotas, dados ou regras de negócio.

A nova experiência apresenta primeiro o contexto necessário para a decisão: classificação, nome, preço, disponibilidade, localização e visualizações. Em seguida, valoriza a fotografia do produto e destaca a ação **Solicitar compra** em um painel próprio, com contraste, hierarquia e orientação sobre o que acontecerá na próxima etapa.

O resultado corrige a principal fragilidade da versão anterior: no desktop, o nome e o preço começavam abaixo da primeira tela, enquanto o botão de compra aparecia isolado na lateral. No mobile, o CTA ficava distante, depois de conteúdo secundário. A nova composição mantém produto, ação e confiança dentro de uma sequência lógica e previsível.

Foram validados desktop, notebook, tablet e celulares desde 320 px, além dos estados com uma foto, cinco fotos e sem imagem. Não foi encontrada rolagem horizontal, erro de console, ID duplicado ou referência ARIA quebrada.

## 2. Escopo e documentos normativos

Antes da implementação foram lidos integralmente:

- `MERCADO_COLATINA_MASTER.md`;
- `docs/DESIGN_SYSTEM_MERCADO_COLATINA.md`;
- `docs/MDS_CHECKLIST.md`.

A Sprint aplicou os seguintes princípios obrigatórios:

- confiança antes de persuasão;
- simplicidade com contexto;
- uma prioridade por vez;
- organização visível;
- clareza operacional;
- mobile first;
- acessibilidade desde a origem;
- uso dos tokens e componentes oficiais do MDS.

## 3. Diagnóstico inicial

### 3.1 Hierarquia

- O nome e o preço do produto apareciam depois da galeria na coluna principal.
- Em 1280 × 720, o H1 começava em aproximadamente 751 px e o preço em 845 px, ambos abaixo da primeira tela.
- O antigo botão **Comprar** aparecia antes do nome e do preço no desktop, criando uma ação sem contexto visual suficiente.
- A descrição ocupava a mesma região do nome e preço, aumentando o tempo até o CTA no mobile.

### 3.2 Ação principal

- O CTA usava o azul Secondary, embora fosse a principal ação da tela.
- O botão de WhatsApp usava verde intenso e competia visualmente com a compra.
- O rótulo **Comprar** não explicava que ainda existia uma etapa de revisão e solicitação.
- Não havia estado desabilitado visível para o próprio vendedor.
- Os estados normal, foco, pressionado e desabilitado não estavam documentados como um conjunto do componente.

### 3.3 Conteúdo e confiança

- Disponibilidade, localização e visualizações eram exibidas como texto corrido e com pouca diferenciação.
- A disponibilidade usava redação inconsistente: “disponivel/disponiveis”.
- O aviso sobre ausência de cobrança automática ficava distante do CTA em alguns tamanhos.
- Informações do vendedor e reputação eram úteis, mas competiam com a decisão principal.
- O aviso de segurança utilizava um símbolo textual em vez da biblioteca oficial de ícones.

### 3.4 Fotografia e galeria

- A fotografia era grande, porém separava o usuário do nome e do preço no desktop.
- A galeria não comunicava explicitamente que cada foto podia ser ampliada.
- O placeholder sem imagem não possuía uma descrição programática específica do produto.
- A composição com várias fotos precisava de uma regra mais consistente no celular.

### 3.5 Mobile e acessibilidade

- Em 390 × 844, o H1 começava em aproximadamente 566 px, o preço em 666 px e o CTA em 1.294 px.
- O texto longo do produto tornava a leitura fragmentada antes da ação principal.
- Metadados não utilizavam ícones Lucide e tinham pouca hierarquia.
- Links secundários não mantinham sempre uma área de toque de 44 px.
- O breadcrumb anterior era apenas um link de retorno, sem identificação estrutural da página atual.

## 4. Solução implementada

### 4.1 Hero premium do produto

Foi criado o componente visual `product-premium`, composto por:

1. introdução do produto;
2. galeria de fotos;
3. painel de solicitação de compra.

No desktop, a introdução ocupa toda a largura útil. Foto e painel de compra ficam lado a lado logo abaixo. Isso permite manter H1, preço e disponibilidade visíveis antes da decisão, sem reduzir a fotografia.

No mobile, a ordem permanece semântica e previsível:

1. nome, preço e disponibilidade;
2. foto;
3. solicitação de compra.

Nenhuma ordem foi invertida visualmente de maneira diferente da ordem do DOM.

### 4.2 Nome, preço e disponibilidade

- H1 único e semântico.
- Tipografia oficial do MDS: 32 px no mobile e 48 px no desktop.
- Preço com peso 800, moeda explícita e números tabulares.
- Disponibilidade apresentada como estado positivo real, com texto e ícone.
- Localização e visualizações organizadas em lista semântica.
- Redação corrigida para “unidade disponível” e “unidades disponíveis”.

### 4.3 Galeria valorizada

- Superfície, borda, raio e sombra oficiais.
- Imagem principal em grande proporção e sem filtros.
- Foto única usa `object-fit: contain` para preservar o produto completo.
- Galerias de duas a cinco fotos usam composição adaptativa.
- No mobile, a primeira foto recebe prioridade e as demais viram miniaturas organizadas.
- Cada imagem possui texto alternativo e link com nome acessível para ampliação.
- O placeholder sem foto informa programaticamente qual produto está sem imagem.

### 4.4 CTA principal

O rótulo passou de **Comprar** para **Solicitar compra**, sem alterar o destino `/comprar/<id>`.

O componente usa:

- fundo Primary `#17633D`;
- texto branco;
- altura de 48 px;
- largura total do painel;
- ícone Lucide consistente;
- sombra MDS para prioridade;
- microcopy explicando a revisão antes do envio.

Estados implementados:

| Estado | Tratamento |
|---|---|
| Normal | Primary com texto branco e sombra média |
| Hover | `--mc-primary-hover`, mantendo contraste |
| Foco | contorno `--mc-focus`, offset de 2 px e `--mc-shadow-focus` |
| Pressionado | `--mc-primary-active`, sem deslocamento |
| Desabilitado | `--mc-disabled-bg`, `--mc-disabled`, sem sombra e cursor indisponível |

Para o proprietário do anúncio, o CTA é exibido como botão nativo desabilitado e associado por `aria-describedby` à explicação: “Este é o seu anúncio. Use as opções de gerenciamento abaixo.”

### 4.5 Ações secundárias

- **Conversar no WhatsApp** passou a usar variante Outline.
- A ação continua apontando para a mesma rota de contato.
- A ação secundária não compete mais com a solicitação de compra.
- O perfil da loja passou a usar o rótulo específico **Abrir perfil da loja**.
- Denúncia e gerenciamento permanecem em áreas separadas da conversão.

### 4.6 Confiança e segurança

- Aviso “Negociação organizada” antes do CTA.
- Explicação clara de que pagamento e entrega serão combinados com o vendedor.
- Informação de que nenhum pagamento é cobrado automaticamente nesta etapa.
- Reputação pública preservada com os mesmos indicadores aprovados.
- Aviso de segurança reorganizado com ícone Shield Check da biblioteca Lucide.
- Links de segurança e denúncia permanecem disponíveis sem destaque promocional.

### 4.7 Descrição e vendedor

- A descrição foi movida para um card próprio, abaixo da área de decisão.
- A largura de leitura foi limitada a 65 caracteres aproximados por linha.
- Tipografia Body de 16 px e altura de linha de leitura 1,6.
- Vendedor, loja e reputação foram agrupados em um card de confiança secundário.
- Ações administrativas permanecem separadas da ação de compra.

## 5. Componentes MDS aplicados

- Navbar responsiva;
- breadcrumb;
- tags de condição e categoria;
- card/superfície de introdução;
- galeria de produto;
- Primary Button;
- Outline Button;
- Disabled Button;
- card de conteúdo;
- card de vendedor;
- badge de loja verificada;
- alerta informativo de segurança;
- inputs, select e textarea da denúncia;
- footer;
- ícones Lucide inline.

## 6. Tokens aplicados

### Cores

- `--mc-primary`;
- `--mc-primary-hover`;
- `--mc-primary-active`;
- `--mc-primary-soft`;
- `--mc-primary-subtle`;
- `--mc-secondary`;
- `--mc-success`;
- `--mc-success-soft`;
- `--mc-danger`;
- `--mc-info`;
- `--mc-info-soft`;
- `--mc-background`;
- `--mc-surface`;
- `--mc-card`;
- `--mc-border`;
- `--mc-border-strong`;
- `--mc-text-primary`;
- `--mc-text-secondary`;
- `--mc-disabled`;
- `--mc-disabled-bg`;
- `--mc-focus`;
- `--mc-white`.

### Tipografia, dimensão e movimento

- família, tamanhos, pesos e alturas de linha `--mc-font-*`;
- escala `--mc-space-*`;
- controles `--mc-control-*`;
- alvo mínimo `--mc-touch-target`;
- ícones `--mc-icon-*`;
- raios `--mc-radius-*`;
- sombras `--mc-shadow-*`;
- durações e curvas `--mc-duration-*` e `--mc-ease-*`;
- container e gutters oficiais.

O token `--mc-space-1` é corrigido somente dentro de `.mds-product` para o valor normativo de 8 px. Isso evita alterar outras telas nesta Sprint.

## 7. Comparação antes e depois

### 7.1 Desktop — 1280 × 720

| Elemento | Antes | Depois | Resultado |
|---|---:|---:|---|
| Início do H1 | 751 px | 238 px | 513 px mais cedo |
| Início do preço | 845 px | 182 px | 663 px mais cedo |
| Início do CTA | 436 px | 572 px | permanece na primeira tela, agora após contexto suficiente |
| Rolagem horizontal | não | não | preservado |

O CTA anterior aparecia cedo, porém isolado do nome e do preço. Depois da Sprint, H1, preço, disponibilidade, foto e CTA convivem na primeira tela.

### 7.2 Mobile — 390 × 844

| Elemento | Antes | Depois | Resultado |
|---|---:|---:|---|
| Início do H1 | 566 px | 206 px | 360 px mais cedo |
| Início do preço | 666 px | 369 px | 297 px mais cedo |
| Início da galeria | 125 px | 545 px | contexto do produto passa a vir antes da foto |
| Início do CTA | 1.294 px | 988 px | 306 px mais cedo |
| Rolagem horizontal | não | não | preservado |

O CTA fica logo após a foto, com o nome, preço e disponibilidade já compreendidos. Essa ordem evita pedir uma decisão antes de o usuário conhecer o produto.

## 8. Validação responsiva final

| Viewport | H1 começa | Galeria começa | CTA começa | Rolagem horizontal | Resultado |
|---|---:|---:|---:|---|---|
| 320 × 568 | 206 px | 528 px | 961 px | não | aprovado |
| 360 × 800 | 206 px | 545 px | 988 px | não | aprovado |
| 390 × 844 | 206 px | 545 px | 988 px | não | aprovado |
| 768 × 1024 | 238 px | 554 px | 723 px | não | aprovado |
| 1024 × 768 | 238 px | 425 px | 572 px | não | aprovado |
| 1280 × 720 | 238 px | 425 px | 572 px | não | aprovado |
| 1440 × 900 | 238 px | 425 px | 572 px | não | aprovado |

Em tablet, foto e painel de compra passam a usar duas colunas quando existe espaço suficiente. Em celulares, os blocos ficam empilhados.

## 9. Casos visuais adicionais

### Produto sem imagem

- Validado em 320 × 568.
- Placeholder com 256 px de altura.
- Nome acessível: “Imagem não enviada para [nome do produto]”.
- Nenhuma rolagem horizontal.

### Produto com cinco imagens

- Validado em 390 × 844.
- Imagem principal com prioridade e quatro miniaturas.
- Galeria com 635 px de altura total.
- Todas as fotos possuem destino de ampliação e texto alternativo.
- Nenhuma rolagem horizontal.

### Conteúdo longo

- Validado com título de 60 caracteres e descrição extensa.
- H1 quebra naturalmente.
- Breadcrumb preserva “Ofertas” e trunca apenas o nome atual.
- Preço, metadados e CTA permanecem dentro do container.

## 10. Acessibilidade

### Estrutura e semântica

- um único H1;
- headings H1 e H2 sem salto estrutural;
- landmarks de header, main, article, aside e footer;
- breadcrumb com lista ordenada e `aria-current="page"`;
- listas semânticas para fatos do produto;
- descrição, compra, vendedor e segurança com nomes acessíveis;
- imagens com `alt` útil;
- SVGs decorativos com `aria-hidden="true"`;
- botão desabilitado nativo com motivo associado;
- nenhum ID duplicado;
- nenhuma referência `aria-labelledby` ou `aria-describedby` quebrada.

### Teclado e foco

- ações essenciais usam links e botões nativos;
- ordem do DOM corresponde à ordem da tarefa;
- foco visível usa `--mc-focus` e `--mc-shadow-focus`;
- todos os alvos interativos visíveis medidos possuem pelo menos 44 px de altura;
- inputs da denúncia usam 16 px no mobile;
- denúncia continua operável por controles nativos.

### Contraste

Foram usadas combinações oficiais já aprovadas pelo MDS:

- Primary sobre White: aproximadamente 7,27:1;
- Surface com Text Primary: aproximadamente 16,54:1;
- Surface com Text Secondary: aproximadamente 5,09:1;
- Info e Success sempre possuem texto ou ícone, nunca apenas cor.

### Movimento

- transições usam os tokens oficiais;
- nenhuma interação ultrapassa 300 ms;
- `prefers-reduced-motion: reduce` remove deslocamentos e reduz transições;
- a interface não depende de hover.

## 11. Checklist MDS

### Aprovado

- [x] ação principal evidente;
- [x] uma ação Primary por região;
- [x] componentes oficiais;
- [x] tokens oficiais;
- [x] container de 1180 px;
- [x] gutters oficiais;
- [x] mobile first;
- [x] 320, 360, 390, 768, 1024, 1280 e 1440 px;
- [x] sem rolagem horizontal;
- [x] um único H1;
- [x] corpo de texto com 16 px;
- [x] área mínima de toque de 44 × 44 px;
- [x] Lucide Icons;
- [x] foco visível;
- [x] HTML semântico antes de ARIA;
- [x] sem IDs ou referências ARIA inválidas;
- [x] estado sem imagem;
- [x] estado desabilitado com motivo;
- [x] conteúdo longo;
- [x] redução de movimento;
- [x] testes automatizados proporcionais ao risco;
- [x] console sem erros.

### Verificação recomendada antes do merge

- [ ] sessão manual completa com leitor de tela real;
- [ ] validação manual em dispositivos físicos Android e iOS;
- [ ] auditoria automatizada WCAG complementar em ambiente de homologação.

Essas verificações são recomendadas como auditoria externa da Sprint e não representam regressão conhecida.

## 12. Testes automatizados

Foram executados:

- `git diff --check`;
- Ruff lint;
- Ruff format check;
- suíte completa com `unittest`.

Resultado funcional:

- **81 testes preexistentes aprovados**;
- **2 testes novos aprovados**;
- **83 testes aprovados no total**;
- **0 falhas**;
- tempo da suíte completa: aproximadamente 10,3 segundos.

Testes adicionados:

1. estrutura MDS, semântica, CTA e rotas preservadas;
2. estado desabilitado do CTA para o proprietário com explicação acessível.

## 13. Arquivos modificados

- `templates/anuncio.html`;
- `static/styles.css`;
- `tests/test_moderacao.py`;
- `RELATORIO_MDS_SPRINT_003_PAGINA_PRODUTO.md`.

## 14. Escopo protegido

Não foram alterados:

- banco de dados;
- models;
- migrations;
- autenticação;
- permissões;
- regras de pedidos;
- regras de estoque;
- reputação;
- rastreabilidade;
- rotas;
- lógica de compra;
- lógica de contato;
- regras de negócio.

As rotas existentes continuam exatamente as mesmas:

- solicitação de compra: `/comprar/<id>`;
- contato: `/anuncio/<id>/contato`;
- denúncia: `/anuncio/<id>/denunciar`;
- gerenciamento: rotas preexistentes de edição e status.

## 15. Conclusão

A Página do Produto agora comunica claramente o que está sendo vendido, quanto custa, onde está, se está disponível, quem vende e qual é o próximo passo.

O CTA **Solicitar compra** tornou-se o principal elemento interativo sem recorrer a urgência artificial. A fotografia permanece valorizada, as informações secundárias foram organizadas abaixo da decisão e a experiência responde de 320 a 1440 px.

A Sprint está pronta para auditoria e aprovação, sem publicação, merge ou deploy.

**Mensagem obrigatória do commit:** `Aplica Mercado Design System na Página do Produto`
