# RFC — PATCH UX-007C Alinhamento final

## Problema real

Em telas largas, Busca Rápida e Encontre Quem Resolve usam um limite de largura diferente da composição Cidade Viva. O Balão da Cidade também pode ficar mais alto que o conteúdo principal, criando vazio visual abaixo dos indicadores.

## Objetivo

Unificar a geometria das seções da Home, aproveitar melhor o espaço quando Cidade Viva possui somente dois indicadores e padronizar o encerramento “Ver todos”, sem alterar conteúdo, rotas ou regras de negócio.

## Solução

- nova flag `HOME_FINISH_007C_ENABLED=false`;
- largura útil comum de `80rem` para Busca Rápida, Encontre Quem Resolve e Cidade Viva;
- grade de dois indicadores ocupando duas colunas equivalentes;
- Balão compacto, alinhado ao topo e organizado como coluna editorial;
- rodapés de seção flexíveis, com “Ver todos” no canto inferior direito;
- redução apenas dos espaços internos do rodapé institucional.

## Limitações

O patch não cria conteúdo, não modifica os indicadores disponíveis e não altera Hero, backend, banco, rotas ou dashboards.

## Reversão

Definir `HOME_FINISH_007C_ENABLED=false` e reiniciar o serviço, ou reverter o único commit do patch.
