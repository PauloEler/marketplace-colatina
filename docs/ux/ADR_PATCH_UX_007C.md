# ADR — PATCH UX-007C Alinhamento final

## Decisão

Aplicar o acabamento como uma camada CSS progressiva, ativada somente quando `HOME_FINISH_007C_ENABLED`, `HOME_FINISH_007B_ENABLED`, Balão da Cidade, Home 2.0 e Cidade Viva estiverem ativos.

## Motivação

A dependência explícita preserva exatamente a Home publicada quando a nova flag estiver desligada e evita duplicação de templates ou regras de negócio.

## Consequências

- reversão imediata por configuração;
- nenhum impacto no banco ou no backend funcional;
- seletores isolados pela classe `home-finish-ux007c`;
- uso de `:has()` limitado à grade visual de Cidade Viva em navegadores modernos.
