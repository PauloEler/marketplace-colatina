# Relatório — PATCH UX-007A Balão da Cidade

## Objetivo

Orientar o visitante dentro da Cidade Viva, aproveitar o espaço lateral da Home, ampliar uniformemente os cards resumidos e compactar o rodapé sem alterar regras de negócio.

## Implementação

- feature flag `HOME_CITY_BALLOON_ENABLED=false` por padrão;
- painel semântico integrado ao layout;
- quatro caminhos e dois CTAs reais;
- reaproveitamento opcional de métricas reais já calculadas;
- estado sem dados sem números inventados;
- largura comum de 80 rem e tokens de proporção para cards;
- rodapé compacto com conteúdo integral;
- comportamento responsivo em três modos;
- botão de sugestão preservado sem sobreposição.

## Arquivos alterados

- `.env.example`
- `app.py`
- `templates/index.html`
- `static/styles.css`
- `tests/test_moderacao.py`
- documentação e evidências em `docs/`.

## Validação

- 157 testes aprovados;
- Ruff check aprovado;
- Ruff format check aprovado;
- `git diff --check` aprovado;
- 1440, 1024, 768, 390 e 320 px sem overflow;
- painel com `position: relative`, sem popup ou sobreposição;
- navegação semântica e foco visível;
- console da aplicação sem erros funcionais;
- Marketplace, banco, rotas e backend preservados.

## Reversão

Operacional: definir `HOME_CITY_BALLOON_ENABLED=false` e reiniciar o serviço. A Home 2.0 anterior volta a ser renderizada sem markup ou classes do patch.

Definitiva: executar o revert do único commit `style(home): adicionar Balão da Cidade e ampliar cards`.

## Situação

Pronto para PR Draft. Sem merge e sem deploy.
