# Auditoria SEO completa — Missão 008.1

- **Projeto:** Mercado Colatina
- **Data da coleta:** 21/07/2026
- **Produção:** `https://mercadocolatina.com.br`
**Natureza:** auditoria somente leitura

## Resumo executivo

A infraestrutura pública está disponível para rastreamento, mas ainda não existe instrumentação oficial para confirmar indexação ou desempenho orgânico. `robots.txt` e `sitemap.xml` respondem corretamente, a Home possui canonical e a mídia usa compressão Brotli quando aplicável. Em contrapartida, o sitemap não representa todos os anúncios ativos, 21 URLs rastreadas não possuem canonical, não há `noindex` nas páginas transacionais examinadas e nenhuma das 35 páginas possui JSON-LD.

O maior risco atual é operar SEO sem Search Console, GA4 ou Tag Manager. A consulta pública `site:mercadocolatina.com.br` não retornou resultados na coleta, mas essa consulta não substitui o relatório de indexação do Search Console.

## Método e limites

- crawl iniciado pela Home, limitado a 80 URLs e sem autenticação;
- 35 documentos HTML públicos efetivamente examinados;
- leitura do sitemap, robots, cabeçalhos HTTP e código-fonte do repositório;
- Lighthouse 13.0 em produção, perfis desktop e mobile;
- inspeção autenticada e somente leitura de Search Console, GA4 e Tag Manager;
- nenhuma conta, propriedade, tag, arquivo de runtime ou configuração foi alterada;
- métricas de campo de Core Web Vitals não estavam disponíveis.

## Inventário objetivo

| Indicador | Resultado |
| --- | ---: |
| Páginas HTML rastreadas | 35 |
| URLs no sitemap | 17 |
| URLs sem canonical | 21 |
| URLs com `noindex` em meta | 0 |
| Páginas sem H1 | 11 |
| Páginas com mais de um H1 | 0 |
| Páginas sem meta description | 0 |
| Páginas sem Twitter Cards | 21 |
| Páginas sem JSON-LD | 35 |
| Imagens encontradas | 34 |
| Imagens sem atributo ALT | 0 |
| Imagens com `loading="lazy"` | 22 |
| Links internos quebrados | 0 |
| Anúncios ativos fora do sitemap | 9 |
| Lojas no sitemap sem link encontrado no crawl | 2 |

## Indexação

### `robots.txt` — aprovado

Responde HTTP 200, permite rastreamento geral e declara `https://mercadocolatina.com.br/sitemap.xml`. Não foi encontrada regra que bloqueie CSS, JavaScript ou imagens necessárias à renderização.

### `sitemap.xml` — alto

Responde HTTP 200 e XML válido, com 17 URLs. Inclui páginas de baixa prioridade orgânica, como Login e Cadastro, mas exclui nove anúncios ativos encontrados pelo crawler. Também inclui seis lojas, das quais duas não receberam link no crawl iniciado pela Home.

- **Impacto:** descoberta incompleta dos anúncios e uso inadequado do sitemap como sinal de URLs canônicas.
- **Correção:** incluir anúncios públicos ativos e retirar URLs transacionais ou de autenticação.
- **Estimativa:** 4–8 horas.
**Prioridade:** alta.

### Canonical — alto

A Home, os anúncios e as lojas públicas possuem canonical. Vinte e uma URLs não possuem, incluindo páginas institucionais, autenticação, recuperação e URLs `/comprar/<id>` que terminam na tela de Login para visitante não autenticado.

- **Impacto:** sinais divididos, relatórios menos claros e risco de o Google escolher outra URL representativa.
- **Correção:** canonical autorreferente nas páginas indexáveis e `noindex` nas páginas que não devem competir na busca.
- **Estimativa:** 6–10 horas.
**Prioridade:** alta.

### `noindex` — alto

Nenhuma das páginas examinadas declarou `noindex` via meta. Também não foi identificada configuração `X-Robots-Tag` no código. Login, Cadastro, Recuperar acesso e fluxos `/comprar/<id>` não oferecem valor como página de entrada orgânica.

- **Impacto:** desperdício de rastreamento e possibilidade de páginas transacionais aparecerem em busca.
- **Correção:** definir matriz indexável/não indexável e aplicar `noindex,follow` às rotas privadas ou transacionais, sem bloqueá-las no robots.
- **Estimativa:** 4–6 horas.
**Prioridade:** alta.

