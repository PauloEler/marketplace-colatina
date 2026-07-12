# Proteção de dados do Mercado Colatina

## Proteções ativas

- O Render executa somente a instalação das dependências durante o build.
- Os testes rodam no GitHub Actions com SQLite temporário e sem acesso aos bancos do Render.
- A suíte interrompe imediatamente se detectar uma conexão PostgreSQL.
- O banco de produção possui recuperação por horário no painel do Render.
- Mudanças de banco devem preservar o banco anterior até a validação da cópia restaurada.

## Regra para publicações

1. Abrir uma pull request.
2. Aguardar a validação segura do GitHub concluir com sucesso.
3. Incorporar a mudança e acompanhar a publicação do Render.
4. Confirmar `/health`, página inicial e quantidade de anúncios.
5. Não executar comandos `DELETE`, `DROP` ou testes usando credenciais de produção.

## Recuperação

Em caso de incidente, criar uma cópia por Point-in-Time Recovery. Validar usuários,
anúncios e tabelas na cópia antes de alterar a conexão do site. O banco anterior só
deve ser removido depois da confirmação do responsável pelo Mercado Colatina.
