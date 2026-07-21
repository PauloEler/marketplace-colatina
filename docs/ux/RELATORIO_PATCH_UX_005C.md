# Relatório — PATCH UX-005C

## Resultado

A primeira dobra da Home foi reorganizada para apresentar rapidamente os caminhos de comprar, anunciar, buscar e descrever uma necessidade local.

## Alterações

- Hero compactado e mensagem mais direta;
- CTAs principais com rótulos orientados à ação;
- busca com pergunta, exemplo e CTA claros;
- nova faixa **Encontre Quem Resolve**;
- foco e interação das categorias reforçados;
- fotografia preservada no desktop e omitida até 960 px para priorizar ações;
- categorias mobile em faixa horizontal acessível.
- atalho flutuante duplicado ocultado somente quando a nova faixa está presente.

## Arquivos alterados

- `templates/index.html`;
- `static/styles.css`;
- `tests/test_moderacao.py`;
- documentação deste patch em `docs/ux/`.

## Escopo preservado

Não foram alterados produtos, pedidos, empresas, dashboards, backend, banco de dados ou regras de negócio.

## Testes

### Automação

- suíte completa: **139 testes aprovados**;
- `ruff check`: aprovado;
- `ruff format --check`: aprovado;
- `git diff --check`: aprovado.

### Validação visual local

- desktop 1440 × 900: Hero, busca e faixa visíveis; sem overflow;
- tablet 768 × 1024: busca e faixa priorizadas; sem overflow;
- mobile 390 × 844: CTAs e busca visíveis na primeira dobra; sem overflow;
- mobile 320 × 720: layout estável e sem overflow horizontal;
- console: nenhum erro registrado.

A auditoria também confirmou que o botão flutuante antigo não cobre a nova faixa quando ela está presente.

## Publicação

Merge: não realizado.

Deploy: não realizado.

## Medição posterior

Após autorização de publicação, executar cinco sessões controladas e verificar quantos participantes iniciam uma ação principal em até cinco segundos. A instrumentação de CTR permanece fora deste patch.
