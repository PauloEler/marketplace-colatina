# Relatório — Missão 001 — Ouvir Colatina

## Problema real da cidade

Moradores não possuíam um canal estruturado para dizer o que está faltando em Colatina. As contribuições ficavam dispersas em conversas, sem classificação, acompanhamento ou medição, o que impedia transformar escuta em decisão verificável.

## Objetivo

Receber sugestões simples da comunidade, organizá-las para análise administrativa e medir o fluxo sem coletar dados pessoais desnecessários nem interferir nos módulos existentes.

## Entrega

- botão global discreto **Sugira uma melhoria**;
- formulário público em `/sugerir`, com nome opcional, dez categorias e mensagem;
- tabela isolada `sugestoes_comunidade`;
- painel restrito a administradores em `/admin/sugestoes`;
- filtros por categoria e estado;
- estados Nova, Em análise, Planejada, Implementada e Arquivada;
- métricas de total, implementadas, ranking de categorias e tempo médio até a primeira análise;
- proteção CSRF, validação de tamanho e categorias permitidas;
- página de privacidade e sitemap atualizados;
- arquitetura de votação registrada para evolução futura, sem criar regra ou armazenamento prematuro.

## Arquitetura e arquivos

- `community_suggestions.py`: regras, consultas e métricas do domínio;
- `database.py`: tabela e índices próprios;
- `app.py`: rotas públicas e administrativas;
- `templates/sugerir.html`: jornada pública;
- `templates/sugestoes_admin.html`: triagem administrativa;
- `templates/base.html`: chamada global e acesso administrativo;
- `static/styles.css`: estilos totalmente prefixados por `community-`;
- `tests/test_moderacao.py`: cobertura funcional, de isolamento e responsividade contratual;
- `docs/comunidade/`: documento funcional, RFC, ADR e este relatório.

## Privacidade e segurança

O nome é opcional. Não são armazenados IP, localização, contato ou vínculo com conta. O formulário orienta o usuário a não informar dados sensíveis. Atualizações de estado são exclusivas de administrador e protegidas por CSRF.

## Validação

- fluxo público de envio: aprovado;
- validação de categoria e mensagem: aprovada;
- acesso administrativo e isolamento de permissão: aprovado;
- filtros e mudança de estado: aprovados;
- cálculo de métricas após análise: aprovado;
- desktop 1440 px: sem overflow;
- tablet 768 px: sem overflow;
- mobile 390 px: sem overflow;
- mobile 320 px: sem overflow;
- teclado, rótulos e foco: estrutura acessível confirmada;
- console do navegador: sem erros ou avisos;
- Marketplace, Analytics de afiliados, Ofertas, Empresas Parceiras, Hoje em Colatina e Central de Notificações: preservados.

- suíte completa: **119 testes aprovados**;
- `ruff check`: aprovado;
- `ruff format --check`: aprovado;
- `git diff --check`: aprovado;
- CI remoto da PR Draft #71: aprovado.

## Limitações

- não há votação nesta missão;
- não há publicação automática nem promessa de implementação;
- não há notificação, e-mail ou integração externa;
- métricas de produção somente existirão depois de eventual merge e deploy autorizados.

## Próximos passos

Revisar a PR Draft. Qualquer votação futura deverá responder a identidade, privacidade, moderação e prevenção a abuso em RFC e ADR próprios.

## Estado da publicação

PR Draft #71 aberta para revisão. Sem merge. Sem deploy. Aguardando aprovação.
