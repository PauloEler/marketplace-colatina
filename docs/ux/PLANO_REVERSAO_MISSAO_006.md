# Plano de reversão — Missão 006

## Ponto seguro

- Branch: `agent/missao-006-cidade-viva-home-reversivel`
- Hash-base da `master`: `364a701f84b8b61902a66be5a12712ff93c4381c`
- Migrações: nenhuma.
- Dados alterados: nenhum.
- Deploy: não realizado.

## Arquivos alterados

- `app.py`
- `templates/index.html`
- `static/styles.css`
- `tests/test_moderacao.py`
- documentação e evidências desta missão.

## Backups preservados

Os arquivos anteriores estão em `docs/ux/backups/missao_006/`:

| Arquivo | SHA-256 |
| --- | --- |
| `app.py.before` | `C726E7FEC9D7EFFEE6CA6DFEA3A6753893D3A8A275A09B384A13BBE5AD7BAF96` |
| `index.html.before` | `FDEB0E73A90E7DF0951A948E6159BDF51C4C20F21FA64B9A687330333770E792` |
| `styles.css.before` | `791CEA195A40A2F3D430FF532D44C0CFAB540A32745307888C01701995911A33` |
| `test_moderacao.py.before` | `5102C35CED0723B2341E2CF9B4EF5F4B4AD65EA81DF41B7BC0A758C199363383` |

## Reversão imediata sem Git

Definir `HOME_CIDADE_VIVA_ENABLED=false` ou remover a variável do ambiente. Reiniciar o serviço. A Home anterior volta a ser renderizada sem alteração de banco.

## Reversão definitiva antes do merge

Descartar a branch `agent/missao-006-cidade-viva-home-reversivel`. A `master` permanece no hash-base e não recebe resíduos.

## Reversão definitiva após eventual merge

Executar `git revert <hash-do-commit-da-missao-006>` em nova branch de correção, executar a suíte completa e publicar somente após aprovação. A entrega utiliza um único commit funcional para tornar esse procedimento atômico.

## Restauração pelos backups

Como alternativa de contingência, copiar os quatro arquivos `.before` para seus caminhos originais, executar formatação, testes e comparar o resultado com o hash-base. Essa opção não deve ser usada para sobrescrever trabalho posterior sem revisão manual.

## Validação obrigatória após reverter

1. Confirmar ausência da classe `home-city-alive`.
2. Confirmar que todos os anúncios e todas as lojas voltaram à Home.
3. Confirmar os blocos institucionais, Hoje em Colatina, QR Code e Como Funciona.
4. Executar `python -m unittest discover -s tests -v`.
5. Executar `ruff check .`, `ruff format --check .` e `git diff --check`.
6. Validar 1440, 1024, 768, 390 e 320 px sem overflow.

O teste de reversão em worktree isolada está registrado no relatório final da missão.
