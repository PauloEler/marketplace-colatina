# Mercado Colatina — Relatório UX Sprint 001: Home First

**Data da entrega:** 13 de julho de 2026

**Objetivo:** fazer a página inicial comunicar, nos primeiros segundos, que o Mercado Colatina é um marketplace local e aproximar os produtos da primeira dobra.

**Escopo:** reorganização da experiência da Home, sem novas funcionalidades e sem alterações em banco de dados, pedidos, estoque, rastreabilidade, reputação, Minha Loja, Perfil Público, Painel Administrativo ou regras de negócio.

## 1. Resumo executivo

A Home foi reorganizada para priorizar descoberta e compra. A sequência principal passou a apresentar busca, uma proposta de valor compacta, navegação por categorias e ofertas locais antes dos blocos institucionais, de parceiros e de monetização.

O resultado mensurado foi uma redução de **63,8% na distância até o início das ofertas no desktop** e de **69,2% no celular**. A primeira oferta começa em aproximadamente **1 tela no desktop** e **1,25 tela no celular**, superando a meta de até aproximadamente 1 tela no desktop e 2 telas no mobile. Não foi identificado transbordamento horizontal da página em desktop, tablet ou celular.

O comunicado global deixou de dominar a abertura da página: agora apresenta um resumo compacto, permite abrir o texto completo sob demanda e pode ser fechado. A escolha de fechamento permanece após recarregar a página no mesmo navegador.

## 2. O que foi alterado

### 2.1 Comunicado global compacto

- O comunicado passou de um bloco extenso para uma faixa compacta com ícone contextual, título e resumo.
- O texto completo fica recolhido e é exibido por meio do controle **“Ler comunicado”**.
- Quando aberto, o controle muda para **“Ocultar comunicado”**.
- Foi incluído o botão acessível **“Fechar comunicado”**.
- O fechamento é salvo localmente no navegador por comunicado, evitando que o mesmo aviso volte a ocupar espaço após cada recarregamento.
- Caso o armazenamento local não esteja disponível, o aviso continua funcional sem interromper a página.

**Motivo:** preservar a comunicação oficial sem adiar a descoberta de produtos.

**Impacto esperado:** menor sensação de página institucional, menos interrupção na entrada e maior controle do usuário sobre o conteúdo auxiliar.

### 2.2 Hero reduzido

- O hero foi reduzido ao conteúdo essencial: título, subtítulo, botão **“Anunciar grátis”** e botão **“Explorar ofertas”**.
- Foram removidos do hero a promoção de cadastro, o painel lateral de estatísticas e elementos decorativos que ampliavam sua altura.
- Os dois chamados principais mantêm destinos já existentes; nenhuma regra ou fluxo foi criado.

**Motivo:** explicar rapidamente a proposta do marketplace e liberar espaço vertical para as ofertas.

**Impacto esperado:** compreensão mais rápida, decisões mais claras e menor tempo até a vitrine.

### 2.3 Nova hierarquia da Home

A ordem principal ficou:

1. Cabeçalho;
2. Busca;
3. Aviso global compacto, quando houver;
4. Hero compacto;
5. Categorias;
6. Ofertas locais;
7. Lojas em destaque;
8. Como funciona;
9. Mercado Livre, identificado como parceiro;
10. Planos;
11. Rodapé.

O aviso é uma camada global e condicional, não um bloco promocional da Home. Quando dispensado, a transição visual ocorre diretamente da busca para o hero.

**Motivo:** colocar navegação e inventário local antes de conteúdo explicativo ou comercial.

**Impacto esperado:** a página passa a se comportar como vitrine de marketplace desde a primeira dobra.

### 2.4 Categorias com maior importância

- As categorias receberam contêiner próprio, título **“Explore por categoria”**, contraste maior e chips mais altos.
- O estado ativo ficou mais evidente.
- No celular, os chips quebram em várias linhas; a navegação não depende de uma faixa rolável lateral.

