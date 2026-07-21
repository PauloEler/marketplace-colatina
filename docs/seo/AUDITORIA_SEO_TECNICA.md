# Auditoria SEO técnica — baseline de 21/07/2026

## Escopo e método

- produção: `https://mercadocolatina.com.br`;
- crawler próprio, somente leitura, limitado a 80 URLs;
- Lighthouse executado contra a Home em produção;
- inspeção do código e consulta pública de indexação;
- baseline completo: `dados/baseline_2026-07-21.json`.

## Resumo executivo

| Item | Resultado | Status |
| --- | --- | --- |
| `robots.txt` | HTTP 200, permite rastreamento e declara sitemap | aprovado |
| `sitemap.xml` | HTTP 200, XML válido, 17 URLs | parcial |
| Canonical da Home | válido e absoluto | aprovado |
| Canonical de anúncios e lojas | presente | aprovado |
| Canonical nas demais páginas públicas | ausente em 21 URLs rastreadas | corrigir |
| Meta description | presente nas 35 páginas HTML rastreadas | parcial; várias genéricas |
| Title | presente | parcial; duplicidade em anúncios 13 e 14 |
| Open Graph | completo em Home, anúncios e lojas | parcial |
| Twitter Cards | completo em anúncios e lojas; incompleto na Home | parcial |
| JSON-LD | ausente nas 35 páginas rastreadas | corrigir |
| Imagens sem `alt` | nenhuma na amostra rastreada | aprovado |
| Links internos quebrados | nenhum | aprovado |
| URLs externas de contato | nove redirecionamentos 302 válidos para WhatsApp | informativo |
| Páginas sem link encontrado | duas lojas listadas no sitemap | investigar |
| Consulta `site:` | nenhum resultado do domínio retornado | crítico |

## Sitemap e arquitetura

O sitemap contém Home, páginas institucionais, login, cadastro e seis lojas. Nove anúncios ativos encontrados pelo crawler não estão no sitemap. Login e cadastro não são páginas prioritárias para resultados de busca e devem ser retirados do sitemap em uma Sprint técnica futura.

Foram encontradas 20 URLs públicas ou redirecionadas não declaradas no sitemap, incluindo nove anúncios, `/quem-resolve`, `/recuperar-acesso` e URLs transacionais `/comprar/<id>`.

As lojas `5-joao-silva` e `6-roberto-dias-ribeiro` aparecem no sitemap, mas não receberam link durante o crawl iniciado pela Home. A classificação é “sem link encontrado na amostra”, não uma afirmação absoluta de orfandade.

## Duplicidades

- anúncios 13 e 14 usam o mesmo título e descrição;
- URLs `/comprar/<id>` redirecionam visitantes não autenticados para Login e multiplicam o mesmo título final;
- filtros da Home possuem canonical para `/`, reduzindo o risco de duplicidade por query string.

## Lighthouse

| Categoria | Nota |
| --- | ---: |
| Performance | 85 |
| Acessibilidade | 93 |
| Boas práticas | 96 |
| SEO | 100 |

Métricas de laboratório:

- FCP: 1,205 s;
- LCP: 3,831 s — precisa melhorar;
- Speed Index: 4,676 s;
- TBT: 49 ms;
- CLS: 0;
- TTI: 3,928 s;
- resposta inicial: 192 ms.

A nota SEO 100 do Lighthouse não avalia a ausência de todas as oportunidades avançadas. O teste marca “dados estruturados válidos” como não aplicável quando não existe JSON-LD.

## Core Web Vitals

Não há dados de campo verificáveis: Search Console não possui propriedade e a consulta pública do PageSpeed Insights retornou limite de quota. O LCP de laboratório em 3,831 s é um sinal de atenção, mas não substitui CrUX ou o relatório de experiência do Search Console.

## Prioridades técnicas

1. configurar e verificar Search Console;
2. corrigir composição do sitemap;
3. adicionar canonical e `noindex` coerentes;
4. criar JSON-LD `Organization`, `WebSite`, `Product` e, quando aplicável, `LocalBusiness`;
5. criar páginas locais úteis, com conteúdo e disponibilidade reais;
6. reduzir LCP sem alterar a identidade visual.

## Referências

- [Criar e enviar sitemap — Google Search Central](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Dados estruturados LocalBusiness](https://developers.google.com/search/docs/appearance/structured-data/local-business)
