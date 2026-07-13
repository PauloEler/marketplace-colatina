# RELATÓRIO MX-002 — HOME PREMIUM

## 1. Resumo executivo

A MX-002 reconstruiu a experiência visual da Home do Mercado Colatina sem alterar banco de dados, regras de negócio, autenticação, pedidos, estoque, reputação, permissões, APIs ou rotas.

A página passou a apresentar uma jornada única e facilmente escaneável: identidade local, busca protagonista, caminhos de compra e publicação, categorias visuais, produtos em destaque, chamada ao vendedor, lojas locais, orientação de uso, parceiro identificado e rodapé institucional.

A nova Home aplica o Mercado Design System (MDS) de forma consistente, adota a identidade provisória v0.9 em formato SVG e foi validada em 320 px, 360 px, 390 px, 768 px, 1024 px e 1440 px. Os 84 testes automatizados foram aprovados, sem regressões.

## 2. Diagnóstico inicial

Antes da Sprint, a Home era funcional e já priorizava as ofertas locais, mas sua apresentação ainda tinha características de uma implementação intermediária:

- a busca estava visualmente separada do Hero;
- o Hero comunicava a proposta do produto, mas não consolidava marca, busca e ações principais;
- as categorias funcionavam como chips, com pouco peso visual;
- os cards de produto tinham fotografia, preço e ação com hierarquia tímida;
- a chamada para novos vendedores estava diluída em blocos de planos;
- o rodapé reunia links, mas não os organizava por intenção;
- a identidade visual não possuía uma assinatura de marca aplicada à experiência principal;
- a experiência era correta, porém ainda não transmitia, nos primeiros segundos, o nível de acabamento esperado de uma empresa de tecnologia.

## 3. Direção de experiência

A reconstrução foi orientada por cinco princípios:

1. **Confiança:** marca local visível, linguagem direta, informações essenciais e componentes previsíveis.
2. **Simplicidade:** uma ação dominante por contexto e redução de blocos concorrentes.
3. **Tecnologia:** acabamento limpo, grid consistente, estados visuais e comportamento responsivo.
4. **Organização:** seções com função clara e progressão natural da descoberta à negociação.
5. **Orgulho da cidade:** presença explícita de Colatina na marca, no texto, na localização e na proposta de valor.

## 4. Melhorias implementadas

### 4.1 Identidade provisória v0.9

- criada uma assinatura vetorial própria para o Mercado Colatina;
- monograma “MC” combinado com referências ao rio, à ponte e à paisagem de Colatina;
- cores baseadas nos tokens oficiais verde e azul do MDS;
- versão horizontal aplicada no cabeçalho, Hero e rodapé;
- arquivo SVG leve, escalável e nítido em telas de alta densidade;
- texto alternativo aplicado quando a marca tem função informativa e ocultado quando sua repetição seria redundante.

A marca permanece identificada como provisória v0.9. A aprovação e normalização definitiva de versões reduzida, monocromática e negativa devem ocorrer em uma futura etapa específica de identidade, sem bloquear esta Sprint.

### 4.2 Hero premium

- marca, mensagem principal, busca e caminhos de ação foram consolidados em um único bloco;
- título principal reduzido a uma proposta direta: “Compre e venda perto de você.”;
- “Praça Digital de Colatina” passou a contextualizar imediatamente a natureza local do produto;
- ações “Comprar em Colatina” e “Anunciar grátis/Publicar anúncio” permanecem claras e condicionadas ao estado de autenticação já existente;
- diferenciais de ofertas locais, contato direto e negociação organizada passaram a funcionar como sinais rápidos de confiança;
- em telas de resultados, o Hero assume uma versão contextual sem introduzir lógica nova.

### 4.3 Busca protagonista

- a busca passou a ocupar a área central do Hero;
- campo de texto, categoria e botão foram agrupados em um único componente visual;
- contraste, rótulos persistentes e ícone de apoio melhoram reconhecimento e acessibilidade;
- controles possuem 48 px de altura, acima do mínimo de toque do MDS;
- o comportamento, os parâmetros e a rota originais foram integralmente preservados.

### 4.4 Categorias em cards

- os chips anteriores foram transformados em cards modernos;
- cada categoria recebeu um ícone consistente no padrão linear adotado pelo MDS;
- estados normal, hover, foco e selecionado utilizam tokens oficiais;
- o grid adapta-se de cinco colunas no desktop para três no tablet e duas no celular;
- textos longos permanecem legíveis sem causar rolagem horizontal.

