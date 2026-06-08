# AUDITORIA PATCH 04 — Admin por variaveis de ambiente

## Data

2026-06-08

## Repositorio

`PauloEler/marketplace-colatina`

## Branch

`patch-04-admin-env`

## Objetivo

Remover a criacao fixa de administrador com usuario/senha padrao em `database.py` e substituir por criacao opcional via variaveis de ambiente.

## Arquivos criados

- `docs/AUDITORIA_PATCH_04.md`

## Arquivos alterados

- `database.py`

## Arquivos nao alterados

- `app.py`
- `README.md`
- `requirements.txt`
- templates HTML
- banco local
- uploads

## Banco tocado

Nao.

Nenhum banco `.db`, `.sqlite` ou `.sqlite3` foi criado, alterado ou enviado neste patch.

## Riscos corrigidos

### 1. Admin fixo removido

Antes, `database.py` criava automaticamente um administrador com usuario, senha e WhatsApp fixos.

Agora, o administrador so e criado se as variaveis `ADMIN_USERNAME` e `ADMIN_PASSWORD` estiverem configuradas.

### 2. Producao sem admin configurado falha

Em `FLASK_ENV=production`, se `ADMIN_USERNAME` e `ADMIN_PASSWORD` nao forem configurados, o sistema falha com erro claro.

### 3. DATABASE_PATH configuravel

O caminho do banco passou a aceitar `DATABASE_PATH` por ambiente, mantendo fallback local para desenvolvimento.

## Dados sensiveis adicionados

Nao.

Nenhuma senha real, Pix real, WhatsApp real, banco real ou dado de usuario foi adicionado.

## Riscos que permanecem

### 1. Senhas em texto puro

O sistema ainda armazena e compara senhas em texto puro.

Recomendacao: PATCH 05 deve implementar hash de senha com `werkzeug.security.generate_password_hash` e `check_password_hash`.

### 2. Usuarios antigos

Se ja existir banco local antigo com admin padrao, este patch nao remove registros existentes porque nao toca banco real.

A limpeza de banco local deve ser feita manualmente e com backup.

### 3. Uploads

O upload de imagens ainda precisa de auditoria especifica.

## Proximos passos recomendados

1. PATCH 05 — Implementar hash de senha.
2. PATCH 06 — Revisar seguranca de uploads.
3. PATCH 07 — Criar procedimento documentado para banco local novo.

## Status final

AMARELO.

Justificativa: a criacao fixa de admin foi removida do codigo, mas o sistema ainda precisa de hash de senha e auditoria de uploads antes de qualquer producao.
