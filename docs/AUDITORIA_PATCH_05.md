# AUDITORIA PATCH 05 — Hash de senha

## Data

2026-06-08

## Repositorio

`PauloEler/marketplace-colatina`

## Branch

`patch-05-password-hash`

## Base tecnica

Este patch foi encadeado sobre `patch-04-admin-env`, porque depende da remocao do admin fixo e da criacao do admin por variaveis de ambiente.

## Objetivo

Substituir armazenamento e comparacao de senhas em texto puro por hash de senha usando `werkzeug.security`.

## Arquivos criados

- `docs/AUDITORIA_PATCH_05.md`

## Arquivos alterados

- `app.py`
- `database.py`

## Arquivos nao alterados

- templates HTML
- banco local
- uploads
- README.md
- requirements.txt

## Banco tocado

Nao diretamente.

Nenhum banco `.db`, `.sqlite` ou `.sqlite3` foi criado, alterado ou enviado neste patch.

Observacao: o codigo inclui compatibilidade para atualizar senha antiga em texto puro no momento de login bem-sucedido, mas isso so ocorrera quando executado em ambiente local com banco existente.

## Riscos corrigidos

### 1. Cadastro de usuarios

Novos usuarios passam a ter senha salva com hash via `generate_password_hash`.

### 2. Login

Login passa a buscar usuario por `username` e validar a senha com `check_password_hash` quando a senha armazenada ja for hash.

### 3. Compatibilidade com senha antiga

Se uma senha antiga em texto puro ainda existir em banco local, o login bem-sucedido converte essa senha para hash automaticamente.

### 4. Troca de senha

Troca de senha passa a verificar a senha atual com funcao segura e salvar a nova senha com hash.

### 5. Criacao de usuario pelo admin

Usuarios criados pelo painel admin passam a receber senha com hash.

### 6. Admin inicial por ambiente

A senha do admin inicial criada via `ADMIN_PASSWORD` passa a ser gravada com hash.

## Dados sensiveis adicionados

Nao.

Nenhuma senha real, Pix real, WhatsApp real, banco real ou dado de usuario foi adicionado.

## Riscos que permanecem

### 1. Banco local antigo

Bancos locais antigos podem conter senhas em texto puro ate que cada usuario faca login ou ate uma migracao manual ser realizada.

### 2. SECRET_KEY e PIX_CHAVE

Este patch nao incorpora a blindagem do PATCH 03 se aplicado isoladamente. A ordem recomendada e revisar/mesclar os patches de seguranca em sequencia ou consolidar depois.

### 3. Uploads

O upload de imagens ainda precisa de auditoria especifica.

### 4. Politica de senha

Ainda nao ha politica forte de senha, limite de tentativas, bloqueio temporario ou protecao anti-forca-bruta.

## Proximos passos recomendados

1. Consolidar PATCH 03, PATCH 04 e PATCH 05 em uma sequencia coerente antes de producao.
2. PATCH 06 — Revisar seguranca de uploads.
3. PATCH 07 — Criar script de migracao manual de senhas antigas com backup.
4. PATCH 08 — Criar politica minima de senha e limite de tentativas.

## Status final

AMARELO.

Justificativa: o fluxo de senha foi melhorado com hash, mas ainda existem riscos de banco antigo, uploads e necessidade de consolidacao com os patches anteriores.
