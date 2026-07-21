# ADR — Balão da Cidade integrado e reversível

## Status

Aceito para PR Draft.

## Contexto

Era necessário usar o espaço lateral da Cidade Viva sem criar uma propaganda, popup ou camada sobre a Home.

## Decisão

Usar um grid de duas colunas somente no encontro entre Cidade Viva e Balão da Cidade. O painel passa para uma linha própria em até 960 px e para um card vertical em até 640 px. Todos os estilos são descendentes de `.home-city-balloon-ux007a`.

A ativação depende de `HOME_CITY_BALLOON_ENABLED`, com valor padrão `false`, e também da Home 2.0. A reversão operacional exige apenas desligar a flag. A reversão definitiva usa um único revert do commit do patch.

## Consequências

- a Home publicada permanece idêntica até ativação explícita;
- dados existentes podem ser apresentados sem duplicar consultas;
- o painel não persiste nem coleta dados;
- o layout continua legível mesmo quando não há métricas reais;
- o rodapé fica menor sem remover informações.
