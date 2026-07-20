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

## Publicação

- PR: #71;
- hash do merge: `5baec757ccf16c16020859f8697fc0d472e2a3cf`;
- CI da `master`: aprovado no workflow `29739307446`;
- deploy automático no Render: detectado em produção em 20/07/2026 às 08h42, horário de Brasília;
- URL: `https://mercadocolatina.com.br`.

## Validação em produção

- botão **Sugira uma melhoria**: aprovado;
- formulário público: aprovado;
- cadastro controlado: aprovado, com confirmação visual após o envio;
- painel administrativo: aprovado, com sugestão, filtros, estados e métricas;
- alteração de status: aprovada, de Nova para Arquivada;
- cálculo do tempo médio até análise: aprovado após a mudança de estado;
- desktop 1440 px: aprovado, sem overflow;
- tablet 768 px: aprovado, sem overflow;
- mobile 390 px: aprovado, sem overflow;
- mobile 320 px: aprovado, sem overflow;
- botão responsivo: aprovado nas quatro larguras;
- console público e administrativo: sem erros originados pelo site.

O registro controlado foi identificado como teste de publicação e arquivado após a validação. Mensagens observadas no console administrativo foram isoladas como originadas por extensões do Chrome, sem relação com o Mercado Colatina.

## Próximos passos

Medir o uso real do canal. Qualquer votação futura deverá responder a identidade, privacidade, moderação e prevenção a abuso em RFC e ADR próprios.

## Estado da publicação

Publicada em produção. O primeiro fluxo de participação da comunidade está ativo.
