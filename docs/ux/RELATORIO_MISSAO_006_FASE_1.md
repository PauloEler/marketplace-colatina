# Relatório — Missão 006, Fase 1

## Status

Protótipo implementado em branch isolada. Sem merge e sem deploy.

## Entrega técnica

- feature flag `HOME_CIDADE_VIVA_ENABLED`, desligada por padrão;
- limite configurável `HOME_CIDADE_VIVA_PRODUCT_LIMIT`;
- vitrine curta com “Ver todos os produtos”;
- até três lojas em destaque com acesso à composição integral;
- bloco Cidade em movimento alimentado somente por consultas reais;
- anúncios recentes sem duplicar a vitrine principal;
- composição responsiva, focável e sem overflow da página;
- backups anteriores com hashes verificáveis;
- evidências antes/depois em cinco referências de largura.

## Preservação

Não foram alterados marketplace, pedidos, anúncios existentes, empresas, parceiros, afiliados, analytics, notificações, dashboards, autenticação, rotas ou banco. Os blocos anteriores permanecem no template e voltam integralmente quando a flag é desativada.

## Arquivos funcionais

- `app.py`
- `templates/index.html`
- `static/styles.css`
- `tests/test_moderacao.py`

## Validação

- suíte completa: **143 testes aprovados**;
- `ruff check .`: aprovado;
- `ruff format --check .`: aprovado, 19 arquivos formatados;
- `git diff --check`: aprovado;
- flag desligada: classe e blocos novos ausentes, composição anterior preservada;
- flag ligada: 4 de 8 produtos, 3 de 4 lojas, 3 novidades e 3 métricas reais;
- “Ver todos os produtos”: destino `/?todos=1#ofertas`, 8 produtos e composição integral confirmados;
- responsividade: 1440, 1024, 768, 390 e 320 px sem overflow da página;
- teclado: foco percorreu logo, menu, Comprar agora, Anunciar grátis, Compartilhar, busca, categoria, Encontrar agora, Encontre Quem Resolve e categorias;
- acessibilidade: um `h1`, nenhum `id` duplicado, alvos novos com no mínimo 44 px e foco visível;
- console da página: sem erros ou avisos da aplicação. Mensagens observadas no histórico global pertenciam a extensões do Chrome e não à Home;
- reversão lógica por flag e por `?todos=1`: aprovada;
- reversão atômica em worktree isolada: aprovada; o revert retornou exatamente ao hash-base e os 139 testes da versão anterior passaram.

## Limitações

- O protótipo não alterna dados por tempo nem adiciona JavaScript novo.
- Cidade em movimento só aparece quando existe pelo menos uma métrica real maior que zero.
- A listagem integral usa a mesma rota com `?todos=1`, sem criar nova regra de negócio.
- A flag deverá continuar desligada até auditoria visual e autorização de publicação.

## Próxima decisão

Paulo deverá comparar as capturas, testar a branch e decidir entre rejeitar integralmente, solicitar ajustes ou autorizar uma publicação futura. Esta missão não realiza merge nem deploy.
