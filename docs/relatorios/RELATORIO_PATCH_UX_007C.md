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

PR Draft, sem merge e sem deploy. Aguardar auditoria visual.