**Motivo:** permitir que o visitante reduza rapidamente o universo de produtos.

**Impacto esperado:** navegação mais previsível, melhor descoberta e menor esforço em telas estreitas.

### 2.5 Ofertas locais antecipadas

- A vitrine **“Ofertas perto de você”** foi movida para imediatamente depois das categorias.
- Lojas, explicação de uso, parceiro e planos passaram a ocupar posições posteriores.
- Os cards e a lógica dos anúncios não foram alterados.

**Motivo:** produtos são a principal evidência de que o sistema é um marketplace.

**Impacto esperado:** reconhecimento imediato do propósito da página e maior probabilidade de exploração de anúncios.

### 2.6 Lojas em destaque

- O bloco foi renomeado de **“Lojas que movimentam Colatina”** para **“Lojas em destaque”**.
- Foi reposicionado depois das ofertas.
- Seu conteúdo e seus destinos permaneceram inalterados.

**Motivo:** tornar o título mais direto e manter a prioridade dos produtos sem perder a valorização do comércio local.

**Impacto esperado:** melhor continuidade entre descobrir um produto e conhecer seus vendedores.

### 2.7 Mercado Livre com menor peso visual

- O parceiro continua explicitamente identificado.
- A transparência sobre redirecionamento, afiliação e possível comissão foi preservada.
- O bloco foi compactado, recebeu fundo neutro e perdeu o tratamento visual que competia com as ofertas locais.
- Foi colocado depois de **“Como funciona”** e antes dos planos.

**Motivo:** manter a parceria e a transparência sem diluir a identidade local da Home.

**Impacto esperado:** diferenciação mais clara entre inventário local e conteúdo externo.

### 2.8 Planos com prioridade reduzida

- O bloco de planos foi transferido para o fim do conteúdo principal, imediatamente antes do rodapé.
- A apresentação recebeu tratamento visual mais discreto.
- Produtos, categorias e lojas passaram a aparecer antes da monetização.

**Motivo:** monetização não é o objetivo prioritário da versão atual.

**Impacto esperado:** jornada inicial mais orientada a valor e menos orientada a venda de plano.

## 3. Comparação antes e depois

As medições foram realizadas na página inicial com a mesma massa controlada de validação, contendo três ofertas e duas lojas. Os valores são coordenadas verticais aproximadas em pixels, medidas a partir do topo do documento.

### 3.1 Desktop — 1280 × 720 px

| Indicador | Antes | Depois | Variação |
|---|---:|---:|---:|
| Altura total da Home | 3.276 px | 2.699 px | **−577 px (−17,6%)** |
| Altura do comunicado | 310 px | 86 px | **−224 px (−72,3%)** |
| Início da seção de ofertas | 1.798 px | 650 px | **−1.148 px (−63,8%)** |
| Início do primeiro card de oferta | não registrado na linha de base | 722 px | aproximadamente **1,00 tela** |

**Posição final da primeira oferta no desktop:** o título da vitrine começa em **650 px**, ainda dentro da primeira tela de 720 px; o primeiro card começa em **722 px**, praticamente na transição da primeira para a segunda tela.

### 3.2 Tablet — 768 × 1024 px

| Indicador | Depois |
|---|---:|
| Altura total da Home | 3.479 px |
| Altura do comunicado | 86 px |
| Início da seção de ofertas | 643 px |
| Início do primeiro card de oferta | 715 px |
| Transbordamento horizontal da página | Não |

No tablet, o título e o primeiro card da vitrine aparecem dentro da primeira tela.

### 3.3 Celular — 390 × 844 px

| Indicador | Antes | Depois | Variação |
|---|---:|---:|---:|
| Altura total da Home | 6.234 px | 4.920 px | **−1.314 px (−21,1%)** |
| Altura do comunicado | 412 px | 100 px | **−312 px (−75,7%)** |
| Início da seção de ofertas | 3.208 px | 987 px | **−2.221 px (−69,2%)** |
| Início do primeiro card de oferta | não registrado na linha de base | 1.059 px | aproximadamente **1,25 tela** |

