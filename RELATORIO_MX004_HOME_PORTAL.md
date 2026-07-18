# RELATORIO MX-004 - HOME COMO PORTAL LOCAL

## Projeto

Mercado Colatina

## Objetivo

Transformar a Home em uma arquitetura visual de portal local para Colatina, mantendo o marketplace como protagonista.

## Alteracoes implementadas

- Mantido o Hero principal com busca, compra, publicacao de anuncio e identidade do Mercado Colatina.
- Mantidas categorias e produtos locais em destaque antes de qualquer bloco institucional/comercial.
- Criada a secao "Ofertas de Parceiros" com carrossel automatico e rotacao continua.
- Criadas 5 ofertas de parceiros, com identificacao comercial e transparencia.
- Criado botao "Ver todas as ofertas".
- Criada a secao "Patrocinadores" como espaco reservado para empresas de Colatina.
- Criada a secao "Colatina Agora" como estrutura visual compacta para:
  - noticias locais;
  - eventos;
  - vagas de emprego;
  - tempo;
  - servicos publicos;
  - telefones uteis.
- Reforcado o rodape com links para parceiros, transparencia, politica de seguranca e quem somos.

## Arquitetura

- Nao houve banco novo.
- Nao houve API externa.
- Nao houve captura automatica de noticias.
- Nao houve alteracao em autenticacao, pedidos, regras de negocio ou pagamento.
- Os novos blocos podem ser ativados ou ocultados por flags em `HOME_PORTAL_SECTIONS`.
- Os conteudos de parceiros e Colatina Agora ficam em constantes reutilizaveis no `app.py`.

## Arquivos alterados

- `app.py`
- `templates/index.html`
- `static/styles.css`
- `tests/test_moderacao.py`
- `RELATORIO_MX004_HOME_PORTAL.md`

## Validacao realizada

- `ruff check .`
- `ruff format --check .`
- `python -m unittest tests.test_moderacao` - 94 testes aprovados.
- `git diff --check`
- Conferencia automatizada da ordem dos blocos:
  1. Hero principal
  2. Categorias
  3. Produtos locais em destaque
  4. Ofertas de Parceiros
  5. Patrocinadores
  6. Colatina Agora
  7. Rodape reforcado

## Status

Implementado em branch propria para PR draft.

Sem merge.

Sem deploy.
