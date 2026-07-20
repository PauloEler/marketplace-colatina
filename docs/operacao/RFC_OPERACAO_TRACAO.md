# RFC — Operação Tração

## Problema

As métricas estavam distribuídas entre dashboards e tabelas operacionais, sem uma leitura única sobre recorrência, empresas, marketplace, afiliados e comunidade.

## Proposta

Ampliar o Dashboard Executivo existente com uma camada de agregação `traction_metrics.py`. Reutilizar dados oficiais já existentes e acrescentar somente duas estruturas mínimas: atividade autenticada diária e origem agregada diária.

O relatório semanal é gerado sob demanda, em Markdown, pelo mesmo agregador. Isso impede divergência entre dashboard e relatório e não exige agendador, arquivo mutável em produção ou serviço externo.

## Alternativas rejeitadas

- criar um segundo dashboard isolado: duplicaria navegação e leitura;
- armazenar cada visita com referrer, IP e user-agent: coleta excessiva;
- estimar receita de afiliados: produziria informação não oficial;
- alterar tabelas centrais: risco desnecessário durante a operação.

## Compatibilidade

O marketplace, os afiliados, a comunidade, as empresas parceiras, o Hoje em Colatina e a Central de Notificações permanecem funcionais. As novas tabelas são aditivas.

## Validação

Suíte completa, Ruff, formatação, verificação de diff, acesso administrativo, geração do Markdown, responsividade em desktop/tablet/mobile e console limpo.
