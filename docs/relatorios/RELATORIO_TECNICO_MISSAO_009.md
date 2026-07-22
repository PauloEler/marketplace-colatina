# Relatório técnico — Missão 009: Compre Perto de Você

## Resultado

A Fase 1 foi implementada de forma reversível. A Home apresenta quatro temas e
cada card abre a listagem já existente do Marketplace por meio do parâmetro
`q`. Não foram criadas rotas, páginas paralelas, catálogo, tabela, migração ou
regra de ordenação.

## Problema real atendido

O morador pode iniciar a navegação por uma necessidade cotidiana, sem precisar
traduzir primeiro essa necessidade para a taxonomia interna do Marketplace.

## Arquitetura

- `home_nearby.py` concentra os quatro temas, textos, termos e ícones;
- `HOME_COMPRE_PERTO_ENABLED=false` é o padrão;
- a rota existente apenas fornece a configuração ao template quando a Home não
  possui busca, categoria ou `todos=1`;
- `templates/index.html` renderiza links reais para a listagem atual;
- o CSS pertence somente ao novo componente;
- a ordem visual `27` mantém a seção depois de Cidade Viva (`25`) e antes de
  Produtos em destaque (`40`) na Home compacta.

## Matriz de destinos

| Tema | Destino no Marketplace |
| --- | --- |
| Mercadinhos | `/?q=mercadinho` |
| Bares | `/?q=bar` |
| Conveniências | `/?q=conveni%C3%AAncia` |
| Padarias | `/?q=padaria` |

Nenhum tema contém `empresa_id`, `loja_id`, link de loja ou link de anúncio.
A ordenação continua sendo a do Marketplace.

## Arquivos da implementação

- `.env.example`;
- `app.py`;
- `home_nearby.py`;
- `render.yaml`;
- `static/styles.css`;
- `templates/index.html`;
- `tests/test_moderacao.py`;
- documentação e evidências desta missão.

## Validação automatizada

- 169 testes aprovados;
- 33 subtestes aprovados;
- quatro testes específicos da Missão 009;
- Ruff check aprovado;
- Ruff format check aprovado após formatação;
- `git diff --check` aprovado.

Os testes cobrem flag desligada, quatro temas, URLs únicas, neutralidade,
posição, ocultamento em resultados filtrados, breakpoints e reversão.

## Validação responsiva

| Largura | Composição | Overflow | CTA |
| --- | --- | --- | --- |
| 1440 px | 4 cards em uma linha | não | 44 px |
| 1024 px | 4 cards em uma linha | não | 44 px |
| 768 px | 2 × 2 cards | não | 44 px |
| 390 px | 1 card por linha | não | 44 px |
| 320 px | 1 card por linha | não | 44 px |

O teste por teclado transferiu foco de Mercadinhos para Bares e confirmou o
contorno visível. O clique controlado em Padarias abriu `/?q=padaria`, mostrou
"Resultados da busca" e ocultou a vitrine na página filtrada. O console da
aplicação foi validado sem erros no navegador isolado.

## Reversão

Com `HOME_COMPRE_PERTO_ENABLED=false`, o markup da vitrine não é renderizado.
Hero, Busca, Encontre Quem Resolve, Cidade Viva e Produtos permanecem presentes.
Não existe dado a remover. A reversão definitiva também pode ser feita pelo
revert do único commit funcional.

## Limitações e próximos passos

- os termos usam o filtro atual, que pesquisa título, descrição e bairro dos
  anúncios; nenhuma regra de busca foi ampliada nesta missão;
- eventos adicionais de Analytics não foram criados nesta fase para respeitar o
  escopo sem alteração de backend;
- temas futuros dependem de inventário real, auditoria e nova autorização.

## Situação de publicação

- PR: Draft;
- merge: não realizado;
- deploy: não realizado;
- flag: desligada por padrão;
- próxima etapa: auditoria visual da Diretoria.
