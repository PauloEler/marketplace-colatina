# AUDITORIA PATCH 06 — Segurança de uploads

## Data

2026-06-08

## Repositorio

`PauloEler/marketplace-colatina`

## Branch

`patch-06-upload-security`

## Base tecnica

Este patch foi encadeado sobre `patch-05-password-hash`, porque altera `app.py` e deve preservar as melhorias de autenticação e senha propostas anteriormente.

## Objetivo

Fortalecer o fluxo de upload de imagens, centralizando validação e salvamento seguro para reduzir riscos de nomes inseguros, extensão inválida e path traversal.

## Arquivos criados

- `docs/AUDITORIA_PATCH_06.md`

## Arquivos alterados

- `app.py`

## Arquivos nao alterados

- `database.py`
- templates HTML
- banco local
- uploads reais
- README.md
- requirements.txt

## Banco tocado

Nao.

Nenhum banco `.db`, `.sqlite` ou `.sqlite3` foi criado, alterado ou enviado neste patch.

## Uploads reais adicionados

Nao.

Nenhum arquivo de usuario, foto real ou pasta `uploads/` foi enviada ao GitHub.

## Riscos corrigidos

### 1. Upload centralizado

O salvamento de imagens foi movido para a funcao `salvar_upload_seguro(file_storage)`.

### 2. Nome original nao usado como nome final

O arquivo continua sendo salvo com UUID, nao com o nome original enviado pelo usuario.

### 3. Nome original sanitizado

O nome original e processado com `secure_filename` antes de qualquer verificacao de extensao.

### 4. Extensao validada

A extensao e normalizada em minusculo e comparada com `ALLOWED_EXTENSIONS`.

### 5. Caminho absoluto validado

O caminho final e convertido para absoluto e validado com `os.path.commonpath` para garantir que fica dentro de `UPLOAD_FOLDER`.

### 6. Pasta de uploads absoluta

`UPLOAD_FOLDER` agora e definido como caminho absoluto.

### 7. Download/servico de arquivo sanitizado

A rota `/uploads/<filename>` passa `secure_filename(filename)` para `send_from_directory`.

## Riscos que permanecem

### 1. Validacao profunda de conteudo

O patch valida extensao e caminho, mas nao verifica assinatura real/magic bytes do arquivo.

### 2. Malware/antivirus

Nao ha varredura de malware.

### 3. Rate limit

Nao ha limite de frequencia de uploads por usuario/IP.

### 4. Processamento de imagem

Nao ha redimensionamento, recompressao, remocao de metadados EXIF ou verificacao de dimensoes.

### 5. Patches de ambiente

Este patch deve ser consolidado com PATCH 03, PATCH 04 e PATCH 05 antes de qualquer producao.

## Proximos passos recomendados

1. Consolidar patches de seguranca em uma branch final.
2. PATCH 07 — Validar conteudo real de imagem com Pillow.
3. PATCH 08 — Criar limite de tentativas/login e politica minima de senha.
4. PATCH 09 — Criar checklist de producao.

## Status final

AMARELO.

Justificativa: o fluxo de upload foi fortalecido, mas ainda faltam validacao profunda de conteudo, protecao contra abuso e consolidacao geral dos patches de seguranca.
