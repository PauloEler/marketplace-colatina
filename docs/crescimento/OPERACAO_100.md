# OPERACAO PRIMEIROS 100

## Problema da cidade

Uma plataforma local sem uso recorrente nao consolida informacoes, comercio e participacao suficientes para facilitar a vida em Colatina. A operacao precisa distinguir cadastro de uso real e agir sobre bloqueios mensuraveis.

## Objetivo

Conquistar e acompanhar os primeiros 100 usuarios nao administrativos ativos em duas semanas consecutivas. O painel administrativo `/admin/operacao-100` reune usuarios, empresas, marketplace, afiliados e comunidade em uma leitura diaria.

## Definicoes oficiais

- usuario ativo: conta nao administrativa com atividade registrada nos ultimos 7 dias;
- usuario recorrente: conta ativa na janela atual de 7 dias e na janela anterior de 7 dias;
- empresa cadastrada: conta ativa com nome de loja;
- empresa ativa: empresa cadastrada com ao menos um anuncio ativo;
- receita de afiliados: somente valor devolvido por fonte oficial do parceiro; atualmente indisponivel;
- tempo medio de resposta: intervalo entre a criacao do pedido e o primeiro evento `VENDEDOR_CONFIRMOU`, nos ultimos 30 dias.

## Operacao diaria

1. Consultar o painel no inicio do dia.
2. Identificar a menor etapa do funil e os bloqueios apresentados.
3. Executar somente uma acao de crescimento rastreavel por vez.
4. Revisar recorrencia semanalmente.
5. Registrar receita ou convite somente quando houver fonte oficial.

## Marcos

- [ ] Primeiro usuario recorrente
- [ ] Primeiros 10 usuarios recorrentes
- [ ] Primeiros 50 usuarios recorrentes
- [ ] Primeiros 100 usuarios recorrentes
- [ ] Primeira empresa parceira
- [ ] Primeira comissao dos afiliados
- [ ] Primeira sugestao implementada
- [ ] Primeira campanha comunitaria

O painel atualiza automaticamente os marcos com fonte interna. Comissao e campanha permanecem pendentes ate existir registro oficial.
