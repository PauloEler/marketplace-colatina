# Arquitetura futura — Encontre Quem Resolve indexável

## Estado

Preparada, não implementada nesta missão por proibição de alterar backend e rotas.

## URLs prioritárias

- `/servicos/eletricista-colatina`
- `/servicos/pedreiro-colatina`
- `/servicos/frete-colatina`
- `/servicos/diarista-colatina`

## Modelo da página

1. H1 específico do serviço e da cidade;
2. explicação objetiva do problema resolvido;
3. bairros atendidos com dados reais;
4. empresas ou profissionais ativos e consentidos;
5. orientação de segurança;
6. CTA “Descrever minha necessidade”;
7. perguntas frequentes reais;
8. conteúdo relacionado;
9. atualização e responsável editorial.

## Metadados

- title: `Eletricista em Colatina | Encontre quem resolve`;
- description única, entre 120 e 155 caracteres;
- canonical da própria URL;
- Open Graph e Twitter Card completos;
- JSON-LD `Service`, `BreadcrumbList` e entidades locais realmente exibidas;
- `noindex` automático quando não houver conteúdo suficiente ou prestadores ativos.

## Antispam

Não gerar combinações automáticas de serviço × bairro sem conteúdo próprio. Quatro páginas úteis têm mais valor que centenas de páginas de entrada repetitivas.

## Dependências para implementação

- autorização para alterar backend e sitemap;
- catálogo normalizado de serviços;
- consentimento e dados públicos das empresas;
- critérios de moderação e expiração;
- Search Console ativo;
- testes de conteúdo vazio, canonical e JSON-LD.
