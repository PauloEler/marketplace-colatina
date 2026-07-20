# RFC — Missão 005 / Sprint 5.1

## Objetivo

Permitir que uma pessoa publique rapidamente um problema cotidiano e seja encontrada por empresas locais capazes de ajudar.

## Público afetado

- moradores que não sabem qual categoria ou empresa procurar;
- empresas e profissionais locais que desejam responder a necessidades reais.

## Proposta

Criar uma jornada mobile-first de quatro passos, sem exigir cadastro para publicar. A pessoa descreve primeiro o problema; uma classificação determinística e interna organiza o mural sem interromper a linguagem natural.

## Critérios

- até quatro passos visuais;
- campos curtos e linguagem direta;
- contato não público;
- resposta em um toque por loja autenticada;
- funcionamento sem JavaScript;
- ausência de dependências e integrações externas;
- nenhuma alteração nas regras dos módulos existentes.

## Fora do escopo

- orçamento dentro da plataforma;
- chat interno;
- pagamento;
- avaliação de prestadores;
- IA, geolocalização ou notificações;
- moderação administrativa completa;
- encerramento automático do pedido.

## Indicador

Razão entre pedidos com ao menos uma resposta e pedidos publicados. A fonte é a tabela `pedidos_servico`; a avaliação deverá começar após a publicação autorizada e uma semana de uso real.

## Riscos

- spam: mitigado inicialmente por CSRF, limites e campo-armadilha;
- exposição de contato: mitigada pela liberação somente a lojas autenticadas;
- classificação imprecisa: não afeta a publicação e pode ser refinada sem alterar o texto do morador.
