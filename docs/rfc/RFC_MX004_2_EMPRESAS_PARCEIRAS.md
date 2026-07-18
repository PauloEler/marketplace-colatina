# RFC MX-004.2 — Empresas Parceiras e Confiança

## Status

Implementada em branch para revisão. Sem merge e sem deploy.

## Objetivo

Introduzir na Home uma camada institucional de confiança e preparar espaços premium para futuras empresas parceiras de Colatina.

## Motivação

Credibilidade e transparência são essenciais para o crescimento local do marketplace. A solução precisa explicar o posicionamento do Mercado Colatina e preparar monetização futura sem simular parcerias, criar pressão publicitária ou alterar regras existentes.

## Decisão

Adotar duas seções visuais após as vitrines locais e antes de “Como funciona”:

1. “Por que confiar no Mercado Colatina?”, com cinco compromissos institucionais;
2. “Empresas Parceiras”, com seis placeholders e identificação institucional.

Os dados dos cards ficam em um módulo Python imutável e centralizado. Foram preparados os níveis Parceiro Local, Parceiro Destaque e Parceiro Premium apenas como metadados. As rotas institucionais reutilizam o template existente.

## Alternativas consideradas

### Dados no template

Rejeitada porque espalharia conteúdo e dificultaria a substituição segura dos placeholders.

### Nova tabela no banco

Rejeitada por ampliar o escopo, exigir migração e introduzir regras comerciais ainda inexistentes.

### Painel administrativo nesta sprint

Rejeitado porque contratação, preços, benefícios e publicação dinâmica ainda dependem de decisões futuras.

## Componentes afetados

- contexto de renderização da Home;
- template da Home;
- folhas de estilo responsivas;
- rodapé geral;
- sitemap público;
- páginas institucionais;
- testes de renderização, conteúdo, ordem e configuração.

## Impacto esperado

Mais clareza sobre a origem local e o modelo de negociação, melhor percepção de seriedade e um ponto institucional pronto para conversas futuras com empresas da cidade.

## Compatibilidade e performance

A solução não usa JavaScript, API, imagem externa, consulta adicional ou banco. SVGs discretos são embutidos e os seis cards são renderizados no mesmo ciclo da Home. O impacto esperado de performance é mínimo.

## Riscos e mitigação

- confusão entre parceiro e anunciante: mitigada por seção separada e identificação institucional;
- impressão de parceria já ativa: mitigada pelo nome “Espaço reservado” e pela página “programa em preparação”;
- perda de protagonismo do marketplace: mitigada pela posição posterior a produtos, afiliados, chamada para vendedores e lojas;
- excesso visual: mitigado por grade estática, sem pop-ups, piscadas ou rotação.

## Limitações

Não há parceiro real, plano comercial ativo, preço, pagamento, vigência, analytics específico ou gestão dinâmica.

## Próximos passos

Definir proposta comercial, critérios de entrada, benefícios por nível, política de transparência, processo de aprovação de logotipos e canal oficial de contato antes de ativar qualquer empresa.
