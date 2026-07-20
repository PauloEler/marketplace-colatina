# ADR - REGISTRO MINIMO DA TRACAO COMERCIAL

## Status

Aceita para a PR Draft da Missao 004.

## Decisao

Usar tres tabelas isoladas e um modulo `commercial_growth.py`. O painel sera exclusivo do administrador. O relatorio sera gerado dinamicamente; nao sera criado scheduler, arquivo mutavel em producao ou integracao externa.

## Motivos

- preserva separacao dos dominios protegidos;
- oferece fonte oficial para indicadores antes inexistentes;
- evita implantar CRM completo;
- permite uma unica missao ativa;
- minimiza contato e participacao armazenados;
- reutiliza dados oficiais da plataforma sem duplicacao.

## Consequencias

Visitas, checklists e indicacoes dependem de registro administrativo correto. O sistema nao confirma automaticamente relacoes externas. Evolucoes como edicao completa, exclusao, automacao ou integracao exigem nova RFC.

## Alternativas rejeitadas

- planilha externa: fragmentaria a fonte de verdade;
- alterar usuarios ou pedidos: violaria separacao de dominio;
- CRM completo: excederia o problema atual;
- relatorio agendado por servico externo: criaria dependencia desnecessaria.
