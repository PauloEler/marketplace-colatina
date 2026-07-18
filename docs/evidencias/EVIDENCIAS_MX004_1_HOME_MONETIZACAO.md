# EVIDENCIAS MX-004.1 - HOME MONETIZACAO

## Objetivo

Registrar as evidencias de validacao da sprint MX-004.1.

## Motivacao

A entrega exige comprovacao de testes de responsividade, links, carrossel, lazy loading, regressao visual, console e qualidade geral antes do PR Draft.

## Decisoes tomadas

- Registrar evidencias textuais no repositorio.
- Usar testes automatizados para confirmar estrutura, ordem, transparencia e comportamento esperado do carrossel.
- Usar verificacao local para desktop, tablet e mobile sem realizar deploy.

## Impacto esperado

- Facilitar revisao do PR.
- Reduzir risco de regressao na Home.
- Manter historico claro da entrega.

## Limitacoes

- Lighthouse depende de ambiente local e pode variar por maquina.
- A validacao visual local nao substitui teste apos publicacao futura.

## Proximos passos

- Repetir validacao visual apos publicacao futura em ambiente homologado.
- Avaliar medicao de clique em sprint posterior.

## Checklist de evidencias

- [x] Responsividade desktop.
- [x] Responsividade tablet.
- [x] Responsividade mobile.
- [x] Console sem erros.
- [x] Lighthouse local.
- [x] Regressao visual por inspecao local de estrutura e breakpoints.
- [x] Links de parceiros.
- [x] Carrossel automatico e manual.
- [x] Lazy loading.
- [x] Testes automatizados.

## Resultados registrados

### Testes automatizados

- `ruff check .` - aprovado.
- `ruff format --check .` - aprovado.
- `python -m unittest tests.test_moderacao` - 94 testes aprovados.
- `git diff --check` - aprovado.

### Responsividade

- Desktop: secao exibida abaixo de "Produtos em destaque", com 6 cards e estimativa de 4 cards visiveis.
- Tablet: secao exibida corretamente, com carrossel rolavel e controles manuais.
- Mobile: secao exibida corretamente, com estimativa de 2 cards visiveis.

### Console

- Console local sem erros JavaScript durante a validacao desktop, tablet e mobile.

### Links

- Todos os cards usam `rel="sponsored nofollow"`.
- Todos os cards abrem em nova aba com `target="_blank"`.
- Todos apontam para o link de parceiro configurado.

### Carrossel

- Navegacao manual validada: botao de proxima oferta move o carrossel.
- Rotacao automatica presente no script.
- No navegador de teste, a rotacao automatica ficou suspensa porque `prefers-reduced-motion: reduce` estava ativo; este comportamento e intencional para acessibilidade.

### Lazy Loading

- Todas as imagens dos cards usam `loading="lazy"` e `decoding="async"`.

### Lighthouse local

- Performance: 85.
- Acessibilidade: 97.
- Boas praticas: 96.
- SEO: 100.
- Observacao: apos gerar as notas, o Lighthouse exibiu um erro de permissao ao limpar pasta temporaria do Windows. O resultado da auditoria foi gerado antes desse erro.
