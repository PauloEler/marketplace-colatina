# ADR — Missão 008 Operação Google Dominante

## Status

Proposto para auditoria.

## Decisão

Executar a Missão 008 em duas camadas:

1. nesta PR, somente auditoria, documentação, baseline e ferramenta externa ao runtime;
2. em Sprints posteriores e explicitamente aprovadas, ativar Search Console, GA4 e mudanças técnicas de indexação.

## Razões

- a Ordem de Serviço proíbe mudanças em backend, banco e Home;
- páginas `/servicos/...`, sitemap de anúncios, JSON-LD e painel integrado exigiriam alteração de runtime;
- Search Console e GA4 ainda não fornecem dados;
- o Perfil “Topa Tudo Colatinense” representa uma loja física real, enquanto o Mercado Colatina é hoje uma plataforma digital.

## Perfil empresarial

O Perfil verificado “Topa Tudo Colatinense” não será renomeado automaticamente. A troca para “Mercado Colatina” poderia contrariar a representação real da empresa. O Google exige consistência com nome, sinalização e atendimento presencial. A elegibilidade de um perfil separado para o Mercado Colatina deverá ser avaliada antes de qualquer criação.

## Consequências

- nenhum risco de regressão na plataforma;
- nenhuma métrica artificial no painel;
- ativação externa depende de autorização e acesso ao DNS;
- futuras páginas locais deverão ter conteúdo útil e único, evitando páginas de entrada repetitivas.

## Reversão

Remover o único commit da Missão 008. Nenhuma configuração externa ou dado de produção foi alterado.

## Fontes oficiais

- [Diretrizes de representação no Google](https://support.google.com/business/answer/3038177)
- [Elegibilidade do Perfil da Empresa](https://support.google.com/business/answer/13763036)
- [Adicionar uma propriedade ao Search Console](https://support.google.com/webmasters/answer/34592)
