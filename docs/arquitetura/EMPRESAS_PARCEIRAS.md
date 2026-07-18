# Empresas Parceiras

## Objetivo

Definir a arquitetura institucional da área de confiança e de empresas parceiras do Mercado Colatina sem misturá-la aos anúncios, às lojas ou às ofertas de afiliados.

## Motivação

A Home precisa comunicar que a plataforma foi criada em Colatina, prioriza o comércio local e identifica relações comerciais com transparência. Ao mesmo tempo, deve permitir uma futura fonte de receita com empresas da cidade sem prejudicar a experiência principal de compra e venda.

## Arquitetura

A implementação usa configuração estática e centralizada em `local_partners.py`. Não há tabela, migração, nova regra de negócio ou integração externa.

`LOCAL_PARTNERS_HOME` contém os seis espaços institucionais. Cada item possui identificador, nome, categoria, slogan, nível, iniciais de logotipo, URL e o marcador explícito de placeholder.

`PARTNER_LEVELS` registra os três níveis preparados:

- `local`: Parceiro Local;
- `destaque`: Parceiro Destaque;
- `premium`: Parceiro Premium.

Os níveis são metadados de apresentação e evolução. Não representam planos ativos, preços, prioridade contratada ou benefícios comerciais vigentes.

## Componentes

### Confiança

Seção institucional com cinco compromissos: origem em Colatina, prioridade ao comércio local, negociação direta, transparência publicitária e evolução contínua. Os ícones são SVG embutidos, discretos e decorativos.

### Empresas Parceiras

Grade responsiva com seis cards de placeholder. Cada card está preparado para logotipo, nome, categoria, slogan, nível e botão “Conhecer”. O texto “Espaço reservado” impede a interpretação de que já existe uma empresa patrocinadora.

### Páginas institucionais

As rotas `/quem-somos` e `/seja-parceiro` reutilizam o template institucional existente. A segunda informa expressamente que o programa está em preparação e que ainda não há regras comerciais ativas.

### Rodapé

O rodapé da Home e o rodapé geral passam a oferecer os acessos Quem Somos, Seja Parceiro, Segurança, Como Funciona, Política de Privacidade e Termos de Uso.

## Responsividade e acessibilidade

- desktop e notebook: três cards por linha;
- tablet: dois cards por linha;
- mobile: um card por linha;
- ícones decorativos não geram ruído para leitores de tela;
- logotipos temporários têm descrição acessível;
- botões possuem foco visível e área mínima de toque;
- não há animação automática, pop-up ou banner intermitente.

## Impacto esperado

O visitante recebe sinais claros de origem, propósito e transparência. Empresas locais passam a visualizar uma possibilidade futura de participação, enquanto produtos, lojas e ofertas continuam aparecendo antes da área institucional.

## Limitações

Não existem empresas reais cadastradas, contratação, preços, gestão administrativa, métricas próprias, ordenação comercial ou publicação dinâmica.

## Evolução futura

Após aprovação comercial e jurídica, a configuração poderá receber parceiros reais ou migrar para uma fonte administrável. Essa evolução deverá definir critérios, benefícios, período de exibição, aprovação de identidade visual e indicadores, preservando a identificação publicitária.
