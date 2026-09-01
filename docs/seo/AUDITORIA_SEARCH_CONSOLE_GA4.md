# Auditoria Search Console e GA4 — 21/07/2026

## Google Search Console

Situação observada na conta `pelers@gmail.com`:

- tela de boas-vindas;
- botão “Adicionar um site” disponível;
- nenhuma propriedade de `mercadocolatina.com.br` cadastrada;
- sitemap não enviado pelo painel;
- cobertura, páginas válidas, erros, desempenho, consultas, CTR e posição média indisponíveis.

O `robots.txt` já declara o sitemap, mas isso não substitui a propriedade verificada nem os relatórios do Search Console.

### Ativação proposta

1. adicionar propriedade de domínio `mercadocolatina.com.br`;
2. verificar via registro DNS TXT;
3. enviar `https://mercadocolatina.com.br/sitemap.xml`;
4. inspecionar Home, uma loja e um anúncio;
5. acompanhar indexação por 28 dias;
6. exportar semanalmente cliques, impressões, CTR, posição, consultas e páginas.

## Google Analytics 4

Situação observada:

- conta selecionada: `topa tudo vila lenira`;
- propriedade exibida como `-` e URL interna `p0`;
- nenhuma propriedade GA4 do Mercado Colatina identificada;
- nenhum ID `G-...`, `gtag` ou Google Tag Manager encontrado no código;
- eventos, conversões, origem, páginas, retenção e receita não mensuráveis no GA4.

### Ativação proposta

1. criar propriedade “Mercado Colatina” com fuso `America/Sao_Paulo` e moeda BRL;
2. criar stream Web para `https://mercadocolatina.com.br`;
3. aprovar política de consentimento e privacidade antes da tag;
4. instalar o Google tag de forma configurável por ambiente;
5. validar `page_view`, `view_item`, `search`, `sign_up`, `generate_lead`, `begin_checkout` e `purchase` quando aplicável;
6. definir eventos-chave sem duplicar Analytics de Afiliados;
7. testar DebugView e tráfego interno;
8. vincular Search Console após haver dados.

## Estado das métricas

Todos os indicadores de Search Console e GA4 estão marcados como **não mensuráveis**, e não como zero. Zero implicaria uma coleta ativa sem ocorrências, o que não é o caso.

## Fontes oficiais

- [Adicionar propriedade ao Search Console](https://support.google.com/webmasters/answer/34592)
- [Relatório de desempenho](https://support.google.com/webmasters/answer/7576553)
- [Configurar Analytics para um site](https://support.google.com/analytics/answer/14183469)
- [Encontrar o ID da Google tag](https://support.google.com/analytics/answer/9539598)
