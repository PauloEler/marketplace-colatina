# Relatório técnico — Missão 007 Home 2.0

## Entrega

- Feature flag `HOME_2_ENABLED=false`.
- Hero amplo com panorama, mensagem e dois CTAs.
- Busca rápida independente, mantendo método, nomes e destino existentes.
- Encontre Quem Resolve em faixa independente.
- CSS responsivo isolado por classe de `body`.
- Testes de flag, separação, rotas, acessibilidade e dependência da Cidade Viva.
- Evidências antes, depois, comparação e reversão.

## Arquivos de aplicação

- `.env.example`
- `app.py`
- `render.yaml`
- `templates/index.html`
- `static/styles.css`
- `tests/test_moderacao.py`

## Integridade do escopo

Banco, migrações, rotas, regras de negócio, produtos, empresas, parceiros,
analytics e dashboards não foram alterados. As seções após a primeira dobra
permanecem no mesmo template e na mesma ordem.

## Validações

- Cinco breakpoints sem overflow horizontal.
- Título em duas linhas em todas as larguras verificadas.
- Console do navegador sem erros.
- HTML semântico com regiões, `role="search"`, labels e foco visível.
- 153 testes automatizados aprovados, incluindo quatro específicos da missão.
- `ruff check .` aprovado.
- `ruff format --check .` aprovado (19 arquivos formatados).
- `git diff --check` aprovado.
- Reversão visual idêntica nas cinco larguras.

- CI oficial do GitHub aprovado em 34 segundos na PR Draft.

Não houve merge nem deploy.

## Limitação operacional

`HOME_2_ENABLED` permanece `false`; portanto, a publicação futura do commit não
ativa a variante automaticamente. A ativação depende de autorização separada.
