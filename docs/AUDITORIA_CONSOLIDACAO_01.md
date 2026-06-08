# AUDITORIA CONSOLIDACAO 01 — Segurança base

## Data

2026-06-08

## Repositorio

`PauloEler/marketplace-colatina`

## Branch

`consolidacao-01-seguranca`

## Objetivo

Unificar em uma branch final revisavel as blindagens principais dos PATCHES 01 a 06.

## Arquivos criados

- `.gitignore`
- `.env.example`
- `docs/SEGURANCA.md`
- `docs/AUDITORIA_CONSOLIDACAO_01.md`

## Arquivos alterados

- `README.md`
- `app.py`
- `database.py`

## Arquivos nao alterados

- templates HTML
- `requirements.txt`
- banco real
- uploads reais

## Banco tocado

Nao.

Nenhum banco `.db`, `.sqlite` ou `.sqlite3` foi criado, alterado ou enviado.

## Uploads reais adicionados

Nao.

Nenhuma foto real, pasta `uploads/` ou arquivo de usuario foi enviado.

## Dados sensiveis adicionados

Nao.

Nenhuma senha real, Pix real, WhatsApp real, banco real ou dado real de usuario foi adicionado.

## Correcoes consolidadas

### 1. `.gitignore` seguro

Bloqueia ambientes virtuais, caches Python, `.env`, bancos locais, uploads, logs, reports, backups e arquivos de sistema/editor.

### 2. `.env.example`

Cria modelo de variaveis locais sem dados reais.

### 3. README seguro

Remove exposicao de admin/senha padrao e orienta configuracao por `.env` local.

### 4. SECRET_KEY por ambiente

`app.py` passa a exigir `SECRET_KEY` em producao e usa fallback apenas para desenvolvimento.

### 5. Pix e limites por ambiente

`PIX_CHAVE`, `LIMITE_GRATIS`, `VALOR_PLANO`, `MAX_UPLOAD_MB` e `PORT` passam a ser configuraveis por variaveis de ambiente.

### 6. Admin inicial por ambiente

`database.py` remove admin fixo e cria admin apenas se `ADMIN_USERNAME` e `ADMIN_PASSWORD` estiverem configurados.

### 7. Hash de senha

Novos usuarios, troca de senha e usuarios criados pelo admin passam a usar hash com `werkzeug.security`.

### 8. Compatibilidade com senha antiga

Login bem-sucedido com senha antiga em texto puro converte a senha para hash.

### 9. Upload seguro centralizado

Upload passa por `salvar_upload_seguro`, valida nome, extensao, caminho absoluto e salva com UUID.

## Riscos restantes

- Validacao profunda de imagem ainda nao implementada.
- Metadados EXIF ainda nao sao removidos.
- Nao ha rate limit de login/upload.
- Nao ha politica forte de senha.
- Bancos antigos podem conter senhas em texto puro ate login/migracao.
- `.env` nao e carregado automaticamente por `python-dotenv`; variaveis precisam ser configuradas pelo ambiente ou patch futuro.

## Proximos passos recomendados

1. Revisar PR consolidado em draft.
2. Rodar teste local em ambiente separado.
3. Criar banco novo de teste.
4. Testar cadastro, login, troca de senha e admin.
5. Testar upload valido e upload invalido.
6. PATCH 07 — Validar imagem com Pillow.
7. PATCH 08 — Limite de tentativas de login e politica minima de senha.

## Status final

AMARELO.

Justificativa: a blindagem base foi consolidada com sucesso na branch, mas ainda exige teste local e auditoria adicional antes de qualquer producao.
