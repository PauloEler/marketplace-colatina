# RFC — Analytics dos Afiliados

## Status

Implementada na branch `agent/mx004-1d-analytics-afiliados`, aguardando revisão.

## Contexto

A seção de parceiros já possui seis links oficiais, mas não havia informação interna sobre exposição e interesse. Tomar decisões apenas pelo painel do parceiro dificulta comparar categorias e entender o comportamento dentro da Home.

## Decisão

Adotar eventos anônimos e append-only no banco atual:

- `impression`: card visível em pelo menos 50%;
- `click`: ativação do link de uma oferta;
- dimensões: parceiro, oferta, categoria, origem, dispositivo e data/hora.

O endpoint público é protegido pelo token CSRF da sessão e valida todos os valores enumerados. Os campos comerciais são obtidos no servidor, não aceitos do cliente.

## Alternativas avaliadas

### Reutilizar somente `estatisticas`

Rejeitada. A estrutura chave/valor não preserva data, dispositivo, categoria e parceiro, inviabilizando janelas de 7/30 dias e CTR.

### Usar somente Google Analytics

Adiada. Criaria dependência externa, exigiria governança adicional de consentimento e não entregaria um dashboard administrativo integrado nesta Sprint.

### Registrar apenas cliques

Rejeitada. Sem impressões não existe denominador técnico para calcular CTR.

## Arquitetura escolhida

- configuração comercial: `partner_offers.py`;
- captura no navegador: `static/partner-offers-carousel.js`;
- endpoint e autorização: `app.py`;
- validação e agregação: `affiliate_analytics.py`;
- persistência: tabela `afiliado_eventos` em `database.py`;
- visualização: `templates/analytics_afiliados.html`.

## Impacto esperado

- decisões de ordem e seleção de ofertas baseadas em dados;
- comparação de desktop e mobile na base bruta;
- inclusão futura de parceiros sem redesenhar a camada de eventos;
- ausência de impacto visual na Home.

## Segurança e privacidade

- nenhum dado pessoal ou IP é persistido;
- token CSRF obrigatório;
- lista fechada para tipo de evento e dispositivo;
- oferta precisa existir na configuração oficial;
- origem, parceiro e categoria são definidos pelo servidor;
- dashboard exclusivo para administrador.

## Consequências e limitações

O banco atual recebe uma nova tabela e dois índices. O volume cresce em uma linha por evento; políticas de retenção e agregação histórica deverão ser avaliadas quando houver volume real. Receita e conversão continuam dependentes dos relatórios de cada parceiro.

## Próximos passos

1. Medir o volume após 30 dias.
2. Definir política de retenção e agregação mensal.
3. Integrar conversões ou receitas quando os programas oferecerem APIs oficiais adequadas.
4. Permitir filtros por parceiro e dispositivo quando houver base suficiente.
