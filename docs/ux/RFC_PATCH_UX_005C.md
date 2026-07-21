# RFC — PATCH UX-005C: Primeira dobra orientada à ação

## Problema real

Na Home em produção, o Hero ocupa quase toda a primeira dobra no desktop. A busca aparece tarde na composição visual e o caminho **Encontre Quem Resolve** depende principalmente de um botão flutuante. Isso aumenta o esforço para o morador identificar rapidamente como comprar, anunciar ou pedir ajuda local.

## Problema da cidade resolvido

Reduzir o tempo necessário para uma pessoa de Colatina encontrar o caminho adequado para comprar, vender ou resolver uma necessidade local.

## Público afetado

- moradores buscando produtos ou serviços;
- pessoas que desejam anunciar;
- visitantes que ainda não conhecem as possibilidades da plataforma.

## Objetivo

Aumentar a taxa de interação na primeira dobra da Home por meio de hierarquia clara, linguagem direta e ações reconhecíveis.

## Escopo

- Hero;
- busca;
- faixa **Encontre Quem Resolve**;
- categorias;
- botões principais.

## Proposta

1. Compactar o Hero sem trocar sua imagem ou identidade.
2. Explicitar no texto os três caminhos principais: comprar, vender e resolver uma necessidade.
3. Tornar a busca mais direta, com exemplo local e CTA orientado ao resultado.
4. Inserir uma faixa dedicada ao fluxo **Encontre Quem Resolve** imediatamente após o Hero.
5. Melhorar foco, hover e exploração das categorias; no celular, usar uma faixa horizontal com alvos de toque preservados.

## Fora do escopo

Produtos, pedidos, empresas, dashboards, backend, banco de dados, regras de negócio e instrumentação analítica.

## Indicador

Indicador primário: percentual de participantes que identifica e inicia um dos três caminhos principais em até cinco segundos.

- Fonte: teste de usabilidade controlado da Home.
- Meta inicial: pelo menos 80% de sucesso.
- Avaliação: após publicação autorizada, em cinco sessões desktop/mobile.

A taxa real de clique ainda não pode ser calculada sem instrumentação específica. Este patch não cria essa instrumentação por respeitar a restrição de backend.

## Critérios de aceite

- busca e CTAs principais visíveis e compreensíveis;
- faixa **Encontre Quem Resolve** acessível por teclado;
- categorias utilizáveis em desktop e mobile;
- sem overflow em 390 px e 320 px;
- produtos e módulos restritos sem alteração;
- testes e lint aprovados;
- sem merge e sem deploy antes da aprovação.
