# Relatório — Perfil Público da Loja

## Resumo técnico

Foi criada uma página pública profissional para cada vendedor ativo do Mercado Colatina. A página apresenta a identidade da loja, descrição, bairro, indicadores públicos de reputação, contato comercial e todos os anúncios ativos disponíveis, ordenados dos mais recentes para os mais antigos.

A URL canônica usa o formato:

```text
/loja/<id>-<slug>
```

Exemplo:

```text
/loja/12-pedal-colatina
```

O identificador garante unicidade e estabilidade. O slug torna o endereço legível e é normalizado sem acentos. Acesso somente pelo identificador e slugs antigos ou incorretos são redirecionados permanentemente para a URL canônica atual.

## Conteúdo público

- nome da loja, com o nome do vendedor como alternativa quando a loja ainda não foi nomeada;
- logo padrão por iniciais;
- descrição e bairro comercial;
- membro desde;
- anúncios ativos;
- vendas concluídas;
- produtos vendidos;
- taxa de conclusão;
- selo de loja verificada somente quando ativo;
- botão de WhatsApp comercial;
- botão de compartilhamento.

## Privacidade e segurança

A página consulta somente o vendedor ativo e seus anúncios públicos com estoque disponível.

Não são exibidos:

- telefone pessoal;
- último acesso;
- pedidos;
- cancelamentos;
- situações em análise;
- dados administrativos;
- endereço detalhado;
- informações internas da conta.

O botão de WhatsApp aparece somente quando `loja_whatsapp` foi configurado. O telefone pessoal cadastrado para a conta não é usado como alternativa pública.

## Descoberta e compartilhamento

- Os cartões da página inicial oferecem o link “Conhecer a loja” antes da abertura do anúncio.
- A página do anúncio também oferece acesso ao perfil público.
- O botão de compartilhamento usa o compartilhamento nativo do dispositivo quando disponível e copia a URL como alternativa.
- Lojas com anúncios ativos são incluídas no sitemap.

## SEO

Cada loja possui:

- título de página próprio;
- meta description baseada na descrição da loja;
- URL canônica;
- Open Graph com título, descrição, URL e imagem;
- metadados de compartilhamento para Twitter;
- imagem social padrão do Mercado Colatina.

## Responsividade

A página utiliza cartões e grades adaptáveis:

- desktop com apresentação ampla e cinco indicadores;
- tablet com reorganização dos indicadores;
- celular com cabeçalho em coluna, ações em largura total e grade simplificada.

## Migração

Nenhuma migração foi necessária.

- Nenhuma tabela ou coluna foi criada.
- O slug é calculado a partir do nome público da loja.
- Nenhum dado existente foi alterado.

## Preservação de escopo

- Pedidos não foram alterados.
- Estoque não foi alterado.
- Rastreabilidade não foi alterada.
- Painel administrativo não foi alterado.
- Painel interno do vendedor não foi alterado.

## Arquivos alterados

- `app.py`
- `static/styles.css`
- `static/store-share.js`
- `static/mercado-colatina-social.svg`
- `templates/base.html`
- `templates/index.html`
- `templates/anuncio.html`
- `templates/loja_publica.html`
- `tests/test_moderacao.py`
- `MERCADO_COLATINA_MASTER.md`
- `docs/README.md`
- `docs/RELATORIO_PERFIL_PUBLICO_DA_LOJA.md`

## Testes executados

Comando:

```powershell
python -m unittest discover -s tests -v
```

Resultado final: **67 testes aprovados de 67**.

Os novos testes validam:

- acesso público sem autenticação;
- slug normalizado e URL canônica;
- redirecionamento do identificador e de slug incorreto;
- perfil, anúncios ativos e ordem por data;
- indicadores públicos disponíveis;
- ausência de informações privadas;
- uso exclusivo do WhatsApp comercial;
- SEO, Open Graph e URL de compartilhamento;
- loja inexistente ou inativa;
- descoberta da loja antes de abrir o anúncio;
- sitemap;
- estrutura responsiva para desktop, tablet e celular.