### 4.5 Cards de produtos premium

- fotografias ganharam proporção 4:3 e maior presença visual;
- preço ganhou prioridade dentro do conteúdo do card;
- disponibilidade passou a aparecer como indicador compacto e claro;
- título, localização e loja foram reorganizados para leitura sequencial;
- a indicação “Ver produto” tornou o destino do card explícito;
- o acesso à loja permanece como ação secundária separada;
- o estado sem foto foi refinado sem inventar imagem ou alterar dados do anúncio;
- a grade utiliza quatro colunas em 1440 px, três em 1024 px, duas em tablet e uma em celular.

### 4.6 Chamada ao vendedor

- os planos deixaram de competir visualmente com a jornada principal;
- foi criada uma chamada editorial de alto contraste para incentivar novos anúncios;
- benefícios objetivos informam limite gratuito, contato e presença na vitrine;
- o destino do CTA respeita a sessão existente: cadastro para visitante e criação de anúncio para usuário autenticado;
- nenhuma regra de plano ou limite foi modificada.

### 4.7 Lojas, orientação e parceiro

- lojas em destaque foram preservadas e receberam contexto editorial mais claro;
- “Como funciona” foi reescrito como uma jornada de descoberta, avaliação e negociação;
- o bloco do Mercado Livre foi mantido, claramente identificado como parceiro e visualmente subordinado às ofertas locais;
- todos os destinos e dados existentes foram preservados.

### 4.8 Rodapé institucional

- o rodapé da Home foi completamente reorganizado;
- links foram agrupados por intenção: Comprar, Vender e Institucional;
- a marca e a proposta local ganharam uma área própria;
- todos os links possuem áreas de toque adequadas no celular;
- páginas internas continuam usando o rodapé anterior, evitando alteração fora do escopo da Home.

## 5. Comparação antes e depois

As medidas abaixo foram coletadas no navegador com o mesmo conteúdo local e representam a posição vertical em relação ao início do documento.

| Indicador | Antes — desktop 1440 × 900 | Depois — desktop 1440 × 900 | Antes — mobile 390 × 844 | Depois — mobile 390 × 844 |
|---|---:|---:|---:|---:|
| Altura total da página | 2.894 px | 3.579 px | 5.601 px | 6.657 px |
| Altura do Hero | 206 px | 463 px | 228 px | 746 px |
| Início da primeira vitrine | 645 px | 900 px | 760 px | 1.559 px |
| Rolagem horizontal | Não | Não | Não | Não |

### Interpretação

O aumento de altura é intencional e decorre de quatro mudanças de qualidade: Hero completo com busca protagonista, categorias transformadas em cards, produtos com imagens maiores e rodapé institucional expandido. A densidade visual dentro de cada tela foi reduzida, embora o documento completo tenha ficado mais longo.

A primeira vitrine permanece dentro de aproximadamente uma tela no desktop e de duas telas no celular. Em 320 px, o início ocorre em 1.680 px, ainda dentro de duas telas de 844 px. Isso equilibra a necessidade de comunicar marca e navegação com o acesso rápido aos produtos.

## 6. Validação responsiva

| Largura solicitada | Categorias | Produtos | Menor controle principal | Rolagem horizontal | Resultado |
|---:|---:|---:|---:|---|---|
| 320 px | 2 colunas | 1 coluna | 48 px | Não | Aprovado |
| 360 px | 2 colunas | 1 coluna | 48 px | Não | Aprovado |
| 390 px | 2 colunas | 1 coluna | 48 px | Não | Aprovado |
| 768 px | 3 colunas | 2 colunas | 48 px | Não | Aprovado |
| 1024 px | 5 colunas | 3 colunas | 48 px | Não | Aprovado |
| 1440 px | 5 colunas | 4 colunas | 48 px | Não | Aprovado |

Também foram validados:

- carregamento correto da marca SVG;
- apenas um H1 em cada estado da Home;
- busca com resultado e preservação dos parâmetros existentes;
- menu móvel funcional;
- destinos corretos de compra, anúncio e categoria;
- textos de localização e loja visíveis nos cards mobile;
- ausência de erros no console do navegador;
- ausência de conteúdo cortado ou extrapolação lateral.

