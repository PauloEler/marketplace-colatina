# RFC — Ouvir Colatina

**Status:** aprovada para implementação pela Missão 001

**Data:** 20 de julho de 2026

## Problema

A evolução do produto depende de necessidades reais da cidade, mas não existe um fluxo oficial para receber, classificar, acompanhar e medir sugestões da população.

## Objetivo

Criar a primeira infraestrutura de escuta comunitária do Mercado Colatina com baixo atrito para o cidadão e controle administrativo suficiente para transformar contribuições em descoberta de produto.

## Proposta

- rota pública `/sugerir` com formulário acessível;
- chamada global discreta no layout base, sem modificar `templates/index.html`;
- tabela própria `sugestoes_comunidade` para SQLite e PostgreSQL;
- módulo de domínio `community_suggestions.py` com validação, consulta, transição de estado e métricas;
- painel exclusivo em `/admin/sugestoes`;
- filtros por categoria e status;
- atualização de estado protegida por autenticação administrativa e CSRF;
- arquitetura documental para votação futura, sem voto nesta Sprint.

## Dados armazenados

- nome informado voluntariamente, quando houver;
- categoria;
- mensagem;
- estado;
- datas de criação, primeira análise, implementação e atualização.

Não serão armazenados IP, localização, telefone, e-mail ou vínculo automático com a conta.

## Validação

- nome vazio aceito; nome informado limitado;
- categoria pertence à lista oficial;
- mensagem possui tamanho mínimo e máximo;
- conteúdo é escapado na renderização;
- visitante não acessa o painel;
- usuário comum não acessa nem altera estados;
- administrador filtra e atualiza estados;
- métricas refletem os registros sem alterar Analytics existente;
- layout funciona em desktop, tablet, 390 px e 320 px.

## Fora do escopo

- votação;
- publicação pública das sugestões;
- notificações, WhatsApp ou e-mail;
- comentários ou respostas;
- alteração de Marketplace, afiliados, empresas parceiras, Hoje em Colatina, Central de Notificações ou Analytics existente.

## Critérios de aceite

O morador envia uma sugestão em poucos passos, o administrador consegue analisá-la e as métricas mostram volume, categorias, implementações e tempo até a primeira análise.
