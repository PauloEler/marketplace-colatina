# Checklist SEO — Missão 008.1

Legenda: `[x]` verificado/aprovado, `[~]` parcial ou requer correção, `[ ]` pendente, `[N/M]` não mensurável.

## Indexação

- [x] `robots.txt` responde HTTP 200.
- [x] `robots.txt` declara sitemap.
- [~] `sitemap.xml` responde e é válido, mas não representa todos os anúncios ativos.
- [~] canonical presente em Home, anúncios e lojas; ausente em 21 URLs.
- [ ] definir e aplicar matriz de `noindex`.
- [~] duas lojas sem link encontrado a partir da Home.
- [~] títulos e descrições duplicados identificados.
- [N/M] cobertura real no Google, pendente do Search Console.
- [~] consulta pública `site:` sem resultados na data da coleta; não conclusiva isoladamente.

## SEO on-page

- [x] title presente em todas as páginas examinadas.
- [~] um title acima de 60 caracteres e um par duplicado.
- [x] meta description presente em todas as páginas.
- [~] descrição genérica repetida em 18 URLs.
- [~] H1 ausente em Login, Cadastro e nos destinos anônimos de `/comprar/<id>`.
- [x] nenhum documento com múltiplos H1 renderizados.
- [x] nenhuma imagem sem atributo ALT.
- [x] Open Graph básico presente.
- [~] Twitter Cards ausentes em 21 URLs.
- [ ] JSON-LD.
- [ ] Schema.org por tipo de página.

## Performance

- [x] Lighthouse desktop executado.
- [x] Lighthouse mobile executado.
- [~] LCP mobile de laboratório: 3,745 s.
- [x] CLS de laboratório: 0.
- [N/M] INP de campo.
- [x] TBT mobile de laboratório: 43 ms.
- [x] compressão Brotli em recursos textuais.
- [ ] cache longo e versionado para estáticos.
- [~] lazy loading em 22 de 34 imagens; exceções exigem revisão contextual.
- [~] aproximadamente 36,6–40,4 KB de CSS não utilizado por perfil.

## Google

- [ ] propriedade de domínio no Search Console.
- [ ] verificação DNS.
- [ ] sitemap enviado no Search Console.
- [N/M] páginas válidas, excluídas e com erro.
- [N/M] impressões, cliques, CTR e posição média.
- [ ] propriedade GA4 do Mercado Colatina.
- [ ] fluxo Web do domínio.
- [ ] Google tag.
- [ ] consentimento e política compatíveis.
- [ ] eventos e conversões.
- [ ] conta/container do Tag Manager, se adotado.
- [ ] validação pelo Tag Assistant.

## SEO local

- [~] lojas públicas existentes.
- [ ] índice público de empresas.
- [ ] landings de categorias locais.
- [ ] páginas editoriais de serviços.
- [ ] páginas úteis por bairro.
- [~] anúncios de produtos indexáveis, mas fora do sitemap em parte.
- [ ] páginas de eventos com dados reais.
- [ ] páginas editoriais do Cidade Viva.
- [~] Encontre Quem Resolve funcional, sem arquitetura pública de descoberta por serviço.
- [ ] governança de privacidade para impedir indexação de necessidades pessoais.

## Restrições respeitadas

- [x] backend preservado.
- [x] banco preservado.
- [x] UX e Home preservadas.
- [x] Marketplace e pedidos preservados.
- [x] nenhuma conta Google alterada.
- [x] sem merge e sem deploy.
