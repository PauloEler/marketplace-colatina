# Relatório da Sprint MX-004.2 — Empresas Parceiras e Confiança

## Objetivo

Reforçar a credibilidade do Mercado Colatina e preparar uma futura fonte de receita com empresas locais, sem interferir na navegação ou nas regras do marketplace.

## Entrega implementada

- seção “Por que confiar no Mercado Colatina?” com cinco compromissos e ícones discretos;
- seção “Empresas Parceiras” com seis placeholders claramente identificados;
- arquitetura centralizada para Parceiro Local, Parceiro Destaque e Parceiro Premium;
- páginas temporárias Quem Somos e Seja Parceiro;
- rodapés atualizados com os seis acessos institucionais obrigatórios;
- sitemap atualizado com as novas páginas públicas;
- testes automatizados de conteúdo, quantidade, níveis, rotas, rodapé e ordem da Home.

## Arquivos alterados

- `app.py`;
- `local_partners.py`;
- `templates/index.html`;
- `templates/base.html`;
- `static/styles.css`;
- `tests/test_moderacao.py`;
- documentação desta sprint.

## Arquitetura e componentes

Os parceiros são definidos em estrutura estática, sem banco. A Home recebe seis placeholders pelo contexto do Flask. Cada card expõe nível e conteúdo institucional, mas não ativa preço, contrato, prioridade comercial ou empresa real.

## Impacto esperado

O visitante percebe a origem local, a prioridade dada ao comércio da cidade, a negociação direta e a transparência publicitária. A grade de parceiros sinaliza uma oportunidade futura de participação sem competir visualmente com produtos e lojas.

## Responsividade planejada

- desktop e notebook: 3 cards por linha;
- tablet: 2 cards por linha;
- mobile: 1 card por linha;
- sem rolagem horizontal da página.

## Limitações

- placeholders apenas;
- sem planos comerciais ativos;
- sem empresas ou patrocinadores reais;
- sem painel administrativo ou banco;
- sem Colatina Agora;
- sem alteração da monetização de afiliados.

## Testes e evidências

- suíte completa: 106 testes aprovados;
- `ruff check`: aprovado;
- `ruff format --check`: aprovado;
- `git diff --check`: aprovado;
- console do navegador: sem erros ou avisos;
- rotas e links institucionais: aprovados;
- ordem da Home: marketplace, confiança, parceiros e Como Funciona preservada;
- banco, pedidos, anúncios e afiliados: sem alteração.

### Matriz responsiva

| Largura | Cards por linha | Seções visíveis | Overflow horizontal |
| --- | ---: | --- | --- |
| 1440 px | 3 | Sim | Não |
| 1280 px | 3 | Sim | Não |
| 1024 px | 3 | Sim | Não |
| 768 px | 2 | Sim | Não |
| 390 px | 1 | Sim | Não |
| 320 px | 1 | Sim | Não |

### Lighthouse local

- Performance: 86;
- Acessibilidade: 97;
- Boas práticas: 96;
- SEO: 100;
- regressão crítica: não identificada em relação à referência anterior da Home.

### Evidências visuais

- desktop 1440 px: `docs/evidencias/mx004-2-local-desktop-1440.png`;
- mobile 390 px: `docs/evidencias/mx004-2-local-mobile-390.png`.

## Evolução futura

Definir regras comerciais e critérios transparentes, substituir placeholders somente mediante autorização e preparar administração dinâmica em sprint própria.

## Publicação

- PR: #62;
- hash do merge: `472281189f4eeefdfdd588cec69e1d228b3bd07f`;
- merge na `master`: concluído em 18/07/2026 às 14h15min22s, horário de Brasília;
- CI da `master`: aprovado no workflow `29653561010`;
- deploy automático no Render: detectado no domínio oficial às 14h18min07s;
- URL: `https://mercadocolatina.com.br/`.

### Validação final em produção

- Home carregando normalmente;
- seção “Por que confiar no Mercado Colatina?” visível;
- seção “Empresas Parceiras” visível com seis placeholders;
- desktop 1280 px: 3 cards por linha, sem overflow;
- tablet 768 px: 2 cards por linha, sem overflow;
- mobile 390 px: 1 card por linha, sem overflow;
- seção “Ofertas de Parceiros” preservada com seis links oficiais `meli.la`;
- camada de analytics dos afiliados carregada e preservada;
- console do navegador sem erros ou avisos;
- Lighthouse em produção: Performance 96, Acessibilidade 97, Boas práticas 96 e SEO 100;
- nenhuma regressão visual crítica identificada;
- funcionalidades anteriores preservadas.

### Encerramento

A MX-004.2 está oficialmente publicada e encerrada. A MX-004.3 não foi iniciada.
