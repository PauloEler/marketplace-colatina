# RFC — Missão 009: Compre Perto de Você

**Status:** proposta
**Decisão solicitada:** aprovar ou rejeitar a especificação antes de implementação

## Problema

A Home oferece busca, categorias e produtos, mas não traduz necessidades cotidianas em caminhos temáticos. Parte do público pensa em “fazer um churrasco” ou “compras do dia”, não em uma taxonomia de categorias.

## Objetivo

Validar uma vitrine temática que aumente entradas qualificadas no Marketplace sem criar canal paralelo, favorecer empresas ou alterar módulos existentes.

## Hipótese

Se a Home apresentar necessidades cotidianas em linguagem natural e cada card abrir uma listagem ampla do Marketplace, mais visitantes iniciarão uma navegação comercial e chegarão a produtos ou empresas locais.

## Proposta

- nova seção após Cidade Viva e antes de Produtos em destaque;
- cinco temas iniciais;
- todos os cards terminam em listagens do Marketplace;
- temas configurados por termos e categorias, nunca por empresa;
- rotação editorial por período;
- feature flag desligada por padrão;
- medição do funil Home → Marketplace → produto/empresa.

## Alternativas consideradas

### A. Destacar uma loja por semana

Rejeitada. Gera favorecimento, transforma a Home em mídia de uma empresa e enfraquece a neutralidade do Marketplace.

### B. Criar catálogo próprio dentro da seção

Rejeitada. Duplica Produtos e cria caminho de venda paralelo.

### C. Usar apenas categorias existentes

Mantida como experiência atual, mas insuficiente para testar linguagem de necessidade. A nova seção complementa, não substitui Categorias.

### D. Vitrine temática com destino agregado

Recomendada. Preserva o Marketplace, amplia descoberta e pode ser revertida integralmente.

## Escopo de uma futura Sprint

Caso o documento seja aprovado, a Sprint técnica poderá incluir somente:

- componente da seção;
- configuração central de temas;
- links para filtros existentes do Marketplace;
- feature flag;
- eventos de Analytics já aprovados;
- testes de neutralidade, destino, acessibilidade e reversão.

Banco novo, alteração da ordenação, checkout, páginas de empresa ou mudança de regras comerciais não estarão autorizados.

## Riscos e controles

| Risco | Controle |
| --- | --- |
| Favorecimento de uma empresa | temas sem identificador de empresa e resultado agregado |
| Tema sem resultados | validação prévia e desativação automática/operacional |
| Duplicação de Categorias | linguagem de necessidade e posição distinta |
| Home mais longa | limite de temas e componente compacto |
| Tema regulado | revisão antes da ativação |
| Métrica de vaidade | sucesso exige navegação interna, não apenas clique |
| Regressão | feature flag, commit único e teste com flag desligada |

## Critérios de aceite documental

- problema, público e benefício observável definidos;
- princípio Home apresenta / Marketplace vende preservado;
- regras de neutralidade verificáveis;
- métricas e limitações documentadas;
- reversão definida;
- protótipos não executáveis disponíveis;
- nenhuma alteração de código ou sistema.

## Pergunta de aprovação

> A Diretoria aprova a vitrine temática, as regras de neutralidade, o piloto e a preparação de uma Sprint técnica separada?
