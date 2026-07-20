# Arquitetura — Encontre Quem Resolve

## Problema da cidade

Moradores de Colatina perdem tempo procurando prestadores em grupos, redes sociais e contatos dispersos. Empresas locais, por outro lado, não enxergam de forma organizada as necessidades que poderiam atender.

## Componentes

- `service_requests.py`: validação, classificação simples, persistência e abertura segura do contato.
- `pedidos_servico`: tabela isolada dos anúncios e pedidos do marketplace.
- `/encontre-quem-resolve`: publicação pública em quatro passos.
- `/quem-resolve`: mural de necessidades sem exposição do WhatsApp.
- `/quem-resolve/<id>/responder`: liberação do contato somente para loja autenticada ou administrador.
- `service-request.js`: melhoria progressiva do formulário; sem JavaScript, os campos continuam disponíveis em uma única página.

## Fluxo

1. Morador descreve o problema em linguagem natural.
2. Informa bairro e prazo.
3. Informa WhatsApp.
4. Revisa, autoriza o contato e publica.
5. Uma loja autenticada escolhe “Posso resolver” e inicia a conversa no WhatsApp.

## Privacidade e segurança

O número não aparece no mural nem no HTML da listagem. A rota de contato exige autenticação, loja cadastrada e CSRF. O formulário possui limite de tamanho, normalização do telefone, consentimento explícito e campo-armadilha para robôs.

## Isolamento

O módulo não reutiliza nem altera regras de anúncios, pedidos, afiliados, empresas parceiras, notificações ou analytics. A integração com esses domínios permanece fora do MVP.

## Medição inicial

- pedidos publicados: contagem em `pedidos_servico`;
- pedidos respondidos: soma de `respostas`;
- tempo até a primeira resposta: preparado como evolução, ainda não medido nesta Sprint.
