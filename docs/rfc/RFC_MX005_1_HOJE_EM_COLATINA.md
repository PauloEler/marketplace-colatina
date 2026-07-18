# RFC MX-005.1 — Hoje em Colatina

## Status

Implementada em branch para revisão. Sem merge e sem deploy.

## Objetivo

Criar o primeiro Painel Diário do Mercado Colatina com leitura rápida e arquitetura reutilizável.

## Motivação

Informações locais aumentam a utilidade recorrente da plataforma. Nesta primeira etapa, a prioridade é validar hierarquia, densidade e responsividade sem assumir riscos de fonte, atualização ou exatidão.

## Proposta

Adicionar uma seção estática com cinco categorias:

1. Tempo;
2. Eventos;
3. Empregos;
4. Farmácia de Plantão;
5. Avisos.

Cada card exibe um ícone, o estado “Em preparação”, título e resumo. A estrutura é configurada em Python e renderizada por um componente repetível no template.

## Decisões

- não integrar APIs nesta sprint;
- não apresentar conteúdo simulado como atual;
- centralizar os dados fora do template;
- usar SVG local e nenhum recurso externo;
- manter o painel abaixo do conteúdo comercial e institucional já aprovado;
- limitar o texto para permitir leitura em menos de dez segundos.

## Impacto esperado

O visitante entende imediatamente quais informações locais serão oferecidas. A equipe obtém um componente visual pronto para evolução controlada, sem criar dependência técnica ou editorial prematura.

## Performance

A seção adiciona somente marcação HTML, CSS e cinco SVGs pequenos. Não há JavaScript, requisição adicional, imagem, consulta ao banco ou processamento assíncrono.

## Riscos e mitigação

- interpretação de placeholder como dado real: mitigada por “Em preparação” em todos os cards;
- crescimento excessivo da Home: mitigado por cards compactos e texto curto;
- perda de protagonismo do marketplace: mitigada pela posição posterior às áreas principais;
- futura mistura de fontes: mitigada por identificadores e configuração centralizada.

## Limitações

Sem conteúdo diário real, filtros, páginas de detalhe, alertas, personalização, histórico, APIs ou administração.

## Próximos passos

Definir uma política de fontes oficiais e critérios de atualização para cada categoria. Toda integração futura deverá ter RFC própria, tratamento de indisponibilidade e validação editorial.
