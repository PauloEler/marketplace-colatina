# As 20 maiores oportunidades de SEO

| # | Severidade | Problema | Impacto | Como corrigir | Estimativa | Prioridade |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | CRÍTICO | Search Console sem propriedade | indexação, cobertura e desempenho ficam desconhecidos | criar propriedade de domínio e verificar por DNS | 1–2 h + propagação | P0 |
| 2 | CRÍTICO | sitemap não enviado ao Search Console | não há monitoramento oficial de leitura e cobertura | enviar `/sitemap.xml` após a verificação | 30 min | P0 |
| 3 | CRÍTICO | GA4 sem propriedade do projeto | origem, retenção e conversões não são mensuradas | criar propriedade e fluxo Web sob titularidade correta | 1–2 h | P0 |
| 4 | CRÍTICO | Google tag ausente | GA4 não recebe pageviews ou eventos | instalar uma única tag com consentimento e validar | 3–6 h | P0 |
| 5 | CRÍTICO | indexação pública não confirmada | consulta `site:` vazia pode sinalizar descoberta insuficiente | inspecionar Home e páginas-chave no Search Console | 1–2 h após P0 | P0 |
| 6 | ALTO | nove anúncios ativos fora do sitemap | produtos podem ser descobertos mais lentamente | incluir somente anúncios públicos, ativos e canônicos | 4–8 h | P1 |
| 7 | ALTO | Login e Cadastro no sitemap | dilui o conjunto de URLs prioritárias | remover páginas de autenticação do sitemap | 1–2 h | P1 |
| 8 | ALTO | 21 URLs sem canonical | sinais de URL podem ser divididos | canonical autorreferente nas indexáveis | 4–8 h | P1 |
| 9 | ALTO | nenhuma regra `noindex` observada | páginas transacionais podem disputar indexação | aplicar `noindex,follow` segundo matriz aprovada | 4–6 h | P1 |
| 10 | ALTO | JSON-LD ausente em 35/35 páginas | Google recebe menos contexto sobre entidade e conteúdo | implementar Organization, Product e Breadcrumb válidos | 1–3 dias | P1 |
| 11 | ALTO | títulos/descrições duplicados nos anúncios 13 e 14 | canibalização e resultados indistintos | consolidar duplicidade ou diferenciar conteúdo real | 2–4 h | P1 |
| 12 | ALTO | descrição genérica repetida em 18 URLs | snippets menos relevantes e menor CTR potencial | criar descrições próprias apenas para páginas indexáveis | 1 dia | P1 |
| 13 | ALTO | estáticos com `Cache-Control: no-cache` | visitas recorrentes baixam novamente CSS, JS e imagens | versionar ativos e usar cache longo imutável | 1–2 dias | P1 |
| 14 | ALTO | LCP mobile de laboratório em 3,745 s | primeira dobra demora em aparelhos/rede simulados | otimizar imagem LCP, CSS crítico e cadeia de carregamento | 1–3 dias | P1 |
| 15 | ALTO | páginas de serviços locais inexistentes | perde intenção “profissional + Colatina” | publicar páginas editoriais úteis e não doorway | 3–5 dias para piloto | P2 |
| 16 | MÉDIO | filtros de categoria não são landings canônicas | intenção por categoria fica concentrada na Home | criar hubs de categoria com conteúdo e inventário reais | 3–5 dias | P2 |
| 17 | MÉDIO | nenhuma arquitetura pública por bairro | perde buscas locais de proximidade | criar hubs apenas para bairros com oferta suficiente | 5–10 dias | P2 |
| 18 | MÉDIO | duas lojas sem link encontrado na amostra | autoridade interna e descoberta ficam reduzidas | garantir paginação/listagem e links contextuais | 4–8 h | P2 |
| 19 | MÉDIO | Twitter Cards ausentes em 21 URLs | compartilhamento pode usar apresentação inconsistente | padronizar card, title, description e image | 4–8 h | P2 |
| 20 | MÉDIO | INP e CWV de campo não mensuráveis | regressões reais de experiência ficam invisíveis | ativar Search Console e coleta Web Vitals/GA4 aprovada | 1 dia + janela de dados | P2 |

## Leitura das estimativas

As estimativas representam esforço técnico ou operacional após aprovação e não incluem espera por DNS, coleta histórica do Google, produção editorial, revisão jurídica ou disponibilidade de responsáveis externos.
