# SEGURANCA — marketplace-colatina

## Principio central

GitHub guarda engenharia. O PC local guarda dados vivos.

Este repositorio deve conter codigo, documentacao, exemplos e estrutura tecnica. Ele nao deve conter banco real, dados reais de usuarios, senhas, chaves, uploads privados ou informacoes sensiveis.

## O que nunca deve subir para o GitHub

- Arquivo `.env` real.
- Banco `marketplace.db` real.
- Bancos `.db`, `.sqlite` ou `.sqlite3` com dados reais.
- Pasta `uploads/` com fotos reais de usuarios.
- Senhas reais.
- Chaves Pix reais.
- Telefones/WhatsApp reais de usuarios.
- Backups locais.
- Logs com informacoes sensiveis.

## Variaveis de ambiente

Use `.env.example` apenas como modelo.

Crie um `.env` local no PC, nunca versionado, com valores reais somente no ambiente de execucao.

## Administrador

O administrador inicial deve ser configurado por variaveis de ambiente:

- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ADMIN_NOME`
- `ADMIN_WHATSAPP`

Nunca use credenciais previsiveis em producao.

## SECRET_KEY

A chave secreta da aplicacao nao deve ter valor fixo em producao.

Em `FLASK_ENV=production`, a aplicacao deve falhar se `SECRET_KEY` nao estiver configurada.

## Senhas

Novas senhas devem ser armazenadas com hash usando `werkzeug.security`.

Bancos antigos podem exigir migracao ou login bem-sucedido para conversao de senhas antigas.

## Banco de dados

O banco real deve ficar fora do repositorio.

Para testes, usar banco ficticio, massa de dados falsa ou scripts de inicializacao sem informacoes reais.

## Uploads

Arquivos enviados por usuarios devem ficar fora do GitHub.

O sistema deve:

- validar extensao;
- usar nome final com UUID;
- sanitizar nome original com `secure_filename`;
- validar caminho final dentro de `UPLOAD_FOLDER`;
- evitar uso direto do nome original.

Antes de producao, ainda e recomendavel validar conteudo real da imagem, remover metadados EXIF e avaliar limite de frequencia.

## Antes de producao

Checklist minimo:

- [ ] Confirmar `.env` fora do GitHub.
- [ ] Confirmar banco real fora do GitHub.
- [ ] Confirmar uploads fora do GitHub.
- [ ] Configurar `SECRET_KEY` real.
- [ ] Configurar admin por ambiente.
- [ ] Testar cadastro, login e troca de senha.
- [ ] Testar upload de imagem.
- [ ] Revisar logs.
- [ ] Criar backup seguro fora do repositorio.

## Regra NEO/Codex

Codex executa patch controlado.
ChatGPT audita antes de aplicar no sistema real.
Nenhum dado vivo entra no GitHub.
