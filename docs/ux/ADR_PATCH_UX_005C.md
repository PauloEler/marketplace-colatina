# ADR — PATCH UX-005C: Hierarquia da primeira dobra

**Status:** aceita para implementação

## Contexto

A primeira dobra da Home concentra marca e imagem da cidade, mas distribui os caminhos de ação de forma desigual. O objetivo do patch exige maior clareza sem redesenhar a Home nem modificar módulos operacionais.

## Decisão

Adotar uma primeira dobra com três níveis:

1. promessa local e CTAs **Comprar agora** e **Anunciar grátis/Publicar anúncio**;
2. busca destacada com linguagem de intenção;
3. faixa própria **Encontre Quem Resolve**, antes da prova de visitas e das categorias.

O Hero será compactado somente por CSS. A fotografia e seu crédito permanecem no desktop. Em telas até 960 px, a fotografia será omitida para priorizar texto, botões, busca e a faixa de serviços. Em celulares, as categorias usarão navegação horizontal para manter alvos legíveis sem alongar a primeira interação.

Quando a faixa **Encontre Quem Resolve** estiver presente, o atalho flutuante equivalente será ocultado para evitar duplicação e sobreposição. Nas demais páginas e nos resultados filtrados, o atalho continua disponível.

## Alternativas rejeitadas

- remover a fotografia no desktop: enfraqueceria a identidade local;
- inserir o fluxo de serviços dentro da busca: misturaria duas jornadas distintas;
- criar novo endpoint ou analytics: violaria o escopo sem backend;
- alterar cards de produtos: fora do escopo aprovado.

## Consequências

### Positivas

- ações principais aparecem mais cedo;
- linguagem reduz ambiguidade;
- o fluxo de serviços ganha presença sem competir com o marketplace;
- solução permanece reversível e restrita à Home.

### Limitações

- o ganho de cliques depende de medição futura;
- a faixa de categorias no celular exige gesto horizontal;
- nenhuma regra de negócio é alterada.