**Posição final da primeira oferta no mobile:** o título da vitrine começa em **987 px** e o primeiro card em **1.059 px**. Ambos ficam confortavelmente antes do limite de duas telas, equivalente a 1.688 px nessa resolução.

O pequeno aumento de altura em relação à primeira versão da Sprint é intencional: as categorias passaram a quebrar em linhas no celular para eliminar a necessidade de rolagem lateral. Mesmo com todos os atalhos visíveis, a primeira oferta permanece muito antes da meta de duas telas.

## 4. Responsividade e validação visual

Foram validados três tamanhos representativos:

- **Desktop:** 1280 × 720 px;
- **Tablet:** 768 × 1024 px;
- **Celular:** 390 × 844 px.

Resultados:

- não houve rolagem horizontal da página nas três resoluções;
- os botões do hero permaneceram legíveis e acionáveis;
- o comunicado preservou título, resumo, expansão e fechamento;
- categorias ficaram acessíveis sem deslocamento lateral no celular;
- ofertas permaneceram antes dos blocos institucionais, do parceiro e dos planos;
- Mercado Livre permaneceu identificado como parceiro e com aviso de afiliação;
- a hierarquia visual ficou consistente entre desktop, tablet e celular.

## 5. Testes e critérios de aceitação

A suíte automatizada foi ajustada para validar a nova apresentação sem alterar as regras existentes. Foram incluídas verificações para:

- ordem Home First dos blocos;
- conteúdo essencial do hero compacto;
- ausência dos antigos elementos de destaque do hero;
- comunicado compacto, expansível e fechável;
- texto e posicionamento conceitual do parceiro Mercado Livre;
- novo título de lojas em destaque.

Também foi realizada validação interativa do comunicado:

1. **“Ler comunicado”** abriu o texto completo;
2. o rótulo passou para **“Ocultar comunicado”**;
3. **“Fechar comunicado”** removeu visualmente o bloco;
4. após recarregar a página, o comunicado permaneceu fechado.

**Suíte completa:** `python -m unittest discover -s tests -v`

**Total:** 80 testes

**Resultado:** todos aprovados, sem regressões detectadas.

## 6. Arquivos da Sprint

- `templates/index.html` — nova ordem e nova hierarquia da Home;
- `templates/base.html` — estrutura compacta do comunicado global;
- `static/styles.css` — estilos, prioridades visuais e responsividade;
- `static/announcement.js` — expansão nativa complementada pelo fechamento persistente do comunicado;
- `tests/test_moderacao.py` — atualização e ampliação das verificações da Home;
- `RELATORIO_UX_SPRINT_001_HOME.md` — documentação desta entrega.

## 7. Garantias de escopo

- Nenhuma tabela foi criada.
- Nenhuma migração ou alteração de banco de dados foi realizada.
- Nenhuma regra de pedido, estoque, rastreabilidade ou reputação foi alterada.
- Minha Loja, Perfil Público e Painel Administrativo não foram modificados.
- Nenhum fluxo de anúncio ou regra de negócio foi criado ou alterado.
- A validação visual utilizou uma base temporária isolada, removida ao término da inspeção.
- A entrega não foi publicada automaticamente.

## 8. Impacto esperado na experiência

O visitante agora encontra, em sequência curta, a proposta local, os caminhos de navegação e o inventário disponível. Isso reduz o tempo necessário para compreender o produto, elimina a impressão inicial de página institucional e coloca o conteúdo transacional acima dos blocos de explicação, parceria e monetização.

Em termos práticos, a mudança desloca a Home de uma apresentação sobre o Mercado Colatina para uma experiência de uso do Mercado Colatina.
