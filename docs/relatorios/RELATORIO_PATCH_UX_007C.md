# Relatório — PATCH UX-007C Alinhamento final

## Objetivo

Eliminar os últimos desalinhamentos da Home e preservar integralmente seu conteúdo e suas funcionalidades.

## Causa visual

- Busca Rápida e Encontre Quem Resolve estavam limitados a `73.75rem`;
- Cidade Viva e as seções compactas utilizavam `80rem`;
- com dois indicadores, a grade mantinha uma terceira coluna vazia;
- o Balão tinha aproximadamente 180 px a mais que Cidade Viva no cenário medido, criando vazio abaixo do bloco principal;
- os contêineres “Ver todos” herdavam larguras e espaçamentos diferentes.

## Implementação

- flag `HOME_FINISH_007C_ENABLED=false` por padrão;
- largura comum de `80rem` para os três blocos principais;
- dois indicadores distribuídos em duas colunas;
- Balão reorganizado em duas colunas no desktop e uma no mobile;
- “Ver todos” padronizado no canto inferior direito;
- raios, padding, margens e intervalos normalizados;
- rodapé aproximado do conteúdo com redução de espaços, sem remoção de informações.

## Preservado

Hero, conteúdo e funcionamento da busca, Encontre Quem Resolve, produtos, empresas, parceiros, backend, banco, rotas e dashboards.

## Validação concluída

- 165 testes automatizados aprovados;
- `ruff check` e `ruff format --check` aprovados;
- `git diff --check` aprovado;
- em 1440 px, os três blocos medem 1278 px e começam em 74 px;
- em 1024 px, os três blocos medem 895 px e começam em 57 px;
- em 768 px, os três blocos medem 660 px;
- em 390 px, os três blocos medem 335 px;
- em 320 px, os três blocos medem 265 px;
- Balão alinhado ao topo da Cidade Viva em desktop e notebook;
- em tablet e mobile, o Balão mantém o empilhamento responsivo previsto;
- dois indicadores ocupam duas colunas de mesma largura;
- os sete links “Ver todos” terminam com deslocamento uniforme de 16–17 px das bordas direita e inferior;
- console sem erros ou avisos;
- nenhum overflow horizontal entre 320 px e 1440 px;
- Home UX-007B preservada quando a flag está desligada;
- ativação condicionada às flags anteriores e reversível por um único commit.

## Publicação

- PR: `#95`.
- Merge por squash: `cf282d76ac718d0930d6a8b882ee135fbda1ff2c`.
- CI da `master`: aprovado no workflow `29859624953`.
- Deploy automático do código: `live` no Render às 16h02, horário de Brasília.
- `HOME_FINISH_007C_ENABLED=true` ativada no Render.
- Deploy da configuração: `live` às 16h06, horário de Brasília.

## Validação final em produção

- classe `home-finish-ux007c` confirmada no HTML da Home;
- Busca Rápida, Encontre Quem Resolve e Cidade Viva com 1280 px de largura e início comum na auditoria desktop;
- Cidade Viva e Balão alinhados na coordenada vertical de 795 px;
- dois indicadores reais distribuídos em duas colunas;
- sete links “Ver todos” presentes e com destinos preenchidos;
- Hero, produtos, empresas e Ofertas de Parceiros operacionais;
- nenhum overflow horizontal da página;
- console da aplicação sem erros; o único registro observado foi originado por uma extensão do navegador e não pelo Mercado Colatina;
- comportamento responsivo de 1024, 768, 390 e 320 px preservado conforme as evidências e testes aprovados do commit publicado;
- produção estável após o deploy.