### Páginas órfãs — médio

As lojas `5-joao-silva` e `6-roberto-dias-ribeiro` estão no sitemap, mas não foram descobertas pelos links do crawl. Isso significa “sem link encontrado na amostra”, não uma prova absoluta de orfandade.

- **Impacto:** menor circulação de autoridade interna e pior descoberta.
- **Correção:** garantir listagem/paginação pública e links contextuais para toda loja ativa.
- **Estimativa:** 4–8 horas.
**Prioridade:** média.

### Duplicidades — alto

- anúncios 13 e 14: mesmo title e mesma descrição;
- nove URLs `/comprar/<id>` terminam no mesmo conteúdo e title de Login para visitante anônimo;
- a descrição global genérica se repete em 18 URLs rastreadas.

- **Impacto:** baixa diferenciação, canibalização e snippets pouco relevantes.
- **Correção:** consolidar anúncios realmente duplicados, aplicar `noindex` aos fluxos e criar descrições próprias para páginas indexáveis.
- **Estimativa:** 1–2 dias.
**Prioridade:** alta.

## SEO on-page

### Title — médio

Todos os documentos examinados possuem title. O anúncio 2 tem 78 caracteres e pode sofrer truncamento. Anúncios 13 e 14 repetem exatamente o mesmo title. Títulos curtos das páginas institucionais não são erro por si só, mas deixam de comunicar intenção local.

### Meta description — médio

Nenhuma está vazia. Sete anúncios têm descrições com menos de 70 caracteres e 18 URLs usam a descrição genérica do template. Não existe garantia de que o Google exibirá a descrição, mas textos específicos melhoram a clareza do resultado.

### Headings — baixo/médio

A Home possui um H1 renderizado, 15 H2 e 32 H3, com hierarquia funcional. Login e Cadastro usam H2 sem H1. As nove URLs `/comprar/<id>` examinadas terminam no Login e também ficam sem H1. Para páginas que receberão `noindex`, isso é baixo; para Login e Cadastro enquanto rastreáveis, é uma inconsistência semântica.

### ALT — aprovado

As 34 imagens examinadas possuem atributo ALT, inclusive ALT vazio em elementos decorativos. Não foram encontradas imagens sem o atributo.

### Open Graph — aprovado/parcial

Todas as páginas herdam propriedades OG básicas. Home, anúncios e lojas possuem sinalização mais específica; diversas páginas institucionais herdam conteúdo genérico. A correção é editorial, não de ausência total.

### Twitter Cards — médio

Vinte e uma URLs não possuem tags Twitter. A Home informa card e imagem, mas não declara `twitter:title` e `twitter:description` próprios; depende dos sinais OG.

### JSON-LD e Schema.org — alto

Nenhuma das 35 páginas examinadas possui bloco `application/ld+json`. Tipos candidatos, sujeitos à correspondência exata com o conteúdo visível:

- Home/Quem Somos: `Organization` ou subtipo compatível com a operação online;
- anúncios: `Product`, sem inventar avaliações, estoque ou frete;
- lojas físicas elegíveis: subtipo específico de `LocalBusiness`;
- navegação: `BreadcrumbList`;
- futuras páginas editoriais: schema correspondente ao conteúdo real.

Não se deve marcar o Mercado Colatina como estabelecimento físico se ele não atender clientes presencialmente no local informado.

## Performance

### Lighthouse

| Perfil | Performance | Acessibilidade | Boas práticas | SEO | FCP | LCP | CLS | TBT | Peso |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Desktop | 99 | 93 | 96 | 100 | 0,448 s | 0,808 s | 0 | 0 ms | 708 KB |
| Mobile | 86 | 93 | 96 | 100 | 1,210 s | 3,745 s | 0 | 43 ms | 709 KB |

### Core Web Vitals — não confirmados em campo

- **LCP:** laboratório mobile em 3,745 s, faixa “precisa melhorar”; desktop em 0,808 s;
- **CLS:** laboratório 0 nos dois perfis;
- **INP:** não mensurável pelo Lighthouse; exige interação real/CrUX ou instrumentação;
- **TBT:** 43 ms no mobile, bom sinal de laboratório, mas não substitui INP;
- **dados de campo:** indisponíveis porque não existe propriedade no Search Console e não foi obtido relatório CrUX verificável.

