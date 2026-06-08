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

## Admin e senha padrao

Senha/admin padrao podem servir apenas para teste local inicial.

Antes de colocar o sistema online, remover credenciais previsiveis e criar mecanismo seguro para configuracao do usuario administrador.

## SECRET_KEY

A chave secreta da aplicacao nao deve ter valor fixo em producao.

Antes de publicar online, exigir `SECRET_KEY` via variavel de ambiente e impedir fallback previsivel em ambiente de producao.

## Banco de dados

O banco real deve ficar fora do repositorio.

Para testes, usar banco ficticio, massa de dados falsa ou scripts de inicializacao sem informacoes reais.

## Uploads

Arquivos enviados por usuarios devem ficar fora do GitHub.

Antes de colocar online, revisar extensoes permitidas, tamanho maximo, nomes de arquivos, pasta de destino e protecao contra arquivos perigosos.

## Antes de producao

Checklist minimo:

- [ ] Remover senha/admin padrao.
- [ ] Exigir `SECRET_KEY` segura via ambiente.
- [ ] Confirmar `.env` fora do GitHub.
- [ ] Confirmar banco real fora do GitHub.
- [ ] Revisar autenticacao.
- [ ] Revisar upload de imagens.
- [ ] Revisar permissoes de usuario/admin.
- [ ] Criar backup seguro fora do repositorio.

## Regra NEO/Codex

Codex executa patch controlado.
ChatGPT audita antes de aplicar no sistema real.
Nenhum dado vivo entra no GitHub.
