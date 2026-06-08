# AUDITORIA PATCH 03 — SECRET_KEY e variaveis de ambiente

## Data

2026-06-08

## Repositorio

`PauloEler/marketplace-colatina`

## Branch

`patch-03-env-secret-key`

## Objetivo

Corrigir o risco de `SECRET_KEY` previsivel em producao e reduzir dados sensiveis fixos no arquivo `app.py`.

## Arquivos criados

- `docs/AUDITORIA_PATCH_03.md`

## Arquivos alterados

- `app.py`

## Arquivos nao alterados

- `database.py`
- `README.md`
- `requirements.txt`
- templates HTML
- banco local
- uploads

## Banco tocado

Nao.

Nenhum banco `.db`, `.sqlite` ou `.sqlite3` foi criado, alterado ou enviado neste patch.

## Riscos corrigidos

### 1. SECRET_KEY previsivel

Antes, `app.py` usava fallback fixo para `SECRET_KEY`.

Agora:

- le `SECRET_KEY` do ambiente;
- em `FLASK_ENV=production`, falha com erro claro se a chave nao existir;
- em desenvolvimento, usa fallback explicito de teste local.

### 2. Chave Pix fixa no codigo

Antes, `PIX_CHAVE` estava fixa no codigo.

Agora, `PIX_CHAVE` vem do ambiente, com fallback ficticio/local.

### 3. Impressao de credenciais no terminal

Antes, o terminal imprimia login e senha padrao.

Agora, imprime apenas orientacao para configurar credenciais localmente.

## Dados sensiveis adicionados

Nao.

Nenhuma senha real, Pix real, WhatsApp real, banco real ou dado de usuario foi adicionado.

## Riscos que permanecem

### 1. Admin/senha padrao no banco

O arquivo `database.py` ainda cria administrador padrao para teste local.

### 2. Senhas em texto puro

O login ainda compara senha diretamente no banco.

Recomendacao futura: usar hash de senha, como `werkzeug.security.generate_password_hash` e `check_password_hash`.

### 3. Uploads

O upload de imagens ainda precisa de auditoria especifica.

### 4. Sem `.env` carregado automaticamente

O sistema depende de variaveis de ambiente reais configuradas fora do codigo. Em patch futuro pode ser avaliado uso opcional de `python-dotenv` em desenvolvimento.

## Proximos passos recomendados

1. PATCH 04 — Remover criacao fixa de admin/senha em `database.py`.
2. PATCH 05 — Implementar hash de senha.
3. PATCH 06 — Revisar seguranca de uploads.
4. PATCH 07 — Avaliar carregamento local opcional de `.env` para desenvolvimento.

## Status final

AMARELO.

Justificativa: o risco da `SECRET_KEY` previsivel foi corrigido e dados sensiveis fixos foram reduzidos, mas ainda existem riscos importantes no fluxo de usuario/senha e inicializacao do administrador.
