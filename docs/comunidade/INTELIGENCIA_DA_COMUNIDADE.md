# Inteligência da Comunidade

## Problema real da cidade

Receber sugestões não é suficiente quando a administração precisa reconhecer padrões sem reler manualmente toda a fila. Sem agregação comparável, decisões podem ser tomadas por impressão e necessidades recorrentes podem permanecer invisíveis.

## Objetivo

Transformar os registros do Ouvir Colatina em indicadores administrativos transparentes para responder, com evidência e limites claros, o que a cidade mais relata precisar.

## Radar da Cidade

O painel administrativo consolida:

- total, implementadas, pendentes e arquivadas;
- volume de hoje e dos últimos 7, 30 e 90 dias;
- ranking por categoria;
- tempo médio entre criação e primeira análise;
- palavras relevantes mais frequentes;
- termos recorrentes presentes em duas ou mais sugestões;
- categorias em crescimento na comparação entre os últimos 30 dias e os 30 dias anteriores.

## Regra de honestidade

O painel não chama um único registro de tendência. Quando a amostra dos últimos 30 dias for inferior a três sugestões, a resposta principal será **dados insuficientes** e mostrará apenas sinais preliminares.

## Método das palavras

As mensagens são normalizadas localmente, sem envio externo. Artigos, preposições, pronomes, números e termos genéricos são removidos. A contagem considera em quantas sugestões distintas cada palavra aparece, evitando que a repetição dentro de uma única mensagem distorça o resultado.

Essa técnica é lexical e determinística. Ela não compreende contexto, ironia, sinônimos ou intenção e não deve ser apresentada como análise semântica.

## Privacidade

O Radar é exclusivo para administradores e exibe dados agregados. Nomes e mensagens completas não são apresentados no painel de inteligência. Nenhum dado novo é coletado e nenhuma informação é enviada a serviços externos.

## Preparação para IA futura

O domínio fornece um conjunto estruturado versionado, sem nomes, contendo identificador, categoria, estado, mensagem e datas já existentes. Nesta missão ele permanece interno e não é transmitido nem processado por IA. Qualquer integração futura exigirá RFC, ADR, base legal, política de retenção e avaliação de fornecedor.

## Pergunta final

O painel responde **“O que Colatina mais precisa neste momento?”** usando a categoria líder, o período recente e os termos recorrentes. Quando não houver amostra suficiente, responde isso explicitamente.
