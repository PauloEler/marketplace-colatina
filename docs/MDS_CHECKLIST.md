# MDS Checklist — Nova tela ou alteração de interface

> **Uso obrigatório:** preencher antes da implementação, revisar durante o desenvolvimento e validar novamente antes do commit.
> **Referência:** [Mercado Design System 1.0](DESIGN_SYSTEM_MERCADO_COLATINA.md)

## Identificação

- Tela ou fluxo:
- Responsável:
- Data:
- Versão do MDS:
- Link da missão, RFC ou requisito:
- Ação principal da tela:
- Público principal:

## 1. Objetivo e hierarquia

- [ ] A tela responde claramente “Qual é a ação principal?”.
- [ ] Existe somente uma ação principal por região ou etapa.
- [ ] Título e subtítulo explicam contexto e objetivo sem depender de conhecimento prévio.
- [ ] A ordem visual corresponde à ordem lógica da tarefa.
- [ ] Informações essenciais aparecem antes de conteúdo institucional, promocional ou secundário.
- [ ] Ações destrutivas estão separadas das ações principais.
- [ ] O próximo passo é evidente em todos os estados.

## 2. Componentes e tokens

- [ ] Usa componentes oficiais do MDS.
- [ ] Usa tokens oficiais de cor.
- [ ] Usa tokens oficiais de tipografia.
- [ ] Usa tokens oficiais de espaçamento.
- [ ] Usa tokens oficiais de raio, sombra, dimensão e movimento.
- [ ] Não introduz valor visual arbitrário quando existe token equivalente.
- [ ] Variantes de componente seguem anatomia e estados documentados.
- [ ] Nenhum componente isolado foi criado apenas para esta tela.
- [ ] Exceções estão justificadas e aprovadas para futura incorporação ao MDS.

## 3. Grid e responsividade

- [ ] Segue container máximo de 1180 px.
- [ ] Segue grid e gutters oficiais.
- [ ] Foi projetada mobile first.
- [ ] Funciona em 320, 360 e 390 px.
- [ ] Funciona em 768 px.
- [ ] Funciona em 1024 px.
- [ ] Funciona em 1280 e 1440 px.
- [ ] Não possui rolagem horizontal da página.
- [ ] A ordem do DOM continua correta quando o layout é reorganizado.
- [ ] Formulários são empilhados no mobile.
- [ ] Elementos fixos não cobrem conteúdo, foco ou mensagens.
- [ ] Textos longos, números grandes e conteúdo ausente não quebram o layout.

## 4. Tipografia e conteúdo

- [ ] Usa Inter com fallbacks oficiais.
- [ ] Possui um único H1.
- [ ] Hierarquia H1–H4 é semântica e não salta níveis por estética.
- [ ] Corpo de texto possui pelo menos 16 px.
- [ ] Inputs possuem pelo menos 16 px no mobile.
- [ ] Nenhum texto fica abaixo de 12 px.
- [ ] Pesos e alturas de linha seguem o MDS.
- [ ] Botões começam com verbos específicos.
- [ ] Labels descrevem o dado esperado.
- [ ] Placeholder não substitui label.
- [ ] Microcopy usa português brasileiro simples e direto.
- [ ] Erros explicam como o usuário pode se recuperar.
- [ ] Publicidade, parceria e afiliação estão identificadas.

## 5. Cores e contraste

- [ ] Usa a paleta oficial.
- [ ] Texto normal atinge contraste mínimo de 4,5:1.
- [ ] Texto grande atinge contraste mínimo de 3:1.
- [ ] Controles e indicadores essenciais atingem 3:1.
- [ ] Foco possui contraste mínimo de 3:1 contra áreas adjacentes.
- [ ] Branco não é usado sobre o azul Secondary.
- [ ] Estados semânticos não são usados apenas como decoração.
- [ ] Nenhuma informação depende somente de cor.
- [ ] Links em conteúdo possuem identificação além da cor.
- [ ] Estados disabled continuam compreensíveis.

## 6. Controles e toque

- [ ] Botões e controles possuem altura mínima de 44 px.
- [ ] Alvos de toque possuem pelo menos 44 × 44 px.
- [ ] Existe pelo menos 8 px entre alvos independentes próximos.
- [ ] A interface não depende de hover.
- [ ] Botões icon-only possuem nome acessível.
- [ ] Checkbox e radio possuem label clicável.
- [ ] Select e autocomplete funcionam com teclado.
- [ ] Disabled comunica o motivo quando ele não for evidente.
- [ ] Loading preserva dimensões e impede duplo envio quando necessário.

## 7. Ícones e imagens

