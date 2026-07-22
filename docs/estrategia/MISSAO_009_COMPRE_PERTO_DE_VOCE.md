# Missão 009 — Compre Perto de Você

**Tipo:** documento estratégico
**Status:** documentação aprovada
**Fase autorizada:** implementação reversível da Fase 1
**Implementação:** autorizada em 22/07/2026

## 1. Problema real da cidade

Moradores de Colatina nem sempre iniciam uma compra sabendo qual categoria ou empresa procurar. Muitas necessidades surgem como situações cotidianas — fazer um churrasco, comprar pão, encontrar remédio ou cuidar do jardim — e a navegação exclusivamente por categorias exige que a pessoa traduza essa necessidade para a estrutura do Marketplace.

O problema não é falta de produtos na Home. É a distância entre uma intenção cotidiana e o conjunto completo de ofertas locais capaz de atendê-la.

## 2. Objetivo

Criar uma vitrine temática na Home que transforme necessidades cotidianas em entradas qualificadas no Marketplace, aumentando a navegação por produtos e empresas locais sem criar um canal de venda paralelo.

## 3. Princípio permanente

> A Home apresenta. O Marketplace vende.

Consequências obrigatórias:

- a Home apresenta temas, não catálogos independentes;
- todo clique termina em uma listagem do Marketplace;
- nenhuma compra, seleção de empresa ou negociação acontece dentro da seção;
- Busca, Categorias e Produtos em destaque permanecem intactos;
- a seção nunca direciona diretamente a uma empresa específica;
- a ordem final dos resultados é a ordem neutra do Marketplace.

## 4. Público beneficiado

### Moradores

- encontram caminhos rápidos para compras recorrentes;
- descobrem mais de uma empresa capaz de atender à necessidade;
- permanecem dentro de uma jornada única e previsível.

### Comerciantes

- participam por compatibilidade entre seus anúncios e o tema;
- não precisam comprar exclusividade para aparecer;
- recebem tráfego contextual sem favorecimento editorial.

## 5. Proposta de experiência

### Nome

**🛒 COMPRE PERTO DE VOCÊ**

### Subtítulo

**Tudo o que você precisa no comércio da sua cidade.**

### Localização

```text
Cidade Viva
    ↓
Compre Perto de Você
    ↓
Produtos em destaque
```

### Comportamento

Cada card representa uma intenção de compra. Ao selecionar um tema, o visitante entra no Marketplace com filtros ou termos previamente definidos e vê todas as empresas e todos os anúncios elegíveis.

Exemplo:

```text
🌿 Jardinagem
    ↓
Marketplace filtrado pelo tema
    ↓
Anúncios compatíveis de todas as empresas
    ↓
Página do produto ou da empresa escolhida pelo usuário
```

## 6. Temas aprovados para a Fase 1

| Identificador | Título | Intenção | Destino obrigatório |
| --- | --- | --- | --- |
| `mercadinhos` | Mercadinhos | itens essenciais e compras do dia a dia | `/?q=mercadinho` |
| `bares` | Bares | bebidas, petiscos e opções locais | `/?q=bar` |
| `conveniencias` | Conveniências | compras rápidas e itens de conveniência | `/?q=conveni%C3%AAncia` |
| `padarias` | Padarias | pães, lanches e produtos compatíveis | `/?q=padaria` |

Jardinagem, Pet, Construção, Churrasco, datas sazonais e outros temas ficam
para fases futuras, condicionados a inventário real, auditoria e nova autorização.

## 7. Neutralidade comercial

### Regras obrigatórias

1. Um tema não contém `empresa_id`, `loja_id` ou destino direto para loja.
2. Toda empresa elegível entra pelos mesmos critérios objetivos.
3. O resultado utiliza o mecanismo e a ordenação vigentes do Marketplace.
4. O piloto não concede posição privilegiada às lojas utilizadas para teste.
5. Tema sem diversidade mínima de oferta não é publicado.
6. Conteúdo patrocinado futuro, se autorizado, será identificado e separado do resultado orgânico.
7. A Diretoria terá registro da regra que associa termos e categorias a cada tema.

### Laboratório

Mercadinho do Paulo, Bar do Paulo e Loja de Jardinagem podem fornecer inventário de teste. Eles não serão nomeados nos cards, não receberão links exclusivos e não alterarão a ordenação do Marketplace. O laboratório valida o fluxo; não valida favorecimento.

## 8. Rotatividade

A rotação é editorial e previsível, não uma animação agressiva. A versão inicial deve exibir um conjunto estável durante o período definido.

Temas possíveis:

- evergreen: Compras do dia, Pão, Jardinagem;
- sazonais: Volta às Aulas, Dia das Mães, Festa Junina, Natal;
- contextuais: Semana do Churrasco.

### Critérios para ativar um tema

- necessidade local compreensível;
- inventário real suficiente;
- ao menos duas empresas elegíveis quando houver empresas disponíveis para o tema;
- destino testado no Marketplace;
- período de validade definido;
- conteúdo legal e comercialmente permitido;
- ausência de empresa destacada pelo próprio tema.

### Critérios para desativar

- fim do período;
- ausência de resultados;
- perda da diversidade mínima;
- erro de destino;
- risco regulatório ou reputacional;
- desempenho insuficiente após janela de medição.

## 9. Modelo conceitual de configuração

Esta estrutura é especificação, não código:

| Campo | Finalidade |
| --- | --- |
| `tema` | identificador estável |
| `titulo` | chamada exibida na Home |
| `icone` | apoio visual acessível |
| `termos` | termos aceitos pelo Marketplace |
| `categorias` | categorias existentes aplicáveis |
| `inicio` / `fim` | janela editorial |
| `ativo` | controle operacional |
| `ordem` | posição entre temas, nunca entre empresas |
| `aviso` | transparência ou restrição aplicável |

Campos proibidos na primeira versão: empresa exclusiva, preço inventado, comissão oculta, segmentação pessoal, localização precisa e destino externo.

## 10. Métricas

### Funil principal

```text
Impressão da seção
    ↓
Clique em tema
    ↓
Entrada no Marketplace
    ↓
Visualização de produto ou empresa
    ↓
Ação de interesse já existente no Marketplace
```

### Indicadores

| Indicador | Definição | Fonte futura |
| --- | --- | --- |
| Impressões da vitrine | visualizações elegíveis da seção | Analytics aprovado |
| Cliques na vitrine | cliques por tema | Analytics aprovado |
| Taxa de entrada | cliques ÷ impressões | Analytics aprovado |
| Produtos visualizados | páginas de produto após clique | Analytics aprovado |
| Empresas acessadas | páginas de loja após clique | Analytics aprovado |
| Profundidade | páginas internas por sessão originada | Analytics aprovado |
| Conversão para Marketplace | sessões que entram e navegam internamente | Analytics aprovado |
| Tempo na Home | indicador secundário, não critério isolado | Analytics aprovado |

Não serão registrados nome, telefone, mensagem, posição precisa ou outro dado pessoal para medir a vitrine.

### Critério de sucesso

A missão terá sucesso quando houver aumento sustentado da proporção de visitantes que entram no Marketplace pela Home e continuam para produto ou empresa.

Antes do piloto, registrar uma linha de base. A meta numérica será definida somente depois de existirem dados válidos. Não será declarada vitória com base apenas em cliques ou tempo de permanência.

## 11. Reversão

Especificação obrigatória para futura implementação:

- feature flag sugerida: `HOME_COMPRE_PERTO_ENABLED=false`;
- valor padrão desligado;
- com a flag desligada, a Home permanece idêntica à versão anterior;
- dados do piloto não alteram produtos, empresas ou pedidos;
- implementação em um único commit funcional;
- reversão por desligamento da flag ou revert desse commit;
- nenhum processo destrutivo ou migração obrigatória.

## 12. Acessibilidade e experiência

- heading único e hierarquia coerente com as seções vizinhas;
- cards implementados como links reais para o Marketplace;
- nome do tema compreensível sem depender do emoji;
- foco visível e navegação completa por teclado;
- área de toque confortável no mobile;
- nenhuma rotação automática durante a leitura;
- nenhuma rolagem horizontal da página;
- aviso de neutralidade disponível em texto;
- estado vazio impede a publicação do tema, em vez de levar a uma página sem resultados.

## 13. Fora do escopo

- mudar busca, categorias, produtos ou ordenação do Marketplace;
- criar checkout ou carrinho na Home;
- criar páginas exclusivas para empresas do laboratório;
- alterar backend, banco ou regras de negócio nesta fase;
- publicidade paga, leilão de posição ou comissão;
- personalização por perfil ou localização precisa;
- automação de temas por IA;
- merge ou deploy.

## 14. Registro da aprovação técnica

A Diretoria aprovou em 22/07/2026:

1. nome, subtítulo e posição;
2. regras de neutralidade;
3. quatro temas habilitados na Fase 1;
4. demais temas somente em fases futuras;
5. diversidade e neutralidade por tema;
6. mecanismo de destino no Marketplace;
7. feature flag e teste de reversão;
8. protótipos desktop e mobile.
