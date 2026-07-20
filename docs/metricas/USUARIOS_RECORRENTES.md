# Usuários Recorrentes

## Objetivo

Medir se o Mercado Colatina se torna útil o suficiente para que pessoas retornem, sem criar rastreamento invasivo.

## Definição inicial

Usuário recorrente autenticado é aquele com atividade válida em pelo menos dois dias distintos dentro de uma janela de 30 dias. Visitas anônimas recorrentes não serão inferidas nesta versão.

## Atividade válida

Uma ação funcional do produto, como consultar conta autenticada, anunciar, gerir anúncio, iniciar ou acompanhar pedido, abrir notificação ou usar uma jornada com evento explicitamente aprovado. Recarregamentos e verificações automáticas devem ser excluídos quando identificáveis.

## Indicadores derivados

- usuários ativos em 30 dias;
- usuários recorrentes em 30 dias;
- proporção de recorrência;
- frequência mediana de dias ativos;
- recorrência por jornada, somente de forma agregada.

## Limitações

A definição não mede satisfação nem prova problema resolvido. Mudanças de autenticação, dispositivos compartilhados e usuários sem login podem afetar a leitura. Qualquer implementação exigirá RFC própria e revisão de privacidade.