- [ ] Usa Lucide Icons no padrão outline e stroke 2.
- [ ] Não mistura bibliotecas ou estilos de ícones.
- [ ] Emojis não são usados como controles funcionais.
- [ ] Ícones decorativos estão ocultos para leitores de tela.
- [ ] Ícones funcionais possuem texto ou nome acessível.
- [ ] Imagens informativas possuem texto alternativo útil.
- [ ] Imagens decorativas possuem alt vazio.
- [ ] Imagens de produto mantêm proporção e placeholder oficial.
- [ ] Logos de parceiros estão identificados sem competir com a marca local.

## 8. Teclado, foco e semântica

- [ ] Toda ação pode ser realizada por teclado.
- [ ] Foco é sempre visível.
- [ ] Ordem do foco acompanha leitura e tarefa.
- [ ] Não existe armadilha de foco fora de modal ou drawer.
- [ ] Modal e drawer contêm foco corretamente.
- [ ] Ao fechar uma camada, o foco retorna ao acionador.
- [ ] Escape fecha camadas temporárias quando seguro.
- [ ] HTML semântico foi usado antes de ARIA.
- [ ] Landmarks e headings estruturam a página.
- [ ] Estado atual usa `aria-current`, `aria-selected` ou equivalente quando aplicável.
- [ ] IDs referenciados por ARIA existem e são únicos.
- [ ] A interface foi inspecionada com leitor de tela ou árvore de acessibilidade.

## 9. Estados da experiência

- [ ] Estado inicial está definido.
- [ ] Estado loading está definido quando necessário.
- [ ] Skeleton é usado somente quando adequado.
- [ ] Estado vazio explica situação e próximo passo.
- [ ] Estado sem resultados permite recuperar ou limpar filtros.
- [ ] Estado de erro explica causa conhecida e recuperação.
- [ ] Estado de sucesso confirma o resultado real.
- [ ] Estado offline ou de falha de rede foi considerado quando relevante.
- [ ] Estado sem permissão não expõe dados nem termina em página sem orientação.
- [ ] Estados pendente, concluído e cancelado são textuais, não apenas coloridos.

## 10. Componentes complexos

- [ ] Tabelas possuem caption e cabeçalhos semânticos.
- [ ] Tabelas adaptam-se ao mobile sem rolagem da página.
- [ ] Paginação possui nome acessível e página atual indicada.
- [ ] Breadcrumb representa hierarquia, não histórico.
- [ ] Alertas usam `role="status"` ou `role="alert"` corretamente.
- [ ] Modal possui nome acessível e `aria-modal="true"`.
- [ ] Drawer não esconde a ação principal.
- [ ] Navbar indica a página atual.
- [ ] Sidebar converte-se em drawer no mobile.
- [ ] Badges e tags não são usados de forma intercambiável.

## 11. Movimento e feedback

- [ ] Tempos e curvas usam tokens do MDS.
- [ ] Movimento explica mudança ou feedback; não é apenas decorativo.
- [ ] Nenhuma interação comum ultrapassa 300 ms sem justificativa.
- [ ] `prefers-reduced-motion` é respeitado.
- [ ] Não existem flashes, parallax agressivo ou loops não essenciais.
- [ ] Toda ação fornece feedback perceptível.
- [ ] Spinners possuem mensagem, limite e recuperação.

## 12. Validação final

- [ ] Contraste foi medido com ferramenta adequada.
- [ ] Fluxo completo foi executado somente por teclado.
- [ ] Zoom de 200% mantém conteúdo e operação.
- [ ] Reflow em 320 CSS px permanece utilizável.
- [ ] Conteúdo real e casos extremos foram validados.
- [ ] Não há erro na árvore de acessibilidade.
- [ ] Não há rolagem horizontal inesperada.
- [ ] Não há regressão em telas relacionadas.
- [ ] Testes automatizados proporcionais ao risco foram adicionados ou atualizados.
- [ ] O MDS foi citado na revisão da implementação.

## Bloqueadores de aprovação

A tela **não pode ser aprovada** se qualquer item abaixo estiver presente:

- [ ] Ação principal indefinida ou competindo com múltiplas ações.
- [ ] Cor, tamanho, raio ou espaçamento criado fora dos tokens sem aprovação.
- [ ] Contraste abaixo do mínimo.
- [ ] Operação essencial impossível por teclado.
- [ ] Falta de foco visível.
- [ ] Rolagem horizontal da página.
- [ ] Conteúdo ou controle inacessível no mobile.
- [ ] Estado de erro, vazio ou loading sem tratamento quando aplicável.
- [ ] Componente novo sem documentação.
- [ ] Exceção ao MDS sem justificativa registrada.

> Para aprovação, todos os bloqueadores acima devem permanecer **desmarcados**.

## Registro da revisão

| Papel | Nome | Data | Resultado | Observações |
|---|---|---|---|---|
| Produto |  |  |  |  |
| UX/UI |  |  |  |  |
| Desenvolvimento |  |  |  |  |
| Acessibilidade/QA |  |  |  |  |

**Resultado final:** [ ] aprovado · [ ] aprovado com ressalvas registradas · [ ] reprovado
