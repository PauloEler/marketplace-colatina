# Plano de ação priorizado — SEO

## P0 — bloquear trabalho às cegas

| Ação | Responsável sugerido | Dependência | Evidência de conclusão |
| --- | --- | --- | --- |
| Criar propriedade de domínio no Search Console | titular do domínio + técnico | acesso ao DNS | propriedade verificada |
| Enviar sitemap | técnico | Search Console verificado | status “Sucesso” no relatório |
| Inspecionar quatro modelos de URL | técnico | propriedade disponível | resultado de URL Inspection registrado |
| Criar GA4 e fluxo Web | titular + técnico | decisão de titularidade | ID `G-` documentado |
| Aprovar consentimento e política | Diretoria | definição de dados | texto e comportamento aprovados |
| Instalar e testar uma única Google tag | técnico | GA4 + consentimento | Realtime e DebugView confirmados |

## P1 — corrigir sinais técnicos

| Ação | Dependência | Aceite |
| --- | --- | --- |
| Refazer sitemap | aprovação de alteração de backend | anúncios ativos incluídos; autenticação excluída |
| Criar matriz `index/noindex` | decisão editorial | todas as rotas públicas classificadas |
| Padronizar canonical | matriz aprovada | nenhuma URL indexável sem canonical |
| Implementar JSON-LD | dados reais disponíveis | Rich Results Test sem erro aplicável |
| Corrigir duplicidades | decisão dos proprietários dos anúncios | uma versão canônica por oferta real |
| Configurar cache de estáticos | versionamento de ativos | cache longo sem impedir atualização |
| Melhorar LCP mobile | captura de elemento LCP | laboratório abaixo de 2,5 s em execuções repetidas |

## P2 — construir demanda local

1. índice de empresas com paginação e filtros rastreáveis;
2. páginas-piloto: eletricista, frete e diarista em Colatina, somente com oferta real;
3. hubs de categorias e bairros com massa crítica;
4. metadados sociais consistentes;
5. links internos entre empresa, produto, serviço e bairro;
6. conteúdo Cidade Viva com fonte, autoria, data e expiração.

## P3 — medir e melhorar

- comparar semanalmente páginas enviadas, indexadas e excluídas;
- acompanhar consultas, cliques, CTR e posição por tipo de landing;
- medir conversões: contato, necessidade publicada, anúncio iniciado e cadastro concluído;
- acompanhar LCP, INP e CLS no percentil 75 quando houver dados;
- revisar páginas sem impressão após 60–90 dias;
- registrar lições aprendidas antes de ampliar a arquitetura.

## Sequência recomendada

```text
Propriedade e medição
        ↓
Controle de indexação
        ↓
Canonical + sitemap + schema
        ↓
Performance móvel
        ↓
Pilotos locais úteis
        ↓
Medição por 30–90 dias
        ↓
Escala baseada em dados
```

## Ações não autorizadas nesta missão

- alterar backend, banco, Home, UX, Marketplace ou pedidos;
- criar propriedades ou tags Google;
- enviar sitemap;
- publicar páginas locais;
- aplicar schema, canonical, cache ou `noindex`;
- fazer merge ou deploy.