## 7. Aderência ao Mercado Design System

- paleta construída com tokens MDS;
- tipografia e hierarquia oficial preservadas;
- espaçamentos baseados na escala 8, 16, 24, 32, 48 e 64;
- containers e gutters coerentes com desktop, tablet e celular;
- controles principais com altura de 48 px;
- foco visível herdado e preservado em links, botões e campos;
- ícones lineares consistentes, sem mistura de bibliotecas visuais;
- sombras, bordas e raios baseados em tokens;
- estados hover, active, disabled e focus preservados pelos componentes;
- conteúdo e navegação sem dependência de cor isolada;
- preferência por movimento reduzido respeitada;
- estrutura semântica com `header`, `main`, `section`, `nav`, `article` e `footer`;
- rótulos de busca, nomes acessíveis e ícones decorativos ocultados de leitores de tela.

## 8. Testes executados

### Testes automatizados

- comando: `python -m unittest discover -s tests -v`;
- resultado: **84/84 testes aprovados**;
- regressões: **nenhuma**.

Foi incluído um novo teste de contrato para confirmar identidade v0.9, quantidade de categorias, chamada ao vendedor e agrupamentos do rodapé. Os testes anteriores da Home foram atualizados somente para refletir a nova apresentação, mantendo a verificação dos mesmos destinos e comportamentos.

### Qualidade estática

- Ruff: aprovado;
- verificação de formatação: aprovada;
- verificação de espaços e conflitos no diff: aprovada.

### Validação no navegador

- seis larguras obrigatórias aprovadas;
- busca principal aprovada;
- menu móvel aprovado;
- links primários aprovados;
- console sem erros;
- nenhum overflow horizontal.

O CI remoto será executado automaticamente pela Pull Request em modo Draft. Nenhum deploy faz parte desta Sprint antes da auditoria.

## 9. Arquivos da Sprint

- `RELATORIO_MX_002_HOME_PREMIUM.md` — relatório único da Sprint;
- `static/mercado-colatina-logo-v0.9.svg` — identidade provisória vetorial;
- `static/styles.css` — estilos da Home Premium, isolados pelo escopo `.mx-home-premium`;
- `templates/base.html` — ponto de extensão visual para marca e rodapé específico da Home;
- `templates/index.html` — nova composição da Home;
- `tests/test_moderacao.py` — atualização e ampliação dos testes de contrato da Home.

## 10. Confirmações de escopo

Confirma-se explicitamente que a MX-002:

- não alterou banco de dados;
- não alterou migrations;
- não alterou models;
- não alterou pedidos;
- não alterou estoque;
- não alterou autenticação;
- não alterou permissões;
- não alterou reputação;
- não alterou APIs;
- não alterou rotas;
- não alterou regras de negócio;
- não adicionou funcionalidade nova;
- não disparou deploy.

O arquivo local `RELATORIO_AUDITORIA_UX_MERCADO_COLATINA.md` não pertence à Sprint e deve permanecer fora do commit e da Pull Request.

## 11. Riscos controlados e próximos passos

### Riscos controlados

- estilos novos isolados na classe da Home, reduzindo impacto nas demais telas;
- rodapé premium aplicado por bloco de template, mantendo páginas internas inalteradas;
- identidade fornecida em SVG local, sem dependência externa;
- rotas e parâmetros existentes reutilizados integralmente;
- resposta mobile validada em navegador real nas seis larguras de aceite.

### Recomendações futuras

1. realizar uma Sprint própria de identidade para aprovar a marca v1.0 e suas variantes oficiais;
2. medir busca, cliques em produtos e conversão de publicação depois da liberação em produção;
3. avaliar, com dados reais, a ordem das categorias mais utilizadas;
4. otimizar imagens de anúncios com formatos responsivos em uma Sprint técnica específica;
5. conduzir teste moderado com usuários de Colatina sem modificar esta entrega antes da auditoria.

## 12. Conclusão

A Home agora comunica, nos primeiros segundos, que o Mercado Colatina é uma praça digital local organizada e confiável. Busca, compra e publicação estão claras; categorias e produtos ganharam apresentação profissional; a experiência mobile é coerente; e a identidade da cidade passou a fazer parte da interface sem comprometer o MDS ou as regras existentes.

A MX-002 está tecnicamente preparada para revisão por Pull Request em modo Draft, sem merge e sem deploy antes da aprovação.
