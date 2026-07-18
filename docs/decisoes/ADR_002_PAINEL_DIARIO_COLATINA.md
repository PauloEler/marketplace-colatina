# ADR 002 — Painel Diário de Colatina com placeholders centralizados

## Status

Aceita para a Sprint MX-005.1.

## Contexto

O projeto precisa testar uma área diária de informação local, mas ainda não definiu provedores, frequência de atualização, responsabilidades editoriais ou contratos de dados. Publicar informações simuladas criaria risco de confiança, especialmente para tempo, vagas e farmácia de plantão.

## Decisão

Criar uma estrutura estática centralizada em `daily_city.py` e renderizar cinco placeholders reutilizáveis na Home. Todos os cards devem declarar visualmente “Em preparação”. Nenhuma integração, dado real ou regra operacional será incluída.

## Razões

- preserva a transparência;
- permite validar UX e responsividade;
- reduz o custo de uma futura integração;
- evita alterações de banco;
- mantém componentes e conteúdo desacoplados;
- não adiciona dependências ou chamadas externas.

## Alternativas consideradas

### Conteúdo escrito diretamente no template

Rejeitado por duplicar estrutura e dificultar a substituição futura por fontes distintas.

### Dados simulados

Rejeitados porque poderiam ser interpretados como informações atuais da cidade.

### Integração imediata com APIs

Rejeitada por ampliar o escopo antes da definição de fontes, disponibilidade, cache, atribuição e responsabilidade editorial.

## Consequências

### Positivas

- componente leve e testável;
- mensagem honesta sobre o estágio do recurso;
- arquitetura pronta para evolução;
- nenhum impacto em banco ou regras de negócio.

### Negativas

- o painel ainda não entrega informação diária real;
- haverá trabalho adicional para definir e integrar cada fonte;
- futuras integrações exigirão estados de carregamento, erro e validade.

## Critérios para evolução

Uma categoria só poderá deixar de ser placeholder quando houver fonte aprovada, horário de atualização visível, tratamento de indisponibilidade e testes de exatidão e acessibilidade.
