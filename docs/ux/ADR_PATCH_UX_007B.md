# ADR — Isolamento e reversão do acabamento UX-007B

## Decisão

Adicionar `HOME_FINISH_007B_ENABLED=false`. A flag somente produz efeito quando Cidade Viva, Home 2.0 e Balão da Cidade também estão ativos.

O servidor adiciona a classe `home-finish-ux007b` e o script `home-finish-007b.js` apenas nesse estado. Toda regra visual nova é descendente dessa classe. Assim, desligar a flag remove CSS, frases rotativas e script sem tocar nos módulos anteriores.

## Consequências

- reversão operacional por uma variável e reinício do serviço;
- reversão definitiva por um único revert do commit;
- nenhuma migração e nenhum dado novo;
- a rotação é progressiva: sem JavaScript, a primeira frase continua legível.
