# Integração automática com o Google Ads

## Objetivo

Atualizar o Dashboard de Campanhas com dados oficiais da conta Google Ads
`333-169-5325`, sem editar campanhas, orçamento, anúncios ou pagamentos.

## Escopo de leitura

A integração consulta, para os últimos 30 dias:

- estado da campanha;
- orçamento médio diário;
- data de início;
- impressões;
- cliques;
- custo;
- conversões.

O saldo pré-pago continua identificado como conferência manual porque ele não
faz parte desta consulta de desempenho.

## Segurança

As credenciais nunca ficam no repositório. Devem ser cadastradas como variáveis
secretas no Render:

- `GOOGLE_ADS_CUSTOMER_ID=3331695325`
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID` — somente quando o acesso ocorrer por uma conta
  administradora;
- `GOOGLE_ADS_DEVELOPER_TOKEN`
- `GOOGLE_ADS_CLIENT_ID`
- `GOOGLE_ADS_CLIENT_SECRET`
- `GOOGLE_ADS_REFRESH_TOKEN`
- `GOOGLE_ADS_API_VERSION=v25`
- `GOOGLE_ADS_SYNC_TTL_SECONDS=900`

O token OAuth deve possuir somente o escopo oficial
`https://www.googleapis.com/auth/adwords`. Nenhuma credencial deve ser enviada
por mensagem, commit, captura de tela ou documento público.

## Funcionamento

1. O administrador abre `/admin?visao=campanhas`.
2. O servidor verifica o cache de 15 minutos.
3. Quando necessário, renova o acesso OAuth e executa uma consulta GAQL.
4. Os resultados oficiais substituem o retrato manual no painel.
5. Se a API falhar, o painel continua disponível com os dados manuais de
   segurança e informa a indisponibilidade sem expor detalhes secretos.

O link `Atualizar agora` ignora o cache uma única vez. A chamada permanece
somente leitura.

## Configuração necessária no Google

1. Criar ou selecionar uma conta administradora do Google Ads.
2. Solicitar o token de desenvolvedor no Centro de API.
3. Criar um projeto no Google Cloud e ativar a Google Ads API.
4. Criar um cliente OAuth apropriado.
5. Autorizar o usuário que possui acesso à conta e gerar o refresh token.
6. Cadastrar as variáveis secretas no Render.
7. Validar o selo `Integração automática` no dashboard.

As etapas de criação do cliente OAuth e do token concedem acesso persistente e
devem ser confirmadas pelo proprietário no momento da execução.

## Limitações

- não cria, pausa ou modifica campanhas;
- não altera orçamento;
- não realiza pagamentos;
- não calcula faturamento do Mercado Colatina;
- o cache é local a cada processo do servidor;
- campanhas removidas não são exibidas pela consulta oficial.

## Reversão

Remover ou desativar as credenciais no Render faz o painel voltar
automaticamente ao modo manual. Nenhuma alteração de banco é necessária.
