# Relatório — Missão 005 / Sprint 5.1

## Entrega

MVP “Encontre Quem Resolve” implementado em domínio isolado, com publicação pública em quatro passos e resposta por WhatsApp restrita a lojas autenticadas.

## Arquivos principais

- `service_requests.py`
- `templates/encontre_quem_resolve.html`
- `templates/quem_resolve.html`
- `static/service-request.js`
- `static/styles.css`
- `database.py`
- `app.py`
- `tests/test_moderacao.py`

## Comportamento

- problema informado antes de qualquer categoria;
- categoria inferida internamente;
- quatro passos visuais;
- publicação sem cadastro;
- consentimento explícito;
- WhatsApp ausente da listagem pública;
- loja autenticada responde em um toque;
- experiência funcional sem JavaScript.

## Testes

- fluxo público e quatro passos;
- validação e consentimento;
- classificação automática;
- normalização e sigilo do WhatsApp;
- bloqueio de visitante e conta sem loja;
- resposta de loja autenticada;
- 138 testes automatizados aprovados;
- Ruff check e format aprovados;
- desktop 1440 px, notebook 1024 px, tablet 768 px, mobile 390 px e 320 px sem overflow;
- alvos principais com no mínimo 44 px e console da aplicação sem erros;
- fluxo completo de quatro passos publicado com sucesso no ambiente local isolado.

## Limitações

O MVP não possui chat, orçamento, pagamento, avaliação, encerramento pelo morador, moderação completa, IA ou notificação. O contador registra intenções de contato, não comprova contratação.

## Próximo aprendizado

Após publicação autorizada, medir quantos pedidos recebem pelo menos uma resposta e identificar bairros, prazos e tipos de problema com maior demanda.

## Status

Branch de desenvolvimento. Sem merge e sem deploy.
