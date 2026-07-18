# RELATORIO SPRINT MX-004.1 - HOME MONETIZACAO

## Objetivo

Implementar a primeira evolucao da Home com foco em monetizacao sustentavel por ofertas de parceiros, preservando o Mercado Colatina como protagonista.

## Motivacao

A plataforma precisa abrir um caminho simples de receita com afiliados sem alterar regras de negocio, banco de dados, autenticacao ou fluxo de anuncios.

## Decisoes tomadas

- Criada a secao "Ofertas de Parceiros" imediatamente abaixo de "Produtos em destaque".
- Removido o bloco antigo e simples de afiliado no fim da Home.
- Criado carrossel responsivo com 6 cards.
- Criados controles manuais de anterior/proximo.
- Adicionada rotacao automatica com pausa em hover/foco.
- Incluido aviso de transparencia para visitantes.
- Adicionados SVGs locais para manter carregamento rapido.
- Criados testes automatizados cobrindo ordem da Home, transparencia, cards, links, lazy loading e controle do carrossel.

## Impacto esperado

- Aumentar potencial de receita por afiliados.
- Melhorar o acabamento comercial da Home.
- Reduzir risco de confusao entre anuncios locais e conteudo de parceiros.
- Manter performance por evitar scripts externos e APIs.

## Limitacoes

- Ofertas ainda sao estaticas.
- Nao ha patrocinadores reais nesta sprint.
- Nao ha APIs externas.
- Nao ha medicao dedicada de conversao.

## Proximos passos

- Revisar ofertas com parceiros comerciais.
- Medir cliques em uma sprint futura.
- Avaliar campanhas por categoria.
- Validar desempenho apos publicacao controlada.

## Evidencias

- Evidencias de validacao registradas em `docs/evidencias/EVIDENCIAS_MX004_1_HOME_MONETIZACAO.md`.

## Validacao realizada

- Responsividade desktop, tablet e mobile.
- Console local sem erros.
- Links de parceiros conferidos.
- Carrossel manual conferido.
- Rotacao automatica preservada no script e suspensa quando `prefers-reduced-motion` esta ativo.
- Lazy loading conferido.
- Lighthouse local executado.
- Testes automatizados executados.
