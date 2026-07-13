# Mercado Colatina — Relatório MDS Sprint 001

**Sprint:** Mercado Design System 1.0

**Data:** 13 de julho de 2026

**Natureza:** documentação e governança visual

## 1. Resumo executivo

A MDS Sprint 001 instituiu a fundação visual oficial do Mercado Colatina. O novo Mercado Design System 1.0 transforma decisões de marca já consolidadas — verde institucional, azul regional, tipografia Inter, clareza e proximidade — em regras normativas para futuras interfaces.

O MDS define filosofia, paleta semântica, tipografia, grid, tokens, anatomia e comportamento de componentes, biblioteca de ícones, mobile first, acessibilidade, movimento, conteúdo e critérios de aprovação. Também foi criado um checklist obrigatório para acompanhar toda nova tela desde a concepção até a validação.

Nenhuma interface foi modificada nesta Sprint. A documentação estabelece o padrão; sua adoção técnica será planejada em Sprints futuras.

## 2. Objetivo alcançado

Foi criada uma referência única capaz de responder:

- como o Mercado Colatina deve parecer;
- como sua interface deve se comportar;
- quais decisões visuais são permitidas;
- quais tokens e componentes devem ser reutilizados;
- como garantir consistência entre mobile, tablet e desktop;
- quais critérios de acessibilidade são obrigatórios;
- quando uma tela está pronta para implementação e aprovação.

## 3. Arquivos criados

### `docs/DESIGN_SYSTEM_MERCADO_COLATINA.md`

Documento normativo do Mercado Design System 1.0. Passa a ser a autoridade oficial para identidade visual e componentes, subordinada apenas às regras de produto do Documento Mestre.

### `docs/MDS_CHECKLIST.md`

Checklist operacional obrigatório para concepção, implementação, revisão e validação de qualquer nova tela ou alteração de interface.

### `RELATORIO_MDS_SPRINT_001.md`

Registro de escopo, decisões, estrutura, validação e próximos passos desta Sprint.

## 4. Estrutura do MDS

O Mercado Design System 1.0 foi organizado em quinze áreas:

1. autoridade, uso e governança;
2. filosofia do design;
3. paleta oficial e contraste;
4. tipografia;
5. grid e layout;
6. design tokens;
7. componentes;
8. biblioteca e padrão de ícones;
9. mobile first;
10. acessibilidade;
11. animações e movimento;
12. conteúdo e microcopy;
13. regras permanentes;
14. critérios de aprovação;
15. controle de versão.

## 5. Decisões fundamentais

### Identidade preservada

A base oficial permanece alinhada à marca vigente:

- Primary verde `#17633D`;
- Secondary azul regional `#6FC2E8`;
- fundo `#F4F7F5`;
- texto principal `#17211B`;
- fonte Inter, com Segoe UI e Arial como fallbacks.

### Paleta ampliada semanticamente

Foram definidos papéis específicos para Success, Warning, Danger e Info, além de fundos suaves, bordas, estados interativos, disabled e focus. Isso reduz o uso arbitrário de cores e separa identidade de significado operacional.

### Contraste documentado

As principais combinações foram verificadas para WCAG 2.2 AA. O MDS registra, por exemplo, que branco não deve ser usado sobre o azul Secondary; o texto correto nesse fundo é o Text Primary.

### Escala de espaçamento previsível

A escala oficial usa 8, 16, 24, 32, 48 e 64 px, com 4 px reservado a ajustes mínimos. Novos valores arbitrários exigem justificativa.

### Componentes como contratos

Botões, cards, campos, seletores, modais, drawers, navegação, tabelas, alertas e estados de sistema receberam finalidade, anatomia, comportamento responsivo e requisitos de acessibilidade.

### Lucide Icons como biblioteca oficial

Foi adotado um único padrão de ícones outline, stroke 2 e tamanhos de 16, 20 e 24 px. Emojis não podem atuar como controles funcionais.

### Mobile first obrigatório

A validação começa em 320 px e considera 360, 390, 768, 1024, 1280 e 1440 px. Alvos de toque e controles possuem mínimo de 44 × 44 px, e a página não pode produzir rolagem horizontal.

