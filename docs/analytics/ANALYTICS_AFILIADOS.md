# Analytics de Afiliados

## Objetivo

Medir o uso real da seção **Ofertas de Parceiros** sem coletar dados pessoais. A camada registra impressões e cliques para produzir totais, ranking e CTR por categoria.

## Eventos registrados

| Campo | Exemplo | Origem |
|---|---|---|
| `parceiro` | `mercado_livre` | Configuração oficial do servidor |
| `oferta_id` | `celulares-acessorios` | Identificador validado no servidor |
| `categoria` | `Celulares e acessórios` | Configuração oficial do servidor |
| `tipo_evento` | `click` ou `impression` | Navegador, com lista permitida |
| `origem` | `home` | Valor fixado pelo servidor |
| `dispositivo` | `desktop` ou `mobile` | Largura da tela no momento do evento |
| `ocorrido_em` | data/hora UTC | Banco existente |

Não são registrados IP, nome, usuário, telefone, e-mail, URL visitada após o clique ou conteúdo da sessão.

## Fluxo

1. A Home fornece ao script o endpoint e um token CSRF da sessão.
2. `IntersectionObserver` registra uma impressão quando pelo menos 50% do card entra na área visível. Cada card gera no máximo uma impressão por carregamento de página.
3. O clique no link do card registra um evento único do DOM. Cliques posteriores são preservados como novas interações.
4. O navegador usa `sendBeacon`; se indisponível, usa `fetch` com `keepalive`.
5. O servidor ignora parceiro, categoria e origem enviados pelo cliente e deriva esses valores da configuração centralizada.
6. O painel administrativo agrega os eventos em tempo de leitura.

## Dashboard

Rota: `/admin?visao=afiliados`.

O acesso exige sessão administrativa e apresenta:

- cliques no dia atual de Colatina;
- cliques nos últimos 7 e 30 dias;
- ranking das seis categorias;
- CTR por categoria (`cliques / impressões × 100`);
- categoria com maior e menor interesse.

## Persistência

A tabela `afiliado_eventos` é criada no banco já utilizado pela aplicação, tanto em SQLite quanto em PostgreSQL. Os índices cobrem consultas por período e por oferta. Não foi criado um novo banco nem alterado o significado das tabelas existentes.

## Inclusão de novos parceiros

Cada oferta possui o campo `parceiro`. Amazon, Magalu, Shopee ou outro parceiro pode usar o mesmo evento e o mesmo dashboard ao adicionar ofertas à configuração centralizada. A camada de analytics não depende do formato da URL do afiliado.

## Limitações

- bloqueadores de JavaScript podem impedir o registro;
- os dados começam a existir somente após a publicação desta Sprint;
- cliques repetidos são contados; por isso o CTR de interação pode superar 100% em situações de múltiplos cliques sobre uma impressão;
- o painel não confirma comissão, venda ou receita no sistema do parceiro;
- não há identificação de visitante único, deliberadamente, para preservar privacidade.
