# Hoje em Colatina — Arquitetura

## Objetivo

Definir um painel diário compacto para que o visitante reconheça, em poucos segundos, as principais categorias de informação útil da cidade.

## Motivação

O Mercado Colatina já conecta produtos, lojas, parceiros e pessoas. O painel “Hoje em Colatina” prepara a evolução da Home para informações locais sem deslocar o marketplace de sua posição principal e sem publicar dados não verificados.

## Arquitetura

Os cards são definidos em `daily_city.py`, na constante imutável `DAILY_CITY_CARDS`. Cada registro possui:

- identificador estável;
- título;
- resumo curto;
- chave do ícone;
- indicador explícito de placeholder.

O `app.py` envia a estrutura ao template da Home. O template cria os cards por repetição, permitindo adicionar fonte, estado e ação em uma sprint futura sem duplicar marcação.

## Componentes

### Cabeçalho do painel

Apresenta o título “Hoje em Colatina”, uma explicação curta e o estado “Conteúdos locais em preparação”.

### Cards

Cinco cards representam Tempo, Eventos, Empregos, Farmácia de Plantão e Avisos. Todos exibem “Em preparação” e uma frase curta. Nenhum card afirma conter informação diária real.

### Ícones

Os ícones são SVG embutidos, decorativos e leves. Não exigem biblioteca ou requisição externa.

## Posição na Home

O painel aparece após “Empresas Parceiras” e antes de “Como Funciona”. Assim, produtos, ofertas, vendedores, lojas e confiança continuam precedendo o novo conteúdo local.

## Responsividade

- desktop e notebook: cinco cards por linha;
- tablet: três cards por linha;
- mobile: dois cards por linha, com Avisos ocupando a largura completa;
- telas até 359 px: um card por linha;
- nenhuma rolagem horizontal da página.

## Acessibilidade

- título associado à seção por `aria-labelledby`;
- ordem semântica consistente;
- ícones decorativos ocultos de leitores de tela;
- textos curtos, contraste e hierarquia visual;
- nenhuma animação, atualização automática ou mudança inesperada.

## Limitações

Não há APIs, banco, atualização automática, links, geolocalização, coleta de dados ou informações operacionais reais.

## Evolução futura

Cada categoria poderá receber um provedor próprio e um contrato de dados verificável. A ativação deve prever fonte, horário de atualização, validade, estado de indisponibilidade, responsabilidade editorial e cache, sem alterar o componente visual comum.