### Acessibilidade como requisito de origem

O MDS adota WCAG 2.2 AA como objetivo mínimo e documenta contraste, foco, teclado, semântica, leitores de tela, ARIA, redução de movimento e linguagem inclusiva.

## 6. Tokens criados

Foram especificadas famílias de tokens para:

- marca e cores semânticas;
- superfícies, bordas e conteúdo;
- tipografia, pesos e alturas de linha;
- escala de espaçamento;
- dimensões, controles e áreas de toque;
- raios e bordas;
- sombras e foco;
- durações e curvas de movimento;
- camadas e z-index;
- container e referências de layout.

Os tokens foram documentados com prefixo `--mc-`, preparando uma adoção técnica consistente em Sprint futura sem alterar o CSS atual.

## 7. Componentes documentados

- Botões;
- Cards;
- Inputs e textarea;
- Checkbox;
- Radio;
- Select;
- Modal;
- Drawer;
- Navbar;
- Footer;
- Sidebar;
- Badges;
- Tags;
- Alertas;
- Tabelas;
- Paginação;
- Breadcrumb;
- Loading;
- Skeleton;
- Empty States.

## 8. Checklist de governança

O checklist cobre:

- objetivo e ação principal;
- uso de tokens e componentes;
- grid e responsividade;
- tipografia e conteúdo;
- contraste;
- controles e toque;
- ícones e imagens;
- teclado, foco, semântica e ARIA;
- estados completos da experiência;
- componentes complexos;
- movimento e feedback;
- validação final e bloqueadores.

Uma tela não pode ser aprovada com contraste insuficiente, foco invisível, operação essencial inacessível por teclado, rolagem horizontal, componente fora do padrão ou exceção não documentada.

## 9. Validação de escopo

Nesta Sprint:

- nenhum HTML foi alterado;
- nenhum CSS existente foi alterado;
- nenhum JavaScript foi alterado;
- nenhuma tela foi modificada;
- nenhum componente foi implementado;
- nenhum banco de dados foi acessado ou alterado;
- nenhuma regra de negócio foi alterada;
- nenhuma publicação foi realizada.

Foram criados somente os três documentos definidos no escopo.

### Validações executadas

- presença dos 65 requisitos e termos obrigatórios do escopo: aprovada;
- 99 tokens definidos, sem nomes duplicados: aprovado;
- hierarquia Markdown com um único H1 por documento: aprovada;
- espaços inválidos e inconsistências de final de linha: não identificados;
- `python -m ruff check .`: aprovado;
- `python -m ruff format --check .`: 8 arquivos Python já formatados;
- `python -m unittest discover -s tests -v`: 80 testes aprovados em 10,293 segundos.

## 10. Impacto esperado

- redução de inconsistências entre telas;
- decisões visuais mais rápidas e objetivas;
- menor criação de estilos isolados;
- melhor previsibilidade para desenvolvimento e revisão;
- experiência coerente em desktop, tablet e celular;
- acessibilidade avaliada antes da implementação;
- evolução visual controlada por tokens e componentes oficiais;
- preservação da identidade local durante o crescimento do produto.

## 11. Próximos passos recomendados

Os itens abaixo não fazem parte desta Sprint e exigem autorização própria:

1. inventariar componentes visuais existentes e mapear divergências em relação ao MDS;
2. criar uma camada técnica de tokens sem alterar o resultado visual;
3. migrar componentes por prioridade e risco, com testes de regressão visual;
4. criar catálogo vivo de componentes e exemplos acessíveis;
5. definir processo de versionamento e aprovação de novas variantes;
6. incluir o checklist nas revisões de interface e templates de missão.

## 12. Conclusão

O Mercado Colatina passa a possuir uma linguagem visual oficial, documentada e verificável. O MDS 1.0 cria a base para que futuras interfaces mantenham confiança, simplicidade, organização, tecnologia, comércio local, clareza, rapidez e acessibilidade sem depender de decisões isoladas por tela.