### Compressão — aprovado

HTML, CSS, JavaScript e SVG examinados usam Brotli. JPEG e WebP não recebem compressão HTTP adicional, comportamento esperado para formatos já comprimidos.

### Cache — alto

Os recursos estáticos respondem com `Cache-Control: no-cache`. O CSS principal possui aproximadamente 313 KB e os ativos usam URLs sem hash de conteúdo.

- **Impacto:** downloads repetidos e pior carregamento em visitas recorrentes.
- **Correção:** versionar ativos por hash ou versão e adotar cache longo `public, max-age, immutable`; manter HTML com política curta.
- **Estimativa:** 1–2 dias.
**Prioridade:** alta.

### Lazy loading — médio

Vinte e duas das 34 imagens usam lazy loading. A imagem principal da Home usa `fetchpriority="high"`, corretamente fora de lazy. As demais exceções devem ser revisadas individualmente; não é correto aplicar lazy indiscriminadamente acima da dobra.

### CSS — médio

O Lighthouse estimou cerca de 36,6 KB de CSS não utilizado no mobile e 40,4 KB no desktop, dentro de um arquivo de 313 KB. Não há CSS não minificado relevante segundo o Lighthouse.

## Sistemas Google

| Sistema | Evidência | Situação | Severidade |
| --- | --- | --- | --- |
| Search Console | tela autenticada exibe “Adicionar um site” | propriedade ausente | crítico |
| Sitemap enviado | não há propriedade para receber envio | não enviado/indisponível | crítico |
| Cobertura e indexação | relatório inacessível sem propriedade | não mensurável | crítico |
| Consultas, cliques, CTR e posição | relatório inacessível sem propriedade | não mensurável | crítico |
| GA4 | conta “topa tudo vila lenira”, propriedade `-` | propriedade do Mercado Colatina não identificada | crítico |
| Google tag | ausente no HTML e no repositório | não instalada | crítico |
| Tag Manager | painel autenticado sem contas/containers | ausente | alto |

Ausência de medição não significa zero tráfego, zero indexação ou zero conversões.

## SEO local por área

| Área | Estado atual | Lacuna |
| --- | --- | --- |
| Empresas | lojas públicas indexáveis | faltam listagem completa, categoria e bairro |
| Categorias | filtro na Home | filtros não formam landing pages canônicas |
| Serviços | formulário “Encontre Quem Resolve” | não há páginas públicas por serviço |
| Produtos | anúncios individuais | sitemap incompleto e schema ausente |
| Bairros | informação presente em parte dos dados | não há hubs úteis por bairro |
| Eventos | placeholder em Hoje em Colatina | não há conteúdo/URL editorial |
| Cidade Viva | seção na Home | não há páginas próprias para conteúdos reais |
| Encontre Quem Resolve | formulário e painel | necessidades não devem ser indexadas sem consentimento; faltam páginas editoriais de oferta do serviço |

## Conclusão

O site pode ser rastreado, mas ainda não está pronto para uma operação de crescimento orgânico mensurável. Primeiro deve ser criada a camada de medição e controle de indexação; depois, corrigidos sitemap, canonical, `noindex`, dados estruturados e cache. Só então devem ser ampliadas as páginas locais, sempre com conteúdo útil e dados reais.

## Referências oficiais

- [Canonicalização — Google Search Central](https://developers.google.com/search/docs/crawling-indexing/canonicalization)
- [`noindex` — Google Search Central](https://developers.google.com/search/docs/crawling-indexing/block-indexing)
- [Dados estruturados de Organization — Google Search Central](https://developers.google.com/search/docs/appearance/structured-data/organization)
- [Uso básico do Search Console](https://support.google.com/webmasters/answer/10351509)
- [Relatório de desempenho do Search Console](https://support.google.com/webmasters/answer/7576553)
- [Core Web Vitals e limites — web.dev](https://web.dev/articles/defining-core-web-vitals-thresholds)
- [Configurar Google tag no GA4](https://support.google.com/analytics/answer/15756615)
- [Configurar GA4 no Tag Manager](https://support.google.com/tagmanager/answer/9442095)
