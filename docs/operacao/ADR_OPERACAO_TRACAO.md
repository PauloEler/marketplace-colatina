# ADR — Agregação mínima da Operação Tração

## Status

Aceita para a PR Draft da Operação Tração.

## Decisão

Reutilizar o Dashboard Executivo e os domínios existentes. Criar duas tabelas aditivas:

- `traction_user_activity_daily`: uma linha por usuário autenticado e dia;
- `traction_access_source_daily`: totais por dia e categoria de origem.

Concentrar definições, consultas e geração do relatório em `traction_metrics.py`.

## Consequências positivas

- uma única definição para cada indicador;
- baixo volume de dados;
- nenhuma API externa;
- relatório reproduzível;
- coleta compatível com minimização de dados.

## Limitações

- recorrência anterior a publicação não pode ser reconstruída;
- visitantes anônimos não formam coorte individual;
- convites a empresas ainda não são registrados;
- receita de afiliados depende de informação oficial externa.

## Revisão

Reavaliar no fim dos 30 dias. Uma integração externa somente será aceita se resolver uma lacuna real, tiver fonte oficial e preservar a minimização de dados.
