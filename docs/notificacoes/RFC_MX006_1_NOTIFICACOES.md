# RFC MX-006.1 — Central de Notificações

## Contexto

O aviso de pedidos nasceu como um contador calculado diretamente no cabeçalho. Esse desenho não poderia atender, de forma consistente, mensagens, moderação, vendas e avisos futuros.

## Proposta

Adotar uma central persistente, orientada a eventos e independente das tabelas de negócio. O cabeçalho consome uma lista resumida e a página da Central oferece histórico e ações.

## Decisões

- Tabela própria, sem alterar regras de pedidos.
- Serviço Python único como porta de entrada.
- Registros por destinatário para garantir isolamento e leitura individual.
- Chave única opcional para idempotência.
- Painel implementado com `details/summary`, funcional sem JavaScript.
- JavaScript apenas aprimora fechamento por clique externo e tecla Escape.
- Administração limitada a estatísticas agregadas.

## Impacto esperado

O usuário identifica ações importantes em qualquer página e pode controlar o estado de leitura. Novas áreas passam a ter um contrato único para emissão de avisos.

## Limitações

- Somente `NOVO_PEDIDO` gera notificações nesta versão.
- Não há atualização em tempo real; o contador é atualizado ao carregar a página.
- Não existem canais externos.
- Registros anteriores ao lançamento não são recriados automaticamente.

## Próximos passos

Adicionar produtores de eventos gradualmente, paginação do histórico, políticas de retenção e, em Sprint específica, avaliar canais externos com consentimento explícito.
