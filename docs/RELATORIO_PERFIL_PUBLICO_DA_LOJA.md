# Relatório — Perfil Público Profissional das Lojas

## Resumo técnico

A página pública existente das lojas foi evoluída sem reconstrução. A rota canônica continua no formato `/loja/<id>-<slug>`, preservando todos os endereços já publicados e redirecionando slugs antigos para o endereço atual.

A evolução concentra apresentação comercial, descoberta de produtos e confiança. Nenhuma regra de pedido, estoque, rastreabilidade, painel ou reputação foi modificada.

## Experiência pública

A página apresenta:

- nome e descrição da loja;
- bairro comercial e município;
- data de entrada no marketplace;
- quantidade de anúncios ativos;
- vendas e produtos vendidos;
- visualizações acumuladas dos anúncios ativos;
- taxa pública de conclusão;
- selo de loja verificada, quando aplicável;
- WhatsApp comercial, quando configurado;
- compartilhamento nativo ou cópia do endereço da loja.

O cabeçalho possui uma área visual própria para futura foto de capa e um avatar por iniciais preparado para futuro upload. Nesta versão não são usadas imagens genéricas ou repetidas.

## Catálogo e descoberta

Os anúncios públicos continuam restritos a itens ativos e com estoque disponível. A página faz uma única consulta do catálogo e reutiliza o resultado para métricas, categorias, filtros e ordenação.

Foram adicionados:

- busca por título e descrição, sem diferenciar acentos ou letras maiúsculas;
- filtro por categoria disponível na própria loja;
- preço mínimo e preço máximo;
- ordenação por mais recentes;
- ordenação por mais vistos;
- ordenação por menor preço;
- ordenação por maior preço;
- indicação da quantidade filtrada em relação ao catálogo completo;
- estado vazio específico para buscas sem resultado;
- contagem de visualizações em cada cartão.

## Privacidade e segurança

A página não expõe:

- CPF;
- e-mail;
- telefone pessoal;
- último acesso;
- endereço completo;
- pedidos;
- cancelamentos;
- casos em análise;
- informações administrativas ou internas.

Somente o WhatsApp comercial configurado no perfil da loja pode aparecer publicamente. Entradas de busca e filtros possuem limites, validação e escape automático na renderização.

## SEO e compartilhamento

Foram preservados:

- título exclusivo por loja;
- meta description baseada na descrição comercial;
- URL canônica amigável;
- Open Graph com título, descrição, URL e imagem institucional;
- metadados para compartilhamento;
- inclusão no sitemap quando a loja possui anúncio público.

## Responsividade

O layout foi preparado para desktop, tablet e celular:

- grades adaptáveis de indicadores e produtos;
- filtros reorganizados conforme a largura disponível;
- botões em largura total no celular;
- textos longos com quebra segura;
- cartões sem largura mínima que provoque rolagem horizontal;
- catálogo em uma coluna nas telas menores.

## Banco de dados e migração

Nenhuma migração foi criada ou executada.

- Nenhuma tabela ou coluna foi adicionada.
- Nenhum registro existente foi alterado.
- As visualizações usam o campo já existente nos anúncios.
- A reputação continua sendo calculada pelas regras já existentes.

## Preservação de escopo

Não foram alterados:

- pedidos;
- estoque;
- dupla confirmação;
- rastreabilidade;
- painel administrativo;
- painel interno do vendedor;
- sistema de reputação.

## Arquivos alterados

- `app.py`
- `templates/loja_publica.html`
- `static/styles.css`
- `tests/test_moderacao.py`
- `docs/RELATORIO_PERFIL_PUBLICO_DA_LOJA.md`

## Testes

Foram mantidos os testes anteriores de rota pública, slug, redirecionamento canônico, privacidade, compartilhamento, SEO, loja inexistente, catálogo e responsividade.

Foi acrescentada cobertura para:

- busca dentro da loja;
- filtro por categoria;
- faixa de preço;
- ordenação por visualizações;
- ordenação crescente e decrescente de preço;
- exclusão permanente de anúncios pausados nos resultados;
- total de visualizações da loja.

Resultado final: **70 testes aprovados de 70**.

## Sugestões futuras

- upload opcional de capa e avatar pela própria loja;
- paginação do catálogo quando lojas passarem a ter grande volume;
- categorias em destaque configuráveis pela loja;
- URL baseada somente em slug após uma estratégia segura de unicidade e histórico de redirecionamentos.
