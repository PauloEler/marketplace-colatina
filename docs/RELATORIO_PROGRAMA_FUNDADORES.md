# Relatório — Programa Fundadores do Mercado Colatina

## Resumo técnico

Foi implementado o Programa Fundadores como uma camada independente sobre as contas de usuários. O programa reconhece automaticamente os primeiros participantes da plataforma e exibe o selo permanente:

> 🏅 Fundador do Mercado Colatina

O limite automático padrão é de **100 Fundadores** e pode ser alterado pela variável de ambiente `FOUNDERS_LIMIT`. Depois que todas as vagas automáticas forem utilizadas, novas contas não recebem o selo, mesmo que um selo automático seja removido posteriormente por exceção administrativa.

## Concessão automática

- Usuários existentes são incorporados em ordem de criação durante a migração segura.
- Novas contas públicas e contas criadas pelo administrador recebem o selo enquanto houver vaga automática.
- A operação usa transação e bloqueio apropriado no PostgreSQL para reduzir risco de ultrapassar o limite em cadastros concorrentes.
- Concessões manuais podem ocorrer como exceção e não consomem nem reabrem vagas automáticas.
- Alterar o limite para um número menor não remove selos já concedidos.

## Administração

O painel administrativo agora apresenta:

- quantidade atual de Fundadores e limite automático;
- lista de Fundadores;
- filtro de usuários Fundadores;
- botão para conceder o selo manualmente;
- botão para remover o selo em situação excepcional;
- registro do administrador responsável pela alteração.

Somente uma sessão administrativa pode executar as alterações manuais. A remoção não apaga o histórico da concessão e não reabre uma vaga automática.

## Exibição

O selo é exibido:

- no perfil público da loja;
- no painel do vendedor;
- na página Minha conta;
- na visualização administrativa da reputação;
- nos cartões de lojas da página inicial.

## Preparação para vantagens futuras

O campo `fundador_beneficios` foi preparado como metadado estruturado vazio (`{}`). Nenhuma vantagem, destaque comercial, acesso antecipado ou benefício financeiro foi ativado nesta missão.

## Migração aditiva

Foram adicionados à tabela `usuarios`:

- `fundador`;
- `fundador_desde`;
- `fundador_origem`;
- `fundador_removido_em`;
- `fundador_alterado_por`;
- `fundador_beneficios`.

A migração:

- não cria outro banco de dados;
- não remove nem renomeia colunas;
- preserva usuários e dados existentes;
- incorpora os primeiros usuários sem ultrapassar o limite configurado;
- pode ser executada novamente com segurança.

## Preservação de escopo

Não foram alterados:

- pedidos;
- estoque;
- dupla confirmação;
- rastreabilidade;
- cálculos de reputação;
- funcionamento do perfil público da loja;
- fluxos administrativos existentes.

## Arquivos alterados

- `.env.example`
- `app.py`
- `database.py`
- `static/styles.css`
- `templates/admin.html`
- `templates/index.html`
- `templates/loja_publica.html`
- `templates/minha_conta.html`
- `templates/painel_vendedor.html`
- `templates/reputacao_usuario.html`
- `tests/test_moderacao.py`
- `docs/README.md`
- `docs/RELATORIO_PROGRAMA_FUNDADORES.md`

## Testes

Foram adicionados testes para:

- concessão automática no cadastro;
- respeito ao limite configurado;
- incorporação segura dos primeiros usuários existentes;
- concessão manual pelo administrador;
- remoção excepcional sem apagar histórico;
- lista, métrica e filtro administrativo;
- bloqueio de alterações por usuário comum;
- exibição no perfil público, painel do vendedor e perfil do usuário.

Resultado final: **77 testes aprovados de 77**.

## Riscos e cuidados de publicação

- A primeira inicialização em produção executará a migração aditiva e classificará os usuários existentes pela data de criação e identificador.
- `FOUNDERS_LIMIT` deve permanecer em `100` se esse for o número oficial da campanha.
- Um backup recente do banco deve continuar disponível antes da publicação, conforme o procedimento permanente do projeto.
